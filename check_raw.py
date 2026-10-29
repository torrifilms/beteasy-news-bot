#!/usr/bin/env python3
import os, httpx
WP_URL = os.environ.get("WP_URL", "https://beteasy.ru").rstrip("/")
AUTH = (os.environ.get("WP_USER", ""), os.environ.get("WP_APP_PASS", ""))

with httpx.Client(timeout=30) as client:
    r = client.get(WP_URL + "/wp-json/wp/v2/pages", params={"slug": "team-real-madrid", "context": "edit"}, auth=AUTH)
    if r.status_code == 200 and r.json():
        content = r.json()[0].get("content", {}).get("raw", "")
        print("FAQ in content:", "FAQPage" in content)
        print("SportsTeam in content:", "SportsTeam" in content)
        print("Content length:", len(content))
        # Find FAQ location
        if "FAQ" in content:
            idx = content.find("FAQ")
            print("FAQ context:", content[max(0,idx-50):idx+100])
