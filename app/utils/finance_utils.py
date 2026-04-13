import logging
from app.constants.app_constants import SAVINGS_RATE

logger = logging.getLogger("app.models.transaction")


def calculate_savings_rate(total_income: float, total_expenses: float) -> float:
    if total_income == 0:
        return 0.0
    savings      = total_income - total_expenses
    savings_rate = (savings / total_income) * 100
    return round(savings_rate, 2)


def format_currency(amount: float) -> str:
    return f"Rs.{amount:,.2f}"


def classify_savings_rate(rate: float) -> str:
    if rate >= SAVINGS_RATE.EXCELLENT.value:
        return "Excellent"
    elif rate >= SAVINGS_RATE.GOOD.value:
        return "Good"
    elif rate >= SAVINGS_RATE.AVERAGE.value:
        return "Average"
    return "Poor"