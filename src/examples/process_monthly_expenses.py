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
    person_a_income: float,
    person_a_statement: Path,
    person_b_name: str,
    person_b_income: float,
    person_b_statement: Path
) -> dict:
    """
    Process monthly expenses for two people and calculate balances.
    
    Args:
        person_a_name: Name of first person
        person_a_income: Monthly income of first person
        person_a_statement: Path to first person's bank statement
        person_b_name: Name of second person
        person_b_income: Monthly income of second person
        person_b_statement: Path to second person's bank statement
        
    Returns:
        Dictionary containing the monthly balance sheet
    """
    # Create person objects
    person_a = Person(person_a_name, monthly_income=person_a_income)
    person_b = Person(person_b_name, monthly_income=person_b_income)
    
    # Create contribution tracker
    contribution = Contribution(person_a, person_b)
    
    # Process person A's statement
    income_a, expenses_a = import_bank_report(person_a_statement)
    categorized_a = categorize_transactions(expenses_a)
    
    # Process person B's statement
    income_b, expenses_b = import_bank_report(person_b_statement)
    categorized_b = categorize_transactions(expenses_b)
    
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
    # Example file paths - you would replace these with actual paths
    data_dir = Path(__file__).parent.parent.parent / 'data'
    person_a_statement = data_dir / 'examples' / 'person_a_march_2024.csv'
    person_b_statement = data_dir / 'examples' / 'person_b_march_2024.csv'
    
    # Process monthly expenses
    balance = process_monthly_expenses(
        person_a_name="Alice",
        person_a_income=3000.0,
        person_a_statement=person_a_statement,
        person_b_name="Bob",
        person_b_income=2000.0,
        person_b_statement=person_b_statement
    )
    
    # Print results
    print("\n=== Monthly Balance Sheet ===")
    print(f"Total Shared Expenses: €{balance['total_shared_expenses']:.2f}")
    print("\nPerson A:")
    print(f"  Name: {balance['person_a']['name']}")
    print(f"  Fair Share: €{balance['person_a']['fair_share']:.2f}")
    print(f"  Actually Paid: €{balance['person_a']['actual_paid']:.2f}")
    print(f"  Balance: €{balance['person_a']['balance']:.2f}")
    print("\nPerson B:")
    print(f"  Name: {balance['person_b']['name']}")
    print(f"  Fair Share: €{balance['person_b']['fair_share']:.2f}")
    print(f"  Actually Paid: €{balance['person_b']['actual_paid']:.2f}")
    print(f"  Balance: €{balance['person_b']['balance']:.2f}")
    print(f"\nSummary: {balance['summary']}")


if __name__ == "__main__":
    main() 