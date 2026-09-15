# Post-Mortem: The Naive Prompting Experiment

Answer the following questions based on the changes your AI assistant made:

1. **Precision & Types:** Did the AI use `float`, `int` (cents), or `Decimal` for split amounts and totals? What happens if you split $100.00 among 3 people?

The code uses Decimal for all expense amounts and totals. In split_expense, it divides the amount using Decimal, rounds to two decimal places, and distributes the remaining cents sequentially. For example, splitting $100.00 among 3 people assigns $33.34 to the first person and $33.33 to the other two, keeping the total exact. Note: The percentage parameter itself is still typed as a list of floats, though the AI casts them to Decimal before calculation.

2. **Architectural Drift:** Did the AI call methods on `StorageInterface`, or did it read/write files directly inside `service.py` or `reports.py`?

It respected the architecture and stuck to StorageInterface rather than writing directly to disk. It correctly leverages get_expense(), get_user(), and save_expense() for splits, and self.storage.list_expenses() for monthly reports. The CSV importer uses open() to read the raw file, but still channels all saves through self.storage.save_expense().

3. **Contracts & Validation:** Did the CSV importer construct validated `Expense` models, or did it pass raw untyped dictionaries around?

It correctly constructed validated Expense models. The importer parses each row, casts the types (dates, Decimal amounts), validates the category against the Category model, verifies the user exists, and then instantiates a proper Expense object before saving.


4. **Code Quality:** What errors did `ruff` and `mypy` flag after the AI generated the code?

ruff flagged 16 errors (14 auto-fixable), mostly covering unsorted imports, an unused json import, and outdated typing syntax (e.g., typing.Dict/List and Optional[X] instead of X | None). mypy caught 6 errors across 2 test files, all due to missing return types or missing annotations on test functions.


5. **System Instructions:** Write 3 concrete repository rules (e.g., for `.cursorrules`) that would have prevented these specific errors.


1. All Python code must pass ruff check . before it is considered complete, including correct import ordering, no unused imports, and the project's preferred modern type-hint syntax.

2. All functions, including test functions, must include complete type annotations and the entire repository must pass mypy . without errors.

3. Monetary values must always use Decimal, validated Expense models must be used when creating expenses, and all application data access must go through StorageInterface rather than directly reading or writing the application's storage files.
