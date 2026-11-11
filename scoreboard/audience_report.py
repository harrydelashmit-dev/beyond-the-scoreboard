"""Audience-focused report and Claude brief from existing evidence, Python only."""
import html
import json

import numpy as np
import pandas as pd

from .download import ROOT
from .feasibility_report import inline_markup
from .hashes import text_sha256


def one(frame, **filters):
    z = frame
    for column, value in filters.items(): z = z.loc[z[column].eq(value)]
    if len(z) != 1: raise ValueError(f'Ambiguous saved result: {filters}')
    return z.iloc[0]


def build():
    f = pd.read_csv(ROOT / 'results/feasibility_models.csv')
    r = pd.read_csv(ROOT / 'results/return_models.csv')
    a = pd.read_csv(ROOT / 'results/anderson_replication.csv')
    t = one(f, model='B_fpi_ticket_sales', term='fpi_10')
    annual = one(r, model='R_annual', term='change_expense_m')
    three = one(r, model='R_three_year', term='cumulative_expense_m')
    high = one(r, model='H_high_support', term='group1_slope')
    low = one(r, model='H_high_support', term='group0_slope')
    gap = one(r, model='H_high_support', term='spend_x_high_support')
    levels = one(r, model='R_levels_year', term='expense_m')
    gift = one(a, estimator='STE', outcome='alumni_ops_athletics')
    if not (t.holm_family_p < .05 and annual.holm_all_primary_p < .05 and
            three.holm_all_primary_p < .05 and gap.holm_all_primary_p < .05):
        raise ValueError('A main inferential finding no longer clears its recorded correction')
    if not (annual.ci_high < 1 and three.ci_high < 1):
        raise ValueError('Main recovery intervals no longer fall below full coverage')
    pct = lambda value: 100 * np.expm1(value)
    thesis = 'Stronger football is linked to higher ticket receipts, but revenue growth falls short of spending growth in our main models. Prior support dependence separates programs with stronger and weaker recovery.'
    prompt = '''Finalize a focused AC 547 Track A presentation using the supplied existing Python results. Build the main story around the strongest supported relationships and their financial consequences. Do not give every attempted analysis equal time.

Use ten main slides for a twenty-minute talk, with two slides and four minutes per group member. Evan West opens; Luis Ramos explains the comparison and football-ticket result; Harrison Delashmit presents the core spending-versus-receipts analysis; Robert Philyaw explains funding models and actual support dollars; Morgan Beckler closes with CFO implications and essential qualifications.

Lead with the funding problem, then show the positive ticket-revenue association, ask whether revenue covers growing costs, compare recovery by prior support dependence, and finish with the actual funding commitment. Keep the approximately 6.4%, 64 cents, 30 versus 70 cents, and 31.7% figures tied to their exact definitions and samples. The 68-cent three-year result supports the cost-recovery section rather than becoming a separate detour.

Use four main chart files. Move recruitment, Directors’ Cup/spending-success tests, smaller-program surprises, AP-event analyses, exploratory basketball, Power Five and budget-size comparisons, and qualitative hype/reputation discussion out of the main narrative. Preserve the complete results in the appendix. Include one brief disclosure that other pathways were tested and remained inconclusive; do not imply that every attempted hypothesis worked.

Donations belong in supporting material, not the headline argument: the reproduced historical STE method estimates roughly $191,000 more athletic alumni gifts per additional football win, but its adjusted p-value is about 0.041 across ten outcomes and 0.074 across twenty tests. The latter does not clear 5%. The other IV translation remains partial. Do not describe the donation evidence as equally robust as our main ticket/cost-recovery findings.

Distinguish regression associations from descriptive accounting facts. The 31.7% support-dollar increase is an observed matched-school comparison, not another estimated correlation or an effect of winning. Preserve the contrary school/year levels model whose interval includes full cost recovery. Briefly explain that historical associations do not identify causal ROI, a 36-cent immediate university bill, or current NIL-era returns. Applications are not tuition income; athletics gifts are not automatically unrestricted university money.

Keep prose and charts accessible to classmates with little analytics experience. Explain uncertainty ranges once, put exact samples and essential definitions near each chart, and keep detailed p-values, equations and alternative models in backup notes. Do not invent qualitative benefits, observations, financial values, group contributions or instructor consultation. Keep all analysis and chart calculations in Python. Do not search for significance or rerun new specifications merely to improve the story. Never modify Fenix Jobsite.

This audience-focused outline supersedes the previous twelve-slide outline for the school Claude handoff. The previously saved native deck is a reference version and has not been rebuilt in this pass. Use the new ten-slide plan, not the old deck order, when finalizing the presentation.'''
    names = ['Evan West', 'Luis Ramos', 'Harrison Delashmit', 'Robert Philyaw', 'Morgan Beckler']
    slides = [
        (1, '0:00–1:45', 105, 1, 'Most athletics departments need additional funding', None,
         'Open with GAO’s 94% statistic for whole Division I athletics departments in 2023–2024. This is external context, not a result from our 2010–2019 panel or a football-only deficit statistic. Ask why spending keeps growing when so many departments need institutional support. A funding gap before allocations is different from a deficit after support.'),
        (2, '1:45–4:00', 135, 1, 'Does the extra money keep up with the extra cost?', None,
         'State the financial question plainly. A stronger season can accompany more receipts, yet those receipts may not match growing expenses. Winning benefits and returns to additional spending are separate questions. Preview the path: tickets, cost recovery, funding model, actual support burden. Keep hype, reputation and campus-pride arguments out of the evidence story because we did not measure them.'),
        (3, '4:00–5:30', 90, 2, 'We compared universities with their own earlier years', None,
         'Use a simple 2010–2019 timeline and the source names, not a methods lecture. Knight-Newhouse supplies finances, ESPN football strength, IPEDS university size and students, BLS inflation. Validated school/year joins and within-school comparisons reduce confusion between large and small institutions. Samples vary: the ticket result uses 817 school-years/109 universities; annual recovery uses 2,002/227. These are observational comparisons.'),
        (4, '5:30–8:00', 150, 2, 'Stronger football is linked to more ticket money', '06_football_tickets.png',
         f'Explain the dot and uncertainty line once. A ten-point increase in ESPN FPI is associated with {pct(t.coefficient):.2f}% higher following-year all-athletics ticket receipts; the 95% range is {pct(t.ci_low):.2f}%–{pct(t.ci_high):.2f}%. N={int(t.n)}, {int(t.schools)} schools. The association survives its related-test correction. FPI points are not wins, and the receipts are not football-only tickets or attendance. Price and capacity can matter. Handoff: money comes in, but how much does spending grow alongside it?'),
        (5, '8:00–10:00', 120, 3, 'Each extra spending dollar accompanies about 64 cents of revenue', '07_cost_recovery.png',
         f'Harrison presents the central result. Annual changes give {annual.coefficient:.2f} revenue dollars per additional spending dollar, with a 95% range of {annual.ci_low:.2f}–{annual.ci_high:.2f}, N={int(annual.n):,}/{int(annual.schools)} schools. The test is full coverage, slope equals one, and remains below that benchmark after adjustment. The three-year accumulated-flow estimate is {three.coefficient:.2f}, range {three.ci_low:.2f}–{three.ci_high:.2f}; it supports the same main comparison without needing another slide. Revenue removes institutional/government allocations and student fees from exported totals.'),
        (6, '10:00–12:00', 120, 3, 'The remaining gap needs a funding explanation', None,
         f'Clarify the meaning of 64 cents. It is a budget association, not a randomized return, a guaranteed loss or an immediate 36-cent taxpayer bill. Revenue can fund spending; transfers, restricted/in-kind gifts and accounting definitions complicate a cash interpretation. The three-year result concerns accumulated budget flows, not a one-time investment. Briefly disclose the contrary levels comparison: {levels.coefficient:.2f}, 95% range {levels.ci_low:.2f}–{levels.ci_high:.2f}, which includes one. The conclusion is strongest for the main change models. Handoff: the average hides important differences in how programs are funded.'),
        (7, '12:00–14:00', 120, 4, 'Prior support dependence separates cost recovery', '08_support_groups.png',
         f'Compare {low.coefficient:.2f} dollars of recovery for lower-support programs with {high.coefficient:.2f} for higher-support programs. High dependence means allocations/student fees covered at least 50% of expenses in 2010–2012; outcomes are evaluated later. The direct difference is {gap.coefficient:.3f}, interval {gap.ci_low:.3f} to {gap.ci_high:.3f}, family-adjusted p={gap.holm_family_p:.6f}; it also survives all-fourteen adjustment. N={int(gap.n):,}/{int(gap.schools)} schools. These are funding classifications, not judgments of educational value. Avoid claiming every small or non-Power-Five program has the same result.'),
        (8, '14:00–16:00', 120, 4, 'A smaller percentage can hide a larger dollar commitment', '09_support_dollars_share.png',
         'Use the same 222 universities at both endpoints. Inflation-adjusted allocated support plus student fees rose from about $2.34 billion to $3.09 billion, an increase of 31.7%, while support/expenses fell from 31.2% to 28.0%. This is a descriptive matched-school accounting comparison, not a regression or an effect of winning. Explain that expenses grew enough to make support a smaller slice while actual support increased. Handoff: the CFO needs to watch dollars, not just ratios.'),
        (9, '16:00–18:00', 120, 5, 'Ask what additional funding the university must commit', None,
         'Turn the evidence into three practical questions: what incremental receipts can we document, which funding-model peers provide a sensible benchmark, and what continuing university support is required? Track actual dollars as well as percentages. Do not invent tuition, brand values or hypothetical repayment schedules. This is an evaluation framework, not a recommendation to cut every program or a prediction for a specific school.'),
        (10, '18:00–20:00', 120, 5, 'More revenue does not establish financial self-sufficiency', None,
         'Close with the supported connections: stronger football and ticket receipts; incomplete recovery in the main budget-change models; weaker recovery among previously support-dependent programs; and rising support dollars despite a lower expense share. Give a short disclosure: recruitment, spending-success and breakthrough pathways were also tested but did not give consistent primary evidence. Detailed results are in backup. Historical associations do not prove causation, and our results do not establish a positive or negative comprehensive university-wide return. End with the need to evaluate receipts, costs and the continuing funding commitment together.'),
    ]
    backups = [
        ('Alternative financial model', f'The school/year levels coefficient is {levels.coefficient:.3f}, interval [{levels.ci_low:.3f}, {levels.ci_high:.3f}], which includes full coverage. Keep this contrary sensitivity available. Primary annual and three-year change models remain below one after adjustment.'),
        ('Other pathways tested', 'Retain the complete primary application/enrollment and spending-success results, smaller-program interactions, Power Five/budget-size comparisons and exploratory basketball/AP findings in the technical reports. These analyses are outside the main story because their proposed advantages are unconfirmed or specification-sensitive. Insignificance does not prove no benefit.'),
        ('Qualified historical donation evidence', f'STE replication: +${gift.coefficient*1000:,.0f} athletic alumni operating gifts per extra football win, interval ${gift.ci_low*1000:,.0f}–${gift.ci_high*1000:,.0f}; N={int(gift.n)}/{int(gift.schools)} schools. Raw p={gift.p_value:.4f}; Holm across ten outcomes={gift.holm_ten_outcomes_p:.4f}; across twenty tests={gift.holm_all_twenty_p:.4f}. Broader correction is inconclusive. All ten STE estimates match printed precision; IV remains partial. This is a separate earlier sample, historical source dollars and athletics-specific gifts. Do not combine it with the ticket coefficient.'),
        ('Sources and definitions', 'Knight-Newhouse methodology: https://knightnewhousedata.org/about-the-data ; GAO external hook: https://www.gao.gov/products/gao-26-108640 ; IPEDS: https://nces.ed.gov/ipeds/ ; Anderson archive: https://doi.org/10.7910/DVN/ASXOBS . Exact annual ESPN/NACDA/EADA/BLS endpoints, years, hashes, terms and matching rules are in docs/sources.md and the complete reports.'),
    ]
    main = [dict(number=n, time=period, duration_seconds=seconds, member=m, speaker=names[m-1],
                 title=title, image=image, hidden=False, notes=notes)
            for n, period, seconds, m, title, image, notes in slides]
    hidden = [dict(number=i+11, title=title, hidden=True, duration_seconds=0, notes=notes) for i, (title, notes) in enumerate(backups)]
    assert sum(s['duration_seconds'] for s in main) == 1200
    assert all(sum(s['duration_seconds'] for s in main if s['member']==m) == 240 for m in range(1,6))
    plan = dict(title='Beyond the Scoreboard', thesis=thesis, main_slide_count=10, total_slide_count=14,
                total_seconds=1200, slides=main+hidden, prompt_for_claude=prompt,
                main_charts=['06_football_tickets.png','07_cost_recovery.png','08_support_groups.png','09_support_dollars_share.png'],
                saved_native_deck_status='Earlier twelve-slide reference version; this ten-slide plan is the current school Claude direction',
                evidence_policy='Main inferential claims survive the recorded related-test corrections; descriptive support accounting is labeled separately. Donation result remains supporting, correction-dependent evidence.')
    (ROOT/'config/audience_focus.json').write_text(json.dumps(plan, indent=2, ensure_ascii=False)+'\n',encoding='utf-8')
    outline = ['# Beyond the Scoreboard audience focused outline\n', '**Ten main slides · 20 minutes · two slides and four minutes per member**\n', thesis+'\n',
               'This is the current school Claude direction. The previous twelve-slide native presentation is a reference version. Four backup slides and full technical reports retain the wider research record.\n',
               '| Slide | Time | Presenter | Point |\n|---|---|---|---|']
    outline.extend(f'| {s["number"]} | {s["time"]} | {s["speaker"]} | {s["title"]} |' for s in main)
    for s in main:
        outline.extend([f'\n## Slide {s["number"]} — {s["title"]}\n', f'**{s["time"]} · {s["speaker"]}**\n', s['notes']+'\n'])
        if s['image']: outline.append(f'Chart: [source PNG](../results/presentation_charts/{s["image"]})\n')
    outline.append('\n## Backup only\n')
    for title, notes in backups: outline.extend(['### '+title+'\n',notes+'\n'])
    (ROOT/'docs/audience_focused_outline.md').write_text('\n'.join(outline).rstrip()+'\n',encoding='utf-8')
    report = [
        '# Beyond the Scoreboard financial evidence for the audience\n',
        '**Main conclusion:** '+thesis+'\n',
        'The main story uses existing supported findings. The complete research record remains in the technical appendices; no new models were estimated or selected by rerunning until significant.\n',
        '## 1 The financial problem\n',
        'GAO reports that 94% of Division I athletics departments spent more than they generated through athletics in 2023–2024. This external hook concerns whole departments, not football alone, and differs from our historical period. A gap before institutional support is not the same as a deficit after that support. [GAO source](https://www.gao.gov/products/gao-26-108640).\n',
        '## 2 Stronger football is linked to higher ticket receipts\n',
        f'A ten-point increase in ESPN FPI is associated with **{pct(t.coefficient):.2f}% higher following-year all-athletics ticket receipts**, with a 95% interval of **{pct(t.ci_low):.2f}%–{pct(t.ci_high):.2f}%**. The model uses {int(t.n)} school-years and {int(t.schools)} universities and survives its recorded related-test adjustment. FPI is a strength rating, not wins; the outcome is receipts rather than attendance. Prices, capacity and strategy may also matter. This is a conditional association, not an effect of an extra spending dollar.\n',
        '![Football and tickets](results/presentation_charts/06_football_tickets.png)\n',
        '## 3 Revenue growth does not fully match spending growth in the main models\n',
        f'In whole athletics-department budgets, annual changes associate each additional expense dollar with **${annual.coefficient:.2f} of additional revenue after allocated support and student fees are removed**. The 95% interval is **${annual.ci_low:.2f}–${annual.ci_high:.2f}**, using {int(annual.n):,} school-years/{int(annual.schools)} schools. The full-coverage null is slope equals one, p={annual.test_p:.6g}; this remains below one after the recorded correction. The three-year cumulative-flow estimate is **${three.coefficient:.2f}**, interval **${three.ci_low:.2f}–${three.ci_high:.2f}**, and supports the same main comparison.\n',
        'Revenue can finance spending, and accounting definitions and omitted decisions affect both. These slopes are not a causal return, an immediate 36-cent university bill or the payoff from a one-time cash investment. Exported revenue already nets some transfers, and gifts can be restricted or in-kind.\n',
        f'**Important sensitivity:** the simpler school/year levels estimate is **{levels.coefficient:.2f} [{levels.ci_low:.2f}, {levels.ci_high:.2f}]**, which includes full coverage. Our conclusion concerns the main change specifications; it is not universal across every model.\n',
        '![Cost recovery](results/presentation_charts/07_cost_recovery.png)\n',
        '## 4 Funding dependence separates financial recovery\n',
        f'Programs with lower prior support dependence show approximately **${low.coefficient:.2f}** revenue growth per spending dollar, versus **${high.coefficient:.2f}** for programs whose allocations and student fees covered at least half of baseline expenses. The groups are fixed using 2010–2012, then evaluated later. The direct difference is **{gap.coefficient:.3f} [{gap.ci_low:.3f}, {gap.ci_high:.3f}]**; family-adjusted p={gap.holm_family_p:.6f}, all-fourteen adjusted p={gap.holm_all_primary_p:.6f}, N={int(gap.n):,}/{int(gap.schools)} schools. This is a funding-model comparison, not proof that a particular school can cause a larger payoff.\n',
        '![Funding model differences](results/presentation_charts/08_support_groups.png)\n',
        '## 5 Percentages can conceal the actual funding commitment\n',
        'For the same 222 universities, real support dollars rose **31.7%**, from about **$2.34 billion to $3.09 billion**, while support as a share of expenses fell from **31.2% to 28.0%**. Expenses grew enough to shrink the share despite more actual funding. This is an observed matched-school accounting comparison, **not another regression correlation or an estimated consequence of winning**. It matters because a CFO must fund dollars, not percentages.\n',
        '![Actual support burden](results/presentation_charts/09_support_dollars_share.png)\n',
        '## 6 The audience takeaway\n',
        'Stronger football and higher ticket receipts can coexist with incomplete cost recovery. A CFO should document expected incremental receipts, compare the program with similar funding models, and make the continuing university support commitment explicit. The study does not identify a comprehensive positive or negative university-wide financial return, nor a current NIL-era forecast.\n',
        '## Brief disclosure and technical appendices\n',
        'We also tested spending-to-success, recruitment and smaller-program breakthrough pathways. Those comparisons did not supply consistent primary evidence for their proposed advantages, so they are not the main presentation. Qualitative hype, pride and reputation were not measured. Omitting them from the main talk does not establish they are absent or have no value.\n',
        f'Historical donations are **supporting evidence only**: the reproduced STE estimate is +${gift.coefficient*1000:,.0f} per extra football win, but ten-outcome Holm p={gift.holm_ten_outcomes_p:.4f} becomes {gift.holm_all_twenty_p:.4f} across twenty coefficient tests. The broader correction does not clear 5%; IV replication remains partial. Do not treat this as equally robust evidence, add it to the ticket coefficient, or call it a spending return.\n',
        'Full results and contrary evidence: [CFO technical report](CFO_RETURN_REPORT.md), [all primary feasibility results](FEASIBILITY_REPORT.md), [Anderson replication](ANDERSON_REPLICATION_REPORT.md), and [source provenance](docs/sources.md). All analysis and charts remain Python.\n',
    ]
    (ROOT/'AUDIENCE_REPORT.md').write_text('\n'.join(report).rstrip()+'\n',encoding='utf-8')
    web=[]
    for paragraph in report:
        if paragraph.startswith('# '):web.append('<h1>'+html.escape(paragraph[2:].strip())+'</h1>')
        elif paragraph.startswith('## '):web.append('<h2>'+html.escape(paragraph[3:].strip())+'</h2>')
        elif paragraph.startswith('!['):
            path=paragraph.split('](')[1].split(')')[0].removeprefix('results/')
            web.append('<img src="'+path+'" alt="Saved Python chart">')
        else:
            text=inline_markup(paragraph.strip())
            for source,target in [('CFO_RETURN_REPORT.md','return_report.html'),('FEASIBILITY_REPORT.md','feasibility_report.html'),('ANDERSON_REPLICATION_REPORT.md','anderson_report.html'),('docs/sources.md','../docs/sources.md')]:text=text.replace('href="'+source+'"','href="'+target+'"')
            web.append('<p>'+text+'</p>')
    css='body{font:17px/1.6 system-ui;max-width:1050px;margin:auto;padding:32px;color:#15324f}h2{margin-top:42px}img{width:100%;height:auto}a{color:#00736f}'
    (ROOT/'results/audience_report.html').write_text('<!doctype html><html lang="en"><meta charset="utf-8"><title>Audience focused financial evidence</title><style>'+css+'</style>'+''.join(web)+'</html>',encoding='utf-8')
    sources=['results/feasibility_models.csv','results/return_models.csv','results/anderson_replication.csv','results/return_matched_endpoints.csv']
    (ROOT/'data/provenance/audience_focus.json').write_text(json.dumps(dict(
        purpose='Audience-focused editorial selection of existing results; no new estimation',
        main_inference='Football/tickets, annual/three-year recovery, prior-support interaction',
        descriptive='Matched-school support dollars and shares; not a correlation test',
        supporting_only='Correction-dependent historical donations',
        omitted_from_main='Recruitment, spending-success, surprise/small-school, budget-size/Power Five, unmeasured qualitative claims',
        disclosure='Full null, contrary and sensitivity findings remain in technical appendices',
        sources={p:text_sha256(ROOT/p) for p in sources}),indent=2)+'\n',encoding='utf-8')
    return plan


if __name__ == '__main__':
    plan=build()
    print(f'Built focused report and {plan["main_slide_count"]}-slide Claude outline; all original results retained.')
