"""Tests for AI routes.

Coverage:
    POST /api/v1/ai/classify
    GET  /api/v1/ai/analyse
    GET  /api/v1/ai/summary
    POST /api/v1/ai/advice
"""
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient


# ============================================================
# POST /api/v1/ai/classify
# ============================================================

class TestClassifyRoute:
    """Tests for POST /api/v1/ai/classify."""

    def test_classify_success(self, client: TestClient):
        """Should classify a valid transaction description."""
        with patch("app.routes.ai_routes.AIService") as mock_service:
            mock_service.return_value.classify_transaction.return_value = {
                "description"    : "Salary credited",
                "classification" : "INCOME"
            }
            response = client.post("/api/v1/ai/classify", json={
                "description": "Salary credited"
            })
        assert response.status_code == 200
        data = response.json()
        assert data["description"]    == "Salary credited"
        assert data["classification"] == "INCOME"

    def test_classify_expense_transaction(self, client: TestClient):
        """Should classify expense transaction correctly."""
        with patch("app.routes.ai_routes.AIService") as mock_service:
            mock_service.return_value.classify_transaction.return_value = {
                "description"    : "Paid rent",
                "classification" : "EXPENSE"
            }
            response = client.post("/api/v1/ai/classify", json={
                "description": "Paid rent"
            })
        assert response.status_code == 200
        assert response.json()["classification"] == "EXPENSE"

    def test_classify_empty_description_rejected(self, client: TestClient):
        """Should reject empty description."""
        response = client.post("/api/v1/ai/classify", json={
            "description": ""
        })
        assert response.status_code == 422

    def test_classify_whitespace_description_rejected(self, client: TestClient):
        """Should reject whitespace-only description."""
        response = client.post("/api/v1/ai/classify", json={
            "description": "   "
        })
        assert response.status_code == 422

    def test_classify_missing_description_rejected(self, client: TestClient):
        """Should reject missing description field."""
        response = client.post("/api/v1/ai/classify", json={})
        assert response.status_code == 422

    def test_classify_service_error_returns_500(self, client: TestClient):
        """Should return 500 when service raises InternalError."""
        from app.exceptions.app_exceptions import InternalError
        with patch("app.routes.ai_routes.AIService") as mock_service:
            mock_service.return_value.classify_transaction.side_effect = \
                InternalError("LLM failed")
            response = client.post("/api/v1/ai/classify", json={
                "description": "Some transaction"
            })
        assert response.status_code == 500

    def test_classify_response_contains_classification_key(self, client: TestClient):
        """Response should always contain classification key."""
        with patch("app.routes.ai_routes.AIService") as mock_service:
            mock_service.return_value.classify_transaction.return_value = {
                "description"    : "Salary",
                "classification" : "INCOME"
            }
            response = client.post("/api/v1/ai/classify", json={
                "description": "Salary"
            })
        assert "classification" in response.json()


# ============================================================
# GET /api/v1/ai/analyse
# ============================================================

class TestAnalyseRoute:
    """Tests for GET /api/v1/ai/analyse."""

    @pytest.fixture
    def sample_report(self):
        return {
            "transactions"  : [],
            "summary"       : {
                "total_income"             : 50000,
                "total_expenses"           : 2500,
                "balance"                  : 47500,
                "savings_rate"             : 95.0,
                "largest_expense_category" : "Food",
                "insight"                  : "Great savings."
            },
            "advice"        : "Keep saving.",
            "has_high_risk" : False,
            "error"         : None
        }

    def test_analyse_success(self, client: TestClient, sample_report):
        """Should return full analysis report."""
        with patch("app.routes.ai_routes.AIService") as mock_service:
            mock_service.return_value.analyse_transactions.return_value = sample_report
            response = client.get("/api/v1/ai/analyse")
        assert response.status_code == 200

    def test_analyse_report_contains_all_keys(
        self, client: TestClient, sample_report
    ):
        """Report should contain all expected keys."""
        with patch("app.routes.ai_routes.AIService") as mock_service:
            mock_service.return_value.analyse_transactions.return_value = sample_report
            response = client.get("/api/v1/ai/analyse")
        data = response.json()
        assert "transactions"  in data
        assert "summary"       in data
        assert "advice"        in data
        assert "has_high_risk" in data

    def test_analyse_no_transactions_returns_404(self, client: TestClient):
        """Should return 404 when no transactions exist."""
        from app.exceptions.app_exceptions import NotFoundError
        with patch("app.routes.ai_routes.AIService") as mock_service:
            mock_service.return_value.analyse_transactions.side_effect = \
                NotFoundError("No transactions found")
            response = client.get("/api/v1/ai/analyse")
        assert response.status_code == 404

    def test_analyse_service_error_returns_500(self, client: TestClient):
        """Should return 500 when agent fails."""
        from app.exceptions.app_exceptions import InternalError
        with patch("app.routes.ai_routes.AIService") as mock_service:
            mock_service.return_value.analyse_transactions.side_effect = \
                InternalError("Agent failed")
            response = client.get("/api/v1/ai/analyse")
        assert response.status_code == 500


# ============================================================
# GET /api/v1/ai/summary
# ============================================================

class TestAISummaryRoute:
    """Tests for GET /api/v1/ai/summary."""

    @pytest.fixture
    def sample_summary(self):
        return {
            "total_income"             : 50000,
            "total_expenses"           : 2500,
            "balance"                  : 47500,
            "savings_rate"             : 95.0,
            "largest_expense_category" : "Food",
            "insight"                  : "Great savings."
        }

    def test_summary_success(self, client: TestClient, sample_summary):
        """Should return AI summary dict."""
        with patch("app.routes.ai_routes.AIService") as mock_service:
            mock_service.return_value.get_ai_summary.return_value = sample_summary
            response = client.get("/api/v1/ai/summary")
        assert response.status_code == 200

    def test_summary_contains_expected_keys(
        self, client: TestClient, sample_summary
    ):
        """Summary should contain all expected keys."""
        with patch("app.routes.ai_routes.AIService") as mock_service:
            mock_service.return_value.get_ai_summary.return_value = sample_summary
            response = client.get("/api/v1/ai/summary")
        data = response.json()
        assert "total_income"   in data
        assert "total_expenses" in data
        assert "balance"        in data
        assert "savings_rate"   in data

    def test_summary_no_transactions_returns_404(self, client: TestClient):
        """Should return 404 when no transactions exist."""
        from app.exceptions.app_exceptions import NotFoundError
        with patch("app.routes.ai_routes.AIService") as mock_service:
            mock_service.return_value.get_ai_summary.side_effect = \
                NotFoundError("No transactions found")
            response = client.get("/api/v1/ai/summary")
        assert response.status_code == 404

    def test_summary_service_error_returns_500(self, client: TestClient):
        """Should return 500 when chain fails."""
        from app.exceptions.app_exceptions import InternalError
        with patch("app.routes.ai_routes.AIService") as mock_service:
            mock_service.return_value.get_ai_summary.side_effect = \
                InternalError("Chain failed")
            response = client.get("/api/v1/ai/summary")
        assert response.status_code == 500


# ============================================================
# POST /api/v1/ai/advice
# ============================================================

class TestAdviceRoute:
    """Tests for POST /api/v1/ai/advice."""

    @pytest.fixture
    def valid_request(self):
        return {
            "total_income"   : 50000,
            "total_expenses" : 10000,
            "savings_rate"   : 80,
            "top_category"   : "Housing"
        }

    def test_advice_success(self, client: TestClient, valid_request):
        """Should return financial advice."""
        with patch("app.routes.ai_routes.AIService") as mock_service:
            mock_service.return_value.get_financial_advice.return_value = {
                "advice": "Consider investing your savings."
            }
            response = client.post("/api/v1/ai/advice", json=valid_request)
        assert response.status_code == 200
        assert "advice" in response.json()

    def test_advice_response_contains_string(
        self, client: TestClient, valid_request
    ):
        """Advice should be a non-empty string."""
        with patch("app.routes.ai_routes.AIService") as mock_service:
            mock_service.return_value.get_financial_advice.return_value = {
                "advice": "Save more."
            }
            response = client.post("/api/v1/ai/advice", json=valid_request)
        assert isinstance(response.json()["advice"], str)
        assert len(response.json()["advice"]) > 0

    def test_advice_negative_income_rejected(self, client: TestClient):
        """Should reject negative total_income."""
        response = client.post("/api/v1/ai/advice", json={
            "total_income"   : -1000,
            "total_expenses" : 500,
            "savings_rate"   : 50,
            "top_category"   : "Food"
        })
        assert response.status_code == 422

    def test_advice_negative_expenses_rejected(self, client: TestClient):
        """Should reject negative total_expenses."""
        response = client.post("/api/v1/ai/advice", json={
            "total_income"   : 50000,
            "total_expenses" : -500,
            "savings_rate"   : 80,
            "top_category"   : "Food"
        })
        assert response.status_code == 422

    def test_advice_invalid_savings_rate_rejected(self, client: TestClient):
        """Should reject savings rate outside -100 to 100."""
        response = client.post("/api/v1/ai/advice", json={
            "total_income"   : 50000,
            "total_expenses" : 10000,
            "savings_rate"   : 200,
            "top_category"   : "Food"
        })
        assert response.status_code == 422

    def test_advice_missing_fields_rejected(self, client: TestClient):
        """Should reject request with missing fields."""
        response = client.post("/api/v1/ai/advice", json={
            "total_income": 50000
        })
        assert response.status_code == 422

    def test_advice_zero_values_accepted(self, client: TestClient):
        """Should accept zero income and expenses."""
        with patch("app.routes.ai_routes.AIService") as mock_service:
            mock_service.return_value.get_financial_advice.return_value = {
                "advice": "Start saving."
            }
            response = client.post("/api/v1/ai/advice", json={
                "total_income"   : 0,
                "total_expenses" : 0,
                "savings_rate"   : 0,
                "top_category"   : "None"
            })
        assert response.status_code == 200

    def test_advice_service_error_returns_500(self, client: TestClient):
        """Should return 500 when service fails."""
        from app.exceptions.app_exceptions import InternalError
        with patch("app.routes.ai_routes.AIService") as mock_service:
            mock_service.return_value.get_financial_advice.side_effect = \
                InternalError("LLM failed")
            response = client.post("/api/v1/ai/advice", json={
                "total_income"   : 50000,
                "total_expenses" : 10000,
                "savings_rate"   : 80,
                "top_category"   : "Housing"
            })
        assert response.status_code == 500