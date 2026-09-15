# Lab 1: Expense Tracker Core (Vibe Coding vs. Engineering)

Welcome to Advanced Python! This lab demonstrates how unguided AI assistants behave on real multi-file Python codebases.

## Objective
Use your AI coding assistant (Cursor, GitHub Copilot Agent Mode, or Claude Code) using **purely conversational chat prompts**—without adding rules, guidelines, or system instructions—to implement the missing features.

## Setup
1. Create and activate a virtual environment:
   ```bash
   uv venv  # or python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   uv pip install -e ".[dev]" # or pip install -e ".[dev]"
   ```
2. Run tests to confirm baseline passing:
   ```bash
   pytest
   ```

## The Exercise: Conversational Prompting
Run these prompts sequentially in your AI assistant chat window:

1. **Prompt 1 (Splitting Expenses):**
   > "Implement `split_expense` in `src/tracker/service.py` so an expense can be split evenly or by percentage across a list of user IDs. Make sure the split expenses are recorded in storage."
2. **Prompt 2 (Monthly Reports & Metrics):**
   > "Implement `generate_monthly_report` in `src/tracker/reports.py` to calculate total spending, spending by category, and the top category for a given month."
3. **Prompt 3 (CSV Importer):**
   > "Add a function `import_expenses_from_csv(filepath)` that reads a CSV file and adds all expenses into storage."

## Deliverable: The Post-Mortem Report
Run your linters and test suite:
```bash
ruff check .
mypy src
pytest
```
Answer the questions in `POST_MORTEM.md` before moving to Lab 2.
