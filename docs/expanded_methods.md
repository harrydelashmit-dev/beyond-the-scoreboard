# Expanded feasibility methods and reproduction

The CFO question is whether returns associated with athletics depend on the type of success. This is an observational, public-university study, with qualified accounting proxies and hypothetical financial scenarios. It does not require every link in the proposed pathway to be significant.

## Source population and accounting

The registered Knight-Newhouse workbook lists 240 institutions in each of ten years. Its 2,400 rows include missing reports and pre-Division-I periods; there are 2,289 total-revenue/expense observations. Historical subdivision eligibility, contemporary IPEDS public status and primary merger exclusions are applied before outcome-specific complete-case selection. All original rows and values are retained locally.

Native expenses, football spending, coaching compensation, all-sports tickets and athletics donor contributions are distinct fields. `net_nonallocated_revenue_proxy = total_revenue - institution_government_support - student_fees`. The export already nets transfers to the institution, and expenses can include excess transfers. This residual is not gross generated receipts, operating cash profit or causal university ROI. No EADA financial values are substituted for missing Knight values. EADA supplies the basketball spending and participation-category controls and an aggregate source reconciliation.

## IDs, membership and calendars

- `unitid` in the private analytical panel is a stable athletics-program key. Source Knight, EADA and IPEDS IDs remain separate columns. Former Kennesaw 140164 maps to program 486840. In fall 2015 its inactive former IPEDS entity has no enrollment; the active consolidated entity is retained and both candidates are audited.
- Kennesaw, UTRGV and Purdue Fort Wayne are excluded throughout the primary window because their institutional scope changes can affect application/enrollment comparisons. Sensitivities include them; no pre/post merger counts are silently spliced.
- NCAA subdivision from the historical financial source identifies Division I membership. EADA classification/coverage differences do not erase valid Knight or IPEDS records, though missing EADA controls reduce particular models.
- Knight/Cup ending year t refers to the academic/fiscal year ending t. ESPN football season s maps to t=s+1. Every FPI response must have the requested season and a January/February postseason run date, not a current or in-season rating.
- Ending-year labels are aligned; individual institutions' precise fiscal closing dates may still differ and are not inferred from the labels. Verified IPEDS aliases recover Army/Army West Point, Navy and Air Force Cup records outside the EADA-only match.
- IPEDS IC conference collection in fall t−1 describes the season ending t. `CONFNO2` is verified as basketball conference in every original dictionary. Nebraska's 2011 move appears in IC2011 and fiscal 2012, confirming the shift. Conference-by-year effects include both general year conditions and annual conference conditions.
- Football student demand uses fall t after season t−1; Cup/Sweet16 uses fall t+1. Financial outcomes use fiscal t+1. Other lags are reported as sensitivity checks. Exact-year joins never step across gaps or require future EADA reporting. Source outcomes stop at 2019.
- Earlier IPEDS IC admissions cohorts follow `APPDATE`, with later collections selected among duplicates and candidates preserved. EF-A level 4 measures first-time degree/certificate-seeking undergraduates. Reported-only sensitivities verify R=Reported in every annual source dictionary.

## Success and visibility

Aggregate outcomes are Cup points, published rank and score percentile. Missing Cup participation/scores remain missing, so Cup models condition on observed scorers. FPI is a continuous strength index, not a national-visibility measure or observed win percentage. `numwins`/`numlosses` provide the separate completed-season winning percentage; projected wins are not used as actual wins.

The winter NACDA files contain complete matched ledgers of sixteen Sweet16 schools and sixty-four main-bracket schools each year. Those exhaustive ledgers permit derived nonmembership indicators for known DI programs, including programs absent from the winter all-sports table. No numeric Cup score is imputed. Main64 excludes opening-round losers. The original 2015 Final Four score of 85 points is retained; the Sweet16 threshold is unaffected.

AP final/opening polls use year-specific core resources. Final polls require the final-occurrence marker. Opening polls are in regular-season week 1, and all ranked teams must have zero wins/losses. A generic ESPN rankings query ignored historical parameters and returned 2026; it was rejected. The nonexistent preseason-season-type probes were retained as failed provenance and replaced with verified opening polls. Final AP top20 and opening-unranked-to-final-top20 are separate visibility measures.

Historical prominence uses mean FPI in 2005–2008, requiring all four seasons. Outperformance is an expanding AR(1) forecast residual using earlier seasons only. Historical ratings were retrieved in 2026 and may be retrospectively revised; this is not a real-time forecast vintage or a direct measure of student expectations.

## Estimation and uncertainty

The expanded primary grid has three spending-success, nine success-finance and six student-demand exposure tests. It was recorded before new Knight estimation; the earlier EADA results were already known. It is an internal plan, not an external preregistration. Additional secondary diagnostics are recorded and fully reported; the primary grid was not replaced after seeing results.

Models absorb school and basketball-conference-by-year effects. Prior log total enrollment is included; spending-success models add the prior EADA participation-category count, a proxy rather than an exact sponsored-team count. A zero category count is retained in source data but treated as unusable for this DI control. Positive logs exclude observed zeros rather than treating them as missing money; financial IHS sensitivities include genuine zeros on a disclosed million-dollar scale. Sweet16 probability uses a linear probability model.

Sparse projection implements the same least-squares coefficients as full-rank dummy OLS. The bipartite incidence graph determines the absorbed rank, including disconnected conference-school components. Covariance uses school-cluster score sums, the finite-sample correction including absorbed rank, and t intervals with clusters minus one degrees of freedom. Absorbed singleton cells are recursively removed. Separate school-trend and first-difference estimators are labeled explicitly.

All primary intervals are pointwise 95%. Holm p-values adjust within the three primary families; all-18 adjustment is also supplied. Secondary p-values are unadjusted exploratory evidence. Positive donor/Sweet16 pointwise results that fail the relevant correction are not relabeled primary discoveries. Different units, samples or p-values do not establish a statistically larger effect or a better return per dollar for one sport.

The common-FBS comparisons use exactly the same school-years/outcome fall for each exposure and their joint model. Aggregate Cup contains the high-profile sports, so joint effects are conditional composition comparisons. A separate basketball diagnostic fixes the same 1,393 cases across level, annual-change, conference/year, year-only and trend specifications. Differences are transformed before restricting cases, preserving valid calendar differences. Rare-event support and switcher counts identify subgroup coefficients driven by very few success programs.

## Validation and limitations

`python -m scoreboard.validate_feasibility` checks all financial-cell preservation, IPEDS joins, football/conference calendars, exact future demand lookup, all 18 primary sample sizes and three independent real-data full-rank dummy-OLS comparisons. Synthetic tests separately check the covariance implementation, contrasts, wrong-season responses, incomplete AP ledgers, missing/zero distinctions, batch conflicts, cohort retention and capacity, NPV arithmetic and saved multiple-testing/interval calculations.

`results/feasibility_sample_flow.csv` gives sequential, mutually exclusive missingness/absorption exclusions for each model; private sample files hold the exact rows/values. Financial group-level descriptions and EADA reconciliation are published; school-level licensed observations remain ignored. Large source changes are review flags, not automatically errors or deleted outliers. A genuine Flutie jump could itself be large.

The design cannot eliminate time-varying marketing, application-platform/policy changes, capacity or price changes, coaching changes, reverse causality or reporting differences. Open-admission and private-school generalizability is limited. Statistical precision does not address those biases. The original 52-school pilot's exact sample/specification was not supplied; independent results are presented with their own observations, timing and specification.

## Reproduction

Build the original public-source extracts using `python run_project.py --download --test`. Stage the legitimate registered workbook using `scoreboard.knight_export`, then run `python run_project.py --expanded --download --test`. The expanded command uses the versioned/rebuilt federal/Cup extracts and raw public performance/conference files. A normal later rerun can omit `--download`; source hashes and selected vintages are recorded. Changing a parser requires rebuilding its corresponding cache.

`python run_project.py --expanded --report-only` recreates figures, scenarios and narrative from saved aggregate results without re-estimating financial models or requiring private inputs. GitHub checks cover that public reproduction path; full licensed-source estimation and source-cell verification were run locally. Expected raw and private exclusions are enforced by `.gitignore`.
