#!/usr/bin/env python3
"""Create remaining CS2 team pages."""

import os
import httpx

WP_URL = os.environ.get("WP_URL", "https://beteasy.ru").rstrip("/")
AUTH = (os.environ.get("WP_USER", ""), os.environ.get("WP_APP_PASS", ""))

CS2_PARENT = 1404  # CS2 hub ID

def create_page(client, slug, title, content, parent):
    r = client.get(WP_URL + "/wp-json/wp/v2/pages", params={"slug": slug, "parent": parent}, auth=AUTH)
    if r.status_code == 200 and r.json():
        pid = r.json()[0]["id"]
        r2 = client.post(WP_URL + "/wp-json/wp/v2/pages/" + str(pid), json={"content": content}, auth=AUTH)
        return "updated" if r2.status_code in (200, 201) else "error"
    r = client.post(WP_URL + "/wp-json/wp/v2/pages", json={
        "title": title, "slug": slug, "status": "publish", "parent": parent, "content": content
    }, auth=AUTH)
    return "created" if r.status_code in (200, 201) else "error"

def make_page(name, slug, country, founded, major, hltv, winrate, prize, form, players, coach, coach_name):
    form_html = ""
    colors = {"W": "#27ae60", "L": "#e74c3c", "D": "#f39c12"}
    for r in form:
        form_html += f'<span class="tp-fb" style="background:{colors[r]}">{r}</span>'
    
    players_html = ""
    for nick, role, full, nat in players:
        players_html += f'<div class="tp-player"><img src="https://ui-avatars.com/api/?name={nick[:2].upper()}&background=141827&color=EDF0F7&size=96" alt="{nick}"><div><span class="role">{role}</span><b>{nick}</b><span>{full} · {nat}</span></div></div>'
    
    return f'''<!-- wp:html -->
<style>.tp{{max-width:960px;margin:20px auto;padding:0 16px}}.bread{{display:flex;gap:8px;margin-bottom:16px;font-size:13px}}.bread a{{color:#79829B;text-decoration:none}}.bread a:hover{{color:#D6FF3B}}.bread span{{color:#79829B}}.tp-hero{{display:flex;justify-content:space-between;align-items:center;gap:20px;padding:24px;background:#0E1016;border:1px solid rgba(121,130,155,.2);border-radius:16px;margin-bottom:16px}}.tp-hero-left{{display:flex;align-items:center;gap:16px}}.tp-logo{{width:80px;height:80px;object-fit:contain}}.tp-hero h1{{font-family:Unbounded,sans-serif;font-size:24px;margin:0;text-transform:uppercase;color:#EDF0F7}}.tp-meta{{color:#79829B;font-size:13px;margin:4px 0}}.tp-titles{{color:#D6FF3B;font-weight:600;margin-top:8px;font-size:14px}}.tp-stats-row{{display:flex;gap:24px;margin-top:12px}}.tp-stat{{text-align:center}}.tp-stat b{{display:block;font-family:"JetBrains Mono",monospace;font-size:20px;color:#D6FF3B}}.tp-stat span{{font-size:10px;color:#79829B;text-transform:uppercase}}.tp-box{{background:#0E1016;border:1px solid rgba(121,130,155,.2);border-radius:12px;padding:18px;margin:12px 0}}.tp-box h3{{font-family:Unbounded,sans-serif;font-size:13px;margin:0 0 12px;text-transform:uppercase;color:#EDF0F7}}.tp-form{{display:flex;gap:6px}}.tp-fb{{width:32px;height:32px;display:flex;align-items:center;justify-content:center;border-radius:6px;font-weight:700;font-size:12px;color:#fff}}.tp-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:12px}}.tp-player{{display:flex;align-items:center;gap:12px;padding:12px;background:#141827;border-radius:10px}}.tp-player img{{width:48px;height:48px;border-radius:50%}}.tp-player b{{display:block;color:#EDF0F7;font-size:14px}}.tp-player span{{font-size:11px;color:#79829B}}.tp-player .role{{font-size:10px;color:#D6FF3B;text-transform:uppercase}}.tp-faq{{margin:0 0 12px;padding:16px;background:#141827;border-radius:10px}}.tp-faq b{{display:block;color:#EDF0F7;margin-bottom:8px}}.tp-faq p{{margin:0;color:#9AA3B8;font-size:14px;line-height:1.6}}</style>
<div class="tp">
<div class="bread"><a href="/">Главная</a><span>→</span><a href="/teams/">Команды</a><span>→</span><a href="/teams/cs2/">CS2</a><span>→</span><span>{name}</span></div>
<div class="tp-hero"><div class="tp-hero-left"><img src="https://logo.clearbit.com/{slug}.gg" alt="{name}" class="tp-logo"><div><h1>{name.upper()}</h1><p class="tp-meta">CS2 · {country} · Основан в {founded}</p><p class="tp-titles">{major} Major · #{hltv} HLTV</p><div class="tp-stats-row"><div class="tp-stat"><b>{winrate}%</b><span>Винрейт</span></div><div class="tp-stat"><b>{prize}</b><span>Призовые</span></div><div class="tp-stat"><b>{major}</b><span>Major</span></div></div></div></div></div>
<div class="tp-box"><h3>Форма</h3><div class="tp-form">{form_html}</div></div>
<div class="tp-box"><h3>Состав 2026</h3><div class="tp-grid">{players_html}</div></div>
<div class="tp-box"><h3>Тренер</h3><div class="tp-player"><img src="https://ui-avatars.com/api/?name={coach[:2].upper()}&background=D6FF3B&color=07080C&size=96" alt="{coach}"><div><span class="role">Coach</span><b>{coach}</b><span>{coach_name}</span></div></div></div>
<div class="tp-box"><h3>FAQ</h3><div class="tp-faq"><b>Кто капитан {name}?</b><p>Капитан {name} — {players[0][0]} ({players[0][2]}).</p></div><div class="tp-faq"><b>Сколько Major выиграла {name}?</b><p>{name} выиграла {major} Major.</p></div></div>
</div>
<script type="application/ld+json">{{"@context":"https://schema.org","@type":"SportsTeam","name":"{name}","sport":"CS2","url":"https://beteasy.ru/teams/cs2/{slug}/","foundingDate":"{founded}"}}</script>
<!-- /wp:html -->'''

def main():
    teams = [
        {
            "name": "FaZe Clan", "slug": "faze", "country": "США", "founded": "2010",
            "major": "1", "hltv": "8", "winrate": "54", "prize": "$8.2M",
            "form": ["W", "W", "L", "W", "W"],
            "players": [
                ("karrigan", "IGL", "Finn Andersen", "Дания"),
                ("rain", "Rifler", "Håvard Nygaard", "Норвегия"),
                ("broky", "AWPer", "Helvijs Saukants", "Латвия"),
                ("ropz", "Lurker", "Robin Kool", "Эстония"),
                ("frozen", "Entry", "David Čerňanský", "Словакия"),
            ],
            "coach": "NEO", "coach_name": "Главный тренер"
        },
        {
            "name": "G2 Esports", "slug": "g2", "country": "Европа", "founded": "2015",
            "major": "0", "hltv": "3", "winrate": "62", "prize": "$5.1M",
            "form": ["W", "W", "W", "L", "W"],
            "players": [
                ("NiKo", "Rifler", "Nikola Kovač", "Босния"),
                ("huNter-", "Rifler", "Nemanja Kovač", "Босния"),
                ("m0NESY", "AWPer", "Ilya Osipov", "Россия"),
                ("jks", "IGL", "Justin Savage", "Австралия"),
                ("nexa", "Support", "Nemanja Isaković", "Сербия"),
            ],
            "coach": "TaZ", "coach_name": "Главный тренер"
        },
        {
            "name": "Team Vitality", "slug": "vitality", "country": "Франция", "founded": "2018",
            "major": "1", "hltv": "1", "winrate": "68", "prize": "$4.8M",
            "form": ["W", "W", "W", "W", "L"],
            "players": [
                ("ZywOo", "AWPer", "Mathieu Herbaut", "Франция"),
                ("apEX", "IGL", "Dan Madesclaire", "Франция"),
                ("flameZ", "Entry", "Shahar Shushan", "Израиль"),
                ("mezii", "Rifler", "William Merriman", "Великобритания"),
                ("Spinx", "Rifler", "Lotan Giladi", "Израиль"),
            ],
            "coach": "XTQZZZ", "coach_name": "Главный тренер"
        },
        {
            "name": "Team Spirit", "slug": "spirit", "country": "Россия", "founded": "2015",
            "major": "1", "hltv": "2", "winrate": "65", "prize": "$3.9M",
            "form": ["W", "L", "W", "W", "W"],
            "players": [
                ("donk", "Rifler", "Danil Kryshkovets", "Россия"),
                ("sh1ro", "AWPer", "Dmitry Sokolov", "Россия"),
                ("chopper", "IGL", "Leonid Vishnyakov", "Россия"),
                ("magixx", "Rifler", "Boris Vorobiev", "Россия"),
                ("zont1x", "Support", "Myroslav Plakhotia", "Украина"),
            ],
            "coach": "hally", "coach_name": "Главный тренер"
        },
        {
            "name": "MOUZ", "slug": "mouz", "country": "Германия", "founded": "2002",
            "major": "0", "hltv": "4", "winrate": "58", "prize": "$2.1M",
            "form": ["W", "W", "L", "W", "L"],
            "players": [
                ("siuhy", "IGL", "Kamil Szkaradek", "Польша"),
                ("torzsi", "AWPer", "Ádám Torzsás", "Венгрия"),
                ("xertioN", "Entry", "Dorian Berman", "Израиль"),
                ("Jimpphat", "Rifler", "Jimi Salo", "Финляндия"),
                ("Brollan", "Rifler", "Ludvig Brolin", "Швеция"),
            ],
            "coach": "sycrone", "coach_name": "Главный тренер"
        },
    ]
    
    with httpx.Client(timeout=60) as client:
        for t in teams:
            content = make_page(t["name"], t["slug"], t["country"], t["founded"], t["major"], t["hltv"], t["winrate"], t["prize"], t["form"], t["players"], t["coach"], t["coach_name"])
            result = create_page(client, t["slug"], t["name"], content, CS2_PARENT)
            print(f"{t['name']}: {result}")

if __name__ == "__main__":
    main()
