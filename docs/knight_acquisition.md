# Knight-Newhouse historical data acquired

On November 10, 2026, the project obtained a valid registered Excel export from the [2010–2019 custom report](https://knightnewhousedata.org/reports/30e5ca83). The user personally completed registration, terms, and CAPTCHA. The workbook contains `Data` and `Data Dictionary` sheets, native IPEDS IDs, fiscal reporting years, NCAA subdivisions, FBS conferences, and these eight measures:

- Total athletics expenses and total athletics revenues
- Donor contributions and ticket sales
- Institutional/government support and separately reported student fees
- Total football spending and total football coaching salaries

The original workbook and staged school-level data remain in ignored `data/private/`. Original SHA-256: `477628256f02980011bf749aa3c1941f8cb939d90fd3640e91b7f62f986cec52` (194,900 bytes). Public acquisition metadata and coverage counts are versioned; the financial observations are not redistributed.

## Coverage and verification

There are **240 listed institutions and 2,400 exported institution-years**. A listed row does not guarantee reported financial data. There are 2,291 rows with at least one measure, 2,289 with both total revenues and expenses, and 1,827 with all eight measures. Available total-expense observations range from 226 to 231 institutions per year. Football coverage is lower and must be analyzed using its own sample.

Python validates workbook signatures, worksheet names, exact headings, integer identifiers/years, and unique institution-years. It retains all source rows and missing cells. Reported zero remains zero. All **1,920 cells** in the workbook's 2019 portion match a separately generated [2019-only report](https://knightnewhousedata.org/reports/dda3742f), including missing cells. This validates acquisition consistency, not the institutions' underlying reports or the future analytical merge.

The report generator timed out on the original 21-year/all-metric request. With eight measures, the 2019, [2014–2019](https://knightnewhousedata.org/reports/ddaeec6f), and full 2010–2019 requests each succeeded. The exact timeout cause is unproven; reducing the request resolved it. Year-by-year generation is unnecessary for this core batch.

## Review before analysis

The [source methodology](https://knightnewhousedata.org/about-the-data) uses NCAA MFRS financial reports and distinguishes these from EADA. It treats FY 2012 as academic year 2011–12. School-specific reporting changes can affect comparisons. The export's total revenue already deducts transfers to the institution, so support/transfer treatment must be reconciled before calculating generated revenue or an operating balance. The methodology also flags a football coaching bonus reporting difference in FY 2015–2017. These require review and sensitivity specifications, not automatic correction.

The next analytical stage must audit historical institution identities, calendar matching, conference histories, unusual values, and usable model samples. No Knight regressions, significance claims, or CFO return estimates have been added yet. The prior football/FPI pilot remains unverified; the proposed spending → success → revenue/student demand pathway remains a hypothesis.

Credit: **Knight-Newhouse College Athletics Database**, a joint project of the Knight Commission on Intercollegiate Athletics and the S.I. Newhouse School of Public Communications, Syracuse University. Academic noncommercial use requires credit; this project assumes no unrestricted right to redistribute its source workbook. See [terms](https://knightnewhousedata.org/privacy-policy-and-terms-of-use).
