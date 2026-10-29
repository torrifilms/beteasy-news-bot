#!/usr/bin/env python3
"""Fix layout and update squads to October 2026."""

import os
import httpx
import re

WP_URL = os.environ.get("WP_URL", "https://beteasy.ru").rstrip("/")
AUTH = (os.environ.get("WP_USER", ""), os.environ.get("WP_APP_PASS", ""))

# 2026 squads
SQUADS = {
    "team-real-madrid": {
        "coach": "Жозе Моуринью",
        "players": [
            ("Тибо Куртуа", "ВР", "1"),
            ("Андрей Лунин", "ВР", "13"),
            ("Эдер Милитао", "ЦЗ", "3"),
            ("Дин Хёйсен", "ЦЗ", "4"),
            ("Ибраима Конате", "ЦЗ", "16"),
            ("Антонио Рюдигер", "ЦЗ", "22"),
            ("Трент Александер-Арнольд", "ПЗ", "12"),
            ("Марк Кукурелья", "ЛЗ", "17"),
            ("Дензел Дюмфрис", "ПЗ", "24"),
            ("Федерико Вальверде", "ЦП", "8"),
            ("Джуд Беллингем", "АП", "5"),
            ("Орельен Тчуамени", "ЦП", "14"),
            ("Арда Гюлер", "АП", "15"),
            ("Бернарду Силва", "ЦП", "20"),
            ("Килиан Мбаппе", "ЦН", "10"),
            ("Винисиус Жуниор", "ЛН", "7"),
            ("Эндрик", "ЦН", "9"),
            ("Браим Диас", "АП", "21"),
        ]
    },
    "team-barselona": {
        "coach": "Ханси Флик",
        "players": [
            ("Жоан Гарсия", "ВР", "1"),
            ("Войцех Щенсны", "ВР", "13"),
            ("Пау Кубарси", "ЦЗ", "5"),
            ("Жерар Мартин", "ЦЗ", "18"),
            ("Жюль Кунде", "ПЗ", "23"),
            ("Эрик Гарсия", "ЦЗ", "24"),
            ("Жоау Канселу", "ПЗ", "2"),
            ("Алехандро Бальде", "ЛЗ", "3"),
            ("Педри", "ЦП", "8"),
            ("Гави", "ЦП", "6"),
            ("Френки де Йонг", "ЦП", "21"),
            ("Фермин Лопес", "АП", "7"),
            ("Родри", "ЦП", "16"),
            ("Ламин Ямаль", "ПН", "10"),
            ("Рафинья", "ЛН", "11"),
            ("Габриэл Жезус", "ЦН", "9"),
            ("Карим Адейеми", "ЛН", "14"),
            ("Энтони Гордон", "ЛН", "17"),
        ]
    },
}

STYLE = '''
<style>
.team-page{max-width:960px;margin:0 auto;padding:20px}
.team-hero{display:flex;justify-content:space-between;align-items:flex-start;gap:24px;padding:28px;background:var(--panel);border:1px solid var(--line);border-radius:16px;margin-bottom:20px;flex-wrap:wrap}
.team-hero h1{font-family:Unbounded,sans-serif;font-size:28px;margin:0 0 8px;text-transform:uppercase}
.team-hero .meta,.team-hero .founded,.team-hero .coach{color:var(--mut);font-size:14px;margin:4px 0}
.team-hero .titles{color:var(--lime);font-weight:600;margin-top:10px}
.fan-box{text-align:center}
.btn-fan{background:var(--lime);color:#07080C;border:none;padding:12px 24px;border-radius:100px;font-weight:700;cursor:pointer}
.btn-fan.active{background:var(--violet);color:#fff}
.fan-count{margin-top:8px;font-size:13px;color:var(--mut)}
.fan-count span{font-family:"JetBrains Mono",monospace;font-size:20px;color:var(--lime);font-weight:700}
.team-section{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:20px;margin:16px 0}
.team-section h3{font-family:Unbounded,sans-serif;font-size:15px;margin:0 0 14px;text-transform:uppercase}
.form-row{display:flex;gap:6px}
.form-badge{width:32px;height:32px;display:flex;align-items:center;justify-content:center;border-radius:6px;font-weight:700;font-size:13px;color:#fff}
.stats-grid{display:grid;grid-template-columns:repeat(5,1fr);gap:10px}
.stat{text-align:center;background:var(--panel2);padding:12px 6px;border-radius:8px}
.stat b{display:block;font-family:"JetBrains Mono",monospace;font-size:20px;color:var(--lime)}
.stat span{font-size:10px;color:var(--mut);text-transform:uppercase}
.coach-box{display:flex;align-items:center;gap:12px;padding:12px;background:var(--panel2);border-radius:10px;margin-bottom:14px}
.coach-box img{width:48px;height:48px;border-radius:50%}
.coach-box span{font-size:10px;color:var(--mut);text-transform:uppercase}
.coach-box b{display:block}
.players-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:8px}
.player{display:flex;align-items:center;gap:10px;background:var(--panel2);padding:10px;border-radius:8px}
.player img{width:40px;height:40px;border-radius:50%}
.player .num{font-size:10px;color:var(--lime)}
.player b{font-size:13px;display:block}
.player span{font-size:11px;color:var(--mut)}
.news-item{display:block;padding:10px;background:var(--panel2);border-radius:8px;margin:6px 0;text-decoration:none}
.news-item span{font-size:11px;color:var(--mut)}
.news-item b{display:block;margin-top:2px}
@media(max-width:600px){.stats-grid{grid-template-columns:repeat(3,1fr)}.team-hero{flex-direction:column}}
</style>
'''

def build_squad(slug, data):
    coach_photo = f"https://ui-avatars.com/api/?name={data['coach'].replace(' ', '+')}&background=D6FF3B&color=07080C&size=80"
    players_html = ""
    for name, pos, num in data["players"]:
        photo = f"https://ui-avatars.com/api/?name={name.replace(' ', '+')}&background=141827&color=EDF0F7&size=60"
        players_html += f'''<div class="player"><img src="{photo}" alt="{name}"><div><span class="num">{num}</span><b>{name}</b><span>{pos}</span></div></div>'''
    return f'''
    <section class="team-section">
        <h3>Состав 2026/27</h3>
        <div class="coach-box"><img src="{coach_photo}" alt="{data['coach']}"><div><span>Тренер</span><b>{data['coach']}</b></div></div>
        <div class="players-grid">{players_html}</div>
    </section>
    '''

def main():
    with httpx.Client(timeout=60) as client:
        for slug, data in SQUADS.items():
            r = client.get(f"{WP_URL}/wp-json/wp/v2/pages", params={"slug": slug}, auth=AUTH)
            if r.status_code != 200 or not r.json():
                continue
            page = r.json()[0]
            content = page.get("content", {}).get("raw") or page.get("content", {}).get("rendered", "")
            # Remove old style and squad
            content = re.sub(r'<style>.*?</style>', '', content, flags=re.DOTALL)
            content = re.sub(r'<section class="team-section team-squad">.*?</section>', '', content, flags=re.DOTALL)
            content = re.sub(r'<section class="team-section">.*?</section>', '', content, flags=re.DOTALL)
            # Add new
            content = STYLE + content
            squad = build_squad(slug, data)
            content = content.replace("</div>", squad + "</div>", 1)
            r2 = client.post(f"{WP_URL}/wp-json/wp/v2/pages/{page['id']}", json={"content": content}, auth=AUTH)
            print(f"{'OK' if r2.status_code in (200,201) else 'ERR'} {slug}")

if __name__ == "__main__":
    main()
