"""
Generates monthly balance summaries and neutral summary messages.
"""

from core.calculations import FairShareCalculator, Contribution

class BalanceSheet:
    """Generates balance sheets and calculates who owes whom."""

    @staticmethod
    def generate_monthly_balance(contribution: Contribution) -> dict:
        fair_share_a, fair_share_b = FairShareCalculator.calculate_fair_shares(contribution)

        actual_paid_a = contribution.get_person_shared_paid(contribution.person_a.name)
        actual_paid_b = contribution.get_person_shared_paid(contribution.person_b.name)

        balance_a = fair_share_a - actual_paid_a

        total_income = contribution.person_a.monthly_income + contribution.person_b.monthly_income
        total_shared = contribution.get_total_shared_expenses()

        income_ratio_a = (contribution.person_a.monthly_income / total_income) if total_income else 0.5
        income_ratio_b = 1 - income_ratio_a

        paid_ratio_a = (actual_paid_a / total_shared) if total_shared else 0.5
        paid_ratio_b = 1 - paid_ratio_a

        return {
            'total_income': total_income,
            'total_shared_expenses': total_shared,
            'income_ratios': {
                'person_a': income_ratio_a,
                'person_b': income_ratio_b
            },
            'paid_ratios': {
                'person_a': paid_ratio_a,
                'person_b': paid_ratio_b
            },
            'person_a': {
                'name': contribution.person_a.name,
                'income': contribution.person_a.monthly_income,
                'fair_share': fair_share_a,
                'actual_paid': actual_paid_a,
                'balance': balance_a
            },
            'person_b': {
                'name': contribution.person_b.name,
                'income': contribution.person_b.monthly_income,
                'fair_share': fair_share_b,
                'actual_paid': actual_paid_b,
                'balance': -balance_a
            },
            'summary': BalanceSheet._generate_summary(
                contribution.person_a.name,
                contribution.person_b.name,
                balance_a
            )
        }

    @staticmethod
    def _generate_summary(person_a_name: str, person_b_name: str, balance_a: float) -> str:
        if abs(balance_a) < 0.01:
            return "All expenses are perfectly balanced"
        debtor = person_a_name if balance_a > 0 else person_b_name
        creditor = person_b_name if balance_a > 0 else person_a_name
        amount = abs(balance_a)
        return f"To equalize this month's shared expenses, {debtor} could transfer €{amount:.2f} to {creditor}."
