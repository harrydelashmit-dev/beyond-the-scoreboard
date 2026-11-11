"""Exact-calendar, real-dollar CFO extension; school-level money stays private."""
import hashlib
import json

import numpy as np
import pandas as pd

from .clean import calendar_join, unique
from .download import ROOT, fetch
from .feasibility_data import POWER_FIVE

CPI_SOURCE = dict(source='U.S. Bureau of Labor Statistics, public API',
    file='economic/bls_api.json',
    url='https://api.bls.gov/publicAPI/v2/timeseries/data/CUUR0000SA0?startyear=2010&endyear=2019&annualaverage=true',
    series='CUUR0000SA0',restriction='Public federal statistical data; attribute BLS')


def annual_cpi(monthly):
    """Reject incomplete years, duplicates, wrong intervals and nonpositive CPI."""
    d=monthly.copy()
    if list(d.columns)!=['observation_date','CPIAUCNS']:
        raise ValueError('Unexpected CPI series headings')
    d['date']=pd.to_datetime(d.observation_date,errors='raise')
    d['value']=pd.to_numeric(d.CPIAUCNS,errors='raise')
    if d.date.duplicated().any() or d.value.le(0).any() or d.value.isna().any():
        raise ValueError('Duplicate/missing/nonpositive CPI')
    expected=pd.date_range('2010-01-01','2019-12-01',freq='MS')
    if sorted(d.date.tolist())!=expected.tolist():
        raise ValueError('CPI must contain every month in 2010-2019 exactly once')
    out=d.groupby(d.date.dt.year).value.mean().round(3).rename('cpi_u').rename_axis('year').reset_index()
    if not np.isclose(out.loc[out.year.eq(2019),'cpi_u'].iloc[0],255.657,atol=.0001):
        raise ValueError('CPI series does not match the published 2019 CPI-U annual average')
    return out


def parse_bls_cpi(payload):
    if payload.get('status')!='REQUEST_SUCCEEDED':raise ValueError('BLS API request failed')
    series=payload['Results']['series']
    if len(series)!=1 or series[0]['seriesID']!='CUUR0000SA0':raise ValueError('Wrong BLS CPI series')
    values=pd.DataFrame(series[0]['data'])
    if values.duplicated(['year','period']).any():raise ValueError('Duplicate BLS period')
    monthly=values[values.period.str.fullmatch(r'M(?:0[1-9]|1[0-2])')].copy()
    monthly['observation_date']=monthly.year+'-'+monthly.period.str[1:]+'-01'
    monthly['CPIAUCNS']=monthly.value
    computed=annual_cpi(monthly[['observation_date','CPIAUCNS']])
    annual=values[values.period.eq('M13')].copy()
    annual['year']=annual.year.astype(int)
    annual['cpi_u']=pd.to_numeric(annual.value,errors='raise')
    annual=annual[['year','cpi_u']].sort_values('year').reset_index(drop=True)
    if not np.array_equal(annual.year,computed.year) or not np.allclose(annual.cpi_u,computed.cpi_u,atol=.00051,rtol=0):
        raise ValueError('Published annual CPI does not match complete monthly observations')
    return annual


def acquire_cpi():
    metadata=fetch(CPI_SOURCE)
    if metadata['status']!='ok':raise ValueError(metadata.get('error','CPI download failed'))
    path=ROOT/'data/raw'/CPI_SOURCE['file']
    cpi=parse_bls_cpi(json.loads(path.read_text(encoding='utf-8')))
    cpi.to_csv(ROOT/'data/processed/cpi_u_annual.csv',index=False)
    metadata.update(aggregation='Published annual M13 CPI-U values verified against twelve monthly NSA CPI-U values; calendar-year fiscal approximation',
        basis='2019 dollars',official_definition='https://www.bls.gov/cpi/tables/supplemental-files/historical-cpi-u-202310.pdf')
    metadata['unused_initial_probe']='FRED graph CSV failed (remote disconnected). No observations were taken from the failed response.'
    (ROOT/'data/provenance/return_cpi_source.json').write_text(json.dumps(metadata,indent=2),encoding='utf-8')


def baseline_groups(d):
    """All baseline classifications require three genuinely observed years."""
    z=d[d.primary_eligible&d.year.between(2010,2012)].copy()
    rows=[]
    for uid,g in z.groupby('unitid'):
        row={'unitid':uid}
        for col in ['expense_m','support_m','log_total_enrollment']:
            values=g[col]
            row['baseline_'+col]=float(values.mean()) if len(g)==3 and values.notna().all() else np.nan
        # Support/expenses is a ratio of observed sums in the same years.
        valid=len(g)==3 and g[['expense_m','support_m']].notna().all().all() and g.expense_m.gt(0).all()
        row['baseline_support_fraction']=g.support_m.sum()/g.expense_m.sum() if valid else np.nan
        row['baseline_fbs']=bool(len(g)==3 and g.fpi.notna().all())
        rows.append(row)
    b=pd.DataFrame(rows)
    all_cut=float(b.baseline_expense_m.median())
    fbs_cut=float(b.loc[b.baseline_fbs,'baseline_expense_m'].median())
    enrollment_cut=float(b.loc[b.baseline_fbs,'baseline_log_total_enrollment'].median())
    b['small_budget_all']=b.baseline_expense_m.lt(all_cut).where(b.baseline_expense_m.notna()).astype(float)
    b['small_budget_fbs']=b.baseline_expense_m.lt(fbs_cut).where(b.baseline_expense_m.notna()&b.baseline_fbs).astype(float)
    b['small_enrollment_fbs']=b.baseline_log_total_enrollment.lt(enrollment_cut).where(b.baseline_log_total_enrollment.notna()&b.baseline_fbs).astype(float)
    b['high_support']=b.baseline_support_fraction.ge(.5).where(b.baseline_support_fraction.notna()).astype(float)
    membership=d[d.year.eq(2014)&d.fpi.notna()].set_index('unitid').fbs_conference
    b['power_2014']=b.unitid.map(membership).isin(POWER_FIVE).astype(float).where(b.unitid.map(membership).notna()&~b.unitid.map(membership).eq('Independent'))
    return b,dict(baseline_years=[2010,2011,2012],evaluation_begins=2013,
        all_DI_budget_median_2019_dollars=all_cut*1e6,FBS_budget_median_2019_dollars=fbs_cut*1e6,
        FBS_enrollment_geometric_median=float(np.exp(enrollment_cut)),high_support_cutoff=.5,
        power_comparison='2014 FBS conference frozen before 2015-2019 evaluation; exclude independents')


def cumulative_changes(d,horizon=3,discount=0.):
    """Annual flows versus the previous annual budget, not terminal levels."""
    if horizon<1 or discount<0:raise ValueError('Invalid horizon or discount rate')
    cols=['expense_m','revenue_m','support_m','total_m']
    out=calendar_join(d,cols+['log_total_enrollment'],-1,'cumulative_pre_')
    for h in range(1,horizon):out=calendar_join(out,cols+['log_total_enrollment'],h,f'cumulative_future{h}_')
    weights=[(1+discount)**(-h) for h in range(horizon)]
    for col in cols:
        values=[out[col]]+[out[f'cumulative_future{h}_{col}'] for h in range(1,horizon)]
        # Ordinary addition intentionally propagates any missing annual flow.
        amount=sum(v*w for v,w in zip(values,weights))-sum(weights)*out['cumulative_pre_'+col]
        out[f'cumulative_{col}']=amount
    end=out['log_total_enrollment'] if horizon==1 else out[f'cumulative_future{horizon-1}_log_total_enrollment']
    out['cumulative_log_enrollment_change']=end-out.cumulative_pre_log_total_enrollment
    return out


def build():
    source=ROOT/'data/private/feasibility_panel.csv'
    d=pd.read_csv(source)
    unique(d,['unitid','year'])
    cpi=pd.read_csv(ROOT/'data/processed/cpi_u_annual.csv')
    if sorted(cpi.year.tolist())!=list(range(2010,2020)) or cpi.year.duplicated().any():
        raise ValueError('Annual CPI coverage is incomplete')
    d=d.merge(cpi,on='year',validate='many_to_one').copy()
    factor=255.657/d.cpi_u/1e6
    d['expense_m']=d.kn_expenses*factor
    d['revenue_m']=d.net_nonallocated_revenue_proxy*factor
    d['support_m']=(d.institution_government_support+d.student_fees)*factor
    d['fees_m']=d.student_fees*factor
    d['total_m']=d.total_revenue*factor
    d['gap_m']=d.expense_m-d.revenue_m
    d['support_pct_expense']=100*d.support_m/d.expense_m.where(d.expense_m>0)
    d['fees_per_student']=d.fees_m*1e6/d.total_enrollment.where(d.total_enrollment>0)
    b,rules=baseline_groups(d)
    d=d.merge(b,on='unitid',how='left',validate='many_to_one')
    b.to_csv(ROOT/'data/private/return_baseline_groups.csv',index=False)
    cols=['expense_m','revenue_m','support_m','total_m','log_total_enrollment',
          'fees_per_student','support_pct_expense','gap_m']
    d=calendar_join(d,cols,-1,'pre_')
    d=calendar_join(d,cols,1,'future_')
    d=d.copy()
    for col in cols:d['change_'+col]=d[col]-d['pre_'+col]
    d['change_gap_m']=d.change_expense_m-d.change_revenue_m
    for group in ['small_budget_all','high_support','power_2014']:
        d['spend_x_'+group]=d.change_expense_m*d[group]
    for group in ['small_budget_fbs','small_enrollment_fbs','low_prominence']:
        d['outperformance_x_'+group]=d.outperformance_10*d[group]
        d['ap_breakthrough_x_'+group]=d.preseason_unranked_breakthrough*d[group]
    d['other_2014']=1-d.power_2014
    d['outperformance_x_other_2014']=d.outperformance_10*d.other_2014
    # Preserve source values, membership and calendar after transformations.
    if len(d)!=2400:raise ValueError('Unexpected source coverage')
    check=d.expense_m-d.revenue_m-d.gap_m
    if not np.allclose(check.dropna(),0,atol=1e-10):raise ValueError('Accounting bridge failed')
    rules.update(source_panel_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
        money='Millions of 2019 CPI-U dollars; source levels unchanged in feasibility_panel.csv',
        support='Institutional/government support + student fees. Gap and allocated support differ by reported total balance.',
        source_rows=len(d))
    (ROOT/'data/provenance/return_period_rules.json').write_text(json.dumps(rules,indent=2),encoding='utf-8')
    d.to_csv(ROOT/'data/private/return_panel.csv',index=False)
    return d


if __name__=='__main__':
    acquire_cpi()
    print('CPI acquired and verified; private panel rows:',len(build()))
