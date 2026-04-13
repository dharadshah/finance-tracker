"""Tests for Category routes.

Coverage:
    POST   /api/v1/categories
    GET    /api/v1/categories
    GET    /api/v1/categories/{id}
    DELETE /api/v1/categories/{id}
"""
import pytest
from fastapi.testclient import TestClient


# ============================================================
# POST /api/v1/categories
# ============================================================

class TestCreateCategory:
    """Tests for POST /api/v1/categories."""

    def test_create_category_success(self, client: TestClient):
        """Should create a category with valid data."""
        response = client.post("/api/v1/categories", json={
            "name"       : "Test Food",
            "description": "Food and groceries"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["name"]        == "Test Food"
        assert data["description"] == "Food and groceries"
        assert data["id"] is not None

    def test_create_category_without_description(self, client: TestClient):
        """Should create a category without optional description."""
        response = client.post("/api/v1/categories", json={
            "name": "Test No Description"
        })
        assert response.status_code == 200
        assert response.json()["description"] is None

    def test_create_category_duplicate_name(self, client: TestClient):
        """Should reject duplicate category name."""
        client.post("/api/v1/categories", json={"name": "Test Duplicate"})
        response = client.post("/api/v1/categories", json={"name": "Test Duplicate"})
        assert response.status_code == 409
        assert response.json()["error"]["code"] == "conflict"

    def test_create_category_empty_name(self, client: TestClient):
        """Should reject empty category name."""
        response = client.post("/api/v1/categories", json={"name": ""})
        assert response.status_code == 422

    def test_create_category_whitespace_name(self, client: TestClient):
        """Should reject whitespace-only category name."""
        response = client.post("/api/v1/categories", json={"name": "   "})
        assert response.status_code == 422

    def test_create_category_missing_name(self, client: TestClient):
        """Should reject request with missing name field."""
        response = client.post("/api/v1/categories", json={
            "description": "No name provided"
        })
        assert response.status_code == 422

    def test_create_category_name_too_long(self, client: TestClient):
        """Should reject name exceeding max length."""
        response = client.post("/api/v1/categories", json={
            "name": "A" * 101
        })
        assert response.status_code == 422

    def test_create_seeded_category_conflict(self, client: TestClient):
        """Should reject creating a category that was already seeded."""
        response = client.post("/api/v1/categories", json={"name": "Food"})
        assert response.status_code == 409


# ============================================================
# GET /api/v1/categories
# ============================================================

class TestGetCategories:
    """Tests for GET /api/v1/categories."""

    def test_get_all_categories_success(self, client: TestClient):
        """Should return list of all categories."""
        response = client.get("/api/v1/categories")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_get_all_categories_includes_seeded(self, client: TestClient):
        """Should include default seeded categories."""
        response  = client.get("/api/v1/categories")
        names     = [c["name"] for c in response.json()]
        assert "Food"     in names
        assert "Housing"  in names
        assert "Income"   in names

    def test_get_all_categories_returns_correct_fields(self, client: TestClient):
        """Each category should have id, name, description."""
        response   = client.get("/api/v1/categories")
        categories = response.json()
        assert len(categories) > 0
        for category in categories:
            assert "id"          in category
            assert "name"        in category
            assert "description" in category


# ============================================================
# GET /api/v1/categories/{id}
# ============================================================

class TestGetCategoryById:
    """Tests for GET /api/v1/categories/{id}."""

    def test_get_category_by_id_success(self, client: TestClient, created_category):
        """Should return category by valid id."""
        category_id = created_category["id"]
        response    = client.get(f"/api/v1/categories/{category_id}")
        assert response.status_code == 200
        assert response.json()["id"]   == category_id
        assert response.json()["name"] == "Test Category"

    def test_get_category_not_found(self, client: TestClient):
        """Should return 404 for non-existent category id."""
        response = client.get("/api/v1/categories/99999")
        assert response.status_code == 404
        assert response.json()["error"]["code"] == "not_found"

    def test_get_category_invalid_id_type(self, client: TestClient):
        """Should return 422 for non-integer id."""
        response = client.get("/api/v1/categories/abc")
        assert response.status_code == 422

    def test_get_category_zero_id(self, client: TestClient):
        """Should return 404 for id zero."""
        response = client.get("/api/v1/categories/0")
        assert response.status_code == 404

    def test_get_seeded_category_by_id(self, client: TestClient, seeded_category):
        """Should return seeded category correctly."""
        response = client.get(f"/api/v1/categories/{seeded_category['id']}")
        assert response.status_code == 200
        assert response.json()["name"] == "Food"


# ============================================================
# DELETE /api/v1/categories/{id}
# ============================================================

class TestDeleteCategory:
    """Tests for DELETE /api/v1/categories/{id}."""

    def test_delete_category_success(self, client: TestClient, created_category):
        """Should delete an existing category."""
        category_id = created_category["id"]
        response    = client.delete(f"/api/v1/categories/{category_id}")
        assert response.status_code == 200
        assert "deleted" in response.json()["message"].lower()

    def test_delete_category_not_found(self, client: TestClient):
        """Should return 404 when deleting non-existent category."""
        response = client.delete("/api/v1/categories/99999")
        assert response.status_code == 404
        assert response.json()["error"]["code"] == "not_found"

    def test_delete_category_already_deleted(self, client: TestClient, created_category):
        """Should return 404 when deleting already deleted category."""
        category_id = created_category["id"]
        client.delete(f"/api/v1/categories/{category_id}")
        response = client.delete(f"/api/v1/categories/{category_id}")
        assert response.status_code == 404

    def test_delete_category_invalid_id_type(self, client: TestClient):
        """Should return 422 for non-integer id."""
        response = client.delete("/api/v1/categories/abc")
        assert response.status_code == 422

    def test_deleted_category_not_accessible(self, client: TestClient, created_category):
        """Should not be accessible after deletion."""
        category_id = created_category["id"]
        client.delete(f"/api/v1/categories/{category_id}")
        response = client.get(f"/api/v1/categories/{category_id}")
        assert response.status_code == 404