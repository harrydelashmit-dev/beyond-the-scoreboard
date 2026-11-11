# Beyond the Scoreboard: 20-minute presentation outline

**Subtitle:** Does athletics revenue growth keep up with spending?

**Audience:** AC 547 classmates and instructor; assume little statistical background.

**Format:** 12 spoken slides, exactly 20 minutes. Five members speak four minutes each. Questions and backup slides follow the talk. Replace member numbers with the actual names. This is an outline with chart assets, not a finished slide deck.

**Main message:** Strong football performance is associated with higher ticket receipts. Growing athletics revenue generally falls short of growing spending in our main models, particularly among programs with high prior support dependence. Recruitment benefits remain uncertain in our sample.

**Named speaking plan:** Evan West (0:00–4:00), Luis Ramos (4:00–8:00), Harrison Delashmit (8:00–12:00), Robert Philyaw (12:00–16:00), Morgan Beckler (16:00–20:00). Harrison presents the core financial findings: football ticket receipts and dollar-for-dollar cost recovery. These names replace Member 1–5 in the original plan.

## Run of show

| Slide | Time | Member | Plain-language slide title | Visual |
|---|---|---|---|---|
| 1 | 0:00–1:15 | 1 | Most DI athletics programs spend more than they generate | Large 94% statistic; source/year |
| 2 | 1:15–2:30 | 1 | What would make athletics a worthwhile investment? | CFO question and three possible benefits |
| 3 | 2:30–4:00 | 1 | We tested the proposed pathway one connection at a time | Spending → success → revenue/student demand → return; label hypotheses |
| 4 | 4:00–6:00 | 2 | We followed public universities across several years | Source list, timeline and sample note |
| 5 | 6:00–8:00 | 2 | Applications did not consistently increase in our main tests | `05_applications.png` |
| 6 | 8:00–10:00 | 3 | Stronger football seasons predict higher ticket receipts | `06_football_tickets.png` |
| 7 | 10:00–12:00 | 3 | Revenue growth generally falls short of spending growth | `07_cost_recovery.png` |
| 8 | 12:00–14:00 | 4 | Prior support dependence separates financial recovery | `08_support_groups.png` |
| 9 | 14:00–16:00 | 4 | A lower support percentage can conceal a larger dollar burden | `09_support_dollars_share.png` |
| 10 | 16:00–17:30 | 5 | A larger breakthrough benefit for smaller programs is uncertain | `10_breakthrough.png` |
| 11 | 17:30–18:30 | 5 | What we checked—and what the data cannot prove | Three checks and three brief limits |
| 12 | 18:30–20:00 | 5 | What should a university CFO take from this? | Four decision points and close |

Six simplified chart pairs are in [results/presentation_charts](../results/presentation_charts). PNG files can be placed in slides; SVG files are scalable. They are generated in Python from existing aggregate results, without new regressions or fabricated observations.

## Slide 1 — Hook: the financial puzzle

**0:00–1:15 · Member 1**

**Display:** Title, **94%**, and “Division I athletics programs that spent more than they generated through athletics, 2023–2024.” Put the source/year in a footer.

**Opening:** “In 2023–2024, 94% of Division I athletics programs spent more than they generated through athletics. Universities help cover that gap. So why continue investing? One argument is that successful sports attract students and bring in more money. We wanted to test how much of that financial argument the data support.”

Clarify that this covers the **whole athletics department, all sports**, not football alone. A gap before support differs from an accounting deficit after that support. This hook is external context, not our own historical-panel result.

**Source:** [U.S. GAO, 2026](https://www.gao.gov/products/gao-26-108640). Its 2023–2024 statistic comes from a different period than our 2010–2019 analysis.

**Transition:** “The decision is whether the benefits justify the financial commitment.”

## Slide 2 — The CFO question

**1:15–2:30 · Member 1**

**Display:** “When athletics spending grows, do the financial benefits keep up?”

Three potential benefits:

- More ticket receipts and other athletics revenue.
- More applications and enrolled students.
- Less need for institutional support and student fees.

**Explain:** A department can bring in more money and still need substantial funding. Extra applications do not automatically become more students or tuition income. Campus culture, participation and educational benefits can matter, but we did not assign invented dollar values to them.

**Transition:** “We separated that argument into connections we could actually test.”

## Slide 3 — The proposed pathway

**2:30–4:00 · Member 1**

**Display:** `More spending → Better results → More revenue / student demand → Worthwhile financial return`.

Label the arrows **“proposed connections to investigate.”** Simple text or dashed arrows are enough.

- We compared overall athletics success with visible football and basketball success.
- Initial spending-to-success results were uncertain after our statistical checks.
- A benefit at one stage does not guarantee the next: higher tickets do not automatically cover additional expenses.

**Handoff:** “To test those connections fairly, we first needed to make sure the schools and years actually lined up.”

## Slide 4 — Data and a fair comparison

**4:00–6:00 · Member 2**

**Display:** 2010–2019, before COVID and the later NIL era. List sources by purpose: Knight-Newhouse/EADA for money; Directors’ Cup/ESPN/tournament results for success; IPEDS for students; BLS for inflation.

**Explain:** “Comparing an established large program with a small program can tell us more about their size than about what an extra dollar accomplishes. We examined changes within universities over time and accounted for common conference and year changes.”

The export lists 240 institutions and 2,400 school-years. Samples differ by analysis. The annual cost-recovery model uses **2,002 school-years across 227 universities**. Do not describe the export as a complete sample for every model or a census of all DI schools.

Mention that school IDs, reporting years, missing observations and original financial values were checked. Financial and football-season labels can differ. Dollar comparisons account for inflation.

**Transition:** “We started with the benefit people often talk about: recruiting more students.”

## Slide 5 — The Flutie Effect in our sample

**6:00–8:00 · Member 2**

**Chart:** [Applications after athletic success](../results/presentation_charts/05_applications.png).

**Say:** “Our main tests did not establish a consistent increase in applications or first-time enrollment following athletic success.”

- Each dot is an estimate; the line shows uncertainty.
- The vertical zero line means no estimated change.
- All three application ranges include zero, leaving the relationship uncertain under these models.

Define Directors’ Cup as broad athletic performance, FPI as football strength, and Sweet Sixteen as a visible basketball achievement. Different success units mean the dots do not rank each sport’s effectiveness per dollar.

**Literature context:** Published studies find recruitment benefits under certain conditions. [Pope and Pope (2009)](https://devingpope.com/assets/files/Website_SEJ%20Sports.pdf) report gains following high-profile football and basketball success, with institution-type differences. Our public-school sample and period differ; we have not disproved the Flutie Effect.

**New replication context (optional 20-second addition):** We downloaded Anderson’s public research archive and reproduced all ten estimates, standard errors and sample sizes from his Table 3 STE method in Python. That method estimates roughly $191,000 more in athletic alumni gifts per additional football win, while applications remain uncertain (+81; 95% interval −39 to +201). The donation result clears a ten-outcome adjustment but not a conservative twenty-test adjustment. The separate IV matching translation remains partial. [Full replication and chart](../ANDERSON_REPLICATION_REPORT.md). This earlier study estimates benefits from wins; it does not estimate returns to spending.

If this addition is used, shorten the preceding literature sentence to preserve the two-minute slot. The paired [replication chart](../results/figures/anderson_replication.png) is an optional literature backup; it has not been inserted into the previously saved presentation. Do not combine its historical donations with our later-period ticket estimate.

**Qualification:** Some annual-change basketball models show a positive applications association, but results depend on the specification. None of the six primary application/enrollment tests clears the related-test adjustment. Keep the complete enrollment figure in backup.

**Handoff:** “Recruitment benefits were uncertain. The ticket-receipts connection was clearer.”

## Slide 6 — The ticket-revenue connection

**8:00–10:00 · Member 3**

**Chart:** [Football strength and following-year ticket receipts](../results/presentation_charts/06_football_tickets.png).

**Display:** **Approximately 6.4% higher following-year ticket receipts per 10 additional FPI points.**

- FPI is ESPN’s strength rating. Ten FPI points are not ten wins or scoreboard points.
- The uncertainty range is approximately **4.0%–8.9%**.
- The sample is **817 school-years / 109 universities**; the association passes our related-test checks.
- These are **all-athletics ticket receipts**, not football-only tickets or measured attendance.

Ticket pricing, capacity and other factors can also matter. This association does not prove that buying a stronger team produces a guaranteed financial return.

**Transition:** “Additional revenue matters, but the CFO still needs to compare it with additional spending.”

## Slide 7 — Does revenue growth cover spending growth?

**10:00–12:00 · Member 3**

**Chart:** [Annual and three-year recovery](../results/presentation_charts/07_cost_recovery.png).

**Display:** Annual **64¢ per $1**; three-year budget flows **68¢ per $1**; orange line **$1 = full coverage**.

Walk through whether the uncertainty ranges reach that line. The main ranges fall below it: **50–79¢** annually and **55–81¢** for three-year flows.

**Define revenue:** We remove reported institutional/government support and student fees from exported revenue. Call it **“revenue after allocated support”** on the slide; explain that transfer/accounting limitations make it a proxy rather than verified cash profit.

These are observed budget relationships. Universities may spend because revenue rose, and other changes can affect both. The remaining 36¢ is not a measured immediate university bill or guaranteed investment loss. Three-year flows compare accumulated changes relative to a preceding annual budget, not a one-time cash investment’s return.

**One-sentence sensitivity:** “A simpler comparison of financial levels is less conclusive about full coverage, while the main annual-change finding remains below coverage across the stated checks.” Put details in backup.

**Handoff:** “The average also hides differences between universities’ funding models.”

## Slide 8 — Which funding models show stronger recovery?

**12:00–14:00 · Member 4**

**Chart:** [Recovery by earlier support dependence](../results/presentation_charts/08_support_groups.png).

**Display:** Lower support dependence **70¢ per $1**; higher support dependence **30¢ per $1**.

Higher dependence means institutional/government support plus student fees covered at least half of expenses in the observed 2010–2012 baseline. Groups were fixed before comparing later outcomes. This is a financial classification, not a judgment of educational quality.

We tested the difference directly; it survives related-test adjustment. It remains negative when each school is removed in turn and in a secondary model including budget size. Prior funding dependence appears more informative than size alone in this panel.

Budget-size and Power Five comparisons are less conclusive. Lower commercial recovery does not establish that participation or other mission benefits lack value.

**Transition:** “Even the way we describe support can change the financial story.”

## Slide 9 — Dollars versus percentages

**14:00–16:00 · Member 4**

**Chart:** [Support dollars and expense share](../results/presentation_charts/09_support_dollars_share.png).

**Display:** Real support dollars **up 31.7%**; support/expenses **31.2% → 28.0%**; same **222 universities**, 2010 versus 2019.

Explain that expenses grew enough for support to become a smaller slice even while the dollar commitment increased. Show the dollar chart first, then the percentage chart. Totals are about **$2.34 billion → $3.09 billion**, in 2019 dollars.

This is a matched descriptive comparison, not an estimated consequence of winning. Our six primary success/support tests also did not reliably establish that success reduces actual support or support shares after adjustment. Higher receipts alone do not establish self-sufficiency.

**Handoff:** “We also checked whether a breakthrough might be especially valuable for a smaller program.”

## Slide 10 — Does a breakthrough help smaller programs more?

**16:00–17:30 · Member 5**

**Chart:** [Revenue and statistical football outperformance](../results/presentation_charts/10_breakthrough.png).

**Ask:** “Could a season stronger than recent history predicts create a larger benefit for a smaller program?”

- Our prediction uses earlier seasons only; we measure how far actual strength exceeds it.
- Smaller-budget FBS programs show a positive within-group revenue estimate.
- Their direct advantage over larger programs remains inconclusive. Different-looking dots alone do not establish different effects.
- Applications and enrollment show no consistent smaller-program advantage.

Smaller means a lower earlier athletics budget among FBS programs, not fewer students. The model does not measure fans’ expectations. An alternative AP-poll definition produces negative applications/enrollment differences; those sparse exploratory results are disclosed in backup.

**Transition:** “The evidence gives us useful financial patterns, along with clear limits.”

## Slide 11 — Checks and limits

**17:30–18:30 · Member 5**

**Display checks:** Correct schools/years; independent recalculation; remove one school at a time.

**Display limits:** Observational data; accounting revenue proxy; historical public-university sample.

The project uses Python, with **32 local tests passing** at the current analysis build. Independent calculations reproduce main estimates. These checks establish implementation consistency, not causation. Our historical findings are not forecasts for the current NIL/revenue-sharing environment. Applications do not automatically create additional net tuition revenue, and campus/educational benefits are incompletely measured.

Keep formulas, p-values and parser details in backup.

## Slide 12 — CFO implications and close

**18:30–20:00 · Member 5**

**Display:**

1. Compare additional revenue with additional costs.
2. Benchmark against comparable funding models.
3. Track support dollars alongside percentages.
4. Require evidence before budgeting for recruitment benefits.

**Close:** “Our study finds a financial benefit associated with stronger football performance, particularly in ticket receipts. But revenue growth generally falls short of spending growth in our main comparisons, and programs with high prior reliance on support show weaker recovery. A university should evaluate the full funding commitment and the benefits it expects, while keeping uncertain recruitment gains separate from revenue it can document.”

Pause, thank the audience, and move to questions. Do not claim that all athletics spending is wasteful or all schools have identical goals.

## Backup slides, outside the 20-minute talk

1. **References:** GAO 2026; Knight-Newhouse methodology/export; IPEDS; EADA; NACDA; ESPN; BLS; Pope and Pope 2009; McFarland, Groothuis and Guignet 2024. Exact source URLs are in [sources](sources.md) and the reports.
2. **Complete recruitment results:** [feasibility_student_demand.png](../results/figures/feasibility_student_demand.png). A raw interval excluding zero does not necessarily pass adjustment across related tests.
3. **Spending-to-success results:** `results/feasibility_primary_coefficients.csv`. All three primary adjusted results remain uncertain.
4. **Cost-recovery sensitivity:** [returns_cost_recovery.png](../results/figures/returns_cost_recovery.png). Include the school/year level estimate **0.929 [0.821, 1.037]**, which includes full recovery. The main change-model conclusion is not universal across specifications.
5. **All school-type comparisons:** [returns_school_types.png](../results/figures/returns_school_types.png). Present direct differences, not a comparison of separate subgroup p-values.
6. **Does success reduce support?** [returns_self_support.png](../results/figures/returns_self_support.png). None of six primary tests clears adjustment.
7. **Exploratory basketball finding:** [feasibility_basketball_robustness.png](../results/figures/feasibility_basketball_robustness.png). Annual-change association is positive; level/trend results depend on model and sample.
8. **Opposite-signed AP results:** `return_models.csv`, models `U_ap_small_budget_fbs_applications` and `U_ap_small_budget_fbs_enrollment`. Negative differences; unadjusted p≈0.0017/0.0010. Smaller-program counts: 11 event rows/10 schools and 12 rows/11 schools. Omission checks retain signs, but sparse events, exploratory multiplicity and observational design limit interpretation.
9. **Hypothetical CFO scenario:** [feasibility_cfo_break_even.png](../results/figures/feasibility_cfo_break_even.png). Label assumptions. Do not multiply regression coefficients into causal ROI.
10. **Technical/source audit:** [CFO methods](cfo_extension_methods.md), [validation](validation.md), sample-flow CSVs and provenance. Exact original 52-school replication requires its missing membership/specification; these slides use independently obtained samples.

## Preparation and language

- Say **“associated with,” “predicts under our model,”** or **“the data suggest.”** Avoid causal return claims.
- Say **“we could not establish a consistent effect in our sample.”** Insignificance does not prove zero benefit or disprove the Flutie Effect.
- Distinguish whole-athletics funding gaps from football-only deficits, and actual allocated support from the accounting gap proxy.
- Explain uncertainty lines once; keep detailed formulas and p-values in backup.
- Use one main takeaway per slide, no more than three or four short bullets, large charts and source/sample footers.
- Rehearse the handoffs. Prepare brief answers on causation, the 94% scope/year, varying samples, the revenue definition and the contrary sensitivity.
- Each member should review the whole analysis and make substantive commits from their own account. Names, instructor consultation, final slide layout and rehearsal remain human project work.

**Rebuild these assets:** `python -m scoreboard.presentation_charts`. It reads versioned aggregate results, generates six PNG/SVG pairs, and records source hashes/plotted coefficients in `data/provenance/presentation_charts.json`. It does not retrieve registered data or rerun regressions.
