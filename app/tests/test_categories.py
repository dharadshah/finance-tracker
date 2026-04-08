import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.config.database_config import Base
from app.dependencies import get_db
from app.schemas import CategoryCreate
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
    # seed default categories for each test
    db = TestingSessionLocal()
    try:
        seed_default_categories(db)
    finally:
        db.close()
    yield


client = TestClient(app)

def test_create_category():
    response = client.post("/api/v1/categories", json={
        "name"       : "Test Food Category",
        "description": "Food and groceries"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Food Category"
    assert data["id"] is not None


def test_get_categories():
    response = client.get("/api/v1/categories")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_category_by_id():
    create = client.post("/api/v1/categories", json={"name": "Test Housing Category"})
    category_id = create.json()["id"]

    response = client.get(f"/api/v1/categories/{category_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Test Housing Category"


def test_category_not_found():
    response = client.get("/api/v1/categories/99999")
    assert response.status_code == 404


def test_duplicate_category():
    client.post("/api/v1/categories", json={"name": "Test Transport Category"})
    response = client.post("/api/v1/categories", json={"name": "Test Transport Category"})
    assert response.status_code == 400


def test_delete_category():
    create = client.post("/api/v1/categories", json={"name": "Test Utilities Category"})
    category_id = create.json()["id"]

    response = client.delete(f"/api/v1/categories/{category_id}")
    assert response.status_code == 200