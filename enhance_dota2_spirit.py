#!/usr/bin/env python3
"""Enhanced Team Spirit Dota 2 page."""

import os
import httpx

WP_URL = os.environ.get("WP_URL", "https://beteasy.ru").rstrip("/")
AUTH = (os.environ.get("WP_USER", ""), os.environ.get("WP_APP_PASS", ""))

PAGE = '''<!-- wp:html -->
<style>
.tp{max-width:960px;margin:20px auto;padding:0 16px}
.bread{display:flex;gap:8px;margin-bottom:16px;font-size:13px}
.bread a{color:#79829B;text-decoration:none}
.bread a:hover{color:#D6FF3B}
.bread span{color:#79829B}
.tp-hero{display:flex;justify-content:space-between;align-items:flex-start;gap:20px;padding:24px;background:linear-gradient(135deg,#0E1016 0%,#1a1f2e 100%);border:1px solid rgba(214,255,59,.15);border-radius:16px;margin-bottom:16px}
.tp-hero-left{display:flex;align-items:center;gap:16px}
.tp-logo{width:90px;height:90px;object-fit:contain;background:#fff;border-radius:12px;padding:10px;box-shadow:0 4px 20px rgba(0,0,0,.3)}
.tp-hero h1{font-family:Unbounded,sans-serif;font-size:26px;margin:0;text-transform:uppercase;color:#EDF0F7;letter-spacing:-0.5px}
.tp-meta{color:#79829B;font-size:13px;margin:6px 0}
.tp-meta a{color:#D6FF3B}
.tp-titles{color:#D6FF3B;font-weight:600;margin-top:10px;font-size:14px}
.tp-stats-row{display:flex;gap:24px;margin-top:14px;flex-wrap:wrap}
.tp-stat{text-align:center;min-width:70px}
.tp-stat b{display:block;font-family:"JetBrains Mono",monospace;font-size:20px;color:#D6FF3B}
.tp-stat span{font-size:10px;color:#79829B;text-transform:uppercase;letter-spacing:0.5px}
.tp-box{background:#0E1016;border:1px solid rgba(121,130,155,.2);border-radius:12px;padding:18px;margin:12px 0}
.tp-box h3{font-family:Unbounded,sans-serif;font-size:13px;margin:0 0 14px;text-transform:uppercase;color:#EDF0F7;letter-spacing:0.5px}
.tp-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:12px}
.tp-player{display:flex;align-items:center;gap:12px;padding:14px;background:#141827;border-radius:10px;border:1px solid rgba(121,130,155,.1)}
.tp-player img{width:52px;height:52px;border-radius:50%;border:2px solid rgba(214,255,59,.3)}
.tp-player-info{flex:1}
.tp-player b{display:block;color:#EDF0F7;font-size:14px}
.tp-player .role{font-size:10px;color:#D6FF3B;text-transform:uppercase;font-weight:600}
.tp-player .name{font-size:11px;color:#79829B}
.tp-match{display:flex;justify-content:space-between;align-items:center;padding:12px 14px;background:#141827;border-radius:8px;margin-bottom:8px;border:1px solid rgba(121,130,155,.08)}
.tp-match-left{display:flex;align-items:center;gap:12px}
.tp-match-date{font-size:11px;color:#79829B;min-width:65px}
.tp-match-tour{font-size:10px;color:#D6FF3B;background:rgba(214,255,59,.1);padding:3px 8px;border-radius:4px;min-width:50px;text-align:center}
.tp-match-opp{color:#EDF0F7;font-size:13px}
.tp-match-score{font-family:"JetBrains Mono",monospace;font-weight:700;font-size:15px}
.tp-match-score.win{color:#27ae60}
.tp-match-score.loss{color:#e74c3c}
.tp-tour-item{display:flex;justify-content:space-between;align-items:center;padding:14px;background:#141827;border-radius:8px;margin-bottom:8px}
.tp-tour-place{width:42px;height:42px;display:flex;align-items:center;justify-content:center;background:#D6FF3B;color:#07080C;font-weight:700;border-radius:8px;font-size:16px}
.tp-tour-info{flex:1;margin-left:14px}
.tp-tour-info b{display:block;color:#EDF0F7;font-size:13px}
.tp-tour-info span{font-size:11px;color:#79829B}
.tp-tour-prize{text-align:right}
.tp-tour-prize b{display:block;color:#D6FF3B;font-family:"JetBrains Mono",monospace;font-size:14px}
.tp-tour-prize span{font-size:10px;color:#79829B}
.tp-faq{margin:0 0 10px;padding:14px;background:#141827;border-radius:10px;border:1px solid rgba(121,130,155,.08)}
.tp-faq b{display:block;color:#EDF0F7;margin-bottom:6px;font-size:14px}
.tp-faq p{margin:0;color:#9AA3B8;font-size:13px;line-height:1.5}
.tp-links{display:flex;gap:12px;margin-top:16px}
.tp-links a{padding:12px 20px;background:#D6FF3B;color:#07080C;text-decoration:none;border-radius:8px;font-size:13px;font-weight:600;transition:opacity .2s}
.tp-links a:hover{opacity:.85}
</style>

<div class="tp">
<div class="bread"><a href="/">Главная</a><span>→</span><a href="/teams/">Команды</a><span>→</span><a href="/teams/dota2/">Dota 2</a><span>→</span><span>Team Spirit</span></div>

<div class="tp-hero">
<div class="tp-hero-left">
<img src="https://logo.clearbit.com/teamspirit.gg" alt="Team Spirit" class="tp-logo">
<div>
<h1>TEAM SPIRIT</h1>
<p class="tp-meta">Dota 2 · Россия · <a href="https://teamspirit.gg" target="_blank" rel="nofollow">teamspirit.gg</a></p>
<p class="tp-titles">3× The International · #2 рейтинг · $33.3M призовых</p>
<div class="tp-stats-row">
<div class="tp-stat"><b>3</b><span>TI</span></div>
<div class="tp-stat"><b>212</b><span>Матчей</span></div>
<div class="tp-stat"><b>65%</b><span>Винрейт</span></div>
<div class="tp-stat"><b>$33M</b><span>Призовых</span></div>
</div>
</div>
</div>
</div>

<div class="tp-box">
<h3>Состав 2026</h3>
<div class="tp-grid">
<div class="tp-player">
<img src="https://ui-avatars.com/api/?name=YE&background=141827&color=D6FF3B&size=104" alt="Yatoro">
<div class="tp-player-info">
<span class="role">Carry</span>
<b>Yatoro</b>
<span class="name">Ilya Mulyarchuk · Украина</span>
</div>
</div>
<div class="tp-player">
<img src="https://ui-avatars.com/api/?name=LA&background=141827&color=D6FF3B&size=104" alt="Larl">
<div class="tp-player-info">
<span class="role">Mid</span>
<b>Larl</b>
<span class="name">Denis Sigitov · Россия</span>
</div>
</div>
<div class="tp-player">
<img src="https://ui-avatars.com/api/?name=CO&background=141827&color=D6FF3B&size=104" alt="Collapse">
<div class="tp-player-info">
<span class="role">Offlane</span>
<b>Collapse</b>
<span class="name">Magomed Khalilov · Россия</span>
</div>
</div>
<div class="tp-player">
<img src="https://ui-avatars.com/api/?name=MI&background=141827&color=D6FF3B&size=104" alt="Mira">
<div class="tp-player-info">
<span class="role">Support</span>
<b>Mira</b>
<span class="name">Miroslav Kolpakov · Россия</span>
</div>
</div>
<div class="tp-player">
<img src="https://ui-avatars.com/api/?name=MP&background=141827&color=D6FF3B&size=104" alt="Miposhka">
<div class="tp-player-info">
<span class="role">Hard Support</span>
<b>Miposhka</b>
<span class="name">Yaroslav Naidenov · Россия</span>
</div>
</div>
</div>
</div>

<div class="tp-box">
<h3>Последние матчи</h3>
<div class="tp-match">
<div class="tp-match-left"><span class="tp-match-date">28.10.26</span><span class="tp-match-tour">PARI</span><span class="tp-match-opp">vs Team Yandex</span></div>
<span class="tp-match-score win">2:1</span>
</div>
<div class="tp-match">
<div class="tp-match-left"><span class="tp-match-date">26.10.26</span><span class="tp-match-tour">PARI</span><span class="tp-match-opp">vs PARIVISION</span></div>
<span class="tp-match-score loss">1:2</span>
</div>
<div class="tp-match">
<div class="tp-match-left"><span class="tp-match-date">24.10.26</span><span class="tp-match-tour">PARI</span><span class="tp-match-opp">vs Aurora</span></div>
<span class="tp-match-score win">2:0</span>
</div>
<div class="tp-match">
<div class="tp-match-left"><span class="tp-match-date">20.10.26</span><span class="tp-match-tour">BLAST</span><span class="tp-match-opp">vs Falcons</span></div>
<span class="tp-match-score win">2:1</span>
</div>
<div class="tp-match">
<div class="tp-match-left"><span class="tp-match-date">18.10.26</span><span class="tp-match-tour">BLAST</span><span class="tp-match-opp">vs Liquid</span></div>
<span class="tp-match-score win">2:0</span>
</div>
</div>

<div class="tp-box">
<h3>Турниры 2026</h3>
<div class="tp-tour-item">
<div class="tp-tour-place">1</div>
<div class="tp-tour-info"><b>The International 2026</b><span>Август 2026</span></div>
<div class="tp-tour-prize"><b>$2.5M</b><span>чемпионы</span></div>
</div>
<div class="tp-tour-item">
<div class="tp-tour-place">2</div>
<div class="tp-tour-info"><b>BLAST SLAM VIII</b><span>Октябрь 2026</span></div>
<div class="tp-tour-prize"><b>$400K</b><span>финалисты</span></div>
</div>
<div class="tp-tour-item">
<div class="tp-tour-place">3</div>
<div class="tp-tour-info"><b>PGL Wallachia Season 9</b><span>Сентябрь 2026</span></div>
<div class="tp-tour-prize"><b>$150K</b><span>3-е место</span></div>
</div>
<div class="tp-tour-item">
<div class="tp-tour-place">1</div>
<div class="tp-tour-info"><b>DreamLeague Season 25</b><span>Июнь 2026</span></div>
<div class="tp-tour-prize"><b>$500K</b><span>чемпионы</span></div>
</div>
</div>

<div class="tp-box">
<h3>FAQ</h3>
<div class="tp-faq"><b>Сколько The International выиграла Team Spirit?</b><p>Team Spirit выиграла The International трижды: в 2021, 2023 и 2026 годах. Это одна из самых успешных команд в истории Dota 2.</p></div>
<div class="tp-faq"><b>Кто капитан Team Spirit?</b><p>Капитан команды — Miposhka (Yaroslav Naidenov), который руководит командой с 2020 года.</p></div>
<div class="tp-faq"><b>Какой винрейт у Spirit в 2026?</b><p>Team Spirit имеет винрейт около 65% в 2026 году, стабильно входя в топ-3 мирового рейтинга.</p></div>
</div>

<div class="tp-links">
<a href="/prognozy/?s=spirit">Прогнозы на Spirit</a>
<a href="/?s=team+spirit">Новости Spirit</a>
</div>
</div>

<script type="application/ld+json">
{"@context":"https://schema.org","@type":"SportsTeam","name":"Team Spirit","sport":"Dota 2","url":"https://beteasy.ru/teams/dota2/team-spirit/","foundingDate":"2015","location":{"@type":"Place","name":"Россия"},"member":[{"@type":"Person","name":"Yatoro"},{"@type":"Person","name":"Larl"},{"@type":"Person","name":"Collapse"},{"@type":"Person","name":"Mira"},{"@type":"Person","name":"Miposhka"}]}
</script>
<!-- /wp:html -->
'''

def main():
    with httpx.Client(timeout=60) as client:
        r = client.get(WP_URL + "/wp-json/wp/v2/pages", params={"slug": "team-spirit", "parent": 1433}, auth=AUTH)
        if r.status_code == 200 and r.json():
            pid = r.json()[0]["id"]
            r2 = client.post(WP_URL + "/wp-json/wp/v2/pages/" + str(pid), json={"content": PAGE}, auth=AUTH)
            print("OK" if r2.status_code in (200, 201) else "ERR")
        else:
            print("ERR: page not found")

if __name__ == "__main__":
    main()
