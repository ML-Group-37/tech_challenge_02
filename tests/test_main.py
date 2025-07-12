from fastapi.testclient import TestClient
from tech_challenge_02.main import app

client = TestClient(app)

def test_read_test_endpoint():
    response = client.get("/api/test")
    assert response.status_code == 200
    assert response.json() == {"message": "API is working!", "status": "success"} 