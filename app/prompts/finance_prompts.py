CLASSIFY_TRANSACTION_PROMPT = """
Examples:
Transaction: "Monthly salary credited"     -> INCOME
Transaction: "Paid electricity bill"       -> EXPENSE
Transaction: "Received freelance payment"  -> INCOME
Transaction: "Grocery shopping at D-Mart"  -> EXPENSE

Now classify:
Transaction: "{transaction}"              ->
"""

ANALYSE_TRANSACTION_PROMPT = """
Analyse this transaction:
Description : {description}
Amount      : Rs.{amount}
Type        : {classification}

Return JSON with exactly these keys: category, risk_level
Values for risk_level: Low, Medium, High
"""

SUMMARISE_TRANSACTIONS_PROMPT = """
Analyse these transactions and return the JSON summary: {transactions}
"""

ANALYSE_TRANSACTIONS_SYSTEM = """
You are a financial analyst assistant for a Personal Finance Tracker API.
Always return valid JSON in this exact format with no extra text:
{{
    "total_income": 0,
    "total_expenses": 0,
    "balance": 0,
    "savings_rate": 0,
    "largest_expense_category": "",
    "insight": ""
}}
"""