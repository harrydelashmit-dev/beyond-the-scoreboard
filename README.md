# Beyond the Scoreboard: Does University Investment in Athletics Pay Off?

**AC 547 · Track A · Python-only analytics · 2010–2019 historical panel**

A reproducible management-accounting/economics study asking: **Does the financial return associated with athletic investment depend on the type of competitive success?** Spending → success → receipts/student demand → worthwhile return is a proposed pathway, not a proven causal chain.

**All project cleaning, joins, calculations, regressions, tests, chart generation, and automated download scripts are written in Python.** The registered Knight-Newhouse workbook is obtained through its website and processed in Python. CSV/JSON store data and configuration; Markdown documents the work; HTML/SVG/PNG are generated static outputs. There is no JavaScript, R, Excel formula logic, or non-Python analytics layer in the repository.

**Start with [the expanded feasibility report](FEASIBILITY_REPORT.md)** or its [formatted HTML version](results/feasibility_report.html). It contains all 18 primary tests, sample sizes, coefficients, confidence intervals and adjusted p-values, plus the complete sensitivity results. Football FPI is associated with next-year ticket receipts (+6.41% per 10 FPI points; 95% interval +3.99% to +8.89%; 817 observations, 109 schools). Spending-success and primary student-demand tests remain uncertain; basketball applications show an exploratory signal in annual-change models. These results do not identify causal ROI.

**New CFO extension: [cost recovery and who benefits](CFO_RETURN_REPORT.md)** ([formatted HTML](results/return_report.html)). Annual changes imply approximately **$0.64 additional nonallocated-revenue proxy per $1 of spending** (95% CI $0.50–$0.79; 2,002 school-years, 227 schools), with a three-year cumulative slope of $0.68. Programs with high prior support dependence have materially weaker recovery ($0.30 versus $0.70; direct difference survives correction). None of the six primary support-response tests establishes that success reduces support; smaller-program breakthrough advantages remain unconfirmed. For 222 matched programs, real support dollars rose 31.7% even while support/expenses fell from 31.2% to 28.0%. These are observational accounting relationships, not causal investment returns. All 14 primary tests, 95 specifications, contrary sensitivity results and sparse negative AP-event comparisons are retained.

The earlier 52-school pilot was independently checked on a broader sample; its directions are supported, but its exact numerical results are **not reproduced** without the original membership/specification. [FINDINGS.md](FINDINGS.md) preserves the earlier EADA-only starter separately.

**Public-study replication:** [Anderson verification and Python results](ANDERSON_REPLICATION_REPORT.md) ([HTML](results/anderson_report.html)) adds an earlier-period check using the public research archive. All ten Table 3 STE estimates, standard errors and sample sizes match the published rounding. Extra football wins predict more athletic alumni donations in that model; applications remain uncertain. The separate IV matching translation is close but not exact, with all discrepancies disclosed. These are benefits of winning under the study's assumptions, not returns from additional spending. Run `python run_project.py --anderson --download --test` to acquire original data and re-estimate, or `python run_project.py --anderson --report-only` to rebuild from aggregates. [Methods and limits](docs/anderson_methods.md) explain source access, period differences and multiplicity. No Stata software is required.

**Presentation:** the [20-minute, twelve-slide outline](docs/20_minute_outline.md) has been turned into a saved presentation with six scientific charts, named notes for Evan West, Luis Ramos, Harrison Delashmit, Robert Philyaw and Morgan Beckler, plus four hidden backups. Harrison presents the core financial findings. See [delivery and PowerPoint export](docs/presentation_delivery.md) and the [speaker notes](docs/speaker_notes.md). Six simpler [PNG/SVG chart pairs](results/presentation_charts) come from existing aggregate results via `python -m scoreboard.presentation_charts`. `python -m scoreboard.presentation_notes` rebuilds the plain content/configuration and notes without financial re-estimation. Rehearsal, consultation and individual group contributions remain group work.

## Run it

Use Python 3.12. From the repository root:

```text
python -m venv .venv
```

For the CFO extension, after building the audited private expanded panel as below, run:

```text
python run_project.py --returns --download --test
```

This acquires the official BLS CPI-U series, estimates all recorded primary and sensitivity models, performs school-omission checks and independent numerical/source validation, then builds the report and five chart pairs. The private Knight observations are required for estimation. For an offline reproduction of the report and figures from saved aggregate results only:

```text
python run_project.py --returns --report-only --test
```

The [CFO extension methods](docs/cfo_extension_methods.md) distinguish annual changes, cumulative flows, accounting gaps, actual support, group comparisons and their limitations. The plan was committed before extension estimation at `a45a7a6`; earlier feasibility findings were already known.

Activate `.venv` using your operating system's normal activation method, then:

```text
python -m pip install -r requirements.txt
python run_project.py --download --test
```

This first command downloads and rebuilds the original 120-file EADA/IPEDS/NACDA source panel. EADA Excel parsing can be slow; intermediate caches accelerate subsequent runs. Source files are hashed and retained locally under ignored `data/raw/`. The Git repository includes compact processed public data so an offline rerun of that public-source starter is also possible:

```text
python run_project.py --from-processed --test
```

To rebuild cleaned data from an existing raw cache, use `python run_project.py --test`. Remove only the generated `data/interim/cup_*.csv` or `eada_*.csv` caches after changing their parser logic, or use a fresh clone/cache. Do not refresh raw files casually when trying to reproduce the saved data vintage.

### Expanded Knight-Newhouse / ESPN study

Obtain the registered 2010–2019 workbook using [the documented report/export procedure](docs/sources.md). Save it under ignored `data/private/knight_reports/`, then stage it in Python:

```text
python -m scoreboard.knight_export --input data/private/knight_reports/knight_2010_2019_30e5ca83.xlsx --source-url https://knightnewhousedata.org/reports/30e5ca83
python run_project.py --expanded --download --test
python -m scoreboard.validate_feasibility
```

The expanded workflow uses the already built/versioned federal/Cup extracts, downloads or verifies 71 configured performance/conference files (including overlap with existing files), rebuilds the audited private panel, estimates the primary and sensitivity models, checks influence, and writes the report/figures/scenarios. ESPN FPI, win records and opening/final AP polls are obtained through public endpoints; no API key is used. For a full fresh raw-source rebuild, run the original `--download --test` command first. A registered Knight workbook is necessary to re-estimate the financial models; the raw data and all school-level financial joins/samples are excluded from Git.

Anyone with the repository can regenerate the expanded report and figures from **saved aggregate coefficients**, without the registered workbook or network access:

```text
python run_project.py --expanded --report-only --test
```

That command does not re-estimate licensed-source regressions. [Expanded methods](docs/expanded_methods.md) distinguish complete estimation from report-only reproduction.

## Results and design

- Three separate analyses: spending/success; success/athletics receipts; success/applications and first-time enrollment.
- 18 primary tests with school and conference-by-year controls, school-clustered intervals, exact-calendar lags and Holm adjustment within families and across all 18.
- Fully reported sensitivity grid: school/year controls, first differences, school trends, common samples, visibility thresholds, rare-event support, conference groups, past-only prominence/outperformance, and leave-one-school-out checks.
- Native Knight financial measures, separately qualified revenue-after-support proxy, and EADA reconciliation. No splicing missing Knight observations from EADA.
- CFO break-even and cohort/retention/capacity/NPV scenarios, with hypothetical benefits clearly separated from causal estimates.

The main estimates are observational associations. Neither significant coefficients nor an appealing diagram establish a causal chain or university ROI. Missing observations are never invented or assigned zero to make a panel look complete.

## Repository map

| Path | Purpose |
|---|---|
| `run_project.py` | Python workflow entry point |
| `scoreboard/download.py` | Official downloads, caching, hash/signature validation |
| `scoreboard/clean.py` | EADA/IPEDS readers, Cup PDF parsing, school aliases and exact-year joins |
| `scoreboard/models.py` | Fixed-effects estimation, clustered inference, sensitivity tables |
| `scoreboard/knight.py` | Validated import of a legitimately obtained registered export |
| `scoreboard/knight_export.py` | Stage the actual 2010–2019 registered workbook, validate identifiers/coverage, check displayed values |
| `scoreboard/knight_reports.py` | Parse displayed report captures in Python; distinguish missing values from zeros |
| `scoreboard/performance.py` | Verified historical ESPN FPI, wins/AP polls and exhaustive NACDA basketball events |
| `scoreboard/feasibility_data.py` | Historical IDs, fiscal/football/fall calendars, conferences, support proxies, private audited panel |
| `scoreboard/feasibility.py` | Expanded model grid, pilot audit, common cases, rare events and influence checks |
| `scoreboard/feasibility_report.py` | Expanded report, aggregate tables and six new figure pairs |
| `scoreboard/validate_feasibility.py` | Source-cell/calendar checks and independent real-data dummy-OLS validation |
| `scoreboard/cfo_scenarios.py` | Explicit student cohorts, retention, capacity, capital and discounted cash flows |
| `scoreboard/scenarios.py` | Explicit hypothetical accounting calculations |
| `scoreboard/report.py` | Python-generated figures and findings |
| `config/` | Exact source URLs and reviewed institution aliases |
| `data/provenance/` | Download hashes, timestamps, selected CSV members, source catalog |
| `data/processed/` | Versioned public derived school-year tables and crosswalks |
| `results/` | Models, descriptive statistics, coverage, residuals, scenarios, static report |
| `results/figures/` | Presentation-ready PNG and SVG charts |
| `tests/` | Logic, independent OLS comparison, source known answers, real-data checks |
| `docs/` | Methods, access/usage notes, proposal, assignment checklist, presentation plan |

## What is complete and what remains

The public-source starter and expanded three-part feasibility analysis execute end to end. A separate private GitHub repository protects unrelated projects; Fenix-Jobsite is outside this project.

The Knight-Newhouse workbook is acquired, staged and joined with retained source IDs and audited calendars. All 1,920 cells in the 2019 portion match a separately generated report. Every source financial value and exact future-cohort join is checked, and three real-data model results agree with an independent full-rank dummy-OLS implementation. The financial transfer/support qualification remains a measurement limit, not an unfulfilled registration step. See [acquisition](docs/knight_acquisition.md), [validation](docs/validation.md), and [the feasibility report](FEASIBILITY_REPORT.md).

The project owner must invite the other four group members and instructor. Each member must commit their own substantive work from their own account; this starter does not manufacture group contributions. Confirm that the local assignment PDF revision matches the previously uploaded copy, obtain instructor topic approval, review the data/methodology, complete final slides, rehearse, attend consultation, and submit peer evaluations. The [assignment checklist](docs/assignment_checklist.md) records the requirements and dates; the [presentation plan](docs/presentation_plan.md) allocates a 20-minute talk among five people.

The optional 2022–2025 extension is deferred. Its NIL, realignment, pandemic, and reporting changes need a separate design and comparable data definitions.

## Data use and credit

Cite the Knight-Newhouse College Athletics Database (a joint project of the Knight Commission and Syracuse University's S.I. Newhouse School), ESPN/AP, U.S. Department of Education EADA, NCES IPEDS, and NACDA/Learfield Directors' Cup. Exact URLs, retrieval times and source hashes are retained. Original publisher PDFs/ESPN JSON and registered financial exports are not redistributed in Git. Derived factual performance tables and aggregate research results support this noncommercial academic project; no unrestricted third-party data license is asserted. See [sources and restrictions](docs/sources.md). No credentials or confidential institutional records are used.
