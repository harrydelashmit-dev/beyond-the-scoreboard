# Beyond the Scoreboard: Does University Investment in Athletics Pay Off?

**AC 547 · Track A · Python-only analytics · 2010–2019 historical panel**

A working, reproducible research starter for university administrators evaluating athletic spending, competitive performance, subsequent student demand, and cautious financial scenarios. This project tests the proposed relationships and reports inconclusive findings as readily as positive ones.

**All data acquisition, cleaning, joins, calculations, regressions, tests, and chart generation are written in Python.** CSV/JSON store data and configuration; Markdown documents the work; HTML/SVG/PNG are generated static outputs. There is no JavaScript, R, Excel formula logic, or non-Python analytics layer.

Read [FINDINGS.md](FINDINGS.md) first. It contains the actual executed coefficients, confidence intervals, and sample sizes. The earlier conversation's football/FPI pilot is not reproduced or treated as evidence here.

## Run it

Use Python 3.12. From the repository root:

```text
python -m venv .venv
```

Activate `.venv` using your operating system's normal activation method, then:

```text
python -m pip install -r requirements.txt
python run_project.py --download --test
```

The first run downloads 120 official files/codebooks. It takes several minutes and requires internet access, but no API key for the available sources. EADA Excel parsing can be slow; intermediate caches accelerate subsequent runs. Source files are hashed and retained locally under ignored `data/raw/`. The Git repository includes compact processed public data so an offline analysis rerun is also possible:

```text
python run_project.py --from-processed --test
```

To rebuild cleaned data from an existing raw cache, use `python run_project.py --test`. Remove only the generated `data/interim/cup_*.csv` or `eada_*.csv` caches after changing their parser logic, or use a fresh clone/cache. Do not refresh raw files casually when trying to reproduce the saved data vintage.

## Results and design

- Three primary tests: prior expenses → Cup points; Cup points → fall t+1 applications; Cup points → fall t+1 first-time enrollment.
- School and year effects, school-clustered intervals, complete-case sample reporting, and Holm adjustment for the primary tests.
- Exploratory football/basketball Cup success comparison on a common FBS sample; timing, first-difference, sample, and scoring-rule sensitivities.
- EADA reported-revenue analysis is explicitly separate from subsidy-adjusted generated revenue.
- Break-even scenarios use additional enrolled students and net tuition contribution, with transparent hypothetical assumptions.

The main estimates are observational associations. Neither significant coefficients nor an appealing diagram establish a causal chain or university ROI. Missing observations are never invented or assigned zero to make a panel look complete.

## Repository map

| Path | Purpose |
|---|---|
| `run_project.py` | Python workflow entry point |
| `scoreboard/download.py` | Official downloads, caching, hash/signature validation |
| `scoreboard/clean.py` | EADA/IPEDS readers, Cup PDF parsing, school aliases and exact-year joins |
| `scoreboard/models.py` | Fixed-effects estimation, clustered inference, sensitivity tables |
| `scoreboard/knight.py` | Validated import of a legitimately obtained registered export |
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

The public-source Python starter executes end to end, includes real historical data, and produces tested empirical results and charts. A separate private GitHub repository protects unrelated projects.

Knight-Newhouse's raw export requires registration and a CAPTCHA. Follow [the source instructions](docs/sources.md) and supply a legitimate export to complete the preferred generated-revenue link. The repository does not represent EADA total revenue as externally generated revenue. No private export, fabricated registration details, or credentials are committed.

The project owner must invite the other four group members and instructor. Each member must commit their own substantive work from their own account; this starter does not manufacture group contributions. Confirm that the local assignment PDF revision matches the previously uploaded copy, obtain instructor topic approval, review the data/methodology, complete final slides, rehearse, attend consultation, and submit peer evaluations. The [assignment checklist](docs/assignment_checklist.md) records the requirements and dates; the [presentation plan](docs/presentation_plan.md) allocates a 20-minute talk among five people.

The optional 2022–2025 extension is deferred. Its NIL, realignment, pandemic, and reporting changes need a separate design and comparable data definitions.

## Data use and credit

Cite U.S. Department of Education EADA, NCES IPEDS, and NACDA/Learfield Directors' Cup for the original data; exact URLs and source pages accompany the derived data. Original publisher PDFs and registered Knight-Newhouse exports are not redistributed in Git. This repository grants no rights to third-party data. See [sources and restrictions](docs/sources.md) before reuse. No confidential sources are used.
