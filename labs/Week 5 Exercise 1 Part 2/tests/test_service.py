from datetime import date
from decimal import Decimal
import pytest
from tracker.models import User, Expense, Category
from tracker.storage import InMemoryStorage
from tracker.service import ExpenseService


@pytest.fixture
def test_env():
    storage = InMemoryStorage()
    service = ExpenseService(storage=storage)
    alice = User(user_id="u1", name="Alice", email="alice@example.com")
    bob = User(user_id="u2", name="Bob", email="bob@example.com")
    storage.save_user(alice)
    storage.save_user(bob)
    return storage, service, alice, bob


def test_record_expense_success(test_env):
    storage, service, alice, _ = test_env
    exp = Expense(
        expense_id="e1",
        amount=Decimal("100.00"),
        category=Category.FOOD,
        description="Groceries",
        date=date(2026, 3, 1),
        paid_by=alice.user_id,
    )
    service.record_expense(exp)
    assert storage.get_expense("e1") is not None


def test_record_expense_unregistered_user(test_env):
    _, service, _, _ = test_env
    exp = Expense(
        expense_id="e2",
        amount=Decimal("25.00"),
        category=Category.FOOD,
        description="Coffee",
        date=date(2026, 3, 1),
        paid_by="non_existent_user",
    )
    with pytest.raises(ValueError, match="does not exist"):
        service.record_expense(exp)
