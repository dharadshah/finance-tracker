import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.config.database_config import Base, get_db

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

Base.metadata.create_all(bind=engine)

client = TestClient(app)


def test_create_category():
    response = client.post("/categories", json={
        "name"       : "Food",
        "description": "Food and groceries"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Food"
    assert data["id"] is not None


def test_get_categories():
    response = client.get("/categories")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_category_by_id():
    create = client.post("/categories", json={"name": "Housing"})
    category_id = create.json()["id"]

    response = client.get(f"/categories/{category_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Housing"


def test_category_not_found():
    response = client.get("/categories/99999")
    assert response.status_code == 404


def test_duplicate_category():
    client.post("/categories", json={"name": "Transport"})
    response = client.post("/categories", json={"name": "Transport"})
    assert response.status_code == 400


def test_delete_category():
    create = client.post("/categories", json={"name": "Utilities"})
    category_id = create.json()["id"]

    response = client.delete(f"/categories/{category_id}")
    assert response.status_code == 200