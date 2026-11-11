"""Checks for calendar alignment, external benchmarks and clustered inference."""
import numpy as np
import pandas as pd
import statsmodels.api as sm

from scoreboard.anderson import fit_cluster, matching_groups, stata_centile, stata_summary_percentile
from scoreboard.anderson_data import correct_reporting_dates, row_lag
from scoreboard.download import ROOT


def test_calendar_lags_do_not_bridge_gaps_or_schools():
    d = pd.DataFrame(dict(teamname=['A', 'A', 'A', 'B'], year=[2000, 2002, 2003, 2004], value=[10., 20., 30., 40.]))
    lag = row_lag(d, 'value', 1)
    assert lag.isna().tolist() == [True, True, False, True]
    assert lag.iloc[2] == 20
    assert row_lag(d, 'value', 2).isna().all()


def test_reporting_period_shift_uses_adjacent_year_and_preserves_missing():
    d = pd.DataFrame(dict(teamname=['A'] * 4 + ['B'], year=[2000, 2001, 2002, 2004, 2005],
                          value=[100., 110., 120., 140., 150.], flag=[2, 1, 2, 2, 2]))
    app = correct_reporting_dates(d, 'value', 'flag')
    assert app.iloc[0] != app.iloc[0]  # following row reports prior year; not a current-year observation
    assert app.iloc[1] == 120.
    assert app.iloc[2:].isna().all()
    sat = correct_reporting_dates(d, 'value', 'flag', keep_last=True)
    assert sat.iloc[2] == 120.
    assert sat.iloc[3] == 140.


def test_source_percentile_definitions_are_distinct_and_support_is_enforced():
    x = np.array([1., 2., 3., 4.])
    assert stata_centile(x, [.25])[0] == 1.25
    assert stata_summary_percentile(x, .25) == 1.5
    p = pd.Series(np.tile(np.linspace(.01, .99, 100), 2))
    win = pd.Series(np.repeat([0., 1.], 100))
    groups = matching_groups(p, win, pd.Series(True, index=p.index))
    assert np.isnan(groups[(p < .05) | (p > .95)]).all()
    assert set(groups[np.isfinite(groups)]) == set(range(1, 13))


def test_weighted_cluster_covariance_agrees_with_independent_statsmodels_path():
    rng = np.random.default_rng(318)
    school = np.repeat(np.arange(20), 8)
    x = sm.add_constant(rng.normal(size=(160, 2)))
    y = x @ np.array([1., 2., -.5]) + rng.normal(size=20)[school] + rng.normal(size=160)
    weight = rng.uniform(.2, 3, 160)
    fit, cov, good, g = fit_cluster(y, x, school, weight)
    reference = sm.WLS(y, x, weights=weight).fit(cov_type='cluster', cov_kwds={'groups': school})
    np.testing.assert_allclose(fit.params, reference.params, rtol=1e-10)
    np.testing.assert_allclose(cov, reference.cov_params(), rtol=1e-10, atol=1e-10)
    assert good.sum() == 160 and g == 20


def test_saved_replication_matches_all_external_ste_benchmarks_and_discloses_iv_gaps():
    d = pd.read_csv(ROOT / 'results/anderson_replication.csv')
    ste = d.loc[d.estimator.eq('STE')]
    assert len(d) == 20 and len(ste) == 10
    # Independent transcription from Table 3, not the implementation's flags.
    published = np.array([[191.2, 65., 616], [-137.4, 96.1, 616], [267.4, 266.9, 1258],
                          [.0002, .0007, 1287], [.003, .002, 650], [81.1, 60.4, 528],
                          [-.003, .002, 979], [1.6, 5., 962], [12.6, 6.4, 962], [.8, .7, 426]])
    tolerance = np.array([.05, .05, .05, .00005, .0005, .05, .0005, .05, .05, .05])
    actual = ste[['coefficient', 'std_error', 'n']].to_numpy()
    assert np.all(np.abs(actual[:, :2] - published[:, :2]) <= tolerance[:, None])
    np.testing.assert_array_equal(actual[:, 2], published[:, 2])
    assert ste[['coefficient_matches_printed', 'std_error_matches_printed', 'n_matches_printed']].to_numpy().all()
    assert d.n_matches_printed.all()
    assert not d.loc[d.estimator.eq('IV'), 'coefficient_matches_printed'].all()
    assert d.holm_ten_outcomes_p.ge(d.p_value - 1e-12).all()
    assert d.holm_all_twenty_p.ge(d.holm_ten_outcomes_p - 1e-12).all()
