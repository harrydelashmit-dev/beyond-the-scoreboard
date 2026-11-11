"""Two-way fixed effects with school-clustered inference.

Sparse least squares projects out institution and year indicators. The
Frisch-Waugh-Lovell theorem makes coefficients identical to dummy-variable OLS.
The covariance small-sample correction counts absorbed fixed-effect parameters.
"""
import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix, hstack
from scipy.sparse.linalg import lsqr
from scipy import stats
import statsmodels.api as sm
from statsmodels.stats.multitest import multipletests
from .download import ROOT

def fixed_effects(data, outcome, exposures, controls=(), *, time_effect='year', school_trends=False, contrasts=None):
    cols=list(dict.fromkeys([outcome,*exposures,*controls,'unitid','year',time_effect]))
    d=data[cols].replace([np.inf,-np.inf],np.nan).dropna().copy()
    # Recursively remove singletons from either absorbed dimension: they have no
    # identifying within-cell variation, including in conference-by-year models.
    while len(d):
        keep=(d.groupby('unitid').unitid.transform('size')>=2)&(d.groupby(time_effect)[time_effect].transform('size')>=2)
        if keep.all():break
        d=d[keep].copy()
    if len(d)<50 or d.unitid.nunique()<20:raise ValueError('Insufficient observations/clusters for panel model')
    si,schools=pd.factorize(d.unitid);ti,years=pd.factorize(d[time_effect])
    n=len(d);g=len(schools);t=len(years)
    design=hstack([csr_matrix((np.ones(n),(np.arange(n),si)),shape=(n,g)),csr_matrix((np.ones(n),(np.arange(n),ti)),shape=(n,t))],format='csr')
    # Rank of bipartite institution-year incidence matrix = vertices-components.
    parent=list(range(g+t))
    def find(x):
        while parent[x]!=x:parent[x]=parent[parent[x]];x=parent[x]
        return x
    for a,b in zip(si,ti):parent[find(a)]=find(g+b)
    components=len({find(i) for i in range(g+t)})
    rank_fe=g+t-components
    if school_trends:
        trend=d.year.to_numpy(dtype=float)-d.year.mean()
        design=hstack([design,csr_matrix((trend,(np.arange(n),si)),shape=(n,g))],format='csr')
        rank_fe=np.linalg.matrix_rank(design.toarray())
    variables=[outcome,*exposures,*controls]
    projected=[]
    for col in variables:
        values=d[col].to_numpy(dtype=float)
        fit=lsqr(design,values,atol=1e-12,btol=1e-12,iter_lim=10000)
        residual=values-design@fit[0]
        if np.max(np.abs(design.T@residual))>1e-6*max(1,np.max(np.abs(values))):
            raise ValueError('Fixed effects projection did not converge')
        projected.append(residual)
    y=projected[0];x=np.column_stack(projected[1:])
    if np.linalg.matrix_rank(x)!=x.shape[1]:raise ValueError('Regressors have no independent within-school variation')
    fit=sm.OLS(y,x).fit()
    k=rank_fe+x.shape[1]
    if n<=k:raise ValueError('No residual degrees of freedom')
    bread=np.linalg.inv(x.T@x)
    score=x*fit.resid[:,None]
    sums=np.zeros((g,x.shape[1]));np.add.at(sums,si,score)
    covariance=bread@(sums.T@sums)@bread*(g/(g-1))*((n-1)/(n-k))
    se=np.sqrt(np.diag(covariance));critical=stats.t.ppf(.975,g-1)
    rows=[]
    for i,col in enumerate([*exposures,*controls]):
        b=fit.params[i];p=2*stats.t.sf(abs(b/se[i]),g-1)
        rows.append(dict(term=col,coefficient=b,std_error=se[i],p_value=p,ci_low=b-critical*se[i],ci_high=b+critical*se[i],n=n,schools=g,year_min=int(d.year.min()),year_max=int(d.year.max()),within_r2=fit.rsquared,outcome=outcome,controls=';'.join(controls),fixed_effects='school;'+time_effect+(';school_linear_trends' if school_trends else ''),cluster='school',df_resid=n-k))
    for name,weights in (contrasts or {}).items():
        columns=[*exposures,*controls]
        if set(weights)-set(columns):raise ValueError('Unknown term in linear contrast')
        w=np.array([weights.get(col,0) for col in columns])
        b=float(w@fit.params);s=float(np.sqrt(w@covariance@w))
        row=rows[0].copy()
        row.update(term=name,coefficient=b,std_error=s,p_value=2*stats.t.sf(abs(b/s),g-1),ci_low=b-critical*s,ci_high=b+critical*s)
        rows.append(row)
    residuals=d[['unitid','year']].copy();residuals['observed_within']=y;residuals['fitted_within']=fit.fittedvalues;residuals['residual']=fit.resid
    return rows,residuals

def run():
    d=pd.read_csv(ROOT/'data/processed/panel.csv')
    base=d[d.public & d.cup_observed].copy()
    results=[];status=[]
    def estimate(name,frame,y,x,controls=(),family='sensitivity'):
        rows,residuals=fixed_effects(frame,y,x,controls)
        for r in rows:r.update(model=name,family=family)
        results.extend(rows)
        residuals.to_csv(ROOT/f'results/residuals_{name}.csv',index=False)
        status.append(dict(model=name,status='estimated',n=rows[0]['n'],schools=rows[0]['schools']))
    estimate('spending_to_cup',base,'cup_100',['lag_log_expenses'],['lag_log_total_enrollment','lag_sport_categories'],'primary')
    estimate('cup_to_applications',base,'next_log_applications',['cup_100'],['lag_log_total_enrollment'],'primary')
    estimate('cup_to_enrollment',base,'next_log_first_time_enrollment',['cup_100'],['lag_log_total_enrollment'],'primary')
    estimate('cup_to_eada_reported_revenue',base,'next_log_reported_revenue',['cup_100'],['lag_log_total_enrollment'],'secondary_accounting')
    estimate('spending_contemporaneous',base,'cup_100',['log_expenses'],['log_total_enrollment','sport_categories'])
    estimate('apps_unadjusted_for_size',base,'next_log_applications',['cup_100'])
    estimate('apps_with_spending',base,'next_log_applications',['cup_100'],['lag_log_total_enrollment','lag_log_expenses','lag_sport_categories'])
    estimate('apps_two_year_lag',base,'next2_log_applications',['cup_100'],['lag_log_total_enrollment'])
    estimate('apps_growth',base,'application_growth',['cup_100'],['lag_log_total_enrollment'])
    estimate('apps_change_performance',base,'application_growth',['performance_change'],['lag_log_total_enrollment'])
    estimate('apps_percentile',base,'next_log_applications',['cup_percentile'],['lag_log_total_enrollment'])
    estimate('apps_pre_scoring_change',base[base.year<2018],'next_log_applications',['cup_100'],['lag_log_total_enrollment'])
    balanced=base.groupby('unitid').year.nunique();ids=balanced[balanced==10].index
    estimate('apps_balanced_cup',base[base.unitid.isin(ids)],'next_log_applications',['cup_100'],['lag_log_total_enrollment'])
    low,high=base.expenses.quantile([.01,.99])
    estimate('apps_trim_expense_tails',base[base.expenses.between(low,high)],'next_log_applications',['cup_100'],['lag_log_total_enrollment'])
    # This is a diagnostic, not a valid causal falsification design: persistent
    # success can be associated with past applications as well as future demand.
    estimate('apps_same_fall_timing_check',base,'log_applications',['cup_100'],['lag_log_total_enrollment'])
    for division,label in [(1,'fbs'),(2,'fcs'),(3,'nonfootball')]:
        estimate(f'apps_{label}',base[base.division_code==division],'next_log_applications',['cup_100'],['lag_log_total_enrollment'])
    if 'mbb_points' in base and 'fbs_points' in base:
        common=base[(base.division_code==1)&base.mbb_points.notna()&base.fbs_points.notna()]
        estimate('profile_vs_aggregate',common,'next_log_applications',['cup_100','fbs_10','mbb_10'],['lag_log_total_enrollment'],'secondary_profile')
        estimate('profile_common_aggregate_only',common,'next_log_applications',['cup_100'],['lag_log_total_enrollment'],'secondary_profile')
        estimate('football_spending_success',base[base.division_code==1],'fbs_10',['lag_log_football_expenses'],['lag_log_total_enrollment'],'secondary_profile')
        estimate('mbb_spending_success',base,'mbb_10',['lag_log_mbb_expenses'],['lag_log_total_enrollment'],'secondary_profile')
    table=pd.DataFrame(results)
    primary=(table.family=='primary') & table.term.isin(['lag_log_expenses','cup_100'])
    table.loc[primary,'holm_p_value']=multipletests(table.loc[primary,'p_value'],method='holm')[1]
    table.to_csv(ROOT/'results/models.csv',index=False)
    pd.DataFrame(status).to_csv(ROOT/'results/model_status.csv',index=False)
    base[['expenses','reported_revenue','cup_points','applications','first_time_enrollment','sport_categories']].describe(percentiles=[.25,.5,.75]).to_csv(ROOT/'results/descriptive_statistics.csv')
    base[['expenses','log_expenses','cup_points','applications','first_time_enrollment']].corr().to_csv(ROOT/'results/pooled_correlations.csv')
    base.groupby('year').agg(schools=('unitid','nunique'),median_expenses=('expenses','median'),median_points=('cup_points','median'),median_applications=('applications','median')).to_csv(ROOT/'results/annual_summary.csv')
    print(table[primary][['model','term','coefficient','ci_low','ci_high','p_value','holm_p_value','n','schools']].to_string(index=False))
    return d,table

if __name__=='__main__':run()
