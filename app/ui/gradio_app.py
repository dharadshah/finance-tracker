import time
import gradio as gr
import requests

API_URL = "http://127.0.0.1:8000"

time.sleep(2)


def add_transaction(description, amount, is_expense, category):
    payload = {
        "description": description,
        "amount": float(amount),
        "is_expense": is_expense,
        "category": category if category else None
    }
    response = requests.post(f"{API_URL}/transactions", json=payload)
    if response.status_code == 200:
        data = response.json()
        return f"Transaction created successfully with id: {data['id']}"
    return f"Error: {response.json()['detail']}"


def get_all_transactions():
    response = requests.get(f"{API_URL}/transactions")
    if response.status_code == 200:
        transactions = response.json()
        if not transactions:
            return "No transactions found"
        result = f"{'ID':<5} {'Type':<10} {'Description':<25} {'Category':<15} {'Amount':>10}\n"
        result += "-" * 70 + "\n"
        for t in transactions:
            label = "EXPENSE" if t["is_expense"] else "INCOME"
            result += f"{t['id']:<5} {label:<10} {t['description']:<25} {str(t['category'] or ''):<15} Rs.{t['amount']:>10.2f}\n"
        return result
    return f"Error: {response.json()}"


def delete_transaction(transaction_id):
    response = requests.delete(f"{API_URL}/transactions/{int(transaction_id)}")
    if response.status_code == 200:
        return f"Transaction {transaction_id} deleted successfully"
    return f"Error: {response.json()['detail']}"


# --- Build UI ---

with gr.Blocks(title="Personal Finance Tracker") as app:
    gr.Markdown("# Personal Finance Tracker")

    # Add Transaction Tab
    with gr.Tab("Add Transaction"):
        gr.Markdown("### Add a new transaction")
        description = gr.Textbox(label="Description")
        amount      = gr.Number(label="Amount (Rs.)")
        is_expense  = gr.Checkbox(label="Is Expense?", value=True)
        category    = gr.Textbox(label="Category (optional)")
        add_btn     = gr.Button("Add Transaction")
        add_output  = gr.Textbox(label="Result")

        add_btn.click(
            fn=add_transaction,
            inputs=[description, amount, is_expense, category],
            outputs=add_output
        )

    # View Transactions Tab
    with gr.Tab("View Transactions"):
        gr.Markdown("### All Transactions")
        view_btn    = gr.Button("Fetch Transactions")
        view_output = gr.Textbox(label="Transactions", lines=15)

        view_btn.click(
            fn=get_all_transactions,
            inputs=[],
            outputs=view_output
        )

    # Delete Transaction Tab
    with gr.Tab("Delete Transaction"):
        gr.Markdown("### Delete a transaction by ID")
        delete_id     = gr.Number(label="Transaction ID")
        delete_btn    = gr.Button("Delete Transaction")
        delete_output = gr.Textbox(label="Result")

        delete_btn.click(
            fn=delete_transaction,
            inputs=[delete_id],
            outputs=delete_output
        )


if __name__ == "__main__":
    app.launch()