import pytest
from models import Transaction, Income, Expense, Category


# --- Transaction Tests ---

def test_transaction_creation():
    t = Transaction("Salary", 50000, False)
    assert t.description == "Salary"
    assert t.amount == 50000
    assert t.is_expense == False


def test_transaction_negative_amount_raises_error():
    with pytest.raises(ValueError):
        Transaction("Bad Entry", -500, True)


def test_transaction_high_amount_is_allowed():
    t = Transaction("Luxury Car", 200000, True)
    assert t.amount == 200000          


# --- Income Tests ---

def test_income_is_not_expense():
    income = Income("Freelance", 15000)
    assert income.is_expense == False


def test_income_summary():
    income = Income("Salary", 50000)
    assert "50000" in income.summary()
    assert "Salary" in income.summary()


# --- Expense Tests ---

def test_expense_is_expense():
    expense = Expense("Netflix", 649)
    assert expense.is_expense == True


def test_expense_summary():
    expense = Expense("Netflix", 649)
    assert "649" in expense.summary()
    assert "Netflix" in expense.summary()


# --- Category Tests ---

def test_category_total():
    food = Category("Food")
    food.add_transaction(Expense("Grocery", 2500))
    food.add_transaction(Expense("Restaurant", 800))
    assert food.total() == 3300


def test_category_empty_total():
    empty = Category("Empty")
    assert empty.total() == 0