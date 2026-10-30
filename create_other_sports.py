#!/usr/bin/env python3
"""Create football and dota2 hubs and team pages."""

import os
import httpx

WP_URL = os.environ.get("WP_URL", "https://beteasy.ru").rstrip("/")
AUTH = (os.environ.get("WP_USER", ""), os.environ.get("WP_APP_PASS", ""))

def get_or_create(client, slug, title, content, parent=0):
    r = client.get(WP_URL + "/wp-json/wp/v2/pages", params={"slug": slug, "parent": parent}, auth=AUTH)
    if r.status_code == 200 and r.json():
        return r.json()[0]["id"]
    r = client.post(WP_URL + "/wp-json/wp/v2/pages", json={
        "title": title, "slug": slug, "status": "publish", "parent": parent, "content": content
    }, auth=AUTH)
    return r.json()["id"] if r.status_code in (200, 201) else None

def main():
    with httpx.Client(timeout=60) as client:
        # Get teams parent
        r = client.get(WP_URL + "/wp-json/wp/v2/pages", params={"slug": "teams"}, auth=AUTH)
        teams_id = r.json()[0]["id"] if r.status_code == 200 and r.json() else None
        print(f"Teams parent: {teams_id}")

        # Football hub
        football_hub = '''<!-- wp:html -->
<style>.hub{max-width:960px;margin:20px auto;padding:0 16px}.hub h1{font-family:Unbounded,sans-serif;font-size:28px;margin:0 0 8px;text-transform:uppercase;color:#EDF0F7}.hub .sub{color:#79829B;margin-bottom:24px}.teams-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:16px}.team-card{display:flex;flex-direction:column;align-items:center;padding:24px 16px;background:#0E1016;border:1px solid rgba(121,130,155,.2);border-radius:16px;text-decoration:none;transition:all .3s}.team-card:hover{border-color:rgba(214,255,59,.4);transform:translateY(-4px)}.team-card img{width:72px;height:72px;object-fit:contain;margin-bottom:12px}.team-card b{font-family:Unbounded,sans-serif;font-size:14px;color:#EDF0F7;text-transform:uppercase}.team-card span{font-size:11px;color:#79829B;margin-top:4px}.bread{display:flex;gap:8px;margin-bottom:16px;font-size:13px}.bread a{color:#79829B;text-decoration:none}.bread a:hover{color:#D6FF3B}.bread span{color:#79829B}</style>
<div class="hub">
<div class="bread"><a href="/">Главная</a><span>→</span><a href="/teams/">Команды</a><span>→</span><span>Футбол</span></div>
<h1>Команды футбола</h1>
<p class="sub">Топ-клубы. Составы, статистика, результаты.</p>
<div class="teams-grid">
<a href="/teams/football/real-madrid/" class="team-card"><img src="https://logo.clearbit.com/realmadrid.com" alt="Real Madrid"><b>Реал Мадрид</b><span>Ла Лига</span></a>
<a href="/teams/football/barcelona/" class="team-card"><img src="https://logo.clearbit.com/fcbarcelona.com" alt="Barcelona"><b>Барселона</b><span>Ла Лига</span></a>
<a href="/teams/football/manchester-city/" class="team-card"><img src="https://logo.clearbit.com/mancity.com" alt="Man City"><b>Манчестер Сити</b><span>АПЛ</span></a>
<a href="/teams/football/psg/" class="team-card"><img src="https://logo.clearbit.com/psg.fr" alt="PSG"><b>ПСЖ</b><span>Лига 1</span></a>
<a href="/teams/football/zenit/" class="team-card"><img src="https://logo.clearbit.com/fc-zenit.ru" alt="Zenit"><b>Зенит</b><span>РПЛ</span></a>
<a href="/teams/football/spartak/" class="team-card"><img src="https://logo.clearbit.com/spartak.com" alt="Spartak"><b>Спартак</b><span>РПЛ</span></a>
</div>
</div>
<!-- /wp:html -->'''
        football_id = get_or_create(client, "football", "Команды футбола", football_hub, teams_id)
        print(f"Football hub: {football_id}")

        # Dota 2 hub
        dota_hub = '''<!-- wp:html -->
<style>.hub{max-width:960px;margin:20px auto;padding:0 16px}.hub h1{font-family:Unbounded,sans-serif;font-size:28px;margin:0 0 8px;text-transform:uppercase;color:#EDF0F7}.hub .sub{color:#79829B;margin-bottom:24px}.teams-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:16px}.team-card{display:flex;flex-direction:column;align-items:center;padding:24px 16px;background:#0E1016;border:1px solid rgba(121,130,155,.2);border-radius:16px;text-decoration:none;transition:all .3s}.team-card:hover{border-color:rgba(214,255,59,.4);transform:translateY(-4px)}.team-card img{width:72px;height:72px;object-fit:contain;margin-bottom:12px}.team-card b{font-family:Unbounded,sans-serif;font-size:14px;color:#EDF0F7;text-transform:uppercase}.team-card span{font-size:11px;color:#79829B;margin-top:4px}.bread{display:flex;gap:8px;margin-bottom:16px;font-size:13px}.bread a{color:#79829B;text-decoration:none}.bread a:hover{color:#D6FF3B}.bread span{color:#79829B}</style>
<div class="hub">
<div class="bread"><a href="/">Главная</a><span>→</span><a href="/teams/">Команды</a><span>→</span><span>Dota 2</span></div>
<h1>Команды Dota 2</h1>
<p class="sub">Топ-команды. Составы, статистика, турниры.</p>
<div class="teams-grid">
<a href="/teams/dota2/team-spirit/" class="team-card"><img src="https://logo.clearbit.com/teamspirit.gg" alt="Team Spirit"><b>Team Spirit</b><span>Россия</span></a>
</div>
</div>
<!-- /wp:html -->'''
        dota_id = get_or_create(client, "dota2", "Команды Dota 2", dota_hub, teams_id)
        print(f"Dota 2 hub: {dota_id}")

        # Sample team pages
        def make_team_page(name, slug, sport, country, league):
            return f'''<!-- wp:html -->
<style>.tp{{max-width:960px;margin:20px auto;padding:0 16px}}.bread{{display:flex;gap:8px;margin-bottom:16px;font-size:13px}}.bread a{{color:#79829B;text-decoration:none}}.bread a:hover{{color:#D6FF3B}}.bread span{{color:#79829B}}.tp-hero{{display:flex;align-items:center;gap:16px;padding:24px;background:#0E1016;border:1px solid rgba(121,130,155,.2);border-radius:16px;margin-bottom:16px}}.tp-logo{{width:80px;height:80px;object-fit:contain;background:#fff;border-radius:8px;padding:8px}}.tp-hero h1{{font-family:Unbounded,sans-serif;font-size:24px;margin:0;text-transform:uppercase;color:#EDF0F7}}.tp-meta{{color:#79829B;font-size:13px;margin:4px 0}}.tp-box{{background:#0E1016;border:1px solid rgba(121,130,155,.2);border-radius:12px;padding:18px;margin:12px 0}}.tp-box h3{{font-family:Unbounded,sans-serif;font-size:13px;margin:0 0 12px;text-transform:uppercase;color:#EDF0F7}}.tp-links{{display:flex;gap:12px;margin-top:16px}}.tp-links a{{padding:10px 16px;background:#D6FF3B;color:#07080C;text-decoration:none;border-radius:8px;font-size:13px;font-weight:600}}</style>
<div class="tp">
<div class="bread"><a href="/">Главная</a><span>→</span><a href="/teams/">Команды</a><span>→</span><a href="/teams/{sport}/">{league}</a><span>→</span><span>{name}</span></div>
<div class="tp-hero">
<img src="https://logo.clearbit.com/{slug}.com" alt="{name}" class="tp-logo">
<div><h1>{name.upper()}</h1><p class="tp-meta">{league} · {country}</p></div>
</div>
<div class="tp-box"><h3>Состав</h3><p class="muted">Обновляется</p></div>
<div class="tp-box"><h3>Последние матчи</h3><p class="muted">Обновляется автоматически</p></div>
<div class="tp-links">
<a href="/prognozy/?s={slug}">Прогнозы</a>
<a href="/?s={slug}">Новости</a>
</div>
</div>
<script type="application/ld+json">{{"@context":"https://schema.org","@type":"SportsTeam","name":"{name}","sport":"{league}"}}</script>
<!-- /wp:html -->'''

        # Football teams
        football_teams = [
            ("Реал Мадрид", "real-madrid", "football", "Испания", "Ла Лига"),
            ("Барселона", "barcelona", "football", "Испания", "Ла Лига"),
            ("Манчестер Сити", "manchester-city", "football", "Англия", "АПЛ"),
            ("ПСЖ", "psg", "football", "Франция", "Лига 1"),
            ("Зенит", "zenit", "football", "Россия", "РПЛ"),
            ("Спартак", "spartak", "football", "Россия", "РПЛ"),
        ]
        for name, slug, sport, country, league in football_teams:
            content = make_team_page(name, slug, sport, country, league)
            pid = get_or_create(client, slug, name, content, football_id)
            print(f"{name}: {pid}")

        # Dota 2 team
        spirit_content = make_team_page("Team Spirit", "team-spirit", "dota2", "Россия", "Dota 2")
        spirit_id = get_or_create(client, "team-spirit", "Team Spirit", spirit_content, dota_id)
        print(f"Team Spirit Dota: {spirit_id}")

if __name__ == "__main__":
    main()
