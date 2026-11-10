"""Import a legitimately obtained Knight-Newhouse export using explicit mapping.

Raw and normalized finances stay in ignored data/private. No login bypass or
guessed export headings. Required fields are separate, non-overlapping amounts.
"""
import argparse
import hashlib
import json
from pathlib import Path
import pandas as pd
from .download import ROOT
from .clean import unique

FIELDS=['unitid','year','total_revenue','institution_government_support','student_fees','total_expenses']

def normalize_finances(frame, mapping):
    if set(mapping['columns'])!=set(FIELDS):raise ValueError('Mapping must specify exactly the required canonical fields')
    if mapping.get('dollars')!='nominal' or mapping.get('year_convention')!='fiscal_year_ending':
        raise ValueError('Confirm nominal dollars and fiscal_year_ending in mapping')
    if mapping.get('support_and_student_fees_are_separate') is not True:
        raise ValueError('Do not subtract student fees twice: confirm non-overlapping support fields')
    if len(set(mapping['columns'].values()))!=len(FIELDS):raise ValueError('Export columns must be distinct')
    d=frame[list(mapping['columns'].values())].rename(columns={v:k for k,v in mapping['columns'].items()}).copy()
    for col in FIELDS:d[col]=pd.to_numeric(d[col],errors='raise')
    if d[FIELDS].isna().any().any():raise ValueError('Required Knight-Newhouse fields contain missing observations')
    for col in ['unitid','year']:
        if not d[col].eq(d[col].astype(int)).all():raise ValueError(f'{col} must be an integer')
        d[col]=d[col].astype(int)
    unique(d,['unitid','year'])
    if (d[FIELDS[2:]]<0).any().any():raise ValueError('Negative financial amounts require source review')
    d['generated_revenue']=d.total_revenue-d.institution_government_support-d.student_fees
    if (d.generated_revenue<0).any():raise ValueError('Support exceeds total revenue; review mapping')
    d['direct_balance']=d.generated_revenue-d.total_expenses
    return d

def main():
    p=argparse.ArgumentParser();p.add_argument('--input',required=True);p.add_argument('--mapping',required=True);a=p.parse_args()
    path=Path(a.input);mapping=json.loads(Path(a.mapping).read_text())
    raw=pd.read_excel(path) if path.suffix.lower() in ['.xlsx','.xls'] else pd.read_csv(path)
    d=normalize_finances(raw,mapping)
    dest=ROOT/'data/private';dest.mkdir(parents=True,exist_ok=True)
    d.to_csv(dest/'knight_normalized.csv',index=False)
    (dest/'knight_import_provenance.json').write_text(json.dumps(dict(source='Knight-Newhouse College Athletics Database',original_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),mapping=mapping,rows=len(d)),indent=2))
    print(f'Imported {len(d)} institution-years into ignored data/private. Review fiscal-year alignment before interpreting models.')

if __name__=='__main__':main()
