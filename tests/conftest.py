import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.config.database_config import Base, create_db_engine
from app.dependencies import get_db
from app.services.category_service import CategoryService

TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_db_engine(TEST_DATABASE_URL)

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
        CategoryService(db).seed_defaults()
    finally:
        db.close()
    yield


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def seeded_category(client):
    categories = client.get("/api/v1/categories").json()
    return next(c for c in categories if c["name"] == "Food")


@pytest.fixture
def created_category(client):
    response = client.post("/api/v1/categories", json={
        "name"       : "Test Category",
        "description": "Created by fixture"
    })
    return response.json()


@pytest.fixture
def created_transaction(client):
    response = client.post("/api/v1/transactions", json={
        "description": "Test Transaction",
        "amount"     : 1000,
        "is_expense" : True
    })
    return response.json()


@pytest.fixture
def created_income_transaction(client, seeded_category):
    response = client.post("/api/v1/transactions", json={
        "description": "Test Income",
        "amount"     : 50000,
        "is_expense" : False,
        "category_id": seeded_category["id"]
    })
    return response.json()