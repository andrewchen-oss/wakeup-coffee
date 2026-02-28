"""
whoop_monitor.py
----------------
Polls the Whoop API to detect when the user has woken up.
Returns True when a new recovery cycle (wake event) is detected.
"""

import json
import time
import urllib.request
import urllib.parse
from datetime import datetime, timezone

BASE_URL = "https://api.prod.whoop.com/developer/v1"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15",
    "Accept": "application/json",
}

STATE_FILE = "state.json"


def load_state():
    try:
        with open(STATE_FILE) as f:
            return json.load(f)
    except Exception:
        return {}


def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)


def refresh_token(config):
    """Refresh the Whoop OAuth token."""
    url = "https://api.prod.whoop.com/oauth/oauth2/token"
    data = urllib.parse.urlencode({
        "grant_type": "refresh_token",
        "refresh_token": config["whoop"]["refresh_token"],
        "client_id": config["whoop"]["client_id"],
        "client_secret": config["whoop"]["client_secret"],
    }).encode()
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    req.add_header("User-Agent", HEADERS["User-Agent"])
    with urllib.request.urlopen(req, timeout=15) as resp:
        result = json.loads(resp.read())
    config["whoop"]["access_token"] = result["access_token"]
    if "refresh_token" in result:
        config["whoop"]["refresh_token"] = result["refresh_token"]
    return config


def get_latest_recovery(access_token):
    """Fetch the most recent recovery record from Whoop."""
    url = f"{BASE_URL}/recovery?limit=1"
    req = urllib.request.Request(url)
    req.add_header("Authorization", f"Bearer {access_token}")
    req.add_header("User-Agent", HEADERS["User-Agent"])
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read())
    records = data.get("records", [])
    return records[0] if records else None


def check_wake_up(config):
    """
    Returns a recovery record if the user has woken up since the last check,
    otherwise returns None.
    """
    state = load_state()
    last_cycle_id = state.get("last_cycle_id")

    try:
        recovery = get_latest_recovery(config["whoop"]["access_token"])
    except urllib.error.HTTPError as e:
        if e.code == 401:
            print("[whoop] Token expired, refreshing...")
            config = refresh_token(config)
            recovery = get_latest_recovery(config["whoop"]["access_token"])
        else:
            raise

    if not recovery:
        return None

    cycle_id = recovery.get("cycle_id") or recovery.get("id")
    created_at = recovery.get("created_at", "")

    # New cycle = new wake-up event
    if cycle_id and str(cycle_id) != str(last_cycle_id):
        state["last_cycle_id"] = str(cycle_id)
        save_state(state)
        return recovery

    return None


def format_recovery_summary(recovery):
    score = recovery.get("score", {})
    return {
        "recovery_score": score.get("recovery_score", "N/A"),
        "hrv_rmssd_milli": round(score.get("hrv_rmssd_milli", 0), 1),
        "resting_heart_rate": score.get("resting_heart_rate", "N/A"),
        "spo2_percentage": round(score.get("spo2_percentage", 0), 1),
        "skin_temp_celsius": round(score.get("skin_temp_celsius", 0), 1),
    }


if __name__ == "__main__":
    import sys
    sys.path.insert(0, ".")
    with open("config/config.json") as f:
        config = json.load(f)

    print("[whoop] Checking for wake-up event...")
    recovery = check_wake_up(config)
    if recovery:
        summary = format_recovery_summary(recovery)
        print(f"[whoop] Wake-up detected! Summary: {summary}")
    else:
        print("[whoop] No new wake-up event.")
