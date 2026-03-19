class Transaction:
    def __init__(self, description, amount, is_expense):
        self.description = description
        self.is_expense = is_expense
        self.amount = amount  # this calls the setter below

    # Encapsulation
    @property
    def amount(self):
        return self._amount

    @amount.setter
    def amount(self, value):
        if value < 0:
            raise ValueError("Amount cannot be negative")
        self._amount = value

    def display(self):
        label = "EXPENSE" if self.is_expense else "INCOME "
        print(f"{label} | {self.description:20} | Rs.{self.amount:>10.2f}")

class Income(Transaction):
    def __init__(self, description, amount):
        super().__init__(description, amount, is_expense=False)

    def summary(self):
        return f"Income of Rs.{self.amount:.2f} from {self.description}"


class Expense(Transaction):
    def __init__(self, description, amount):
        super().__init__(description, amount, is_expense=True)

    def summary(self):
        return f"Spent Rs.{self.amount:.2f} on {self.description}"


if __name__ == "__main__":
    transactions = [
        Income("Salary", 50000),
        Expense("Netflix", 649),
        Expense("Grocery Shopping", 2500),
        Income("Freelance Work", 15000),
    ]

    for t in transactions:
        print(t.summary())   # calls the right summary() based on type
        t.display()
