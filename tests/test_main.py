import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_triage_endpoint():
    response = client.post("/triage", json={"claim_text": "Patient requires emergency surgery due to severe injury."})
    assert response.status_code == 200
    data = response.json()
    assert "urgency" in data
    assert "risk" in data
    assert "route" in data
    assert "explanation" in data
