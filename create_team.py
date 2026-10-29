#!/usr/bin/env python3
"""Create/update team page with full template."""

import os
import sys
import httpx

WP_URL = os.environ.get("WP_URL", "https://beteasy.ru").rstrip("/")
AUTH = (os.environ.get("WP_USER", ""), os.environ.get("WP_APP_PASS", ""))

# Team data
TEAMS = {
    "team-barselona": {
        "name": "Барселона",
        "name_en": "Barcelona",
        "sport": "Футбол",
        "league": "Ла Лига",
        "country": "Испания",
        "founded": "1899",
        "stadium": "Камп Ноу",
        "titles": "5 ЛЧ, 27 Ла Лига",
        "coach": "Ханси Флик",
        "logo": "https://upload.wikimedia.org/wikipedia/en/4/47/FC_Barcelona_%28crest%29.svg",
        "form": ["W", "W", "W", "W", "L"],
        "stats": {"wins": 9, "draws": 0, "losses": 1, "gf": 29, "ga": 8, "pts": 27, "pos": 1},
        "players": [
            ("Марк-Андре тер Стеген", "ВР", "1"),
            ("Жюль Кунде", "ЦЗ", "23"),
            ("Алехандро Бальде", "ЛЗ", "3"),
            ("Педри", "ЦП", "8"),
            ("Гави", "ЦП", "6"),
            ("Ламин Ямаль", "ПН", "19"),
            ("Роберт Левандовски", "ЦН", "9"),
            ("Рафинья", "ЛН", "11"),
        ]
    }
}

def build_page(team):
    form_html = ""
    colors = {"W": "#27ae60", "D": "#f39c12", "L": "#e74c3c"}
    for r in team["form"]:
        form_html += f'<span class="tp-fb" style="background:{colors[r]}">{r}</span>\n'
    
    players_html = ""
    for name, pos, num in team["players"]:
        photo = "https://ui-avatars.com/api/?name=" + name.split()[0] + "&background=141827&color=EDF0F7&size=60"
        players_html += f'<div class="tp-pl"><img src="{photo}" alt="{name}"><div><span class="n">{num}</span><b>{name}</b><span>{pos}</span></div></div>\n'
    
    s = team["stats"]
    
    return f'''<!-- wp:html -->
<style>
.tp{{max-width:960px;margin:20px auto;padding:0 16px}}
.tp-hero{{display:flex;justify-content:space-between;align-items:center;gap:20px;padding:24px;background:#0E1016;border:1px solid rgba(121,130,155,.2);border-radius:16px;margin-bottom:16px}}
.tp-hero h1{{font-family:Unbounded,sans-serif;font-size:24px;margin:0;text-transform:uppercase;color:#EDF0F7}}
.tp-meta{{color:#79829B;font-size:13px;margin:4px 0}}
.tp-titles{{color:#D6FF3B;font-weight:600;margin-top:8px;font-size:14px}}
.tp-fan{{text-align:center}}
.tp-btn{{background:#D6FF3B;color:#07080C;border:none;padding:12px 22px;border-radius:100px;font-weight:700;cursor:pointer;font-size:14px;transition:all .2s}}
.tp-btn:hover{{transform:scale(1.05)}}
.tp-btn.on{{background:#8F6BFF;color:#fff}}
.tp-count{{margin-top:6px;font-size:12px;color:#79829B}}
.tp-count b{{font-family:"JetBrains Mono",monospace;font-size:18px;color:#D6FF3B}}
.tp-box{{background:#0E1016;border:1px solid rgba(121,130,155,.2);border-radius:12px;padding:18px;margin:12px 0}}
.tp-box h3{{font-family:Unbounded,sans-serif;font-size:13px;margin:0 0 12px;text-transform:uppercase;color:#EDF0F7}}
.tp-form{{display:flex;gap:6px}}
.tp-fb{{width:30px;height:30px;display:flex;align-items:center;justify-content:center;border-radius:6px;font-weight:700;font-size:12px;color:#fff}}
.tp-stats{{display:grid;grid-template-columns:repeat(5,1fr);gap:8px}}
.tp-st{{text-align:center;background:#141827;padding:10px 4px;border-radius:8px}}
.tp-st b{{display:block;font-family:"JetBrains Mono",monospace;font-size:18px;color:#D6FF3B}}
.tp-st span{{font-size:9px;color:#79829B;text-transform:uppercase}}
.tp-stats-table{{width:100%;border-collapse:collapse}}
.tp-stats-table tr{{border-bottom:1px solid rgba(121,130,155,.15)}}
.tp-stats-table tr:last-child{{border-bottom:none}}
.tp-stats-table td{{padding:12px 8px;font-size:14px}}
.tp-stats-table td:first-child{{color:#79829B}}
.tp-stats-table td:last-child{{text-align:right;font-family:"JetBrains Mono",monospace;color:#D6FF3B;font-weight:600}}
.tp-coach{{display:flex;align-items:center;gap:10px;padding:10px;background:#141827;border-radius:8px;margin-bottom:12px}}
.tp-coach img{{width:44px;height:44px;border-radius:50%}}
.tp-coach span{{font-size:9px;color:#79829B;text-transform:uppercase}}
.tp-coach b{{display:block;color:#EDF0F7}}
.tp-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(190px,1fr));gap:8px}}
.tp-pl{{display:flex;align-items:center;gap:8px;background:#141827;padding:8px;border-radius:8px}}
.tp-pl img{{width:36px;height:36px;border-radius:50%}}
.tp-pl .n{{font-size:9px;color:#D6FF3B}}
.tp-pl b{{font-size:12px;display:block;color:#EDF0F7}}
.tp-pl span{{font-size:10px;color:#79829B}}
.tp-logo{{width:80px;height:80px;object-fit:contain;margin-right:16px}}
.tp-hero-left{{display:flex;align-items:center}}
.tp-faq-wrap{{background:linear-gradient(145deg,#0E1016 0%,#141827 100%);border:1px solid rgba(214,255,59,.15);border-radius:16px;padding:24px;margin:16px 0}}
.tp-faq-wrap h3{{font-family:Unbounded,sans-serif;font-size:16px;margin:0 0 20px;text-transform:uppercase;color:#EDF0F7;letter-spacing:1px}}
.tp-faq{{margin:0 0 12px;padding:16px 20px;background:rgba(20,24,39,.6);border:1px solid rgba(121,130,155,.15);border-radius:12px;transition:all .3s ease}}
.tp-faq:hover{{border-color:rgba(214,255,59,.3);background:rgba(20,24,39,.9);transform:translateX(4px)}}
.tp-faq b{{display:flex;align-items:center;gap:12px;color:#EDF0F7;font-size:15px;font-weight:600;cursor:pointer}}
.tp-faq b::before{{content:"→";color:#D6FF3B;font-size:18px}}
.tp-faq p{{margin:10px 0 0 30px;color:#9AA3B8;font-size:14px;line-height:1.7}}
@media(max-width:600px){{.tp-stats{{grid-template-columns:repeat(3,1fr)}}.tp-hero{{flex-direction:column;text-align:center}}}}
</style>

<div class="tp">
<div class="tp-hero">
<div class="tp-hero-left">
<img src="{team["logo"]}" alt="{team["name"]}" class="tp-logo">
<div>
<h1>{team["name"].upper()}</h1>
<p class="tp-meta">{team["sport"]} · {team["league"]} · {team["country"]}</p>
<p class="tp-meta">Основан: {team["founded"]} · Стадион: {team["stadium"]}</p>
<p class="tp-titles">Титулы: {team["titles"]}</p>
</div>
</div>
<div class="tp-fan">
<button class="tp-btn" id="fan-btn" onclick="toggleFan()">❤️ Болею</button>
<div class="tp-count"><b id="fan-count">0</b> болельщиков</div>
</div>
</div>

<div class="tp-box">
<h3>Форма</h3>
<div class="tp-form">
{form_html}
</div>
</div>

<div class="tp-box">
<h3>Статистика сезона</h3>
<div class="tp-stats">
<div class="tp-st"><b>{s["wins"]}</b><span>Побед</span></div>
<div class="tp-st"><b>{s["draws"]}</b><span>Ничьих</span></div>
<div class="tp-st"><b>{s["losses"]}</b><span>Поражений</span></div>
<div class="tp-st"><b>{s["gf"]}</b><span>Забито</span></div>
<div class="tp-st"><b>{s["ga"]}</b><span>Пропущено</span></div>
</div>
</div>

<div class="tp-box">
<h3>Подробная статистика</h3>
<table class="tp-stats-table">
<tr><td>Матчей сыграно</td><td>{s["wins"]+s["draws"]+s["losses"]}</td></tr>
<tr><td>Побед</td><td>{s["wins"]}</td></tr>
<tr><td>Ничьих</td><td>{s["draws"]}</td></tr>
<tr><td>Поражений</td><td>{s["losses"]}</td></tr>
<tr><td>Голов забито</td><td>{s["gf"]}</td></tr>
<tr><td>Голов пропущено</td><td>{s["ga"]}</td></tr>
<tr><td>Разница мячей</td><td>+{s["gf"]-s["ga"]}</td></tr>
<tr><td>Очки</td><td>{s["pts"]}</td></tr>
<tr><td>Место в таблице</td><td>{s["pos"]}</td></tr>
</table>
</div>

<div class="tp-box">
<h3>Состав 2026/27</h3>
<div class="tp-coach">
<img src="https://ui-avatars.com/api/?name={team["coach"].split()[0][0]}{team["coach"].split()[-1][0]}&background=D6FF3B&color=07080C&size=80" alt="{team["coach"]}">
<div><span>Тренер</span><b>{team["coach"]}</b></div>
</div>
<div class="tp-grid">
{players_html}
</div>
</div>

<div class="tp-faq-wrap" itemscope itemtype="https://schema.org/FAQPage">
<h3>FAQ</h3>
<div class="tp-faq" itemscope itemprop="mainEntity" itemtype="https://schema.org/Question">
<b itemprop="name">Кто тренер {team["name"]} в сезоне 2026/27?</b>
<div itemscope itemprop="acceptedAnswer" itemtype="https://schema.org/Answer">
<p itemprop="text">Главный тренер «{team["name"]}» в сезоне 2026/27 — {team["coach"]}.</p>
</div>
</div>
<div class="tp-faq" itemscope itemprop="mainEntity" itemtype="https://schema.org/Question">
<b itemprop="name">Какой стадион у {team["name"]}?</b>
<div itemscope itemprop="acceptedAnswer" itemtype="https://schema.org/Answer">
<p itemprop="text">Домашний стадион «{team["name"]}» — {team["stadium"]}.</p>
</div>
</div>
<div class="tp-faq" itemscope itemprop="mainEntity" itemtype="https://schema.org/Question">
<b itemprop="name">В какой лиге играет {team["name"]}?</b>
<div itemscope itemprop="acceptedAnswer" itemtype="https://schema.org/Answer">
<p itemprop="text">«{team["name"]}» выступает в {team["league"]}.</p>
</div>
</div>
</div>
</div>

<script>
function toggleFan(){{
var btn=document.getElementById("fan-btn");
var countEl=document.getElementById("fan-count");
var key="fan-{team["name_en"].lower().replace(" ","-")}";
var isOn=localStorage.getItem(key)==="1";
var count=parseInt(localStorage.getItem(key+"-count")||"0");
if(isOn){{
localStorage.setItem(key,"0");
count=Math.max(0,count-1);
btn.classList.remove("on");
btn.textContent="❤️ Болею";
}}else{{
localStorage.setItem(key,"1");
count++;
btn.classList.add("on");
btn.textContent="❤️ Болею!";
}}
localStorage.setItem(key+"-count",count);
countEl.textContent=count;
}}
(function(){{
var btn=document.getElementById("fan-btn");
var countEl=document.getElementById("fan-count");
var key="fan-{team["name_en"].lower().replace(" ","-")}";
if(localStorage.getItem(key)==="1"){{
btn.classList.add("on");
btn.textContent="❤️ Болею!";
}}
countEl.textContent=localStorage.getItem(key+"-count")||"0";
}})();
</script>

<script type="application/ld+json">
{{"@context":"https://schema.org","@type":"SportsTeam","name":"{team["name"]}","alternateName":"{team["name_en"]}","sport":"{team["sport"]}","memberOf":{{"@type":"SportsOrganization","name":"{team["league"]}"}},"coach":{{"@type":"Person","name":"{team["coach"]}"}},"location":{{"@type":"StadiumOrArena","name":"{team["stadium"]}","address":"{team["country"]}"}},"foundingDate":"{team["founded"]}"}}
</script>
<!-- /wp:html -->
'''

def main():
    slug = sys.argv[1] if len(sys.argv) > 1 else "team-barselona"
    team = TEAMS.get(slug)
    if not team:
        print(f"ERR: team {slug} not found")
        return
    
    content = build_page(team)
    
    with httpx.Client(timeout=60) as client:
        r = client.get(WP_URL + "/wp-json/wp/v2/pages", params={"slug": slug}, auth=AUTH)
        if r.status_code == 200 and r.json():
            pid = r.json()[0]["id"]
            r2 = client.post(WP_URL + "/wp-json/wp/v2/pages/" + str(pid), json={"content": content}, auth=AUTH)
            print("OK" if r2.status_code in (200, 201) else "ERR")
        else:
            print("ERR: page not found")

if __name__ == "__main__":
    main()
