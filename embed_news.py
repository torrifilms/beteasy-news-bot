#!/usr/bin/env python3
"""Team page with embedded news and working button."""

import os
import httpx

WP_URL = os.environ.get("WP_URL", "https://beteasy.ru").rstrip("/")
AUTH = (os.environ.get("WP_USER", ""), os.environ.get("WP_APP_PASS", ""))

# Fetch recent posts with auth
def get_news():
    with httpx.Client(timeout=30) as client:
        r = client.get(WP_URL + "/wp-json/wp/v2/posts", 
                       params={"per_page": 5, "_fields": "title,link,date"},
                       auth=AUTH)
        if r.status_code == 200:
            return r.json()
    return []

news = get_news()
news_html = ""
for p in news[:3]:
    title = p.get("title", {}).get("rendered", "")
    link = p.get("link", "")
    date = p.get("date", "")[:10]
    news_html += f'<a href="{link}"><span>{date}</span><b>{title}</b></a>\n'

if not news_html:
    news_html = '<p style="color:#79829B">Новостей пока нет</p>'

PLAYERS = [
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
    ("Эдуардо Камавинга", "ЦП", "6"),
    ("Килиан Мбаппе", "ЦН", "10"),
    ("Винисиус Жуниор", "ЛН", "7"),
    ("Эндрик", "ЦН", "9"),
    ("Браим Диас", "АП", "21"),
    ("Ян Диоманде", "ЛН", "25"),
]

players_html = ""
for name, pos, num in PLAYERS:
    photo = "https://ui-avatars.com/api/?name=" + name.split()[0] + "&background=141827&color=EDF0F7&size=60"
    players_html += '<div class="tp-pl"><img src="' + photo + '" alt="' + name + '"><div><span class="n">' + num + '</span><b>' + name + '</b><span>' + pos + '</span></div></div>\n'

PAGE = '''
<style>
.tp{max-width:960px;margin:20px auto;padding:0 16px}
.tp-hero{display:flex;justify-content:space-between;align-items:center;gap:20px;padding:24px;background:#0E1016;border:1px solid rgba(121,130,155,.2);border-radius:16px;margin-bottom:16px}
.tp-hero h1{font-family:Unbounded,sans-serif;font-size:24px;margin:0;text-transform:uppercase;color:#EDF0F7}
.tp-meta{color:#79829B;font-size:13px;margin:4px 0}
.tp-titles{color:#D6FF3B;font-weight:600;margin-top:8px;font-size:14px}
.tp-fan{text-align:center}
.tp-btn{background:#D6FF3B;color:#07080C;border:none;padding:12px 22px;border-radius:100px;font-weight:700;cursor:pointer;font-size:14px;transition:all .2s}
.tp-btn:hover{transform:scale(1.05)}
.tp-btn.on{background:#8F6BFF;color:#fff}
.tp-count{margin-top:6px;font-size:12px;color:#79829B}
.tp-count b{font-family:"JetBrains Mono",monospace;font-size:18px;color:#D6FF3B}
.tp-box{background:#0E1016;border:1px solid rgba(121,130,155,.2);border-radius:12px;padding:18px;margin:12px 0}
.tp-box h3{font-family:Unbounded,sans-serif;font-size:13px;margin:0 0 12px;text-transform:uppercase;color:#EDF0F7}
.tp-form{display:flex;gap:6px}
.tp-fb{width:30px;height:30px;display:flex;align-items:center;justify-content:center;border-radius:6px;font-weight:700;font-size:12px;color:#fff}
.tp-stats{display:grid;grid-template-columns:repeat(5,1fr);gap:8px}
.tp-st{text-align:center;background:#141827;padding:10px 4px;border-radius:8px}
.tp-st b{display:block;font-family:"JetBrains Mono",monospace;font-size:18px;color:#D6FF3B}
.tp-st span{font-size:9px;color:#79829B;text-transform:uppercase}
.tp-coach{display:flex;align-items:center;gap:10px;padding:10px;background:#141827;border-radius:8px;margin-bottom:12px}
.tp-coach img{width:44px;height:44px;border-radius:50%}
.tp-coach span{font-size:9px;color:#79829B;text-transform:uppercase}
.tp-coach b{display:block;color:#EDF0F7}
.tp-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(190px,1fr));gap:8px}
.tp-pl{display:flex;align-items:center;gap:8px;background:#141827;padding:8px;border-radius:8px}
.tp-pl img{width:36px;height:36px;border-radius:50%}
.tp-pl .n{font-size:9px;color:#D6FF3B}
.tp-pl b{font-size:12px;display:block;color:#EDF0F7}
.tp-pl span{font-size:10px;color:#79829B}
.tp-news a{display:block;padding:10px;background:#141827;border-radius:8px;margin:6px 0;text-decoration:none;color:#EDF0F7}
.tp-news a:hover{background:#1a1d2e}
.tp-news a span{font-size:10px;color:#79829B}
.tp-news a b{display:block;margin-top:2px;font-size:13px}
@media(max-width:600px){.tp-stats{grid-template-columns:repeat(3,1fr)}.tp-hero{flex-direction:column;text-align:center}}
</style>

<div class="tp">
<div class="tp-hero">
<div>
<h1>РЕАЛ МАДРИД</h1>
<p class="tp-meta">Футбол · Ла Лига · Испания</p>
<p class="tp-meta">Основан: 1902 · Стадион: Сантьяго Бернабеу</p>
<p class="tp-titles">Титулы: 15 ЛЧ, 36 Ла Лига</p>
</div>
<div class="tp-fan">
<button class="tp-btn" id="fan-btn" onclick="toggleFan()">❤️ Болею</button>
<div class="tp-count"><b id="fan-count">0</b> болельщиков</div>
</div>
</div>

<div class="tp-box">
<h3>Форма</h3>
<div class="tp-form">
<span class="tp-fb" style="background:#27ae60">W</span>
<span class="tp-fb" style="background:#27ae60">W</span>
<span class="tp-fb" style="background:#f39c12">D</span>
<span class="tp-fb" style="background:#27ae60">W</span>
<span class="tp-fb" style="background:#e74c3c">L</span>
</div>
</div>

<div class="tp-box">
<h3>Статистика сезона</h3>
<div class="tp-stats">
<div class="tp-st"><b>8</b><span>Побед</span></div>
<div class="tp-st"><b>2</b><span>Ничьих</span></div>
<div class="tp-st"><b>1</b><span>Поражений</span></div>
<div class="tp-st"><b>28</b><span>Забито</span></div>
<div class="tp-st"><b>12</b><span>Пропущено</span></div>
</div>
</div>

<div class="tp-box">
<h3>Состав 2026/27</h3>
<div class="tp-coach">
<img src="https://ui-avatars.com/api/?name=JM&background=D6FF3B&color=07080C&size=80" alt="Моуринью">
<div><span>Тренер</span><b>Жозе Моуринью</b></div>
</div>
<div class="tp-grid">
PLAYERS_PLACEHOLDER
</div>
</div>

<div class="tp-box tp-news">
<h3>Последние новости</h3>
NEWS_PLACEHOLDER
</div>
</div>

<script>
function toggleFan(){
var btn=document.getElementById("fan-btn");
var countEl=document.getElementById("fan-count");
var key="fan-team-real-madrid";
var isOn=localStorage.getItem(key)==="1";
var count=parseInt(localStorage.getItem("fan-count-real")||"0");
if(isOn){
localStorage.setItem(key,"0");
count=Math.max(0,count-1);
btn.classList.remove("on");
btn.textContent="❤️ Болею";
}else{
localStorage.setItem(key,"1");
count++;
btn.classList.add("on");
btn.textContent="❤️ Болею!";
}
localStorage.setItem("fan-count-real",count);
countEl.textContent=count;
}
(function(){
var btn=document.getElementById("fan-btn");
var countEl=document.getElementById("fan-count");
var key="fan-team-real-madrid";
if(localStorage.getItem(key)==="1"){
btn.classList.add("on");
btn.textContent="❤️ Болею!";
}
countEl.textContent=localStorage.getItem("fan-count-real")||"0";
})();
</script>
'''

PAGE = PAGE.replace("PLAYERS_PLACEHOLDER", players_html)
PAGE = PAGE.replace("NEWS_PLACEHOLDER", news_html)

def main():
    with httpx.Client(timeout=60) as client:
        r = client.get(WP_URL + "/wp-json/wp/v2/pages", params={"slug": "team-real-madrid"}, auth=AUTH)
        if r.status_code == 200 and r.json():
            pid = r.json()[0]["id"]
            r2 = client.post(WP_URL + "/wp-json/wp/v2/pages/" + str(pid), json={"content": PAGE}, auth=AUTH)
            print("OK" if r2.status_code in (200, 201) else "ERR")
            print("News count:", len(news))

if __name__ == "__main__":
    main()
