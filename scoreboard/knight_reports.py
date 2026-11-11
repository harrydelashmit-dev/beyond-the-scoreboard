"""Validate saved, displayed Knight-Newhouse report text without imputing data.

The browser capture is an acquisition artifact, not a financial export. This
module parses dollar text in Python and preserves missing observations and zeros.
School names remain source names until a reviewed UNITID crosswalk is available.
"""
import argparse
from decimal import Decimal, InvalidOperation
import hashlib
import json
from pathlib import Path
import re

import pandas as pd

METRICS = (
    'total_expenses', 'total_revenue', 'donor_contributions', 'ticket_sales',
    'institution_government_support', 'student_fees', 'football_spending',
    'football_coaching_salaries',
)


def parse_dollars(text):
    """Return cents-exact Decimal or None; reject unexpected source text."""
    if text == 'N/A':
        return None
    if not re.fullmatch(r'\$-?\d{1,3}(?:,\d{3})*\.\d{2}|\$-?\d+\.\d{2}', text):
        raise ValueError(f'Unrecognized source value: {text!r}')
    try:
        return Decimal(text.replace('$', '').replace(',', ''))
    except InvalidOperation as exc:
        raise ValueError(f'Invalid dollars: {text!r}') from exc


def parse_capture(data, report_url):
    schools = data['schools']
    if not schools or len(set(schools)) != len(schools):
        raise ValueError('Source school names must be nonempty and unique')
    if tuple(data['metrics']) != METRICS or len(data['tables']) != len(METRICS):
        raise ValueError('Metric order must match the inspected report headings')
    rows = []
    reference_years = data['tables'][0]['years']
    if len(set(reference_years)) != len(reference_years):
        raise ValueError('Duplicate year columns')
    for metric, table in zip(METRICS, data['tables'], strict=True):
        years = table['years']
        if years != reference_years or any(not re.fullmatch(r'20\d{2}', y) for y in years):
            raise ValueError('Misaligned or invalid year columns')
        if len(table['values']) != len(schools):
            raise ValueError('School/value row counts differ')
        for school, values in zip(schools, table['values'], strict=True):
            if len(values) != len(years):
                raise ValueError('Dollar cells do not align with year headings')
            for year, text in zip(years, values, strict=True):
                amount = parse_dollars(text)
                rows.append(dict(school_name=school, year=int(year), metric=metric,
                                 source_text=text, dollars=amount,
                                 reported=amount is not None, source_url=report_url))
    return pd.DataFrame(rows)


def combine_captures(frames):
    """Deduplicate identical overlapping reports and reject conflicting values."""
    joined = pd.concat(frames, ignore_index=True)
    keys = ['school_name', 'year', 'metric']
    conflicts = joined.groupby(keys).source_text.nunique().gt(1)
    if conflicts.any():
        raise ValueError(f'Conflicting report values: {list(conflicts[conflicts].index)[:5]}')
    return joined.drop_duplicates(keys).sort_values(keys).reset_index(drop=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--source-url', required=True)
    parser.add_argument('--output-dir', type=Path, default=Path('data/private/knight_reports'))
    args = parser.parse_args()
    data = json.loads(args.input.read_text(encoding='utf-8'))
    frame = parse_capture(data, args.source_url)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    frame.to_csv(args.output_dir / f'{args.input.stem}.long.csv', index=False)
    coverage = frame.groupby(['year', 'metric']).agg(
        listed_schools=('school_name', 'size'), reported=('reported', 'sum'))
    coverage['missing'] = coverage.listed_schools - coverage.reported
    coverage.to_csv(args.output_dir / f'{args.input.stem}.coverage.csv')
    print(coverage.to_string())
    print('Input SHA-256:', hashlib.sha256(args.input.read_bytes()).hexdigest())
    print('Acquisition validation only: school identifiers and fiscal-year alignment still require review.')


if __name__ == '__main__':
    main()
