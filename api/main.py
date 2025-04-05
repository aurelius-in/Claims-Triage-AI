from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from api.model.classifier import classify_claim
from api.utils.router import determine_route

app = FastAPI(
    title="Claims Triage API",
    description="An API for classifying insurance claims based on urgency and risk, and determining appropriate processing routes.",
    version="1.0.0"
)

class ClaimRequest(BaseModel):
    claim_text: str

class ClaimResponse(BaseModel):
    urgency: str
    risk: str
    route: str
    explanation: str

@app.post("/triage", response_model=ClaimResponse)
async def triage_claim(claim: ClaimRequest):
    """
    Endpoint to classify an insurance claim's urgency and risk,
    and determine the appropriate processing route.
    """
    if not claim.claim_text.strip():
        raise HTTPException(status_code=400, detail="Claim text cannot be empty.")

    urgency, risk = classify_claim(claim.claim_text)
    route, explanation = determine_route(claim.claim_text, urgency, risk)

    return ClaimResponse(
        urgency=urgency,
        risk=risk,
        route=route,
        explanation=explanation
    )
