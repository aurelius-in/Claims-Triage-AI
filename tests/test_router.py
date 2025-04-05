import pytest
from api.utils.router import determine_route

def test_determine_route():
    route, explanation = determine_route("Patient requires emergency surgery due to severe injury.", "High", "High")
    assert route == "Escalate to Clinical Review"
    assert explanation == "Detected critical urgency or high-risk indicators. Needs clinical attention."
