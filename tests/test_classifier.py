import pytest
from api.model.classifier import classify_claim

def test_classify_claim():
    urgency, risk = classify_claim("Patient requires emergency surgery due to severe injury.")
    assert urgency == "High"
    assert risk == "High"
