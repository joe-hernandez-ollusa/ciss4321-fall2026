from decimal import Decimal
from typing import Any

from tracker.models import Category
from tracker.storage import StorageInterface


class ReportService:
    """Generates summaries and spending metrics."""

    def __init__(self, storage: StorageInterface) -> None:
        self.storage = storage

    def generate_monthly_report(self, year: int, month: int) -> dict[str, Any]:
        """Generate a monthly spending report with totals and category breakdown.
        
        Requirements:
        1. Calculate total spending for the given year and month.
        2. Breakdown total by Category.
        3. Identify the highest spending Category.
        4. Return a structured summary dictionary or model.
        
        Args:
            year: The year for the report.
            month: The month for the report (1-12).
        
        Returns:
            A dictionary containing:
            - 'total_spending': Total amount spent in the month (Decimal)
            - 'by_category': Dict[str, Decimal] with spending per category
            - 'top_category': Category with highest spending, or None if no expenses
        """
        # Validate month
        if month < 1 or month > 12:
            raise ValueError("Month must be between 1 and 12.")
        
        # Fetch all expenses
        all_expenses = self.storage.list_expenses()
        
        # Filter expenses for the given month and year
        month_expenses = [
            exp for exp in all_expenses
            if exp.date.year == year and exp.date.month == month
        ]
        
        # Calculate total spending
        total_spending = Decimal("0.00")
        spending_by_category: dict[str, Decimal] = {}
        
        # Initialize category dict with all categories (set to 0)
        for category in Category:
            spending_by_category[category.value] = Decimal("0.00")
        
        # Sum up expenses by category
        for expense in month_expenses:
            total_spending += expense.amount
            category_key = expense.category.value
            spending_by_category[category_key] += expense.amount
        
        # Find top category (highest spending)
        top_category: str | None = None
        max_spending = Decimal("0.00")
        for category_key, amount in spending_by_category.items():
            if amount > max_spending:
                max_spending = amount
                top_category = category_key
        
        return {
            "total_spending": total_spending,
            "by_category": spending_by_category,
            "top_category": top_category,
        }
