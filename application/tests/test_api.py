from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_root():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["status"] == "running"


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_get_patients():
    response = client.get("/patients")

    assert response.status_code == 200
    assert len(response.json()) >= 2


def test_get_existing_patient():
    response = client.get("/patients/1")

    assert response.status_code == 200
    assert response.json()["name"] == "Alice Martin"


def test_get_unknown_patient():
    response = client.get("/patients/9999")

    assert response.status_code == 404


def test_create_patient():
    patient = {
        "name": "Charlie Test",
        "age": 28,
        "email": "charlie@example.com",
    }

    response = client.post("/patients", json=patient)

    assert response.status_code == 201
    assert response.json()["name"] == "Charlie Test"
