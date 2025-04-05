import pytest
from api.model.classifier import classify_claim

@pytest.mark.parametrize(
    "claim_text, expected_urgency, expected_risk",
    [
        ("Patient suffered a minor ankle sprain.", "low", "low"),
        ("Patient experienced chest pain and shortness of breath.", "high", "high"),
        ("Routine check-up appointment.", "low", "low"),
        ("Severe headache and dizziness.", "medium", "medium"),
    ],
)
def test_classify_claim(claim_text, expected_urgency, expected_risk):
    """
    Test the classify_claim function with various claim texts.
    """
    urgency, risk = classify_claim(claim_text)
    assert urgency == expected_urgency
    assert risk == expected_risk
