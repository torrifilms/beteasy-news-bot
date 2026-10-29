#!/usr/bin/env python3
"""Create team pages MVP with fan counter."""

import os
import httpx
import json
import re

WP_URL = os.environ.get("WP_URL", "https://beteasy.ru").rstrip("/")
AUTH = (os.environ.get("WP_USER", ""), os.environ.get("WP_APP_PASS", ""))

TRANSLIT = {
    "а": "a", "б": "b", "в": "v", "г": "g", "д": "d", "е": "e",
    "ё": "yo", "ж": "zh", "з": "z", "и": "i", "й": "y", "к": "k",
    "л": "l", "м": "m", "н": "n", "о": "o", "п": "p", "р": "r",
    "с": "s", "т": "t", "у": "u", "ф": "f", "х": "kh", "ц": "ts",
    "ч": "ch", "ш": "sh", "щ": "shch", "ъ": "", "ы": "y", "ь": "",
    "э": "e", "ю": "yu", "я": "ya",
}

def slugify(text):
    result = [TRANSLIT.get(ch, ch) for ch in text.lower()]
    s = "".join(result)
    s = re.sub(r"[^a-z0-9\-]", "-", s)
    s = re.sub(r"-+", "-", s).strip("-")
    return s[:50] or "team"

TEAMS = [
    {
        "name": "Реал Мадрид",
        "sport": "Футбол",
        "league": "Ла Лига",
        "country": "Испания",
        "desc": "Один из самых титулованных клубов мира. 15 побед в Лиге чемпионов, рекордсмен по числу трофеев в Испании.",
        "founded": "1902",
    },
    {
        "name": "Барселона",
        "sport": "Футбол",
        "league": "Ла Лига",
        "country": "Испания",
        "desc": "Каталонский клуб с философией тики-така. 5 побед в Лиге чемпионов, воспитанники Ла Масии.",
        "founded": "1899",
    },
    {
        "name": "Манчестер Сити",
        "sport": "Футбол",
        "league": "АПЛ",
        "country": "Англия",
        "desc": "Доминирующий клуб Англии последних лет. Победа в Лиге чемпионов 2023, множество титулов АПЛ.",
        "founded": "1880",
    },
    {
        "name": "Зенит",
        "sport": "Футбол",
        "league": "РПЛ",
        "country": "Россия",
        "desc": "Самый титулованный клуб России. Многократный чемпион РПЛ, обладатель Кубка УЕФА 2008.",
        "founded": "1925",
    },
    {
        "name": "Спартак Москва",
        "sport": "Футбол",
        "league": "РПЛ",
        "country": "Россия",
        "desc": "Народный клуб России. 10 чемпионств СССР, один из самых популярных клубов страны.",
        "founded": "1922",
    },
    {
        "name": "Natus Vincere",
        "sport": "CS2",
        "league": "Киберспорт",
        "country": "Украина",
        "desc": "Легендарная организация. Победа на PGL Major Stockholm 2021, одна из самых узнаваемых команд CS.",
        "founded": "2009",
    },
    {
        "name": "Team Spirit",
        "sport": "Dota 2",
        "league": "Киберспорт",
        "country": "Россия",
        "desc": "Победители The International 2021. Одна из сильнейших команд мира по Dota 2.",
        "founded": "2015",
    },
    {
        "name": "Gaimin Gladiators",
        "sport": "Dota 2",
        "league": "Киберспорт",
        "country": "Европа",
        "desc": "Топ-команда по Dota 2. Регулярные участники мейджоров и претенденты на The International.",
        "founded": "2022",
    },
    {
        "name": "FaZe Clan",
        "sport": "CS2",
        "league": "Киберспорт",
        "country": "Международная",
        "desc": "Одна из самых известных киберспортивных организаций. Множество титулов в CS и других дисциплинах.",
        "founded": "2010",
    },
    {
        "name": "ПСЖ",
        "sport": "Футбол",
        "league": "Лига 1",
        "country": "Франция",
        "desc": "Доминирующий клуб Франции. Регулярный участник Лиги чемпионов, звёздный состав.",
        "founded": "1970",
    },
]

def build_content(team):
    slug = slugify(team["name"])
    return f'''
<div class="team-page">
    <div class="team-header">
        <h2>{team["name"]}</h2>
        <p class="team-meta">{team["sport"]} · {team["league"]} · {team["country"]}</p>
        <p class="team-founded">Основан: {team["founded"]}</p>
    </div>
    <div class="team-fans">
        <button class="btn-fan" data-team="{slug}" onclick="toggleFan(this)">❤️ Болею</button>
        <span class="fan-count" id="fans-{slug}">0</span> болельщиков
    </div>
    <div class="team-about">
        <h3>О команде</h3>
        <p>{team["desc"]}</p>
    </div>
    <div class="team-news">
        <h3>Новости и прогнозы</h3>
        <p>Актуальные материалы о команде «{team["name"]}» появляются в разделах 
        <a href="/prognozy/">Прогнозы</a> и <a href="/">Новости</a>.</p>
    </div>
</div>
<script>
function toggleFan(btn) {{
    var team = btn.dataset.team;
    var countEl = document.getElementById("fans-" + team);
    var count = parseInt(countEl.textContent) || 0;
    if (btn.classList.contains("active")) {{
        btn.classList.remove("active");
        btn.textContent = "❤️ Болею";
        count = Math.max(0, count - 1);
    }} else {{
        btn.classList.add("active");
        btn.textContent = "❤️ Болею!";
        count += 1;
    }}
    countEl.textContent = count;
    localStorage.setItem("fan-" + team, btn.classList.contains("active") ? "1" : "0");
}}
document.addEventListener("DOMContentLoaded", function() {{
    var btns = document.querySelectorAll(".btn-fan");
    btns.forEach(function(btn) {{
        var team = btn.dataset.team;
        if (localStorage.getItem("fan-" + team) === "1") {{
            btn.classList.add("active");
            btn.textContent = "❤️ Болею!";
        }}
    }});
}});
</script>
<style>
.team-page {{ max-width: 700px; margin: 0 auto; }}
.team-header {{ margin-bottom: 20px; }}
.team-meta {{ color: #666; }}
.team-fans {{ background: #f5f5f5; padding: 15px; border-radius: 8px; margin: 20px 0; }}
.btn-fan {{ background: #e74c3c; color: #fff; border: none; padding: 10px 20px; border-radius: 20px; cursor: pointer; font-size: 16px; }}
.btn-fan.active {{ background: #c0392b; }}
.fan-count {{ font-weight: bold; font-size: 18px; margin-left: 10px; }}
.team-about, .team-news {{ margin: 20px 0; }}
</style>
'''

def main():
    with httpx.Client(timeout=60) as client:
        created = 0
        for team in TEAMS:
            slug = "team-" + slugify(team["name"])
            # Check if exists
            r = client.get(f"{WP_URL}/wp-json/wp/v2/pages", params={"slug": slug}, auth=AUTH)
            if r.status_code == 200 and r.json():
                print(f"SKIP {team['name']}")
                continue
            content = build_content(team)
            payload = {
                "title": f"{team['name']} — состав, новости, прогнозы",
                "content": content,
                "status": "publish",
                "slug": slug,
            }
            r = client.post(f"{WP_URL}/wp-json/wp/v2/pages", json=payload, auth=AUTH)
            if r.status_code in (200, 201):
                link = r.json().get("link", "")
                print(f"OK {team['name']} → {link}")
                created += 1
            else:
                print(f"ERR {team['name']} {r.status_code}")
        print(f"\nCreated: {created}")

if __name__ == "__main__":
    main()
