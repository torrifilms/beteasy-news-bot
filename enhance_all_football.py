#!/usr/bin/env python3
"""Apply enhanced template to all football teams."""

import os
import httpx

WP_URL = os.environ.get("WP_URL", "https://beteasy.ru").rstrip("/")
AUTH = (os.environ.get("WP_USER", ""), os.environ.get("WP_APP_PASS", ""))

def get_parent(client, slug):
    r = client.get(WP_URL + "/wp-json/wp/v2/pages", params={"slug": slug}, auth=AUTH)
    if r.status_code == 200 and r.json():
        return r.json()[0]["id"]
    return None

def update_page(client, slug, content, parent):
    r = client.get(WP_URL + "/wp-json/wp/v2/pages", params={"slug": slug, "parent": parent}, auth=AUTH)
    if r.status_code == 200 and r.json():
        pid = r.json()[0]["id"]
        r2 = client.post(WP_URL + "/wp-json/wp/v2/pages/" + str(pid), json={"content": content}, auth=AUTH)
        return "updated" if r2.status_code in (200, 201) else "error"
    return "not found"

def make_page(name, slug, country, league, site, titles, matches, wins, winrate, coach, players, faq):
    players_html = ""
    for nick, pos, full, nat in players:
        players_html += f'''<div class="tp-player">
<img src="https://ui-avatars.com/api/?name={nick[:2].upper()}&background=141827&color=D6FF3B&size=104" alt="{nick}">
<div class="tp-player-info"><span class="role">{pos}</span><b>{nick}</b><span class="name">{full} · {nat}</span></div>
</div>'''

    faq_html = ""
    for q, a in faq:
        faq_html += f'<div class="tp-faq"><b>{q}</b><p>{a}</p></div>'

    return f'''<!-- wp:html -->
<style>.tp{{max-width:960px;margin:20px auto;padding:0 16px}}.bread{{display:flex;gap:8px;margin-bottom:16px;font-size:13px}}.bread a{{color:#79829B;text-decoration:none}}.bread a:hover{{color:#D6FF3B}}.bread span{{color:#79829B}}.tp-hero{{display:flex;align-items:center;gap:16px;padding:24px;background:linear-gradient(135deg,#0E1016 0%,#1a1f2e 100%);border:1px solid rgba(214,255,59,.15);border-radius:16px;margin-bottom:16px}}.tp-logo{{width:90px;height:90px;object-fit:contain;background:#fff;border-radius:12px;padding:10px;box-shadow:0 4px 20px rgba(0,0,0,.3)}}.tp-hero h1{{font-family:Unbounded,sans-serif;font-size:26px;margin:0;text-transform:uppercase;color:#EDF0F7}}.tp-meta{{color:#79829B;font-size:13px;margin:6px 0}}.tp-meta a{{color:#D6FF3B}}.tp-titles{{color:#D6FF3B;font-weight:600;margin-top:10px;font-size:14px}}.tp-stats-row{{display:flex;gap:24px;margin-top:14px}}.tp-stat{{text-align:center}}.tp-stat b{{display:block;font-family:"JetBrains Mono",monospace;font-size:20px;color:#D6FF3B}}.tp-stat span{{font-size:10px;color:#79829B;text-transform:uppercase}}.tp-box{{background:#0E1016;border:1px solid rgba(121,130,155,.2);border-radius:12px;padding:18px;margin:12px 0}}.tp-box h3{{font-family:Unbounded,sans-serif;font-size:13px;margin:0 0 14px;text-transform:uppercase;color:#EDF0F7}}.tp-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:12px}}.tp-player{{display:flex;align-items:center;gap:12px;padding:14px;background:#141827;border-radius:10px}}.tp-player img{{width:52px;height:52px;border-radius:50%;border:2px solid rgba(214,255,59,.3)}}.tp-player b{{display:block;color:#EDF0F7;font-size:14px}}.tp-player .role{{font-size:10px;color:#D6FF3B;text-transform:uppercase;font-weight:600}}.tp-player .name{{font-size:11px;color:#79829B}}.tp-faq{{margin:0 0 10px;padding:14px;background:#141827;border-radius:10px}}.tp-faq b{{display:block;color:#EDF0F7;margin-bottom:6px;font-size:14px}}.tp-faq p{{margin:0;color:#9AA3B8;font-size:13px;line-height:1.5}}.tp-links{{display:flex;gap:12px;margin-top:16px}}.tp-links a{{padding:12px 20px;background:#D6FF3B;color:#07080C;text-decoration:none;border-radius:8px;font-size:13px;font-weight:600}}</style>
<div class="tp">
<div class="bread"><a href="/">Главная</a><span>→</span><a href="/teams/">Команды</a><span>→</span><a href="/teams/football/">Футбол</a><span>→</span><span>{name}</span></div>
<div class="tp-hero">
<img src="https://logo.clearbit.com/{slug}.com" alt="{name}" class="tp-logo">
<div>
<h1>{name.upper()}</h1>
<p class="tp-meta">{league} · {country} · <a href="{site}" target="_blank" rel="nofollow">{site.replace("https://","").replace("http://","")}</a></p>
<p class="tp-titles">{titles} · Тренер: {coach}</p>
<div class="tp-stats-row">
<div class="tp-stat"><b>{matches}</b><span>Матчей</span></div>
<div class="tp-stat"><b>{wins}</b><span>Побед</span></div>
<div class="tp-stat"><b>{winrate}%</b><span>Винрейт</span></div>
</div>
</div>
</div>
<div class="tp-box"><h3>Состав 2026</h3><div class="tp-grid">{players_html}</div></div>
<div class="tp-box"><h3>Последние матчи</h3><p class="muted">Обновляется автоматически</p></div>
<div class="tp-box"><h3>FAQ</h3>{faq_html}</div>
<div class="tp-links">
<a href="/prognozy/?s={slug}">Прогнозы</a>
<a href="/?s={slug}">Новости</a>
</div>
</div>
<script type="application/ld+json">{{"@context":"https://schema.org","@type":"SportsTeam","name":"{name}","sport":"Football","url":"https://beteasy.ru/teams/football/{slug}/"}}</script>
<!-- /wp:html -->'''

def main():
    teams = [
        {
            "name": "Реал Мадрид", "slug": "real-madrid", "country": "Испания", "league": "Ла Лига",
            "site": "https://realmadrid.com", "titles": "15× ЛЧ · 36× Ла Лига", "matches": 38, "wins": 28, "winrate": 74,
            "coach": "Carlo Ancelotti",
            "players": [
                ("Courtois", "GK", "Thibaut Courtois", "Бельгия"),
                ("Carvajal", "RB", "Dani Carvajal", "Испания"),
                ("Militao", "CB", "Eder Militão", "Бразилия"),
                ("Alaba", "CB", "David Alaba", "Австрия"),
                ("Mendy", "LB", "Ferland Mendy", "Франция"),
                ("Valverde", "CM", "Federico Valverde", "Уругвай"),
                ("Camavinga", "CM", "Eduardo Camavinga", "Франция"),
                ("Bellingham", "AM", "Jude Bellingham", "Англия"),
                ("Vinicius", "LW", "Vinícius Júnior", "Бразилия"),
                ("Mbappe", "ST", "Kylian Mbappé", "Франция"),
                ("Rodrygo", "RW", "Rodrygo", "Бразилия"),
            ],
            "faq": [("Сколько ЛЧ у Реала?", "Реал Мадрид выиграл Лигу чемпионов 15 раз — рекорд турнира.")]
        },
        {
            "name": "Барселона", "slug": "barcelona", "country": "Испания", "league": "Ла Лига",
            "site": "https://fcbarcelona.com", "titles": "5× ЛЧ · 27× Ла Лига", "matches": 38, "wins": 26, "winrate": 68,
            "coach": "Hansi Flick",
            "players": [
                ("Ter Stegen", "GK", "Marc-André ter Stegen", "Германия"),
                ("Kounde", "RB", "Jules Koundé", "Франция"),
                ("Araujo", "CB", "Ronald Araújo", "Уругвай"),
                ("Christensen", "CB", "Andreas Christensen", "Дания"),
                ("Balde", "LB", "Alejandro Balde", "Испания"),
                ("Pedri", "CM", "Pedri", "Испания"),
                ("Gavi", "CM", "Gavi", "Испания"),
                ("De Jong", "CM", "Frenkie de Jong", "Нидерланды"),
                ("Yamal", "RW", "Lamine Yamal", "Испания"),
                ("Lewandowski", "ST", "Robert Lewandowski", "Польша"),
                ("Raphinha", "LW", "Raphinha", "Бразилия"),
            ],
            "faq": [("Кто главный тренер Барселоны?", "Главный тренер Барселоны — Hansi Flick.")]
        },
        {
            "name": "Манчестер Сити", "slug": "manchester-city", "country": "Англия", "league": "АПЛ",
            "site": "https://mancity.com", "titles": "1× ЛЧ · 8× АПЛ", "matches": 38, "wins": 28, "winrate": 74,
            "coach": "Pep Guardiola",
            "players": [
                ("Ederson", "GK", "Ederson", "Бразилия"),
                ("Walker", "RB", "Kyle Walker", "Англия"),
                ("Dias", "CB", "Rúben Dias", "Португалия"),
                ("Stones", "CB", "John Stones", "Англия"),
                ("Gvardiol", "LB", "Joško Gvardiol", "Хорватия"),
                ("Rodri", "CDM", "Rodri", "Испания"),
                ("De Bruyne", "CM", "Kevin De Bruyne", "Бельгия"),
                ("Foden", "AM", "Phil Foden", "Англия"),
                ("Doku", "LW", "Jérémy Doku", "Бельгия"),
                ("Haaland", "ST", "Erling Haaland", "Норвегия"),
                ("Silva", "RW", "Bernardo Silva", "Португалия"),
            ],
            "faq": [("Сколько АПЛ у Сити?", "Манчестер Сити выиграл АПЛ 8 раз под руководством Пепа Гвардиолы.")]
        },
        {
            "name": "ПСЖ", "slug": "psg", "country": "Франция", "league": "Лига 1",
            "site": "https://psg.fr", "titles": "1× ЛЧ · 12× Лига 1", "matches": 34, "wins": 26, "winrate": 76,
            "coach": "Luis Enrique",
            "players": [
                ("Donnarumma", "GK", "Gianluigi Donnarumma", "Италия"),
                ("Hakimi", "RB", "Achraf Hakimi", "Марокко"),
                ("Marquinhos", "CB", "Marquinhos", "Бразилия"),
                ("Skriniar", "CB", "Milan Škriniar", "Словакия"),
                ("Mendes", "LB", "Nuno Mendes", "Португалия"),
                ("Vitinha", "CM", "Vitinha", "Португалия"),
                ("Ruiz", "CM", "Fabián Ruiz", "Испания"),
                ("Dembele", "RW", "Ousmane Dembélé", "Франция"),
                ("Barcola", "LW", "Bradley Barcola", "Франция"),
                ("Kolo Muani", "ST", "Randal Kolo Muani", "Франция"),
                ("Lee", "AM", "Lee Kang-in", "Южная Корея"),
            ],
            "faq": [("Кто главный тренер ПСЖ?", "Главный тренер ПСЖ — Luis Enrique.")]
        },
        {
            "name": "Зенит", "slug": "zenit", "country": "Россия", "league": "РПЛ",
            "site": "https://fc-zenit.ru", "titles": "9× РПЛ · 4× Кубок России", "matches": 30, "wins": 20, "winrate": 67,
            "coach": "Сергей Семак",
            "players": [
                ("Кержаков", "GK", "Михаил Кержаков", "Россия"),
                ("Караваев", "RB", "Вячеслав Караваев", "Россия"),
                ("Ловре", "CB", "Деян Ловрен", "Хорватия"),
                ("Родригао", "CB", "Родригао", "Бразилия"),
                ("Сантос", "LB", "Дуглас Сантос", "Бразилия"),
                ("Барриос", "CDM", "Вильмар Барриос", "Колумбия"),
                ("Вендел", "CM", "Вендел", "Бразилия"),
                ("Клаудиньо", "AM", "Клаудиньо", "Бразилия"),
                ("Мостовой", "RW", "Андрей Мостовой", "Россия"),
                ("Кассьерра", "ST", "Матео Кассьерра", "Колумбия"),
                ("Сергеев", "LW", "Иван Сергеев", "Россия"),
            ],
            "faq": [("Сколько чемпионств у Зенита?", "Зенит выиграл чемпионат России 9 раз.")]
        },
        {
            "name": "Спартак", "slug": "spartak", "country": "Россия", "league": "РПЛ",
            "site": "https://spartak.com", "titles": "10× Чемпионат СССР · 1× РПЛ", "matches": 30, "wins": 16, "winrate": 53,
            "coach": "Деян Станкович",
            "players": [
                ("Максименко", "GK", "Александр Максименко", "Россия"),
                ("Рыбус", "RB", "Мацей Рыбус", "Польша"),
                ("Дуарте", "CB", "Алекс Дуарте", "Бразилия"),
                ("Бабич", "CB", "Срджан Бабич", "Сербия"),
                ("Мартинс", "LB", "Кристофер Мартинс", "Люксембург"),
                ("Зобнин", "CM", "Роман Зобнин", "Россия"),
                ("Умяров", "CM", "Наиль Умяров", "Россия"),
                ("Промес", "AM", "Квинси Промес", "Нидерланды"),
                ("Соболев", "ST", "Александр Соболев", "Россия"),
                ("Ларссон", "LW", "Джордан Ларссон", "Швеция"),
                ("Игнатов", "RW", "Михаил Игнатов", "Россия"),
            ],
            "faq": [("Кто главный тренер Спартака?", "Главный тренер Спартака — Деян Станкович.")]
        },
    ]

    with httpx.Client(timeout=120) as client:
        parent = get_parent(client, "football")
        if not parent:
            print("ERR: football parent not found")
            return
        print(f"Football parent: {parent}")
        for t in teams:
            content = make_page(
                t["name"], t["slug"], t["country"], t["league"], t["site"],
                t["titles"], t["matches"], t["wins"], t["winrate"], t["coach"],
                t["players"], t["faq"]
            )
            result = update_page(client, t["slug"], content, parent)
            print(f"{t['name']}: {result}")

if __name__ == "__main__":
    main()
