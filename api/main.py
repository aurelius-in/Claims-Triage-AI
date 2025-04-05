from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from api.model import classify_claim
from api.utils import determine_route

app = FastAPI()

class ClaimRequest(BaseModel):
    claim_text: str

class ClaimResponse(BaseModel):
    urgency: str
    risk: str
    route: str
    explanation: str

@app.post("/process-claim", response_model=ClaimResponse)
async def process_claim(claim: ClaimRequest):
    """
    Endpoint to process an insurance claim and determine its urgency, risk, and processing route.

    Args:
        claim (ClaimRequest): The insurance claim text.

    Returns:
        ClaimResponse: The assessed urgency, risk, processing route, and explanation.
    """
    try:
        # Classify the claim to determine urgency and risk
        urgency, risk = classify_claim(claim.claim_text)

        # Determine the processing route based on urgency and risk
        route, explanation = determine_route(claim.claim_text, urgency, risk)

        return ClaimResponse(
            urgency=urgency,
            risk=risk,
            route=route,
            explanation=explanation
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
