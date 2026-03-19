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


class Category:
    def __init__(self, name):
        self.name = name
        self.transactions = []

    def add_transaction(self, transaction):
        self.transactions.append(transaction)

    def total(self):
        return sum(t.amount for t in self.transactions)

    def display(self):
        print(f"\nCategory: {self.name}")
        for t in self.transactions:
            t.display()
        print(f"Total: Rs.{self.total():>10.2f}")


if __name__ == "__main__":
    food = Category("Food")
    food.add_transaction(Expense("Grocery Shopping", 2500))
    food.add_transaction(Expense("Restaurant", 800))
    food.display()
