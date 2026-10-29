#!/usr/bin/env python3
"""Create Manchester City page with exact template."""

import os
import httpx

WP_URL = os.environ.get("WP_URL", "https://beteasy.ru").rstrip("/")
AUTH = (os.environ.get("WP_USER", ""), os.environ.get("WP_APP_PASS", ""))

PAGE = '''<!-- wp:html -->
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
.tp-stats-table{width:100%;border-collapse:collapse}
.tp-stats-table tr{border-bottom:1px solid rgba(121,130,155,.15)}
.tp-stats-table tr:last-child{border-bottom:none}
.tp-stats-table td{padding:12px 8px;font-size:14px}
.tp-stats-table td:first-child{color:#79829B}
.tp-stats-table td:last-child{text-align:right;font-family:"JetBrains Mono",monospace;color:#D6FF3B;font-weight:600}
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
.tp-pred-item{display:flex;flex-direction:column;padding:14px 16px;background:rgba(20,24,39,.6);border:1px solid rgba(214,255,59,.15);border-radius:10px;text-decoration:none;transition:all .3s}
.tp-pred-item:hover{border-color:rgba(214,255,59,.4);background:rgba(20,24,39,.9);transform:translateX(4px)}
.tp-pred-date{font-size:11px;color:#79829B;text-transform:uppercase;letter-spacing:.5px}
.tp-pred-item b{color:#EDF0F7;font-size:14px;margin-top:4px}
.tp-faq-wrap{background:linear-gradient(145deg,#0E1016 0%,#141827 100%);border:1px solid rgba(214,255,59,.15);border-radius:16px;padding:24px;margin:16px 0}
.tp-faq-wrap h3{font-family:Unbounded,sans-serif;font-size:16px;margin:0 0 20px;text-transform:uppercase;color:#EDF0F7;letter-spacing:1px}
.tp-faq{margin:0 0 12px;padding:16px 20px;background:rgba(20,24,39,.6);border:1px solid rgba(121,130,155,.15);border-radius:12px;transition:all .3s ease}
.tp-faq:hover{border-color:rgba(214,255,59,.3);background:rgba(20,24,39,.9);transform:translateX(4px)}
.tp-faq b{display:flex;align-items:center;gap:12px;color:#EDF0F7;font-size:15px;font-weight:600;cursor:pointer}
.tp-faq b::before{content:"→";color:#D6FF3B;font-size:18px}
.tp-faq p{margin:10px 0 0 30px;color:#9AA3B8;font-size:14px;line-height:1.7}
.tp-logo{width:80px;height:80px;object-fit:contain;margin-right:16px}
.tp-hero-left{display:flex;align-items:center}
@media(max-width:600px){.tp-stats{grid-template-columns:repeat(3,1fr)}.tp-hero{flex-direction:column;text-align:center}}
</style>

<div class="tp">
<div class="tp-hero">
<div class="tp-hero-left">
<img src="https://upload.wikimedia.org/wikipedia/en/e/eb/Manchester_City_FC_badge.svg" alt="Manchester City" class="tp-logo">
<div>
<h1>МАНЧЕСТЕР СИТИ</h1>
<p class="tp-meta">Футбол · АПЛ · Англия</p>
<p class="tp-meta">Основан: 1880 · Стадион: Этихад</p>
<p class="tp-titles">Титулы: 1 ЛЧ, 10 АПЛ</p>
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
<span class="tp-fb" style="background:#27ae60">W</span>
<span class="tp-fb" style="background:#27ae60">W</span>
<span class="tp-fb" style="background:#f39c12">D</span>
<span class="tp-fb" style="background:#27ae60">W</span>
<span class="tp-fb" style="background:#27ae60">W</span>
</div>
</div>

<div class="tp-box">
<h3>Статистика сезона</h3>
<div class="tp-stats">
<div class="tp-st"><b>7</b><span>Побед</span></div>
<div class="tp-st"><b>2</b><span>Ничьих</span></div>
<div class="tp-st"><b>1</b><span>Поражений</span></div>
<div class="tp-st"><b>24</b><span>Забито</span></div>
<div class="tp-st"><b>9</b><span>Пропущено</span></div>
</div>
</div>

<div class="tp-box">
<h3>Подробная статистика</h3>
<table class="tp-stats-table">
<tr><td>Матчей сыграно</td><td>10</td></tr>
<tr><td>Побед</td><td>7</td></tr>
<tr><td>Ничьих</td><td>2</td></tr>
<tr><td>Поражений</td><td>1</td></tr>
<tr><td>Голов забито</td><td>24</td></tr>
<tr><td>Голов пропущено</td><td>9</td></tr>
<tr><td>Разница мячей</td><td>+15</td></tr>
<tr><td>Очки</td><td>23</td></tr>
<tr><td>Место в таблице</td><td>2</td></tr>
<tr><td>Среднее голов за матч</td><td>2.4</td></tr>
</table>
</div>

<div class="tp-box">
<h3>Состав 2026/27</h3>
<div class="tp-coach">
<img src="https://ui-avatars.com/api/?name=PG&background=D6FF3B&color=07080C&size=80" alt="Гвардиола">
<div><span>Тренер</span><b>Пеп Гвардиола</b></div>
</div>
<div class="tp-grid">
<div class="tp-pl"><img src="https://ui-avatars.com/api/?name=E&background=141827&color=EDF0F7&size=60" alt="Эдерсон"><div><span class="n">31</span><b>Эдерсон</b><span>ВР</span></div></div>
<div class="tp-pl"><img src="https://ui-avatars.com/api/?name=R&background=141827&color=EDF0F7&size=60" alt="Рубен Диаш"><div><span class="n">3</span><b>Рубен Диаш</b><span>ЦЗ</span></div></div>
<div class="tp-pl"><img src="https://ui-avatars.com/api/?name=K&background=141827&color=EDF0F7&size=60" alt="Де Брёйне"><div><span class="n">17</span><b>Кевин Де Брёйне</b><span>ЦП</span></div></div>
<div class="tp-pl"><img src="https://ui-avatars.com/api/?name=H&background=141827&color=EDF0F7&size=60" alt="Холанд"><div><span class="n">9</span><b>Эрлинг Холанд</b><span>ЦН</span></div></div>
<div class="tp-pl"><img src="https://ui-avatars.com/api/?name=F&background=141827&color=EDF0F7&size=60" alt="Фоден"><div><span class="n">47</span><b>Фил Фоден</b><span>АП</span></div></div>
<div class="tp-pl"><img src="https://ui-avatars.com/api/?name=B&background=141827&color=EDF0F7&size=60" alt="Бернарду"><div><span class="n">20</span><b>Бернарду Силва</b><span>ЦП</span></div></div>
</div>
</div>

<div class="tp-box">
<h3>Прогнозы на матчи</h3>
<a href="https://beteasy.ru/prognozy/" class="tp-pred-item">
<span class="tp-pred-date">Все прогнозы</span>
<b>Смотреть прогнозы на матчи Манчестер Сити →</b>
</a>
</div>

<div class="tp-faq-wrap" itemscope itemtype="https://schema.org/FAQPage">
<h3>FAQ</h3>
<div class="tp-faq" itemscope itemprop="mainEntity" itemtype="https://schema.org/Question">
<b itemprop="name">Кто тренер Манчестер Сити?</b>
<div itemscope itemprop="acceptedAnswer" itemtype="https://schema.org/Answer">
<p itemprop="text">Главный тренер «Манчестер Сити» — Пеп Гвардиола, который руководит командой с 2016 года. Под его руководством клуб выиграл 6 титулов АПЛ и Лигу чемпионов 2023.</p>
</div>
</div>
<div class="tp-faq" itemscope itemprop="mainEntity" itemtype="https://schema.org/Question">
<b itemprop="name">Сколько титулов АПЛ у Сити?</b>
<div itemscope itemprop="acceptedAnswer" itemtype="https://schema.org/Answer">
<p itemprop="text">«Манчестер Сити» выигрывал чемпионат Англии 10 раз, включая 4 титула подряд в 2021-2024 годах. Это один из самых успешных периодов в истории клуба.</p>
</div>
</div>
<div class="tp-faq" itemscope itemprop="mainEntity" itemtype="https://schema.org/Question">
<b itemprop="name">Кто лучший бомбардир Сити?</b>
<div itemscope itemprop="acceptedAnswer" itemtype="https://schema.org/Answer">
<p itemprop="text">Эрлинг Холанд — лучший бомбардир «Манчестер Сити» в сезоне 2026/27. Норвежец забил 14 голов в 10 матчах АПЛ.</p>
</div>
</div>
</div>
</div>

<script>
function toggleFan(){
var btn=document.getElementById("fan-btn");
var countEl=document.getElementById("fan-count");
var key="fan-mancity";
var isOn=localStorage.getItem(key)==="1";
var count=parseInt(localStorage.getItem(key+"-count")||"0");
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
localStorage.setItem(key+"-count",count);
countEl.textContent=count;
}
(function(){
var btn=document.getElementById("fan-btn");
var countEl=document.getElementById("fan-count");
var key="fan-mancity";
if(localStorage.getItem(key)==="1"){
btn.classList.add("on");
btn.textContent="❤️ Болею!";
}
countEl.textContent=localStorage.getItem(key+"-count")||"0";
})();
</script>

<script type="application/ld+json">
{"@context":"https://schema.org","@type":"SportsTeam","name":"Манчестер Сити","alternateName":"Manchester City","sport":"Football","memberOf":{"@type":"SportsOrganization","name":"АПЛ"},"coach":{"@type":"Person","name":"Пеп Гвардиола"},"location":{"@type":"StadiumOrArena","name":"Этихад","address":"Манчестер, Англия"},"foundingDate":"1880","url":"https://beteasy.ru/team-manchester-siti/"}
</script>
<!-- /wp:html -->
'''

def main():
    with httpx.Client(timeout=60) as client:
        r = client.get(WP_URL + "/wp-json/wp/v2/pages", params={"slug": "team-manchester-siti"}, auth=AUTH)
        if r.status_code == 200 and r.json():
            pid = r.json()[0]["id"]
            r2 = client.post(WP_URL + "/wp-json/wp/v2/pages/" + str(pid), json={"content": PAGE}, auth=AUTH)
            print("OK" if r2.status_code in (200, 201) else "ERR")
        else:
            print("ERR: page not found")

if __name__ == "__main__":
    main()
