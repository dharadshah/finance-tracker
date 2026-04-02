import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def call_groq(system_prompt, user_prompt):
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_prompt}
        ]
    )
    return response.choices[0].message.content


# Sample transactions from our Finance Tracker
transactions = [
    {"description": "Salary",           "amount": 50000, "is_expense": False, "category": "Income"},
    {"description": "Grocery Shopping", "amount": 2500,  "is_expense": True,  "category": "Food"},
    {"description": "Netflix",          "amount": 649,   "is_expense": True,  "category": "Entertainment"},
    {"description": "Electricity Bill", "amount": 1800,  "is_expense": True,  "category": "Utilities"},
    {"description": "Freelance Work",   "amount": 15000, "is_expense": False, "category": "Income"},
    {"description": "Rent",             "amount": 12000, "is_expense": True,  "category": "Housing"},
]


# --- Test 1: Zero-shot ---
def test_zero_shot():
    print("\n" + "=" * 60)
    print("TEST 1 - Zero-shot Prompting")
    print("=" * 60)

    system = "You are a financial assistant."
    user   = f"Analyze these transactions: {transactions}"

    response = call_groq(system, user)
    print(response)


# --- Test 2: Few-shot ---
def test_few_shot():
    print("\n" + "=" * 60)
    print("TEST 2 - Few-shot Prompting")
    print("=" * 60)

    system = "You are a financial assistant."
    user   = """
Extract transaction details and return as JSON.

Examples:
Input:  "Paid Rs.2500 for groceries at D-Mart"
Output: {"description": "Groceries at D-Mart", "amount": 2500, "is_expense": true, "category": "Food"}

Input:  "Received Rs.50000 salary for March"
Output: {"description": "Salary March", "amount": 50000, "is_expense": false, "category": "Income"}

Now extract:
Input:  "Netflix subscription renewed for Rs.649"
Output:
"""

    response = call_groq(system, user)
    print(response)


# --- Test 3: Chain of Thought ---
def test_chain_of_thought():
    print("\n" + "=" * 60)
    print("TEST 3 - Chain of Thought Prompting")
    print("=" * 60)

    system = "You are a financial analyst assistant."
    user   = f"""
Given these transactions:
{transactions}

Think step by step:
1. Calculate total income
2. Calculate total expenses
3. Calculate savings
4. Calculate savings rate
5. Identify the largest expense category
6. Give one actionable recommendation

Then provide your final summary.
"""

    response = call_groq(system, user)
    print(response)


# --- Test 4: Structured System Prompt + JSON Output ---
def test_structured_output():
    print("\n" + "=" * 60)
    print("TEST 4 - Structured System Prompt with JSON Output")
    print("=" * 60)

    system = """
You are a financial analyst assistant for a Personal Finance
Tracker API. Your job is to analyse transaction data and provide
clear, actionable financial insights.

Always base your analysis on the actual transaction data provided.
Never make assumptions about transactions not in the data.
Always return your response as valid JSON in this exact format with no extra text:
{
    "total_income": 0,
    "total_expenses": 0,
    "balance": 0,
    "savings_rate": 0,
    "largest_expense_category": "",
    "insight": ""
}
Keep the insight concise - maximum 2 sentences.
"""

    user = f"Analyse these transactions and return the JSON summary: {transactions}"

    response = call_groq(system, user)
    print(response)


if __name__ == "__main__":
    test_zero_shot()
    test_few_shot()
    test_chain_of_thought()
    test_structured_output()