"""Read original archives, retain source flags, and audit every institution join."""
import json
import re
import unicodedata
from collections import defaultdict
from io import BytesIO
from pathlib import Path
from zipfile import ZipFile
import numpy as np
import pandas as pd
import pdfplumber
from .download import ROOT

def unique(frame, keys):
    if frame.duplicated(keys).any():
        raise ValueError(f'Duplicate key {keys}: {frame.loc[frame.duplicated(keys,False),keys].head().to_dict("records")}')

def positive_log(series):
    return np.log(series.where(series > 0))

def csv_zip(path):
    with ZipFile(path) as z:
        names=[n for n in z.namelist() if n.lower().endswith('.csv') and not n.startswith('__')]
        revised=[n for n in names if re.search(r'_rv\d*\.csv$',n,re.I)]
        if revised: name=sorted(revised)[-1]
        elif len(names)==1: name=names[0]
        else: raise ValueError(f'Ambiguous CSV archive {path}: {names}')
        # Some NCES files append a trailing delimiter to data lines but not the
        # header. Explicit index_col=False prevents shifting UNITID into the index.
        frame=pd.read_csv(z.open(name),encoding='cp1252',low_memory=False,index_col=False)
        frame.columns=frame.columns.str.strip().str.lower()
        frame['unitid']=pd.to_numeric(frame.unitid,errors='raise').astype(int)
        return frame,name

def normalize(name):
    name=unicodedata.normalize('NFKD',str(name)).encode('ascii','ignore').decode().lower()
    name=name.replace('&',' and ')
    # Keep parenthetical campus/state qualifiers: Miami (Ohio) is not Miami (FL).
    name=re.sub(r'\b(university|college|the|of|at|in|u)\b','',name)
    return re.sub(r'[^a-z0-9]','',name)

def read_eada():
    results=[]
    for year in range(2010,2020):
        cache=ROOT/f'data/interim/eada_{year}.csv'
        if cache.exists():
            results.append(pd.read_csv(cache));continue
        with ZipFile(ROOT/f'data/raw/eada/{year}.zip') as z:
            name=next(n for n in z.namelist() if n.lower().endswith(('.xlsx','.xls')))
            wanted={'unitid','institution_name','classificationcode','classification_name','grnd_total_expense','grnd_total_revenue','exp_men_football','exp_men_bskball','il_sum_total_hdcoach'}
            d=pd.read_excel(BytesIO(z.read(name)),usecols=lambda c: str(c).lower() in wanted or bool(re.match(r'^PARTIC_(MEN|WOMEN)_',str(c),re.I)))
        d.columns=d.columns.str.lower()
        d=d[d.classificationcode.isin([1,2,3])].copy()
        participation=[c for c in d if re.match('partic_(men|women)_',c)]
        # This is a participation-category proxy; combined track reporting can differ.
        d['sport_categories']=(d[participation].apply(pd.to_numeric,errors='coerce')>0).sum(axis=1)
        d=d.drop(columns=participation).rename(columns={'institution_name':'eada_name','classificationcode':'division_code','classification_name':'division_name','grnd_total_expense':'expenses','grnd_total_revenue':'reported_revenue','exp_men_football':'football_expenses','exp_men_bskball':'mbb_expenses','il_sum_total_hdcoach':'head_coach_count'})
        d['year']=year;d['eada_member']=name
        unique(d,['unitid','year']);cache.parent.mkdir(parents=True,exist_ok=True);d.to_csv(cache,index=False)
        results.append(d);print('Cleaned EADA',year,len(d),flush=True)
    return pd.concat(results,ignore_index=True)

def align_admissions_period(frame,collection_year):
    """IC APPDATE=1 means previous fall; 2 means current fall (verified dictionaries)."""
    d=frame.copy();d['admissions_collection_year']=collection_year
    if collection_year<2014:
        d['year']=d.appdate.map({1:collection_year-1,2:collection_year})
        d=d.dropna(subset=['year']).copy();d.year=d.year.astype(int)
    else:d['year']=collection_year
    return d

def read_ipeds():
    frames=[];members=[];admissions=[];period_rules=[]
    for year in range(2010,2020):
        hd,member=csv_zip(ROOT/f'data/raw/ipeds/hd{year}.zip')
        d=hd[['unitid','instnm','control','stabbr']].copy()
        comp=f'ic{year}' if year<2014 else f'adm{year}'
        a,member=csv_zip(ROOT/f'data/raw/ipeds/{comp}.zip');members.append(dict(component=comp,selected_member=member))
        if year<2014:
            with ZipFile(ROOT/f'data/raw/ipeds/{comp}_dict.zip') as z:
                book=pd.ExcelFile(BytesIO(z.read(z.namelist()[0])))
                freq=pd.read_excel(book,sheet_name='FrequenciesRV')
                codes=freq[freq.varname=='APPDATE']
                mapping={int(r.codevalue):int(re.search(r'20\d\d',r.valuelabel).group()) for r in codes.itertuples() if re.search(r'20\d\d',str(r.valuelabel))}
                if mapping!={1:year-1,2:year}:raise ValueError(f'Unexpected APPDATE mapping {year}: {mapping}')
                period_rules.append(dict(collection_year=year,codes=mapping,source=f'{comp}_dict.zip:FrequenciesRV:APPDATE'))
        keep=[c for c in ['unitid','appdate','applcn','admssn','enrlt','xapplcn','xadmssn','xenrlt'] if c in a]
        a=align_admissions_period(a[keep],year)
        a['admissions_member']=member
        admissions.append(a)
        e,member=csv_zip(ROOT/f'data/raw/ipeds/ef{year}a.zip')
        first=e.loc[e.efalevel==4,['unitid','eftotlt','xeftotlt']].rename(columns={'eftotlt':'first_time_enrollment','xeftotlt':'first_time_enrollment_flag'})
        total=e.loc[e.efalevel==1,['unitid','eftotlt']]
        unique(first,['unitid']);unique(total,['unitid'])
        d=d.merge(total,on='unitid',how='left',validate='one_to_one').merge(first,on='unitid',how='left',validate='one_to_one')
        tuition,_=csv_zip(ROOT/f'data/raw/ipeds/ic{year}_ay.zip')
        cols=[c for c in ['unitid','tuition2','tuition3'] if c in tuition]
        d=d.merge(tuition[cols],on='unitid',how='left',validate='one_to_one')
        finpath=ROOT/f'data/raw/ipeds/f{str(year-1)[2:]}{str(year)[2:]}_f1a.zip'
        if finpath.exists():
            f,member=csv_zip(finpath);members.append(dict(component=finpath.stem,selected_member=member))
            keep=[c for c in ['unitid','f1b01','f1b02','f1b03','f1b27','f1c011','f1c191'] if c in f]
            d=d.merge(f[keep],on='unitid',how='left',validate='one_to_one')
        d['year']=year
        for c in ['first_time_enrollment','eftotlt','tuition2','tuition3']:
            if c in d:d[c]=pd.to_numeric(d[c],errors='coerce').where(lambda s:s>=0)
        frames.append(d)
    (ROOT/'data/provenance/ipeds_selected_members.json').write_text(json.dumps(members,indent=2))
    (ROOT/'data/provenance/admissions_period_rules.json').write_text(json.dumps(period_rules,indent=2))
    adm=pd.concat(admissions,ignore_index=True)
    duplicates=adm[adm.duplicated(['unitid','year'],False)].sort_values(['unitid','year','admissions_collection_year'])
    duplicates.to_csv(ROOT/'data/provenance/admissions_duplicate_candidates.csv',index=False)
    # Some cohorts are reported in two collections. Retain the later collection;
    # save every candidate and its collection year so this rule is reviewable.
    adm=adm.sort_values('admissions_collection_year').drop_duplicates(['unitid','year'],keep='last')
    adm=adm.rename(columns={'applcn':'applications','admssn':'admissions','enrlt':'admissions_enrollment','xenrlt':'admissions_enrollment_flag'})
    for c in ['applications','admissions','admissions_enrollment']:adm[c]=pd.to_numeric(adm[c],errors='coerce').where(lambda s:s>=0)
    adm.to_csv(ROOT/'data/processed/admissions_by_cohort.csv',index=False)
    d=pd.concat(frames,ignore_index=True).rename(columns={'eftotlt':'total_enrollment','tuition2':'in_state_sticker_tuition','tuition3':'out_state_sticker_tuition'})
    d=d.merge(adm,on=['unitid','year'],how='left',validate='one_to_one')
    for col in ['applications','first_time_enrollment','total_enrollment']:d['log_'+col]=positive_log(d[col])
    unique(d,['unitid','year']);return d

def read_cup(year, suffix=''):
    """Read table coordinates, not narrative press-release numbers.

    Column boundaries are inferred on the first table's Stanford row. No fuzzy
    row matching; each record preserves original PDF page and school label.
    """
    cache=ROOT/f'data/interim/cup_{year}{suffix}.csv'
    if cache.exists():return pd.read_csv(cache)
    records=[];layout=None;previous_header=None;previous_cx=None
    with pdfplumber.open(ROOT/f'data/raw/nacda/{year}{suffix}.pdf') as pdf:
        for page_no,page in enumerate(pdf.pages,1):
            words=page.extract_words(x_tolerance=1)
            ranks=[w for w in words if w['text']=='Rank']
            if not ranks and previous_header is None:
                inst=next((w for w in words if w['text']=='Institution'),None)
                stan=next((w for w in words if w['text']=='Stanford' and inst and w['top']>inst['top']),None)
                if inst is None or stan is None:continue
                header=dict(top=inst['top'],x1=stan['x0']-2)
            else:header=ranks[0] if ranks else previous_header
            previous_header=header;top=header['top']
            totals=[w for w in words if w['text'] in ['Total','Points','Final','Fall'] and abs(w['top']-top)<18 and w['x0']>header['x1']]
            if totals:
                total=min(totals,key=lambda w:w['x0']);cx=previous_cx if previous_cx is not None else (total['x0']+total['x1'])/2
            elif previous_cx is not None:cx=previous_cx
            else:continue
            rank_words=[w for w in words if re.fullmatch(r'\d+',w['text']) and w['x0']<header['x1']+2 and w['top']>(top+3 if ranks else top-20)]
            if not rank_words:continue
            if layout is None:
                stanford=next((w for w in words if w['text']=='Stanford' and w['top']>top),None)
                if stanford is None:raise ValueError(f'Stanford row unavailable {year}{suffix}')
                first=stanford
                row=sorted([w for w in words if abs(w['top']-first['top'])<2],key=lambda w:w['x0'])
                numeric=[w for w in row if re.fullmatch(r'\d+(?:\.\d+)?',w['text'])]
                amount=min(numeric,key=lambda w:abs((w['x0']+w['x1'])/2-cx))
                cx=(amount['x0']+amount['x1'])/2;previous_cx=cx
                inst_header=next(w for w in words if w['text']=='Institution' and abs(w['top']-top)<10)
                conf_header=next((w for w in words if w['text']=='Conference' and abs(w['top']-top)<10),None)
                school_left=stanford['x0']-0.5
                after=[w for w in row if stanford['x1']<w['x0']<cx-10]
                if conf_header and conf_header['x0']>inst_header['x0']:
                    inst_center=(inst_header['x0']+inst_header['x1'])/2
                    conf_center=(conf_header['x0']+conf_header['x1'])/2
                    boundaries=[edge['x0'] for edge in page.vertical_edges if inst_center<edge['x0']<conf_center]
                    school_right=min(boundaries) if boundaries else min(conf_header['x0'],after[0]['x0'])-0.5
                else:school_right=amount['x0']-1
                # Sport-specific success is measured using official Cup sport points.
                sport_headers=[w for w in words if abs(w['top']-top)<9 and w['text'] in ['BB','Bsk','Basketball','FB','Football']]
                pts_headers=[w for w in words if w['text'] in ['Pts.','Pts'] and top-0.5 <= w['top']<top+15]
                sport_cols={}
                if suffix=='_winter':
                    bb=[w for w in sport_headers if w['text'] in ['BB','Bsk','Basketball']]
                    if len(bb)>=2:
                        # In these source tables women's basketball precedes men's.
                        target=bb[1]
                        ph=min(pts_headers,key=lambda w:abs(w['x0']-target['x0']))
                        sport_cols['mbb_points']=(ph['x0']+ph['x1'])/2
                if suffix=='_fall':
                    fb=[w for w in sport_headers if w['text'] in ['FB','Football']]
                    if fb:
                        for j,target in enumerate(fb[:2]):
                            ph=min(pts_headers,key=lambda w:abs(w['x0']-target['x0']))
                            sport_cols[['fbs_points','fcs_points'][j]]=(ph['x0']+ph['x1'])/2
                layout=(school_left,school_right,sport_cols)
            for rw in rank_words:
                row=[w for w in words if abs(w['top']-rw['top'])<2]
                name_words=[]
                for w in sorted(row,key=lambda w:w['x0']):
                    if not layout[0] <= w['x0'] < layout[1]:continue
                    text=w['text']
                    if w['x1']>layout[1]:
                        text=''.join(ch['text'] for ch in page.chars if abs(ch['top']-w['top'])<1 and w['x0']<=ch['x0']<layout[1])
                    name_words.append(text)
                school=' '.join(name_words).strip()
                values=[w for w in row if abs((w['x0']+w['x1'])/2-cx)<8 and re.fullmatch(r'\d+(?:\.\d+)?',w['text'])]
                if len(values)!=1 or not school:continue
                record=dict(year=year,cup_name=school,cup_rank=int(rw['text']),cup_points=float(values[0]['text']),pdf_page=page_no,pdf_file=f'nacda/{year}{suffix}.pdf')
                for col,pos in layout[2].items():
                    cells=[w for w in row if abs((w['x0']+w['x1'])/2-pos)<5]
                    nums=[w for w in cells if re.fullmatch(r'\d+(?:\.\d+)?',w['text'])]
                    record[col]=float(nums[0]['text']) if len(nums)==1 else np.nan
                records.append(record)
    d=pd.DataFrame(records)
    if len(d)<150:raise ValueError(f'Too few Cup rows: {year}{suffix}: {len(d)}')
    unique(d,['cup_name','year'])
    # The 2014 publisher table places rank 205 before rank 204 on page 5.
    # Sort published ranks; retain original source page and all published values.
    d=d.sort_values('cup_rank',kind='stable').reset_index(drop=True)
    if suffix=='':
        if d.cup_points.max()<1000 or d.loc[d.cup_rank==1,'cup_name'].tolist()!=['Stanford']:
            raise ValueError(f'Cup validation failed: {year}')
        if not d.cup_points.is_monotonic_decreasing:
            bad=d.index[d.cup_points.diff()>0].tolist()
            raise ValueError(f'Cup points not sorted {year}: {d.loc[sorted(set(bad+[i-1 for i in bad])),["cup_name","cup_rank","cup_points","pdf_page"]].to_dict("records")}')
    d.to_csv(cache,index=False)
    return d

def make_crosswalk(cup,eada):
    schools=eada[['unitid','eada_name']].drop_duplicates()
    # Exact normalized names must identify exactly one institution across all years.
    candidates=defaultdict(set)
    for r in schools.itertuples():candidates[normalize(r.eada_name)].add(int(r.unitid))
    overrides=json.loads((ROOT/'config/school_aliases.json').read_text())
    rows=[]
    for name,year in sorted(set(zip(cup.cup_name,cup.year))):
        key=normalize(name);ids=candidates.get(key,set())
        uid=overrides.get(name)
        if isinstance(uid,dict):uid=uid.get(str(year))
        if uid is not None and uid not in set(schools.unitid):raise ValueError(f'Alias not in EADA DI sample: {name}:{uid}')
        if uid is None and len(ids)==1:uid=next(iter(ids));method='exact_normalized'
        else:method='reviewed_alias' if uid is not None else 'unmatched'
        rows.append(dict(cup_name=name,year=year,unitid=uid,match_method=method,candidate_ids=';'.join(map(str,sorted(ids)))))
    return pd.DataFrame(rows)

def calendar_join(frame, columns, offset, prefix, lookup=None):
    """For each (school,t), join observations from exact calendar year t+offset."""
    right=(frame if lookup is None else lookup)[['unitid','year']+columns].copy()
    unique(right,['unitid','year'])
    right['year']=right['year']-offset
    return frame.merge(right.rename(columns={c:prefix+c for c in columns}),on=['unitid','year'],how='left',validate='one_to_one')

def main():
    for p in ['data/processed','data/interim','results']:(ROOT/p).mkdir(parents=True,exist_ok=True)
    eada=read_eada();ipeds=read_ipeds()
    cup=pd.concat([read_cup(y) for y in range(2010,2020)],ignore_index=True)
    fall=pd.concat([read_cup(y,'_fall') for y in range(2010,2020)],ignore_index=True)
    winter=pd.concat([read_cup(y,'_winter') for y in range(2010,2020)],ignore_index=True)
    cup.to_csv(ROOT/'data/processed/directors_cup.csv',index=False)
    crosswalk=make_crosswalk(pd.concat([cup,fall,winter]),eada);crosswalk.to_csv(ROOT/'data/processed/school_crosswalk.csv',index=False)
    c=cup.merge(crosswalk,on=['cup_name','year'],validate='one_to_one')
    matched=c.dropna(subset=['unitid']).copy();matched.unitid=matched.unitid.astype(int)
    unique(matched,['unitid','year'])
    c[c.unitid.isna()].to_csv(ROOT/'results/unmatched_cup.csv',index=False)
    d=eada.merge(ipeds,on=['unitid','year'],how='left',validate='one_to_one',indicator='ipeds_join')
    d=d.merge(matched.drop(columns=['match_method','candidate_ids']),on=['unitid','year'],how='left',validate='one_to_one',indicator='cup_join')
    for season,frame,cols in [('fall',fall,['fbs_points','fcs_points']),('winter',winter,['mbb_points'])]:
        p=frame.merge(crosswalk,on=['cup_name','year'],validate='one_to_one').dropna(subset=['unitid'])
        p.unitid=p.unitid.astype(int);unique(p,['unitid','year'])
        p[cols+['unitid','year','cup_name','pdf_page','pdf_file']].to_csv(ROOT/f'data/processed/{season}_performance.csv',index=False)
        d=d.merge(p[['unitid','year',*cols]],on=['unitid','year'],how='left',validate='one_to_one')
    d['fbs_10']=d.fbs_points/10;d['mbb_10']=d.mbb_points/10
    d['public']=d.control.eq(1)
    d['cup_observed']=d.cup_points.notna()
    d['cup_100']=d.cup_points/100
    d['cup_percentile']=d.groupby('year').cup_points.rank(pct=True)*100
    d['acceptance_rate']=d.admissions/d.applications.where(d.applications>0)
    d['yield_rate']=d.admissions_enrollment/d.admissions.where(d.admissions>0)
    d['eada_reported_balance']=d.reported_revenue-d.expenses
    for col in ['expenses','reported_revenue','applications','first_time_enrollment','total_enrollment','football_expenses','mbb_expenses']:
        d['log_'+col]=positive_log(d[col])
    d=calendar_join(d,['log_expenses','log_total_enrollment','sport_categories','cup_100','log_football_expenses','log_mbb_expenses'], -1,'lag_')
    d=calendar_join(d,['reported_revenue','log_reported_revenue'],1,'next_')
    # Future admissions come from IPEDS independently of future EADA membership.
    d=calendar_join(d,['applications','first_time_enrollment','log_applications','log_first_time_enrollment','xapplcn','first_time_enrollment_flag'],1,'next_',lookup=ipeds)
    d=calendar_join(d,['log_applications','log_first_time_enrollment'],2,'next2_',lookup=ipeds)
    d['application_growth']=d.next_log_applications-d.log_applications
    d['performance_change']=d.cup_100-d.lag_cup_100
    unique(d,['unitid','year']);d.to_csv(ROOT/'data/processed/panel.csv',index=False)
    # Keep full institution-year federal extracts for transparent exclusions.
    ipeds.to_csv(ROOT/'data/processed/ipeds.csv',index=False)
    eada.to_csv(ROOT/'data/processed/eada.csv',index=False)
    coverage=d.groupby('year').agg(eada_di=('unitid','size'),public_di=('public','sum'),cup_matches=('cup_observed','sum'),applications=('applications','count'),next_applications=('next_applications','count'))
    coverage.to_csv(ROOT/'results/coverage.csv')
    print(coverage.to_string(),flush=True)

if __name__=='__main__':main()
