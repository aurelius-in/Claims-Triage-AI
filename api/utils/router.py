def determine_route(claim_text: str, urgency: str, risk: str) -> tuple:
    """
    Determine the processing route for an insurance claim based on its urgency and risk levels.

    Args:
        claim_text (str): The text of the insurance claim.
        urgency (str): The urgency level of the claim ('Low', 'Medium', 'High').
        risk (str): The risk level of the claim ('Low', 'Medium', 'High').

    Returns:
        tuple: A tuple containing:
            - route (str): The determined processing route.
            - explanation (str): Explanation for the chosen route.
    """
    if urgency == "High" or risk == "High":
        route = "Escalate to Clinical Review"
        explanation = "Detected critical urgency or high-risk indicators. Needs clinical attention."
    elif urgency == "Medium" and risk == "Medium":
        route = "Refer to Specialist Team"
        explanation = "Moderate urgency and risk detected. Specialist review recommended."
    else:
        route = "Standard Processing"
        explanation = "Low urgency and risk. Proceed with standard claim processing."

    return route, explanation
