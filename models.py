class Transaction:
    def __init__(self, description, amount, is_expense):
        self.description = description
        self.amount = amount
        self.is_expense = is_expense

    def display(self):
        label = "EXPENSE" if self.is_expense else "INCOME "
        print(f"{label} | {self.description:20} | Rs.{self.amount:>10.2f}")


if __name__ == "__main__":
    t1 = Transaction("Salary", 50000, False)
    t2 = Transaction("Netflix", 649, True)

    t1.display()
    t2.display()