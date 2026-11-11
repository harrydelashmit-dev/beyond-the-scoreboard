"""Independent checks of inference, season alignment, and event completeness."""
from copy import deepcopy

import numpy as np
import pandas as pd
import pytest
from scipy import linalg, stats
import statsmodels.api as sm

from scoreboard.models import fixed_effects
from scoreboard.performance import parse_fpi,parse_ap_poll
from scoreboard.feasibility_data import program_ids
from scoreboard.feasibility import primary_specs
from scoreboard.cfo_scenarios import cohort_stock,npv_from_cohorts


def test_conference_year_effects_and_contrasts_match_full_rank_dummy_ols():
    rng=np.random.default_rng(547)
    d=pd.DataFrame([(s,y) for s in range(32) for y in range(2010,2016)
        if not (s%7==0 and y==2012)],columns=['unitid','year'])
    conference=d.unitid//8
    conference=conference.where(~(d.unitid.eq(1)&d.year.ge(2013)),1)
    d['conference_year']=conference.astype(str)+':'+d.year.astype(str)
    d['x']=rng.normal(size=len(d));d['z']=rng.normal(size=len(d))
    d['y']=.4*d.x-.3*d.z+.8*d.unitid+conference*.1*(d.year-2010)+rng.normal(scale=.3,size=len(d))
    rows,_=fixed_effects(d,'y',['x'],['z'],time_effect='conference_year',
        contrasts={'sum_effect':{'x':1,'z':1}})
    # Independent full-rank fixed-effect basis avoids redundant dummies when
    # conference-school components are disconnected. The correction uses rank.
    fixed=pd.concat([pd.get_dummies(d.unitid,dtype=float),
                     pd.get_dummies(d.conference_year,dtype=float)],axis=1).to_numpy()
    _,tri,piv=linalg.qr(fixed,pivoting=True,mode='economic')
    rank=np.linalg.matrix_rank(tri)
    design=np.column_stack([d[['x','z']],fixed[:,piv[:rank]]])
    expected=sm.OLS(d.y,design).fit(cov_type='cluster',cov_kwds={'groups':d.unitid},use_t=True)
    for row,index in [(rows[0],0),(rows[1],1)]:
        assert row['coefficient']==pytest.approx(expected.params.iloc[index],abs=1e-8)
        assert row['std_error']==pytest.approx(expected.bse.iloc[index],rel=1e-7)
        assert row['p_value']==pytest.approx(expected.pvalues.iloc[index],rel=1e-6)
    weights=np.array([1,1]+[0]*(design.shape[1]-2))
    se=float(np.sqrt(weights@expected.cov_params().to_numpy()@weights))
    assert rows[2]['coefficient']==pytest.approx(float(weights@expected.params),abs=1e-8)
    assert rows[2]['std_error']==pytest.approx(se,rel=1e-7)
    assert rows[0]['df_resid']==pytest.approx(expected.df_resid)


def fpi_payload():
    return {'count':1,'pageCount':1,'items':[{'season':2014,'runDateTimeKey':20150113040000,
        'team':{'$ref':'https://sports.core.api.espn.com/teams/194'},
        'predictives':[{'name':'fpi','value':25},{'name':'fpirank','value':3},
                       {'name':'numwins','value':14},{'name':'numlosses','value':1}]}]}


def test_fpi_year_is_season_plus_one_and_requires_final_snapshot():
    actual=parse_fpi(fpi_payload(),2014)
    assert actual.year.tolist()==[2015]
    assert actual.football_win_pct.iloc[0]==pytest.approx(14/15)
    wrong=fpi_payload();wrong['items'][0]['season']=2026
    with pytest.raises(ValueError,match='wrong season'):parse_fpi(wrong,2014)
    wrong=fpi_payload();wrong['items'][0]['runDateTimeKey']=20140901040000
    with pytest.raises(ValueError,match='postseason'):parse_fpi(wrong,2014)


def ap_payload(preseason=False):
    return dict(type='ap',season={'year':2014,'type':{'type':2 if preseason else 3}},
        occurrence={'last':not preseason,'number':1},
        ranks=[dict(current=i,team={'id':str(i)},record={'stats':[
            dict(name='wins',value=0),dict(name='losses',value=0)]}) for i in range(1,26)])


def test_ap_poll_does_not_silently_accept_current_season_or_played_games():
    assert len(parse_ap_poll(ap_payload(),2014))==25
    wrong=ap_payload();wrong['season']['year']=2026
    with pytest.raises(ValueError,match='Wrong AP'):parse_ap_poll(wrong,2014)
    missing=ap_payload();missing['ranks'].pop()
    with pytest.raises(ValueError,match='incomplete'):parse_ap_poll(missing,2014)
    assert len(parse_ap_poll(ap_payload(True),2014,True))==25
    played=ap_payload(True);played['ranks'][0]['record']['stats'][0]['value']=1
    with pytest.raises(ValueError,match='games played'):parse_ap_poll(played,2014,True)


def test_stable_program_key_and_primary_plan():
    assert program_ids(pd.Series([140164,486840,227368,151102])).tolist()==[486840,486840,227368,151102]
    specs=primary_specs()
    assert len(specs)==18
    assert pd.Series(s['family'] for s in specs).value_counts().to_dict()=={
        'success_finance':9,'flutie':6,'spending_success':3}
    football=next(s for s in specs if s['model']=='C_fpi_applications')
    cup=next(s for s in specs if s['model']=='C_cup_applications')
    assert football['y']=='log_applications'
    assert cup['y']=='next_log_applications'


def test_student_stock_is_not_new_intake_and_capacity_is_respected():
    assert cohort_stock(100,.9,4,4,10000)==pytest.approx(343.9)
    assert cohort_stock(100,1,4,8,10000)==400
    assert cohort_stock(200,.8,4,10,500)<=500
    assert cohort_stock(200,1,4,10,500)==500
    with pytest.raises(ValueError):cohort_stock(100,1.2,4,1,500)


def test_npv_counts_capital_once_and_never_converts_applications_to_students():
    value,flows=npv_from_cohorts(new_students=0,generated_receipts=0,
        annual_athletics_cost=5_000_000,capital_outlay=1_000_000,discount_rate=0,horizon=3)
    assert value==-16_000_000
    assert all(f['extra_enrolled_stock']==0 for f in flows)


def test_saved_primary_adjustment_and_intervals_are_consistent():
    from scoreboard.download import ROOT
    from statsmodels.stats.multitest import multipletests
    path=ROOT/'results/feasibility_models.csv'
    if not path.exists():pytest.skip('Expanded results not generated yet')
    d=pd.read_csv(path)
    primary=d[d.primary&d.exposure_term]
    assert len(primary)==18
    for _,group in primary.groupby('family'):
        np.testing.assert_allclose(group.holm_family_p,multipletests(group.p_value,method='holm')[1])
    np.testing.assert_allclose(primary.holm_all_primary_p,multipletests(primary.p_value,method='holm')[1])
    critical=stats.t.ppf(.975,primary.schools-1)
    np.testing.assert_allclose(primary.ci_low,primary.coefficient-critical*primary.std_error)
    np.testing.assert_allclose(primary.ci_high,primary.coefficient+critical*primary.std_error)


def test_report_validation_hash_survives_git_line_ending_conversion(tmp_path):
    from scoreboard.hashes import text_sha256
    windows=tmp_path/'windows.csv';linux=tmp_path/'linux.csv'
    windows.write_bytes(b'model,coefficient\r\nexample,0.5\r\n')
    linux.write_bytes(b'model,coefficient\nexample,0.5\n')
    assert text_sha256(windows)==text_sha256(linux)
