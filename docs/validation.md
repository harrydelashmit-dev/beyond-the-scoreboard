# Executed validation

Validation date: November 10, 2026. Python 3.12; exact directly used package versions are pinned in `requirements.txt`.

- All 120 configured official files/codebooks downloaded successfully. SHA-256 checks verified every cached source before the final build.
- The end-to-end Python workflow rebuilt the processed school-year panel from original cached sources, estimated 22 models, wrote six PNG/SVG chart pairs, generated findings and the static report, and ran the test suite.
- **14 tests passed.** Tests cover exact-calendar joins across gaps, admissions lookup independent of future athletics reporting, pre-2014 admissions reporting-period alignment, duplicate keys, nonpositive logs, generated revenue excluding support exactly once, marginal contribution arithmetic, independent fixed-effects/clustered-OLS equivalence, source metadata coverage, actual public-data uniqueness, institutional separation, source-known Cup totals, football/basketball champions, and Kennesaw's changing UNITID.
- Six chart PNGs were visually inspected; labels, uncertainty intervals, source notes, sample sizes and hypothetical scenario assumptions were reviewed. Charts explicitly distinguish pooled descriptive patterns from within-university models.
- Final admissions timing uses the institution's actual APPDATE reporting period before 2014; first-time enrollment uses EF-A level 4. Missing or unknown periods are not inferred. Cohort duplicate candidates and the latest-collection selection are documented in provenance.
- Original source quirks were preserved or handled explicitly: varying PDF layouts and header repetition, a published 2014 rank-row ordering issue, trailing CSV delimiters, and campus/name ambiguity.

Reproduction commands:

```text
python run_project.py --download --test
python run_project.py --from-processed --test
```

The first command requires original public data downloads. The second uses the versioned processed public datasets and is used by the GitHub workflow. Network availability, future upstream revisions and package availability are outside this recorded local run. A fresh dependency installation in GitHub is reported separately by its workflow status.

Pending validation: legitimate Knight-Newhouse export and source-definition reconciliation; final five-person review; final slides and instructor approval. The earlier football/FPI pilot was not validated by this repository.
