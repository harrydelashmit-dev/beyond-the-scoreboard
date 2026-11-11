"""Public Anderson replication archive: acquisition and Python data preparation.

The archived Stata files are input data, not executable analysis. All transformations
below translate the author's documented preparation; no Stata process is called.
"""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
import requests
import statsmodels.api as sm

from .download import ROOT

RAW = ROOT / 'data/raw/literature/anderson'
DOI = '10.7910/DVN/ASXOBS'
FILES = {
    'college data.dta': (2769468, 'a194694a1eed8dfba717f5f8b070eb17'),
    'covers_data.dta': (2769470, '3cd1f273ff09838c8561419a0fd5f2b6'),
    'generate tables.do': (2769472, '575c26df5d31bce932082046a850875f'),
    'README.txt': (2769471, 'df8560ebff021fdd5452be835c06c23d'),
    'import college data.do': (2769469, 'a6f9999a0b5522208ae063be297b8074'),
    'import football data.do': (2769466, 'a2480c1f4ffc58ef4b6ef8badaeb0f21'),
    'Raw Data.tar.gz': (2769467, '049e938156349152614c977b6daf07c1'),
}
OUTCOMES = [
    'alumni_ops_athletics', 'alum_non_athl_ops', 'alumni_total_giving',
    'vse_alum_giving_rate', 'usnews_academic_rep_new', 'applicants',
    'acceptance_rate', 'firsttime_outofstate', 'first_time_instate', 'sat_25',
]


def acquire(all_files=False):
    """Retrieve original formats, verify archive MD5, also record SHA256.

    Dataverse's ingested TAB size differs from original DTA size. Its published
    checksum describes the ORIGINAL file, hence format=original is essential.
    """
    RAW.mkdir(parents=True, exist_ok=True)
    records = []
    for name, (file_id, expected) in FILES.items():
        if not all_files and name == 'Raw Data.tar.gz':
            continue
        path = RAW / name
        url = f'https://dataverse.harvard.edu/api/access/datafile/{file_id}?format=original'
        cached = path.exists() and hashlib.md5(path.read_bytes()).hexdigest() == expected
        if not cached:
            response = requests.get(url, timeout=180)
            response.raise_for_status()
            content = response.content
            if hashlib.md5(content).hexdigest() != expected:
                raise ValueError(f'Published original checksum does not match: {name}')
            path.write_bytes(content)
        content = path.read_bytes()
        records.append(dict(file=name, id=file_id, url=url, bytes=len(content),
                            md5=expected, sha256=hashlib.sha256(content).hexdigest(),
                            status='verified', cached=cached))
    manifest = dict(doi=DOI, version='1.1', license='CC0 1.0', restricted=False,
                    checked_utc=datetime.now(timezone.utc).isoformat(), files=records,
                    note='Original format resolves the ingested TAB/original DTA checksum distinction.')
    (ROOT / 'data/provenance/anderson_replication_downloads.json').write_text(
        json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    return manifest


def f32(x):
    """Stata gen/predict default float storage; keep subsequent math in doubles."""
    return np.asarray(x, dtype=np.float32).astype(float)


def polynomial_pscore(line, win):
    """Fifth-degree source polynomial, rescaled only for numerical conditioning."""
    line = np.asarray(line, dtype=float)
    x = np.column_stack([np.ones(len(line)), line / 10] +
                        [f32(line ** k) / 10 ** k for k in range(2, 6)])
    good = np.isfinite(x).all(axis=1) & np.isfinite(win)
    fit = sm.Logit(np.asarray(win)[good], x[good]).fit(disp=False, maxiter=200, tol=1e-11)
    if not fit.mle_retvals['converged']:
        raise RuntimeError('Propensity logit did not converge')
    result = np.full(len(line), np.nan)
    valid = np.isfinite(x).all(axis=1)
    result[valid] = f32(fit.predict(x[valid]))
    return result


def row_lag(frame, column, periods, consecutive=True):
    """Author's positional lags, protected against school and calendar gaps."""
    valid = frame.teamname.eq(frame.teamname.shift(periods))
    steps = range(1, periods + 1) if consecutive else [periods]
    for step in steps:
        valid &= frame.year.eq(frame.year.shift(step) + step)
    return frame[column].shift(periods).where(valid)


def correct_reporting_dates(frame, column, flag, keep_last=False):
    """Translate reporting period before next-year shift; never bridge gaps."""
    next_year = frame.teamname.eq(frame.teamname.shift(-1)) & frame.year.eq(frame.year.shift(-1) - 1)
    corrected = frame[column].mask(frame[flag].eq(1))
    replace = corrected.isna() & frame[flag].shift(-1).eq(1) & next_year
    corrected = corrected.where(~replace, frame[column].shift(-1))
    # SAT source retains corrected final-year values; applicants source does not.
    return corrected.where(~next_year, corrected.shift(-1)) if keep_last else corrected.shift(-1).where(next_year)


def prepare():
    for name in ('college data.dta', 'covers_data.dta'):
        if not (RAW / name).exists():
            raise FileNotFoundError('Run python -m scoreboard.anderson --download first')
        if hashlib.md5((RAW / name).read_bytes()).hexdigest() != FILES[name][1]:
            raise ValueError(f'Input checksum mismatch: {name}')
    college = pd.read_stata(RAW / 'college data.dta', convert_categoricals=False, convert_dates=False)
    games = pd.read_stata(RAW / 'covers_data.dta', convert_categoricals=False, convert_dates=False)
    audit = dict(college_rows=len(college), college_schools=college.teamname.nunique(), raw_game_rows=len(games))
    bad = games.team.isin([68, 136]) & games.date.eq(14568) & games.line.isna()
    audit['source_error_rows_removed'] = int(bad.sum())
    games = games.loc[~bad].sort_values(['team', 'season', 'date']).copy()
    games['week'] = games.groupby(['team', 'season']).cumcount() + 1
    games = games.loc[games.week.le(12) & ~games.month.isin([12, 1])].copy()
    games = games.loc[games.groupby(['teamname', 'season']).line.transform('count').ge(8)].copy()
    games = games.sort_values(['teamname', 'season', 'week']).reset_index(drop=True)
    games.loc[games.line.isna(), 'win'] = np.nan
    audit.update(eligible_game_rows=len(games), games_with_lines=int(games.line.notna().sum()))
    games['pscore'] = polynomial_pscore(games.line.to_numpy(), games.win.to_numpy())
    games['outperform'] = f32(games.realspread + games.line)
    previous = []
    for week in range(1, 13):
        if week == 1:
            games['line_clean'] = games.line.where(games.week.eq(1))
        else:
            mask = games.week.eq(week) & games.line.notna()
            x = np.column_stack([np.ones(mask.sum()), games.loc[mask, previous].to_numpy()])
            fit = sm.OLS(games.loc[mask, 'line'].to_numpy(), x).fit()
            games.loc[mask, 'line_clean'] = f32(f32(fit.resid) + fit.params[0])
        if week < 12:
            games[f'outperform_{week}'] = games.outperform.where(games.week.eq(week)).groupby(
                [games.teamname, games.season]).transform('mean').fillna(0)
            for power in range(1, 4):
                name = f'outperform_{week}_{power}'
                # Scaling leaves the span unchanged and avoids ill-conditioned cubics.
                games[name] = f32(games[f'outperform_{week}'] ** power) / 10 ** power
                previous.append(name)
    games['line_clean'] = f32(games.line_clean)
    games['pscore_clean'] = polynomial_pscore(games.line_clean.to_numpy(), games.win.to_numpy())
    keys = ['teamname', 'season']
    grouped = games.groupby(keys)
    season = grouped.agg(seasonwins=('win', 'sum'), seasongames=('win', 'count'),
                         bcs=('bcs', 'mean'), exp_wins=('pscore_clean', 'sum'))
    season['pct_win'] = season.seasonwins / season.seasongames
    season['exp_wins_wk12'] = 0.
    for week in range(1, 13):
        weekly = games.loc[games.week.eq(week)].set_index(keys)
        for variable in ('pscore', 'win'):
            season[f'{variable}_wk{week}'] = weekly[variable]
        if week < 12:
            later = games.loc[games.week.gt(week)].groupby(keys).pscore.sum()
            season[f'exp_wins_wk{week}'] = later
    season = season.reset_index().rename(columns={'season': 'year'})
    # Stata collapse of float variables retains float storage.
    for column in season.columns.difference(['teamname', 'year']):
        season[column] = f32(season[column])
    frame = season.merge(college, on=['teamname', 'year'], how='inner', validate='one_to_one')
    frame = frame.sort_values(['teamname', 'year']).reset_index(drop=True)
    audit.update(merged_rows=len(frame), merged_schools=frame.teamname.nunique(),
                 min_year=int(frame.year.min()), max_year=int(frame.year.max()))
    additions = {}
    for variable in season.columns.difference(['teamname', 'year', 'bcs']):
        for lag in (1, 2, 3):
            prefix = 'lag_' if lag == 1 else f'lag{lag}_'
            additions[prefix + variable] = f32(row_lag(frame, variable, lag))
    frame = pd.concat([frame, pd.DataFrame(additions)], axis=1).copy()
    for column in ('satmt25', 'satmt75', 'satvr25', 'satvr75'):
        frame[column] = correct_reporting_dates(frame, column, 'satdate', keep_last=True)
    for column in ('applicants_male', 'applicants_female', 'enrolled_male', 'enrolled_female'):
        frame[column] = correct_reporting_dates(frame, column, 'appdate')
    frame['alum_non_athl_ops'] = f32(frame.alumni_ops_total - frame.alumni_ops_athletics)
    frame['sat_25'] = f32(frame.satmt25 + frame.satvr25)
    frame['applicants'] = f32(frame.applicants_male + frame.applicants_female)
    frame = frame.rename(columns={'first_time_outofstate': 'firsttime_outofstate'})
    for column in OUTCOMES:
        frame['lag2_' + column] = f32(row_lag(frame, column, 2, consecutive=False))
    frame.loc[frame.teamname.isin(['Cincinnati', 'Louisville', 'South Florida', 'Connecticut']), 'bcs'] = 0.
    frame.loc[frame.teamname.eq('Temple'), 'bcs'] = 1.
    factors = []
    for week in range(1, 13):
        win = frame[f'lag_win_wk{week}']
        prob = frame[f'lag_pscore_wk{week}']
        # A missing/nonexistent game contributes probability 1, not an observed win.
        factors.append((win * prob + (1 - win) * (1 - prob)).fillna(1).to_numpy())
    frame['lag_ipw_weight'] = f32(1 / np.prod(factors, axis=0))
    frame.loc[frame.lag_seasongames.isna(), 'lag_ipw_weight'] = np.nan
    frame['school_id'] = pd.factorize(frame.teamname, sort=True)[0] + 1
    audit['eligible_sample_schools'] = int(frame.loc[frame.bcs.le(1), 'teamname'].nunique())
    return frame, audit
