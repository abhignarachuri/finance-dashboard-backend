from sqlalchemy.orm import Session
from app import models
from collections import defaultdict


def get_summary(db: Session) -> dict:
    records = db.query(models.FinanceRecord).all()

    total_income  = sum(r.amount for r in records if r.type == "income")
    total_expense = sum(r.amount for r in records if r.type == "expense")

    category_totals: dict = defaultdict(float)
    for r in records:
        category_totals[r.category] += r.amount

    recent = (
        db.query(models.FinanceRecord)
        .order_by(models.FinanceRecord.date.desc())
        .limit(5)
        .all()
    )

    monthly: dict = defaultdict(lambda: {"income": 0.0, "expense": 0.0})
    for r in records:
        key = r.date.strftime("%Y-%m")
        monthly[key][r.type] += r.amount

    return {
        "total_income": total_income,
        "total_expenses": total_expense,
        "net_balance": total_income - total_expense,   
        "category_totals": dict(category_totals),
        "recent_transactions": recent,
        "monthly_trends": dict(sorted(monthly.items())),  
    }
