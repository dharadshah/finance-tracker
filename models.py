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

if __name__ == "__main__":
    t1 = Transaction("Salary", 50000, False)
    t2 = Transaction("Netflix", 649, True)
    t = Transaction("Test", -100, True)  # should raise ValueError
    
    t1.display()
    t2.display()