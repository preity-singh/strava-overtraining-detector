"""
This module provides functions to interact with the Strava API, 
including generating the authorization URL for OAuth, 
exchanging the authorization code for an access token, 
and retrieving the athlete's activities using the access token.
"""
import requests 
import os
from dotenv import load_dotenv

load_dotenv()

STRAVA_CLIENT_ID = os.getenv("STRAVA_CLIENT_ID")
STRAVA_CLIENT_SECRET = os.getenv("STRAVA_CLIENT_SECRET")

# Generate the authorization URL for Strava OAuth
def get_authorization_url(redirect_uri):
    base_url = "https://www.strava.com/oauth/authorize"
    params = {
        "client_id": STRAVA_CLIENT_ID,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "approval_prompt": "auto",
        "scope": "read,activity:read_all"
    }
    query_string = "&".join([f"{key}={value}" for key, value in params.items()])
    return f"{base_url}?{query_string}"

# Exchange the authorization code for an access token
def exchange_code_for_token(code):
    url = "https://www.strava.com/oauth/token"
    payload = {
        "client_id": STRAVA_CLIENT_ID,
        "client_secret": STRAVA_CLIENT_SECRET,
        "code": code,
        "grant_type": "authorization_code"
    }
    response = requests.post(url, data=payload)
    data = response.json()
    return data

# Get the athlete's activities using the access token
def get_activities(access_token, per_page=200):
    url = "https://www.strava.com/api/v3/athlete/activities"
    headers = {
        'Authorization': f"Bearer {access_token}"
    }
    params = {
        "per_page": per_page
    }
    response = requests.get(url, headers=headers, params=params)
    activities = response.json()
    return activities