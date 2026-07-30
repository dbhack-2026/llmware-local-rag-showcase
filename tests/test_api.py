from fastapi.testclient import TestClient

from app.main import app


def test_live_endpoint():
    response = TestClient(app).get("/health/live")
    assert response.status_code == 200
    assert response.json() == {"status": "UP"}
