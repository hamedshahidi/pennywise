"""
Core calculation module for tracking contributions, calculating fair shares,
and generating balance sheets.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime
import pandas as pd


@dataclass
class Person:
    """Represents a person's financial data."""
    name: str
    monthly_income: float = 0.0
    personal_expenses: Dict[str, float] = field(default_factory=dict)
    shared_expenses_paid: Dict[str, float] = field(default_factory=dict)


@dataclass
class Contribution:
    """Tracks financial contributions between two partners."""
    person_a: Person
    person_b: Person
    shared_expenses: Dict[str, float] = field(default_factory=dict)
    date: datetime = field(default_factory=datetime.now)

    def add_expense(self, category: str, amount: float, paid_by: str, is_shared: bool = True) -> None:
        """
        Add an expense to the tracking system.
        
        Args:
            category: Expense category (e.g., 'food', 'rent')
            amount: Amount paid
            paid_by: Name of person who paid
            is_shared: Whether this is a shared expense or personal
        """
        if paid_by == self.person_a.name:
            person = self.person_a
        elif paid_by == self.person_b.name:
            person = self.person_b
        else:
            raise ValueError(f"Unknown person: {paid_by}")

        if is_shared:
            person.shared_expenses_paid[category] = person.shared_expenses_paid.get(category, 0) + amount
            self.shared_expenses[category] = self.shared_expenses.get(category, 0) + amount
        else:
            person.personal_expenses[category] = person.personal_expenses.get(category, 0) + amount

    def get_total_shared_expenses(self) -> float:
        """Get total amount of shared expenses."""
        return sum(self.shared_expenses.values())

    def get_person_shared_paid(self, name: str) -> float:
        """Get total amount of shared expenses paid by a person."""
        if name == self.person_a.name:
            return sum(self.person_a.shared_expenses_paid.values())
        elif name == self.person_b.name:
            return sum(self.person_b.shared_expenses_paid.values())
        raise ValueError(f"Unknown person: {name}")


class FairShareCalculator:
    """Calculates fair shares based on income ratios."""
    
    @staticmethod
    def calculate_income_ratio(person_a: Person, person_b: Person) -> tuple[float, float]:
        """
        Calculate the fair share ratio based on incomes.
        
        Returns:
            Tuple of (person_a_ratio, person_b_ratio)
        """
        total_income = person_a.monthly_income + person_b.monthly_income
        if total_income == 0:
            return (0.5, 0.5)  # Default to 50/50 if no income
        
        ratio_a = person_a.monthly_income / total_income
        return (ratio_a, 1 - ratio_a)

    @staticmethod
    def calculate_fair_shares(contribution: Contribution) -> tuple[float, float]:
        """
        Calculate how much each person should pay based on income ratios.
        
        Returns:
            Tuple of (person_a_fair_share, person_b_fair_share)
        """
        ratio_a, ratio_b = FairShareCalculator.calculate_income_ratio(
            contribution.person_a, contribution.person_b
        )
        total_shared = contribution.get_total_shared_expenses()
        return (total_shared * ratio_a, total_shared * ratio_b)


class BalanceSheet:
    """Generates balance sheets and calculates who owes whom."""
    
    @staticmethod
    def generate_monthly_balance(contribution: Contribution) -> dict:
        """
        Generate a monthly balance sheet showing who owes whom.
        
        Returns:
            Dictionary containing balance details
        """
        # Calculate fair shares
        fair_share_a, fair_share_b = FairShareCalculator.calculate_fair_shares(contribution)
        
        # Get actual payments
        actual_paid_a = contribution.get_person_shared_paid(contribution.person_a.name)
        actual_paid_b = contribution.get_person_shared_paid(contribution.person_b.name)
        
        # Calculate balance
        balance_a = fair_share_a - actual_paid_a  # Positive means A owes, negative means A is owed
        
        return {
            'total_shared_expenses': contribution.get_total_shared_expenses(),
            'person_a': {
                'name': contribution.person_a.name,
                'fair_share': fair_share_a,
                'actual_paid': actual_paid_a,
                'balance': balance_a
            },
            'person_b': {
                'name': contribution.person_b.name,
                'fair_share': fair_share_b,
                'actual_paid': actual_paid_b,
                'balance': -balance_a  # Opposite of person A's balance
            },
            'summary': BalanceSheet._generate_summary(contribution.person_a.name, contribution.person_b.name, balance_a)
        }

    @staticmethod
    def _generate_summary(person_a_name: str, person_b_name: str, balance_a: float) -> str:
        """Generate a human-readable summary of who owes whom."""
        if abs(balance_a) < 0.01:  # Handle floating point comparison
            return "All expenses are perfectly balanced"
        
        debtor = person_a_name if balance_a > 0 else person_b_name
        creditor = person_b_name if balance_a > 0 else person_a_name
        amount = abs(balance_a)
        
        return f"{debtor} owes {creditor} €{amount:.2f}" 