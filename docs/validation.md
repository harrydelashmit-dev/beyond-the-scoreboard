# Executed validation

Validation date: November 10, 2026. Python 3.12; exact directly used package versions are pinned in `requirements.txt`.

## Expanded feasibility update

- **27 local tests passed** after the expanded build and final portability check, including real registered-workbook checks. The public GitHub path skips the licensed-workbook test when the file is absent; the raw workbook is not redistributed.
- The expanded workflow executed **189 primary/sensitivity specifications**, plus four independent pilot specifications and **995 leave-one-school-out fits**. All planned primary models were estimable. The primary grid has 18 exposure tests; the other specifications remain explicitly exploratory.
- Every one of the 2,400 original financial rows retains its original values through the join. All source rows link to IPEDS; original source IDs and the stable program key are retained. Primary merger exclusions and duplicate Kennesaw fall-2015 candidates are audited.
- The expanded IPEDS-based Cup aliases recover the thirty Army/Army West Point, Navy and Air Force rows absent from the EADA-only crosswalk. The legacy starter retains its separate original sample.
- Source manifests, exact future-cohort lookups, football season-plus-one and conference fall-plus-one rules are verified. All eighteen model-specific primary sample sizes and the five identical-case basketball samples are checked.
- Independent full-rank dummy OLS reproduces the real-data Cup-spending, football-ticket and Sweet16-application coefficients, clustered standard errors and p-values. Synthetic tests independently cover disconnected conference/year effects, linear contrasts, FPI/AP wrong-season rejection, preseason zero-games validation, incomplete polls, missing/zero distinctions and financial/cohort arithmetic.
- Each year has a complete sixteen-school Sweet16 and sixty-four-school main-bracket ledger before negative membership indicators are derived. No missing Cup score is assigned zero. Historical FPI snapshots have the correct requested season and a verified postseason run date.
- Six new PNG/SVG figure pairs were generated in Python and visually inspected. Financial and student-demand figures distinguish unadjusted confidence intervals from Holm-adjusted inference. The two-year football-receipt estimate and sample-sensitive basketball trend result are disclosed.
- Source-cell, sample and independent-estimation results are recorded in `data/provenance/feasibility_validation.json` and `results/independent_fe_validation.csv`. Runtime, source/panel/result/plan hashes and code hashes are in `feasibility_analysis_manifest.json`.

The full private-data build and source checks establish implementation/source consistency, not institutional reporting accuracy or causal identification. They do not reproduce the original missing 52-school pilot or identify cash ROI. Report-only reproduction is separate from re-estimation; it uses versioned aggregate results.

```text
python run_project.py --expanded --download --test
python -m scoreboard.validate_feasibility
python run_project.py --expanded --report-only --test
```

## Earlier public-source build

- All 120 configured official files/codebooks downloaded successfully. SHA-256 checks verified every cached source before the final build.
- The end-to-end Python workflow rebuilt the processed school-year panel from original cached sources, estimated 22 models, wrote six PNG/SVG chart pairs, generated findings and the static report, and ran the test suite.
- **19 tests passed after the Knight acquisition update** (14 at the initial end-to-end build). Tests cover exact-calendar joins across gaps, admissions lookup independent of future athletics reporting, pre-2014 admissions reporting-period alignment, duplicate keys, nonpositive logs, generated revenue excluding support exactly once, marginal contribution arithmetic, independent fixed-effects/clustered-OLS equivalence, source metadata coverage, actual public-data uniqueness, institutional separation, source-known Cup totals, football/basketball champions, and Kennesaw's changing UNITID. Added acquisition tests preserve missing values versus zero and cents, reject malformed tables and conflicting batch overlaps, reject HTML masquerading as Excel, and check the real registered workbook against the independent 2019 report. The private-workbook test skips in clones without the licensed source file.
- Six chart PNGs were visually inspected; labels, uncertainty intervals, source notes, sample sizes and hypothetical scenario assumptions were reviewed. Charts explicitly distinguish pooled descriptive patterns from within-university models.
- Final admissions timing uses the institution's actual APPDATE reporting period before 2014; first-time enrollment uses EF-A level 4. Missing or unknown periods are not inferred. Cohort duplicate candidates and the latest-collection selection are documented in provenance.
- Original source quirks were preserved or handled explicitly: varying PDF layouts and header repetition, a published 2014 rank-row ordering issue, trailing CSV delimiters, and campus/name ambiguity.

Reproduction commands:

```text
python run_project.py --download --test
python run_project.py --from-processed --test
```

The first command requires original public data downloads. The second uses the versioned processed public datasets and is used by the GitHub workflow. Network availability, future upstream revisions and package availability are outside this recorded local run. A fresh dependency installation in GitHub is reported separately by its workflow status.

Knight acquisition validation: the real workbook has 2,400 exported rows; 2,289 report total revenues and expenses. All 1,920 displayed 2019 cells match the workbook. No missing financial values were invented. See `data/provenance/knight_acquisition.json` and `knight_coverage.csv`.

Remaining limits/actions: the financial measure is a qualified transfer-netted proxy; the original 52-school data/specification are missing; institutional interpretation of large reporting changes and the final five-person review remain group work. Final slides and instructor approval are not complete. The expanded report contains the completed feasibility conclusions and does not infer causal return.
