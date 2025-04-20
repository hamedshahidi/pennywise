"""
Unit tests for transaction categorization functionality.
"""
import unittest
from pathlib import Path
import pandas as pd
from src.categorization.transaction_categories import (
    categorize_transactions,
    override_category,
    save_categorized_data,
    load_category_mappings,
    DEFAULT_CATEGORY_MAPPINGS
)
from src.data_import.bank_report import import_bank_report


class TestTransactionCategories(unittest.TestCase):
    """Test cases for transaction categorization functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.sample_file = Path(__file__).parent.parent.parent.parent / 'data' / 'examples' / 'sample_bank_report.csv'
        self.output_dir = Path(__file__).parent.parent.parent.parent / 'data' / 'processed'
        self.output_dir.mkdir(exist_ok=True)
        
        # Import and categorize test data
        _, self.expenses_df = import_bank_report(self.sample_file)
        self.categorized_df = categorize_transactions(self.expenses_df)
    
    def test_default_mappings(self):
        """Test that default category mappings are loaded correctly."""
        mappings = load_category_mappings()
        self.assertEqual(mappings, DEFAULT_CATEGORY_MAPPINGS)
    
    def test_categorization(self):
        """Test that transactions are correctly categorized."""
        test_cases = {
            'LIDL HELSINKI': 'food',
            'HSL': 'transport',
            'NETFLIX': 'entertainment',
            'MEHILÄINEN': 'health',
            'DNA OYJ': 'utilities',
            'VUOKRANANTAJA OY': 'rent'
        }
        
        for recipient, expected_category in test_cases.items():
            with self.subTest(recipient=recipient):
                actual = self.categorized_df[
                    self.categorized_df['recipient_name'] == recipient
                ]['category'].iloc[0]
                self.assertEqual(
                    actual, 
                    expected_category, 
                    f"Expected {recipient} to be {expected_category}, got {actual}"
                )
    
    def test_manual_override(self):
        """Test manual category override functionality."""
        # Find Netflix transaction
        netflix_idx = self.categorized_df[
            self.categorized_df['recipient_name'] == 'NETFLIX'
        ].index[0]
        
        # Override category
        updated_df = override_category(self.categorized_df, netflix_idx, 'streaming')
        
        # Verify override
        self.assertEqual(
            updated_df[updated_df['recipient_name'] == 'NETFLIX']['category'].iloc[0],
            'streaming'
        )
        self.assertFalse(
            updated_df[updated_df['recipient_name'] == 'NETFLIX']['auto_categorized'].iloc[0]
        )
    
    def test_data_export(self):
        """Test data export functionality."""
        # Test CSV export
        csv_path = self.output_dir / 'test_categorized_expenses.csv'
        save_categorized_data(self.categorized_df, csv_path, 'csv')
        self.assertTrue(csv_path.exists())
        
        # Test JSON export
        json_path = self.output_dir / 'test_categorized_expenses.json'
        save_categorized_data(self.categorized_df, json_path, 'json')
        self.assertTrue(json_path.exists())
        
        # Verify data can be read back
        exported_df = pd.read_csv(csv_path)
        self.assertEqual(len(exported_df), len(self.categorized_df))


if __name__ == '__main__':
    unittest.main() 