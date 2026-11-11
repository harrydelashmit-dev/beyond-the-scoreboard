"""Independent numerical and source-calendar checks on the executed study."""
from datetime import datetime, timezone
import hashlib
import json

import numpy as np
import pandas as pd
from scipy import linalg
import statsmodels.api as sm

from .download import ROOT
from .feasibility_data import institutional_lookup
from .hashes import text_sha256


def main():
    panel=ROOT/'data/private/feasibility_panel.csv'
    if not panel.exists():raise SystemExit('Local registered data are required for this validation.')
    d=pd.read_csv(panel)
    k=pd.read_csv(ROOT/'data/private/knight_source_panel.csv')
    m=pd.read_csv(ROOT/'results/feasibility_models.csv')
    primary=m[m.primary&m.exposure_term]
    source_count=0
    for name in ['download_manifest.json','feasibility_download_manifest.json']:
        for source in json.loads((ROOT/'data/provenance'/name).read_text(encoding='utf-8')):
            if source['status']!='ok':continue
            path=ROOT/'data/raw'/source['file']
            assert hashlib.sha256(path.read_bytes()).hexdigest()==source['sha256']
            source_count+=1
    assert len(primary)==18 and primary.model.nunique()==18
    assert not d.duplicated(['unitid','year']).any()
    assert d.ipeds_match.eq('both').all()
    assert (d.year-d.conference_collection_fall).eq(1).all()
    assert d.loc[d.fpi.notna(),'year'].eq(d.loc[d.fpi.notna(),'season']+1).all()
    assert d.loc[d.year.eq(2019),'next_log_applications'].isna().all()
    assert d.loc[d.year.eq(2019),'next_log_first_time_enrollment'].isna().all()
    # Every original financial value, including missing cells, survives the join.
    financial=['total_revenue','donor_contributions','ticket_sales','institution_government_support',
               'student_fees','football_spending','football_coaching_salaries']
    actual=d.rename(columns={'knight_source_unitid':'source_id','kn_expenses':'total_expenses'})
    expected=k.rename(columns={'unitid':'source_id'})
    columns=['source_id','year','total_expenses',*financial]
    pd.testing.assert_frame_equal(actual[columns].sort_values(columns[:2]).reset_index(drop=True),
        expected[columns].sort_values(columns[:2]).reset_index(drop=True),check_dtype=False)
    lookup=institutional_lookup()[['unitid','year','log_applications','log_first_time_enrollment']]
    right=lookup.rename(columns={'year':'outcome_year','log_applications':'check_apps',
                                 'log_first_time_enrollment':'check_enrollment'})
    temporal=d[['unitid','year','next_log_applications','next_log_first_time_enrollment']].copy()
    temporal['outcome_year']=temporal.year+1
    temporal=temporal.merge(right,on=['unitid','outcome_year'],how='left',validate='one_to_one')
    np.testing.assert_allclose(temporal.next_log_applications,temporal.check_apps,equal_nan=True)
    np.testing.assert_allclose(temporal.next_log_first_time_enrollment,temporal.check_enrollment,equal_nan=True)
    for row in primary.itertuples():
        cases=pd.read_csv(ROOT/f'data/private/feasibility_samples/{row.model}.csv')
        assert len(cases)==row.n and cases.unitid.nunique()==row.schools
        assert not cases.duplicated(['unitid','year']).any()
    common_names=sorted(m.loc[m.model.str.startswith('C_sweet16_common_fd_'),'model'].unique())
    assert len(common_names)==5
    reference=None
    for name in common_names:
        cases=pd.read_csv(ROOT/f'data/private/feasibility_samples/{name}.csv')[['unitid','year']].sort_values(['unitid','year']).reset_index(drop=True)
        if reference is None:reference=cases
        else:pd.testing.assert_frame_equal(reference,cases)
    independent=[]
    for name in ['A_spend_cup','B_fpi_ticket_sales','C_sweet16_applications']:
        saved=primary[primary.model.eq(name)].iloc[0]
        data=pd.read_csv(ROOT/f'data/private/feasibility_samples/{name}.csv')
        controls=saved.controls.split(';') if isinstance(saved.controls,str) else []
        terms=[saved.term,*controls]
        fixed=pd.concat([pd.get_dummies(data.unitid,dtype=float),
                         pd.get_dummies(data.conference_year,dtype=float)],axis=1).to_numpy()
        _,tri,piv=linalg.qr(fixed,mode='economic',pivoting=True)
        diagonal=np.abs(np.diag(tri))
        rank=int((diagonal>diagonal.max()*1e-10).sum())
        design=np.column_stack([data[terms].to_numpy(),fixed[:,piv[:rank]]])
        fitted=sm.OLS(data[saved.outcome],design).fit(cov_type='cluster',
            cov_kwds={'groups':data.unitid},use_t=True)
        b=float(fitted.params.iloc[0]);se=float(fitted.bse.iloc[0]);p=float(fitted.pvalues.iloc[0])
        np.testing.assert_allclose(b,saved.coefficient,rtol=1e-7,atol=1e-9)
        np.testing.assert_allclose(se,saved.std_error,rtol=1e-6,atol=1e-10)
        np.testing.assert_allclose(p,saved.p_value,rtol=1e-5,atol=1e-10)
        independent.append(dict(model=name,n=int(saved.n),schools=int(saved.schools),
            sparse_coefficient=saved.coefficient,independent_coefficient=b,
            sparse_se=saved.std_error,independent_se=se,sparse_p=saved.p_value,independent_p=p,
            status='passed_full_rank_dummy_ols'))
    pd.DataFrame(independent).to_csv(ROOT/'results/independent_fe_validation.csv',index=False)
    report=dict(validated_utc=datetime.now(timezone.utc).isoformat(),
        panel_sha256=hashlib.sha256(panel.read_bytes()).hexdigest(),
        results_sha256=text_sha256(ROOT/'results/feasibility_models.csv'),
        all_18_primary_sample_counts_checked=True,all_2400_financial_rows_preserved=True,
        all_2400_ipeds_identity_matches=True,exact_future_fall_joins_checked=True,
        source_manifest_entries_hash_verified=source_count,
        five_basketball_common_samples_identical=True,
        football_season_plus_one_checked=True,conference_fall_plus_one_checked=True,
        independent_primary_models=independent,
        limits='Checks establish source consistency and numerical implementation; they do not establish correct institutional reporting or causal identification.')
    (ROOT/'data/provenance/feasibility_validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(pd.DataFrame(independent).to_string(index=False))
    print('Financial cells, identities, calendar joins, and all primary model sample counts verified.')


if __name__=='__main__':main()
