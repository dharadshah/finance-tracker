"""Tests for Transaction routes.

Coverage:
    POST   /api/v1/transactions
    POST   /api/v1/transactions/bulk
    GET    /api/v1/transactions
    GET    /api/v1/transactions/{id}
    GET    /api/v1/transactions/filter
    GET    /api/v1/transactions/summary
    GET    /api/v1/transactions/breakdown
    PUT    /api/v1/transactions/{id}
    DELETE /api/v1/transactions/{id}
"""
import pytest
from fastapi.testclient import TestClient


# ============================================================
# POST /api/v1/transactions
# ============================================================

class TestCreateTransaction:
    """Tests for POST /api/v1/transactions."""

    def test_create_transaction_success(self, client: TestClient):
        """Should create a transaction with valid data."""
        response = client.post("/api/v1/transactions", json={
            "description": "Salary",
            "amount"     : 50000,
            "is_expense" : False
        })
        assert response.status_code == 200
        data = response.json()
        assert data["description"]      == "Salary"
        assert data["amount"]           == 50000
        assert data["transaction_type"] == "INCOME"
        assert data["id"] is not None

    def test_create_expense_transaction(self, client: TestClient):
        """Should create an expense transaction correctly."""
        response = client.post("/api/v1/transactions", json={
            "description": "Netflix",
            "amount"     : 649,
            "is_expense" : True
        })
        assert response.status_code == 200
        assert response.json()["transaction_type"] == "EXPENSE"

    def test_create_transaction_with_category(self, client: TestClient, seeded_category):
        """Should create transaction linked to a category."""
        response = client.post("/api/v1/transactions", json={
            "description": "Grocery Shopping",
            "amount"     : 2500,
            "is_expense" : True,
            "category_id": seeded_category["id"]
        })
        assert response.status_code == 200
        data = response.json()
        assert data["category_id"]      == seeded_category["id"]
        assert data["category"]["name"] == "Food"

    def test_create_transaction_negative_amount(self, client: TestClient):
        """Should reject negative amount."""
        response = client.post("/api/v1/transactions", json={
            "description": "Bad Entry",
            "amount"     : -500,
            "is_expense" : True
        })
        assert response.status_code == 422

    def test_create_transaction_zero_amount(self, client: TestClient):
        """Should reject zero amount."""
        response = client.post("/api/v1/transactions", json={
            "description": "Zero Entry",
            "amount"     : 0,
            "is_expense" : True
        })
        assert response.status_code == 422

    def test_create_transaction_empty_description(self, client: TestClient):
        """Should reject empty description."""
        response = client.post("/api/v1/transactions", json={
            "description": "",
            "amount"     : 1000,
            "is_expense" : True
        })
        assert response.status_code == 422

    def test_create_transaction_whitespace_description(self, client: TestClient):
        """Should reject whitespace-only description."""
        response = client.post("/api/v1/transactions", json={
            "description": "   ",
            "amount"     : 1000,
            "is_expense" : True
        })
        assert response.status_code == 422

    def test_create_transaction_missing_amount(self, client: TestClient):
        """Should reject missing amount field."""
        response = client.post("/api/v1/transactions", json={
            "description": "No Amount",
            "is_expense" : True
        })
        assert response.status_code == 422

    def test_create_transaction_missing_is_expense(self, client: TestClient):
        """Should reject missing is_expense field."""
        response = client.post("/api/v1/transactions", json={
            "description": "No Type",
            "amount"     : 1000
        })
        assert response.status_code == 422

    def test_create_transaction_invalid_category_id(self, client: TestClient):
        """Should reject non-existent category id."""
        response = client.post("/api/v1/transactions", json={
            "description": "Bad Category",
            "amount"     : 1000,
            "is_expense" : True,
            "category_id": 99999
        })
        assert response.status_code == 422
        assert response.json()["error"]["code"] == "validation_error"


    def test_create_transaction_formatted_amount(self, client: TestClient):
        """Should return formatted amount in response."""
        response = client.post("/api/v1/transactions", json={
            "description": "Salary",
            "amount"     : 50000,
            "is_expense" : False
        })
        assert response.status_code == 200
        assert response.json()["formatted_amount"] == "Rs.50,000.00"


# ============================================================
# POST /api/v1/transactions/bulk
# ============================================================

class TestBulkCreateTransactions:
    """Tests for POST /api/v1/transactions/bulk."""

    def test_bulk_create_success(self, client: TestClient):
        """Should create multiple transactions at once."""
        response = client.post("/api/v1/transactions/bulk", json={
            "transactions": [
                {"description": "Salary",  "amount": 50000, "is_expense": False},
                {"description": "Grocery", "amount": 2500,  "is_expense": True},
                {"description": "Netflix", "amount": 649,   "is_expense": True}
            ]
        })
        assert response.status_code == 200
        assert len(response.json()) == 3

    def test_bulk_create_empty_list(self, client: TestClient):
        """Should reject empty transactions list."""
        response = client.post("/api/v1/transactions/bulk", json={
            "transactions": []
        })
        assert response.status_code == 422

    def test_bulk_create_exceeds_limit(self, client: TestClient):
        """Should reject more than 100 transactions."""
        transactions = [
            {"description": f"Transaction {i}", "amount": 100, "is_expense": True}
            for i in range(101)
        ]
        response = client.post("/api/v1/transactions/bulk", json={
            "transactions": transactions
        })
        assert response.status_code == 422

    def test_bulk_create_invalid_entry_rejected(self, client: TestClient):
        """Should reject bulk create if any entry is invalid."""
        response = client.post("/api/v1/transactions/bulk", json={
            "transactions": [
                {"description": "Valid",   "amount": 1000,  "is_expense": True},
                {"description": "Invalid", "amount": -500,  "is_expense": True}
            ]
        })
        assert response.status_code == 422


# ============================================================
# GET /api/v1/transactions
# ============================================================

class TestGetTransactions:
    """Tests for GET /api/v1/transactions."""

    def test_get_all_transactions_empty(self, client: TestClient):
        """Should return empty list when no transactions exist."""
        response = client.get("/api/v1/transactions")
        assert response.status_code == 200
        assert response.json() == []

    def test_get_all_transactions_success(self, client: TestClient, created_transaction):
        """Should return list with created transactions."""
        response = client.get("/api/v1/transactions")
        assert response.status_code == 200
        assert len(response.json()) == 1

    def test_get_all_transactions_correct_fields(self, client: TestClient, created_transaction):
        """Each transaction should have required fields."""
        response     = client.get("/api/v1/transactions")
        transactions = response.json()
        for t in transactions:
            assert "id"               in t
            assert "description"      in t
            assert "amount"           in t
            assert "is_expense"       in t
            assert "transaction_type" in t
            assert "formatted_amount" in t


# ============================================================
# GET /api/v1/transactions/{id}
# ============================================================

class TestGetTransactionById:
    """Tests for GET /api/v1/transactions/{id}."""

    def test_get_transaction_by_id_success(self, client: TestClient, created_transaction):
        """Should return transaction by valid id."""
        transaction_id = created_transaction["id"]
        response       = client.get(f"/api/v1/transactions/{transaction_id}")
        assert response.status_code == 200
        assert response.json()["id"] == transaction_id

    def test_get_transaction_not_found(self, client: TestClient):
        """Should return 404 for non-existent transaction."""
        response = client.get("/api/v1/transactions/99999")
        assert response.status_code == 404
        assert response.json()["error"]["code"] == "not_found"

    def test_get_transaction_invalid_id(self, client: TestClient):
        """Should return 422 for non-integer id."""
        response = client.get("/api/v1/transactions/abc")
        assert response.status_code == 422

    def test_get_transaction_zero_id(self, client: TestClient):
        """Should return 404 for id zero."""
        response = client.get("/api/v1/transactions/0")
        assert response.status_code == 404


# ============================================================
# GET /api/v1/transactions/filter
# ============================================================

class TestFilterTransactions:
    """Tests for GET /api/v1/transactions/filter."""

    def test_filter_by_expense(self, client: TestClient):
        """Should return only expense transactions."""
        client.post("/api/v1/transactions", json={
            "description": "Salary",  "amount": 50000, "is_expense": False
        })
        client.post("/api/v1/transactions", json={
            "description": "Netflix", "amount": 649,   "is_expense": True
        })
        response = client.get("/api/v1/transactions/filter?is_expense=true")
        assert response.status_code == 200
        assert all(t["is_expense"] for t in response.json())

    def test_filter_by_income(self, client: TestClient):
        """Should return only income transactions."""
        client.post("/api/v1/transactions", json={
            "description": "Salary",  "amount": 50000, "is_expense": False
        })
        client.post("/api/v1/transactions", json={
            "description": "Netflix", "amount": 649,   "is_expense": True
        })
        response = client.get("/api/v1/transactions/filter?is_expense=false")
        assert response.status_code == 200
        assert all(not t["is_expense"] for t in response.json())

    def test_filter_by_min_amount(self, client: TestClient):
        """Should return only transactions above min amount."""
        client.post("/api/v1/transactions", json={
            "description": "High",  "amount": 10000, "is_expense": True
        })
        client.post("/api/v1/transactions", json={
            "description": "Low",   "amount": 100,   "is_expense": True
        })
        response = client.get("/api/v1/transactions/filter?min_amount=5000")
        assert response.status_code == 200
        assert all(t["amount"] >= 5000 for t in response.json())

    def test_filter_by_max_amount(self, client: TestClient):
        """Should return only transactions below max amount."""
        client.post("/api/v1/transactions", json={
            "description": "High",  "amount": 10000, "is_expense": True
        })
        client.post("/api/v1/transactions", json={
            "description": "Low",   "amount": 100,   "is_expense": True
        })
        response = client.get("/api/v1/transactions/filter?max_amount=500")
        assert response.status_code == 200
        assert all(t["amount"] <= 500 for t in response.json())

    def test_filter_pagination_limit(self, client: TestClient):
        """Should respect limit query parameter."""
        for i in range(5):
            client.post("/api/v1/transactions", json={
                "description": f"Transaction {i}", "amount": 100, "is_expense": True
            })
        response = client.get("/api/v1/transactions/filter?limit=3")
        assert response.status_code == 200
        assert len(response.json()) == 3

    def test_filter_pagination_offset(self, client: TestClient):
        """Should respect offset query parameter."""
        for i in range(5):
            client.post("/api/v1/transactions", json={
                "description": f"Transaction {i}", "amount": 100, "is_expense": True
            })
        response_p1 = client.get("/api/v1/transactions/filter?limit=3&offset=0")
        response_p2 = client.get("/api/v1/transactions/filter?limit=3&offset=3")
        assert response_p1.status_code == 200
        assert response_p2.status_code == 200
        ids_p1 = [t["id"] for t in response_p1.json()]
        ids_p2 = [t["id"] for t in response_p2.json()]
        assert not set(ids_p1) & set(ids_p2)

    def test_filter_limit_exceeds_max(self, client: TestClient):
        """Should reject limit above 100."""
        response = client.get("/api/v1/transactions/filter?limit=101")
        assert response.status_code == 422

    def test_filter_negative_offset(self, client: TestClient):
        """Should reject negative offset."""
        response = client.get("/api/v1/transactions/filter?offset=-1")
        assert response.status_code == 422


# ============================================================
# GET /api/v1/transactions/summary
# ============================================================

class TestGetSummary:
    """Tests for GET /api/v1/transactions/summary."""

    def test_summary_empty_database(self, client: TestClient):
        """Should return zero values when no transactions exist."""
        response = client.get("/api/v1/transactions/summary")
        assert response.status_code == 200
        data = response.json()
        assert data["total_income"]    == 0
        assert data["total_expenses"]  == 0
        assert data["balance"]         == 0
        assert data["savings_rate"]    == 0

    def test_summary_with_transactions(self, client: TestClient):
        """Should return correct summary values."""
        client.post("/api/v1/transactions", json={
            "description": "Salary",  "amount": 50000, "is_expense": False
        })
        client.post("/api/v1/transactions", json={
            "description": "Grocery", "amount": 2500,  "is_expense": True
        })
        response = client.get("/api/v1/transactions/summary")
        assert response.status_code == 200
        data = response.json()
        assert data["total_income"]   == 50000
        assert data["total_expenses"] == 2500
        assert data["balance"]        == 47500

    def test_summary_savings_rate_calculation(self, client: TestClient):
        """Should calculate savings rate correctly."""
        client.post("/api/v1/transactions", json={
            "description": "Salary",  "amount": 100000, "is_expense": False
        })
        client.post("/api/v1/transactions", json={
            "description": "Expense", "amount": 20000,  "is_expense": True
        })
        response = client.get("/api/v1/transactions/summary")
        assert response.status_code == 200
        assert response.json()["savings_rate"] == 80.0

    def test_summary_required_fields(self, client: TestClient):
        """Summary response should contain all required fields."""
        response = client.get("/api/v1/transactions/summary")
        data     = response.json()
        assert "total_income"       in data
        assert "total_expenses"     in data
        assert "balance"            in data
        assert "savings_rate"       in data
        assert "transaction_count"  in data


# ============================================================
# GET /api/v1/transactions/breakdown
# ============================================================

class TestGetBreakdown:
    """Tests for GET /api/v1/transactions/breakdown."""

    def test_breakdown_empty_database(self, client: TestClient):
        """Should return empty list when no transactions exist."""
        response = client.get("/api/v1/transactions/breakdown")
        assert response.status_code == 200
        assert response.json() == []

    def test_breakdown_with_categories(self, client: TestClient, seeded_category):
        """Should return breakdown grouped by category."""
        client.post("/api/v1/transactions", json={
            "description": "Grocery",
            "amount"     : 2500,
            "is_expense" : True,
            "category_id": seeded_category["id"]
        })
        response = client.get("/api/v1/transactions/breakdown")
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0
        assert "category"          in data[0]
        assert "transaction_count" in data[0]
        assert "total_amount"      in data[0]
        assert "avg_amount"        in data[0]


# ============================================================
# PUT /api/v1/transactions/{id}
# ============================================================

class TestUpdateTransaction:
    """Tests for PUT /api/v1/transactions/{id}."""

    def test_update_transaction_success(self, client: TestClient, created_transaction):
        """Should update transaction with valid data."""
        transaction_id = created_transaction["id"]
        response = client.put(f"/api/v1/transactions/{transaction_id}", json={
            "description": "Updated Description",
            "amount"     : 2000,
            "is_expense" : True
        })
        assert response.status_code == 200
        data = response.json()
        assert data["description"] == "Updated Description"
        assert data["amount"]      == 2000

    def test_update_transaction_not_found(self, client: TestClient):
        """Should return 404 for non-existent transaction."""
        response = client.put("/api/v1/transactions/99999", json={
            "description": "Updated",
            "amount"     : 1000,
            "is_expense" : True
        })
        assert response.status_code == 404

    def test_update_transaction_negative_amount(self, client: TestClient, created_transaction):
        """Should reject negative amount on update."""
        transaction_id = created_transaction["id"]
        response = client.put(f"/api/v1/transactions/{transaction_id}", json={
            "description": "Updated",
            "amount"     : -500,
            "is_expense" : True
        })
        assert response.status_code == 422

    def test_update_transaction_empty_description(self, client: TestClient, created_transaction):
        """Should reject empty description on update."""
        transaction_id = created_transaction["id"]
        response = client.put(f"/api/v1/transactions/{transaction_id}", json={
            "description": "",
            "amount"     : 1000,
            "is_expense" : True
        })
        assert response.status_code == 422

    def test_update_transaction_change_type(self, client: TestClient, created_transaction):
        """Should allow changing transaction type."""
        transaction_id = created_transaction["id"]
        response = client.put(f"/api/v1/transactions/{transaction_id}", json={
            "description": "Now Income",
            "amount"     : 1000,
            "is_expense" : False
        })
        assert response.status_code == 200
        assert response.json()["transaction_type"] == "INCOME"

    def test_update_transaction_with_category(
        self, client: TestClient, created_transaction, seeded_category
    ):
        """Should allow updating transaction category."""
        transaction_id = created_transaction["id"]
        response = client.put(f"/api/v1/transactions/{transaction_id}", json={
            "description": "Updated",
            "amount"     : 1000,
            "is_expense" : True,
            "category_id": seeded_category["id"]
        })
        assert response.status_code == 200
        assert response.json()["category"]["name"] == "Food"


# ============================================================
# DELETE /api/v1/transactions/{id}
# ============================================================

class TestDeleteTransaction:
    """Tests for DELETE /api/v1/transactions/{id}."""

    def test_delete_transaction_success(self, client: TestClient, created_transaction):
        """Should delete an existing transaction."""
        transaction_id = created_transaction["id"]
        response       = client.delete(f"/api/v1/transactions/{transaction_id}")
        assert response.status_code == 200
        assert "deleted" in response.json()["message"].lower()

    def test_delete_transaction_not_found(self, client: TestClient):
        """Should return 404 for non-existent transaction."""
        response = client.delete("/api/v1/transactions/99999")
        assert response.status_code == 404
        assert response.json()["error"]["code"] == "not_found"

    def test_delete_transaction_already_deleted(self, client: TestClient, created_transaction):
        """Should return 404 when deleting already deleted transaction."""
        transaction_id = created_transaction["id"]
        client.delete(f"/api/v1/transactions/{transaction_id}")
        response = client.delete(f"/api/v1/transactions/{transaction_id}")
        assert response.status_code == 404

    def test_deleted_transaction_not_accessible(self, client: TestClient, created_transaction):
        """Should not be accessible after deletion."""
        transaction_id = created_transaction["id"]
        client.delete(f"/api/v1/transactions/{transaction_id}")
        response = client.get(f"/api/v1/transactions/{transaction_id}")
        assert response.status_code == 404

    def test_delete_transaction_invalid_id(self, client: TestClient):
        """Should return 422 for non-integer id."""
        response = client.delete("/api/v1/transactions/abc")
        assert response.status_code == 422