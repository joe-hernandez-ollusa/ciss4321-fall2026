import csv
from datetime import date
from decimal import Decimal

from tracker.models import Category, Expense
from tracker.storage import StorageInterface


class ExpenseService:
    """Core service orchestrating expense operations and business rules."""

    def __init__(self, storage: StorageInterface) -> None:
        self.storage = storage

    def record_expense(self, expense: Expense) -> None:
        """Record a single expense after validating the payer exists."""
        payer = self.storage.get_user(expense.paid_by)
        if payer is None:
            raise ValueError(f"User {expense.paid_by} does not exist.")
        self.storage.save_expense(expense)

    def split_expense(
        self,
        original_expense_id: str,
        target_user_ids: list[str],
        percentages: list[float] | None = None,
    ) -> list[Expense]:
        """Split an expense evenly or by percentage across target users.
        
        Requirements:
        1. Original expense must exist in storage.
        2. All target users must exist in storage.
        3. Splitting must conserve exact currency values (no fractional cent loss).
        4. Record all individual split expenses back to storage.
        
        Args:
            original_expense_id: The ID of the expense to split.
            target_user_ids: List of user IDs to split the expense across.
            percentages: Optional list of percentages for each user (must sum to ~100).
                        If None, splits evenly.
        
        Returns:
            List of individual Expense objects created by the split.
        """
        # Validate original expense exists
        original_expense = self.storage.get_expense(original_expense_id)
        if original_expense is None:
            raise ValueError(f"Expense {original_expense_id} does not exist.")
        
        # Validate all target users exist
        for user_id in target_user_ids:
            user = self.storage.get_user(user_id)
            if user is None:
                raise ValueError(f"User {user_id} does not exist.")
        
        num_participants = len(target_user_ids)
        if num_participants == 0:
            raise ValueError("Must split expense across at least one participant.")
        
        # Calculate split amounts using Decimal for precision
        split_amounts: list[Decimal] = []
        
        if percentages is None:
            # Split evenly
            base_amount = original_expense.amount / Decimal(num_participants)
            base_amount_truncated = base_amount.quantize(Decimal("0.01"))
            remainder = original_expense.amount - (base_amount_truncated * Decimal(num_participants))
            
            for i in range(num_participants):
                if i == 0:
                    # Give first participant the base amount plus any remainder
                    split_amounts.append(base_amount_truncated + remainder)
                else:
                    split_amounts.append(base_amount_truncated)
        else:
            # Split by percentage
            if len(percentages) != num_participants:
                raise ValueError(
                    f"Number of percentages ({len(percentages)}) must match "
                    f"number of participants ({num_participants})."
                )
            
            if abs(sum(percentages) - 100.0) > 0.01:
                raise ValueError("Percentages must sum to approximately 100.")
            
            # Calculate each split amount, with last participant getting remainder
            total_allocated = Decimal("0.00")
            for i, percentage in enumerate(percentages):
                if i == num_participants - 1:
                    # Last participant gets the remainder to ensure exact conservation
                    split_amounts.append(original_expense.amount - total_allocated)
                else:
                    amount = (
                        original_expense.amount * Decimal(str(percentage)) / Decimal(100)
                    ).quantize(Decimal("0.01"))
                    split_amounts.append(amount)
                    total_allocated += amount
        
        # Create and record split expenses
        split_expenses: list[Expense] = []
        for i, user_id in enumerate(target_user_ids):
            split_expense_obj = Expense(
                expense_id=f"{original_expense_id}_split_{i}",
                amount=split_amounts[i],
                category=original_expense.category,
                description=f"Split from {original_expense.description}",
                date=original_expense.date,
                paid_by=original_expense.paid_by,
                split_group_id=original_expense_id,
            )
            self.storage.save_expense(split_expense_obj)
            split_expenses.append(split_expense_obj)
        
        return split_expenses

    def import_expenses_from_csv(self, filepath: str) -> list[Expense]:
        """Import expenses from a CSV file and record them to storage.
        
        The CSV file must have the following columns (header required):
        - date: ISO format date (YYYY-MM-DD)
        - amount: Decimal amount as string (e.g., "42.50")
        - category: One of the valid Category values
        - description: Text description of the expense
        - paid_by: User ID of the person who paid
        
        Args:
            filepath: Path to the CSV file.
        
        Returns:
            List of Expense objects that were imported and recorded.
        
        Raises:
            ValueError: If users don't exist, categories are invalid, or data is malformed.
            FileNotFoundError: If the CSV file does not exist.
        """
        imported_expenses: list[Expense] = []
        
        with open(filepath, "r", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            if reader.fieldnames is None:
                raise ValueError("CSV file is empty or has no header row.")
            
            required_fields = {"date", "amount", "category", "description", "paid_by"}
            if not required_fields.issubset(set(reader.fieldnames)):
                missing = required_fields - set(reader.fieldnames)
                raise ValueError(
                    f"CSV file missing required columns: {', '.join(missing)}"
                )
            
            for row_num, row in enumerate(reader, start=2):  # Start at 2 (after header)
                try:
                    # Parse and validate date
                    expense_date = date.fromisoformat(row["date"].strip())
                    
                    # Parse and validate amount using Decimal (NOT float)
                    amount_str = row["amount"].strip()
                    try:
                        amount = Decimal(amount_str)
                    except Exception as exc:
                        raise ValueError(
                            f"Invalid amount '{amount_str}': {exc}"
                        ) from exc
                    
                    # Parse and validate category
                    category_str = row["category"].strip().lower()
                    try:
                        category = Category(category_str)
                    except ValueError as exc:
                        valid_categories = ", ".join(c.value for c in Category)
                        raise ValueError(
                            f"Invalid category '{category_str}'. "
                            f"Valid categories: {valid_categories}"
                        ) from exc
                    
                    # Parse description and paid_by
                    description = row["description"].strip()
                    paid_by = row["paid_by"].strip()
                    
                    # Validate that the payer exists
                    payer = self.storage.get_user(paid_by)
                    if payer is None:
                        raise ValueError(f"User '{paid_by}' does not exist in storage.")
                    
                    # Generate unique expense ID from date and row number
                    expense_id = f"imported_{expense_date.isoformat()}_{row_num}"
                    
                    # Create and record the expense
                    expense = Expense(
                        expense_id=expense_id,
                        amount=amount,
                        category=category,
                        description=description,
                        date=expense_date,
                        paid_by=paid_by,
                    )
                    self.storage.save_expense(expense)
                    imported_expenses.append(expense)
                
                except ValueError as exc:
                    raise ValueError(f"Error parsing CSV row {row_num}: {exc}") from exc
        
        return imported_expenses
