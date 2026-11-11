"""Synthesize existing research into a readable CFO report; no re-estimation."""
import html
import json

import numpy as np
import pandas as pd

from .download import ROOT
from .feasibility_report import inline_markup, md_table
from .hashes import text_sha256


def main():
    files = ['results/feasibility_models.csv', 'results/return_models.csv', 'results/anderson_replication.csv']
    f, r, a = [pd.read_csv(ROOT / path) for path in files]
    def one(frame, **filters):
        z = frame
        for column, value in filters.items(): z = z.loc[z[column].eq(value)]
        if len(z) != 1: raise ValueError(f'Ambiguous report source: {filters}')
        return z.iloc[0]
    ticket = one(f, model='B_fpi_ticket_sales', term='fpi_10')
    annual = one(r, model='R_annual', term='change_expense_m')
    levels = one(r, model='R_levels_year', term='expense_m')
    high = one(r, model='H_high_support', term='group1_slope')
    low = one(r, model='H_high_support', term='group0_slope')
    gift = one(a, estimator='STE', outcome='alumni_ops_athletics')
    apps = one(a, estimator='STE', outcome='applicants')
    pct = lambda value: 100 * np.expm1(value)
    sections = []
    def section(title, *values): sections.append((title, values))
    section('The question and the conclusion',
        '**Winning has value. Whether additional athletics spending pays for itself is a separate question.** A winning season may bring visibility, pride, recognition and engagement. We did not directly measure those benefits. We found measurable associations with athletics receipts, while recruitment gains and a positive university-wide financial return remain unestablished in our analysis.',
        'The project asks: **Does the financial return associated with athletic investment depend on the type of success and the university’s funding model?** We examine spending, competitive performance, receipts, applications, enrollment and support separately. The proposed spending → success → benefits → return pathway is not a proven causal chain. A win’s benefits do not establish that a university can reliably purchase enough additional wins to cover its spending.')
    evidence = pd.DataFrame([
        ['Visibility, pride, reputation and engagement', 'Plausible campus benefits; no direct measurement or valuation in this project', 'Potential value, not a tested result or assumed financial offset'],
        ['Athletic alumni operating donations', f'STE replication: +${gift.coefficient * 1000:,.0f} per extra football win; 95% interval ${gift.ci_low * 1000:,.0f}–${gift.ci_high * 1000:,.0f}', 'Historical source dollars; gift outcome is athletics-specific; correction-dependent evidence'],
        ['Following-year athletics ticket receipts', f'+{pct(ticket.coefficient):.2f}% per +10 FPI; 95% interval +{pct(ticket.ci_low):.2f}% to +{pct(ticket.ci_high):.2f}%', 'Later-period observational association; survives related-test adjustment'],
        ['Applications and first-time enrollment', 'No primary later-period comparison survives its six-test adjustment', 'Uncertain under these models; absence of a detectable effect does not prove no benefit'],
        ['Additional revenue versus spending', f'Annual main model: ${annual.coefficient:.2f} per additional spending dollar; 95% interval ${annual.ci_low:.2f}–${annual.ci_high:.2f}', 'Below full coverage in main change models; not a causal return or university-wide cash-flow estimate'],
    ], columns=['Benefit or financial question', 'What the evidence shows', 'Interpretation'])
    section('Separate potential benefits from measured outcomes', ('table', evidence),
        'Ticket receipts and donations are quantitative outcomes within athletics. They may have economic value even when they do not cover all expenses. Broader university outcomes require additional evidence: applications must translate into actual incremental entrants, retention, net tuition contribution and costs. We have not measured a comprehensive university-wide cash return or the dollar value of campus benefits.')
    section('Football wins and donations: what the replication adds',
        f'We obtained the public archive for Anderson’s published study and translated its methods into Python. Using author-prepared analytic files, all ten Table 3 sequential-treatment-effect (STE) estimates, standard errors and sample sizes match published rounding. In that method, athletic alumni operating donations are approximately **+${gift.coefficient * 1000:,.0f} per additional football win** ({int(gift.n)} school-years, {int(gift.schools)} schools). The estimate’s ordinary p-value is {gift.p_value:.4f}.',
        f'This finding requires a clear statistical qualification. Holm adjustment across the ten STE outcomes gives **p={gift.holm_ten_outcomes_p:.4f}**; a more conservative adjustment across both methods’ twenty coefficient tests gives **p={gift.holm_all_twenty_p:.4f}**. The donation result therefore clears the 5% threshold for the recorded ten-outcome family, but not the broader sensitivity. We present it as qualified evidence rather than a conclusive payoff.',
        f'The same STE method estimates **{apps.coefficient:.0f} additional applications per win**, with an unadjusted 95% interval from **{apps.ci_low:.0f} to {apps.ci_high:.0f}** ({int(apps.n)} school-years, {int(apps.schools)} schools; p={apps.p_value:.3f}). That interval includes no increase. Our separate IV matching translation is close but still differs from some printed coefficients and standard errors. It remains a partial replication; the report exposes every discrepancy.',
        'These are donations for athletic operations, not verified unrestricted university income. The archived study covers a separate, earlier historical sample including public and private universities. Source dollars, outcome definitions and identifying assumptions differ from our later financial panel. Do not add its donation estimate to our ticket coefficient or treat either as the proceeds of a one-dollar spending intervention. See [the full replication report](ANDERSON_REPLICATION_REPORT.md).',
        ('figure', '05_winning_donations'))
    section('Our later-period panel: success and ticket receipts',
        f'The 2010–2019 source window combines Knight-Newhouse finances, NACDA Directors’ Cup results, ESPN football measures, basketball achievements and NCES IPEDS student outcomes. After audited school/year alignment, stronger football performance predicts higher following-year **all-athletics ticket receipts**: approximately **{pct(ticket.coefficient):.1f}% per 10 FPI points** ({int(ticket.n)} school-years, {int(ticket.schools)} schools). FPI points measure team strength; they are not wins or scoreboard points.',
        'The ticket association survives our related-test correction. It does not establish that an extra spending dollar, a coaching hire or a facility improvement caused the receipts. Pricing, capacity, institutional strategy and other factors can affect the relationship. Initial adjusted spending-to-success tests remain uncertain, so we cannot connect the steps into a demonstrated causal spending payoff.',
        ('figure', '06_football_tickets'))
    section('Do additional receipts cover additional spending?',
        f'In the main annual-change model, a $1 spending increase accompanies approximately **${annual.coefficient:.2f} in additional revenue after institutional/government support and student fees are removed** ({int(annual.n):,} school-years, {int(annual.schools)} schools). The approximately ${annual.ci_low:.2f}–${annual.ci_high:.2f} interval falls below dollar-for-dollar coverage. The three-year cumulative budget-flow model gives approximately $0.68 and also falls below one after adjustment.',
        'These are conditional relationships between reported budgets, with school-clustered inference and enrollment-growth/conference-year controls. Revenue can finance spending, and omitted changes can affect both. The remaining roughly 36 cents is an accounting-gap slope, not an immediate taxpayer bill, a measured causal loss or an investment’s net present value. Three-year flows are not the payoff from a one-time payment.',
        f'Financial definitions matter: exported revenue already nets some transfers, gifts can be restricted or in-kind, and expenses are not a complete incremental economic-cost measure. A contrary school/year levels model gives **{levels.coefficient:.2f}**, with an interval of **{levels.ci_low:.2f}–{levels.ci_high:.2f}** that includes full coverage. The conclusion is strongest for the stated main change models, not every possible specification. Full model and sensitivity tables remain in [the CFO technical report](CFO_RETURN_REPORT.md).',
        ('figure', '07_cost_recovery'))
    section('Which universities show stronger financial recovery?',
        f'Programs with high prior support dependence show weaker cost recovery: approximately **${high.coefficient:.2f} versus ${low.coefficient:.2f} per spending dollar**. High dependence means institutional/government support and student fees covered at least half of observed 2010–2012 expenses. The direct group difference survives related-test adjustment. This is a historical funding-model comparison, not evidence of a larger causal payoff for a particular school.',
        'Budget-size and fixed Power Five comparisons remain less conclusive. The proposed smaller-program advantage after unexpected success is also unconfirmed; contrary exploratory AP-event findings are retained. Across 222 matched universities, real support dollars rose 31.7% from 2010 to 2019 while their expense share fell from 31.2% to 28.0%. A shrinking percentage can coexist with a growing funding commitment. None of the six primary success/support tests establishes that success reduces support after correction.')
    section('University-wide benefits remain a separate assessment',
        'Our primary later-period application/enrollment models do not establish a consistent benefit. Some exploratory basketball specifications are positive but sample/model-sensitive. Published Flutie Effect research finds recruitment benefits under some conditions; differences in samples, eras, outcomes and methods prevent a blanket rejection. Statistical insignificance can reflect small effects, limited power, missing information or model limitations.',
        'Visibility, campus pride, reputation, participation and alumni engagement may matter to a university’s mission. This project did not measure their magnitude or monetize them. Their potential importance does not justify assuming they cover a financial gap; incomplete financial recovery does not establish they have no value. A comprehensive financial assessment would need actual incremental receipts and costs, restricted-gift treatment, student contribution margins, capacity, retention and an appropriate time horizon.')
    section('What a university CFO can take from this',
        'Evaluate two questions separately: what benefits accompany competitive success, and what additional spending is expected to accomplish. Make the continuing university support commitment explicit. Benchmark against programs with comparable funding models, and track support dollars alongside percentages.',
        'Define campus objectives and measures before committing funds. Treat recruitment or reputation benefits as uncertain until measured; do not insert assumed tuition or brand values into a break-even calculation. A university can choose to support athletics for educational or campus reasons without describing that support as a proven self-financing investment.',
        '**Presentation conclusion:** Successful athletics can generate attention and additional receipts. Our evidence supports some measurable athletics benefits, with important qualifications, while it does not establish that increasing spending pays for itself or produces a positive university-wide financial return.')
    section('Evidence, reproducibility and limits',
        'All cleaning, joins, model estimation, chart calculations and tests are Python. No new regressions were run to produce this narrative. The source-specific technical reports retain complete coefficients, p-values, intervals, samples, sensitivity results and provenance. Implementation checks establish consistency, not causation. These historical estimates are not current NIL/revenue-sharing forecasts.',
        'Start with [the feasibility report](FEASIBILITY_REPORT.md), [the CFO technical report](CFO_RETURN_REPORT.md) and [the Anderson replication](ANDERSON_REPLICATION_REPORT.md). [Sources and data use](docs/sources.md) document access and restrictions. The public [Anderson archive](https://doi.org/10.7910/DVN/ASXOBS) and [author manuscript](https://anderson.are.berkeley.edu/pdf/Anderson%202017.pdf) support the historical replication. Rebuild this synthesis using `python -m scoreboard.project_report`.')
    md = ['# Beyond the Scoreboard: winning, spending and university value\n',
          'AC 547 · Track A · Python analytics · Evidence synthesis · November 11, 2026\n']
    web = ['<h1>Beyond the Scoreboard: winning, spending and university value</h1>']
    for title, values in sections:
        md.append('## ' + title + '\n'); web.append('<h2>' + html.escape(title) + '</h2>')
        for value in values:
            if isinstance(value, tuple):
                kind, payload = value
                if kind == 'table':
                    md.append(md_table(payload)); web.append(payload.to_html(index=False, border=0))
                else:
                    md.append(f'![{payload}](results/presentation_charts/{payload}.png)\n')
                    web.append(f'<img src="presentation_charts/{payload}.png" alt="{payload}">')
            else:
                md.append(value + '\n')
                linked = inline_markup(value)
                for source, target in [('FEASIBILITY_REPORT.md', 'feasibility_report.html'),
                                       ('CFO_RETURN_REPORT.md', 'return_report.html'),
                                       ('ANDERSON_REPLICATION_REPORT.md', 'anderson_report.html'),
                                       ('docs/sources.md', '../docs/sources.md')]:
                    linked = linked.replace('href="' + source + '"', 'href="' + target + '"')
                web.append('<p>' + linked + '</p>')
    (ROOT / 'PROJECT_REPORT.md').write_text('\n'.join(md).rstrip() + '\n', encoding='utf-8')
    css = 'body{font:16px/1.6 system-ui;max-width:1100px;margin:auto;padding:32px;color:#15324f}h2{margin-top:40px}table{border-collapse:collapse;font-size:14px}th,td{padding:10px;border-bottom:1px solid #ddd;text-align:left}th{background:#edf5f5}img{width:100%;height:auto}'
    (ROOT / 'results/project_report.html').write_text('<!doctype html><html lang="en"><meta charset="utf-8"><title>Beyond the Scoreboard</title><style>' + css + '</style>' + ''.join(web) + '</html>', encoding='utf-8')
    (ROOT / 'data/provenance/project_report.json').write_text(json.dumps(dict(
        purpose='Synthesis of existing results; no new models or observations',
        sources={path: text_sha256(ROOT / path) for path in files},
        thesis='Winning benefits and returns to additional spending are separate questions',
        quantitative_scope='Athletics receipts and accounting associations; comprehensive university-wide return unmeasured',
        qualitative_scope='Potential campus benefits not directly measured or valued'), indent=2) + '\n', encoding='utf-8')
    print('Built the synthesis report from existing finance, recruitment and replication results.')


if __name__ == '__main__': main()
