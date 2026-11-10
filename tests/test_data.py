import json
from pathlib import Path
import pandas as pd
import pytest
from scoreboard.download import ROOT
from scoreboard.clean import unique

@pytest.fixture
def panel():
    return pd.read_csv(ROOT/'data/processed/panel.csv')

def test_real_data_unique_and_coverage(panel):
    unique(panel,['unitid','year'])
    assert set(panel.year)==set(range(2010,2020))
    assert panel.unitid.nunique()>300
    assert panel.loc[panel.cup_join=='left_only','cup_points'].isna().all()
    assert panel.loc[panel.year==2019,'next_applications'].isna().all()
    assert panel.loc[panel.year==2010,'lag_log_expenses'].isna().all()
    assert panel.loc[panel.cup_observed,'cup_points'].between(0,2000).all()

def test_official_cup_known_answers():
    cup=pd.read_csv(ROOT/'data/processed/directors_cup.csv')
    # Published NACDA final totals, manually checked against original first pages.
    known=[(2010,'Stanford',1,1508.50),(2019,'Stanford',1,1503.75),(2019,'Michigan',2,1272.25),(2019,'Florida',3,1156.75)]
    for year,name,rank,points in known:
        row=cup[(cup.year==year)&(cup.cup_name==name)].iloc[0]
        assert row.cup_rank==rank
        assert row.cup_points==pytest.approx(points)
    assert cup.groupby('year').size().min()>250

def test_sources_have_verified_hashes():
    manifest=json.loads((ROOT/'data/provenance/download_manifest.json').read_text())
    configured={s['file'] for s in json.loads((ROOT/'config/sources.json').read_text())}
    successful={s['file'] for s in manifest if s['status']=='ok' and len(s['sha256'])==64}
    assert configured<=successful

def test_institution_join_does_not_combine_campuses(panel):
    # Alabama and UAB have different permanent UNITIDs.
    a=panel[(panel.unitid==100751)&(panel.year==2019)].iloc[0]
    b=panel[(panel.unitid==100663)&(panel.year==2019)].iloc[0]
    assert a.expenses==166812799
    assert a.expenses!=b.expenses

def test_high_profile_success_known_answers(panel):
    for year,uid,field in [(2010,100751,'fbs_points'),(2019,217882,'fbs_points'),(2010,198419,'mbb_points'),(2019,234076,'mbb_points')]:
        row=panel[(panel.year==year)&(panel.unitid==uid)].iloc[0]
        assert row[field]==pytest.approx(100)
    names=pd.read_csv(ROOT/'data/processed/school_crosswalk.csv').cup_name
    assert not names.str.contains(r'\d+\.\d+').any(), 'Financial/point columns leaked into school labels'

def test_calendar_school_aliases(panel):
    for year,uid in [(2015,140164),(2016,486840)]:
        row=panel[(panel.year==year)&(panel.unitid==uid)].iloc[0]
        assert 'Kennesaw' in row.eada_name
    for uid in [204024,135726,164924,164988]:
        assert panel.loc[panel.unitid==uid,'cup_points'].notna().sum()>5
