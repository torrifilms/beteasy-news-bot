#!/usr/bin/env python3
"""Apply enhanced template to all Dota 2 teams."""

import os
import httpx

WP_URL = os.environ.get("WP_URL", "https://beteasy.ru").rstrip("/")
AUTH = (os.environ.get("WP_USER", ""), os.environ.get("WP_APP_PASS", ""))
DOTA_PARENT = 1433

def update_page(client, slug, content):
    r = client.get(WP_URL + "/wp-json/wp/v2/pages", params={"slug": slug, "parent": DOTA_PARENT}, auth=AUTH)
    if r.status_code == 200 and r.json():
        pid = r.json()[0]["id"]
        r2 = client.post(WP_URL + "/wp-json/wp/v2/pages/" + str(pid), json={"content": content}, auth=AUTH)
        return "updated" if r2.status_code in (200, 201) else "error"
    return "not found"

def make_page(name, slug, country, site, prize, rank, ti, matches, winrate, players, tournaments, faq):
    players_html = ""
    for nick, role, full, nat in players:
        players_html += f'''<div class="tp-player">
<img src="https://ui-avatars.com/api/?name={nick[:2].upper()}&background=141827&color=D6FF3B&size=104" alt="{nick}">
<div class="tp-player-info"><span class="role">{role}</span><b>{nick}</b><span class="name">{full} · {nat}</span></div>
</div>'''

    tours_html = ""
    for place, tour_name, dates, prize_amt, note in tournaments:
        tours_html += f'''<div class="tp-tour-item">
<div class="tp-tour-place">{place}</div>
<div class="tp-tour-info"><b>{tour_name}</b><span>{dates}</span></div>
<div class="tp-tour-prize"><b>{prize_amt}</b><span>{note}</span></div>
</div>'''

    faq_html = ""
    for q, a in faq:
        faq_html += f'<div class="tp-faq"><b>{q}</b><p>{a}</p></div>'

    return f'''<!-- wp:html -->
<style>.tp{{max-width:960px;margin:20px auto;padding:0 16px}}.bread{{display:flex;gap:8px;margin-bottom:16px;font-size:13px}}.bread a{{color:#79829B;text-decoration:none}}.bread a:hover{{color:#D6FF3B}}.bread span{{color:#79829B}}.tp-hero{{display:flex;align-items:center;gap:16px;padding:24px;background:linear-gradient(135deg,#0E1016 0%,#1a1f2e 100%);border:1px solid rgba(214,255,59,.15);border-radius:16px;margin-bottom:16px}}.tp-logo{{width:90px;height:90px;object-fit:contain;background:#fff;border-radius:12px;padding:10px;box-shadow:0 4px 20px rgba(0,0,0,.3)}}.tp-hero h1{{font-family:Unbounded,sans-serif;font-size:26px;margin:0;text-transform:uppercase;color:#EDF0F7}}.tp-meta{{color:#79829B;font-size:13px;margin:6px 0}}.tp-meta a{{color:#D6FF3B}}.tp-titles{{color:#D6FF3B;font-weight:600;margin-top:10px;font-size:14px}}.tp-stats-row{{display:flex;gap:24px;margin-top:14px}}.tp-stat{{text-align:center}}.tp-stat b{{display:block;font-family:"JetBrains Mono",monospace;font-size:20px;color:#D6FF3B}}.tp-stat span{{font-size:10px;color:#79829B;text-transform:uppercase}}.tp-box{{background:#0E1016;border:1px solid rgba(121,130,155,.2);border-radius:12px;padding:18px;margin:12px 0}}.tp-box h3{{font-family:Unbounded,sans-serif;font-size:13px;margin:0 0 14px;text-transform:uppercase;color:#EDF0F7}}.tp-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:12px}}.tp-player{{display:flex;align-items:center;gap:12px;padding:14px;background:#141827;border-radius:10px}}.tp-player img{{width:52px;height:52px;border-radius:50%;border:2px solid rgba(214,255,59,.3)}}.tp-player b{{display:block;color:#EDF0F7;font-size:14px}}.tp-player .role{{font-size:10px;color:#D6FF3B;text-transform:uppercase;font-weight:600}}.tp-player .name{{font-size:11px;color:#79829B}}.tp-match{{display:flex;justify-content:space-between;align-items:center;padding:12px 14px;background:#141827;border-radius:8px;margin-bottom:8px}}.tp-match-left{{display:flex;align-items:center;gap:12px}}.tp-match-date{{font-size:11px;color:#79829B;min-width:65px}}.tp-match-tour{{font-size:10px;color:#D6FF3B;background:rgba(214,255,59,.1);padding:3px 8px;border-radius:4px}}.tp-match-opp{{color:#EDF0F7;font-size:13px}}.tp-match-score{{font-family:"JetBrains Mono",monospace;font-weight:700;font-size:15px}}.tp-match-score.win{{color:#27ae60}}.tp-match-score.loss{{color:#e74c3c}}.tp-tour-item{{display:flex;justify-content:space-between;align-items:center;padding:14px;background:#141827;border-radius:8px;margin-bottom:8px}}.tp-tour-place{{width:42px;height:42px;display:flex;align-items:center;justify-content:center;background:#D6FF3B;color:#07080C;font-weight:700;border-radius:8px;font-size:16px}}.tp-tour-info{{flex:1;margin-left:14px}}.tp-tour-info b{{display:block;color:#EDF0F7;font-size:13px}}.tp-tour-info span{{font-size:11px;color:#79829B}}.tp-tour-prize{{text-align:right}}.tp-tour-prize b{{display:block;color:#D6FF3B;font-family:"JetBrains Mono",monospace;font-size:14px}}.tp-tour-prize span{{font-size:10px;color:#79829B}}.tp-faq{{margin:0 0 10px;padding:14px;background:#141827;border-radius:10px}}.tp-faq b{{display:block;color:#EDF0F7;margin-bottom:6px;font-size:14px}}.tp-faq p{{margin:0;color:#9AA3B8;font-size:13px;line-height:1.5}}.tp-links{{display:flex;gap:12px;margin-top:16px}}.tp-links a{{padding:12px 20px;background:#D6FF3B;color:#07080C;text-decoration:none;border-radius:8px;font-size:13px;font-weight:600}}</style>
<div class="tp">
<div class="bread"><a href="/">Главная</a><span>→</span><a href="/teams/">Команды</a><span>→</span><a href="/teams/dota2/">Dota 2</a><span>→</span><span>{name}</span></div>
<div class="tp-hero">
<img src="https://logo.clearbit.com/{slug}.gg" alt="{name}" class="tp-logo">
<div>
<h1>{name.upper()}</h1>
<p class="tp-meta">Dota 2 · {country} · <a href="{site}" target="_blank" rel="nofollow">{site.replace("https://","").replace("http://","")}</a></p>
<p class="tp-titles">{ti}× TI · #{rank} рейтинг · {prize} призовых</p>
<div class="tp-stats-row">
<div class="tp-stat"><b>{ti}</b><span>TI</span></div>
<div class="tp-stat"><b>{matches}</b><span>Матчей</span></div>
<div class="tp-stat"><b>{winrate}%</b><span>Винрейт</span></div>
<div class="tp-stat"><b>{prize}</b><span>Призовых</span></div>
</div>
</div>
</div>
<div class="tp-box"><h3>Состав 2026</h3><div class="tp-grid">{players_html}</div></div>
<div class="tp-box"><h3>Последние матчи</h3><p class="muted">Обновляется автоматически</p></div>
<div class="tp-box"><h3>Турниры 2026</h3>{tours_html}</div>
<div class="tp-box"><h3>FAQ</h3>{faq_html}</div>
<div class="tp-links">
<a href="/prognozy/?s={slug}">Прогнозы</a>
<a href="/?s={slug}">Новости</a>
</div>
</div>
<script type="application/ld+json">{{"@context":"https://schema.org","@type":"SportsTeam","name":"{name}","sport":"Dota 2","url":"https://beteasy.ru/teams/dota2/{slug}/"}}</script>
<!-- /wp:html -->'''

def main():
    teams = [
        {
            "name": "PARIVISION", "slug": "parivision", "country": "Россия", "site": "https://parivision.gg",
            "prize": "$4.5M", "rank": 1, "ti": 0, "matches": 173, "winrate": 70,
            "players": [
                ("No[o]ne", "Mid", "Vladimir Minenko", "Украина"),
                ("DM", "Carry", "Dmitry Dorokhin", "Россия"),
                ("9Class", "Offlane", "Artem Barshak", "Украина"),
                ("Dukalis", "Support", "Denis Filatov", "Россия"),
                ("SoNNeikO", "Hard Support", "Akbar Butaev", "Россия"),
            ],
            "tournaments": [
                ("1", "Esports World Cup 2026", "Август 2026", "$1M", "чемпионы"),
                ("2", "The International 2026", "Август 2026", "$800K", "финалисты"),
            ],
            "faq": [
                ("Кто капитан PARIVISION?", "Капитан PARIVISION — SoNNeikO, опытный hard support."),
                ("Сколько TI выиграла PARIVISION?", "PARIVISION ещё не выигрывала The International, но заняла 2-е место в 2026."),
            ]
        },
        {
            "name": "Team Falcons", "slug": "falcons", "country": "Саудовская Аравия", "site": "https://teamfalcons.gg",
            "prize": "$7.3M", "rank": 3, "ti": 0, "matches": 219, "winrate": 68,
            "players": [
                ("skiter", "Carry", "Oliver Lepko", "Словакия"),
                ("Malr1ne", "Mid", "Ibrahim Al-Ali", "Саудовская Аравия"),
                ("ATF", "Offlane", "Ammar Al-Assaf", "Иордания"),
                ("Cr1t-", "Support", "Andreas Nielsen", "Дания"),
                ("Sneyking", "Hard Support", "Jingjun Wu", "Китай"),
            ],
            "tournaments": [
                ("3", "The International 2026", "Август 2026", "$500K", "3-е место"),
            ],
            "faq": [
                ("Кто капитан Team Falcons?", "Капитан Falcons — Cr1t-, датский support."),
            ]
        },
        {
            "name": "Team Yandex", "slug": "yandex", "country": "Россия", "site": "https://yandex.ru",
            "prize": "$2.8M", "rank": 4, "ti": 0, "matches": 111, "winrate": 67,
            "players": [
                ("Nightfall", "Carry", "Egor Grigorenko", "Россия"),
                ("gpk", "Mid", "Danil Skutin", "Россия"),
                ("Save-", "Offlane", "Vitalie Melnic", "Молдова"),
                ("TORONTOTOKYO", "Support", "Alexander Khertek", "Россия"),
                ("Solo", "Hard Support", "Alexey Berezin", "Россия"),
            ],
            "tournaments": [
                ("1", "PGL Wallachia Season 9", "Сентябрь 2026", "$400K", "чемпионы"),
                ("1", "BLAST SLAM VIII", "Октябрь 2026", "$500K", "чемпионы"),
            ],
            "faq": [
                ("Кто капитан Team Yandex?", "Капитан Team Yandex — Solo, опытный hard support."),
            ]
        },
        {
            "name": "Aurora Gaming", "slug": "aurora", "country": "Россия", "site": "https://auroragaming.gg",
            "prize": "$1.9M", "rank": 5, "ti": 0, "matches": 184, "winrate": 61,
            "players": [
                ("Pure", "Carry", "Ivan Moskalenko", "Россия"),
                ("lorenof", "Mid", "Roman Paley", "Россия"),
                ("Nightfall", "Offlane", "Egor Grigorenko", "Россия"),
                ("Korb3n", "Support", "Daniel Zadorozhny", "Украина"),
                ("Puppey", "Hard Support", "Clement Ivanov", "Эстония"),
            ],
            "tournaments": [
                ("4", "BLAST SLAM VIII", "Октябрь 2026", "$150K", "4-е место"),
            ],
            "faq": [
                ("Кто капитан Aurora Gaming?", "Капитан Aurora — Puppey, легенда Dota 2."),
            ]
        },
        {
            "name": "Team Liquid", "slug": "liquid", "country": "Европа", "site": "https://teamliquid.com",
            "prize": "$34.2M", "rank": 6, "ti": 1, "matches": 206, "winrate": 59,
            "players": [
                ("miCKe", "Carry", "Michael Vu", "Швеция"),
                ("Nisha", "Mid", "Michał Jankowski", "Польша"),
                ("33", "Offlane", "Neta Shapira", "Израиль"),
                ("Boxi", "Support", "Samuel Svahn", "Швеция"),
                ("Insania", "Hard Support", "Aydin Sarkohi", "Швеция"),
            ],
            "tournaments": [
                ("1", "The International 2017", "Август 2017", "$10.8M", "чемпионы"),
            ],
            "faq": [
                ("Сколько TI выиграла Liquid?", "Team Liquid выиграла The International один раз — в 2017 году."),
            ]
        },
        {
            "name": "Natus Vincere", "slug": "navi", "country": "Украина", "site": "https://navi.gg",
            "prize": "$6.3M", "rank": 7, "ti": 0, "matches": 137, "winrate": 58,
            "players": [
                ("Crystallize", "Carry", "Vladislav Krystanek", "Украина"),
                ("No[o]ne", "Mid", "Vladimir Minenko", "Украина"),
                ("V-Tune", "Offlane", "Viktor Nikulin", "Россия"),
                ("pma", "Support", "Pavel Pavlushko", "Украина"),
                ("Swedenstrong", "Hard Support", "Martin Andréasson", "Швеция"),
            ],
            "tournaments": [
                ("2", "PGL Wallachia Season 9", "Сентябрь 2026", "$200K", "финалисты"),
            ],
            "faq": [
                ("Кто капитан NaVi?", "Капитан NaVi — Swedenstrong."),
            ]
        },
        {
            "name": "Nigma Galaxy", "slug": "nigma", "country": "Европа", "site": "https://nigma-galaxy.com",
            "prize": "$1.9M", "rank": 8, "ti": 0, "matches": 142, "winrate": 55,
            "players": [
                ("SumaiL", "Mid", "Syed Sumail Hassan", "Пакистан"),
                ("Miracle-", "Carry", "Amer Al-Barkawi", "Иордания"),
                ("MinD_ContRoL", "Offlane", "Ivan Borislavov", "Болгария"),
                ("GH", "Support", "Maroun Merhej", "Ливан"),
                ("KuroKy", "Hard Support", "Kuro Salehi Takhasomi", "Германия"),
            ],
            "tournaments": [],
            "faq": [
                ("Кто капитан Nigma Galaxy?", "Капитан Nigma — KuroKy, легенда Dota 2."),
            ]
        },
        {
            "name": "Xtreme Gaming", "slug": "xtreme", "country": "Китай", "site": "https://xtremegaming.gg",
            "prize": "$3.8M", "rank": 9, "ti": 0, "matches": 160, "winrate": 56,
            "players": [
                ("Ame", "Carry", "Wang Chunyu", "Китай"),
                ("XinQ", "Mid", "Zhao Zixing", "Китай"),
                ("Xxs", "Offlane", "Shen Zeyu", "Китай"),
                ("Dy", "Support", "Ding Cong", "Китай"),
                ("xNova", "Hard Support", "Yap Jian Wei", "Малайзия"),
            ],
            "tournaments": [],
            "faq": [
                ("Кто капитан Xtreme Gaming?", "Капитан Xtreme Gaming — xNova."),
            ]
        },
        {
            "name": "1win Team", "slug": "1win", "country": "Россия", "site": "https://1win.team",
            "prize": "$0.7M", "rank": 10, "ti": 0, "matches": 184, "winrate": 59,
            "players": [
                ("Natsumi", "Carry", "Aliaksei Zavadski", "Беларусь"),
                ("Stormstormer", "Mid", "Vladimir Nikogosyan", "Россия"),
                ("Bignum", "Offlane", "Oleksandr Gasanov", "Украина"),
                ("Noticed", "Support", "Evgeniy Ignatenko", "Украина"),
                ("Saksa", "Hard Support", "Martin Sazdov", "Северная Македония"),
            ],
            "tournaments": [],
            "faq": [
                ("Кто капитан 1win Team?", "Капитан 1win — Saksa."),
            ]
        },
        {
            "name": "BetBoom Team", "slug": "betboom", "country": "Россия", "site": "https://betboom.team",
            "prize": "$2.1M", "rank": 11, "ti": 0, "matches": 188, "winrate": 59,
            "players": [
                ("Nightfall", "Carry", "Egor Grigorenko", "Россия"),
                ("gpk", "Mid", "Danil Skutin", "Россия"),
                ("Save-", "Offlane", "Vitalie Melnic", "Молдова"),
                ("TORONTOTOKYO", "Support", "Alexander Khertek", "Россия"),
                ("Solo", "Hard Support", "Alexey Berezin", "Россия"),
            ],
            "tournaments": [
                ("4", "The International 2026", "Август 2026", "$300K", "4-е место"),
            ],
            "faq": [
                ("Кто капитан BetBoom Team?", "Капитан BetBoom — Solo."),
            ]
        },
        {
            "name": "OG", "slug": "og", "country": "Европа", "site": "https://ogs.gg",
            "prize": "$37.8M", "rank": 12, "ti": 2, "matches": 122, "winrate": 46,
            "players": [
                ("Yuragi", "Carry", "Artem Golubiev", "Украина"),
                ("bzm", "Mid", "Bojan Vukadinović", "Сербия"),
                ("DM", "Offlane", "Dmitry Dorokhin", "Россия"),
                ("Taiga", "Support", "Tommy Le", "Норвегия"),
                ("Misha", "Hard Support", "Mikhail Agatov", "Россия"),
            ],
            "tournaments": [
                ("1", "The International 2018", "Август 2018", "$11.2M", "чемпионы"),
                ("1", "The International 2019", "Август 2019", "$15.6M", "чемпионы"),
            ],
            "faq": [
                ("Сколько TI выиграла OG?", "OG выиграла The International дважды подряд — в 2018 и 2019 годах."),
            ]
        },
    ]

    with httpx.Client(timeout=120) as client:
        for t in teams:
            content = make_page(
                t["name"], t["slug"], t["country"], t["site"],
                t["prize"], t["rank"], t["ti"], t["matches"], t["winrate"],
                t["players"], t["tournaments"], t["faq"]
            )
            result = update_page(client, t["slug"], content)
            print(f"{t['name']}: {result}")

if __name__ == "__main__":
    main()
