from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_process_claim():
    """
    Test the /process-claim endpoint with a sample claim.
    """
    sample_claim = {"claim_text": "Patient suffered a minor ankle sprain."}
    response = client.post("/process-claim", json=sample_claim)
    assert response.status_code == 200
    response_data = response.json()
    assert "urgency" in response_data
    assert "risk" in response_data
    assert "route" in response_data
    assert "explanation" in response_data
