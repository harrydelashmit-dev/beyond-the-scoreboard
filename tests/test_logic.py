"""Small artificial fixtures test logic; never used as empirical observations."""
import numpy as np
import pandas as pd
import pytest
import statsmodels.formula.api as smf
from scoreboard.clean import calendar_join, positive_log, unique,align_admissions_period
from scoreboard.knight import normalize_finances, FIELDS
from scoreboard.models import fixed_effects
from scoreboard.scenarios import annual_contribution

def test_calendar_lags_do_not_bridge_gaps_or_schools():
    d=pd.DataFrame({'unitid':[1,1,2,2],'year':[2010,2012,2010,2011],'value':[10,12,20,21]})
    joined=calendar_join(d,['value'],1,'next_')
    assert np.isnan(joined.loc[0,'next_value'])
    assert joined.loc[2,'next_value']==21
    assert joined.loc[0,'value']==10

def test_independent_admissions_lookup_survives_finance_sample_exit():
    finance=pd.DataFrame({'unitid':[1],'year':[2018]})
    admissions=pd.DataFrame({'unitid':[1],'year':[2019],'applications':[500]})
    joined=calendar_join(finance,['applications'],1,'next_',lookup=admissions)
    assert joined.next_applications.iloc[0]==500

def test_pre_2014_admissions_follow_reported_fall_not_collection_label():
    d=pd.DataFrame({'unitid':[1,2,3],'appdate':[1,2,-1],'applcn':[100,200,300]})
    aligned=align_admissions_period(d,2010)
    assert aligned.year.tolist()==[2009,2010]
    assert aligned.applcn.tolist()==[100,200]

def test_duplicate_school_year_rejected():
    with pytest.raises(ValueError):unique(pd.DataFrame({'unitid':[1,1],'year':[2010,2010]}),['unitid','year'])

def test_log_does_not_fabricate_positive_spending():
    actual=positive_log(pd.Series([0,-1,np.nan,np.e]))
    assert actual.iloc[:3].isna().all()
    assert actual.iloc[3]==pytest.approx(1)

def test_fixed_effects_agree_with_independent_dummy_ols():
    rng=np.random.default_rng(47)
    d=pd.DataFrame([(s,y) for s in range(25) for y in range(2010,2015) if not(s%4==0 and y==2012)],columns=['unitid','year'])
    d['x']=rng.normal(size=len(d));d['z']=rng.normal(size=len(d))
    d['y']=.7*d.x-.2*d.z+d.unitid*.4+(d.year-2010)*2+rng.normal(scale=.1,size=len(d))
    actual,_=fixed_effects(d,'y',['x'],['z'])
    expected=smf.ols('y ~ x + z + C(unitid) + C(year)',d).fit(cov_type='cluster',cov_kwds={'groups':d.unitid},use_t=True)
    for row in actual:
        term=row['term']
        assert row['coefficient']==pytest.approx(expected.params[term],abs=1e-8)
        assert row['std_error']==pytest.approx(expected.bse[term],rel=1e-7)
        assert row['p_value']==pytest.approx(expected.pvalues[term],rel=1e-6)

def test_generated_revenue_excludes_subsidies_once():
    frame=pd.DataFrame([[1,2015,100,20,5,90]],columns=FIELDS)
    mapping=dict(columns={x:x for x in FIELDS},dollars='nominal',year_convention='fiscal_year_ending',support_and_student_fees_are_separate=True)
    d=normalize_finances(frame,mapping)
    assert d.generated_revenue.iloc[0]==75
    assert d.direct_balance.iloc[0]==-15
    mapping['support_and_student_fees_are_separate']=False
    with pytest.raises(ValueError):normalize_finances(frame,mapping)

def test_net_tuition_uses_incremental_cost():
    assert annual_contribution(100,12000,6000)==600000
