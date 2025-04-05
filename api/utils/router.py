def determine_route(text: str, urgency: str, risk: str) -> tuple:
    """
    Determine the triage route and explanation based on urgency and risk.
    """
    if urgency == "High" or risk == "High":
        route = "Escalate to Clinical Review"
        explanation = "Detected critical urgency or high-risk indicators. Needs clinical attention."
    elif urgency == "Medium" and risk == "Medium":
        route = "Send to Manual Review Team"
        explanation = "Moderate urgency and complexity. Recommended for manual handling."
    else:
        route = "Auto-Approve"
        explanation = "Low urgency and risk detected. Safe to auto-approve."

    return route, explanation
