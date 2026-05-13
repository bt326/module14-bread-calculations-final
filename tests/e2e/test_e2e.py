from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_power_feature():
    response = client.post(
        "/calculations",
        json={
            "operation": "power",
            "num1": 2,
            "num2": 3
        }
    )

    assert response.status_code == 200
    assert response.json()["result"] == 8


def test_modulus_feature():
    response = client.post(
        "/calculations",
        json={
            "operation": "modulus",
            "num1": 10,
            "num2": 3
        }
    )

    assert response.status_code == 200
    assert response.json()["result"] == 1