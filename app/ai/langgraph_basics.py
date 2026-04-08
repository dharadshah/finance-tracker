import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langgraph.graph import StateGraph, END
from typing import TypedDict

load_dotenv()

llm = ChatGroq(
    api_key=os.getenv("GROQ_API_KEY"),
    model="llama-3.3-70b-versatile"
)

output_parser = StrOutputParser()


# --- Step 1: Define State ---
# State is the shared data structure passed between all nodes

class TransactionState(TypedDict):
    description    : str
    amount         : float
    classification : str       # filled by classify_node
    category       : str       # filled by analyse_node
    risk_level     : str       # filled by analyse_node
    insight        : str       # filled by insight_node
    is_expense     : bool      # filled by classify_node


# --- Step 2: Define Nodes ---
# Each node is a function that receives state and returns updated state

def classify_node(state: TransactionState) -> dict:
    print(f"  classify_node: classifying '{state['description']}'")

    prompt = ChatPromptTemplate.from_messages([
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

    chain  = prompt | llm | output_parser
    result = chain.invoke({"transaction": state["description"]})

    # Sanitize output
    classification = "INCOME" if "INCOME" in result.upper() else "EXPENSE"
    is_expense     = classification == "EXPENSE"

    return {
        "classification": classification,
        "is_expense"     : is_expense
    }


def analyse_node(state: TransactionState) -> dict:
    print(f"  analyse_node: analysing '{state['description']}'")

    prompt = ChatPromptTemplate.from_messages([
        ("system", """
You are a financial analyst.
Always return valid JSON with no extra text.
"""),
        ("human", """
Analyse this transaction:
Description : {description}
Amount      : Rs.{amount}
Type        : {classification}

Return JSON with exactly these keys: category, risk_level
Values for risk_level: Low, Medium, High
""")
    ])

    chain  = prompt | llm | output_parser
    result = chain.invoke({
        "description"    : state["description"],
        "amount"         : state["amount"],
        "classification" : state["classification"]
    })

    cleaned = result.strip().replace("```json", "").replace("```", "")
    parsed  = json.loads(cleaned)

    return {
        "category"  : parsed.get("category", "Uncategorized"),
        "risk_level": parsed.get("risk_level", "Low")
    }


def insight_node(state: TransactionState) -> dict:
    print(f"  insight_node: generating insight for '{state['description']}'")

    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a financial advisor. Give one concise actionable tip in one sentence."),
        ("human", """
Transaction : {description}
Amount      : Rs.{amount}
Type        : {classification}
Category    : {category}
Risk Level  : {risk_level}

Give one actionable tip.
""")
    ])

    chain  = prompt | llm | output_parser
    result = chain.invoke({
        "description"    : state["description"],
        "amount"         : state["amount"],
        "classification" : state["classification"],
        "category"       : state["category"],
        "risk_level"     : state["risk_level"]
    })

    return {"insight": result.strip()}


# --- Step 3: Conditional Edge ---
# Route to different nodes based on classification

def route_by_classification(state: TransactionState) -> str:
    if state["classification"] == "INCOME":
        print("  routing to: insight_node (income does not need risk analysis)")
        return "insight_node"
    else:
        print("  routing to: analyse_node (expense needs risk analysis)")
        return "analyse_node"


# --- Step 4: Build the Graph ---

graph_builder = StateGraph(TransactionState)

# Add nodes
graph_builder.add_node("classify_node", classify_node)
graph_builder.add_node("analyse_node",  analyse_node)
graph_builder.add_node("insight_node",  insight_node)

# Set entry point
graph_builder.set_entry_point("classify_node")

# Add conditional edge after classification
graph_builder.add_conditional_edges(
    "classify_node",
    route_by_classification,
    {
        "analyse_node" : "analyse_node",
        "insight_node" : "insight_node"
    }
)

# analyse_node always goes to insight_node
graph_builder.add_edge("analyse_node", "insight_node")

# insight_node ends the graph
graph_builder.add_edge("insight_node", END)

# Compile the graph
graph = graph_builder.compile()


# --- Step 5: Run the Graph ---

if __name__ == "__main__":

    # Test with an EXPENSE
    print("\n" + "=" * 60)
    print("TEST 1 - Expense Transaction")
    print("=" * 60)

    result = graph.invoke({
        "description"    : "Netflix subscription renewed",
        "amount"         : 649,
        "classification" : "",
        "category"       : "",
        "risk_level"     : "",
        "insight"        : "",
        "is_expense"     : False
    })

    print(f"\n  Classification : {result['classification']}")
    print(f"  Category       : {result['category']}")
    print(f"  Risk Level     : {result['risk_level']}")
    print(f"  Insight        : {result['insight']}")

    # Test with an INCOME
    print("\n" + "=" * 60)
    print("TEST 2 - Income Transaction")
    print("=" * 60)

    result = graph.invoke({
        "description"    : "Received salary for March",
        "amount"         : 50000,
        "classification" : "",
        "category"       : "",
        "risk_level"     : "",
        "insight"        : "",
        "is_expense"     : False
    })

    print(f"\n  Classification : {result['classification']}")
    print(f"  Category       : {result['category']}")
    print(f"  Risk Level     : {result['risk_level']}")
    print(f"  Insight        : {result['insight']}")