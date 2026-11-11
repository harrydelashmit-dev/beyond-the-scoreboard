"""Python translation of Anderson Table 3; every outcome is retained."""
import argparse
import hashlib
import json

import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.api as sm
from statsmodels.stats.multitest import multipletests

from .anderson_data import RAW, OUTCOMES, acquire, f32, prepare
from .download import ROOT

# Transcribed before local estimation: author manuscript Table 3, PDF page 36.
# Donations are thousands; acceptance rate is a share in the printed table.
BENCHMARK = [
    ('Athletic alumni operating donations', 1000., 136.4, 41.1, 637, 191.2, 65., 616, .001, .053),
    ('Nonathletic alumni operating donations', 1000., 227.9, 171.4, 637, -137.4, 96.1, 616, .210, .289),
    ('Total alumni donations', 1000., 311.9, 295.7, 1264, 267.4, 266.9, 1258, .450, .539),
    ('Alumni giving rate', 1., -.0001, .0005, 1293, .0002, .0007, 1287, .698, .612),
    ('Academic reputation', 1., .004, .001, 669, .003, .002, 650, .015, .087),
    ('Applications', 1., 135.3, 49.9, 533, 81.1, 60.4, 528, .005, .063),
    ('Acceptance rate (share)', 100., -.003, .001, 967, -.003, .002, 979, .022, .100),
    ('First-time out-of-state enrollment', 1., -.4, 3.4, 1038, 1.6, 5., 962, .983, .704),
    ('First-time in-state enrollment', 1., 15.2, 5.8, 1038, 12.6, 6.4, 962, .007, .069),
    ('25th percentile SAT', 1., 1.8, .6, 431, .8, .7, 426, .002, .053),
]


def stata_centile(values, probs):
    """Stata centile interpolation: order statistic at (n+1)*p."""
    return np.quantile(np.asarray(values)[np.isfinite(values)], probs, method='weibull')


def stata_summary_percentile(values, prob):
    """summarize, detail uses the averaged inverse empirical distribution."""
    return np.quantile(np.asarray(values)[np.isfinite(values)], prob, method='averaged_inverted_cdf')


def matching_groups(prob, win, sample):
    low = max(float(prob.loc[sample & win.eq(1)].min()), .05)
    high = min(float(prob.loc[sample & win.eq(0)].max()), .95)
    eligible = sample & prob.between(low, high)
    cuts = stata_centile(prob.loc[eligible].to_numpy(), np.arange(10, 91, 8) / 100)
    group = np.full(len(prob), np.nan)
    # Equal boundaries belong to the higher bin, exactly as the source loops do.
    group[eligible] = np.searchsorted(cuts, prob.loc[eligible], side='right') + 1
    return group


def design_groups(groups, win, prob):
    """Twelve separate intercept/win/propensity strata (no global constant)."""
    return np.column_stack([part for j in range(1, 13)
                            for part in (np.asarray(groups == j, float),
                                         np.asarray(groups == j, float) * win,
                                         np.asarray(groups == j, float) * prob)])


def fit_cluster(y, x, clusters, weights=None):
    good = np.isfinite(y) & np.isfinite(x).all(axis=1)
    if weights is not None:
        good &= np.isfinite(weights) & (weights > 0)
    model = sm.OLS(y[good], x[good]) if weights is None else sm.WLS(y[good], x[good], weights=weights[good])
    fit = model.fit()
    n, rank = int(fit.nobs), int(fit.model.rank)
    cluster = np.asarray(clusters)[good]
    g = len(np.unique(cluster))
    # Explicit rank-based CR1; unlike cov_cluster's default, it handles empty bins.
    score = fit.model.wexog * fit.wresid[:, None]
    summed = np.stack([score[cluster == key].sum(axis=0) for key in np.unique(cluster)])
    cov = fit.normalized_cov_params @ (summed.T @ summed) @ fit.normalized_cov_params
    cov *= g / (g - 1) * (n - 1) / (n - rank)
    return fit, cov, good, g


def estimate(frame):
    sample = frame.bcs.le(1)
    clusters = frame.school_id.to_numpy()
    # Year effects are fitted before weekly overlap filtering, as in main_results.
    year_x = sm.add_constant(pd.get_dummies(frame.year, drop_first=True, dtype=float)).to_numpy()
    residuals = {}
    for outcome in OUTCOMES:
        difference = f32(frame[outcome] - frame['lag2_' + outcome])
        good = sample.to_numpy() & np.isfinite(difference)
        fit = sm.OLS(difference[good], year_x[good]).fit()
        residuals[outcome] = f32(difference - year_x @ fit.params)
    week_results = []
    for week in range(1, 13):
        win = frame[f'lag_win_wk{week}'].to_numpy()
        prob = frame[f'lag_pscore_wk{week}'].to_numpy()
        groups = matching_groups(pd.Series(prob), pd.Series(win), sample)
        x = design_groups(groups, win, prob)
        x[~(sample.to_numpy() & np.isfinite(groups))] = np.nan
        fs, _, _, _ = fit_cluster(frame[f'lag_exp_wins_wk{week}'].to_numpy(), x, clusters)
        # Author smooths twelve first-stage stratum coefficients with a quadratic.
        grid = np.arange(1, 13, dtype=float)
        sx = np.column_stack([np.ones(12), grid, grid ** 2])
        smooth = sm.OLS(fs.params[1::3], sx).fit()
        fs_effect = f32(smooth.predict(sx))
        fs_se = f32(np.sqrt(np.einsum('ij,jk,ik->i', sx, smooth.cov_params(), sx)))
        if week == 12:
            fs_effect[:] = 0
            fs_se[:] = 0
        denom = 1 + fs_effect
        for outcome in OUTCOMES:
            fit, cov, good, g = fit_cluster(residuals[outcome], x, clusters)
            freq = np.array([np.sum(good & (groups == j)) for j in range(1, 13)], dtype=float)
            wins = np.array([np.sum(good & (groups == j) & (win == 1)) for j in range(1, 13)])
            losses = np.array([np.sum(good & (groups == j) & (win == 0)) for j in range(1, 13)])
            freq[(freq <= 3) | (wins < 2) | (losses < 2)] = 0
            weight = freq / freq.sum()
            effect = fit.params[1::3]
            effect_var = np.diag(cov)[1::3]
            iv = np.sum(weight * effect / denom)
            # Preserve the author's diagonal delta-method approximation for IV.
            iv_var = np.sum(weight ** 2 * (effect_var / denom ** 2 + fs_se ** 2 * effect ** 2 / denom ** 4))
            contrast = np.zeros(x.shape[1]); contrast[1::3] = weight
            rf = contrast @ fit.params
            rf_var = contrast @ cov @ contrast
            week_results.append(dict(outcome=outcome, week=week, coefficient=float(f32(iv)),
                                     std_error=float(f32(np.sqrt(iv_var))), n=int(good.sum()), schools=g,
                                     rf=float(f32(rf)), rf_se=float(f32(np.sqrt(rf_var))),
                                     overlap_n=int(freq.sum())))
    weekly = pd.DataFrame(week_results)
    rows = []
    trim = stata_summary_percentile(frame.lag_ipw_weight.to_numpy(), .9)
    weights = frame.lag_ipw_weight.to_numpy()
    for outcome, benchmark in zip(OUTCOMES, BENCHMARK):
        label, scale, b_iv, se_iv, n_iv, b_ste, se_ste, n_ste, sharp, q = benchmark
        z = weekly.loc[weekly.outcome.eq(outcome)]
        share = z.n / z.n.sum()
        b = float(f32(np.sum(share * z.coefficient)))
        se = float(f32(np.sqrt(np.sum((share * z.std_error) ** 2))))
        rf = float(f32(np.sum(share * z.rf)))
        rf_se = float(f32(np.sqrt(np.sum((share * z.rf_se) ** 2))))
        # Source hard-codes 105 degrees of freedom for matching coefficient p.
        p_iv = 2 * stats.t.sf(abs(b / se), 105)
        critical = stats.t.ppf(.975, 105)
        common = dict(outcome=outcome, label=label, unit_divisor=scale,
                      published_sharp_null_p=sharp, published_all_table_fdr_q=q)
        rows.append(dict(**common, estimator='IV', coefficient=b / scale, std_error=se / scale,
                         n=int(z.n.max()), schools=int(z.schools.max()), p_value=p_iv,
                         ci_low=(b - critical * se) / scale, ci_high=(b + critical * se) / scale,
                         published_coefficient=b_iv, published_std_error=se_iv, published_n=n_iv,
                         rf_sharp_null_p=2 * stats.t.sf(abs(rf / rf_se), 105)))
        difference = f32(frame[outcome] - frame['lag2_' + outcome])
        wins_diff = f32(frame.lag_seasonwins - frame.lag3_seasonwins)
        ste_x = np.column_stack([year_x, wins_diff, frame.lag3_seasonwins,
                                frame.lag_seasongames, frame.lag3_seasongames])
        ste_x[~(sample.to_numpy() & (weights < trim))] = np.nan
        fit, cov, good, g = fit_cluster(difference, ste_x, clusters, weights=weights)
        index = year_x.shape[1]
        b = fit.params[index]; se = np.sqrt(cov[index, index])
        # Original code uses G, rather than G-1, df for STE p-values.
        critical = stats.t.ppf(.975, g)
        rows.append(dict(**common, estimator='STE', coefficient=b / scale, std_error=se / scale,
                         n=int(good.sum()), schools=g, p_value=2 * stats.t.sf(abs(b / se), g),
                         ci_low=(b - critical * se) / scale, ci_high=(b + critical * se) / scale,
                         published_coefficient=b_ste, published_std_error=se_ste, published_n=n_ste,
                         rf_sharp_null_p=np.nan))
    results = pd.DataFrame(rows)
    for estimator in ('IV', 'STE'):
        subset = results.estimator.eq(estimator)
        results.loc[subset, 'holm_ten_outcomes_p'] = multipletests(results.loc[subset, 'p_value'], method='holm')[1]
    results['holm_all_twenty_p'] = multipletests(results.p_value, method='holm')[1]
    # Honest, unit-aware comparison against rounding in the printed table.
    precision = {name: (4 if name == 'vse_alum_giving_rate' else
                        3 if name in ('usnews_academic_rep_new', 'acceptance_rate') else 1)
                 for name in OUTCOMES}
    for column, published in [('coefficient', 'published_coefficient'), ('std_error', 'published_std_error')]:
        results[column + '_matches_printed'] = [
            abs(row[column] - row[published]) <= .5 * 10 ** -precision[row.outcome] + 1e-10
            for _, row in results.iterrows()]
    results['n_matches_printed'] = results.n.eq(results.published_n)
    return results, weekly, float(trim)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--download', action='store_true')
    parser.add_argument('--all-files', action='store_true', help='Also retrieve optional 48MB raw archive')
    parser.add_argument('--report-only', action='store_true')
    args = parser.parse_args()
    if not args.report_only:
        if args.download:
            acquire(args.all_files)
        frame, audit = prepare()
        results, weekly, trim = estimate(frame)
        results.to_csv(ROOT / 'results/anderson_replication.csv', index=False)
        weekly.to_csv(ROOT / 'results/anderson_weekly_estimates.csv', index=False)
        audit.update(trim_90th_percentile=trim, plan_sha256=hashlib.sha256(
            (ROOT / 'config/anderson_plan.json').read_bytes()).hexdigest())
        (ROOT / 'data/provenance/anderson_analysis.json').write_text(json.dumps(audit, indent=2) + '\n', encoding='utf-8')
        print(results[['label', 'estimator', 'coefficient', 'std_error', 'n', 'published_coefficient', 'published_n']].to_string(index=False))
    # Report module is deliberately independent of the raw files.
    from .anderson_report import main as report
    report()


if __name__ == '__main__':
    main()
