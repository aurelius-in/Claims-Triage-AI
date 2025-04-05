from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from model.classifier import classify_claim
from utils.router import determine_route

app = FastAPI()

class ClaimInput(BaseModel):
    claim_text: str

class TriageOutput(BaseModel):
    urgency: str
    risk: str
    route: str
    explanation: str

@app.post("/triage", response_model=TriageOutput)
def triage_claim(input: ClaimInput):
    try:
        urgency, risk = classify_claim(input.claim_text)
        route, explanation = determine_route(input.claim_text, urgency, risk)
        return TriageOutput(
            urgency=urgency,
            risk=risk,
            route=route,
            explanation=explanation
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
