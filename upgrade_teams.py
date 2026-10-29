#!/usr/bin/env python3
"""Upgrade team pages with rich blocks based on competitor analysis."""

import os
import httpx
import re

WP_URL = os.environ.get("WP_URL", "https://beteasy.ru").rstrip("/")
AUTH = (os.environ.get("WP_USER", ""), os.environ.get("WP_APP_PASS", ""))

TEAMS = {
    "team-real-madrid": {
        "name": "Реал Мадрид",
        "sport": "Футбол",
        "league": "Ла Лига",
        "country": "Испания",
        "founded": "1902",
        "stadium": "Сантьяго Бернабеу",
        "coach": "Карло Анчелотти",
        "titles": "15 ЛЧ, 36 Ла Лига",
        "form": ["W", "W", "D", "W", "L"],
        "players": ["Винисиус Жуниор", "Джуд Беллингем", "Килиан Мбаппе", "Тони Кроос", "Тибо Куртуа"],
        "stats": {"goals": 28, "conceded": 12, "wins": 8, "draws": 2, "losses": 1},
    },
    "team-barselona": {
        "name": "Барселона",
        "sport": "Футбол",
        "league": "Ла Лига",
        "country": "Испания",
        "founded": "1899",
        "stadium": "Камп Ноу",
        "coach": "Ханси Флик",
        "titles": "5 ЛЧ, 27 Ла Лига",
        "form": ["W", "W", "W", "D", "W"],
        "players": ["Роберт Левандовски", "Ламин Ямаль", "Педри", "Рафинья", "Марк-Андре тер Стеген"],
        "stats": {"goals": 32, "conceded": 14, "wins": 9, "draws": 1, "losses": 1},
    },
    "team-manchester-siti": {
        "name": "Манчестер Сити",
        "sport": "Футбол",
        "league": "АПЛ",
        "country": "Англия",
        "founded": "1880",
        "stadium": "Этихад",
        "coach": "Пеп Гвардиола",
        "titles": "1 ЛЧ, 8 АПЛ",
        "form": ["W", "W", "W", "W", "D"],
        "players": ["Эрлинг Холанд", "Кевин Де Брюйне", "Фил Фоден", "Родри", "Эдерсон"],
        "stats": {"goals": 30, "conceded": 10, "wins": 9, "draws": 1, "losses": 0},
    },
    "team-zenit": {
        "name": "Зенит",
        "sport": "Футбол",
        "league": "РПЛ",
        "country": "Россия",
        "founded": "1925",
        "stadium": "Газпром Арена",
        "coach": "Сергей Семак",
        "titles": "10 РПЛ, Кубок УЕФА 2008",
        "form": ["W", "W", "D", "W", "W"],
        "players": ["Вендел", "Клаудиньо", "Малком", "Дуглас Сантос", "Михаил Кержаков"],
        "stats": {"goals": 22, "conceded": 8, "wins": 7, "draws": 2, "losses": 1},
    },
    "team-natus-vincere": {
        "name": "Natus Vincere",
        "sport": "CS2",
        "league": "Киберспорт",
        "country": "Украина",
        "founded": "2009",
        "stadium": "—",
        "coach": "B1ad3",
        "titles": "PGL Major Stockholm 2021",
        "form": ["W", "W", "L", "W", "W"],
        "players": ["s1mple", "b1t", "electronic", "Perfecto", "npl"],
        "stats": {"goals": 0, "conceded": 0, "wins": 12, "draws": 0, "losses": 4},
    },
    "team-team-spirit": {
        "name": "Team Spirit",
        "sport": "Dota 2",
        "league": "Киберспорт",
        "country": "Россия",
        "founded": "2015",
        "stadium": "—",
        "coach": "Silent",
        "titles": "The International 2021",
        "form": ["W", "W", "W", "L", "W"],
        "players": ["Yatoro", "Larl", "Collapse", "Mira", "Miposhka"],
        "stats": {"goals": 0, "conceded": 0, "wins": 15, "draws": 0, "losses": 3},
    },
}

def form_html(form):
    colors = {"W": "#27ae60", "D": "#f39c12", "L": "#e74c3c"}
    return "".join(f'<span class="form-badge" style="background:{colors.get(f,"#999")}">{f}</span>' for f in form)

def build_content(slug, t):
    players_html = "".join(f"<li>{p}</li>" for p in t["players"])
    return f'''
<div class="team-page">
    <header class="team-hero">
        <div class="team-info">
            <h1>{t["name"]}</h1>
            <p class="meta">{t["sport"]} · {t["league"]} · {t["country"]}</p>
            <p class="founded">Основан: {t["founded"]} · Стадион: {t["stadium"]}</p>
            <p class="coach">Тренер: <b>{t["coach"]}</b></p>
            <p class="titles">Титулы: {t["titles"]}</p>
        </div>
        <div class="fan-box">
            <button class="btn-fan" data-team="{slug}" onclick="toggleFan(this)">❤️ Болею</button>
            <div class="fan-count"><span id="fans-{slug}">0</span> болельщиков</div>
        </div>
    </header>

    <section class="team-form">
        <h3>Форма (последние 5)</h3>
        <div class="form-row">{form_html(t["form"])}</div>
    </section>

    <section class="team-stats">
        <h3>Статистика сезона</h3>
        <div class="stats-grid">
            <div class="stat"><b>{t["stats"]["wins"]}</b><span>Побед</span></div>
            <div class="stat"><b>{t["stats"]["draws"]}</b><span>Ничьих</span></div>
            <div class="stat"><b>{t["stats"]["losses"]}</b><span>Поражений</span></div>
            <div class="stat"><b>{t["stats"]["goals"]}</b><span>Забито</span></div>
            <div class="stat"><b>{t["stats"]["conceded"]}</b><span>Пропущено</span></div>
        </div>
    </section>

    <section class="team-squad">
        <h3>Ключевые игроки</h3>
        <ul class="squad-list">{players_html}</ul>
    </section>

    <section class="team-news">
        <h3>Новости и прогнозы</h3>
        <p>Материалы о «{t["name"]}» в разделах 
        <a href="/prognozy/">Прогнозы</a> и <a href="/">Новости</a>.</p>
        <p><a href="/prognozy/?s={t["name"].replace(" ", "+")}">Все прогнозы на {t["name"]}</a></p>
    </section>

    <section class="team-faq">
        <h3>Частые вопросы</h3>
        <details><summary>Где смотреть матчи {t["name"]}?</summary><p>Матчи транслируются на официальных каналах лиги и стриминговых сервисах.</p></details>
        <details><summary>Какие ставки популярны на {t["name"]}?</summary><p>Чаще всего ставят на исход, тотал и фору. Смотрите актуальные коэффициенты в разделе прогнозов.</p></details>
    </section>
</div>

<script>
function toggleFan(btn) {{
    var team = btn.dataset.team;
    var el = document.getElementById("fans-" + team);
    var count = parseInt(el.textContent) || 0;
    if (btn.classList.contains("active")) {{
        btn.classList.remove("active");
        btn.textContent = "❤️ Болею";
        count = Math.max(0, count - 1);
    }} else {{
        btn.classList.add("active");
        btn.textContent = "❤️ Болею!";
        count += 1;
    }}
    el.textContent = count;
    localStorage.setItem("fan-" + team, btn.classList.contains("active") ? "1" : "0");
}}
document.addEventListener("DOMContentLoaded", function() {{
    document.querySelectorAll(".btn-fan").forEach(function(btn) {{
        var team = btn.dataset.team;
        if (localStorage.getItem("fan-" + team) === "1") {{
            btn.classList.add("active");
            btn.textContent = "❤️ Болею!";
        }}
    }});
}});
</script>

<style>
.team-page {{ max-width: 800px; margin: 0 auto; font-family: system-ui, sans-serif; }}
.team-hero {{ display: flex; justify-content: space-between; align-items: flex-start; gap: 20px; padding: 20px; background: linear-gradient(135deg, #1a1a2e, #16213e); color: #fff; border-radius: 12px; margin-bottom: 20px; }}
.team-hero h1 {{ margin: 0 0 8px; font-size: 28px; }}
.team-hero .meta {{ opacity: 0.8; margin: 4px 0; }}
.fan-box {{ text-align: center; }}
.btn-fan {{ background: #e74c3c; color: #fff; border: none; padding: 12px 24px; border-radius: 24px; cursor: pointer; font-size: 16px; }}
.btn-fan.active {{ background: #c0392b; }}
.fan-count {{ margin-top: 8px; font-size: 14px; }}
.team-form, .team-stats, .team-squad, .team-news, .team-faq {{ background: #f8f9fa; padding: 16px; border-radius: 8px; margin: 16px 0; }}
.form-badge {{ display: inline-block; width: 28px; height: 28px; line-height: 28px; text-align: center; color: #fff; border-radius: 4px; margin-right: 4px; font-weight: bold; }}
.stats-grid {{ display: grid; grid-template-columns: repeat(5, 1fr); gap: 10px; }}
.stat {{ text-align: center; background: #fff; padding: 10px; border-radius: 6px; }}
.stat b {{ display: block; font-size: 20px; }}
.stat span {{ font-size: 12px; color: #666; }}
.squad-list {{ columns: 2; margin: 0; padding-left: 20px; }}
.team-faq details {{ margin: 8px 0; }}
.team-faq summary {{ cursor: pointer; font-weight: 500; }}
@media (max-width: 600px) {{
    .team-hero {{ flex-direction: column; }}
    .stats-grid {{ grid-template-columns: repeat(3, 1fr); }}
    .squad-list {{ columns: 1; }}
}}
</style>
'''

def main():
    with httpx.Client(timeout=60) as client:
        updated = 0
        for slug, team in TEAMS.items():
            r = client.get(f"{WP_URL}/wp-json/wp/v2/pages", params={"slug": slug}, auth=AUTH)
            if r.status_code != 200 or not r.json():
                print(f"NOT FOUND {slug}")
                continue
            page_id = r.json()[0]["id"]
            content = build_content(slug, team)
            r2 = client.post(
                f"{WP_URL}/wp-json/wp/v2/pages/{page_id}",
                json={"content": content},
                auth=AUTH,
            )
            if r2.status_code in (200, 201):
                print(f"OK {team['name']}")
                updated += 1
            else:
                print(f"ERR {slug} {r2.status_code}")
        print(f"\nUpdated: {updated}")

if __name__ == "__main__":
    main()
