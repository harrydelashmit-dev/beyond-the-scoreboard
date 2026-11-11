"""Audited, exact-calendar panel for the expanded financial feasibility study.

Licensed financial observations and the joined panel remain in data/private.
Only aggregate coverage, public performance facts, and ID rules are published.
"""
from io import BytesIO
import json
from zipfile import ZipFile

import numpy as np
import pandas as pd

from .clean import calendar_join, csv_zip, positive_log, unique
from .download import ROOT
from .knight_reports import METRICS
from .performance import basketball_events

MERGER_PROGRAMS={486840:'Kennesaw consolidation; old UNITID 140164',
                 227368:'UT Pan American/UTRGV consolidation, 2015',
                 151102:'IPFW split/Purdue Fort Wayne institutional scope change, 2018'}
DI_SUBDIVISIONS={'Football Bowl Subdivision','Football Championship Subdivision',
                 'Basketball Subdivision (No Football)'}
POWER_FIVE={'Atlantic Coast Conference','Big 12 Conference','Big Ten Conference',
             'Pacific-12 Conference','Southeastern Conference'}


def program_ids(series):
    """Stable athletics-program key; do not overwrite original source UNITIDs."""
    return series.replace({140164:486840}).astype(int)


def institutional_lookup():
    d=pd.read_csv(ROOT/'data/processed/ipeds.csv')
    d=d.rename(columns={'unitid':'ipeds_source_unitid'})
    d['unitid']=program_ids(d.ipeds_source_unitid)
    # In fall 2015 IPEDS includes a closed former KSU row without enrollment
    # and the consolidated active entity. Keep the source candidates for audit.
    duplicate=d[d.duplicated(['unitid','year'],False)].copy()
    duplicate.to_csv(ROOT/'data/private/ipeds_program_duplicate_candidates.csv',index=False)
    if not duplicate.empty:
        if not duplicate.unitid.eq(486840).all():
            raise ValueError('New institution-lineage ambiguity requires review')
        d=d.sort_values(['total_enrollment','ipeds_source_unitid'],na_position='first')
        d=d.drop_duplicates(['unitid','year'],keep='last')
    unique(d,['unitid','year'])
    return d


def conference_lookup():
    frames=[];rules=[]
    for fall in range(2009,2019):
        d,member=csv_zip(ROOT/f'data/raw/ipeds/ic{fall}.zip')
        with ZipFile(ROOT/f'data/raw/ipeds/ic{fall}_dict.zip') as z:
            book=pd.ExcelFile(BytesIO(z.read(z.namelist()[0])))
            variables=pd.read_excel(book,sheet_name='varlist')
            title=variables.loc[variables.varname.eq('CONFNO2'),'varTitle'].iloc[0]
            if 'basketball' not in str(title).lower():
                raise ValueError('IPEDS conference field meaning changed')
            freq=pd.read_excel(book,sheet_name='FrequenciesRV')
            codes=freq[freq.varname.eq('CONFNO2')][['codevalue','valuelabel']].drop_duplicates()
        c=d[['unitid','sport2','confno2']].copy()
        c['conference_source_unitid']=c.unitid
        c.unitid=program_ids(c.unitid)
        c['basketball_conference_code']=c.confno2.where(c.sport2.eq(1)&c.confno2.gt(0))
        # The fall IC conference belongs to the season ending the following year.
        c['year']=fall+1
        c['conference_collection_fall']=fall
        c=c.sort_values('basketball_conference_code',na_position='first').drop_duplicates(['unitid','year'],keep='last')
        unique(c,['unitid','year'])
        frames.append(c[['unitid','year','conference_source_unitid','basketball_conference_code','conference_collection_fall']])
        rules.append(dict(collection_fall=fall,athletic_ending_year=fall+1,
            selected_member=member,variable='CONFNO2',title=str(title),codes=codes.to_dict('records')))
    (ROOT/'data/provenance/conference_period_rules.json').write_text(json.dumps(rules,indent=2),encoding='utf-8')
    return pd.concat(frames,ignore_index=True)


def reported_flag_rules():
    """Verify 'R=Reported' using each original admission/enrollment dictionary."""
    checked=[]
    for year in range(2010,2020):
        for component in ([f'ic{year}' if year<2014 else f'adm{year}',f'ef{year}a']):
            path=ROOT/f'data/raw/ipeds/{component}_dict.zip'
            with ZipFile(path) as z:
                book=pd.ExcelFile(BytesIO(z.read(z.namelist()[0])))
                sheet=next(s for s in book.sheet_names if s.lower()=='imputation values')
                values=pd.read_excel(book,sheet_name=sheet,header=None)
                rows=values[values.apply(lambda row:row.astype(str).str.fullmatch('Reported',case=False).any(),axis=1)]
                if len(rows)!=1 or 'R' not in rows.iloc[0].astype(str).tolist():
                    raise ValueError(f'Reported flag code needs review: {component}')
            checked.append(dict(component=component,reported_code='R',source=path.name,sheet=sheet))
    (ROOT/'data/provenance/reported_flag_rules.json').write_text(json.dumps(checked,indent=2),encoding='utf-8')


def add_history_features(fpi):
    d=fpi.copy().sort_values(['unitid','season'])
    unique(d,['unitid','year'])
    d=calendar_join(d,['fpi'],-1,'previous_')
    baseline=d[d.season.between(2005,2008)].groupby('unitid').fpi.agg(['mean','count'])
    baseline=baseline[baseline['count'].eq(4)]
    threshold=float(baseline['mean'].median())
    d['historical_fpi']=d.unitid.map(baseline['mean'])
    d['low_prominence']=d.historical_fpi.lt(threshold).where(d.historical_fpi.notna()).astype(float)
    d['fpi_outperformance']=np.nan
    forecasts=[]
    for season in range(2009,2020):
        # Expanding training window contains past seasons only. This models
        # statistical outperformance, not market/preseason expectations.
        train=d[(d.season<season)&d.previous_fpi.notna()].copy()
        current=d[d.season.eq(season)&d.previous_fpi.notna()]
        x=np.column_stack([np.ones(len(train)),train.previous_fpi])
        beta=np.linalg.lstsq(x,train.fpi,rcond=None)[0]
        predictions=beta[0]+beta[1]*current.previous_fpi
        d.loc[current.index,'fpi_outperformance']=current.fpi-predictions
        forecasts.append(dict(forecast_season=season,last_training_season=int(train.season.max()),
            training_n=len(train),intercept=float(beta[0]),lag_coefficient=float(beta[1])))
    (ROOT/'data/provenance/football_outperformance_rules.json').write_text(json.dumps(
        dict(baseline_seasons=[2005,2006,2007,2008],low_prominence_cutoff=threshold,
             forecasts=forecasts,interpretation='Expanding AR(1) residual; not a measured surprise to prospective students'),indent=2),encoding='utf-8')
    return d


def descriptive_audit(d):
    base=d[d.primary_eligible].copy()
    variables=['kn_expenses','total_revenue','ticket_sales','donor_contributions',
        'net_nonallocated_revenue_proxy','allocated_support_share','football_spending',
        'football_coaching_salaries','mbb_expenses','cup_points','fpi','sweet16',
        'applications','first_time_enrollment','total_enrollment','sport_categories']
    base[variables].describe(percentiles=[.25,.5,.75]).T.to_csv(
        ROOT/'results/feasibility_descriptive_statistics.csv')
    base.groupby('year').agg(schools=('unitid','nunique'),
        expense_reports=('kn_expenses','count'),median_expenses=('kn_expenses','median'),
        median_tickets=('ticket_sales','median'),median_donations=('donor_contributions','median'),
        median_support_share=('allocated_support_share','median')).to_csv(
            ROOT/'results/feasibility_annual_financial_summary.csv')
    comparable=base[base.kn_expenses.gt(0)&base.expenses.gt(0)].copy()
    comparable['knight_eada_ratio']=comparable.kn_expenses/comparable.expenses
    comparable['absolute_relative_difference']=(comparable.knight_eada_ratio-1).abs()
    comparable.groupby('year').agg(matched_rows=('unitid','size'),
        median_knight_eada_ratio=('knight_eada_ratio','median'),
        median_absolute_relative_difference=('absolute_relative_difference','median')).to_csv(
            ROOT/'results/source_reconciliation_summary.csv')
    comparable[['unitid','year','kn_expenses','expenses','knight_eada_ratio']].to_csv(
        ROOT/'data/private/source_financial_reconciliation.csv',index=False)
    # These are review flags only: genuine athletic exposure can itself produce
    # a large applications change. Flagging never imputes or removes a result.
    previous=calendar_join(base,['applications','first_time_enrollment','kn_expenses'],-1,'audit_previous_')
    flags=[]
    for variable,ratio in [('applications',2.),('first_time_enrollment',1.25),('kn_expenses',1.5)]:
        old=previous['audit_previous_'+variable]
        change=previous[variable]/old.where(old>0)
        selected=previous[change.gt(ratio)|change.lt(1/ratio)].copy()
        for row in selected.itertuples():
            flags.append(dict(unitid=row.unitid,year=row.year,variable=variable,
                value=getattr(row,variable),previous_value=getattr(row,'audit_previous_'+variable),
                interpretation='Large source change for review; not automatically an error or an exclusion'))
    flagged=pd.DataFrame(flags,columns=['unitid','year','variable','value','previous_value','interpretation'])
    flagged.to_csv(ROOT/'data/private/large_source_change_flags.csv',index=False)
    flagged.groupby(['year','variable']).size().rename('flagged_school_years').to_csv(
        ROOT/'results/source_change_flag_counts.csv')


def main():
    private=ROOT/'data/private';private.mkdir(exist_ok=True)
    k=pd.read_csv(private/'knight_source_panel.csv')
    k=k.rename(columns={'unitid':'knight_source_unitid','total_expenses':'kn_expenses'})
    k['unitid']=program_ids(k.knight_source_unitid)
    unique(k,['unitid','year'])
    k['di_eligible']=k.ncaa_subdivision.isin(DI_SUBDIVISIONS)
    k['merger_program']=k.unitid.isin(MERGER_PROGRAMS)
    # Explicitly named net-of-allocation proxy. Exported revenue already nets
    # transfers; this is not gross externally generated receipts or cash profit.
    k['net_nonallocated_revenue_proxy']=k.total_revenue-k.institution_government_support-k.student_fees
    k['accounting_gap_proxy']=k.kn_expenses-k.net_nonallocated_revenue_proxy
    k['allocated_support_share']=(k.institution_government_support+k.student_fees)/k.total_revenue.where(k.total_revenue>0)
    ipeds=institutional_lookup()
    eada=pd.read_csv(ROOT/'data/processed/eada.csv').rename(columns={'unitid':'eada_source_unitid'})
    eada['unitid']=program_ids(eada.eada_source_unitid)
    unique(eada,['unitid','year'])
    d=k.merge(ipeds,on=['unitid','year'],how='left',validate='one_to_one',indicator='ipeds_match')
    d=d.merge(eada[['unitid','year','eada_source_unitid','eada_name','division_code',
        'expenses','reported_revenue','mbb_expenses','football_expenses','sport_categories']],
        on=['unitid','year'],how='left',validate='one_to_one',indicator='eada_match')
    cup=pd.read_csv(ROOT/'data/processed/directors_cup.csv')
    cup['cup_percentile_success']=cup.groupby('year').cup_points.rank(pct=True)*100
    cross=pd.read_csv(ROOT/'data/processed/school_crosswalk.csv')
    cup=cup.merge(cross,on=['cup_name','year'],how='left',validate='one_to_one')
    expanded_aliases=json.loads((ROOT/'config/expanded_cup_ids.json').read_text(encoding='utf-8'))
    for name,uid in expanded_aliases.items():
        if uid not in set(ipeds.unitid):raise ValueError('Expanded Cup alias absent from IPEDS')
        mask=cup.cup_name.eq(name)&cup.unitid.isna()
        cup.loc[mask,'unitid']=uid
        cup.loc[mask,'match_method']='reviewed_ipeds_alias'
    cup[['cup_name','year','unitid','match_method']].to_csv(ROOT/'data/processed/expanded_cup_crosswalk.csv',index=False)
    cup=cup.dropna(subset=['unitid'])
    cup.unitid=program_ids(cup.unitid)
    unique(cup,['unitid','year'])
    d=d.merge(cup[['unitid','year','cup_name','cup_points','cup_rank','cup_percentile_success']],
        on=['unitid','year'],how='left',validate='one_to_one',indicator='cup_match')
    fpi=pd.read_csv(ROOT/'data/processed/football_fpi.csv').dropna(subset=['unitid'])
    fpi.unitid=program_ids(fpi.unitid)
    fpi=add_history_features(fpi)
    visibility=pd.read_csv(ROOT/'data/processed/football_visibility.csv')
    visibility.unitid=program_ids(visibility.unitid)
    fpi=fpi.merge(visibility[['unitid','year','ap_final_rank','ap_preseason_rank',
        'ap_top20','preseason_unranked_breakthrough']],on=['unitid','year'],how='left',validate='one_to_one')
    d=d.merge(fpi[['unitid','year','season','espn_id','fpi','fpi_rank','football_win_pct',
        'historical_fpi','low_prominence','fpi_outperformance','ap_final_rank','ap_preseason_rank',
        'ap_top20','preseason_unranked_breakthrough']],on=['unitid','year'],how='left',validate='one_to_one')
    events=basketball_events()
    events.unitid=program_ids(events.unitid)
    d=d.merge(events[['unitid','year','sweet16','main64']],on=['unitid','year'],how='left',validate='one_to_one')
    # These are exhaustive event-membership indicators, not imputed Cup scores.
    # The reader asserts exactly sixteen Sweet16 and sixty-four main-bracket
    # schools, all successfully mapped, in each year before this closed set join.
    for event in ['sweet16','main64']:
        d.loc[d.di_eligible,event]=d.loc[d.di_eligible,event].fillna(0)
        d.loc[~d.di_eligible,event]=np.nan
    conf=conference_lookup()
    d=d.merge(conf,on=['unitid','year'],how='left',validate='one_to_one')
    d['conference_year']=d.basketball_conference_code.astype('Int64').astype('string')+':'+d.year.astype('string')
    d.loc[d.basketball_conference_code.isna(),'conference_year']=pd.NA
    d['power_five']=d.fbs_conference.isin(POWER_FIVE).astype(float).where(d.fpi.notna())
    d['other_fbs']=(1-d.power_five).where(d.fpi.notna()&~d.fbs_conference.eq('Independent'))
    d['public']=d.control.eq(1)
    d['primary_eligible']=d.public&d.di_eligible&~d.merger_program
    d['cup_100']=d.cup_points/100
    d['cup_rank_better_50']=-d.cup_rank/50
    d['fpi_10']=d.fpi/10
    d['win_pct_10pp']=d.football_win_pct/.1
    d['outperformance_10']=d.fpi_outperformance/10
    d['outperformance_low_prominence']=d.outperformance_10*d.low_prominence
    logs=['kn_expenses','football_spending','football_coaching_salaries','mbb_expenses',
        'ticket_sales','donor_contributions','net_nonallocated_revenue_proxy']
    for column in logs:d['log_'+column]=positive_log(d[column])
    for column in ['ticket_sales','donor_contributions','net_nonallocated_revenue_proxy']:
        d['ihs_'+column]=np.arcsinh(d[column]/1_000_000)
    d=calendar_join(d,['log_kn_expenses','log_football_spending','log_football_coaching_salaries',
        'log_mbb_expenses','log_total_enrollment','sport_categories','fpi_10','cup_100'],-1,'lag_')
    # Revenue lags use the full Knight panel, independently of future EADA/Cup.
    revenue_cols=['log_'+c for c in ['ticket_sales','donor_contributions','net_nonallocated_revenue_proxy']]
    revenue_cols+=['ihs_'+c for c in ['ticket_sales','donor_contributions','net_nonallocated_revenue_proxy']]
    d=calendar_join(d,revenue_cols,1,'next_')
    d=calendar_join(d,revenue_cols,2,'next2_')
    outcomes=['log_applications','log_first_time_enrollment','xapplcn','first_time_enrollment_flag']
    for offset,prefix in [(1,'next_'),(2,'next2_'),(-1,'previous_')]:
        d=calendar_join(d,outcomes,offset,prefix,lookup=ipeds)
    d['fpi10_other_fbs']=d.fpi_10*d.other_fbs
    unique(d,['unitid','year'])
    d.to_csv(private/'feasibility_panel.csv',index=False)
    audit=['knight_source_unitid','unitid','year','school_name','ipeds_source_unitid','instnm',
        'eada_source_unitid','eada_name','di_eligible','merger_program','ipeds_match','eada_match','cup_match',
        'conference_collection_fall','basketball_conference_code','primary_eligible']
    d[audit].to_csv(private/'feasibility_join_audit.csv',index=False)
    coverage=d.groupby('year').agg(listed=('unitid','size'),di_eligible=('di_eligible','sum'),
        primary_eligible=('primary_eligible','sum'),ipeds_matched=('total_enrollment','count'),
        financial_expenses=('kn_expenses','count'),cup_observed=('cup_points','count'),
        fpi_observed=('fpi','count'),basketball_event_observed=('sweet16','count'),
        conference_observed=('basketball_conference_code','count'))
    coverage.to_csv(ROOT/'results/feasibility_coverage.csv')
    rules=dict(stable_key='unitid is the athletics-program key in this private joined panel; original source IDs retained',
        old_to_program={'140164':486840},primary_merger_exclusions=MERGER_PROGRAMS,
        ipeds_fall_2015_ksu='Keep active consolidated 486840 row with reported enrollment; retain closed former 140164 candidate in private audit',
        conference_year='Fall IC collection t-1 maps to athletic year ending t; verified using Nebraska Big12/BigTen transition',
        financial_year='Knight year is academic/fiscal ending year, as source YEAR definition states',
        football_year='ESPN season s maps to athletic ending year s+1; January/February postseason run date checked',
        basketball_event_zeros='Derived only from exhaustive matched 16/64-school annual positive ledgers; Cup scores stay missing')
    rules['expanded_cup_aliases']=expanded_aliases
    (ROOT/'data/provenance/institution_period_rules.json').write_text(json.dumps(rules,indent=2),encoding='utf-8')
    reported_flag_rules()
    descriptive_audit(d)
    print(coverage.to_string())
    print('Private audited panel:',len(d),'rows; primary eligible',d.primary_eligible.sum())
    return d


if __name__=='__main__':main()
