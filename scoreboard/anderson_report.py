"""Readable replication report and chart from aggregate Python results."""
import html
import json

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from .download import ROOT
from .feasibility_report import md_table, pvalue, inline_markup


def main():
    result = pd.read_csv(ROOT / 'results/anderson_replication.csv')
    audit = json.loads((ROOT / 'data/provenance/anderson_analysis.json').read_text())
    ste = result.loc[result.estimator.eq('STE')].copy()
    iv = result.loc[result.estimator.eq('IV')].copy()
    def number(row, column):
        digits = 4 if row.outcome == 'vse_alum_giving_rate' else 3 if row.outcome in ('acceptance_rate', 'usnews_academic_rep_new') else 1
        return f'{row[column]:,.{digits}f}'
    rows = []
    for _, row in ste.iterrows():
        rows.append({'Outcome': row.label, 'Per extra win': number(row, 'coefficient'),
                     '95% interval': '[' + number(row, 'ci_low') + ', ' + number(row, 'ci_high') + ']',
                     'N / schools': f'{row.n:,} / {row.schools}', 'Raw p': pvalue(row.p_value),
                     'Holm p (10 STE outcomes)': pvalue(row.holm_ten_outcomes_p),
                     'Matches published estimate / SE / N': 'Yes' if all([row.coefficient_matches_printed, row.std_error_matches_printed, row.n_matches_printed]) else 'No'})
    table = pd.DataFrame(rows)
    comparisons = []
    for _, row in iv.iterrows():
        comparisons.append({'Outcome': row.label, 'Python IV': number(row, 'coefficient'),
                            'Published IV': number(row, 'published_coefficient'),
                            'Python SE': number(row, 'std_error'), 'Published SE': number(row, 'published_std_error'),
                            'N (both)': f'{row.n:,}'})
    comparison = pd.DataFrame(comparisons)
    sections = []
    def section(title, *paragraphs):
        sections.append((title, paragraphs))
    section('What this adds to our project',
        'We obtained the public replication archive and translated the main analysis into Python. All ten sequential-treatment-effect (STE) estimates, standard errors and sample sizes match the author manuscript’s Table 3 at its displayed precision. This validates one published estimator using the author’s analytic data. The IV matching translation is close but does not fully reproduce the printed coefficients or standard errors; its discrepancies remain visible below.',
        'The useful distinction is between the benefits of winning and the return from buying more athletic inputs. Our later-period cost-recovery analysis addresses the latter accounting relationship. Neither exercise proves that a university can purchase additional wins or earn a positive net institutional return. We keep these cohorts and estimands separate.')
    section('Source verification: how to use Claude’s claims',
        'The [NBER Digest](https://www.nber.org/digest/nov12/benefits-college-athletic-success) summarizes athletic alumni donations as $134,000 per win. The [2012 working paper](https://www.nber.org/system/files/working_papers/w18196/w18196.pdf) instead uses $136,400: five wins yield $682,000, approximately 28%; its accompanying illustrations are 677 applications (5%), a 1.5 percentage-point acceptance-rate decline, 76 additional in-state entrants and nine SAT points. These are scaled model estimates, not five separately observed intervention effects. Five times $134,000 is $670,000, so the two donation figures should not be mixed.',
        'The [author manuscript for the 2017 journal article](https://anderson.are.berkeley.edu/pdf/Anderson%202017.pdf), dated January 21, 2016, distinguishes a fixed schedule’s zero-sum wins from improvements in playing quality that can expand demand. It supports an arms-race interpretation as a possibility, not proof that every athletics benefit is zero-sum. Its Table 3 IV estimates motivate the five-win illustration, while its STE estimates differ. The paper supports some Flutie-type benefits; it cannot support saying that the literature has disproved them. Its all-table FDR q-values for the highlighted positive findings are above 0.05.')
    section('What we downloaded and audited',
        f'The [Harvard Dataverse replication archive](https://doi.org/10.7910/DVN/ASXOBS), version 1.1, lists CC0 1.0 and no restricted files. We obtained both prepared analytic datasets, the original method documentation and the optional raw-source archive. Published MD5 and locally recorded SHA256 hashes verify all seven original files. The ingested game TAB has a different format and byte count; requesting the original DTA resolves its checksum mismatch. No registration or author contact was required.',
        f'The college file contains {audit["college_rows"]:,} rows from {audit["college_schools"]} schools; the game file contains {audit["raw_game_rows"]:,} team-game rows. Two documented source errors are removed. Restricting potential postseason games and requiring at least eight nonmissing betting lines leaves {audit["eligible_game_rows"]:,} rows ({audit["games_with_lines"]:,} with lines). A validated one-to-one school-year merge yields {audit["merged_rows"]:,} rows, {audit["merged_schools"]} schools, {audit["min_year"]}–{audit["max_year"]}. This is the merged analytic frame, not every outcome’s regression sample. Games before the first college year help estimate propensities. Team-game rows can represent both sides of one contest.',
        'This is a replication from author-prepared analytic files. We downloaded the underlying raw archive but have not independently rebuilt its VSE, IPEDS, U.S. News and Covers imports. Archive CC0 metadata does not establish a new license for every upstream commercial source; retain attribution and source terms when reusing those materials. Raw files remain outside Git. The original football data and outcomes predate our 2010–2019 Knight panel and today’s NIL/revenue-sharing environment.')
    section('Reproduced STE results: all ten outcomes',
        'Each estimate describes one additional win under the published weighted model. Donations are thousands of source-period dollars; acceptance rate is a fraction (−0.00333 equals −0.333 percentage points). SAT is the combined math/verbal 25th percentile, not an average score. Intervals are unadjusted 95% coefficient intervals. Holm p-values adjust across these ten STE outcomes, as recorded in the plan.',
        ('table', table),
        'The athletic-donation estimate is approximately +$191,243 per win (95% interval $62,114–$320,373; N=616, 94 schools; raw p=0.0041; ten-outcome Holm p=0.0412). Applications are +81 per win with an interval spanning −39 to +201 (N=528, 111 schools; raw p=0.182). A positive estimate alone does not establish a consistent recruitment benefit. None of the other nine STE outcomes survives the ten-outcome correction.',
        'The original plan separates the two estimators’ ten-outcome families. An additional, more conservative correction across all twenty translated coefficient tests is also supplied in the CSV: the athletic-donation STE p-value becomes approximately 0.074. It therefore does not survive that broader 5% threshold. Multiplicity choices matter; do not present a threshold-dependent result as conclusive.',
        ('figure', 'anderson_replication'))
    section('IV matching translation: unresolved numerical differences',
        'Every printed IV N matches, but some point estimates and standard errors do not match at published precision. For example, our athletic-donation estimate is +$138,010 rather than +$136,400, and applications are +128.7 rather than +135.3. We checked source checksums, year alignment, propensity support/percentiles, overlap restrictions and matrix rank. The remaining matching discrepancy is unresolved. Treat these as a documented partial replication, not an exact validation of the IV method or its published p-values.',
        ('table', comparison),
        'The complete CSV includes our ordinary coefficient p-values, intervals, estimator-specific Holm adjustment, conservative all-twenty adjustment, reduced-form sharp-null p-values where translated, and the paper’s published sharp-null p/FDR q as separate benchmark columns. The latter q-values cover the paper’s broader tables, not just our ten outcomes. We have not reproduced that complete FDR, placebo or robustness pipeline. Do not substitute our ordinary IV coefficient p-value for the paper’s sharp-null test.')
    section('How the Python models work',
        'Game eligibility, reporting-period corrections, adjacent-calendar lags and the fifth-degree logistic propensity models follow the archived documentation. The STE model regresses the two-year change in the outcome on the change in prior-season wins, controlling for earlier wins, both season game counts and year effects. It weights by the inverse probability of the observed season’s win/loss sequence and excludes weights at or above the original global 90th percentile. Standard errors cluster by school. Author-code degrees of freedom are retained for replication.',
        'The matching method uses twelve weekly propensity strata, requires outcome-specific wins/losses overlap, corrects for the effect of an early win on later expected wins, and averages weekly estimates by their sample sizes. Its N is the maximum weekly outcome sample, not twelve times that number. Its reported school count is the maximum weekly cluster count. We retain the source’s quadratic first-stage smoothing and approximate diagonal IV variance calculation, including its assumptions about aggregation.',
        'These methods offer a stronger design than a simple spending/wins correlation, but their interpretation depends on the bookmaker propensity model, common support and the study’s identifying assumptions. Replication does not prove those assumptions. In particular, the later project’s AR(1) FPI outperformance measure is not the same as bookmaker-based unexpected game wins.')
    section('Presentation recommendation and management implication',
        'Replace “the Flutie Effect has little statistical support” with “published research finds benefits from football wins, but our later-period tests do not establish a dependable recruitment payoff.” Keep the central question: can an institution cover additional spending, and under which conditions?',
        'Suggested spoken explanation: “We checked a well-known study using its public data. Our Python replication reproduced its second main method. Extra football wins predicted more alumni gifts to athletics, while the applications estimate was uncertain in that method. Winning can have value, but it does not follow that every school should spend more to chase it.”',
        'Use the paired chart below as an optional backup or brief literature bridge. Keep Harrison’s ticket receipts and cost-recovery findings as the main financial results. Do not add the donation estimate to our ticket coefficient: periods, samples, outcomes, scales and models differ, and doing so could double-count receipts. Tuition ROI additionally requires actual incremental entrants, capacity, retention and net contribution margins; applications are not tuition revenue.')
    section('Reproduce and review',
        'Run `python run_project.py --anderson --download --test` from the repository root. This downloads the required original-format archive files, checks hashes, prepares data, estimates all twenty models and builds this report/chart. Add `python -m scoreboard.anderson --download --all-files` to fetch the optional 48MB raw archive. No Stata software is needed. For offline rebuilding from saved aggregate results, run `python run_project.py --anderson --report-only`.',
        'See `config/anderson_plan.json` (committed before local estimation, dc01b53), `docs/anderson_methods.md`, `results/anderson_replication.csv`, `results/anderson_weekly_estimates.csv`, and the source/analysis manifests under `data/provenance/`. No financial or football observations were invented or added to the original Knight analysis.')
    # A chart of the fully reproduced estimator only; separate units and axes.
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 11,
                         'svg.hashsalt': 'beyond-the-scoreboard-anderson'})
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.8))
    for ax, name, title, unit in zip(axes, ['alumni_ops_athletics', 'applicants'],
                                    ['More athletic alumni donations', 'Applications remain uncertain'],
                                    ['Thousands of source-period dollars', 'Applications']):
        row = ste.loc[ste.outcome.eq(name)].iloc[0]
        ax.errorbar(row.coefficient, 0, xerr=[[row.coefficient - row.ci_low], [row.ci_high - row.coefficient]],
                    fmt='o', color='#008681', capsize=7, markersize=9, linewidth=2)
        ax.axvline(0, color='#667b86', linestyle='--', linewidth=1)
        ax.set_ylim(-.65, .65); ax.set_yticks([])
        ax.set_title(title, fontweight='bold', pad=16)
        ax.set_xlabel('Per additional football win\n' + unit)
        ax.text(.5, .16, f'N = {int(row.n):,}; raw p = {row.p_value:.3f}\n95% interval shown',
                transform=ax.transAxes, ha='center', fontsize=10)
        for edge in ('top', 'right', 'left'): ax.spines[edge].set_visible(False)
    fig.suptitle('Python replication of Anderson’s STE model', fontsize=16, fontweight='bold', y=.99)
    fig.text(.5, .01, 'Donation Holm p: 0.041 across 10 outcomes; 0.074 across 20 tests. Intervals are unadjusted.\nHistorical author-prepared data; winning benefits do not identify spending ROI.',
             ha='center', fontsize=9)
    fig.tight_layout(rect=[0, .12, 1, .91])
    directory = ROOT / 'results/figures'; directory.mkdir(exist_ok=True)
    for suffix in ('png', 'svg'):
        metadata = {'Date': None, 'Creator': 'Beyond the Scoreboard Python'} if suffix == 'svg' else {'Software': 'Beyond the Scoreboard Python'}
        fig.savefig(directory / f'anderson_replication.{suffix}', dpi=180, bbox_inches='tight', metadata=metadata)
        if suffix == 'svg':
            path = directory / f'anderson_replication.{suffix}'
            path.write_text('\n'.join(line.rstrip() for line in path.read_text(encoding='utf-8').splitlines()) + '\n', encoding='utf-8')
    plt.close(fig)
    md = ['# Anderson verification and Python replication\n', 'AC 547 · Beyond the Scoreboard · Public research replication · November 11, 2026\n']
    web = ['<h1>Anderson verification and Python replication</h1>']
    for title, paragraphs in sections:
        md.append('## ' + title + '\n'); web.append('<h2>' + html.escape(title) + '</h2>')
        for value in paragraphs:
            if isinstance(value, tuple):
                kind, payload = value
                if kind == 'table':
                    md.append(md_table(payload)); web.append(payload.to_html(index=False, border=0))
                else:
                    md.append('![Reproduced STE estimates](results/figures/anderson_replication.png)')
                    web.append('<img src="figures/anderson_replication.png" alt="Reproduced STE estimates">')
            else:
                md.append(value + '\n'); web.append('<p>' + inline_markup(value) + '</p>')
    (ROOT / 'ANDERSON_REPLICATION_REPORT.md').write_text('\n'.join(md).rstrip() + '\n', encoding='utf-8')
    css = 'body{font:16px/1.6 system-ui;max-width:1200px;margin:auto;padding:32px;color:#15324f}table{border-collapse:collapse;font-size:13px;width:100%}th,td{padding:8px;border-bottom:1px solid #ddd;text-align:left}th{background:#edf5f5}img{width:100%;height:auto}h2{margin-top:40px}'
    (ROOT / 'results/anderson_report.html').write_text('<!doctype html><html lang="en"><meta charset="utf-8"><title>Anderson replication</title><style>' + css + '</style>' + ''.join(web) + '</html>', encoding='utf-8')
    print('Wrote Anderson replication report, full comparison and PNG/SVG chart.')


if __name__ == '__main__':
    main()
