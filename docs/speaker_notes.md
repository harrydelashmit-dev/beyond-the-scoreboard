# Speaker notes: Beyond the Scoreboard

12 main slides, 20 minutes; four hidden backup slides.

## Slide 1: Beyond the Scoreboard
EVAN WEST
SLIDE 1 OF 12 | 0:00–1:15 | 75 seconds
ROLE: Winning, spending and the research question

0:00–1:15 · Evan West

Display: Title, 94%, and “Division I athletics programs that spent more than they generated through athletics, 2023–2024.” Put the source/year in a footer.

Opening: “In 2023–2024, 94% of Division I athletics programs spent more than they generated through athletics. Yet a winning season can attract attention and bring people together. We asked two different questions: what benefits accompany winning, and does additional spending generate enough revenue to cover its cost?”

Clarify that this covers the whole athletics department, all sports, not football alone. A gap before support differs from an accounting deficit after that support. This hook is external context, not our own historical-panel result.

Source: U.S. GAO, 2026 (https://www.gao.gov/products/gao-26-108640). Its 2023–2024 statistic comes from a different period than our 2010–2019 analysis.

Transition: “A winning program can have value even when athletics requires continuing university support. Those are different parts of the decision.”

KEY SOURCES
Knight-Newhouse financial methodology: https://knightnewhousedata.org/about-the-data
NCES IPEDS: https://nces.ed.gov/ipeds/
EADA: https://ope.ed.gov/athletics/
NACDA Directors' Cup ledgers and ESPN historical performance endpoints: exact annual URLs and hashes in docs/sources.md and data/provenance.
BLS CPI-U series CUUR0000SA0: https://api.bls.gov/publicAPI/v2/timeseries/data/CUUR0000SA0?startyear=2010&endyear=2019&annualaverage=true
GAO context: https://www.gao.gov/products/gao-26-108640
Pope and Pope (2009): https://devingpope.com/assets/files/Website_SEJ%20Sports.pdf
McFarland, Groothuis and Guignet (2024): https://onlinelibrary.wiley.com/doi/full/10.1111/coep.12642
Anderson replication archive: https://doi.org/10.7910/DVN/ASXOBS; author manuscript: https://anderson.are.berkeley.edu/pdf/Anderson%202017.pdf
Our Python STE replication and partial IV comparison: ANDERSON_REPLICATION_REPORT.md. Main slide 5: results/presentation_charts/05_winning_donations.png.
Synthesis and framing: PROJECT_REPORT.md. Potential qualitative benefits were not directly measured or valued.
Our results and exact model IDs: FEASIBILITY_REPORT.md, CFO_RETURN_REPORT.md, results/feasibility_models.csv and results/return_models.csv.
Repository: https://github.com/harrydelashmit-dev/beyond-the-scoreboard


## Slide 2: Winning can have several kinds of value
EVAN WEST
SLIDE 2 OF 12 | 1:15–2:30 | 75 seconds
ROLE: Winning, spending and the research question

1:15–2:30 · Evan West

Display: “Winning can have several kinds of value.”

Separate three categories:

- Visibility, pride, reputation and engagement: plausible benefits, not directly measured here.
- Athletics receipts: ticket revenue and alumni donations have quantitative evidence, with qualifications.
- University-wide finances: recruitment and net tuition benefits remain uncertain; full financial return is unestablished.

Explain: A department can bring in more money and still need substantial funding. Extra applications do not automatically become more enrolled students or net tuition income. We did not assign invented dollar values to campus benefits. Lack of measurement does not prove they are absent; it also does not establish that they offset costs.

Transition: “The key is to distinguish the rewards of winning from what an extra spending dollar accomplishes.”

KEY SOURCES
Knight-Newhouse financial methodology: https://knightnewhousedata.org/about-the-data
NCES IPEDS: https://nces.ed.gov/ipeds/
EADA: https://ope.ed.gov/athletics/
NACDA Directors' Cup ledgers and ESPN historical performance endpoints: exact annual URLs and hashes in docs/sources.md and data/provenance.
BLS CPI-U series CUUR0000SA0: https://api.bls.gov/publicAPI/v2/timeseries/data/CUUR0000SA0?startyear=2010&endyear=2019&annualaverage=true
GAO context: https://www.gao.gov/products/gao-26-108640
Pope and Pope (2009): https://devingpope.com/assets/files/Website_SEJ%20Sports.pdf
McFarland, Groothuis and Guignet (2024): https://onlinelibrary.wiley.com/doi/full/10.1111/coep.12642
Anderson replication archive: https://doi.org/10.7910/DVN/ASXOBS; author manuscript: https://anderson.are.berkeley.edu/pdf/Anderson%202017.pdf
Our Python STE replication and partial IV comparison: ANDERSON_REPLICATION_REPORT.md. Main slide 5: results/presentation_charts/05_winning_donations.png.
Synthesis and framing: PROJECT_REPORT.md. Potential qualitative benefits were not directly measured or valued.
Our results and exact model IDs: FEASIBILITY_REPORT.md, CFO_RETURN_REPORT.md, results/feasibility_models.csv and results/return_models.csv.
Repository: https://github.com/harrydelashmit-dev/beyond-the-scoreboard


## Slide 3: Winning benefits and spending returns are different questions
EVAN WEST
SLIDE 3 OF 12 | 2:30–4:00 | 90 seconds
ROLE: Winning, spending and the research question

2:30–4:00 · Evan West

Display: Three separate questions: “Does spending predict success?” “Does success predict receipts or student demand?” “Does revenue growth cover spending growth?”

The proposed spending → success → benefits → return pathway is a hypothesis, not a demonstrated causal chain.

- Our adjusted spending-to-success results remain uncertain.
- A win can bring benefits without proving a university can reliably buy additional wins.
- Higher receipts do not automatically cover the full added cost or establish university-wide profit.

Optional analogy: More customers entering a store does not establish that a costly renovation paid for itself. Likewise, the benefits accompanying wins and the payoff from a larger athletics budget require separate evidence.

Handoff: “To test those connections fairly, we first needed to make sure the schools and years actually lined up.”

KEY SOURCES
Knight-Newhouse financial methodology: https://knightnewhousedata.org/about-the-data
NCES IPEDS: https://nces.ed.gov/ipeds/
EADA: https://ope.ed.gov/athletics/
NACDA Directors' Cup ledgers and ESPN historical performance endpoints: exact annual URLs and hashes in docs/sources.md and data/provenance.
BLS CPI-U series CUUR0000SA0: https://api.bls.gov/publicAPI/v2/timeseries/data/CUUR0000SA0?startyear=2010&endyear=2019&annualaverage=true
GAO context: https://www.gao.gov/products/gao-26-108640
Pope and Pope (2009): https://devingpope.com/assets/files/Website_SEJ%20Sports.pdf
McFarland, Groothuis and Guignet (2024): https://onlinelibrary.wiley.com/doi/full/10.1111/coep.12642
Anderson replication archive: https://doi.org/10.7910/DVN/ASXOBS; author manuscript: https://anderson.are.berkeley.edu/pdf/Anderson%202017.pdf
Our Python STE replication and partial IV comparison: ANDERSON_REPLICATION_REPORT.md. Main slide 5: results/presentation_charts/05_winning_donations.png.
Synthesis and framing: PROJECT_REPORT.md. Potential qualitative benefits were not directly measured or valued.
Our results and exact model IDs: FEASIBILITY_REPORT.md, CFO_RETURN_REPORT.md, results/feasibility_models.csv and results/return_models.csv.
Repository: https://github.com/harrydelashmit-dev/beyond-the-scoreboard


## Slide 4: Two historical sources of evidence
LUIS RAMOS
SLIDE 4 OF 12 | 4:00–6:00 | 120 seconds
ROLE: Data, donations and recruitment evidence

4:00–6:00 · Luis Ramos

Display: 2010–2019, before COVID and the later NIL era. List sources by purpose: Knight-Newhouse/EADA for money; Directors’ Cup/ESPN/tournament results for success; IPEDS for students; BLS for inflation.

Show Anderson’s public replication archive as a separate earlier historical study, covering public and private institutions. Our Python translation reproduces all ten Table 3 STE point estimates, standard errors and sample sizes at published precision. The other IV matching translation is close but incomplete. This is replication from author-prepared files; the raw underlying imports have not been independently reconstructed.

Explain: “Comparing an established large program with a small program can tell us more about their size than about what an extra dollar accomplishes. We examined changes within universities over time and accounted for common conference and year changes.”

The export lists 240 institutions and 2,400 school-years. Samples differ by analysis. The annual cost-recovery model uses 2,002 school-years across 227 universities. Do not describe the export as a complete sample for every model or a census of all DI schools.

Mention that school IDs, reporting years, missing observations and original financial values were checked. Financial and football-season labels can differ. Dollar comparisons account for inflation.

Transition: “The historical replication lets us compare a direct athletics benefit—donations—with the broader recruitment argument.”

KEY SOURCES
Knight-Newhouse financial methodology: https://knightnewhousedata.org/about-the-data
NCES IPEDS: https://nces.ed.gov/ipeds/
EADA: https://ope.ed.gov/athletics/
NACDA Directors' Cup ledgers and ESPN historical performance endpoints: exact annual URLs and hashes in docs/sources.md and data/provenance.
BLS CPI-U series CUUR0000SA0: https://api.bls.gov/publicAPI/v2/timeseries/data/CUUR0000SA0?startyear=2010&endyear=2019&annualaverage=true
GAO context: https://www.gao.gov/products/gao-26-108640
Pope and Pope (2009): https://devingpope.com/assets/files/Website_SEJ%20Sports.pdf
McFarland, Groothuis and Guignet (2024): https://onlinelibrary.wiley.com/doi/full/10.1111/coep.12642
Anderson replication archive: https://doi.org/10.7910/DVN/ASXOBS; author manuscript: https://anderson.are.berkeley.edu/pdf/Anderson%202017.pdf
Our Python STE replication and partial IV comparison: ANDERSON_REPLICATION_REPORT.md. Main slide 5: results/presentation_charts/05_winning_donations.png.
Synthesis and framing: PROJECT_REPORT.md. Potential qualitative benefits were not directly measured or valued.
Our results and exact model IDs: FEASIBILITY_REPORT.md, CFO_RETURN_REPORT.md, results/feasibility_models.csv and results/return_models.csv.
Repository: https://github.com/harrydelashmit-dev/beyond-the-scoreboard


## Slide 5: Football wins, donations and recruitment
LUIS RAMOS
SLIDE 5 OF 12 | 6:00–8:00 | 120 seconds
ROLE: Data, donations and recruitment evidence

6:00–8:00 · Luis Ramos

Chart: Football wins, donations and applications (../results/presentation_charts/05_winning_donations.png).

Say: “In the historical method we reproduced, one additional football win predicts more alumni donations to athletics. The applications estimate is much less certain. This provides evidence of a benefit from winning, without proving that a larger athletics budget pays for itself.”

- Athletic alumni operating donations: approximately +$191,000 per additional win, 95% interval +$62,000 to +$320,000, 616 school-years / 94 schools; source-period dollars.
- Applications: approximately +81, with interval −39 to +201, 528 school-years / 111 schools. The range includes no increase.
- Dots are estimates; lines are unadjusted 95% ranges. The donation result passes correction across ten STE outcomes (p=0.041), but not a broader twenty-test correction (p=0.074). Avoid presenting it as conclusive.

Spend about 65 seconds on the paired chart, 25 seconds on statistical limitations, and 30 seconds connecting it to our later-period study. Dollars and applications have separate axes. This is the reproduced STE method; Claude’s roughly $136,400-per-win figure comes from the paper’s different IV estimator. Our IV translation has unresolved numerical discrepancies, so do not present that figure as our exact replication.

Connection to our study: None of our six primary application/enrollment tests clears its related-test adjustment. Some annual-change basketball models are positive but specification-sensitive. Keep the original three-measure applications chart (../results/presentation_charts/05_applications.png) and complete enrollment results in backup. This does not disprove the Flutie Effect or establish that all university-wide benefits are zero.

Literature context: Published research supports recruitment effects under some conditions; samples, periods and methods differ. Anderson verification and full results (../ANDERSON_REPLICATION_REPORT.md) and Pope and Pope (2009) (https://devingpope.com/assets/files/Website_SEJ%20Sports.pdf) provide context. We do not claim the literature has rejected the Flutie Effect.

Accounting qualification: These are alumni gifts for athletic operations, not unrestricted university income. Do not add them to our later-period ticket estimate: the samples, years, models and units differ, and revenue categories may overlap.

Handoff: “That was evidence about wins. Harrison will show the ticket-receipts connection in our later-period panel, then ask whether growing receipts keep pace with spending.”

KEY SOURCES
Knight-Newhouse financial methodology: https://knightnewhousedata.org/about-the-data
NCES IPEDS: https://nces.ed.gov/ipeds/
EADA: https://ope.ed.gov/athletics/
NACDA Directors' Cup ledgers and ESPN historical performance endpoints: exact annual URLs and hashes in docs/sources.md and data/provenance.
BLS CPI-U series CUUR0000SA0: https://api.bls.gov/publicAPI/v2/timeseries/data/CUUR0000SA0?startyear=2010&endyear=2019&annualaverage=true
GAO context: https://www.gao.gov/products/gao-26-108640
Pope and Pope (2009): https://devingpope.com/assets/files/Website_SEJ%20Sports.pdf
McFarland, Groothuis and Guignet (2024): https://onlinelibrary.wiley.com/doi/full/10.1111/coep.12642
Anderson replication archive: https://doi.org/10.7910/DVN/ASXOBS; author manuscript: https://anderson.are.berkeley.edu/pdf/Anderson%202017.pdf
Our Python STE replication and partial IV comparison: ANDERSON_REPLICATION_REPORT.md. Main slide 5: results/presentation_charts/05_winning_donations.png.
Synthesis and framing: PROJECT_REPORT.md. Potential qualitative benefits were not directly measured or valued.
Our results and exact model IDs: FEASIBILITY_REPORT.md, CFO_RETURN_REPORT.md, results/feasibility_models.csv and results/return_models.csv.
Repository: https://github.com/harrydelashmit-dev/beyond-the-scoreboard


## Slide 6: Football strength and ticket receipts
HARRISON DELASHMIT
SLIDE 6 OF 12 | 8:00–10:00 | 120 seconds
ROLE: Core financial findings: tickets and cost recovery

8:00–10:00 · Harrison Delashmit

Chart: Football strength and following-year ticket receipts (../results/presentation_charts/06_football_tickets.png).

Display: Approximately 6.4% higher following-year ticket receipts per 10 additional FPI points.

- FPI is ESPN’s strength rating. Ten FPI points are not ten wins or scoreboard points.
- The uncertainty range is approximately 4.0%–8.9%.
- The sample is 817 school-years / 109 universities; the association passes our related-test checks.
- These are all-athletics ticket receipts, not football-only tickets or measured attendance.

Ticket pricing, capacity and other factors can also matter. This association does not prove that buying a stronger team produces a guaranteed financial return.

Transition: “We have evidence connecting success with receipts. That still leaves a different CFO question: does additional revenue cover additional spending?”
HARRISON: CORE FINANCIAL INTERPRETATION
This is the clearest financial association from the first study. Explain FPI once, then focus on receipts. The outcome is next-year all-athletics ticket receipts, not ticket attendance and not football-only sales. A 10-point change is on the FPI strength scale. Our estimate is 6.41%, with 95% interval 3.99% to 8.89%, based on 817 observations and 109 schools. Related-test correction does not remove the association. Ticket price, capacity and pricing strategy are not fully measured. We cannot infer that a particular coaching hire or budget increase produces this result.
Spend about 30 seconds explaining the measure, 45 seconds walking through the dot and range, and 45 seconds on interpretation and the handoff to costs.
SOURCE ROW: B_fpi_ticket_sales / fpi_10, results/feasibility_models.csv.


KEY SOURCES
Knight-Newhouse financial methodology: https://knightnewhousedata.org/about-the-data
NCES IPEDS: https://nces.ed.gov/ipeds/
EADA: https://ope.ed.gov/athletics/
NACDA Directors' Cup ledgers and ESPN historical performance endpoints: exact annual URLs and hashes in docs/sources.md and data/provenance.
BLS CPI-U series CUUR0000SA0: https://api.bls.gov/publicAPI/v2/timeseries/data/CUUR0000SA0?startyear=2010&endyear=2019&annualaverage=true
GAO context: https://www.gao.gov/products/gao-26-108640
Pope and Pope (2009): https://devingpope.com/assets/files/Website_SEJ%20Sports.pdf
McFarland, Groothuis and Guignet (2024): https://onlinelibrary.wiley.com/doi/full/10.1111/coep.12642
Anderson replication archive: https://doi.org/10.7910/DVN/ASXOBS; author manuscript: https://anderson.are.berkeley.edu/pdf/Anderson%202017.pdf
Our Python STE replication and partial IV comparison: ANDERSON_REPLICATION_REPORT.md. Main slide 5: results/presentation_charts/05_winning_donations.png.
Synthesis and framing: PROJECT_REPORT.md. Potential qualitative benefits were not directly measured or valued.
Our results and exact model IDs: FEASIBILITY_REPORT.md, CFO_RETURN_REPORT.md, results/feasibility_models.csv and results/return_models.csv.
Repository: https://github.com/harrydelashmit-dev/beyond-the-scoreboard


## Slide 7: Annual and cumulative cost recovery
HARRISON DELASHMIT
SLIDE 7 OF 12 | 10:00–12:00 | 120 seconds
ROLE: Core financial findings: tickets and cost recovery

10:00–12:00 · Harrison Delashmit

Chart: Annual and three-year recovery (../results/presentation_charts/07_cost_recovery.png).

Display: Annual 64¢ per $1; three-year budget flows 68¢ per $1; orange line $1 = full coverage.

Walk through whether the uncertainty ranges reach that line. The main ranges fall below it: 50–79¢ annually and 55–81¢ for three-year flows.

Define revenue: We remove reported institutional/government support and student fees from exported revenue. Call it “revenue after allocated support” on the slide; explain that transfer/accounting limitations make it a proxy rather than verified cash profit.

These are observed budget relationships. Universities may spend because revenue rose, and other changes can affect both. The remaining 36¢ is not a measured immediate university bill or guaranteed investment loss. Three-year flows compare accumulated changes relative to a preceding annual budget, not a one-time cash investment’s return.

One-sentence sensitivity: “A simpler comparison of financial levels is less conclusive about full coverage, while the main annual-change finding remains below coverage across the stated checks.” Put details in backup.

Handoff: “The average also hides differences between universities’ funding models.”
HARRISON: THE CENTRAL COST-RECOVERY RESULT
The annual model relates real-dollar revenue changes to real-dollar spending changes, with enrollment growth and conference-year controls. The financial benchmark is 1 dollar, not a zero correlation. The coefficient is 0.6424, with pointwise 95% interval 0.4997 to 0.7852; 2,002 cases and 227 schools. Three-year cumulative annual-flow changes give 0.6809, interval 0.5489 to 0.8128; 1,545 overlapping windows and 225 schools. These windows compare t, t+1 and t+2 with three times the preceding annual budget. They are not returns on one initial cash payment.
Both primary tests remain below one after adjustment across all fourteen extension tests. One-school omission ranges remain below one. Positive-spending-only, balanced-reporting and several time-control variants agree directionally. The school/year LEVEL sensitivity is less conclusive: 0.929, interval 0.821 to 1.037. We disclose it in backup slide 13.
R equals exported total revenues minus institutional/government support and student fees. Transfers already netted from revenue, restricted/in-kind donations and expense definitions limit a cash interpretation. The 36-cent residual is an accounting-gap slope, not an immediate taxpayer bill or a causal loss. Actual allocated support is measured separately. Revenue can fund spending, and omitted strategy affects both.
SOURCE ROWS: R_annual / change_expense_m; R_three_year / cumulative_expense_m; R_levels_year / expense_m, results/return_models.csv.
HANDOFF TO ROBERT: The average also hides differences between universities' funding models.


KEY SOURCES
Knight-Newhouse financial methodology: https://knightnewhousedata.org/about-the-data
NCES IPEDS: https://nces.ed.gov/ipeds/
EADA: https://ope.ed.gov/athletics/
NACDA Directors' Cup ledgers and ESPN historical performance endpoints: exact annual URLs and hashes in docs/sources.md and data/provenance.
BLS CPI-U series CUUR0000SA0: https://api.bls.gov/publicAPI/v2/timeseries/data/CUUR0000SA0?startyear=2010&endyear=2019&annualaverage=true
GAO context: https://www.gao.gov/products/gao-26-108640
Pope and Pope (2009): https://devingpope.com/assets/files/Website_SEJ%20Sports.pdf
McFarland, Groothuis and Guignet (2024): https://onlinelibrary.wiley.com/doi/full/10.1111/coep.12642
Anderson replication archive: https://doi.org/10.7910/DVN/ASXOBS; author manuscript: https://anderson.are.berkeley.edu/pdf/Anderson%202017.pdf
Our Python STE replication and partial IV comparison: ANDERSON_REPLICATION_REPORT.md. Main slide 5: results/presentation_charts/05_winning_donations.png.
Synthesis and framing: PROJECT_REPORT.md. Potential qualitative benefits were not directly measured or valued.
Our results and exact model IDs: FEASIBILITY_REPORT.md, CFO_RETURN_REPORT.md, results/feasibility_models.csv and results/return_models.csv.
Repository: https://github.com/harrydelashmit-dev/beyond-the-scoreboard


## Slide 8: Cost recovery by support dependence
ROBERT PHILYAW
SLIDE 8 OF 12 | 12:00–14:00 | 120 seconds
ROLE: Funding-model comparisons and support dollars

12:00–14:00 · Robert Philyaw

Chart: Recovery by earlier support dependence (../results/presentation_charts/08_support_groups.png).

Display: Lower support dependence 70¢ per $1; higher support dependence 30¢ per $1.

Higher dependence means institutional/government support plus student fees covered at least half of expenses in the observed 2010–2012 baseline. Groups were fixed before comparing later outcomes. This is a financial classification, not a judgment of educational quality.

We tested the difference directly; it survives related-test adjustment. It remains negative when each school is removed in turn and in a secondary model including budget size. Prior funding dependence appears more informative than size alone in this panel.

Budget-size and Power Five comparisons are less conclusive. Lower commercial recovery does not establish that participation or other mission benefits lack value.

Transition: “Even the way we describe support can change the financial story.”

KEY SOURCES
Knight-Newhouse financial methodology: https://knightnewhousedata.org/about-the-data
NCES IPEDS: https://nces.ed.gov/ipeds/
EADA: https://ope.ed.gov/athletics/
NACDA Directors' Cup ledgers and ESPN historical performance endpoints: exact annual URLs and hashes in docs/sources.md and data/provenance.
BLS CPI-U series CUUR0000SA0: https://api.bls.gov/publicAPI/v2/timeseries/data/CUUR0000SA0?startyear=2010&endyear=2019&annualaverage=true
GAO context: https://www.gao.gov/products/gao-26-108640
Pope and Pope (2009): https://devingpope.com/assets/files/Website_SEJ%20Sports.pdf
McFarland, Groothuis and Guignet (2024): https://onlinelibrary.wiley.com/doi/full/10.1111/coep.12642
Anderson replication archive: https://doi.org/10.7910/DVN/ASXOBS; author manuscript: https://anderson.are.berkeley.edu/pdf/Anderson%202017.pdf
Our Python STE replication and partial IV comparison: ANDERSON_REPLICATION_REPORT.md. Main slide 5: results/presentation_charts/05_winning_donations.png.
Synthesis and framing: PROJECT_REPORT.md. Potential qualitative benefits were not directly measured or valued.
Our results and exact model IDs: FEASIBILITY_REPORT.md, CFO_RETURN_REPORT.md, results/feasibility_models.csv and results/return_models.csv.
Repository: https://github.com/harrydelashmit-dev/beyond-the-scoreboard


## Slide 9: Support dollars versus percentages
ROBERT PHILYAW
SLIDE 9 OF 12 | 14:00–16:00 | 120 seconds
ROLE: Funding-model comparisons and support dollars

14:00–16:00 · Robert Philyaw

Chart: Support dollars and expense share (../results/presentation_charts/09_support_dollars_share.png).

Display: Real support dollars up 31.7%; support/expenses 31.2% → 28.0%; same 222 universities, 2010 versus 2019.

Explain that expenses grew enough for support to become a smaller slice even while the dollar commitment increased. Show the dollar chart first, then the percentage chart. Totals are about $2.34 billion → $3.09 billion, in 2019 dollars.

This is a matched descriptive comparison, not an estimated consequence of winning. Our six primary success/support tests also did not reliably establish that success reduces actual support or support shares after adjustment. Higher receipts alone do not establish self-sufficiency.

Handoff: “We also checked whether a breakthrough might be especially valuable for a smaller program.”

KEY SOURCES
Knight-Newhouse financial methodology: https://knightnewhousedata.org/about-the-data
NCES IPEDS: https://nces.ed.gov/ipeds/
EADA: https://ope.ed.gov/athletics/
NACDA Directors' Cup ledgers and ESPN historical performance endpoints: exact annual URLs and hashes in docs/sources.md and data/provenance.
BLS CPI-U series CUUR0000SA0: https://api.bls.gov/publicAPI/v2/timeseries/data/CUUR0000SA0?startyear=2010&endyear=2019&annualaverage=true
GAO context: https://www.gao.gov/products/gao-26-108640
Pope and Pope (2009): https://devingpope.com/assets/files/Website_SEJ%20Sports.pdf
McFarland, Groothuis and Guignet (2024): https://onlinelibrary.wiley.com/doi/full/10.1111/coep.12642
Anderson replication archive: https://doi.org/10.7910/DVN/ASXOBS; author manuscript: https://anderson.are.berkeley.edu/pdf/Anderson%202017.pdf
Our Python STE replication and partial IV comparison: ANDERSON_REPLICATION_REPORT.md. Main slide 5: results/presentation_charts/05_winning_donations.png.
Synthesis and framing: PROJECT_REPORT.md. Potential qualitative benefits were not directly measured or valued.
Our results and exact model IDs: FEASIBILITY_REPORT.md, CFO_RETURN_REPORT.md, results/feasibility_models.csv and results/return_models.csv.
Repository: https://github.com/harrydelashmit-dev/beyond-the-scoreboard


## Slide 10: Smaller-program breakthroughs
MORGAN BECKLER
SLIDE 10 OF 12 | 16:00–17:30 | 90 seconds
ROLE: Breakthroughs, limitations and CFO implications

16:00–17:30 · Morgan Beckler

Chart: Revenue and statistical football outperformance (../results/presentation_charts/10_breakthrough.png).

Ask: “Could a season stronger than recent history predicts create a larger benefit for a smaller program?”

- Our prediction uses earlier seasons only; we measure how far actual strength exceeds it.
- Smaller-budget FBS programs show a positive within-group revenue estimate.
- Their direct advantage over larger programs remains inconclusive. Different-looking dots alone do not establish different effects.
- Applications and enrollment show no consistent smaller-program advantage.

Smaller means a lower earlier athletics budget among FBS programs, not fewer students. The model does not measure fans’ expectations. An alternative AP-poll definition produces negative applications/enrollment differences; those sparse exploratory results are disclosed in backup.

Transition: “The evidence gives us useful financial patterns, along with clear limits.”

KEY SOURCES
Knight-Newhouse financial methodology: https://knightnewhousedata.org/about-the-data
NCES IPEDS: https://nces.ed.gov/ipeds/
EADA: https://ope.ed.gov/athletics/
NACDA Directors' Cup ledgers and ESPN historical performance endpoints: exact annual URLs and hashes in docs/sources.md and data/provenance.
BLS CPI-U series CUUR0000SA0: https://api.bls.gov/publicAPI/v2/timeseries/data/CUUR0000SA0?startyear=2010&endyear=2019&annualaverage=true
GAO context: https://www.gao.gov/products/gao-26-108640
Pope and Pope (2009): https://devingpope.com/assets/files/Website_SEJ%20Sports.pdf
McFarland, Groothuis and Guignet (2024): https://onlinelibrary.wiley.com/doi/full/10.1111/coep.12642
Anderson replication archive: https://doi.org/10.7910/DVN/ASXOBS; author manuscript: https://anderson.are.berkeley.edu/pdf/Anderson%202017.pdf
Our Python STE replication and partial IV comparison: ANDERSON_REPLICATION_REPORT.md. Main slide 5: results/presentation_charts/05_winning_donations.png.
Synthesis and framing: PROJECT_REPORT.md. Potential qualitative benefits were not directly measured or valued.
Our results and exact model IDs: FEASIBILITY_REPORT.md, CFO_RETURN_REPORT.md, results/feasibility_models.csv and results/return_models.csv.
Repository: https://github.com/harrydelashmit-dev/beyond-the-scoreboard


## Slide 11: Checks strengthen the analysis, with limits
MORGAN BECKLER
SLIDE 11 OF 12 | 17:30–18:30 | 60 seconds
ROLE: Breakthroughs, limitations and CFO implications

17:30–18:30 · Morgan Beckler

Display checks: Correct schools/years; independent recalculation; remove one school at a time.

Display limits: Observational budget relationships; historical and separate study samples; qualitative benefits and net university-wide returns unmeasured.

The project uses Python, with 37 local tests passing after the Anderson extension. Independent calculations reproduce main finance estimates, and all ten historical STE estimates match published rounding. The other IV matching translation remains partial. These checks establish implementation consistency, not causation. Our historical findings are not current NIL/revenue-sharing forecasts. Applications do not automatically create additional net tuition revenue. Visibility, pride, reputation, engagement and educational benefits were not directly measured or valued.

Keep formulas, p-values and parser details in backup.

KEY SOURCES
Knight-Newhouse financial methodology: https://knightnewhousedata.org/about-the-data
NCES IPEDS: https://nces.ed.gov/ipeds/
EADA: https://ope.ed.gov/athletics/
NACDA Directors' Cup ledgers and ESPN historical performance endpoints: exact annual URLs and hashes in docs/sources.md and data/provenance.
BLS CPI-U series CUUR0000SA0: https://api.bls.gov/publicAPI/v2/timeseries/data/CUUR0000SA0?startyear=2010&endyear=2019&annualaverage=true
GAO context: https://www.gao.gov/products/gao-26-108640
Pope and Pope (2009): https://devingpope.com/assets/files/Website_SEJ%20Sports.pdf
McFarland, Groothuis and Guignet (2024): https://onlinelibrary.wiley.com/doi/full/10.1111/coep.12642
Anderson replication archive: https://doi.org/10.7910/DVN/ASXOBS; author manuscript: https://anderson.are.berkeley.edu/pdf/Anderson%202017.pdf
Our Python STE replication and partial IV comparison: ANDERSON_REPLICATION_REPORT.md. Main slide 5: results/presentation_charts/05_winning_donations.png.
Synthesis and framing: PROJECT_REPORT.md. Potential qualitative benefits were not directly measured or valued.
Our results and exact model IDs: FEASIBILITY_REPORT.md, CFO_RETURN_REPORT.md, results/feasibility_models.csv and results/return_models.csv.
Repository: https://github.com/harrydelashmit-dev/beyond-the-scoreboard


## Slide 12: Winning has value. Spending still needs a financial case.
MORGAN BECKLER
SLIDE 12 OF 12 | 18:30–20:00 | 90 seconds
ROLE: Breakthroughs, limitations and CFO implications

18:30–20:00 · Morgan Beckler

Display:

1. Separate the benefits of winning from the payoff to spending.
2. Compare added receipts with the full added cost and funding commitment.
3. Use comparable funding models; track support dollars and shares.
4. State campus objectives explicitly; require evidence for recruitment income.

Close: “Winning can have value through attention, engagement and athletics receipts. We measured associations with ticket revenue and reproduced qualified evidence for athletic donations; we did not measure the value of campus pride or reputation. Those benefits do not establish that increasing athletics spending pays for itself. Our main budget comparisons show incomplete revenue recovery, especially among programs with high prior support dependence. A CFO should make the continuing funding commitment explicit and evaluate campus goals alongside financial evidence.”

Pause, thank the audience, and move to questions. Do not claim that all athletics spending is wasteful or all schools have identical goals.

KEY SOURCES
Knight-Newhouse financial methodology: https://knightnewhousedata.org/about-the-data
NCES IPEDS: https://nces.ed.gov/ipeds/
EADA: https://ope.ed.gov/athletics/
NACDA Directors' Cup ledgers and ESPN historical performance endpoints: exact annual URLs and hashes in docs/sources.md and data/provenance.
BLS CPI-U series CUUR0000SA0: https://api.bls.gov/publicAPI/v2/timeseries/data/CUUR0000SA0?startyear=2010&endyear=2019&annualaverage=true
GAO context: https://www.gao.gov/products/gao-26-108640
Pope and Pope (2009): https://devingpope.com/assets/files/Website_SEJ%20Sports.pdf
McFarland, Groothuis and Guignet (2024): https://onlinelibrary.wiley.com/doi/full/10.1111/coep.12642
Anderson replication archive: https://doi.org/10.7910/DVN/ASXOBS; author manuscript: https://anderson.are.berkeley.edu/pdf/Anderson%202017.pdf
Our Python STE replication and partial IV comparison: ANDERSON_REPLICATION_REPORT.md. Main slide 5: results/presentation_charts/05_winning_donations.png.
Synthesis and framing: PROJECT_REPORT.md. Potential qualitative benefits were not directly measured or valued.
Our results and exact model IDs: FEASIBILITY_REPORT.md, CFO_RETURN_REPORT.md, results/feasibility_models.csv and results/return_models.csv.
Repository: https://github.com/harrydelashmit-dev/beyond-the-scoreboard


## Slide 13: Sensitivity: full coverage depends on the comparison
BACKUP | HARRISON DELASHMIT
These specifications estimate different comparisons and use different samples. The school/year level model includes dollar-for-dollar coverage in its interval. Conference-year controls remove shared annual conference changes; school/year controls retain those differences. Annual changes remain below one with either time control. Do not imply that every possible model proves incomplete recovery. Original rows: R_annual (N=2002/G=227), R_three_year (N=1545/G=225), R_levels_year (N=2258/G=228). KEY SOURCES
Knight-Newhouse financial methodology: https://knightnewhousedata.org/about-the-data
NCES IPEDS: https://nces.ed.gov/ipeds/
EADA: https://ope.ed.gov/athletics/
NACDA Directors' Cup ledgers and ESPN historical performance endpoints: exact annual URLs and hashes in docs/sources.md and data/provenance.
BLS CPI-U series CUUR0000SA0: https://api.bls.gov/publicAPI/v2/timeseries/data/CUUR0000SA0?startyear=2010&endyear=2019&annualaverage=true
GAO context: https://www.gao.gov/products/gao-26-108640
Pope and Pope (2009): https://devingpope.com/assets/files/Website_SEJ%20Sports.pdf
McFarland, Groothuis and Guignet (2024): https://onlinelibrary.wiley.com/doi/full/10.1111/coep.12642
Anderson replication archive: https://doi.org/10.7910/DVN/ASXOBS; author manuscript: https://anderson.are.berkeley.edu/pdf/Anderson%202017.pdf
Our Python STE replication and partial IV comparison: ANDERSON_REPLICATION_REPORT.md. Main slide 5: results/presentation_charts/05_winning_donations.png.
Synthesis and framing: PROJECT_REPORT.md. Potential qualitative benefits were not directly measured or valued.
Our results and exact model IDs: FEASIBILITY_REPORT.md, CFO_RETURN_REPORT.md, results/feasibility_models.csv and results/return_models.csv.
Repository: https://github.com/harrydelashmit-dev/beyond-the-scoreboard


## Slide 14: Complete primary recruitment results
BACKUP | LUIS RAMOS
Show all six primary applications/enrollment comparisons. Pointwise 95% intervals are not multiplicity-adjusted confidence intervals. A raw football enrollment interval can exclude zero while its six-test family-adjusted p-value is inconclusive (approximately 0.267). None of the six primary demand tests survives family adjustment. Some Sweet16 annual-change specifications are positive and exploratory. We do not claim that the Flutie Effect has been disproved. Published samples, periods, success definitions and private/public composition differ. KEY SOURCES
Knight-Newhouse financial methodology: https://knightnewhousedata.org/about-the-data
NCES IPEDS: https://nces.ed.gov/ipeds/
EADA: https://ope.ed.gov/athletics/
NACDA Directors' Cup ledgers and ESPN historical performance endpoints: exact annual URLs and hashes in docs/sources.md and data/provenance.
BLS CPI-U series CUUR0000SA0: https://api.bls.gov/publicAPI/v2/timeseries/data/CUUR0000SA0?startyear=2010&endyear=2019&annualaverage=true
GAO context: https://www.gao.gov/products/gao-26-108640
Pope and Pope (2009): https://devingpope.com/assets/files/Website_SEJ%20Sports.pdf
McFarland, Groothuis and Guignet (2024): https://onlinelibrary.wiley.com/doi/full/10.1111/coep.12642
Anderson replication archive: https://doi.org/10.7910/DVN/ASXOBS; author manuscript: https://anderson.are.berkeley.edu/pdf/Anderson%202017.pdf
Our Python STE replication and partial IV comparison: ANDERSON_REPLICATION_REPORT.md. Main slide 5: results/presentation_charts/05_winning_donations.png.
Synthesis and framing: PROJECT_REPORT.md. Potential qualitative benefits were not directly measured or valued.
Our results and exact model IDs: FEASIBILITY_REPORT.md, CFO_RETURN_REPORT.md, results/feasibility_models.csv and results/return_models.csv.
Repository: https://github.com/harrydelashmit-dev/beyond-the-scoreboard


## Slide 15: Alternative breakthrough tests also give contrary results
BACKUP | MORGAN BECKLER
AP breakthrough means preseason-unranked and final AP top20. Smaller-budget versus larger-budget log-slope differences are -0.143 (raw p about 0.00166) for applications and -0.095 (raw p about 0.00103) for enrollment. These secondary comparisons are unadjusted, observational and based on sparse events. The sample has 651 cases/99 schools for applications and 681/100 for enrollment. School-omission checks retain negative interaction signs. This does not identify a causal decline in demand, and does not support the proposed smaller-program advantage. Models: U_ap_small_budget_fbs_applications and U_ap_small_budget_fbs_enrollment. KEY SOURCES
Knight-Newhouse financial methodology: https://knightnewhousedata.org/about-the-data
NCES IPEDS: https://nces.ed.gov/ipeds/
EADA: https://ope.ed.gov/athletics/
NACDA Directors' Cup ledgers and ESPN historical performance endpoints: exact annual URLs and hashes in docs/sources.md and data/provenance.
BLS CPI-U series CUUR0000SA0: https://api.bls.gov/publicAPI/v2/timeseries/data/CUUR0000SA0?startyear=2010&endyear=2019&annualaverage=true
GAO context: https://www.gao.gov/products/gao-26-108640
Pope and Pope (2009): https://devingpope.com/assets/files/Website_SEJ%20Sports.pdf
McFarland, Groothuis and Guignet (2024): https://onlinelibrary.wiley.com/doi/full/10.1111/coep.12642
Anderson replication archive: https://doi.org/10.7910/DVN/ASXOBS; author manuscript: https://anderson.are.berkeley.edu/pdf/Anderson%202017.pdf
Our Python STE replication and partial IV comparison: ANDERSON_REPLICATION_REPORT.md. Main slide 5: results/presentation_charts/05_winning_donations.png.
Synthesis and framing: PROJECT_REPORT.md. Potential qualitative benefits were not directly measured or valued.
Our results and exact model IDs: FEASIBILITY_REPORT.md, CFO_RETURN_REPORT.md, results/feasibility_models.csv and results/return_models.csv.
Repository: https://github.com/harrydelashmit-dev/beyond-the-scoreboard


## Slide 16: Sources and five-member speaking plan
BACKUP | ALL MEMBERS
KEY SOURCES
Knight-Newhouse financial methodology: https://knightnewhousedata.org/about-the-data
NCES IPEDS: https://nces.ed.gov/ipeds/
EADA: https://ope.ed.gov/athletics/
NACDA Directors' Cup ledgers and ESPN historical performance endpoints: exact annual URLs and hashes in docs/sources.md and data/provenance.
BLS CPI-U series CUUR0000SA0: https://api.bls.gov/publicAPI/v2/timeseries/data/CUUR0000SA0?startyear=2010&endyear=2019&annualaverage=true
GAO context: https://www.gao.gov/products/gao-26-108640
Pope and Pope (2009): https://devingpope.com/assets/files/Website_SEJ%20Sports.pdf
McFarland, Groothuis and Guignet (2024): https://onlinelibrary.wiley.com/doi/full/10.1111/coep.12642
Anderson replication archive: https://doi.org/10.7910/DVN/ASXOBS; author manuscript: https://anderson.are.berkeley.edu/pdf/Anderson%202017.pdf
Our Python STE replication and partial IV comparison: ANDERSON_REPLICATION_REPORT.md. Main slide 5: results/presentation_charts/05_winning_donations.png.
Synthesis and framing: PROJECT_REPORT.md. Potential qualitative benefits were not directly measured or valued.
Our results and exact model IDs: FEASIBILITY_REPORT.md, CFO_RETURN_REPORT.md, results/feasibility_models.csv and results/return_models.csv.
Repository: https://github.com/harrydelashmit-dev/beyond-the-scoreboard
