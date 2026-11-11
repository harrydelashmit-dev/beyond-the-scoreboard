"""Python readers for public ESPN ratings and exhaustive NACDA sport ledgers."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import json
import re

import numpy as np
import pandas as pd

from .clean import normalize, unique
from .download import ROOT, fetch


def download_sources():
    specs = json.loads((ROOT/'config/feasibility_sources.json').read_text(encoding='utf-8'))
    with ThreadPoolExecutor(max_workers=4) as pool:
        metadata = list(pool.map(fetch, specs))
    (ROOT/'data/provenance/feasibility_download_manifest.json').write_text(
        json.dumps(metadata, indent=2), encoding='utf-8')
    failed = [m for m in metadata if m['status'] != 'ok']
    if failed:
        raise ValueError(f'Failed source downloads: {[m["file"] for m in failed]}')
    print(f'{len(metadata)} historical performance/conference sources available')


def parse_fpi(payload, season):
    if payload.get('pageCount') != 1 or len(payload['items']) != payload['count']:
        raise ValueError('Incomplete ESPN FPI pagination')
    rows = []
    for item in payload['items']:
        if item['season'] != season:
            raise ValueError('FPI response returned the wrong season')
        run = str(item['runDateTimeKey'])
        if run[:4] != str(season+1) or run[4:6] not in ['01', '02']:
            raise ValueError('FPI is not a verified postseason snapshot')
        team_id = int(re.search(r'/teams/(\d+)', item['team']['$ref']).group(1))
        stats = {s['name']: s.get('value', np.nan) for s in item['predictives']}
        rows.append(dict(espn_id=team_id, season=season, year=season+1,
            fpi=stats.get('fpi'), fpi_rank=stats.get('fpirank'),
            football_wins=stats.get('numwins'), football_losses=stats.get('numlosses'),
            run_date=run, source_updated=item.get('lastUpdated')))
    d = pd.DataFrame(rows)
    unique(d, ['espn_id', 'season'])
    if d.fpi.isna().any():
        raise ValueError('Missing headline FPI rating')
    d['football_win_pct'] = d.football_wins/(d.football_wins+d.football_losses).where(lambda s:s>0)
    return d


def team_catalog():
    payload=json.loads((ROOT/'data/raw/espn/team_catalog.json').read_text(encoding='utf-8'))
    teams=payload['sports'][0]['leagues'][0]['teams']
    d=pd.DataFrame([dict(espn_id=int(t['team']['id']),
        espn_location=t['team'].get('location'),
        espn_display_name=t['team']['displayName'],
        espn_abbreviation=t['team'].get('abbreviation')) for t in teams])
    unique(d,['espn_id'])
    return d


def build_football():
    ratings=pd.concat([parse_fpi(json.loads((ROOT/f'data/raw/espn/fpi_{s}.json').read_text(encoding='utf-8')),s)
        for s in range(2005,2020)],ignore_index=True)
    names=team_catalog()
    schools=pd.read_csv(ROOT/'data/processed/eada.csv')[['unitid','eada_name']].drop_duplicates()
    aliases=json.loads((ROOT/'config/school_aliases.json').read_text(encoding='utf-8'))
    by_name={}
    for row in schools.itertuples():by_name.setdefault(normalize(row.eada_name),set()).add(int(row.unitid))
    for name, uid in aliases.items():
        if isinstance(uid,int):by_name.setdefault(normalize(name),set()).add(uid)
    overrides_path=ROOT/'config/espn_school_ids.json'
    overrides=json.loads(overrides_path.read_text(encoding='utf-8')) if overrides_path.exists() else {}
    mapping=[]
    for row in names[names.espn_id.isin(ratings.espn_id)].itertuples():
        candidates=by_name.get(normalize(row.espn_location),set())
        uid=overrides.get(str(row.espn_id))
        method='reviewed_alias' if uid is not None else 'exact_normalized'
        if uid is None and len(candidates)==1:uid=next(iter(candidates))
        mapping.append(dict(espn_id=row.espn_id,espn_location=row.espn_location,
            espn_display_name=row.espn_display_name,unitid=uid,
            method=method if uid is not None else 'unmatched'))
    crosswalk=pd.DataFrame(mapping)
    crosswalk.to_csv(ROOT/'data/provenance/espn_school_crosswalk.csv',index=False)
    d=ratings.merge(crosswalk,on='espn_id',how='left',validate='many_to_one')
    # Historical names are labels only; historical conference comes from IC/KN.
    d.to_csv(ROOT/'data/processed/football_fpi.csv',index=False)
    print('FPI schools needing review:',d[d.unitid.isna()][['espn_id','espn_location']].drop_duplicates().to_dict('records'))
    return d


def parse_ap_poll(payload, season, preseason=False):
    expected_type=2 if preseason else 3
    if (payload.get('type')!='ap' or payload.get('season',{}).get('year')!=season or
        payload['season'].get('type',{}).get('type')!=expected_type):
        raise ValueError('Wrong AP poll, season, or season type')
    if not preseason and payload.get('occurrence',{}).get('last') is not True:
        raise ValueError('Expected final AP poll, not an intermediate week')
    if preseason:
        if payload.get('occurrence',{}).get('number')!=1:
            raise ValueError('Expected season-opening poll')
        for rank in payload['ranks']:
            record=rank.get('record',{})
            stats={s['name']:s.get('value') for s in record.get('stats',[])}
            if stats.get('wins')!=0 or stats.get('losses')!=0:
                raise ValueError('Opening AP poll has games played; preseason classification unverified')
    rows=[]
    for rank in payload['ranks']:
        team=rank['team']
        espn_id=team.get('id')
        if espn_id is None:
            espn_id=re.search(r'/teams/(\d+)',team['$ref']).group(1)
        rows.append(dict(espn_id=int(espn_id),season=season,
                         ap_rank=int(rank['current'])))
    d=pd.DataFrame(rows)
    unique(d,['espn_id','season'])
    if not 25<=len(d)<=26 or d.ap_rank.min()!=1 or not d.ap_rank.between(1,25).all():
        raise ValueError('AP top25 ledger is incomplete or contains unexpected ranks')
    return d


def add_ap_visibility(football):
    frames=[]
    for season in range(2009,2020):
        data=football[football.season.eq(season)].copy()
        for preseason,label in [(False,'final'),(True,'preseason')]:
            payload=json.loads((ROOT/f'data/raw/espn/ap_{label}_{season}.json').read_text(encoding='utf-8'))
            poll=parse_ap_poll(payload,season,preseason)
            if not set(poll.espn_id).issubset(set(data.espn_id)):
                raise ValueError('AP-ranked team absent from the verified FBS universe')
            data=data.merge(poll.rename(columns={'ap_rank':f'ap_{label}_rank'}),
                            on=['espn_id','season'],how='left',validate='one_to_one')
        # Missing rank is unranked in a verified exhaustive top25 ledger. It is
        # never converted into a fabricated numerical rank or FPI value.
        data['ap_top20']=data.ap_final_rank.le(20).astype(int)
        data['preseason_unranked_breakthrough']=(data.ap_final_rank.le(20)&data.ap_preseason_rank.isna()).astype(int)
        frames.append(data)
    return pd.concat(frames,ignore_index=True)


def basketball_events():
    raw=pd.concat([pd.read_csv(ROOT/f'data/interim/cup_{year}_winter.csv')
        for year in range(2010,2020)],ignore_index=True)
    for year,g in raw.groupby('year'):
        if g.mbb_points.ge(64).sum()!=16 or g.mbb_points.ge(25).sum()!=64:
            raise ValueError(f'Incomplete Sweet16/main64 ledger: {year}')
    cross=pd.read_csv(ROOT/'data/processed/school_crosswalk.csv')
    positive=raw[raw.mbb_points.ge(25)].merge(cross,on=['cup_name','year'],how='left',validate='one_to_one')
    if positive.unitid.isna().any():
        raise ValueError('Unmatched NCAA main64 participant; cannot infer other programs were absent')
    positive.unitid=positive.unitid.astype(int)
    unique(positive,['unitid','year'])
    positive['sweet16']=positive.mbb_points.ge(64).astype(int)
    positive['main64']=1
    positive[['unitid','year','cup_name','mbb_points','sweet16','main64','pdf_page','pdf_file']].to_csv(
        ROOT/'data/processed/basketball_events.csv',index=False)
    return positive


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--download',action='store_true')
    args=parser.parse_args()
    if args.download:download_sources()
    football=build_football()
    if (ROOT/'data/raw/espn/ap_final_2009.json').exists():
        add_ap_visibility(football).to_csv(ROOT/'data/processed/football_visibility.csv',index=False)
    basketball_events()


if __name__=='__main__':main()
