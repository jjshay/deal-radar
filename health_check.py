#!/usr/bin/env python3
"""
DATARADAR Health Check
Run this to verify all systems are working
"""

import os
import base64
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent


def check_mark(ok):
    return "OK" if ok else "FAIL"


def run_health_check():
    print("=" * 50)
    print("DATARADAR HEALTH CHECK")
    print("=" * 50)

    issues = []

    # 1. Check .env file
    env_ok = (BASE_DIR / '.env').exists()
    print(f"[{check_mark(env_ok)}] .env file exists")
    if not env_ok:
        issues.append("Missing .env file - copy from .env.example")

    # 2. Check eBay credentials
    client_id = os.getenv('EBAY_CLIENT_ID')
    client_secret = os.getenv('EBAY_CLIENT_SECRET')
    creds_ok = bool(client_id and client_secret)
    print(f"[{check_mark(creds_ok)}] eBay credentials configured")
    if not creds_ok:
        issues.append("Set EBAY_CLIENT_ID and EBAY_CLIENT_SECRET in .env")

    # 3. Check watchlist file
    watchlist_ok = (BASE_DIR / 'watchlist.json').exists()
    print(f"[{check_mark(watchlist_ok)}] watchlist.json exists")

    # 4. Check web app running
    webapp_ok = False
    try:
        resp = requests.get('http://localhost:5051/api/deals', timeout=5)
        webapp_ok = resp.status_code == 200
        print(f"[{check_mark(webapp_ok)}] Web app running on port 5051")
    except:
        print(f"[{check_mark(False)}] Web app - NOT RUNNING")
        issues.append("Run: python app.py")

    # 5. Check eBay API connection
    ebay_ok = False
    if creds_ok:
        try:
            creds = f"{client_id}:{client_secret}"
            encoded = base64.b64encode(creds.encode()).decode()

            resp = requests.post(
                'https://api.ebay.com/identity/v1/oauth2/token',
                headers={
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Authorization': f'Basic {encoded}'
                },
                data={
                    'grant_type': 'client_credentials',
                    'scope': 'https://api.ebay.com/oauth/api_scope'
                },
                timeout=10
            )
            ebay_ok = resp.status_code == 200
            print(f"[{check_mark(ebay_ok)}] eBay API connection")
        except Exception as e:
            print(f"[{check_mark(False)}] eBay API - {e}")
            issues.append("Check eBay credentials in .env")

    # 6. Check Python dependencies
    deps_ok = True
    required = ['flask', 'requests', 'python-dotenv']
    for dep in required:
        try:
            __import__(dep.replace('-', '_'))
        except ImportError:
            deps_ok = False
            issues.append(f"Missing dependency: {dep}")
    print(f"[{check_mark(deps_ok)}] Python dependencies")

    print("\n" + "=" * 50)
    if issues:
        print("ISSUES FOUND:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("ALL SYSTEMS OK")
    print("=" * 50)

    return len(issues) == 0


if __name__ == "__main__":
    run_health_check()
