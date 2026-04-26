import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db.session import Base, get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

# Mock the LLM service
async def mock_generate_structured_context(raw_context: str) -> dict:
    return {
        "problem": "Mock problem",
        "current_progress": "Mock progress",
        "next_step": "Mock step",
        "open_questions": ["Mock question"],
        "notes": "Mock notes"
    }

@pytest.fixture(autouse=True)
def mock_llm(monkeypatch):
    monkeypatch.setattr("app.routes.context.generate_structured_context", mock_generate_structured_context)

@pytest.fixture
def test_user():
    response = client.post("/auth/register", json={"username": "testuser", "password": "password123"})
    if response.status_code == 400:
        return {"username": "testuser", "password": "password123"}
    return response.json()

@pytest.fixture
def auth_headers(test_user):
    response = client.post("/auth/login", data={"username": "testuser", "password": "password123"})
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_save_context(auth_headers):
    response = client.post("/save", json={
        "raw_context": "I am working on tests"
    }, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["problem"] == "Mock problem"
    assert data["next_step"] == "Mock step"
    
def test_resume_context(auth_headers):
    save_resp = client.post("/save", json={
        "raw_context": "I am working on tests"
    }, headers=auth_headers)
    context_id = save_resp.json()["id"]
    
    response = client.get(f"/resume/{context_id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["next_step"] == "Mock step"
    assert "summary" in data
    assert data["questions"] == ["Mock question"]

def test_invalid_input(auth_headers):
    response = client.post("/save", json={}, headers=auth_headers)
    assert response.status_code == 422
