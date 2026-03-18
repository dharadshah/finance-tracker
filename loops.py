transactions = [
    {"description": "Salary",           "amount": 50000, "is_expense": False},
    {"description": "Grocery Shopping", "amount": 2500,  "is_expense": True},
    {"description": "Netflix",          "amount": 649,   "is_expense": True},
    {"description": "Freelance Work",   "amount": 15000, "is_expense": False},
    {"description": "Electricity Bill", "amount": 1800,  "is_expense": True},
]

for t in transactions:
    if t["is_expense"]:
        print(f"EXPENSE  | {t['description']:20} | Rs.{t['amount']:>10}")

    else:
        print(f"INCOME   | {t['description']:20} | Rs.{t['amount']:>10}")



total_income = 0
total_expense = 0

for t in transactions:
    if t["is_expense"]:
        total_expense += t["amount"]
    else:
        total_income += t["amount"]

balance = total_income - total_expense

print(f"\nSummary")
print(f"Total Income  : ₹{total_income:>10}")
print(f"Total Expense : ₹{total_expense:>10}")
print(f"Balance       : ₹{balance:>10}")