"""
Multi-month and multi-account expense processor for PennyWise.
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

import os
from collections import defaultdict
import pandas as pd

from data_import.filename_parser import parse_filename
from data_import.bank_report import import_bank_report
from core.categorization import categorize_transactions
from core.calculations import Person, Contribution
from core.balancesheet import BalanceSheet


def process_all_months(data_dir: str = "data/statements/"):
    all_files = [f for f in os.listdir(data_dir) if f.endswith(".csv")]
    month_groups = defaultdict(list)
    results_by_month = {}

    for file in all_files:
        metadata = parse_filename(file)
        if not metadata:
            print(f"⚠️ Skipping invalid file name: {file}")
            continue

        metadata["filepath"] = os.path.join(data_dir, file)
        month_groups[metadata["year_month"]].append(metadata)

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
            income_df, expenses_df = import_bank_report(meta["filepath"])
            people[name].monthly_income += income_df["amount"].sum()

            categorized_expenses = categorize_transactions(expenses_df)
            for _, row in categorized_expenses.iterrows():
                contribution.add_expense(
                    category=row["category"],
                    amount=row["amount"],
                    paid_by=name,
                    is_shared=True
                )

        result = BalanceSheet.generate_monthly_balance(contribution)
        results_by_month[year_month] = result

        print(result["summary"])

        a = result["person_a"]
        b = result["person_b"]
        ir = result["income_ratios"]
        pr = result["paid_ratios"]

        print(f"--- {a['name']} ---")
        print(f"  Income:            €{a['income']:.2f}  ({ir['person_a'] * 100:.2f}% of household income)")
        print(f"  Shared Paid:       €{a['actual_paid']:.2f}  ({pr['person_a'] * 100:.2f}% of shared expenses)")
        print(f"  Fair Contribution: €{a['fair_share']:.2f}")
        print(f"  Adjustment:        €{a['balance']:+.2f}\n")

        print(f"--- {b['name']} ---")
        print(f"  Income:            €{b['income']:.2f}  ({ir['person_b'] * 100:.2f}% of household income)")
        print(f"  Shared Paid:       €{b['actual_paid']:.2f}  ({pr['person_b'] * 100:.2f}% of shared expenses)")
        print(f"  Fair Contribution: €{b['fair_share']:.2f}")
        print(f"  Adjustment:        €{b['balance']:+.2f}")

    # Step 4: Final summary across all months
    print("\n📊 === Multi-Month Summary ===")
    total_paid = {}
    total_fair = {}
    total_balance = {}

    for result in results_by_month.values():
        for key in ['person_a', 'person_b']:
            p = result[key]['name']
            total_paid[p] = total_paid.get(p, 0) + result[key]['actual_paid']
            total_fair[p] = total_fair.get(p, 0) + result[key]['fair_share']
            total_balance[p] = total_balance.get(p, 0) + result[key]['balance']

    for person in total_paid:
        print(f"--- {person} ---")
        print(f"  Total Paid:        €{total_paid[person]:.2f}")
        print(f"  Total Fair Share:  €{total_fair[person]:.2f}")
        print(f"  Net Adjustment:    €{total_balance[person]:+.2f}\n")

    # Summary sentence like single-month style
    debtor, creditor = None, None
    amount = 0

    balances = list(total_balance.items())
    if abs(balances[0][1]) > 0.01:
        if balances[0][1] > 0:
            debtor, creditor = balances[0][0], balances[1][0]
            amount = balances[0][1]
        else:
            debtor, creditor = balances[1][0], balances[0][0]
            amount = balances[1][1]

        print(f"\n💸 To equalize the full period, {debtor} could transfer €{amount:.2f} to {creditor}.")
    else:
        print("\n✅ All shared expenses are perfectly balanced over the full period.")



if __name__ == "__main__":
    process_all_months("data/statements/")
