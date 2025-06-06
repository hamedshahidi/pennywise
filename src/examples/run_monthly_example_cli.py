"""
Example CLI script to run a one-month expense report using PennyWise.
"""

from pathlib import Path
from workflows.monthly_runner import process_monthly_expenses

def main():
    # Example file paths - replace with your actual file locations
    data_dir = Path(__file__).parent.parent / 'data' / 'examples'
    person_a_statement = data_dir / 'person_a_jan_2025.csv'
    person_b_statement = data_dir / 'person_b_jan_2025.csv'

    balance = process_monthly_expenses(
        person_a_name="Alice",
        person_a_statement=person_a_statement,
        person_b_name="Bob",
        person_b_statement=person_b_statement
    )

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
    elif total_shared < total_income:
        surplus = total_income - total_shared
        print("\n💰 Budget Health:")
        print(f"  You spent €{surplus:.2f} less than total income. Good job!")
    else:
        print("\n🧾 Budget Health: Spending exactly matched total income.")


if __name__ == "__main__":
    main()
