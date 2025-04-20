"""
Unit tests for bank report import functionality.
"""
import unittest
from pathlib import Path
import pandas as pd
from src.data_import.bank_report import import_bank_report, get_transaction_summary


class TestBankReport(unittest.TestCase):
    """Test cases for bank report import functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.sample_file = Path(__file__).parent.parent.parent.parent / 'data' / 'examples' / 'sample_bank_report.csv'
        _, self.expenses_df = import_bank_report(self.sample_file)
        self.income_df, _ = import_bank_report(self.sample_file)
    
    def test_import_structure(self):
        """Test that imported data has the correct structure."""
        required_columns = {
            'posting_date', 'payment_date', 'amount', 'transaction_type',
            'recipient_name', 'recipient_account', 'recipient_bic',
            'reference_number', 'message', 'archive_id'
        }
        
        # Check columns exist
        self.assertTrue(
            required_columns.issubset(self.expenses_df.columns),
            "Missing required columns in expenses DataFrame"
        )
        self.assertTrue(
            required_columns.issubset(self.income_df.columns),
            "Missing required columns in income DataFrame"
        )
        
        # Check data types
        self.assertTrue(pd.api.types.is_datetime64_any_dtype(self.expenses_df['posting_date']))
        self.assertTrue(pd.api.types.is_float_dtype(self.expenses_df['amount']))
    
    def test_transaction_separation(self):
        """Test that transactions are correctly separated into income and expenses."""
        # All amounts in expenses should be positive (we convert them in import)
        self.assertTrue((self.expenses_df['amount'] > 0).all())
        
        # All amounts in income should be positive
        self.assertTrue((self.income_df['amount'] > 0).all())
        
        # Check specific transactions
        expense_types = self.expenses_df['transaction_type'].unique()
        self.assertIn('KORTTIOSTO', expense_types)  # Card purchase
        
        income_types = self.income_df['transaction_type'].unique()
        self.assertIn('PALKKA', income_types)  # Salary
    
    def test_transaction_summary(self):
        """Test transaction summary generation."""
        summary = get_transaction_summary(self.expenses_df)
        
        # Check summary structure
        self.assertIn('amount', summary.columns.levels[0])
        self.assertIn('posting_date', summary.columns.levels[0])
        
        # Check summary calculations
        korttiosto = summary.loc['KORTTIOSTO']
        korttiosto_count = len(self.expenses_df[self.expenses_df['transaction_type'] == 'KORTTIOSTO'])
        self.assertEqual(korttiosto[('amount', 'count')], korttiosto_count)
        
        # Verify total amounts
        total_expenses = self.expenses_df['amount'].sum()
        sum_by_type = summary[('amount', 'sum')].sum()
        self.assertAlmostEqual(total_expenses, sum_by_type)
    
    def test_finnish_format(self):
        """Test handling of Finnish date and number formats."""
        # Check date parsing
        self.assertTrue(all(isinstance(date, pd.Timestamp) 
                          for date in self.expenses_df['posting_date']))
        
        # Verify amounts are correctly parsed from Finnish format (comma as decimal)
        sample_amount = self.expenses_df.iloc[0]['amount']
        self.assertIsInstance(sample_amount, float)


if __name__ == '__main__':
    unittest.main() 