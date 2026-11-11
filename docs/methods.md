# Research design and interpretation

This file documents the **earlier EADA-only starter**. The preferred three-part Knight/ESPN analysis, its additional calendar/ID audits, hypotheses, sensitivities and financial qualifications are in [expanded_methods.md](expanded_methods.md) and [FEASIBILITY_REPORT.md](../FEASIBILITY_REPORT.md). The separate source populations and definitions must not be conflated.

## Population and calendar

Start with institutions classified as NCAA Division I in each annual EADA file (codes 1, 2, 3). Restrict primary models to public institutions using the contemporaneous IPEDS `CONTROL=1`. Preserve private DI institutions in the clean data for audit and possible extensions. Schools absent from the Cup table remain missing; they are not assigned zero points. This conditions primary results on observed Cup scorers and can introduce selection bias. Crosswalk coverage and exclusions must accompany findings.

`year=t` is the ending year of the athletic academic season: 2009–10 is 2010. EADA is matched by its explicitly labeled academic year, not simply the collection-date label. IPEDS admissions year is the incoming fall cohort. Before 2014, institutions could report the previous or current fall: `APPDATE=1` maps to collection year minus one, while `APPDATE=2` maps to collection year. These mappings are checked against every relevant original dictionary. Unknown reporting periods are excluded. If the same institution/cohort appears in two collections, the later collection takes priority; all duplicate candidates and their original values are retained for audit. Admissions from 2014 onward use the separate ADM current-fall component. The primary first-time enrollment outcome uses EF-A `EFALEVEL=4`, full- plus part-time first-time degree/certificate-seeking undergraduates; this has a consistent fall date and broader reporting coverage than admissions. Admissions-reported enrollment is retained separately for calculating the admission yield rate.

Total Cup performance is finalized after spring championships. Many fall-t application deadlines precede that final performance. The primary demand outcome therefore uses fall t+1; fall t and fall t+2 are sensitivity checks. No admissions outcomes after fall 2019 enter this historical analysis: 2019 success cannot have an observed t+1 outcome here. Future admissions/enrollment are joined directly from IPEDS, so they do not require the institution to remain in the next year's EADA financial sample. No forward-filling or row-shift across missing years.

Prior spending is from t−1 and performance is from t. Nominal spending is logged. A common annual inflation deflator subtracts a year-specific constant from log spending, absorbed exactly by year effects; coefficient estimates are invariant to that common deflator. Descriptive dollar levels remain nominal. School-specific costs and fiscal-year timing differences remain limitations.

## Primary tests

1. Cup points/100 at t versus log athletic expenses at t−1, with lagged enrollment and a lagged sport-participation-category proxy.
2. Log applications at fall t+1 versus Cup points/100 at t, with lagged total enrollment.
3. Log first-time enrollment at fall t+1 versus Cup points/100 at t, with lagged total enrollment.

All models absorb school and year indicators. Errors are clustered by school to allow serial dependence within schools. Confidence intervals use a Student t distribution with clusters minus one degrees of freedom. Sparse projections are tested against independent dummy-variable OLS on an unbalanced artificial test fixture. Covariance corrections include absorbed parameters. `results/models.csv` reports complete-case N, schools, year bounds, coefficients, intervals, p values, and within R-squared. Holm-adjusted p values accompany the three primary exposure tests. Secondary and sensitivity tests are exploratory and have no multiplicity adjustment.

Year effects absorb common time changes; school effects absorb stable differences. They do not resolve reverse causality, donor expectations, conference changes, coaching changes, marketing, academic reputation, local demographics, changing admissions policies, or spending responding to anticipated demand. No instrumental-variable, randomized, or defensible quasi-experimental design is claimed. A series of significant regressions would not establish mediation or the complete causal chain.

## Sensitivity and measurement

Compare contemporaneous versus prior spending, admissions lags, changes in performance and application growth, within-year Cup percentiles, a balanced Cup panel, trimming expenditure tails, pre-2018 results, and FBS/FCS/nonfootball subsamples. Current spending can be jointly determined with current performance. The participation-category count is a proxy rather than an official sponsored-team count: combined versus separate track and swimming reporting can differ. Missing participation entries are not filled into financial observations. The Cup's maximum and required-sport rules changed over the period; year effects do not remove differential school exposure to those changes. The pre-2018 restriction is therefore useful.

IPEDS reported and imputed values are preserved with X flags. A reported-only sensitivity must use the official per-year dictionaries rather than assume one flag code across every survey. Admissions cover the survey population and may be missing for open-admission institutions. University mergers, system-level finance reporting, changed applications platforms, and unusual reporting jumps require human review. No interpolation, winsorization, or fabricated observations. The 1st/99th percentile sensitivity removes observations and reports its new N.

Sport-specific Cup points measure postseason/poll/bowl success, not regular-season winning percentage, audience size, or FPI. Fall and winter tables can be provisional and can differ from final spring totals after discarded scores. Use a common observed sample for aggregate-versus-profile comparisons. The joint model holds aggregate Cup points and the other sport measure fixed. Since aggregate points include the high-profile sports, the football coefficient is a conditional composition association, not its total effect. Secondary sport spending models relate prior sport-specific expenses to the sport's Cup points. Neither a larger coefficient in different units nor a smaller p value establishes that one sport generates a greater causal return.

## Accounting

EADA `GRND_TOTAL_REVENUE` is reported athletics revenue, which can include allocated support. It is not a validated measure of externally generated revenue. Reported balance is only an accounting description, not athletics profit or university ROI. A secondary reported-revenue model does not validate the generated-revenue link.

Legacy residual arithmetic with mapped Knight-Newhouse fields:

`generated revenue = total revenue − institutional/government support − student fees`

`direct balance = generated revenue − total athletic expenses`

Support and fee fields must be separate and non-overlapping. For the actual registered export, total revenues already net transfers and expenses can include excess transfers. Thus the expanded study calls the residual a **net nonallocated-revenue proxy** and does not interpret the legacy `direct_balance` expression as cash profit or university ROI. Do not splice missing observations from EADA or automatically treat source disagreements as errors.

For a hypothetical incremental program, annual net contribution is incremental generated athletics revenue plus additional enrolled students times (net collected tuition minus variable service cost), minus incremental athletics cost. Applications are not students. Sticker tuition is not net collected tuition. Existing athletics donations cannot be counted twice; future enrollment attributable to athletics is not identified by this study. Capacity, aid, crowd-out, capital costs, financing, persistence, discount rates and opportunity costs would be needed for a full net-present-value analysis. Scenarios are break-even arithmetic, not empirical causal ROI estimates.

## Scope boundary

The earlier 52-school football pilot's original data/specification were not supplied. The expanded analysis independently estimates the relationships on a broader identified sample and reports different numbers, without claiming an exact replication. The 2022–2025 pandemic/NIL/realignment extension remains deferred.
