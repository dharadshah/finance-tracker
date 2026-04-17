"""Application constants: environment, model config, route paths, finance rules."""
from enum import Enum


class Environment(Enum):
    """Environment names."""
    LOCAL = "local"
    DEV   = "dev"
    PROD  = "prod"


class GROQ_CHAT_MODEL(Enum):
    """Groq LLM configuration."""
    MODEL_NAME  = "llama-3.3-70b-versatile"
    TEMPERATURE = 0.0


class GEMINI_CHAT_MODEL(Enum):
    """Gemini LLM configuration."""
    MODEL_NAME  = "gemini-1.5-flash"
    TEMPERATURE = 0.0


class ROUTE_CONSTANTS(Enum):
    """API route prefix constants."""
    API_V1_PREFIX        = "/api/v1"
    TRANSACTIONS_PREFIX  = "/api/v1/transactions"
    CATEGORIES_PREFIX    = "/api/v1/categories"
    AI_PREFIX            = "/api/v1/ai"


class TRANSACTION_TYPE(Enum):
    """Transaction classification types."""
    INCOME  = "INCOME"
    EXPENSE = "EXPENSE"


class RISK_LEVEL(Enum):
    """Risk levels for expense transactions."""
    LOW    = "Low"
    MEDIUM = "Medium"
    HIGH   = "High"


class SAVINGS_RATE(Enum):
    """Savings rate thresholds as percentages."""
    EXCELLENT = 30
    GOOD      = 20
    AVERAGE   = 10
    POOR      = 0


class DEFAULT_CATEGORIES(Enum):
    """Default transaction categories."""
    FOOD          = "Food"
    HOUSING       = "Housing"
    TRANSPORT     = "Transport"
    ENTERTAINMENT = "Entertainment"
    UTILITIES     = "Utilities"
    HEALTHCARE    = "Healthcare"
    INCOME        = "Income"
    SAVINGS       = "Savings"
    EDUCATION     = "Education"
    OTHER         = "Other"


class AI_RESPONSE_KEYS(Enum):
    """Expected keys in AI analysis response."""
    TOTAL_INCOME              = "total_income"
    TOTAL_EXPENSES            = "total_expenses"
    BALANCE                   = "balance"
    SAVINGS_RATE              = "savings_rate"
    LARGEST_EXPENSE_CATEGORY  = "largest_expense_category"
    INSIGHT                   = "insight"