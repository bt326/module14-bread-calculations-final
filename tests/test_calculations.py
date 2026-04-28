from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_home():
    response = client.get("/")
    assert response.status_code == 200

def test_get_calculations():
    response = client.get("/calculations")
    assert response.status_code == 200

def test_add_calculation():
    response = client.post(
        "/calculations",
        json={"operation": "add", "num1": 2, "num2": 3}
    )
    assert response.status_code == 200
    assert response.json()["result"] == 5

def test_invalid_operation():
    response = client.post(
        "/calculations",
        json={"operation": "wrong", "num1": 2, "num2": 3}
    )
    assert response.status_code == 400