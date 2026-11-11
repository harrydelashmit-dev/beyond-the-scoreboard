"""CFO extension checks target accounting, timing and inferential failure risks."""
import json

import numpy as np
import pandas as pd
import pytest
from scipy import stats
import statsmodels.api as sm
from statsmodels.stats.multitest import multipletests

from scoreboard.download import ROOT
from scoreboard.return_data import annual_cpi, baseline_groups, cumulative_changes
from scoreboard.returns import changes_ols


def test_cumulative_flows_propagate_missing_years_and_discount_both_sides():
    d=pd.DataFrame({'unitid':[1]*5,'year':[2010,2011,2012,2013,2015],
        'expense_m':[10.,12.,13.,14.,99.],'revenue_m':[5.,6.,7.,8.,99.],
        'support_m':[5.,6.,6.,6.,99.],'total_m':[10.,12.,13.,14.,198.],
        'log_total_enrollment':[1.,1.1,1.2,1.3,2.]})
    c=cumulative_changes(d).set_index('year')
    assert c.loc[2011,'cumulative_expense_m']==pytest.approx(9.)
    assert c.loc[2011,'cumulative_revenue_m']==pytest.approx(6.)
    assert c.loc[2011,'cumulative_log_enrollment_change']==pytest.approx(.3)
    assert np.isnan(c.loc[2012,'cumulative_expense_m'])
    discounted=cumulative_changes(d,discount=.03).set_index('year')
    expected=2+3/1.03+4/1.03**2
    assert discounted.loc[2011,'cumulative_expense_m']==pytest.approx(expected)


def test_cpi_requires_complete_monthly_coverage_and_correct_series_values():
    dates=pd.date_range('2010-01-01','2019-12-01',freq='MS')
    d=pd.DataFrame({'observation_date':dates,'CPIAUCNS':255.657})
    assert len(annual_cpi(d))==10
    with pytest.raises(ValueError,match='every month'):annual_cpi(d.iloc[1:])
    with pytest.raises(ValueError,match='Duplicate'):annual_cpi(pd.concat([d,d.iloc[:1]]))
    d.loc[0,'CPIAUCNS']=0
    with pytest.raises(ValueError,match='nonpositive'):annual_cpi(d)


def test_change_model_matches_full_dummy_ols_and_direct_contrast():
    rng=np.random.default_rng(77)
    d=pd.MultiIndex.from_product([range(35),range(2011,2018)],names=['unitid','year']).to_frame(index=False)
    d['conference_year']=(d.unitid%3).astype(str)+':'+d.year.astype(str)
    d['x']=rng.normal(size=len(d));d['z']=rng.normal(size=len(d))
    d['y']=.65*d.x-.2*d.z+.03*d.unitid+rng.normal(size=len(d))
    rr,_=changes_ols(d,'y',['x'],['z'],contrasts={'sum':{'x':1,'z':1}})
    design=pd.concat([d[['x','z']],pd.get_dummies(d.conference_year,drop_first=True,dtype=float)],axis=1)
    design['constant']=1.
    reference=sm.OLS(d.y,design).fit(cov_type='cluster',cov_kwds={'groups':d.unitid},use_t=True)
    assert rr[0]['coefficient']==pytest.approx(reference.params.x)
    assert rr[0]['std_error']==pytest.approx(reference.bse.x)
    assert rr[0]['p_value']==pytest.approx(reference.pvalues.x)
    w=np.array([1.,1.]+[0.]*(design.shape[1]-2))
    assert rr[2]['coefficient']==pytest.approx(float(w@reference.params))
    assert rr[2]['std_error']==pytest.approx(float(np.sqrt(w@reference.cov_params()@w)))


def test_baseline_groups_ignore_future_finances_and_require_three_years():
    rows=[]
    for uid in range(1,5):
        for year in range(2010,2015):
            rows.append(dict(unitid=uid,year=year,primary_eligible=True,
                expense_m=10*uid if year<=2012 else 99999.,support_m=6*uid,
                log_total_enrollment=np.log(1000*uid),fpi=1.,
                fbs_conference='Big Ten Conference' if uid<3 else 'Conference USA'))
    d=pd.DataFrame(rows)
    d.loc[d.unitid.eq(1)&d.year.eq(2011),'expense_m']=np.nan
    b,_=baseline_groups(d);b=b.set_index('unitid')
    assert np.isnan(b.loc[1,'small_budget_fbs'])
    assert b.loc[2,'baseline_expense_m']==20
    assert b.loc[2,'high_support']==1
    assert b.loc[4,'small_budget_fbs']==0


def test_saved_primary_return_tests_use_recovery_null_one_and_full_adjustment():
    path=ROOT/'results/return_models.csv'
    if not path.exists():pytest.skip('CFO extension outputs not yet built')
    d=pd.read_csv(path);p=d[d.primary].copy()
    assert p.groupby('family').size().to_dict()==dict(cost_recovery=2,school_types=3,self_support=6,small_school_breakthrough=3)
    assert p.loc[p.family.eq('cost_recovery'),'primary_null'].eq(1).all()
    expected=2*stats.t.sf(abs((p.coefficient-p.primary_null)/p.std_error),p.schools-1)
    assert np.allclose(p.test_p,expected,atol=1e-12)
    assert np.allclose(p.holm_all_primary_p,multipletests(p.test_p,method='holm')[1])
    for _,g in p.groupby('family'):
        assert np.allclose(g.holm_family_p,multipletests(g.test_p,method='holm')[1])
    execution=json.loads((ROOT/'data/provenance/return_execution.json').read_text())
    from scoreboard.hashes import text_sha256
    assert execution['hashes']['results/return_models.csv']==text_sha256(path)
