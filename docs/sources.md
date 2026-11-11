# Sources, provenance, access, and data use

Retrieved November 10, 2026. Original source files are cached locally in ignored `data/raw/`; no invented observations or fabricated missing-value replacements. `config/sources.json` contains each exact download URL, year, description, and local filename. `data/provenance/download_manifest.json` records UTC retrieval timestamps, resolved URLs, byte counts, SHA-256 hashes, and status. The downloader verifies cached hashes, checks PDF/ZIP signatures, retries network failures, and exits nonzero on failed active downloads. Superseded unsuccessful filename probes, if present, are retained separately.

| Source | Coverage obtained / fields | Access and restrictions |
|---|---|---|
| [U.S. Department of Education EADA](https://ope.ed.gov/athletics/) | Ten all-data-combined academic-year archives, 2009–10 through 2018–19; total expenses, reported revenue, men's football/basketball expenses, sport participation categories, Division I classification, UNITID | Public bulk download, no login used. Federal data; cite Department of Education EADA. Retain the original codebook inside each ZIP. Data are institutional self-reports, not audited causal or economic profit estimates. |
| [NACDA previous Directors' Cup standings](https://nacda.com/sports/2018/7/17/directorscup-nacda-directorscup-previous-standings-html.aspx) | Ten final Division I standings PDFs and twenty fall/winter PDFs, ending 2010–2019; published rank/points, football and men's basketball sport points | Public PDFs. Publisher copyright remains; no blanket open-data license is asserted. Original PDFs are not republished in Git. Small derived factual tables, source/page references, and reproducible download URLs support this noncommercial academic analysis. Seek permission before broader redistribution of publisher content. |
| [NCES IPEDS complete files](https://nces.ed.gov/ipeds/use-the-data/download-access-database) | Ten years each of HD, IC/ADM, EF-A, IC-AY and public GASB finance F1A; thirty official codebook ZIPs | Public federal bulk CSV files, no login or API key used. Preserve imputation flags and revised-version selection. Cite NCES IPEDS and each survey year. Finance coverage and reporting entity differ across schools. |
| [Knight-Newhouse reports](https://knightnewhousedata.org/reports/30e5ca83) | Registered Excel workbook obtained for 2010–2019: 240 listed institutions, 2,400 rows, eight measures; native IPEDS IDs, subdivision and FBS conference. Revenue/expenses available for 2,289 rows. | User completed registration, terms, and CAPTCHA. Noncommercial use requires attribution; commercial use requires permission. Raw exports and school-level financial data are ignored by Git. |

## Reproducible acquisition

From the repository root, `python -m scoreboard.download` fetches all 120 configured original files and codebooks. `python run_project.py --download --test` performs the entire workflow. Downloads can take several minutes. Once cached, the source hash check avoids unnecessary downloads. `--refresh` explicitly retrieves new versions and updates the manifest; compare hashes before describing updated results as the same vintage.

EADA catalog endpoint: [official file list](https://ope.ed.gov/athletics/api/dataFiles/fileList). The Python downloader uses `api/dataFiles/file?fileName=` with the exact published, URL-encoded filename. The catalog lists `Year=2010` as academic year 2009–10. For the combined series, every archive has an institution-level Excel workbook and SAS/SPSS equivalents. The pipeline reads only required Excel columns, preserving the original member filename. The [EADA user guide](https://ope.ed.gov/athletics/public/html/help/2017_EADA_Data_Analysis_Cutting_Tool_User_Guide_May2017.pdf) explains that bulk files reflect the data collection snapshot and may not incorporate later corrections.

IPEDS official paths use `https://nces.ed.gov/ipeds/datacenter/data/{component}.zip`. Admissions appear in `IC2010`–`IC2013`, then `ADM2014`–`ADM2019`. In the IC files, `APPDATE` identifies whether the institution reported the previous or current fall. The pipeline checks the 1/2 code meanings against each original dictionary, aligns the cohort year, records the collection year, and retains duplicate candidate reports before selecting the latest collection for each institution/cohort. See `admissions_period_rules.json`, `admissions_duplicate_candidates.csv`, and `admissions_by_cohort.csv`. The [NCES survey-methods handbook](https://nces.ed.gov/statprog/handbook/ipeds.asp) documents this timing change. Primary first-time enrollment comes from EF-A level 4, not the variably dated IC enrollment field; ADM/IC enrollment remains a separate field for yield calculations.

The public GASB finance file for fiscal 2018–19 is `f1819_f1a.zip`, not a full four-digit start-year prefix. When a ZIP includes a revised `_rv` CSV, that member is preferred; selected member names are recorded in provenance. Some CSVs have a trailing delimiter only on data lines; `index_col=False` prevents an implicit one-column shift. UNITID is explicitly numeric and merges enforce uniqueness.

NACDA's linked document wrappers can return HTML. The configured URLs use the publisher's public Sidearm S3 PDF location, preserving path and filename. The archive page without a trailing `.aspx` was also accessible during acquisition. Source year/season was verified from the PDF title. The 2010 and 2019 leading rows were checked against original published values. The parser reads table coordinates and retains original page numbers. Source layout differs by year: institution and conference column order, page dimensions, and missing repeated headers require careful handling. In the 2014 final source, Santa Clara's rank 204 appears after rank 205; sorting published ranks preserves both original values.

## Preferred financial source: Knight-Newhouse

The original workbook is now saved locally under ignored `data/private/knight_reports/`. Its [acquisition record](knight_acquisition.md), `data/provenance/knight_acquisition.json`, and `data/provenance/knight_coverage.csv` document the exact report, SHA-256, validation, and missing coverage. It is staged as `data/private/knight_source_panel.csv`; no Knight-based statistical results have yet been finalized.

To reproduce acquisition, use [custom reports](https://knightnewhousedata.org/reports), select **Data (Custom)** and all listed institutions individually, choose 2010–2019 fiscal years, and turn inflation adjustment off. Select Total Expenses, Total Revenues, Donor Contributions, Ticket Sales, Institutional/Government Support, Student Fees, Total Football Spending, and Total Football Coaching Salaries. Leave combined support/fee aggregates and 2025-only participation measures unchecked. Generate the report after the human CAPTCHA. Open **DOWNLOAD DATA from that generated report**, complete registration/terms/CAPTCHA, then use its Excel Data Download link. The generic standalone download link previously returned a 404 HTML page despite the .xlsx filename; that file was rejected. A 21-year all-metric report timed out; this ten-year, eight-metric report succeeded.

Stage the actual workbook, preserving all missing values:

```text
python -m scoreboard.knight_export --input data/private/knight_reports/knight_2010_2019_30e5ca83.xlsx --source-url https://knightnewhousedata.org/reports/30e5ca83
```

`--verify-capture data/private/knight_reports/dda3742f.displayed.json` additionally checks the saved 2019 browser capture. This acquisition checked all 1,920 cells, including missing values. A fresh user can omit that optional capture check and retain the workbook hash/coverage checks. Native IPEDS IDs avoid inventing a school identifier; historical mergers and reporting entities still need review.

The following generic adapter remains available **after** reviewing fiscal-year alignment and transfer/support definitions. It deliberately requires complete financial fields; do not pass the entire missing-data source panel to it or replace missing values with zero.

Copy `config/knight_mapping.example.json` to an ignored local mapping file, replace headings with the actual export headings, and confirm that support and fees are separate. If the export has only school names, build and review a name-to-UNITID crosswalk first; do not invent identifiers. Then run:

```text
python -m scoreboard.knight --input data/private/knight_export.xlsx --mapping data/private/knight_mapping.json
```

The adapter rejects missing fields, duplicate institution-years, negative amounts needing review, and overlapping column mappings. It records an original-file hash, checks integer identifiers/years, and calculates generated revenue and direct balance. Raw and normalized exports stay outside Git. Review [Knight-Newhouse methodology](https://knightnewhousedata.org/about-the-data) before comparing its MFRS-based numbers with EADA, whose financial definitions differ. Do not fill missing Knight-Newhouse years from EADA as though the measures were identical.

Attribution required by [Knight-Newhouse terms](https://knightnewhousedata.org/privacy-policy-and-terms-of-use): Knight-Newhouse College Athletics Database, a joint project of the Knight Commission on Intercollegiate Athletics and the S.I. Newhouse School of Public Communications, Syracuse University. The site permits noncommercial use with credit and requires prior permission for commercial use. It does not state an unrestricted redistribution license for raw exports.

## University finance context

IPEDS F1A fields retained: `F1B01` tuition and fees after discounts/allowances; `F1B02` federal operating grants/contracts; `F1B03` state operating grants/contracts; `F1B27` total operating/nonoperating revenues; `F1C011` instruction expenses; `F1C191` total expenses/deductions. Dictionaries define these fields; public GASB files do not cover every private institution. Aggregate net tuition revenue divided by enrollment would be an average, not an incremental contribution margin, and is not used to value athletics-induced enrollment. Sticker tuition from IC-AY is contextual only.

## Matching audit

`school_crosswalk.csv` identifies each exact-normalized or reviewed alias match at school/year level. Parenthetical state/campus qualifiers are retained during normalization. Miami (Ohio) is distinguished from Miami (Florida); Boston College from Boston University; Saint Francis PA from St. Francis NY; and Alabama from UAB. Kennesaw State has an explicitly year-specific UNITID map around its merger. Military academies are in Cup standings but absent from the downloaded EADA DI records and remain unmatched. Never accept fuzzy-match suggestions automatically.

The resulting sample is not a balanced census of every Division I program. `coverage.csv`, `unmatched_cup.csv`, season-specific tables, and model-specific sample sizes document the usable coverage. Federal self-reports can contain classification anomalies; unmatched EADA records do not enter the Cup-based primary models. Treat unresolved campus/system or reporting changes as a limitation requiring review.
