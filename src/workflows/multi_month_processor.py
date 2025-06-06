"""
Multi-month and multi-account expense processor for PennyWise.

Reads all CSV files in the data directory, parses metadata from filenames,
groups transactions by month, and processes each using the existing fairness logic.

Responsibilities:
- Validate and parse filename structure: <person>-<account>-YYYY-MM.csv
- Detect and warn on unrecognized filenames
- Aggregate income and expenses by person and month
- Run fair-share calculation per month and collect summary results

This module powers the full-period financial analysis across multiple months.

Dependencies:
- core.calculations (Person, Contribution, FairShareCalculator)
- core.balancesheet (BalanceSheet)
- data_import.bank_report (BankReport)
- data_import.filename_parser (parse_filename)
"""
