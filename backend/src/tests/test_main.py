from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_app_health_status():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert "environment" in response.json()
