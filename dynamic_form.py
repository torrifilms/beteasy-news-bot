#!/usr/bin/env python3
"""Update team form by fetching actual results for each team."""

import os
import httpx
import re

WP_URL = os.environ.get("WP_URL", "https://beteasy.ru").rstrip("/")
AUTH = (os.environ.get("WP_USER", ""), os.environ.get("WP_APP_PASS", ""))

# Team configurations with search terms
TEAMS = {
    "team-real-madrid": {
        "name": "Real Madrid",
        "search": "Real Madrid results",
        "espn_id": "86"
    },
    "team-barselona": {
        "name": "Barcelona", 
        "search": "Barcelona results",
        "espn_id": "83"
    },
    "team-natus-vincere": {
        "name": "Natus Vincere",
        "search": "NaVi CS2 results",
        "espn_id": None
    },
    "team-team-spirit": {
        "name": "Team Spirit",
        "search": "Team Spirit Dota 2 results",
        "espn_id": None
    }
}

def fetch_form_espn(espn_id):
    """Fetch last 5 results from ESPN."""
    if not espn_id:
        return None
    try:
        url = f"https://site.api.espn.com/apis/site/v2/sports/soccer/esp.1/teams/{espn_id}/schedule"
        r = httpx.get(url, timeout=15)
        if r.status_code != 200:
            return None
        data = r.json()
        events = data.get("events", [])[:5]
        form = []
        for e in events:
            comp = e.get("competitions", [{}])[0]
            competitors = comp.get("competitors", [])
            for c in competitors:
                if c.get("team", {}).get("id") == espn_id:
                    winner = c.get("winner", False)
                    score = c.get("score", {})
                    if winner:
                        form.append("W")
                    elif score.get("value") == competitors[1-competitors.index(c)].get("score", {}).get("value"):
                        form.append("D")
                    else:
                        form.append("L")
                    break
        return form if form else None
    except:
        return None

def update_page(client, slug, form):
    """Update team page with new form."""
    r = client.get(WP_URL + "/wp-json/wp/v2/pages", params={"slug": slug}, auth=AUTH)
    if r.status_code != 200 or not r.json():
        return False
    
    page = r.json()[0]
    content = page.get("content", {}).get("raw") or page.get("content", {}).get("rendered", "")
    
    colors = {"W": "#27ae60", "D": "#f39c12", "L": "#e74c3c"}
    badges = ""
    for result in form[:5]:
        badges += f'<span class="tp-fb" style="background:{colors.get(result, "#79829B")}">{result}</span>\n'
    
    content = re.sub(
        r'(<div class="tp-form">).*?(</div>)',
        r'\1\n' + badges + r'\2',
        content,
        flags=re.DOTALL
    )
    
    r2 = client.post(WP_URL + "/wp-json/wp/v2/pages/" + str(page["id"]), 
                    json={"content": content}, auth=AUTH)
    return r2.status_code in (200, 201)

def main():
    with httpx.Client(timeout=60) as client:
        for slug, team in TEAMS.items():
            form = fetch_form_espn(team.get("espn_id"))
            if form:
                ok = update_page(client, slug, form)
                print(f"{'OK' if ok else 'ERR'} {slug}: {''.join(form)}")
            else:
                print(f"SKIP {slug}: no data")

if __name__ == "__main__":
    main()
