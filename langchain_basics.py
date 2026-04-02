import os
import json
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

# --- Part 1: Connect to LLM ---
llm = ChatGroq(
    api_key=os.getenv("GROQ_API_KEY"),
    model="llama-3.3-70b-versatile"
)

# --- Part 2: Prompt Templates ---
prompt_template = ChatPromptTemplate.from_messages([
    ("system", "You are a financial assistant. Reply with only one word: INCOME or EXPENSE."),
    ("human", """
Examples:
Transaction: "Monthly salary credited"     -> INCOME
Transaction: "Paid electricity bill"       -> EXPENSE
Transaction: "Received freelance payment"  -> INCOME
Transaction: "Grocery shopping at D-Mart"  -> EXPENSE

Now classify:
Transaction: "{transaction}"              ->
""")
])

formatted = prompt_template.format_messages(transaction="Monthly salary credited")
print("Formatted Prompt:")
for msg in formatted:
    print(f"  {msg.type}: {msg.content}")
print()

# --- Chain = Prompt | LLM | Output Parser ---
output_parser = StrOutputParser()

classification_chain = prompt_template | llm | output_parser

result = classification_chain.invoke({
    "transaction": "Received salary for March"
})
print("Chain Result:")
print(result)
print()

# --- Multi-variable Template ---
analysis_template = ChatPromptTemplate.from_messages([
    ("system", """
You are a financial analyst for a Personal Finance Tracker.
Always return your response as valid JSON with no extra text.
"""),
    ("human", """
Analyse this transaction:
Description : {description}
Amount      : Rs.{amount}
Type        : {transaction_type}

Return JSON with keys: category, risk_level, suggestion
""")
])

analysis_chain = analysis_template | llm | output_parser

result = analysis_chain.invoke({
    "description"      : "Netflix subscription",
    "amount"           : 649,
    "transaction_type" : "EXPENSE"
})

print("Analysis Chain Result:")
print(result)
print()

# --- Summary Chain ---
summary_template = ChatPromptTemplate.from_messages([
    ("system", """
You are a financial analyst assistant for a Personal Finance Tracker.
Always return valid JSON in this exact format with no extra text:
{{
    "total_income": 0,
    "total_expenses": 0,
    "balance": 0,
    "savings_rate": 0,
    "largest_expense_category": "",
    "insight": ""
}}
"""),
    ("human", "Analyse these transactions: {transactions}")
])

summary_chain = summary_template | llm | output_parser

transactions = [
    {"description": "Salary",           "amount": 50000, "is_expense": False, "category": "Income"},
    {"description": "Grocery Shopping", "amount": 2500,  "is_expense": True,  "category": "Food"},
    {"description": "Netflix",          "amount": 649,   "is_expense": True,  "category": "Entertainment"},
    {"description": "Electricity Bill", "amount": 1800,  "is_expense": True,  "category": "Utilities"},
    {"description": "Freelance Work",   "amount": 15000, "is_expense": False, "category": "Income"},
    {"description": "Rent",             "amount": 12000, "is_expense": True,  "category": "Housing"},
]

result = summary_chain.invoke({"transactions": transactions})

print("Summary Chain Result:")
print(result)

cleaned = result.strip().replace("```json", "").replace("```", "")
parsed  = json.loads(cleaned)
print("\nParsed JSON:")
for key, value in parsed.items():
    print(f"  {key}: {value}")