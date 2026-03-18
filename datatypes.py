# A single transaction — using Python's core data types

transaction_id = 1                        # int
amount = 2500.75                          # float
description = "Grocery Shopping"          # str
is_expense = True                         # bool
tags = ["food", "monthly", "essentials"]  # list
transaction = {                           # dict
    "id": transaction_id,
    "amount": amount,
    "description": description,
    "is_expense": is_expense,
    "tags": tags
}

print(transaction)