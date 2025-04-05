def classify_claim(text: str) -> tuple:
    """
    Very simple rule-based classifier for demo purposes.
    Replace with actual ML model for production use.
    """
    text_lower = text.lower()

    # Determine urgency
    if "emergency" in text_lower or "urgent" in text_lower or "critical" in text_lower:
        urgency = "High"
    elif "follow-up" in text_lower or "moderate" in text_lower:
        urgency = "Medium"
    else:
        urgency = "Low"

    # Determine risk
    if "surgery" in text_lower or "fracture" in text_lower or "high cost" in text_lower:
        risk = "High"
    elif "pain" in text_lower or "diagnostics" in text_lower:
        risk = "Medium"
    else:
        risk = "Low"

    return urgency, risk
