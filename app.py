from flask import Flask, request, redirect, jsonify, send_file
import requests
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")

@app.route("/oauth/callback")
def oauth_callback():
    code = request.args.get("code")
    if not code:
        return "No code provided", 400

    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "code": code,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code"
    }

    token_response = requests.post(token_url, data=data)
    if token_response.status_code != 200:
        return token_response.text, token_response.status_code

    tokens = token_response.json()
    return jsonify(tokens)

@app.route("/calendar/events")
def get_calendar_events():
    access_token = request.headers.get("Authorization", "").replace("Bearer ", "")
    if not access_token:
        return "Missing access token", 401

    calendar_url = "https://www.googleapis.com/calendar/v3/calendars/primary/events"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    response = requests.get(calendar_url, headers=headers)
    return jsonify(response.json()), response.status_code

@app.route("/.well-known/ai-plugin.json")
def plugin_manifest():
    return send_file(".well-known/ai-plugin.json")

@app.route("/openapi.yaml")
def openapi_spec():
    return send_file("openapi.yaml", mimetype="text/yaml")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
