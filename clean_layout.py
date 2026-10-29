#!/usr/bin/env python3
"""Rewrite team page with clean, working layout."""

import os
import httpx

WP_URL = os.environ.get("WP_URL", "https://beteasy.ru").rstrip("/")
AUTH = (os.environ.get("WP_USER", ""), os.environ.get("WP_APP_PASS", ""))

PAGE = '''
<style>
.tp{max-width:900px;margin:30px auto;padding:0 16px}
.tp-hero{display:flex;justify-content:space-between;align-items:center;gap:20px;padding:24px;background:#0E1016;border:1px solid rgba(121,130,155,.2);border-radius:16px;margin-bottom:16px}
.tp-hero h1{font-family:Unbounded,sans-serif;font-size:26px;margin:0;text-transform:uppercase;color:#EDF0F7}
.tp-meta{color:#79829B;font-size:13px;margin:6px 0}
.tp-titles{color:#D6FF3B;font-weight:600;margin-top:8px}
.tp-fan{text-align:center}
.tp-btn{background:#D6FF3B;color:#07080C;border:none;padding:12px 22px;border-radius:100px;font-weight:700;cursor:pointer;font-size:14px}
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
.tp-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:8px}
.tp-pl{display:flex;align-items:center;gap:8px;background:#141827;padding:8px;border-radius:8px}
.tp-pl img{width:36px;height:36px;border-radius:50%}
.tp-pl .n{font-size:9px;color:#D6FF3B}
.tp-pl b{font-size:12px;display:block;color:#EDF0F7}
.tp-pl span{font-size:10px;color:#79829B}
.tp-news a{display:block;padding:10px;background:#141827;border-radius:8px;margin:6px 0;text-decoration:none;color:#EDF0F7}
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
<button class="tp-btn" data-team="team-real-madrid">❤️ Болею</button>
<div class="tp-count"><b id="fc-team-real-madrid">0</b> болельщиков</div>
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
<h3>Статистика</h3>
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
<img src="https://ui-avatars.com/api/?name=Jose+Mourinho&background=D6FF3B&color=07080C&size=80" alt="Моуринью">
<div><span>Тренер</span><b>Жозе Моуринью</b></div>
</div>
<div class="tp-grid">
<div class="tp-pl"><img src="https://ui-avatars.com/api/?name=Courtois&background=141827&color=EDF0F7&size=60"><div><span class="n">1</span><b>Тибо Куртуа</b><span>ВР</span></div></div>
<div class="tp-pl"><img src="https://ui-avatars.com/api/?name=Lunin&background=141827&color=EDF0F7&size=60"><div><span class="n">13</span><b>Андрей Лунин</b><span>ВР</span></div></div>
<div class="tp-pl"><img src="https://ui-avatars.com/api/?name=Militao&background=141827&color=EDF0F7&size=60"><div><span class="n">3</span><b>Эдер Милитао</b><span>ЦЗ</span></div></div>
<div class="tp-pl"><img src="https://ui-avatars.com/api/?name=Huijsen&background=141827&color=EDF0F7&size=60"><div><span class="n">4</span><b>Дин Хёйсен</b><span>ЦЗ</span></div></div>
<div class="tp-pl"><img src="https://ui-avatars.com/api/?name=Konate&background=141827&color=EDF0F7&size=60"><div><span class="n">16</span><b>Ибраима Конате</b><span>ЦЗ</span></div></div>
<div class="tp-pl"><img src="https://ui-avatars.com/api/?name=Valverde&background=141827&color=EDF0F7&size=60"><div><span class="n">8</span><b>Федерико Вальверде</b><span>ЦП</span></div></div>
<div class="tp-pl"><img src="https://ui-avatars.com/api/?name=Bellingham&background=141827&color=EDF0F7&size=60"><div><span class="n">5</span><b>Джуд Беллингем</b><span>АП</span></div></div>
<div class="tp-pl"><img src="https://ui-avatars.com/api/?name=Mbappe&background=141827&color=EDF0F7&size=60"><div><span class="n">10</span><b>Килиан Мбаппе</b><span>ЦН</span></div></div>
<div class="tp-pl"><img src="https://ui-avatars.com/api/?name=Vinicius&background=141827&color=EDF0F7&size=60"><div><span class="n">7</span><b>Винисиус Жуниор</b><span>ЛН</span></div></div>
<div class="tp-pl"><img src="https://ui-avatars.com/api/?name=Bernardo&background=141827&color=EDF0F7&size=60"><div><span class="n">20</span><b>Бернарду Силва</b><span>ЦП</span></div></div>
</div>
</div>

<div class="tp-box tp-news">
<h3>Последние новости</h3>
<div id="news-real">Загрузка...</div>
</div>
</div>

<script>
(function(){
var btn=document.querySelector(".tp-btn");
var slug="team-real-madrid";
var el=document.getElementById("fc-"+slug);
if(!btn)return;
var fd=new FormData();fd.append("action","beteasy_fan");fd.append("slug",slug);fd.append("do","get");
fetch("/wp-admin/admin-ajax.php",{method:"POST",body:fd}).then(r=>r.json()).then(d=>{if(d.success&&el)el.textContent=d.data.count}).catch(()=>{});
if(localStorage.getItem("fan-"+slug)==="1"){btn.classList.add("on");btn.textContent="❤️ Болею!"}
btn.onclick=function(){
var on=btn.classList.contains("on");
var fd2=new FormData();fd2.append("action","beteasy_fan");fd2.append("slug",slug);fd2.append("do",on?"remove":"add");
fetch("/wp-admin/admin-ajax.php",{method:"POST",body:fd2}).then(r=>r.json()).then(d=>{
if(d.success){if(el)el.textContent=d.data.count;if(d.data.status==="ok"){if(on){btn.classList.remove("on");btn.textContent="❤️ Болею";localStorage.setItem("fan-"+slug,"0")}else{btn.classList.add("on");btn.textContent="❤️ Болею!";localStorage.setItem("fan-"+slug,"1")}}else if(d.data.status==="limited")alert("Уже голосовали")}}).catch(()=>{});
};
fetch("/wp-json/wp/v2/posts?search="+encodeURIComponent("Реал Мадрид")+"&per_page=3&_fields=title,link,date").then(r=>r.json()).then(posts=>{
var c=document.getElementById("news-real");
if(!posts.length){c.innerHTML="<p>Нет новостей</p>";return}
c.innerHTML=posts.map(p=>"<a href='"+p.link+"'><span>"+new Date(p.date).toLocaleDateString("ru-RU")+"</span><b>"+p.title.rendered+"</b></a>").join("");
}).catch(()=>{document.getElementById("news-real").innerHTML="<p>Ошибка</p>"});
})();
</script>
'''

def main():
    with httpx.Client(timeout=60) as client:
        r = client.get(f"{WP_URL}/wp-json/wp/v2/pages", params={"slug": "team-real-madrid"}, auth=AUTH)
        if r.status_code == 200 and r.json():
            pid = r.json()[0]["id"]
            r2 = client.post(f"{WP_URL}/wp-json/wp/v2/pages/{pid}", json={"content": PAGE}, auth=AUTH)
            print(f"{'OK' if r2.status_code in (200,201) else 'ERR'} real-madrid")

if __name__ == "__main__":
    main()
