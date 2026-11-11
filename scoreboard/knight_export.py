"""Stage the verified Knight-Newhouse custom-report workbook using Python.

This retains every exported row and missing cell. It does not authorize the
school-year merge or compute generated revenue before definition review.
"""
import argparse
from datetime import datetime, timezone
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import zipfile

import pandas as pd

from .download import ROOT
from .knight_reports import METRICS, parse_capture

COLUMNS = {
    'Data': 'school_name', 'IPEDS ID': 'unitid', 'Year': 'year',
    'NCAA Subdivision': 'ncaa_subdivision', 'FBS Conference': 'fbs_conference',
    'Total Expenses': 'total_expenses', 'Total Revenues': 'total_revenue',
    'Donor Contributions': 'donor_contributions', 'Ticket Sales': 'ticket_sales',
    'Institutional/Government Support': 'institution_government_support',
    'Student Fees': 'student_fees', 'Total Football Spending': 'football_spending',
    'Total Football Coaching Salaries': 'football_coaching_salaries',
}


def read_export(path):
    if not zipfile.is_zipfile(path):
        raise ValueError('Expected a real XLSX workbook, not an HTML error page')
    book = pd.ExcelFile(path)
    if book.sheet_names != ['Data', 'Data Dictionary']:
        raise ValueError(f'Unexpected worksheets: {book.sheet_names}')
    raw = pd.read_excel(book, sheet_name='Data')
    if list(raw.columns) != list(COLUMNS):
        raise ValueError('Export headings changed; inspect before importing')
    d = raw.rename(columns=COLUMNS)
    for column in ['unitid', 'year']:
        values = pd.to_numeric(d[column], errors='raise')
        if values.isna().any() or not values.eq(values.astype(int)).all():
            raise ValueError(f'Invalid {column}')
        d[column] = values.astype(int)
    if d.duplicated(['unitid', 'year']).any():
        raise ValueError('Duplicate source institution-years')
    for column in METRICS:
        d[column] = pd.to_numeric(d[column], errors='raise')
    if d.school_name.isna().any() or d.unitid.le(0).any():
        raise ValueError('Missing school names or invalid identifiers')
    dictionary = pd.read_excel(book, sheet_name='Data Dictionary')
    if list(dictionary.Metric) != list(COLUMNS)[5:]:
        raise ValueError('Dictionary does not match the financial fields')
    return d, dictionary


def verify_displayed_2019(panel, capture_path):
    data = json.loads(Path(capture_path).read_text(encoding='utf-8'))
    displayed = parse_capture(data, 'https://knightnewhousedata.org/reports/dda3742f')
    actual = panel[panel.year.eq(2019)].melt(
        id_vars=['school_name', 'year'], value_vars=list(METRICS),
        var_name='metric', value_name='workbook_dollars')
    joined = displayed.merge(actual, on=['school_name', 'year', 'metric'],
                             how='outer', indicator=True, validate='one_to_one')
    if not joined['_merge'].eq('both').all():
        raise ValueError('Workbook/displayed report school-year coverage differs')
    def same(row):
        if not row.reported:
            return pd.isna(row.workbook_dollars)
        return (pd.notna(row.workbook_dollars) and
                Decimal(str(row.workbook_dollars)).quantize(Decimal('.01')) == row.dollars)
    if not joined.apply(same, axis=1).all():
        raise ValueError('Workbook values disagree with the displayed 2019 report')
    return len(joined)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--source-url', required=True)
    parser.add_argument('--verify-capture', type=Path)
    args = parser.parse_args()
    d, dictionary = read_export(args.input)
    if sorted(d.year.unique().tolist()) != list(range(2010, 2020)):
        raise ValueError('This acquisition expects exactly the 2010–2019 study years')
    checked = verify_displayed_2019(d, args.verify_capture) if args.verify_capture else 0
    private = ROOT / 'data/private'
    private.mkdir(parents=True, exist_ok=True)
    d.to_csv(private / 'knight_source_panel.csv', index=False)
    dictionary.to_json(private / 'knight_data_dictionary.json', orient='records', indent=2)
    long = d.melt(id_vars=['unitid', 'year'], value_vars=list(METRICS), value_name='dollars')
    coverage = long.groupby(['year', 'variable']).dollars.agg(listed='size', reported='count')
    coverage['missing'] = coverage.listed - coverage.reported
    provenance = ROOT / 'data/provenance'
    coverage.to_csv(provenance / 'knight_coverage.csv')
    metadata = dict(source='Knight-Newhouse College Athletics Database',
        attribution='A joint project of the Knight Commission on Intercollegiate Athletics and the S.I. Newhouse School of Public Communications, Syracuse University',
        report_url=args.source_url, retrieval_date_utc=datetime.now(timezone.utc).isoformat(),
        original_filename='Custom Reporting Results Data.xlsx',
        sha256=hashlib.sha256(args.input.read_bytes()).hexdigest(),bytes=args.input.stat().st_size,
        years=sorted(d.year.unique().tolist()),listed_school_years=len(d),
        listed_unitids=int(d.unitid.nunique()),metrics=list(METRICS),dollars='nominal_current',
        rows_with_any_metric=int(d[list(METRICS)].notna().any(axis=1).sum()),
        rows_with_all_eight_metrics=int(d[list(METRICS)].notna().all(axis=1).sum()),
        displayed_2019_cells_independently_checked=checked,
        acquisition='User-generated Custom Reporting result; user completed registration, terms, and CAPTCHA; native Excel download through report modal',
        restrictions='Copyright protected. Academic noncommercial use with attribution. No unrestricted redistribution permission asserted; original workbook and school-level financial data excluded from Git.',
        status='acquired_and_staged_pending_identifier_period_definition_review',
        notes=['All 2400 exported rows and missing values retained; reported zero is not missing',
               'IPEDS ID is provided by source; historical campus/merger reporting identities still require review',
               'Source year is fiscal reporting year; align FY t with academic year ending t before regressions',
               'Total Revenues already deduct Less Transfers to the Institution; reconcile transfer treatment before generated-revenue/ROI calculations',
               'Source methodology flags 2015–2017 football coach-bonus comparability changes',
               'Earlier generic download was a 404 HTML page with .xlsx extension and was not imported',
               'Full 21-year/all-metric report timed out; eight-metric 2019, 2014–2019, and 2010–2019 reports each succeeded'],
        methodology_url='https://knightnewhousedata.org/about-the-data')
    (provenance / 'knight_acquisition.json').write_text(json.dumps(metadata, indent=2), encoding='utf-8')
    print(json.dumps({key:metadata[key] for key in ['listed_school_years','listed_unitids',
        'rows_with_any_metric','rows_with_all_eight_metrics','displayed_2019_cells_independently_checked','sha256']}, indent=2))
    print(coverage.unstack('variable')['reported'].to_string())
    print('Staged private source panel. No regressions or ROI estimates were updated.')


if __name__ == '__main__':
    main()
