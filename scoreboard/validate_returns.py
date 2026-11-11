"""Independent source and full-rank numerical checks for the CFO extension."""
import json

import numpy as np
import pandas as pd
from scipy import linalg
import statsmodels.api as sm

from .download import ROOT
from .hashes import text_sha256


def dummy_reference(sample,y,x,controls,levels=False,effects='conference_year'):
    terms=[*x,*controls]
    fixed=pd.get_dummies(sample[effects].astype(str),dtype=float).to_numpy()
    if levels:
        fixed=np.column_stack([pd.get_dummies(sample.unitid,dtype=float).to_numpy(),fixed])
    _,r,pivot=linalg.qr(fixed,pivoting=True,mode='economic')
    rank=np.linalg.matrix_rank(r)
    design=np.column_stack([sample[terms].to_numpy(float),fixed[:,pivot[:rank]]])
    if np.linalg.matrix_rank(design)!=design.shape[1]:raise ValueError('Independent reference rank failure')
    return sm.OLS(sample[y].to_numpy(float),design).fit(cov_type='cluster',
        cov_kwds={'groups':sample.unitid.to_numpy()},use_t=True)


def main():
    d=pd.read_csv(ROOT/'data/private/return_panel.csv')
    original=pd.read_csv(ROOT/'data/private/feasibility_panel.csv')
    paired=d.merge(original,on=['unitid','year'],suffixes=('','_source'),validate='one_to_one')
    preserved=['kn_expenses','total_revenue','institution_government_support','student_fees',
        'ticket_sales','donor_contributions','football_spending','football_coaching_salaries',
        'net_nonallocated_revenue_proxy','fpi','log_applications','log_first_time_enrollment']
    for col in preserved:
        if not np.allclose(paired[col],paired[col+'_source'],equal_nan=True,rtol=1e-12,atol=1e-8):
            raise ValueError('Source observations changed: '+col)
    if len(paired)!=len(original):raise ValueError('Source rows lost')
    for lhs,rhs in [(d.revenue_m+d.support_m,d.total_m),
                    (d.gap_m,d.support_m+d.expense_m-d.total_m)]:
        if not np.allclose(lhs,rhs,equal_nan=True,rtol=1e-12,atol=1e-9):raise ValueError('Accounting identity failed')
    models=pd.read_csv(ROOT/'results/return_models.csv')
    checks=[]
    for name,y,x,controls,levels in [
        ('R_annual','change_revenue_m',['change_expense_m'],['change_log_total_enrollment'],False),
        ('R_three_year','cumulative_revenue_m',['cumulative_expense_m'],['cumulative_log_enrollment_change'],False),
        ('H_high_support','change_revenue_m',['change_expense_m','high_support','spend_x_high_support'],['change_log_total_enrollment'],False),
        ('S_fpi_support_m','future_support_m',['fpi_10'],['lag_log_total_enrollment'],True),
        ('U_small_revenue','next_log_net_nonallocated_revenue_proxy',['outperformance_10','outperformance_x_small_budget_fbs'],['lag_fpi_10','lag_log_total_enrollment'],True)]:
        sample=pd.read_csv(ROOT/f'data/private/return_samples/{name}.csv')
        fit=dummy_reference(sample,y,x,controls,levels)
        for index,term in enumerate([*x,*controls]):
            row=models[models.model.eq(name)&models.term.eq(term)].iloc[0]
            for key,value in [('coefficient',fit.params[index]),('std_error',fit.bse[index]),('p_value',fit.pvalues[index])]:
                if not np.isclose(row[key],value,atol=2e-8,rtol=2e-6):raise ValueError(f'Independent fit differs: {name}/{term}/{key}')
        checks.append(dict(model=name,n=len(sample),schools=sample.unitid.nunique(),status='passed'))
    # Both sides of the accounting bridge must be fitted on identical cases.
    for prefix,term,expense,revenue,gap in [
        ('R_bridge_','change_expense_m',None,'change_revenue_m','change_gap_m'),
        *[(f'S_bridge_{metric}_',x,'expense_m','revenue_m','gap_m') for metric,x in
          [('cup','cup_100'),('fpi','fpi_10'),('sweet16','sweet16')]]]:
        def row(out):return models[models.model.eq(prefix+out)&models.term.eq(term)].iloc[0]
        e=1. if expense is None else row(expense).coefficient
        if not np.isclose(e-row(revenue).coefficient,row(gap).coefficient,atol=1e-8):raise ValueError('Shared-sample coefficient identity failed')
        names=[revenue,gap]+([] if expense is None else [expense])
        samples=[pd.read_csv(ROOT/f'data/private/return_samples/{prefix+name}.csv')[['unitid','year']].sort_values(['unitid','year']).reset_index(drop=True) for name in names]
        if not all(samples[0].equals(k) for k in samples[1:]):raise ValueError('Accounting bridge uses different cases')
    validation=dict(status='passed',source_rows_preserved=len(paired),accounting_identities='passed',
        full_rank_independent_OLS=checks,shared_case_coefficient_bridges='passed',
        models_sha256=text_sha256(ROOT/'results/return_models.csv'),
        caveat='Numerical agreement and accounting identities do not establish causal identification')
    (ROOT/'data/provenance/return_validation.json').write_text(json.dumps(validation,indent=2),encoding='utf-8')
    print(json.dumps(validation,indent=2))


if __name__=='__main__':main()
