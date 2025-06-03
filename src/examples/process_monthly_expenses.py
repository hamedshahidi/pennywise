"""
Example script demonstrating how to process monthly expenses using PennyWise.
"""
from pathlib import Path
from datetime import datetime
from src.data_import.bank_report import import_bank_report
from src.categorization.transaction_categories import categorize_transactions
from src.core.calculations import Person, Contribution, BalanceSheet


def process_monthly_expenses(
    person_a_name: str,
    person_a_statement: Path,
    person_b_name: str,
    person_b_statement: Path
) -> dict:
    """
    Process monthly expenses for two people and calculate balances.

    Args:
        person_a_name: Name of first person
        person_a_statement: Path to first person's bank statement
        person_b_name: Name of second person
        person_b_statement: Path to second person's bank statement

    Returns:
        Dictionary containing the monthly balance sheet
    """
    # Process person A's statement
    income_a, expenses_a = import_bank_report(person_a_statement)
    person_a = Person(person_a_name, monthly_income=income_a["amount"].sum())
    categorized_a = categorize_transactions(expenses_a)

    # Process person B's statement
    income_b, expenses_b = import_bank_report(person_b_statement)
    person_b = Person(person_b_name, monthly_income=income_b["amount"].sum())
    categorized_b = categorize_transactions(expenses_b)

    # Create contribution tracker
    contribution = Contribution(person_a, person_b)

    # Add expenses to contribution tracker
    for _, row in categorized_a.iterrows():
        contribution.add_expense(
            category=row['category'],
            amount=row['amount'],
            paid_by=person_a_name,
            is_shared=True  # You might want to add logic to determine if an expense is shared
        )

    for _, row in categorized_b.iterrows():
        contribution.add_expense(
            category=row['category'],
            amount=row['amount'],
            paid_by=person_b_name,
            is_shared=True  # You might want to add logic to determine if an expense is shared
        )

    # Generate and return balance sheet
    return BalanceSheet.generate_monthly_balance(contribution)


def main():
    """Example usage of the monthly expense processor."""
    from pathlib import Path

    # Example file paths - you would replace these with actual paths
    data_dir = Path(__file__).parent.parent.parent / 'data'
    person_a_statement = data_dir / 'examples' / 'person_a_jan_2025.csv'
    person_b_statement = data_dir / 'examples' / 'person_b_jan_2025.csv'

    # Process monthly expenses
    balance = process_monthly_expenses(
        person_a_name="Alice",
        person_a_statement=person_a_statement,
        person_b_name="Bob",
        person_b_statement=person_b_statement
    )

    # Extract data
    total_income = balance['total_income']
    total_shared = balance['total_shared_expenses']

    a = balance['person_a']
    b = balance['person_b']
    ir = balance['income_ratios']
    pr = balance['paid_ratios']

    # Print report
    print("\n=== Monthly Household Summary ===")
    print(f"Total Combined Income: €{total_income:.2f}")
    print(f"Total Shared Expenses: €{total_shared:.2f}\n")

    print(f"--- {a['name']} ---")
    print(f"  Income:            €{a['income']:.2f}  ({ir['person_a'] * 100:.2f}% of household income)")
    print(f"  Shared Paid:       €{a['actual_paid']:.2f}  ({pr['person_a'] * 100:.2f}% of shared expenses)")
    print(f"  Fair Contribution: €{a['fair_share']:.2f}")
    print(f"  Adjustment:        €{a['balance']:+.2f}\n")

    print(f"--- {b['name']} ---")
    print(f"  Income:            €{b['income']:.2f}  ({ir['person_b'] * 100:.2f}% of household income)")
    print(f"  Shared Paid:       €{b['actual_paid']:.2f}  ({pr['person_b'] * 100:.2f}% of shared expenses)")
    print(f"  Fair Contribution: €{b['fair_share']:.2f}")
    print(f"  Adjustment:        €{b['balance']:+.2f}\n")

    print("🔄 Balance Adjustment Suggestion:")
    print(f"  {balance['summary']}")

    # Budget health check
    if total_shared > total_income:
        deficit = total_shared - total_income
        print("\n💸 Budget Health Warning:")
        print(f"  Shared expenses exceeded total income by €{deficit:.2f}.")
        print("  Consider reviewing spending or covering the difference from savings.")
    elif total_shared < total_income:
        surplus = total_income - total_shared
        print("\n💰 Budget Health:")
        print(f"  You spent €{surplus:.2f} less than total income. Good job!")
    else:
        print("\n🧾 Budget Health: Spending exactly matched total income.")

    """Example usage of the monthly expense processor."""
    # Example file paths - you would replace these with actual paths
    data_dir = Path(__file__).parent.parent.parent / 'data'
    person_a_statement = data_dir / 'examples' / 'person_a_jan_2025.csv'
    person_b_statement = data_dir / 'examples' / 'person_b_jan_2025.csv'

    # Process monthly expenses
    balance = process_monthly_expenses(
        person_a_name="Alice",
        person_a_statement=person_a_statement,
        person_b_name="Bob",
        person_b_statement=person_b_statement
    )

if __name__ == "__main__":
    main()
