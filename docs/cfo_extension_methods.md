# CFO extension: cost recovery, school differences and financial support

The user selected directions 1 (cost recovery), 2 (school types), 6 (self-support) and 3 (unexpected success, especially smaller programs). All new analytics, charts, validations and tests are Python. The prior feasibility results remain separate. This extension has sufficient accounting/presentation value; the other proposed directions were not pursued to search for significance.

## Recorded scope and timing

`config/return_plan.json` was committed at `a45a7a6` before extension estimation. The previously completed feasibility results were known. This is exploratory development of a course project, not an independently preregistered confirmation. Fourteen primary null tests are retained in families of 2/3/6/3. After the first extension estimates, three secondary diagnostics were added and disclosed: joint budget/support interactions; shared-case dollar outperformance responses; and influence checks for opposite-signed AP-event results.

Money is in millions of 2019 CPI-U dollars. Published annual M13 values from the official BLS public API (`CUUR0000SA0`, all items, all urban consumers, not seasonally adjusted) are validated against all twelve monthly observations. Calendar-year CPI approximates fiscal-year inflation. It is not an athletics-specific cost index. All original nominal data remain unchanged. An initial FRED CSV probe failed; the official BLS response supplies the actual observations. Provenance includes retrieval time, URL, original-response hash and aggregation rules.

Financial year t is the academic/fiscal ending year. Football season t−1 aligns with this year. Football demand uses fall t; financial responses use fiscal t+1. No outcome after 2019 is fabricated. Exact calendar joins, not positional shifts, provide prior and future observations. Merger and Division I eligibility rules are inherited from the audited feasibility panel.

## Accounting variables

- E: exported total expenses.
- R: exported total revenues less institutional/government support and student fees.
- S: institutional/government support plus student fees.
- Gap proxy: E−R = S + E−total revenues.

R is a **net nonallocated-revenue proxy**, not gross external receipts or verified cash profit. The export nets transfers to the institution; expense totals may contain excess transfers. Donations may be restricted or in-kind. Reported debt/operating/capital distinctions and indirect institutional costs are incomplete in the eight-field export. Consequently the gap proxy and actual allocated support are measured separately. Revenue plus S equaling exported total revenue is an accounting identity, not evidence of a behavioral financing response.

## Cost recovery

Annual primary model:

`change_R_t = beta * change_E_t + gamma * change_log_enrollment_t + conference_year_indicators + error`.

Changes include decreases and zero changes. Source prior-year values are looked up in the full original panel, including any source reporting before a current program's DI eligibility. Nominal sensitivity uses the same lookup. Its sample matches the real-dollar annual specification. A conference-year cell with only one complete row is removed; a school with a single valid change is retained as an independent difference cluster. There is no school dummy in this primary difference regression because the time-invariant school intercept has already been removed. Adding school effects to changes is a sensitivity that controls school-specific average growth. Other sensitivities compare level models with school/year or school/conference-year effects.

The financial null is **beta = 1**, tested two-sided, rather than beta = 0. All coefficients also retain their conventional zero-null p-values in `return_models.csv`. Primary inference uses the `test_p` column; `primary_null` identifies the tested benchmark. A positive, significant zero-null coefficient can still imply incomplete cost recovery.

Three-year primary model at anchor t:

`sum(R_t, R_(t+1), R_(t+2)) - 3*R_(t-1)`

is regressed on the same accumulated-flow expression for E, with `log(enrollment_(t+2)) - log(enrollment_(t-1))` and conference-year indicators. All four years must be present in the eligible panel. Missing components propagate; no sum silently treats missing as zero. A 3% real-discount sensitivity discounts both revenue and expense increments. These are overlapping budget-flow comparisons, **not a causal return on a one-time spending shock**, and not terminal-stock changes. School clustering accounts for within-program dependence but cannot remove endogeneity.

Additional checks include balanced ten-year financial reporters, fixed 1st/99th percentile exclusion of observed expense/revenue changes, removal of 2015–2017, positive increases only, nominal dollars, and joint current/prior spending changes. Trimming is a sensitivity, not a claim that genuine large changes are errors. All specified fits are reported, including the school/year level specification whose interval includes dollar-for-dollar coverage.

## School types and breakthrough comparisons

Baseline budget/support/enrollment groups require all three observed years 2010–2012 and precede evaluation from 2013. Budget cutoffs are medians across eligible DI programs or, separately, established FBS programs. These are athletics-budget definitions; enrollment size is a different secondary measure. High support means baseline S/E at least 50%, using the ratio of matched sums. The Power Five comparison freezes 2014 football conference membership and evaluates 2015–2019, excluding independents.

Cost-recovery interactions include the fixed baseline-group indicator to allow different mean growth. A direct interaction tests differences in slopes. Group-specific slopes and their confidence intervals are computed using the full coefficient covariance. Separate subgroup p-values are never used as evidence that groups differ. Baseline characteristics overlap, so a secondary joint size/support interaction is retained. It is observational and does not identify the effect of changing a school's group.

The main football outperformance measure is the existing expanding AR(1) forecast residual, trained on past seasons only. Historical FPI series collected now may have been revised. This is **statistical outperformance**, not measured market/fan/applicant expectations or an exogenous shock. Outcome models include prior FPI, prior enrollment, school and conference-year effects; inference is conditional on the estimated forecasting rule. Three primary interactions compare smaller versus larger baseline FBS budgets for revenue, applications and first-time enrollment. Direct interaction and group-specific effects are both reported. A percentage revenue response does not establish a dollar return.

Secondary definitions include baseline enrollment, historical 2005–2008 FPI prominence, non-Power membership and preseason-unranked/final-top20 AP events. Event counts and event-school counts are published for the actual regression sample. Sparse negative AP interactions are disclosed, with one-school omission checks; they are not treated as causal evidence or a confirmed headline.

## Support, descriptions and uncertainty

Six primary success/support comparisons pair Cup/100, FPI/10 and Sweet16 with actual next-year S dollars and S/E percentage points. They use school/conference-year effects and prior log enrollment. Student-fee dollars per enrolled student, gap responses and year-effect alternatives are secondary. Shared-case expense/revenue/gap/support models verify coefficient identities. A declining support fraction is distinct from declining actual support dollars.

Descriptive coverage selects observed positive expense changes and reports the fraction with change R at least change E. Ratios are **ratios of sums**, not means of unstable individual ratios. The associated 1,000-replicate school bootstrap describes this selected positive-change sample; it is not a probability of investment success. Model slopes and descriptive coverage ratios are explicitly different estimates. Matched endpoint bridges require all four reported financial measures at both endpoints. Unmatched annual totals do not supply the endpoint growth percentages.

One additional descriptive risk check compares the variability of annual log revenue growth for programs with at least five observed changes after baseline, grouped by historical support dependence. That cross-program comparison does not control all institutional differences; lower starting revenue can itself make proportional growth more volatile. It has no causal insurance interpretation.

School-clustered covariance uses small-sample correction and t reference with G−1 degrees of freedom. Level-model absorbed rank and connected components follow the validated fixed-effects implementation. Difference models use a full-rank explicit time-indicator design. Pointwise 95% confidence intervals and raw p-values remain available. Holm corrections apply within each primary family and across all fourteen tests. These do not retroactively combine the earlier eighteen feasibility tests or make the unadjusted secondary family confirmatory. Every non-estimable status must remain visible.

## Verification and reproducibility

`python run_project.py --returns --download --test` uses the already audited local feasibility panel, retrieves/validates CPI, rebuilds the private CFO panel, executes all 95 primary/secondary specifications and 1,167 school-omission fits, records hashes/runtime versions, performs independent validation, and regenerates five scientific chart pairs. The earlier expanded build must be completed first if the private panel is absent. Without `--download`, the versioned CPI extract suffices; original private money is still required.

`python -m scoreboard.validate_returns` checks preservation of all eight financial source columns, accounting identities, identical bridge cases and independent full-rank dummy OLS agreement on coefficients, school-clustered standard errors and p-values for five real-data models. Synthetic tests cover contrasts, missing-year propagation, complete CPI coverage, past-only baseline classifications and the dollar-for-dollar null. The aggregate coefficient hash must match its execution and validation records. Binary private-source hashes are byte-exact; versioned text hashes normalize CRLF/LF for portability.

`python run_project.py --returns --report-only --test` reconstructs reports and figures from saved aggregate outputs without the registered workbook. It does not claim to re-estimate the private financial models. GitHub runs the public-source build/tests and both aggregate report builds. Individual Knight money, exact cases and finance-based school assignments remain ignored. No registration information or credentials are published.

More historical pre-NIL years could improve lag coverage and precision; additional transfers/media/operating/capital fields may improve measurement more directly. Neither additional N nor additional fields automatically solves reverse causality. COVID and later NIL/revenue-sharing regimes require separate analysis. No extra user access is necessary for the completed 2010–2019 extension.
