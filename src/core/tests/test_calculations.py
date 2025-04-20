"""
Unit tests for core financial calculations.
"""
import unittest
from datetime import datetime
from src.core.calculations import Person, Contribution, FairShareCalculator, BalanceSheet


class TestCoreCalculations(unittest.TestCase):
    """Test cases for core financial calculations."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create test persons
        self.person_a = Person("Alice", monthly_income=3000.0)
        self.person_b = Person("Bob", monthly_income=2000.0)
        self.contribution = Contribution(self.person_a, self.person_b)

    def test_person_creation(self):
        """Test person object creation and properties."""
        person = Person("Test", monthly_income=1500.0)
        self.assertEqual(person.name, "Test")
        self.assertEqual(person.monthly_income, 1500.0)
        self.assertEqual(person.personal_expenses, {})
        self.assertEqual(person.shared_expenses_paid, {})

    def test_expense_tracking(self):
        """Test expense tracking functionality."""
        # Add some shared expenses
        self.contribution.add_expense("rent", 1000.0, "Alice", is_shared=True)
        self.contribution.add_expense("food", 200.0, "Bob", is_shared=True)
        
        # Add some personal expenses
        self.contribution.add_expense("hobby", 50.0, "Alice", is_shared=False)
        self.contribution.add_expense("gym", 40.0, "Bob", is_shared=False)

        # Check shared expenses
        self.assertEqual(self.contribution.get_total_shared_expenses(), 1200.0)
        self.assertEqual(self.contribution.get_person_shared_paid("Alice"), 1000.0)
        self.assertEqual(self.contribution.get_person_shared_paid("Bob"), 200.0)

        # Check personal expenses
        self.assertEqual(self.person_a.personal_expenses["hobby"], 50.0)
        self.assertEqual(self.person_b.personal_expenses["gym"], 40.0)

    def test_fair_share_calculation(self):
        """Test fair share calculation based on income."""
        # Test income ratio calculation
        ratio_a, ratio_b = FairShareCalculator.calculate_income_ratio(self.person_a, self.person_b)
        self.assertAlmostEqual(ratio_a, 0.6)  # Alice should pay 60%
        self.assertAlmostEqual(ratio_b, 0.4)  # Bob should pay 40%

        # Add some shared expenses
        self.contribution.add_expense("rent", 1000.0, "Alice")
        self.contribution.add_expense("utilities", 200.0, "Bob")

        # Test fair share amounts
        fair_share_a, fair_share_b = FairShareCalculator.calculate_fair_shares(self.contribution)
        self.assertAlmostEqual(fair_share_a, 720.0)  # 60% of 1200
        self.assertAlmostEqual(fair_share_b, 480.0)  # 40% of 1200

    def test_balance_sheet(self):
        """Test balance sheet generation."""
        # Add expenses
        self.contribution.add_expense("rent", 1000.0, "Alice")
        self.contribution.add_expense("utilities", 200.0, "Bob")
        
        # Generate balance sheet
        balance = BalanceSheet.generate_monthly_balance(self.contribution)
        
        # Check totals
        self.assertEqual(balance["total_shared_expenses"], 1200.0)
        
        # Check individual balances
        self.assertAlmostEqual(balance["person_a"]["fair_share"], 720.0)
        self.assertEqual(balance["person_a"]["actual_paid"], 1000.0)
        self.assertAlmostEqual(balance["person_a"]["balance"], -280.0)  # Alice overpaid
        
        self.assertAlmostEqual(balance["person_b"]["fair_share"], 480.0)
        self.assertEqual(balance["person_b"]["actual_paid"], 200.0)
        self.assertAlmostEqual(balance["person_b"]["balance"], 280.0)  # Bob needs to pay more
        
        # Check summary
        self.assertEqual(balance["summary"], "Bob owes Alice €280.00")

    def test_edge_cases(self):
        """Test edge cases and error handling."""
        # Test zero income case
        zero_income_a = Person("Zero", monthly_income=0.0)
        zero_income_b = Person("Also Zero", monthly_income=0.0)
        zero_contrib = Contribution(zero_income_a, zero_income_b)
        
        ratio_a, ratio_b = FairShareCalculator.calculate_income_ratio(zero_income_a, zero_income_b)
        self.assertEqual((ratio_a, ratio_b), (0.5, 0.5))  # Should default to 50/50
        
        # Test invalid person name
        with self.assertRaises(ValueError):
            self.contribution.add_expense("food", 100.0, "Charlie")  # Non-existent person
            
        # Test perfectly balanced case
        balanced_a = Person("Balanced A", monthly_income=1000.0)
        balanced_b = Person("Balanced B", monthly_income=1000.0)
        balanced_contrib = Contribution(balanced_a, balanced_b)
        
        balanced_contrib.add_expense("rent", 500.0, "Balanced A")
        balanced_contrib.add_expense("food", 500.0, "Balanced B")
        
        balance = BalanceSheet.generate_monthly_balance(balanced_contrib)
        self.assertEqual(balance["summary"], "All expenses are perfectly balanced")

    def test_expense_categories(self):
        """Test expense categorization and aggregation."""
        # Add expenses in different categories
        categories = ["rent", "food", "utilities", "entertainment"]
        amounts = [1000.0, 200.0, 150.0, 80.0]
        
        for category, amount in zip(categories, amounts):
            self.contribution.add_expense(category, amount, "Alice", is_shared=True)
        
        # Check category totals
        for category, amount in zip(categories, amounts):
            self.assertEqual(
                self.contribution.shared_expenses.get(category, 0),
                amount,
                f"Category {category} total doesn't match"
            )
        
        # Check total across all categories
        self.assertEqual(
            self.contribution.get_total_shared_expenses(),
            sum(amounts)
        )


if __name__ == "__main__":
    unittest.main() 