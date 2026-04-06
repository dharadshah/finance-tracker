import logging

logger = logging.getLogger(__name__)

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
        if value > 100000:
            logger.warning(f"Unusually high amount entered: Rs.{value} for {self.description}")
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
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.FileHandler("finance_tracker.log"),
            logging.StreamHandler()           # this keeps terminal output as well
        ]
    )
    # Test normal transaction
    try:
        t1 = Transaction("Salary", 50000, False)
        t1.display()
        logger.info(f"Transaction created: {t1.description}")
    except ValueError as e:
        logger.error(f"Failed to create transaction: {e}")

    # Test negative amount
    try:
        t2 = Transaction("Bad Entry", -500, True)
        t2.display()
    except ValueError as e:
        logger.error(f"Failed to create transaction: {e}")

    # Test high amount warning
    try:
        t3 = Transaction("Luxury Car", 200000, True)
        t3.display()
    except ValueError as e:
        logger.error(f"Failed to create transaction: {e}")


