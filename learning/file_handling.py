import json

transactions = [
    {"description": "Salary",           "amount": 50000, "is_expense": False},
    {"description": "Grocery Shopping", "amount": 2500,  "is_expense": True},
    {"description": "Netflix",          "amount": 649,   "is_expense": True},
    {"description": "Freelance Work",   "amount": 15000, "is_expense": False},
    {"description": "Electricity Bill", "amount": 1800,  "is_expense": True},
]

# Write to a JSON file
with open("transactions.json", "w") as f:
    json.dump(transactions, f, indent=4)

print("Transactions saved.")

# Read from the JSON file
with open("transactions.json", "r") as f:
    loaded = json.load(f)

for t in loaded:
    label = "EXPENSE" if t["is_expense"] else "INCOME "
    print(f"{label} | {t['description']:20} | Rs.{t['amount']:>10.2f}")


new_transaction = {"description": "Gym Membership", "amount": 1200, "is_expense": True}

# Read existing
with open("transactions.json", "r") as f:
    existing = json.load(f)

# Append new
existing.append(new_transaction)

# Write back
with open("transactions.json", "w") as f:
    json.dump(existing, f, indent=4)

print("New transaction added.")

with open("transactions.json", "r") as f:
    loaded = json.load(f)

for t in loaded:
    label = "EXPENSE" if t["is_expense"] else "INCOME "
    print(f"{label} | {t['description']:20} | Rs.{t['amount']:>10.2f}")

