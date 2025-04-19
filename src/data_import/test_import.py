"""
Test script for bank report import functionality.
"""
from pathlib import Path
from bank_report import import_bank_report, get_transaction_summary

def main():
    # Get the example file path
    sample_file = Path(__file__).parent.parent.parent / 'data' / 'examples' / 'sample_bank_report.csv'
    
    # Import the bank report
    income_df, expenses_df = import_bank_report(sample_file)
    
    print("\n=== Income Transactions ===")
    print(income_df[['posting_date', 'amount', 'transaction_type', 'payer', 'message']].to_string())
    print("\nSummary:")
    print(get_transaction_summary(income_df).to_string())
    
    print("\n=== Expense Transactions ===")
    print(expenses_df[['posting_date', 'amount', 'transaction_type', 'recipient_name', 'message']].to_string())
    print("\nSummary:")
    print(get_transaction_summary(expenses_df).to_string())

if __name__ == '__main__':
    main() 