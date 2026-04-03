# This service does all the number crunching for the dashboard summary.
# It's kept separate from the route so the logic is easy to read, test, and change
# without touching the API layer.

from sqlalchemy.orm import Session
from app import models
from collections import defaultdict


def get_summary(db: Session) -> dict:
    # Pull all finance records from the database in one go.
    # We'll loop through them multiple times to calculate different things.
    records = db.query(models.FinanceRecord).all()

    # Add up all income and all expenses separately.
    total_income  = sum(r.amount for r in records if r.type == "income")
    total_expense = sum(r.amount for r in records if r.type == "expense")

    # Group spending/earnings by category so we can see where money is going.
    # defaultdict(float) means any new category starts at 0 automatically.
    category_totals: dict = defaultdict(float)
    for r in records:
        category_totals[r.category] += r.amount

    # Grab the 5 most recent transactions for the "recent activity" section.
    recent = (
        db.query(models.FinanceRecord)
        .order_by(models.FinanceRecord.date.desc())
        .limit(5)
        .all()
    )

    # Build a month-by-month breakdown of income vs expenses.
    # The key is "YYYY-MM" (e.g. "2024-03") so it sorts chronologically.
    monthly: dict = defaultdict(lambda: {"income": 0.0, "expense": 0.0})
    for r in records:
        key = r.date.strftime("%Y-%m")
        monthly[key][r.type] += r.amount

    return {
        "total_income": total_income,
        "total_expenses": total_expense,
        "net_balance": total_income - total_expense,   # positive = profit, negative = loss
        "category_totals": dict(category_totals),
        "recent_transactions": recent,
        "monthly_trends": dict(sorted(monthly.items())),  # sorted so oldest month comes first
    }
