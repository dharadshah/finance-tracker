import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.config.database_config import Base
from app.dependencies import get_db
from app.services.category_service import seed_default_categories

TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def reset_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        seed_default_categories(db)
    finally:
        db.close()
    yield


client = TestClient(app)


def test_create_transaction():
    response = client.post("/api/v1/transactions", json={
        "description": "Salary",
        "amount"     : 50000,
        "is_expense" : False
    })
    assert response.status_code == 200
    data = response.json()
    assert data["description"] == "Salary"
    assert data["amount"]      == 50000
    assert data["id"] is not None


def test_create_transaction_with_category():
    categories  = client.get("/api/v1/categories").json()
    income_cat  = next((c for c in categories if c["name"] == "Income"), None)
    assert income_cat is not None, "Income category should be seeded"
    category_id = income_cat["id"]

    response = client.post("/api/v1/transactions", json={
        "description": "Freelance Payment",
        "amount"     : 15000,
        "is_expense" : False,
        "category_id": category_id
    })
    assert response.status_code == 200
    data = response.json()

    # debug - print full response
    print("\nFull response:", data)
    print("category_id in response:", data.get("category_id"))
    print("category in response:", data.get("category"))

    assert data["category_id"]      == category_id
    assert data["category"]["name"] == "Income"


def test_get_transactions():
    response = client.get("/api/v1/transactions")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_transaction_by_id():
    create = client.post("/api/v1/transactions", json={
        "description": "Netflix",
        "amount"     : 649,
        "is_expense" : True
    })
    transaction_id = create.json()["id"]

    response = client.get(f"/api/v1/transactions/{transaction_id}")
    assert response.status_code == 200
    assert response.json()["description"] == "Netflix"


def test_transaction_not_found():
    response = client.get("/api/v1/transactions/99999")
    assert response.status_code == 404


def test_update_transaction():
    create = client.post("/api/v1/transactions", json={
        "description": "Electricity",
        "amount"     : 1800,
        "is_expense" : True
    })
    transaction_id = create.json()["id"]

    response = client.put(f"/api/v1/transactions/{transaction_id}", json={
        "description": "Electricity Bill",
        "amount"     : 2000,
        "is_expense" : True
    })
    assert response.status_code == 200
    assert response.json()["amount"] == 2000


def test_negative_amount_rejected():
    response = client.post("/api/v1/transactions", json={
        "description": "Bad Entry",
        "amount"     : -500,
        "is_expense" : True
    })
    assert response.status_code == 422


def test_delete_transaction():
    create = client.post("/api/v1/transactions", json={
        "description": "Grocery",
        "amount"     : 2500,
        "is_expense" : True
    })
    transaction_id = create.json()["id"]

    response = client.delete(f"/api/v1/transactions/{transaction_id}")
    assert response.status_code == 200