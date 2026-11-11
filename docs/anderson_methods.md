# Anderson replication: scope, validation and limitations

The all-ten-outcomes, two-estimator plan was committed at `dc01b53`, before local model estimation. Published targets were known when the plan was recorded. This is a retrospective replication exercise, not a preregistered new test. Main finance models and observations are unchanged.

## Source and reproducible download

- Michael L. Anderson, *The Benefits of College Athletic Success: An Application of the Propensity Score Design*, Review of Economics and Statistics 99(1), 2017, 119–134, [journal DOI](https://doi.org/10.1162/REST_a_00589).
- Benchmark: [author manuscript dated January 21, 2016](https://anderson.are.berkeley.edu/pdf/Anderson%202017.pdf), Table 3, PDF page 36. Distinguish this from the [June 2012 NBER working paper](https://www.nber.org/system/files/working_papers/w18196/w18196.pdf) and its Digest summary.
- Public [Dataverse archive DOI](https://doi.org/10.7910/DVN/ASXOBS), dataset 2769465, released version 1.1. Version metadata: `https://dataverse.harvard.edu/api/datasets/2769465/versions/1.1`. The archive lists CC0 1.0 and all seven files unrestricted.
- `python run_project.py --anderson --download --test` downloads six required/review files. The optional complete 48MB underlying-source archive is obtained with `python -m scoreboard.anderson --download --all-files`. All seven have already been obtained locally. Only Python code executes.
- `scoreboard/anderson_data.py` records exact original-format file IDs and published MD5 checksums. The ingested `covers_data.tab` is not byte-identical to the original `covers_data.dta`; use `?format=original` for file 2769470. Comparing the converted TAB bytes with the original checksum would incorrectly report corruption. Both original DTA datasets passed their published checksums. SHA256 is additionally recorded for modern local identity checks.
- Raw and analytic source files stay under ignored `data/raw/literature/anderson/`. `data/provenance/anderson_replication_downloads.json` records retrieval/checksums; the separate probe manifests preserve the acquisition history, including initially rejected converted-format validation.

The raw archive includes VSE, IPEDS, U.S. News and Covers material. We have not independently rebuilt those historical imports, nor asserted that archive metadata grants new rights to upstream commercial products. Use attribution and respect upstream terms if separately distributing them. No credentials or access request were needed for this public archive. Files are read as data or method documentation; no `.do` program executes.

## Preparation and alignment

`prepare` validates both original dataset hashes; removes the two explicit source errors; assigns each team's season week **before** postseason filters; retains weeks 1–12 outside December/January; requires at least eight nonmissing lines. The fifth-degree game-win propensity fit uses the entire eligible game archive, including games preceding the college-outcome panel. We condition later betting lines on cubics of earlier game outperformance and fit a second propensity for the author's expected-wins controls.

Team-season aggregates join to college data one-to-one on the original team name and year. Calendar lags are generated after that inner join, as in the author's preparation; school boundaries and calendar gaps cannot be crossed. For athletic lags, every intermediate year must exist. Source outcome lags use an exact positional/calendar check at the requested lag, matching the original code's slightly different rule. IPEDS reporting-date flags are corrected before the next-year SAT/applicant shift. The original SAT last-year retention rule is preserved; final applicant observations without an adjacent following year remain missing.

Stata's default float storage is emulated at generated intermediate steps. Polynomial columns are rescaled for numerical stability, without changing their span. No missing financial or game outcome is manufactured. A missing or nonexistent game contributes probability one to the season-weight product, as the source does; it is not added to season wins.

## STE (fully matched at published precision)

For college-outcome row year y, the dependent variable is Y[y] − Y[y−2], after the source reporting-period corrections. The exposure is wins[y−1] − wins[y−3], with wins[y−3], game counts[y−1] and [y−3], a constant and year indicators as controls. Weighted least squares uses the inverse probability of the observed prior season's win/loss sequence. The global 90th percentile is calculated before outcome-specific listwise deletion; observations with weights equal to or above that threshold are excluded. Standard errors cluster by school with rank-aware CR1 correction. Source STE coefficient tests use G degrees of freedom; our displayed 95% intervals retain that convention for comparison.

All ten Table 3 STE point estimates, standard errors and Ns agree with printed rounding. This is direct numerical validation of our translation using the author's analytic data; it is not an independent validation of source accuracy, model assumptions or causal identification. The CSV has outcome-specific N and school counts. Its intervals are coefficient intervals without simultaneous-coverage adjustment.

## IV matching (partial numerical replication)

For each week, support is bounded by observed treated/untreated propensities and 0.05/0.95. Eleven cutpoints at percentiles 10, 18, …, 90 form twelve strata. The original `centile` uses (n+1)p interpolation ([Stata 13/14 documentation](https://www.stata.com/manuals14/rcentile.pdf)); season trimming's `summarize, detail` uses the averaged inverse empirical distribution. We implement these separately.

Within strata, intercepts, win indicators and propensity slopes estimate remaining expected wins and outcome differences. First-stage win coefficients are smoothed over stratum order using a quadratic. Outcome two-year differences are residualized on year effects over the eligible sample **before** weekly support restrictions. An outcome/stratum must have at least two wins and two losses. Stratum estimates are frequency-weighted; week estimates are weighted by their respective regression Ns. Reported N is the maximum weekly N, not a pooled total. `schools` is the maximum weekly school count. Weekly diagnostics are provided for all 120 outcome-week combinations.

The delta-method IV standard error and weekly aggregation preserve the archived code's approximate diagonal variance calculation rather than silently replacing it with a modern bootstrap. Matching coefficient tests retain the source's hard-coded 105 degrees of freedom. The ordinary coefficient test differs from the sharp-null reduced-form test; both are labeled separately. No claim is made that we replicated inference for estimated propensities beyond what the archived code implements.

Every IV sample N matches Table 3, and point estimates are close, but some differ beyond printed rounding. The exact original hashes, reporting shifts, calendar lags, support bounds, percentile formulas and first-stage matrix ranks were checked. All twelve first-stage designs have rank 36, so omitted empty/collinear first-stage strata do not explain the discrepancy. The matching numerical difference remains unresolved. We do not adjust results to force agreement and do not call the IV magnitudes an exact replication. STE provides the numerically validated estimator for the presentation chart. All partial IV output is retained for review.

## Multiplicity and interpretation

The recorded plan uses Holm adjustment within each estimator's ten outcomes. We additionally show Holm across all twenty coefficient tests as a conservative sensitivity. This differs from the article's sharp-null p-values and all-table FDR q-values, which are retained only as **published** benchmarks. We have not reproduced the entire paper's placebo/robustness/FDR pipeline. All twenty estimates are disclosed regardless of significance.

Outcomes/periods differ from our later-period panel. Old monetary estimates remain in original source dollars; no claim is made they are comparable to a 2019-real budget coefficient. Restricted athletic gifts need not be available to fund general university operations. Applications, enrollment, tuition receipts and net student contribution are different quantities. No paper coefficient here supplies an athletics-spending treatment effect, a current-NIL forecast, or a university-wide investment return.

The earlier 52-school football pilot, our later-period FPI models and this archive are three distinct exercises. Bookmaker-based conditional unexpected game outcomes are different from AR(1) FPI forecast residuals. Positive benefits from football wins can coexist with the project's uncertain recruitment estimates and partial spending recovery. Competitive records on a fixed schedule are zero-sum; demand and all institutional benefits need not be.
