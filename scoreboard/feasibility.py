"""Execute the specified three-part observational feasibility study in Python."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import platform
from importlib.metadata import version

import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.api as sm
from statsmodels.stats.multitest import multipletests

from .clean import calendar_join
from .download import ROOT
from .models import fixed_effects
from .hashes import text_sha256

METRICS={'cup':'cup_100','fpi':'fpi_10','sweet16':'sweet16'}
REVENUES=['ticket_sales','donor_contributions','net_nonallocated_revenue_proxy']
DEMAND=['applications','first_time_enrollment']


def primary_specs():
    specs=[dict(model='A_spend_cup',family='spending_success',stage='Spending → success',
                metric='cup',y='cup_100',x='lag_log_kn_expenses',
                controls=['lag_log_total_enrollment','lag_sport_categories']),
           dict(model='A_spend_fpi',family='spending_success',stage='Spending → success',
                metric='fpi',y='fpi_10',x='lag_log_football_spending',
                controls=['lag_log_total_enrollment','lag_sport_categories']),
           dict(model='A_spend_sweet16',family='spending_success',stage='Spending → success',
                metric='sweet16',y='sweet16',x='lag_log_mbb_expenses',
                controls=['lag_log_total_enrollment','lag_sport_categories'])]
    for metric,x in METRICS.items():
        for revenue in REVENUES:
            specs.append(dict(model=f'B_{metric}_{revenue}',family='success_finance',
                stage='Success → athletics finances',metric=metric,y='next_log_'+revenue,
                x=x,controls=['lag_log_total_enrollment']))
        for outcome in DEMAND:
            prefix='' if metric=='fpi' else 'next_'
            specs.append(dict(model=f'C_{metric}_{outcome}',family='flutie',
                stage='Success → student demand',metric=metric,y=prefix+'log_'+outcome,
                x=x,controls=['lag_log_total_enrollment']))
    return specs


def year_effects_ols(frame,y,x,controls,*,time_effect='year'):
    columns=list(dict.fromkeys([y,*x,*controls,'unitid','year',time_effect]))
    d=frame[columns].replace([np.inf,-np.inf],np.nan).dropna().copy()
    n=len(d);g=d.unitid.nunique()
    if n<50 or g<20:raise ValueError('Insufficient observations/clusters for differenced model')
    design=sm.add_constant(pd.concat([d[[*x,*controls]].astype(float),
        pd.get_dummies(d[time_effect].astype(str),drop_first=True,dtype=float)],axis=1),has_constant='add')
    if np.linalg.matrix_rank(design)!=design.shape[1]:raise ValueError('Differenced design is rank deficient')
    fitted=sm.OLS(d[y].astype(float),design).fit(cov_type='cluster',
        cov_kwds={'groups':d.unitid},use_t=True)
    critical=stats.t.ppf(.975,g-1)
    rows=[]
    for term in [*x,*controls]:
        b=float(fitted.params[term]);se=float(fitted.bse[term])
        rows.append(dict(term=term,coefficient=b,std_error=se,
            p_value=2*stats.t.sf(abs(b/se),g-1),ci_low=b-critical*se,ci_high=b+critical*se,
            n=n,schools=g,year_min=int(d.year.min()),year_max=int(d.year.max()),
            within_r2=fitted.rsquared,outcome=y,controls=';'.join(controls),
            fixed_effects=time_effect+';first_differences',cluster='school',df_resid=fitted.df_resid))
    return rows,d[['unitid','year']]


class Study:
    def __init__(self,data):
        self.data=data
        self.results=[];self.status=[];self.flows=[];self.cases={}
        self.support=[]

    def estimate(self,spec,frame,*,name=None,primary=False,time_effect='conference_year',
                 x=None,y=None,controls=None,trends=False,contrasts=None,difference=False,
                 case_keys=None,difference_effect='year'):
        model=name or spec['model']
        y=y or spec['y'];x=x or [spec['x']]
        controls=spec['controls'] if controls is None else controls
        d=frame.copy()
        if difference:
            d=calendar_join(d,[y,*x,*controls],-1,'difference_previous_')
            for col in [y,*x,*controls]:d[col]=d[col]-d['difference_previous_'+col]
        if case_keys is not None:
            d=d.merge(case_keys[['unitid','year']],on=['unitid','year'],validate='one_to_one')
            self.flows.append(dict(model=model,step=-1,reason='common_case_filter',excluded=len(frame)-len(d),remaining=len(d)))
        columns=list(dict.fromkeys([y,*x,*controls,'unitid','year',difference_effect if difference else time_effect]))
        remaining=d.copy()
        for order,col in enumerate(columns):
            mask=remaining[col].notna()
            if pd.api.types.is_numeric_dtype(remaining[col]):mask&=np.isfinite(remaining[col])
            self.flows.append(dict(model=model,step=order,reason='missing_or_nonfinite_'+col,
                excluded=int((~mask).sum()),remaining=int(mask.sum())))
            remaining=remaining[mask]
        try:
            if difference:rows,residuals=year_effects_ols(d,y,x,controls,time_effect=difference_effect)
            else:rows,residuals=fixed_effects(d,y,x,controls,time_effect=time_effect,
                school_trends=trends,contrasts=contrasts)
            for row in rows:
                row.update(model=model,family=spec['family'] if primary else 'secondary',
                    stage=spec['stage'],metric=spec['metric'],primary=primary,
                    exposure_term=row['term'] in x,difference=difference)
                if not np.isfinite([row['coefficient'],row['std_error'],row['p_value']]).all():
                    raise ValueError('Nonfinite coefficient/inference')
            self.results.extend(rows)
            self.cases[model]=residuals[['unitid','year']].copy()
            sample=d.merge(residuals[['unitid','year']],on=['unitid','year'],validate='one_to_one')
            folder=ROOT/'data/private/feasibility_samples';folder.mkdir(exist_ok=True)
            sample[columns].to_csv(folder/f'{model}.csv',index=False)
            # Report effective support for rare visibility events, especially
            # subgroup interactions that can be driven by a single program.
            for term in x:
                values=sample[term].dropna()
                if values.isin([0,1]).all():
                    groups=[('all',sample)]
                    if 'other_fbs' in sample and spec['stage']=='Power5 versus other FBS':
                        groups += [('power_five',sample[sample.other_fbs.eq(0)]),
                                   ('other_fbs',sample[sample.other_fbs.eq(1)])]
                    for label,g in groups:
                        self.support.append(dict(model=model,term=term,group=label,n=len(g),
                            schools=g.unitid.nunique(),event_rows=int(g[term].eq(1).sum()),
                            event_schools=g.loc[g[term].eq(1),'unitid'].nunique(),
                            switching_schools=int(g.groupby('unitid')[term].nunique().ge(2).sum())))
            self.flows.append(dict(model=model,step=len(columns),reason='absorbed_singletons',
                excluded=len(remaining)-rows[0]['n'],remaining=rows[0]['n']))
            self.status.append(dict(model=model,status='estimated',primary=primary,
                initial_n=len(frame),n=rows[0]['n'],schools=rows[0]['schools']))
            return rows
        except (ValueError,np.linalg.LinAlgError) as exc:
            self.status.append(dict(model=model,status='not_estimable',primary=primary,
                initial_n=len(frame),n=0,schools=0,reason=str(exc)))
            print('Not estimable:',model,str(exc),flush=True)
            return []

    def save(self):
        models=pd.DataFrame(self.results)
        models['holm_family_p']=np.nan;models['holm_all_primary_p']=np.nan
        primary=models.primary&models.exposure_term
        for family in ['spending_success','success_finance','flutie']:
            mask=primary&models.family.eq(family)
            models.loc[mask,'holm_family_p']=multipletests(models.loc[mask,'p_value'],method='holm')[1]
        models.loc[primary,'holm_all_primary_p']=multipletests(models.loc[primary,'p_value'],method='holm')[1]
        models.to_csv(ROOT/'results/feasibility_models.csv',index=False)
        pd.DataFrame(self.status).to_csv(ROOT/'results/feasibility_model_status.csv',index=False)
        pd.DataFrame(self.flows).to_csv(ROOT/'results/feasibility_sample_flow.csv',index=False)
        pd.DataFrame(self.support).to_csv(ROOT/'results/feasibility_event_support.csv',index=False)
        return models


def pilot_audit(data):
    """Independent public-school checks; never select 52 to mimic the pilot."""
    f=data[data.primary_eligible&data.year.between(2014,2019)&data.fpi.notna()].copy()
    correlations=[]
    def describe(frame,label):
        for x,y,claim in [('football_spending','fpi',.556),
                          ('football_coaching_salaries','fpi',.646),('fpi','ticket_sales',.479)]:
            z=frame[['unitid','year',x,y]].dropna()
            correlations.append(dict(sample=label,x=x,y=y,relation='pooled_school_years',
                pearson_r=z[x].corr(z[y]),n=len(z),schools=z.unitid.nunique(),prior_claim=claim))
            between=z.groupby('unitid')[[x,y]].mean()
            correlations.append(dict(sample=label,x=x,y=y,relation='between_school_means',
                pearson_r=between[x].corr(between[y]),n=len(between),schools=len(between),prior_claim=np.nan))
            within=z[[x,y]]-z.groupby('unitid')[[x,y]].transform('mean')
            correlations.append(dict(sample=label,x=x,y=y,relation='within_school_demeaned',
                pearson_r=within[x].corr(within[y]),n=len(z),schools=z.unitid.nunique(),prior_claim=np.nan))
    describe(f,'FY2014-2019 aligned with football seasons2013-2018')
    # Restrict the football season as stated in the earlier conversation;
    # source finances end FY2019, so the aligned 2019 football season is absent.
    describe(f[f.season.between(2014,2019)],'Football seasons2014-2018 observed within FY2010-2019 export')
    describe(f[~f.year.between(2015,2017)],'Coach comparability check excluding FY2015-2017')
    historical=pd.read_csv(ROOT/'data/processed/football_fpi.csv').dropna(subset=['unitid'])
    naive=data[data.primary_eligible&data.year.between(2014,2019)].drop(columns=['fpi','season']).merge(
        historical[['unitid','season','fpi']],left_on=['unitid','year'],right_on=['unitid','season'],
        how='inner',validate='one_to_one')
    naive['fpi_10']=naive.fpi/10
    describe(naive,'Timing diagnostic ONLY: same printed fiscal and football-season labels2014-2019')
    pd.DataFrame(correlations).to_csv(ROOT/'results/pilot_correlations.csv',index=False)
    spec=dict(model='pilot_fpi_ticket',family='pilot',stage='Pilot validation',metric='fpi',
        y='next_log_ticket_sales',x='fpi_10',controls=[])
    study=Study(data)
    study.estimate(spec,f,primary=False,time_effect='year')
    study.estimate(spec,f,name='pilot_fpi_ticket_size_adjusted',time_effect='year',controls=['lag_log_total_enrollment'])
    study.estimate(spec,f[f.season.between(2014,2019)],name='pilot_season2014plus_ticket',time_effect='year')
    study.estimate(spec,naive,name='pilot_same_label_timing_diagnostic',time_effect='year')
    pd.DataFrame(study.results).to_csv(ROOT/'results/pilot_models.csv',index=False)
    pd.DataFrame(study.status).to_csv(ROOT/'results/pilot_model_status.csv',index=False)
    for model,cases in study.cases.items():cases.to_csv(ROOT/f'data/private/feasibility_samples/{model}_keys.csv',index=False)
    return correlations


def run_models(data,influence=True):
    data=data.copy()
    # Zero is retained in the source count but is not a credible DI team-count
    # control. A positive-value rule avoids treating unreported participation as
    # a university sponsoring no sports; no sports are invented.
    data['lag_sport_categories']=data.lag_sport_categories.where(data.lag_sport_categories>0)
    base=data[data.primary_eligible].copy()
    all_di=data[data.public&data.di_eligible].copy()
    study=Study(data);specs=primary_specs()
    for spec in specs:study.estimate(spec,base,primary=True)
    models=study.save()
    print('Primary estimates\n',models[models.primary&models.exposure_term][
        ['model','coefficient','ci_low','ci_high','p_value','holm_family_p','n','schools']].to_string(index=False),flush=True)
    # Each primary model also receives the simpler school/year specification.
    for spec in specs:
        study.estimate(spec,base,name=spec['model']+'_school_year',time_effect='year')
        if spec['metric']!='fpi':
            study.estimate(spec,all_di,name=spec['model']+'_include_mergers')
        if spec['family'] in ['success_finance','flutie']:
            study.estimate(spec,base,name=spec['model']+'_prior_budget',
                controls=[*spec['controls'],'lag_log_kn_expenses'])
        if spec['metric']=='cup':
            study.estimate(spec,base[base.year<2018],name=spec['model']+'_pre2018')
            complete=base.groupby('unitid').cup_points.count()
            study.estimate(spec,base[base.unitid.isin(complete[complete.eq(10)].index)],name=spec['model']+'_balanced_cup')
    for spec in specs[:3]:
        study.estimate(spec,base,name=spec['model']+'_current_spending',x=[spec['x'].removeprefix('lag_')])
    study.estimate(specs[0],base,name='A_spend_cup_rank',y='cup_rank_better_50')
    study.estimate(specs[0],base,name='A_spend_cup_percentile',y='cup_percentile_success')
    # Same FBS school-years for the aggregate/sport comparison. All predictors
    # use the same outcome fall here, t+1, to avoid a timing/sample comparison.
    for y in ['next_log_applications','next_log_first_time_enrollment',
              *['next_log_'+r for r in REVENUES]]:
        common=base.dropna(subset=[y,*METRICS.values(),'lag_log_total_enrollment','conference_year'])
        for label,x in [('aggregate',['cup_100']),('football',['fpi_10']),
                        ('basketball',['sweet16']),('joint',list(METRICS.values()))]:
            spec=dict(model=f'common_{y}_{label}',family='secondary',stage='Common-sample comparison',
                metric=label,y=y,x=x[0],controls=['lag_log_total_enrollment'])
            study.estimate(spec,common,x=x)
    # Alternative success measures chosen by visibility/previous literature.
    for exposure in ['win_pct_10pp','ap_top20','preseason_unranked_breakthrough']:
        for y in ['log_applications','log_first_time_enrollment',*['next_log_'+r for r in REVENUES]]:
            spec=dict(model=f'football_{exposure}_{y}',family='secondary',stage='Football visibility',
                metric=exposure,y=y,x=exposure,controls=['lag_log_total_enrollment'])
            study.estimate(spec,base)
    for y in ['next_log_applications','next_log_first_time_enrollment',*['next_log_'+r for r in REVENUES]]:
        spec=dict(model=f'basketball_main64_{y}',family='secondary',stage='Basketball visibility',
            metric='main64',y=y,x='main64',controls=['lag_log_total_enrollment'])
        study.estimate(spec,base)
    for spec in specs:
        if spec['family']=='success_finance':
            study.estimate(spec,base,name=spec['model']+'_ihs',y=spec['y'].replace('log_','ihs_'))
            study.estimate(spec,base,name=spec['model']+'_extra_year',y=spec['y'].replace('next_','next2_'))
        if spec['family']=='flutie':
            flag='xapplcn' if spec['y'].endswith('log_applications') else 'first_time_enrollment_flag'
            prefix='' if spec['metric']=='fpi' else 'next_'
            study.estimate(spec,base[base[prefix+flag].eq('R')],name=spec['model']+'_reported_only')
            alternate=('next_'+spec['y']) if spec['metric']=='fpi' else spec['y'].replace('next_','')
            study.estimate(spec,base,name=spec['model']+'_alternate_fall',y=alternate)
            if spec['metric']!='fpi':
                study.estimate(spec,base,name=spec['model']+'_extra_year',y=spec['y'].replace('next_','next2_'))
    selected=['B_fpi_ticket_sales','B_fpi_net_nonallocated_revenue_proxy',
              'C_cup_applications','C_fpi_applications','C_sweet16_applications']
    for spec in specs:
        if spec['model'] in selected:
            study.estimate(spec,base,name=spec['model']+'_first_differences',difference=True)
            study.estimate(spec,base,name=spec['model']+'_school_trends',trends=True,time_effect='year')
            lo,hi=base.kn_expenses.quantile([.01,.99])
            study.estimate(spec,base[base.kn_expenses.between(lo,hi)],name=spec['model']+'_trim_expense_tails')
    # Separate a growth estimator change from a sample/control change. Transform
    # differences on the full exact-calendar panel before restricting cases.
    bb=next(s for s in specs if s['model']=='C_sweet16_applications')
    fd_cases=study.cases['C_sweet16_applications_first_differences']
    study.estimate(bb,base,name='C_sweet16_common_fd_level_conference_year',case_keys=fd_cases)
    common=study.cases['C_sweet16_common_fd_level_conference_year']
    study.estimate(bb,base,name='C_sweet16_common_fd_level_year',case_keys=common,time_effect='year')
    study.estimate(bb,base,name='C_sweet16_common_fd_changes_year',case_keys=common,difference=True)
    study.estimate(bb,base,name='C_sweet16_common_fd_changes_conference_year',case_keys=common,
        difference=True,difference_effect='conference_year')
    study.estimate(bb,base,name='C_sweet16_common_fd_school_trends',case_keys=common,
        time_effect='year',trends=True)
    # A direct interaction tests differences, rather than comparing two p values.
    for metric,x in METRICS.items():
        for y in [('log_applications' if metric=='fpi' else 'next_log_applications'),
                  'next_log_net_nonallocated_revenue_proxy']:
            h=base[base.year.between(2015,2019)&base.other_fbs.notna()].copy()
            h['success_other']=h[x]*h.other_fbs
            spec=dict(model=f'heterogeneity_{metric}_{y}',family='secondary',stage='Power5 versus other FBS',
                metric=metric,y=y,x=x,controls=['lag_log_total_enrollment'])
            study.estimate(spec,h,x=[x,'success_other'],contrasts={
                'effect_power_five':{x:1},'effect_other_fbs':{x:1,'success_other':1}})
    for y in ['log_applications','log_first_time_enrollment','next_log_ticket_sales']:
        spec=dict(model=f'outperformance_{y}',family='secondary',stage='Historical prominence',
            metric='outperformance',y=y,x='outperformance_10',controls=['lag_log_total_enrollment','lag_fpi_10'])
        study.estimate(spec,base,x=['outperformance_10','outperformance_low_prominence'],contrasts={
            'effect_higher_prominence':{'outperformance_10':1},
            'effect_lower_prominence':{'outperformance_10':1,'outperformance_low_prominence':1}})
    # Replication-style comparison with the 2024 win-percentage paper. The
    # sample is public schools, with fewer controls than that paper; not an
    # exact replication of its 121-school specification.
    h=base[base.year.between(2015,2019)&base.other_fbs.notna()].copy()
    h['wins_other']=h.win_pct_10pp*h.other_fbs
    published=dict(model='published_comparison_winpct',family='secondary',stage='Published-research comparison',
        metric='win_pct_10pp',y='log_applications',x='win_pct_10pp',controls=['lag_log_total_enrollment'])
    for effect in ['conference_year','year']:
        study.estimate(published,h,name='published_comparison_winpct_'+effect,
            x=['win_pct_10pp','wins_other'],time_effect=effect,contrasts={
                'effect_power_five':{'win_pct_10pp':1},'effect_other_fbs':{'win_pct_10pp':1,'wins_other':1}})
    for y in ['log_applications','next_log_ticket_sales']:
        h=base.copy()
        h['breakthrough_lower']=h.preseason_unranked_breakthrough*h.low_prominence
        spec=dict(model='breakthrough_prominence_'+y,family='secondary',stage='Historical prominence',
            metric='breakthrough',y=y,x='preseason_unranked_breakthrough',controls=['lag_log_total_enrollment'])
        study.estimate(spec,h,x=['preseason_unranked_breakthrough','breakthrough_lower'],contrasts={
            'effect_higher_prominence':{'preseason_unranked_breakthrough':1},
            'effect_lower_prominence':{'preseason_unranked_breakthrough':1,'breakthrough_lower':1}})
    coach=dict(model='coaching_to_fpi',family='secondary',stage='Coaching reporting sensitivity',
        metric='fpi',y='fpi_10',x='lag_log_football_coaching_salaries',controls=['lag_log_total_enrollment','lag_sport_categories'])
    study.estimate(coach,base)
    study.estimate(coach,base[~(base.year-1).between(2015,2017)],name='coaching_to_fpi_comparable_years')
    models=study.save()
    if influence:
        sensitivity=[]
        influence_specs=[s for s in specs if s['model'] in selected]
        fd=next(s.copy() for s in specs if s['model']=='C_sweet16_applications')
        fd['model']='C_sweet16_applications_first_differences';fd['difference']=True
        influence_specs.append(fd)
        for spec in influence_specs:
            keys=study.cases.get(spec['model'])
            if keys is None:continue
            matched=pd.read_csv(ROOT/f'data/private/feasibility_samples/{spec["model"]}.csv')
            for uid in sorted(matched.unitid.unique()):
                try:
                    if spec.get('difference'):
                        rows,_=year_effects_ols(matched[matched.unitid.ne(uid)],spec['y'],[spec['x']],spec['controls'])
                    else:
                        rows,_=fixed_effects(matched[matched.unitid.ne(uid)],spec['y'],[spec['x']],
                            spec['controls'],time_effect='conference_year')
                    sensitivity.append(dict(model=spec['model'],omitted_unitid=int(uid),
                        coefficient=rows[0]['coefficient'],p_value=rows[0]['p_value'],
                        n=rows[0]['n'],schools=rows[0]['schools']))
                except ValueError as exc:
                    sensitivity.append(dict(model=spec['model'],omitted_unitid=int(uid),reason=str(exc)))
            print('Influence checks complete:',spec['model'],len(matched.unitid.unique()),'omissions',flush=True)
        pd.DataFrame(sensitivity).to_csv(ROOT/'results/feasibility_influence.csv',index=False)
    else:
        pd.DataFrame(columns=['model','omitted_unitid','coefficient','p_value','n','schools']).to_csv(
            ROOT/'results/feasibility_influence.csv',index=False)
    return models


def record_execution():
    panel=ROOT/'data/private/feasibility_panel.csv'
    results=ROOT/'results/feasibility_models.csv'
    plan=ROOT/'config/feasibility_plan.json'
    metadata=dict(execution_recorded_utc=datetime.now(timezone.utc).isoformat(),
        panel_sha256=hashlib.sha256(panel.read_bytes()).hexdigest(),
        results_sha256=text_sha256(results),
        plan_sha256=text_sha256(plan),
        source_workbook_sha256=json.loads((ROOT/'data/provenance/knight_acquisition.json').read_text(encoding='utf-8'))['sha256'],
        plan='config/feasibility_plan.json',initial_plan_commit='629d6ca',primary_tests=len(primary_specs()),
        full_results='results/feasibility_models.csv',private_samples='data/private/feasibility_samples',
        causal_identification=False,original_52_school_pilot_membership_available=False)
    metadata['python_version']=platform.python_version()
    metadata['tracked_text_hash_convention']='CRLF normalized to LF; ignored binary sources and private panel use byte-exact hashes'
    metadata['package_versions']={name:version(name) for name in ['pandas','numpy','scipy','statsmodels','matplotlib','openpyxl']}
    metadata['code_sha256']={str(p.relative_to(ROOT)).replace('\\','/'):text_sha256(p)
        for p in sorted((ROOT/'scoreboard').glob('*.py'))}
    (ROOT/'data/provenance/feasibility_analysis_manifest.json').write_text(json.dumps(metadata,indent=2),encoding='utf-8')


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--download',action='store_true')
    p.add_argument('--build',action='store_true')
    p.add_argument('--no-influence',action='store_true')
    p.add_argument('--report-only',action='store_true')
    args=p.parse_args()
    if not args.report_only:
        if args.download:
            from .performance import download_sources
            download_sources()
        if args.build:
            from .performance import build_football,add_ap_visibility,basketball_events
            from .feasibility_data import main as build_data
            football=build_football()
            add_ap_visibility(football).to_csv(ROOT/'data/processed/football_visibility.csv',index=False)
            basketball_events();build_data()
        path=ROOT/'data/private/feasibility_panel.csv'
        if not path.exists():
            raise SystemExit('Registered Knight workbook staging is required. See docs/sources.md. Use --report-only to regenerate the report from published aggregate results.')
        data=pd.read_csv(path)
        run_models(data,influence=not args.no_influence)
        pilot_audit(data)
        record_execution()
    from .feasibility_report import main as report
    report()


if __name__=='__main__':main()
