"""
Processes a single month's worth of bank statements into a fair-share summary.

Used by multi_month_processor, CLI tools, or test runners.
"""

from pathlib import Path
from core.calculations import Person, Contribution
from core.balancesheet import BalanceSheet
from data_import.bank_report import import_bank_report
from core.categorization import categorize_transactions


def process_monthly_expenses(
    person_a_name: str,
    person_a_statement: Path,
    person_b_name: str,
    person_b_statement: Path
) -> dict:
    """Processes two CSV files and returns a monthly balance summary."""
    # Process person A
    income_a, expenses_a = import_bank_report(person_a_statement)
    person_a = Person(name=person_a_name, monthly_income=income_a["amount"].sum())
    categorized_a = categorize_transactions(expenses_a)

    # Process person B
    income_b, expenses_b = import_bank_report(person_b_statement)
    person_b = Person(name=person_b_name, monthly_income=income_b["amount"].sum())
    categorized_b = categorize_transactions(expenses_b)

    # Contribution tracker
    contribution = Contribution(person_a, person_b)

    for _, row in categorized_a.iterrows():
        contribution.add_expense(
            category=row["category"],
            amount=row["amount"],
            paid_by=person_a_name,
            is_shared=True
        )

    for _, row in categorized_b.iterrows():
        contribution.add_expense(
            category=row["category"],
            amount=row["amount"],
            paid_by=person_b_name,
            is_shared=True
        )

    return BalanceSheet.generate_monthly_balance(contribution)
