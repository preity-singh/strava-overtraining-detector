from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
import os
from dotenv import load_dotenv

from strava import get_authorization_url, exchange_code_for_token, get_activities
from metrics import clean_activities, load_activities, compute_weekly_mileage, fill_missing_weeks, compute_acwr, get_summary
from llm import get_coaching_note

load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/login")
def login():
    redirect_uri = f"{BACKEND_URL}/callback"
    auth_url = get_authorization_url(redirect_uri)
    return {"auth_url": auth_url}


@app.get("/callback")
def callback(code: str):
    return RedirectResponse(url=f"{FRONTEND_URL}?code={code}")


@app.get("/process")
def process(code: str):
    try:
        token_data = exchange_code_for_token(code)
        if 'access_token' not in token_data:
            return {"error": "Authorization failed or code already used. Please reconnect."}
        access_token = token_data['access_token']

        activities_raw = get_activities(access_token)
        activities = clean_activities(activities_raw)

        weekly = compute_weekly_mileage(activities)
        weekly = fill_missing_weeks(weekly)
        acwr_results = compute_acwr(weekly, activities)
        summary = get_summary(acwr_results)

        if 'error' in summary:
            return {"error": summary['error']}

        coaching_note = get_coaching_note(summary)

        recent = acwr_results[-3:]
        risk_priority = ['High Risk', 'Moderate Risk', 'Reduced Conditioning', 'Optimal']
        worst_risk = next((r for r in risk_priority if any(w['risk'] == r for w in recent)), 'Optimal')
        risk_level_map = {
            'High Risk': 'high',
            'Moderate Risk': 'moderate',
            'Optimal': 'optimal',
            'Reduced Conditioning': 'reduced_conditioning',
        }
        risk_level = risk_level_map[worst_risk]

        return {
            "risk_level": risk_level,
            "peak_acwr": summary['peak_acwr'],
            "peak_week": summary['peak_week'],
            "high_risk_weeks": summary['high_risk_weeks'],
            "moderate_risk_weeks": summary['moderate_risk_weeks'],
            "total_weeks": summary['total_weeks'],
            "timeline": summary['all_weeks'],
            "coaching_note": coaching_note
        }
    except Exception as e:
        return {"error": f"Failed to process your data: {str(e)}"}