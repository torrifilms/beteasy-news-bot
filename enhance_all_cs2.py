#!/usr/bin/env python3
"""Apply enhanced template to all CS2 teams."""

import os
import httpx

WP_URL = os.environ.get("WP_URL", "https://beteasy.ru").rstrip("/")
AUTH = (os.environ.get("WP_USER", ""), os.environ.get("WP_APP_PASS", ""))
CS2_PARENT = 1404

def update_page(client, slug, content):
    r = client.get(WP_URL + "/wp-json/wp/v2/pages", params={"slug": slug, "parent": CS2_PARENT}, auth=AUTH)
    if r.status_code == 200 and r.json():
        pid = r.json()[0]["id"]
        r2 = client.post(WP_URL + "/wp-json/wp/v2/pages/" + str(pid), json={"content": content}, auth=AUTH)
        return "updated" if r2.status_code in (200, 201) else "error"
    return "not found"

def make_page(name, slug, country, site, prize, rank, majors, matches, winrate, players, maps, faq):
    players_html = ""
    for nick, role, full, nat in players:
        players_html += f'''<div class="tp-player">
<img src="https://ui-avatars.com/api/?name={nick[:2].upper()}&background=141827&color=D6FF3B&size=104" alt="{nick}">
<div class="tp-player-info"><span class="role">{role}</span><b>{nick}</b><span class="name">{full} · {nat}</span></div>
</div>'''

    maps_html = '<table class="tp-map-table"><tr><th>#</th><th>Карта</th><th>И</th><th>В</th><th>П</th><th>%</th></tr>'
    for i, (map_name, played, wins, losses, pct) in enumerate(maps, 1):
        maps_html += f'<tr><td>{i}</td><td>{map_name}</td><td>{played}</td><td class="win">{wins}</td><td class="loss">{losses}</td><td>{pct}%</td></tr>'
    maps_html += '</table>'

    faq_html = ""
    for q, a in faq:
        faq_html += f'<div class="tp-faq"><b>{q}</b><p>{a}</p></div>'

    return f'''<!-- wp:html -->
<style>.tp{{max-width:960px;margin:20px auto;padding:0 16px}}.bread{{display:flex;gap:8px;margin-bottom:16px;font-size:13px}}.bread a{{color:#79829B;text-decoration:none}}.bread a:hover{{color:#D6FF3B}}.bread span{{color:#79829B}}.tp-hero{{display:flex;align-items:center;gap:16px;padding:24px;background:linear-gradient(135deg,#0E1016 0%,#1a1f2e 100%);border:1px solid rgba(214,255,59,.15);border-radius:16px;margin-bottom:16px}}.tp-logo{{width:90px;height:90px;object-fit:contain;background:#fff;border-radius:12px;padding:10px;box-shadow:0 4px 20px rgba(0,0,0,.3)}}.tp-hero h1{{font-family:Unbounded,sans-serif;font-size:26px;margin:0;text-transform:uppercase;color:#EDF0F7}}.tp-meta{{color:#79829B;font-size:13px;margin:6px 0}}.tp-meta a{{color:#D6FF3B}}.tp-titles{{color:#D6FF3B;font-weight:600;margin-top:10px;font-size:14px}}.tp-stats-row{{display:flex;gap:24px;margin-top:14px}}.tp-stat{{text-align:center}}.tp-stat b{{display:block;font-family:"JetBrains Mono",monospace;font-size:20px;color:#D6FF3B}}.tp-stat span{{font-size:10px;color:#79829B;text-transform:uppercase}}.tp-box{{background:#0E1016;border:1px solid rgba(121,130,155,.2);border-radius:12px;padding:18px;margin:12px 0}}.tp-box h3{{font-family:Unbounded,sans-serif;font-size:13px;margin:0 0 14px;text-transform:uppercase;color:#EDF0F7}}.tp-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:12px}}.tp-player{{display:flex;align-items:center;gap:12px;padding:14px;background:#141827;border-radius:10px}}.tp-player img{{width:52px;height:52px;border-radius:50%;border:2px solid rgba(214,255,59,.3)}}.tp-player b{{display:block;color:#EDF0F7;font-size:14px}}.tp-player .role{{font-size:10px;color:#D6FF3B;text-transform:uppercase;font-weight:600}}.tp-player .name{{font-size:11px;color:#79829B}}.tp-map-table{{width:100%;border-collapse:collapse}}.tp-map-table th,.tp-map-table td{{padding:10px 8px;text-align:left;font-size:13px;border-bottom:1px solid rgba(121,130,155,.15)}}.tp-map-table th{{color:#79829B;font-weight:500;font-size:11px;text-transform:uppercase}}.tp-map-table td{{color:#EDF0F7}}.tp-map-table .win{{color:#27ae60}}.tp-map-table .loss{{color:#e74c3c}}.tp-faq{{margin:0 0 10px;padding:14px;background:#141827;border-radius:10px}}.tp-faq b{{display:block;color:#EDF0F7;margin-bottom:6px;font-size:14px}}.tp-faq p{{margin:0;color:#9AA3B8;font-size:13px;line-height:1.5}}.tp-links{{display:flex;gap:12px;margin-top:16px}}.tp-links a{{padding:12px 20px;background:#D6FF3B;color:#07080C;text-decoration:none;border-radius:8px;font-size:13px;font-weight:600}}</style>
<div class="tp">
<div class="bread"><a href="/">Главная</a><span>→</span><a href="/teams/">Команды</a><span>→</span><a href="/teams/cs2/">CS2</a><span>→</span><span>{name}</span></div>
<div class="tp-hero">
<img src="https://logo.clearbit.com/{slug}.gg" alt="{name}" class="tp-logo">
<div>
<h1>{name.upper()}</h1>
<p class="tp-meta">CS2 · {country} · <a href="{site}" target="_blank" rel="nofollow">{site.replace("https://","").replace("http://","")}</a></p>
<p class="tp-titles">{majors} Major · #{rank} HLTV · {prize}</p>
<div class="tp-stats-row">
<div class="tp-stat"><b>{majors}</b><span>Major</span></div>
<div class="tp-stat"><b>{matches}</b><span>Матчей</span></div>
<div class="tp-stat"><b>{winrate}%</b><span>Винрейт</span></div>
<div class="tp-stat"><b>{prize}</b><span>Призовых</span></div>
</div>
</div>
</div>
<div class="tp-box"><h3>Состав 2026</h3><div class="tp-grid">{players_html}</div></div>
<div class="tp-box"><h3>Форма</h3><div class="tp-form"><span class="tp-fb" style="background:#79829B">—</span></div></div>
<div class="tp-box"><h3>Последние матчи</h3><p class="muted">Обновляется автоматически</p></div>
<div class="tp-box"><h3>Статистика по картам</h3>{maps_html}</div>
<div class="tp-box"><h3>FAQ</h3>{faq_html}</div>
<div class="tp-links">
<a href="/prognozy/?s={slug}">Прогнозы</a>
<a href="/?s={slug}">Новости</a>
</div>
</div>
<script type="application/ld+json">{{"@context":"https://schema.org","@type":"SportsTeam","name":"{name}","sport":"CS2","url":"https://beteasy.ru/teams/cs2/{slug}/"}}</script>
<!-- /wp:html -->'''

def main():
    teams = [
        {
            "name": "Natus Vincere", "slug": "navi", "country": "Украина", "site": "https://navi.gg",
            "prize": "$6.3M", "rank": 5, "majors": 1, "matches": 180, "winrate": 62,
            "players": [
                ("b1t", "Rifler", "Valeriy Vakhovskiy", "Украина"),
                ("iM", "Rifler", "Mihai Ivan", "Румыния"),
                ("w0nderful", "AWP", "Ihor Zhdanov", "Украина"),
                ("jL", "Rifler", "Justinas Lekavicius", "Литва"),
                ("Aleksib", "IGL", "Aleksi Virolainen", "Финляндия"),
            ],
            "maps": [("Mirage", 45, 28, 17, 62), ("Inferno", 38, 22, 16, 58), ("Nuke", 32, 20, 12, 63)],
            "faq": [("Сколько Major выиграла NaVi?", "Natus Vincere выиграла один Major — PGL Major Stockholm 2021.")]
        },
        {
            "name": "FaZe Clan", "slug": "faze", "country": "Европа", "site": "https://fazeclan.com",
            "prize": "$8.5M", "rank": 4, "majors": 1, "matches": 165, "winrate": 58,
            "players": [
                ("rain", "Rifler", "Håvard Nygaard", "Норвегия"),
                ("karrigan", "IGL", "Finn Andersen", "Дания"),
                ("ropz", "Rifler", "Robin Kool", "Эстония"),
                ("broky", "AWP", "Helvijs Saukants", "Латвия"),
                ("frozen", "Rifler", "David Čerňanský", "Словакия"),
            ],
            "maps": [("Mirage", 42, 26, 16, 62), ("Inferno", 35, 20, 15, 57)],
            "faq": [("Сколько Major выиграла FaZe?", "FaZe Clan выиграла PGL Major Antwerp 2022.")]
        },
        {
            "name": "G2 Esports", "slug": "g2", "country": "Европа", "site": "https://g2esports.com",
            "prize": "$5.2M", "rank": 6, "majors": 0, "matches": 150, "winrate": 55,
            "players": [
                ("m0NESY", "AWP", "Ilya Osipov", "Россия"),
                ("NiKo", "Rifler", "Nikola Kovač", "Босния"),
                ("huNter-", "Rifler", "Nemanja Kovač", "Босния"),
                ("nexa", "IGL", "Nemanja Isaković", "Сербия"),
                ("Snax", "Rifler", "Janusz Pogorzelski", "Польша"),
            ],
            "maps": [("Mirage", 40, 24, 16, 60), ("Ancient", 28, 16, 12, 57)],
            "faq": [("Кто капитан G2?", "Капитан G2 — nexa.")]
        },
        {
            "name": "Team Spirit", "slug": "spirit", "country": "Россия", "site": "https://teamspirit.gg",
            "prize": "$4.1M", "rank": 3, "majors": 1, "matches": 140, "winrate": 64,
            "players": [
                ("donk", "Rifler", "Danil Kryshkovets", "Россия"),
                ("sh1ro", "AWP", "Dmitry Sokolov", "Россия"),
                ("magixx", "Rifler", "Boris Vorobiev", "Россия"),
                ("zont1x", "Rifler", "Myroslav Plakhotia", "Украина"),
                ("chopper", "IGL", "Leonid Vishnyakov", "Россия"),
            ],
            "maps": [("Mirage", 48, 32, 16, 67), ("Inferno", 35, 22, 13, 63)],
            "faq": [("Сколько Major выиграла Spirit?", "Team Spirit выиграла Perfect World Shanghai Major 2024.")]
        },
        {
            "name": "MOUZ", "slug": "mouz", "country": "Европа", "site": "https://mouz.gg",
            "prize": "$3.8M", "rank": 2, "majors": 0, "matches": 155, "winrate": 61,
            "players": [
                ("torzsi", "AWP", "Ádám Torzsás", "Венгрия"),
                ("xertioN", "Rifler", "Dorian Berman", "Израиль"),
                ("Jimpphat", "Rifler", "Jimi Salo", "Финляндия"),
                ("Brollan", "Rifler", "Ludvig Brolin", "Швеция"),
                ("siuhy", "IGL", "Kamil Szkaradek", "Польша"),
            ],
            "maps": [("Mirage", 44, 28, 16, 64), ("Anubis", 30, 18, 12, 60)],
            "faq": [("Кто капитан MOUZ?", "Капитан MOUZ — siuhy.")]
        },
        {
            "name": "Team Liquid", "slug": "liquid", "country": "США", "site": "https://teamliquid.com",
            "prize": "$4.2M", "rank": 7, "majors": 0, "matches": 130, "winrate": 54,
            "players": [
                ("NAF", "Rifler", "Keith Markovic", "Канада"),
                ("EliGE", "Rifler", "Jonathan Jablonowski", "США"),
                ("oSee", "AWP", "Josh Ohm", "США"),
                ("YEKINDAR", "Rifler", "Mareks Gaļinskis", "Латвия"),
                ("cadiaN", "IGL", "Casper Møller", "Дания"),
            ],
            "maps": [("Mirage", 38, 20, 18, 53), ("Nuke", 32, 18, 14, 56)],
            "faq": [("Кто капитан Liquid?", "Капитан Liquid — cadiaN.")]
        },
        {
            "name": "Astralis", "slug": "astralis", "country": "Дания", "site": "https://astralis.gg",
            "prize": "$12.5M", "rank": 12, "majors": 4, "matches": 110, "winrate": 52,
            "players": [
                ("device", "AWP", "Nicolai Reedtz", "Дания"),
                ("dupreeh", "Rifler", "Peter Rasmussen", "Дания"),
                ("Xyp9x", "Rifler", "Andreas Højsleth", "Дания"),
                ("Magisk", "Rifler", "Emil Reif", "Дания"),
                ("gla1ve", "IGL", "Lukas Rossander", "Дания"),
            ],
            "maps": [("Nuke", 55, 38, 17, 69), ("Inferno", 48, 30, 18, 63)],
            "faq": [("Сколько Major выиграла Astralis?", "Astralis выиграла 4 Major: Atlanta 2017, London 2018, Katowice 2019, Berlin 2019.")]
        },
    ]

    with httpx.Client(timeout=120) as client:
        for t in teams:
            content = make_page(
                t["name"], t["slug"], t["country"], t["site"],
                t["prize"], t["rank"], t["majors"], t["matches"], t["winrate"],
                t["players"], t["maps"], t["faq"]
            )
            result = update_page(client, t["slug"], content)
            print(f"{t['name']}: {result}")

if __name__ == "__main__":
    main()
