#!/usr/bin/env python3
"""Add last 3 news and full squad with photos to team pages."""

import os
import httpx
import re

WP_URL = os.environ.get("WP_URL", "https://beteasy.ru").rstrip("/")
AUTH = (os.environ.get("WP_USER", ""), os.environ.get("WP_APP_PASS", ""))

# Full squads with placeholder photos (using UI Avatars or similar)
SQUADS = {
    "team-real-madrid": {
        "coach": {"name": "Карло Анчелотти", "photo": "https://ui-avatars.com/api/?name=Carlo+Ancelotti&background=D6FF3B&color=07080C&size=80"},
        "players": [
            {"name": "Тибо Куртуа", "pos": "ВР", "num": "1"},
            {"name": "Дани Карвахаль", "pos": "ПЗ", "num": "2"},
            {"name": "Эдер Милитао", "pos": "ЦЗ", "num": "3"},
            {"name": "Давид Алаба", "pos": "ЦЗ", "num": "4"},
            {"name": "Ферлан Менди", "pos": "ЛЗ", "num": "23"},
            {"name": "Тони Кроос", "pos": "ЦП", "num": "8"},
            {"name": "Лука Модрич", "pos": "ЦП", "num": "10"},
            {"name": "Феде Вальверде", "pos": "ЦП", "num": "15"},
            {"name": "Джуд Беллингем", "pos": "АП", "num": "5"},
            {"name": "Винисиус Жуниор", "pos": "ЛН", "num": "7"},
            {"name": "Килиан Мбаппе", "pos": "ЦН", "num": "9"},
        ]
    },
    "team-barselona": {
        "coach": {"name": "Ханси Флик", "photo": "https://ui-avatars.com/api/?name=Hansi+Flick&background=D6FF3B&color=07080C&size=80"},
        "players": [
            {"name": "Марк-Андре тер Стеген", "pos": "ВР", "num": "1"},
            {"name": "Жюль Кунде", "pos": "ПЗ", "num": "23"},
            {"name": "Рональд Араухо", "pos": "ЦЗ", "num": "4"},
            {"name": "Иньиго Мартинес", "pos": "ЦЗ", "num": "5"},
            {"name": "Алехандро Бальде", "pos": "ЛЗ", "num": "3"},
            {"name": "Педри", "pos": "ЦП", "num": "8"},
            {"name": "Гави", "pos": "ЦП", "num": "6"},
            {"name": "Френки де Йонг", "pos": "ЦП", "num": "21"},
            {"name": "Ламин Ямаль", "pos": "ПН", "num": "19"},
            {"name": "Роберт Левандовски", "pos": "ЦН", "num": "9"},
            {"name": "Рафинья", "pos": "ЛН", "num": "11"},
        ]
    },
    "team-natus-vincere": {
        "coach": {"name": "B1ad3", "photo": "https://ui-avatars.com/api/?name=B1ad3&background=8F6BFF&color=fff&size=80"},
        "players": [
            {"name": "s1mple", "pos": "AWP", "num": ""},
            {"name": "b1t", "pos": "Rifler", "num": ""},
            {"name": "electronic", "pos": "Rifler", "num": ""},
            {"name": "Perfecto", "pos": "Support", "num": ""},
            {"name": "npl", "pos": "Entry", "num": ""},
        ]
    },
    "team-team-spirit": {
        "coach": {"name": "Silent", "photo": "https://ui-avatars.com/api/?name=Silent&background=8F6BFF&color=fff&size=80"},
        "players": [
            {"name": "Yatoro", "pos": "Carry", "num": ""},
            {"name": "Larl", "pos": "Mid", "num": ""},
            {"name": "Collapse", "pos": "Offlane", "num": ""},
            {"name": "Mira", "pos": "Support", "num": ""},
            {"name": "Miposhka", "pos": "Support", "num": ""},
        ]
    },
}

def build_squad_html(slug, data):
    coach = data["coach"]
    players = data["players"]
    players_html = ""
    for p in players:
        photo = f"https://ui-avatars.com/api/?name={p['name'].replace(' ', '+')}&background=141827&color=EDF0F7&size=60"
        num = f"<span class='num'>{p['num']}</span>" if p['num'] else ""
        players_html += f'''
        <div class="player">
            <img src="{photo}" alt="{p['name']}" loading="lazy">
            <div class="pinfo">{num}<b>{p['name']}</b><span>{p['pos']}</span></div>
        </div>'''
    return f'''
    <section class="team-section team-squad">
        <h3>Состав</h3>
        <div class="coach">
            <img src="{coach['photo']}" alt="{coach['name']}">
            <div><span>Тренер</span><b>{coach['name']}</b></div>
        </div>
        <div class="players-grid">{players_html}</div>
    </section>
    <style>
    .coach{{display:flex;align-items:center;gap:12px;margin-bottom:16px;padding:12px;background:var(--panel2);border-radius:10px}}
    .coach img{{width:56px;height:56px;border-radius:50%}}
    .coach span{{font-size:11px;color:var(--mut);text-transform:uppercase}}
    .coach b{{display:block}}
    .players-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:10px}}
    .player{{display:flex;align-items:center;gap:10px;background:var(--panel2);padding:10px;border-radius:8px}}
    .player img{{width:44px;height:44px;border-radius:50%}}
    .player .pinfo{{display:flex;flex-direction:column}}
    .player .num{{font-size:10px;color:var(--lime)}}
    .player b{{font-size:13px}}
    .player span{{font-size:11px;color:var(--mut)}}
    </style>
    '''

def build_news_html(team_name):
    return f'''
    <section class="team-section team-news" data-team="{team_name}">
        <h3>Последние новости</h3>
        <div class="news-list" id="news-{team_name.replace(' ', '-').lower()}">
            <p class="loading">Загрузка...</p>
        </div>
    </section>
    <script>
    (function(){{
        var team = "{team_name}";
        var container = document.getElementById("news-" + team.replace(/\\s+/g, "-").toLowerCase());
        if(!container) return;
        fetch("/wp-json/wp/v2/posts?search=" + encodeURIComponent(team) + "&per_page=3&_fields=id,title,link,date")
            .then(function(r){{return r.json()}})
            .then(function(posts){{
                if(!posts.length){{
                    container.innerHTML = "<p>Новостей пока нет</p>";
                    return;
                }}
                var html = "";
                posts.forEach(function(p){{
                    var d = new Date(p.date).toLocaleDateString("ru-RU");
                    html += "<a href='" + p.link + "' class='news-item'><span>" + d + "</span><b>" + p.title.rendered + "</b></a>";
                }});
                container.innerHTML = html;
            }})
            .catch(function(){{container.innerHTML = "<p>Не удалось загрузить</p>"}});
    }})();
    </script>
    <style>
    .news-item{{display:block;padding:12px;background:var(--panel2);border-radius:8px;margin:8px 0;text-decoration:none}}
    .news-item span{{font-size:11px;color:var(--mut)}}
    .news-item b{{display:block;margin-top:4px;color:var(--text)}}
    .news-item:hover{{background:var(--panel)}}
    </style>
    '''

def main():
    with httpx.Client(timeout=60) as client:
        updated = 0
        for slug, data in SQUADS.items():
            r = client.get(f"{WP_URL}/wp-json/wp/v2/pages", params={"slug": slug}, auth=AUTH)
            if r.status_code != 200 or not r.json():
                continue
            page = r.json()[0]
            content = page.get("content", {}).get("raw") or page.get("content", {}).get("rendered", "")
            # Remove old squad and news sections
            content = re.sub(r'<section class="team-section team-squad">.*?</section>', '', content, flags=re.DOTALL)
            content = re.sub(r'<section class="team-section team-news".*?</section>', '', content, flags=re.DOTALL)
            # Add new sections before closing div
            team_name = data.get("name", slug.replace("team-", "").replace("-", " ").title())
            if slug == "team-real-madrid":
                team_name = "Реал Мадрид"
            elif slug == "team-barselona":
                team_name = "Барселона"
            elif slug == "team-natus-vincere":
                team_name = "Natus Vincere"
            elif slug == "team-team-spirit":
                team_name = "Team Spirit"
            squad_html = build_squad_html(slug, data)
            news_html = build_news_html(team_name)
            content = content.replace("</div>", squad_html + news_html + "</div>", 1)
            r2 = client.post(
                f"{WP_URL}/wp-json/wp/v2/pages/{page['id']}",
                json={"content": content},
                auth=AUTH,
            )
            if r2.status_code in (200, 201):
                print(f"OK {slug}")
                updated += 1
        print(f"Updated: {updated}")

if __name__ == "__main__":
    main()
