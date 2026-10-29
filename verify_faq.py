#!/usr/bin/env python3
import os, httpx
WP_URL = os.environ.get("WP_URL", "https://beteasy.ru").rstrip("/")
AUTH = (os.environ.get("WP_USER", ""), os.environ.get("WP_APP_PASS", ""))

with httpx.Client(timeout=30) as client:
    r = client.get(WP_URL + "/wp-json/wp/v2/pages", params={"slug": "team-real-madrid", "context": "edit"}, auth=AUTH)
    if r.status_code == 200 and r.json():
        content = r.json()[0].get("content", {}).get("raw", "")
        print("FAQPage:", "FAQPage" in content)
        print("Кто тренер:", "Кто тренер" in content)
        print("SportsTeam:", "SportsTeam" in content)
