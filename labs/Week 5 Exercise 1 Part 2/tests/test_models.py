from datetime import date
from decimal import Decimal
import pytest
from pydantic import ValidationError
from tracker.models import Expense, Category, User


def test_valid_user_creation():
    user = User(user_id="u1", name="Alice", email="alice@example.com")
    assert user.user_id == "u1"
    assert user.name == "Alice"


def test_valid_expense_creation():
    expense = Expense(
        expense_id="e1",
        amount=Decimal("45.50"),
        category=Category.FOOD,
        description="Lunch",
        date=date(2026, 3, 1),
        paid_by="u1",
    )
    assert expense.amount == Decimal("45.50")
    assert expense.category == Category.FOOD


def test_expense_rejects_negative_or_zero_amount():
    with pytest.raises(ValidationError):
        Expense(
            expense_id="e2",
            amount=Decimal("-10.00"),
            category=Category.FOOD,
            description="Invalid",
            date=date(2026, 3, 1),
            paid_by="u1",
        )
