"""Observational CFO cost recovery, school-type and support analysis in Python."""
import argparse
from datetime import datetime, timezone
import hashlib
from importlib.metadata import version
import json
import platform

import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.api as sm
from statsmodels.stats.multitest import multipletests

from .download import ROOT
from .hashes import text_sha256
from .models import fixed_effects
from .return_data import acquire_cpi, build, cumulative_changes

METRICS={'cup':'cup_100','fpi':'fpi_10','sweet16':'sweet16'}


def linear_results(fit,terms,covariance,n,g,years,y,controls,effects,contrasts=None):
    """Direct contrasts use the full covariance, never compare subgroup p-values."""
    beta=np.asarray(fit.params)[:len(terms)]
    cov=np.asarray(covariance)[:len(terms),:len(terms)]
    vectors={name:np.eye(len(terms))[i] for i,name in enumerate(terms)}
    for name,weights in (contrasts or {}).items():
        if set(weights)-set(terms):raise ValueError('Unknown contrast variable')
        vectors[name]=np.array([weights.get(term,0) for term in terms])
    critical=stats.t.ppf(.975,g-1)
    rows=[]
    for name,w in vectors.items():
        b=float(w@beta);se=float(np.sqrt(w@cov@w))
        rows.append(dict(term=name,coefficient=b,std_error=se,
            p_value=float(2*stats.t.sf(abs(b/se),g-1)),
            ci_low=b-critical*se,ci_high=b+critical*se,
            n=n,schools=g,year_min=int(min(years)),year_max=int(max(years)),
            within_r2=float(fit.rsquared),outcome=y,controls=';'.join(controls),
            fixed_effects=effects,cluster='school',df_resid=float(fit.df_resid)))
    return rows


def changes_ols(data,y,x,controls=(),time_effect='conference_year',contrasts=None):
    columns=list(dict.fromkeys(['unitid','year',time_effect,y,*x,*controls]))
    d=data[columns].replace([np.inf,-np.inf],np.nan).dropna().copy()
    # An isolated time cell contributes no exposure information. School
    # singletons remain valid independent first-difference clusters.
    d=d[d.groupby(time_effect)[time_effect].transform('size').ge(2)]
    n=len(d);g=d.unitid.nunique()
    if n<50 or g<20:raise ValueError('Insufficient observations/clusters')
    terms=[*x,*controls]
    design=pd.concat([d[terms].astype(float).reset_index(drop=True),
        pd.get_dummies(d[time_effect].astype(str),drop_first=True,dtype=float).reset_index(drop=True)],axis=1)
    # Put substantive terms first so covariance and contrasts have stable indices.
    design['intercept']=1.
    if np.linalg.matrix_rank(design)!=design.shape[1]:raise ValueError('Rank deficient change model')
    fit=sm.OLS(d[y].to_numpy(float),design.to_numpy(float)).fit(
        cov_type='cluster',cov_kwds={'groups':d.unitid.to_numpy()},use_t=True)
    rows=linear_results(fit,terms,fit.cov_params(),n,g,d.year,y,controls,
        time_effect+';calendar_changes',contrasts)
    return rows,d[['unitid','year']]


class ReturnStudy:
    def __init__(self):
        self.rows=[];self.status=[];self.flows=[];self.cases={};self.specs={};self.events=[]

    def estimate(self,name,frame,y,x,controls=(),*,mode='changes',effects='conference_year',
                 contrasts=None,family='secondary',primary_term=None,null=0.):
        columns=list(dict.fromkeys(['unitid','year',effects,y,*x,*controls]))
        remaining=frame.copy()
        for order,col in enumerate(columns):
            valid=remaining[col].notna()
            if pd.api.types.is_numeric_dtype(remaining[col]):valid&=np.isfinite(remaining[col])
            self.flows.append(dict(model=name,step=order,reason='missing_or_nonfinite_'+col,
                excluded=int((~valid).sum()),remaining=int(valid.sum())))
            remaining=remaining[valid]
        try:
            if mode=='changes':rows,keys=changes_ols(frame,y,x,controls,effects,contrasts)
            else:rows,keys=fixed_effects(frame,y,x,controls,time_effect=effects,contrasts=contrasts)
            if not np.isfinite([[r['coefficient'],r['std_error'],r['p_value']] for r in rows]).all():
                raise ValueError('Nonfinite inference')
            for r in rows:
                primary=r['term']==primary_term
                target=null if primary else 0.
                r.update(model=name,family=family if primary else 'secondary',primary=primary,
                    primary_null=target,test_p=float(2*stats.t.sf(abs((r['coefficient']-target)/r['std_error']),r['schools']-1)),
                    mode=mode,holm_family_p=np.nan,holm_all_primary_p=np.nan)
            self.rows.extend(rows)
            self.cases[name]=keys
            self.specs[name]=dict(frame=frame,y=y,x=x,controls=controls,mode=mode,effects=effects,
                                  contrasts=contrasts,primary_term=primary_term,null=null)
            selected=frame.merge(keys,on=['unitid','year'],validate='one_to_one')
            private=ROOT/'data/private/return_samples';private.mkdir(exist_ok=True)
            selected[columns].to_csv(private/f'{name}.csv',index=False)
            for group in ['small_budget_all','high_support','power_2014','small_budget_fbs',
                          'small_enrollment_fbs','low_prominence','other_2014']:
                if group not in selected:continue
                for value in [0.,1.]:
                    z=selected[selected[group].eq(value)]
                    if not len(z):continue
                    self.events.append(dict(model=name,group=group,value=int(value),n=len(z),
                        schools=z.unitid.nunique(),outperformance_sd=z.outperformance_10.std(),
                        ap_breakthrough_rows=int(z.preseason_unranked_breakthrough.eq(1).sum()),
                        ap_breakthrough_schools=z.loc[z.preseason_unranked_breakthrough.eq(1),'unitid'].nunique()))
            self.flows.append(dict(model=name,step=len(columns),reason='absorbed_singletons',
                excluded=len(remaining)-len(keys),remaining=len(keys)))
            self.status.append(dict(model=name,status='estimated',primary=primary_term is not None,
                initial_n=len(frame),n=len(keys),schools=rows[0]['schools']))
            return rows
        except (ValueError,np.linalg.LinAlgError) as error:
            self.status.append(dict(model=name,status='not_estimable',primary=primary_term is not None,
                initial_n=len(frame),n=0,schools=0,reason=str(error)))
            return []

    def save(self):
        d=pd.DataFrame(self.rows)
        for family in d.loc[d.primary,'family'].unique():
            mask=d.primary&d.family.eq(family)
            d.loc[mask,'holm_family_p']=multipletests(d.loc[mask,'test_p'],method='holm')[1]
        d.loc[d.primary,'holm_all_primary_p']=multipletests(d.loc[d.primary,'test_p'],method='holm')[1]
        d.to_csv(ROOT/'results/return_models.csv',index=False)
        pd.DataFrame(self.status).to_csv(ROOT/'results/return_model_status.csv',index=False)
        pd.DataFrame(self.flows).to_csv(ROOT/'results/return_sample_flow.csv',index=False)
        pd.DataFrame(self.events).to_csv(ROOT/'results/return_group_support.csv',index=False)
        d[d.primary].to_csv(ROOT/'results/return_primary.csv',index=False)
        return d


def estimate_all(d,influence=True):
    s=ReturnStudy()
    base=d[d.primary_eligible].copy()
    controls=['change_log_total_enrollment']
    s.estimate('R_annual',base,'change_revenue_m',['change_expense_m'],controls,
        family='cost_recovery',primary_term='change_expense_m',null=1.)
    cumulative=cumulative_changes(base)
    s.estimate('R_three_year',cumulative,'cumulative_revenue_m',['cumulative_expense_m'],
        ['cumulative_log_enrollment_change'],family='cost_recovery',primary_term='cumulative_expense_m',null=1.)
    for group in ['small_budget_all','high_support','power_2014']:
        z=base[base.year.ge(2015 if group=='power_2014' else 2013)&base[group].notna()].copy()
        term='spend_x_'+group
        s.estimate('H_'+group,z,'change_revenue_m',['change_expense_m',group,term],controls,
            contrasts={'group0_slope':{'change_expense_m':1},'group1_slope':{'change_expense_m':1,term:1}},
            family='school_types',primary_term=term)
    for metric,x in METRICS.items():
        for y in ['support_m','support_pct_expense']:
            s.estimate(f'S_{metric}_{y}',base,'future_'+y,[x],['lag_log_total_enrollment'],
                mode='levels',family='self_support',primary_term=x)
    for label,y in [('revenue','next_log_net_nonallocated_revenue_proxy'),
                    ('applications','log_applications'),('enrollment','log_first_time_enrollment')]:
        group='small_budget_fbs';term='outperformance_x_'+group
        z=base[base.year.ge(2013)&base[group].notna()]
        s.estimate('U_small_'+label,z,y,['outperformance_10',term],
            ['lag_fpi_10','lag_log_total_enrollment'],mode='levels',
            contrasts={'larger_slope':{'outperformance_10':1},
                'smaller_slope':{'outperformance_10':1,term:1}},
            family='small_school_breakthrough',primary_term=term)
    primary=s.save()
    print('Primary extension tests (cost-recovery null is 1):',flush=True)
    print(primary[primary.primary][['model','coefficient','ci_low','ci_high','test_p','holm_family_p','n','schools']].to_string(index=False),flush=True)
    # Pre-specified accounting and timing checks; every result is retained.
    for effects in ['year','conference_year']:
        s.estimate('R_levels_'+effects,base,'revenue_m',['expense_m'],['log_total_enrollment'],mode='levels',effects=effects)
    s.estimate('R_changes_school_effects',base,'change_revenue_m',['change_expense_m'],controls,mode='levels')
    s.estimate('R_changes_year',base,'change_revenue_m',['change_expense_m'],controls,effects='year')
    joint=base.dropna(subset=['change_expense_m','change_revenue_m','change_support_m','change_total_m',
                                'change_log_total_enrollment','conference_year'])
    for y in ['change_revenue_m','change_support_m','change_gap_m','change_total_m']:
        s.estimate('R_bridge_'+y,joint,y,['change_expense_m'],controls)
    s.estimate('R_three_year_discounted',cumulative_changes(base,discount=.03),
        'cumulative_revenue_m',['cumulative_expense_m'],['cumulative_log_enrollment_change'])
    s.estimate('R_three_year_school_effects',cumulative,'cumulative_revenue_m',
        ['cumulative_expense_m'],['cumulative_log_enrollment_change'],mode='levels')
    positive=base[base.change_expense_m.gt(0)]
    s.estimate('R_positive_increases_only',positive,'change_revenue_m',['change_expense_m'],controls)
    cut=base[['change_expense_m','change_revenue_m']].quantile([.01,.99])
    keep=base.change_expense_m.between(*cut.change_expense_m)&base.change_revenue_m.between(*cut.change_revenue_m)
    s.estimate('R_trim_1_99',base[keep],'change_revenue_m',['change_expense_m'],controls)
    s.estimate('R_exclude_2015_2017',base[~base.year.between(2015,2017)],'change_revenue_m',['change_expense_m'],controls)
    balanced=base.groupby('unitid')[['expense_m','revenue_m']].count().min(axis=1).eq(10)
    s.estimate('R_balanced',base[base.unitid.isin(balanced[balanced].index)],'change_revenue_m',['change_expense_m'],controls)
    nominal=base.copy()
    from .clean import calendar_join
    nominal=calendar_join(nominal,['kn_expenses','net_nonallocated_revenue_proxy'],-1,'nominal_pre_',lookup=d)
    nominal['nominal_expense_change']=(nominal.kn_expenses-nominal.nominal_pre_kn_expenses)/1e6
    nominal['nominal_revenue_change']=(nominal.net_nonallocated_revenue_proxy-nominal.nominal_pre_net_nonallocated_revenue_proxy)/1e6
    s.estimate('R_nominal',nominal,'nominal_revenue_change',['nominal_expense_change'],controls)
    lagged=calendar_join(base,['change_expense_m'],-1,'previous_')
    s.estimate('R_distributed_lag',lagged,'change_revenue_m',['change_expense_m','previous_change_expense_m'],controls,
        contrasts={'current_plus_prior':{'change_expense_m':1,'previous_change_expense_m':1}})
    # On a shared sample, gap response = expense response - revenue response.
    for metric,x in METRICS.items():
        z=base.dropna(subset=[x,'future_expense_m','future_revenue_m','future_gap_m',
                               'future_support_m','lag_log_total_enrollment','conference_year'])
        for y in ['expense_m','revenue_m','gap_m','support_m']:
            s.estimate(f'S_bridge_{metric}_{y}',z,'future_'+y,[x],['lag_log_total_enrollment'],mode='levels')
        for y in ['fees_per_student','gap_m']:
            s.estimate(f'S_{metric}_{y}',base,'future_'+y,[x],['lag_log_total_enrollment'],mode='levels')
        for y in ['support_m','support_pct_expense']:
            s.estimate(f'S_{metric}_{y}_year',base,'future_'+y,[x],['lag_log_total_enrollment'],mode='levels',effects='year')
    for group in ['small_budget_all','high_support','power_2014']:
        z=base[base.year.ge(2015 if group=='power_2014' else 2013)&base[group].notna()]
        term='spend_x_'+group
        s.estimate('H_'+group+'_year',z,'change_revenue_m',['change_expense_m',group,term],controls,effects='year',
            contrasts={'group0_slope':{'change_expense_m':1},'group1_slope':{'change_expense_m':1,term:1}})
    joint_groups=base[base.year.ge(2013)&base.small_budget_all.notna()&base.high_support.notna()]
    s.estimate('H_joint_budget_support',joint_groups,'change_revenue_m',
        ['change_expense_m','small_budget_all','high_support','spend_x_small_budget_all','spend_x_high_support'],controls)
    z=base[base.year.ge(2013)&base.small_budget_fbs.notna()].dropna(subset=[
        'outperformance_10','outperformance_x_small_budget_fbs','lag_fpi_10','lag_log_total_enrollment',
        'conference_year','future_expense_m','future_revenue_m','future_gap_m','future_support_m'])
    for outcome in ['expense_m','revenue_m','gap_m','support_m']:
        s.estimate('U_small_dollars_'+outcome,z,'future_'+outcome,
            ['outperformance_10','outperformance_x_small_budget_fbs'],['lag_fpi_10','lag_log_total_enrollment'],
            mode='levels',contrasts={'larger_slope':{'outperformance_10':1},
                'smaller_slope':{'outperformance_10':1,'outperformance_x_small_budget_fbs':1}})
    for group in ['small_budget_fbs','small_enrollment_fbs','low_prominence','other_2014']:
        for label,y in [('revenue','next_log_net_nonallocated_revenue_proxy'),
                        ('applications','log_applications'),('enrollment','log_first_time_enrollment')]:
            z=base[base.year.ge(2015 if group=='other_2014' else 2013)&base[group].notna()]
            term='outperformance_x_'+group
            for effects in ['year','conference_year']:
                s.estimate(f'U_{group}_{label}_{effects}',z,y,['outperformance_10',term],
                    ['lag_fpi_10','lag_log_total_enrollment'],mode='levels',effects=effects,
                    contrasts={'group0_slope':{'outperformance_10':1},'group1_slope':{'outperformance_10':1,term:1}})
            if group=='other_2014':continue
            term='ap_breakthrough_x_'+group
            s.estimate(f'U_ap_{group}_{label}',z,y,['preseason_unranked_breakthrough',term],
                ['lag_fpi_10','lag_log_total_enrollment'],mode='levels',
                contrasts={'group0_slope':{'preseason_unranked_breakthrough':1},
                           'group1_slope':{'preseason_unranked_breakthrough':1,term:1}})
    models=s.save()
    descriptive_tables(base,s)
    influence_rows=[]
    if influence:
        for name in ['R_annual','R_three_year','H_high_support','U_small_revenue','U_small_applications','U_small_enrollment',
                     'U_ap_small_budget_fbs_applications','U_ap_small_budget_fbs_enrollment']:
            spec=s.specs.get(name)
            if not spec:continue
            sample=spec['frame'].merge(s.cases[name],on=['unitid','year'],validate='one_to_one')
            for uid in sorted(sample.unitid.unique()):
                subset=sample[sample.unitid.ne(uid)]
                try:
                    if spec['mode']=='changes':rr,_=changes_ols(subset,spec['y'],spec['x'],spec['controls'],spec['effects'],spec['contrasts'])
                    else:rr,_=fixed_effects(subset,spec['y'],spec['x'],spec['controls'],time_effect=spec['effects'],contrasts=spec['contrasts'])
                    term=spec['primary_term'] or 'ap_breakthrough_x_small_budget_fbs'
                    row=next(r for r in rr if r['term']==term)
                    influence_rows.append(dict(model=name,**{k:row[k] for k in ['coefficient','std_error','p_value','n','schools']},
                        null_test_p=float(2*stats.t.sf(abs((row['coefficient']-spec['null'])/row['std_error']),row['schools']-1)),status='estimated'))
                except (ValueError,np.linalg.LinAlgError) as error:
                    influence_rows.append(dict(model=name,status='not_estimable',reason=str(error)))
            print('Influence completed:',name,len(sample.unitid.unique()),flush=True)
    inf=pd.DataFrame(influence_rows,columns=['model','coefficient','std_error','p_value','n','schools','null_test_p','status','reason'])
    inf.to_csv(ROOT/'results/return_influence.csv',index=False)
    if len(inf):
        inf[inf.status.eq('estimated')].groupby('model').agg(omissions=('coefficient','size'),
            min_coefficient=('coefficient','min'),max_coefficient=('coefficient','max'),
            max_null_p=('null_test_p','max')).to_csv(ROOT/'results/return_influence_summary.csv')
    else:pd.DataFrame(columns=['model','omissions','min_coefficient','max_coefficient','max_null_p']).to_csv(ROOT/'results/return_influence_summary.csv',index=False)
    return models,s


def descriptive_tables(d,study):
    """Accounting levels, matched growth and coverage are distinct quantities."""
    rows=[];endpoint=[]
    groups=[('All eligible DI',d),('Smaller baseline DI budget',d[d.small_budget_all.eq(1)&d.year.ge(2013)]),
        ('Larger baseline DI budget',d[d.small_budget_all.eq(0)&d.year.ge(2013)]),
        ('High baseline support',d[d.high_support.eq(1)&d.year.ge(2013)]),
        ('Lower baseline support',d[d.high_support.eq(0)&d.year.ge(2013)]),
        ('2014 Power Five',d[d.power_2014.eq(1)&d.year.ge(2015)]),
        ('Other 2014 FBS',d[d.power_2014.eq(0)&d.year.ge(2015)])]
    rng=np.random.default_rng(547)
    for label,frame in groups:
        z=frame.merge(study.cases['R_annual'],on=['unitid','year'],validate='one_to_one')
        positive=z[z.change_expense_m.gt(0)].copy()
        by_school=positive.groupby('unitid')[['change_revenue_m','change_expense_m']].sum()
        boot=[]
        values=by_school.to_numpy()
        if len(values):
            for _ in range(1000):
                totals=values[rng.integers(0,len(values),len(values))].sum(axis=0)
                boot.append(totals[0]/totals[1])
        rows.append(dict(group=label,n=len(z),schools=z.unitid.nunique(),
            expense_increase_rows=len(positive),expense_decrease_rows=int(z.change_expense_m.lt(0).sum()),
            expense_unchanged_rows=int(z.change_expense_m.eq(0).sum()),
            revenue_covers_increase_rows=int(positive.change_revenue_m.ge(positive.change_expense_m).sum()),
            fraction_increases_covered=float(positive.change_revenue_m.ge(positive.change_expense_m).mean()),
            positive_cost_increase_sum_m=positive.change_expense_m.sum(),
            matching_revenue_change_sum_m=positive.change_revenue_m.sum(),
            observed_recovery_ratio=positive.change_revenue_m.sum()/positive.change_expense_m.sum() if len(positive) else np.nan,
            bootstrap_ratio_low=np.quantile(boot,.025) if boot else np.nan,
            bootstrap_ratio_high=np.quantile(boot,.975) if boot else np.nan,
            interpretation='Descriptive selection on observed positive expense changes; not causal ROI or the adjusted regression slope'))
    pd.DataFrame(rows).to_csv(ROOT/'results/return_observed_coverage.csv',index=False)
    # Matched endpoints within each period; missing endpoint observations excluded.
    for label,start,end in [('Full historical period',2010,2019),('After baseline',2013,2019)]:
        a=d[d.year.eq(start)][['unitid','expense_m','revenue_m','support_m','total_m']]
        b=d[d.year.eq(end)][['unitid','expense_m','revenue_m','support_m','total_m']]
        z=a.merge(b,on='unitid',suffixes=('_start','_end'),validate='one_to_one').dropna()
        for col in ['expense_m','revenue_m','support_m','total_m']:
            endpoint.append(dict(period=label,start=start,end=end,schools=len(z),measure=col,
                start_sum_m=z[col+'_start'].sum(),end_sum_m=z[col+'_end'].sum(),
                change_sum_m=(z[col+'_end']-z[col+'_start']).sum(),
                interpretation='Matched reporting programs, constant 2019 dollars; amounts are aggregate annual flows at endpoints'))
    pd.DataFrame(endpoint).to_csv(ROOT/'results/return_matched_endpoints.csv',index=False)
    annual=d.dropna(subset=['expense_m','revenue_m','support_m','total_m','fees_per_student'])
    annual.groupby('year').agg(n=('unitid','size'),schools=('unitid','nunique'),
        sum_expense_m=('expense_m','sum'),sum_revenue_m=('revenue_m','sum'),sum_support_m=('support_m','sum'),
        median_support_pct_expense=('support_pct_expense','median'),median_fees_per_student=('fees_per_student','median'),
        programs_revenue_covers_total_expense=('gap_m',lambda x:int(x.le(0).sum()))).to_csv(ROOT/'results/return_annual_accounting.csv')
    risk=d[d.year.ge(2013)&d.revenue_m.gt(0)&d.pre_revenue_m.gt(0)&d.high_support.notna()].copy()
    risk['revenue_growth']=np.log(risk.revenue_m/risk.pre_revenue_m)
    volatility=risk.groupby(['unitid','high_support']).revenue_growth.agg(['std','count']).reset_index()
    volatility=volatility[volatility['count'].ge(5)]
    volatility.groupby('high_support').agg(schools=('unitid','size'),median_annual_log_growth_sd=('std','median'),
        mean_annual_log_growth_sd=('std','mean')).to_csv(ROOT/'results/return_revenue_volatility.csv')


def record_run():
    files=['data/private/feasibility_panel.csv','data/private/return_panel.csv',
           'results/return_models.csv','config/return_plan.json','data/processed/cpi_u_annual.csv']
    manifest=dict(executed_utc=datetime.now(timezone.utc).isoformat(),python=platform.python_version(),
        packages={p:version(p) for p in ['numpy','pandas','scipy','statsmodels','matplotlib']},
        plan_commit='a45a7a6',known_prior_results='Expanded feasibility study f0b7406 was already known',
        hashes={p:(hashlib.sha256((ROOT/p).read_bytes()).hexdigest() if p.startswith('data/private/') else text_sha256(ROOT/p)) for p in files},
        code={str(p.relative_to(ROOT)):text_sha256(p) for p in sorted((ROOT/'scoreboard').glob('*.py'))})
    (ROOT/'data/provenance/return_execution.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--download',action='store_true')
    parser.add_argument('--report-only',action='store_true')
    parser.add_argument('--no-influence',action='store_true')
    args=parser.parse_args()
    if not args.report_only:
        if args.download:acquire_cpi()
        d=build()
        models,_=estimate_all(d,influence=not args.no_influence)
        expected={'cost_recovery':2,'school_types':3,'self_support':6,'small_school_breakthrough':3}
        counts=models.loc[models.primary].groupby('family').size().to_dict()
        if counts!=expected:raise ValueError(f'Primary planned tests missing: {counts}')
        record_run()
        from .validate_returns import main as validate
        validate()
    from .return_report import main as report
    report()


if __name__=='__main__':main()
