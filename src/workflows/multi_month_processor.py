"""
Multi-month and multi-account expense processor for PennyWise.

Reads all CSV files in the data directory, parses metadata from filenames,
groups transactions by month, and processes each using the existing fairness logic.

Responsibilities:
- Validate and parse filename structure: <person>_<account>_YYYY_MM.csv
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

"""
Multi-month and multi-account expense processor for PennyWise.
"""

import os
from collections import defaultdict
from pathlib import Path

import pandas as pd

from data_import.filename_parser import parse_filename
from data_import.bank_report import BankReport
from core.calculations import Person, Contribution
from core.balancesheet import BalanceSheet


def process_all_months(data_dir: str = "data/statements/"):
    # Step 1: Collect all CSV files
    all_files = [f for f in os.listdir(data_dir) if f.endswith(".csv")]

    # Step 2: Group files by year_month
    month_groups = defaultdict(list)

    for file in all_files:
        metadata = parse_filename(file)
        if not metadata:
            print(f"⚠️ Skipping invalid file name: {file}")
            continue

        metadata["filepath"] = os.path.join(data_dir, file)
        month_groups[metadata["year_month"]].append(metadata)

    # Step 3: Process each month
    for year_month, files in sorted(month_groups.items()):
        print(f"\n📅 Processing month: {year_month}")

        people: dict[str, Person] = {}

        for meta in files:
            name = meta["person"]
            if name not in people:
                people[name] = Person(name=name)

        all_people = sorted(people.keys())
        if len(all_people) != 2:
            print(f"⚠️ Expected 2 people for shared expenses, found: {all_people}")
            continue

        person_a = people[all_people[0]]
        person_b = people[all_people[1]]
        contribution = Contribution(person_a=person_a, person_b=person_b)

        for meta in files:
            name = meta["person"]
            df = BankReport.read_csv(meta["filepath"])

            for _, row in df.iterrows():
                amount = row["amount"]
                category = row["category"]

                if amount > 0:
                    people[name].monthly_income += amount
                else:
                    contribution.add_expense(
                        category=category,
                        amount=-amount,
                        paid_by=name,
                        is_shared=True
                    )

        result = BalanceSheet.generate_monthly_balance(contribution)
        print(result["summary"])
