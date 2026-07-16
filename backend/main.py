from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from strava import get_authorization_url, exchange_code_for_token, get_activities
from metrics import clean_activities, load_acitvities, compute_weekly_mileage, fill_missing_weeks, compute_acwr, get_summary
from llm import get_coaching_note

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/login")
def login():
    redirect_uri = "http://localhost:8000/callback"
    auth_url = get_authorization_url(redirect_uri)
    return {"auth_url": auth_url}


@app.get("/callback")
def callback(code: str):
    return RedirectResponse(url=f"http://localhost:5173?code={code}")


@app.get("/process")
def process(code: str):
    token_data = exchange_code_for_token(code)
    access_token = token_data['access_token']

    activities_raw = get_activities(access_token)
    activities = clean_activities(activities_raw)

    weekly = compute_weekly_mileage(activities)
    weekly = fill_missing_weeks(weekly)
    acwr_results = compute_acwr(weekly)
    summary = get_summary(acwr_results)
    coaching_note = get_coaching_note(summary)

    return {
        "risk_level": "high" if summary['high_risk_weeks'] > 0 else "moderate" if summary['moderate_risk_weeks'] > 0 else "low",
        "peak_acwr": summary['peak_acwr'],
        "peak_week": summary['peak_week'],
        "high_risk_weeks": summary['high_risk_weeks'],
        "moderate_risk_weeks": summary['moderate_risk_weeks'],
        "total_weeks": summary['total_weeks'],
        "timeline": summary['all_weeks'],
        "coaching_note": coaching_note
    }