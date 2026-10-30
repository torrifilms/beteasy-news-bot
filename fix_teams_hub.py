#!/usr/bin/env python3
"""Rebuild /teams/ hub with all teams and emblems."""

import os
import httpx

WP_URL = os.environ.get("WP_URL", "https://beteasy.ru").rstrip("/")
AUTH = (os.environ.get("WP_USER", ""), os.environ.get("WP_APP_PASS", ""))

# Emblem domains that work with Clearbit or fallback
EMBLEMS = {
    "vitality": "vitality.gg",
    "navi": "navi.gg",
    "faze": "fazeclan.com",
    "g2": "g2esports.com",
    "spirit": "teamspirit.gg",
    "mouz": "mousesports.com",
    "liquid": "teamliquid.com",
    "astralis": "astralis.gg",
    "team-spirit": "teamspirit.gg",
    "parivision": "parivision.gg",
    "og": "og.gg",
    "betboom": "betboom.gg",
    "1win": "1win.team",
    "xtreme": "xtreme.gg",
    "nigma": "nigma-galaxy.com",
    "aurora": "aurora.gg",
    "yandex": "yandex-team.ru",
    "falcons": "falcons.gg",
    "real-madrid": "realmadrid.com",
    "barcelona": "fcbarcelona.com",
    "manchester-city": "mancity.com",
    "psg": "psg.fr",
    "zenit": "fc-zenit.ru",
    "spartak": "spartak.com",
}

def get_parent(client, slug):
    r = client.get(WP_URL + "/wp-json/wp/v2/pages", params={"slug": slug}, auth=AUTH)
    if r.status_code == 200 and r.json():
        return r.json()[0]["id"]
    return None

def build_hub_content():
    teams = {
        "CS2": ["vitality", "navi", "faze", "g2", "spirit", "mouz", "liquid", "astralis"],
        "Dota 2": ["team-spirit", "parivision", "og", "betboom", "1win", "xtreme", "nigma", "aurora", "yandex", "falcons", "navi", "liquid"],
        "Футбол": ["real-madrid", "barcelona", "manchester-city", "psg", "zenit", "spartak"],
    }
    sport_slugs = {"CS2": "cs2", "Dota 2": "dota2", "Футбол": "football"}
    
    html = '''<!-- wp:html -->
<style>.th{max-width:1100px;margin:20px auto;padding:0 16px}.th-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:16px;margin:16px 0}.th-card{display:flex;flex-direction:column;align-items:center;padding:16px;background:#0E1016;border:1px solid rgba(121,130,155,.2);border-radius:12px;text-decoration:none;transition:border-color .2s}.th-card:hover{border-color:#D6FF3B}.th-card img{width:64px;height:64px;object-fit:contain;background:#fff;border-radius:8px;padding:6px;margin-bottom:10px}.th-card span{color:#EDF0F7;font-size:13px;font-weight:600;text-align:center}.th h2{font-family:Unbounded,sans-serif;font-size:18px;color:#EDF0F7;margin:24px 0 12px;text-transform:uppercase}</style>
<div class="th">
<h1 style="font-family:Unbounded,sans-serif;color:#EDF0F7">Команды</h1>
<p style="color:#79829B">Все команды CS2, Dota 2 и футбола</p>
'''
    for sport, slugs in teams.items():
        sport_slug = sport_slugs[sport]
        html += f'<h2>{sport}</h2><div class="th-grid">'
        for slug in slugs:
            domain = EMBLEMS.get(slug, f"{slug}.com")
            name = slug.replace("-", " ").title()
            html += f'''<a href="/teams/{sport_slug}/{slug}/" class="th-card">
<img src="https://logo.clearbit.com/{domain}" alt="{name}" onerror="this.src='https://ui-avatars.com/api/?name={name[:2]}&background=141827&color=D6FF3B&size=64'">
<span>{name}</span>
</a>'''
        html += '</div>'
    html += '</div><!-- /wp:html -->'
    return html

def main():
    with httpx.Client(timeout=60) as client:
        # Find or create teams parent
        r = client.get(WP_URL + "/wp-json/wp/v2/pages", params={"slug": "teams"}, auth=AUTH)
        if r.status_code == 200 and r.json():
            pid = r.json()[0]["id"]
            content = build_hub_content()
            r2 = client.post(WP_URL + f"/wp-json/wp/v2/pages/{pid}", json={"content": content}, auth=AUTH)
            print(f"Hub updated: {r2.status_code}")
        else:
            print("Teams page not found")

if __name__ == "__main__":
    main()
