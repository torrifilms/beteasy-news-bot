#!/usr/bin/env python3
"""Update team form with actual results."""

import os
import httpx
import re

WP_URL = os.environ.get("WP_URL", "https://beteasy.ru").rstrip("/")
AUTH = (os.environ.get("WP_USER", ""), os.environ.get("WP_APP_PASS", ""))

# Actual last 5 results (newest first)
# W = win, D = draw, L = loss
FORM = ["W", "W", "W", "W", "W"]  # 5 wins in a row

# Actual stats
STATS = {
    "wins": 8,
    "draws": 0,
    "losses": 2,
    "goals_for": 25,
    "goals_against": 10
}

def build_form_html():
    colors = {"W": "#27ae60", "D": "#f39c12", "L": "#e74c3c"}
    badges = ""
    for result in FORM:
        badges += f'<span class="tp-fb" style="background:{colors[result]}">{result}</span>\n'
    return badges

def main():
    with httpx.Client(timeout=60) as client:
        r = client.get(WP_URL + "/wp-json/wp/v2/pages", params={"slug": "team-real-madrid"}, auth=AUTH)
        if r.status_code != 200 or not r.json():
            print("ERR: page not found")
            return
        
        page = r.json()[0]
        content = page.get("content", {}).get("raw") or page.get("content", {}).get("rendered", "")
        
        # Update form badges
        form_html = build_form_html()
        content = re.sub(
            r'(<div class="tp-form">).*?(</div>)',
            r'\1\n' + form_html + r'\2',
            content,
            flags=re.DOTALL
        )
        
        # Update stats
        content = re.sub(r'(<div class="tp-st"><b>)\d+(</b><span>Побед</span>)', 
                        r'\g<1>' + str(STATS["wins"]) + r'\2', content)
        content = re.sub(r'(<div class="tp-st"><b>)\d+(</b><span>Ничьих</span>)', 
                        r'\g<1>' + str(STATS["draws"]) + r'\2', content)
        content = re.sub(r'(<div class="tp-st"><b>)\d+(</b><span>Поражений</span>)', 
                        r'\g<1>' + str(STATS["losses"]) + r'\2', content)
        content = re.sub(r'(<div class="tp-st"><b>)\d+(</b><span>Забито</span>)', 
                        r'\g<1>' + str(STATS["goals_for"]) + r'\2', content)
        content = re.sub(r'(<div class="tp-st"><b>)\d+(</b><span>Пропущено</span>)', 
                        r'\g<1>' + str(STATS["goals_against"]) + r'\2', content)
        
        r2 = client.post(WP_URL + "/wp-json/wp/v2/pages/" + str(page["id"]), 
                        json={"content": content}, auth=AUTH)
        print("OK" if r2.status_code in (200, 201) else "ERR")

if __name__ == "__main__":
    main()
