#!/usr/bin/env python3
"""Fix form to correct results."""

import os
import httpx
import re

WP_URL = os.environ.get("WP_URL", "https://beteasy.ru").rstrip("/")
AUTH = (os.environ.get("WP_USER", ""), os.environ.get("WP_APP_PASS", ""))

# Correct last 5: all wins
# Oct 25: W (Barca 1-2), Oct 21: W (4-1 Leipzig), Oct 18: W (4-1 Sevilla), 
# Oct 14: W (Roma 3-4), Oct 10: W (1-0 Villarreal)
FORM = ["W", "W", "W", "W", "W"]

def main():
    with httpx.Client(timeout=60) as client:
        r = client.get(WP_URL + "/wp-json/wp/v2/pages", params={"slug": "team-real-madrid"}, auth=AUTH)
        if r.status_code != 200 or not r.json():
            print("ERR: page not found")
            return
        
        page = r.json()[0]
        content = page.get("content", {}).get("raw") or page.get("content", {}).get("rendered", "")
        
        colors = {"W": "#27ae60", "D": "#f39c12", "L": "#e74c3c"}
        badges = ""
        for result in FORM:
            badges += f'<span class="tp-fb" style="background:{colors[result]}">{result}</span>\n'
        
        content = re.sub(
            r'(<div class="tp-form">).*?(</div>)',
            r'\1\n' + badges + r'\2',
            content,
            flags=re.DOTALL
        )
        
        r2 = client.post(WP_URL + "/wp-json/wp/v2/pages/" + str(page["id"]), 
                        json={"content": content}, auth=AUTH)
        print("OK" if r2.status_code in (200, 201) else "ERR")

if __name__ == "__main__":
    main()
