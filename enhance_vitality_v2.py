#!/usr/bin/env python3
"""Add recent matches, join dates, former players to Vitality."""

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
.tp-hero{display:flex;justify-content:space-between;align-items:flex-start;gap:20px;padding:24px;background:#0E1016;border:1px solid rgba(121,130,155,.2);border-radius:16px;margin-bottom:16px}
.tp-hero-left{display:flex;align-items:center;gap:16px}
.tp-logo{width:80px;height:80px;object-fit:contain;background:#fff;border-radius:8px;padding:8px}
.tp-hero h1{font-family:Unbounded,sans-serif;font-size:24px;margin:0;text-transform:uppercase;color:#EDF0F7}
.tp-meta{color:#79829B;font-size:13px;margin:4px 0}
.tp-meta a{color:#D6FF3B}
.tp-titles{color:#D6FF3B;font-weight:600;margin-top:8px;font-size:14px}
.tp-stats-row{display:flex;gap:20px;margin-top:12px;flex-wrap:wrap}
.tp-stat{text-align:center;min-width:70px}
.tp-stat b{display:block;font-family:"JetBrains Mono",monospace;font-size:18px;color:#D6FF3B}
.tp-stat span{font-size:10px;color:#79829B;text-transform:uppercase}
.tp-box{background:#0E1016;border:1px solid rgba(121,130,155,.2);border-radius:12px;padding:18px;margin:12px 0}
.tp-box h3{font-family:Unbounded,sans-serif;font-size:13px;margin:0 0 12px;text-transform:uppercase;color:#EDF0F7}
.tp-form{display:flex;gap:6px}
.tp-fb{width:32px;height:32px;display:flex;align-items:center;justify-content:center;border-radius:6px;font-weight:700;font-size:12px;color:#fff}
.tp-map-table{width:100%;border-collapse:collapse}
.tp-map-table th,.tp-map-table td{padding:10px 8px;text-align:left;font-size:13px;border-bottom:1px solid rgba(121,130,155,.15)}
.tp-map-table th{color:#79829B;font-weight:500;font-size:11px;text-transform:uppercase}
.tp-map-table td{color:#EDF0F7}
.tp-map-table .win{color:#27ae60}
.tp-map-table .loss{color:#e74c3c}
.tp-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:12px}
.tp-player{display:flex;align-items:center;gap:12px;padding:14px;background:#141827;border-radius:10px}
.tp-player img{width:52px;height:52px;border-radius:50%}
.tp-player-info{flex:1}
.tp-player b{display:block;color:#EDF0F7;font-size:14px}
.tp-player .role{font-size:10px;color:#D6FF3B;text-transform:uppercase}
.tp-player .name{font-size:11px;color:#79829B}
.tp-player .joined{font-size:10px;color:#79829B;margin-top:2px}
.tp-player-stats{display:flex;gap:12px;margin-top:6px}
.tp-player-stats span{font-size:11px;color:#9AA3B8}
.tp-player-stats b{color:#D6FF3B;font-family:"JetBrains Mono",monospace}
.tp-match{display:flex;justify-content:space-between;align-items:center;padding:12px;background:#141827;border-radius:8px;margin-bottom:8px}
.tp-match-left{display:flex;align-items:center;gap:12px}
.tp-match-date{font-size:11px;color:#79829B;min-width:70px}
.tp-match-tour{font-size:11px;color:#D6FF3B;min-width:50px}
.tp-match-opp{color:#EDF0F7;font-size:13px}
.tp-match-score{font-family:"JetBrains Mono",monospace;font-weight:700;font-size:14px}
.tp-match-score.win{color:#27ae60}
.tp-match-score.loss{color:#e74c3c}
.tp-tour-item{display:flex;justify-content:space-between;align-items:center;padding:12px;background:#141827;border-radius:8px;margin-bottom:8px}
.tp-tour-place{width:40px;height:40px;display:flex;align-items:center;justify-content:center;background:#D6FF3B;color:#07080C;font-weight:700;border-radius:8px;font-size:14px}
.tp-tour-info{flex:1;margin-left:12px}
.tp-tour-info b{display:block;color:#EDF0F7;font-size:13px}
.tp-tour-info span{font-size:11px;color:#79829B}
.tp-tour-prize{text-align:right}
.tp-tour-prize b{display:block;color:#D6FF3B;font-family:"JetBrains Mono",monospace;font-size:14px}
.tp-tour-prize span{font-size:10px;color:#79829B}
.tp-faq{margin:0 0 12px;padding:16px;background:#141827;border-radius:10px}
.tp-faq b{display:block;color:#EDF0F7;margin-bottom:8px}
.tp-faq p{margin:0;color:#9AA3B8;font-size:14px;line-height:1.6}
.tp-links{display:flex;gap:12px;margin-top:16px}
.tp-links a{padding:10px 16px;background:#D6FF3B;color:#07080C;text-decoration:none;border-radius:8px;font-size:13px;font-weight:600}
.tp-links a:hover{opacity:.9}
</style>

<div class="tp">
<div class="bread"><a href="/">Главная</a><span>→</span><a href="/teams/">Команды</a><span>→</span><a href="/teams/cs2/">CS2</a><span>→</span><span>Team Vitality</span></div>

<div class="tp-hero">
<div class="tp-hero-left">
<img src="https://logo.clearbit.com/teamvitality.gg" alt="Team Vitality" class="tp-logo">
<div>
<h1>TEAM VITALITY</h1>
<p class="tp-meta">CS2 · Франция · <a href="https://www.team-vitality.fr/" target="_blank" rel="nofollow">team-vitality.fr</a></p>
<p class="tp-meta">Основан: 2018 (CS2 состав с 2023)</p>
<p class="tp-titles">1 Major · #1 HLTV · $5.7M призовых</p>
<div class="tp-stats-row">
<div class="tp-stat"><b>224</b><span>Матчей</span></div>
<div class="tp-stat"><b>177</b><span>Побед</span></div>
<div class="tp-stat"><b>79%</b><span>Винрейт</span></div>
<div class="tp-stat"><b>47</b><span>Поражений</span></div>
</div>
</div>
</div>
</div>

<div class="tp-box">
<h3>Форма</h3>
<div class="tp-form">
<span class="tp-fb" style="background:#27ae60">W</span>
<span class="tp-fb" style="background:#27ae60">W</span>
<span class="tp-fb" style="background:#27ae60">W</span>
<span class="tp-fb" style="background:#27ae60">W</span>
<span class="tp-fb" style="background:#e74c3c">L</span>
</div>
</div>

<div class="tp-box">
<h3>Последние матчи</h3>
<div class="tp-match">
<div class="tp-match-left"><span class="tp-match-date">29.10.26</span><span class="tp-match-tour">PGL</span><span class="tp-match-opp">vs NAVI</span></div>
<span class="tp-match-score win">13:6</span>
</div>
<div class="tp-match">
<div class="tp-match-left"><span class="tp-match-date">29.10.26</span><span class="tp-match-tour">PGL</span><span class="tp-match-opp">vs NAVI</span></div>
<span class="tp-match-score loss">5:13</span>
</div>
<div class="tp-match">
<div class="tp-match-left"><span class="tp-match-date">29.10.26</span><span class="tp-match-tour">PGL</span><span class="tp-match-opp">vs NAVI</span></div>
<span class="tp-match-score win">13:9</span>
</div>
<div class="tp-match">
<div class="tp-match-left"><span class="tp-match-date">27.10.26</span><span class="tp-match-tour">PGL</span><span class="tp-match-opp">vs NAVI</span></div>
<span class="tp-match-score win">13:2</span>
</div>
<div class="tp-match">
<div class="tp-match-left"><span class="tp-match-date">26.10.26</span><span class="tp-match-tour">PGL</span><span class="tp-match-opp">vs FUT</span></div>
<span class="tp-match-score loss">10:13</span>
</div>
<div class="tp-match">
<div class="tp-match-left"><span class="tp-match-date">04.10.26</span><span class="tp-match-tour">EPL</span><span class="tp-match-opp">vs NAVI</span></div>
<span class="tp-match-score loss">5:13</span>
</div>
</div>

<div class="tp-box">
<h3>Статистика по картам</h3>
<table class="tp-map-table">
<tr><th>#</th><th>Карта</th><th>И</th><th>В</th><th>П</th><th>%</th></tr>
<tr><td>1</td><td>Mirage</td><td>5</td><td class="win">5</td><td>0</td><td>100%</td></tr>
<tr><td>2</td><td>Inferno</td><td>4</td><td class="win">4</td><td>0</td><td>100%</td></tr>
<tr><td>3</td><td>Dust2</td><td>7</td><td class="win">6</td><td class="loss">1</td><td>86%</td></tr>
<tr><td>4</td><td>Cache</td><td>6</td><td class="win">5</td><td class="loss">1</td><td>83%</td></tr>
<tr><td>5</td><td>Anubis</td><td>4</td><td class="win">1</td><td class="loss">3</td><td>25%</td></tr>
<tr><td>6</td><td>Nuke</td><td>1</td><td>0</td><td class="loss">1</td><td>0%</td></tr>
</table>
</div>

<div class="tp-box">
<h3>Текущий состав</h3>
<div class="tp-grid">
<div class="tp-player">
<img src="https://ui-avatars.com/api/?name=ZY&background=141827&color=EDF0F7&size=104" alt="ZywOo">
<div class="tp-player-info">
<span class="role">AWPer</span>
<b>ZywOo</b>
<span class="name">Mathieu Herbaut · Франция</span>
<span class="joined">В команде с 29.09.2023</span>
<div class="tp-player-stats"><span>Матчей: <b>224</b></span><span>WR: <b>79%</b></span></div>
</div>
</div>
<div class="tp-player">
<img src="https://ui-avatars.com/api/?name=AP&background=141827&color=EDF0F7&size=104" alt="apEX">
<div class="tp-player-info">
<span class="role">IGL</span>
<b>apEX</b>
<span class="name">Dan Madesclaire · Франция</span>
<span class="joined">В команде с 29.09.2023</span>
<div class="tp-player-stats"><span>Матчей: <b>219</b></span><span>WR: <b>79%</b></span></div>
</div>
</div>
<div class="tp-player">
<img src="https://ui-avatars.com/api/?name=FL&background=141827&color=EDF0F7&size=104" alt="flameZ">
<div class="tp-player-info">
<span class="role">Entry</span>
<b>flameZ</b>
<span class="name">Shahar Shushan · Израиль</span>
<span class="joined">В команде с 29.09.2023</span>
<div class="tp-player-stats"><span>Матчей: <b>224</b></span><span>WR: <b>79%</b></span></div>
</div>
</div>
<div class="tp-player">
<img src="https://ui-avatars.com/api/?name=ME&background=141827&color=EDF0F7&size=104" alt="mezii">
<div class="tp-player-info">
<span class="role">Rifler</span>
<b>mezii</b>
<span class="name">William Merriman · Великобритания</span>
<span class="joined">В команде с 08.11.2023</span>
<div class="tp-player-stats"><span>Матчей: <b>212</b></span><span>WR: <b>81%</b></span></div>
</div>
</div>
<div class="tp-player">
<img src="https://ui-avatars.com/api/?name=RO&background=141827&color=EDF0F7&size=104" alt="ropz">
<div class="tp-player-info">
<span class="role">Lurker</span>
<b>ropz</b>
<span class="name">Robin Kool · Эстония</span>
<span class="joined">В команде с 10.01.2025</span>
<div class="tp-player-stats"><span>Матчей: <b>150</b></span><span>WR: <b>83%</b></span></div>
</div>
</div>
</div>
</div>

<div class="tp-box">
<h3>Бывшие игроки</h3>
<div class="tp-grid">
<div class="tp-player">
<img src="https://ui-avatars.com/api/?name=SP&background=141827&color=79829B&size=104" alt="Spinx">
<div class="tp-player-info">
<span class="role">Rifler</span>
<b>Spinx</b>
<span class="name">Lotan Giladi · Израиль</span>
<span class="joined">2023 — 2025</span>
</div>
</div>
<div class="tp-player">
<img src="https://ui-avatars.com/api/?name=DU&background=141827&color=79829B&size=104" alt="dupreeh">
<div class="tp-player-info">
<span class="role">Rifler</span>
<b>dupreeh</b>
<span class="name">Peter Rasmussen · Дания</span>
<span class="joined">2020 — 2023</span>
</div>
</div>
<div class="tp-player">
<img src="https://ui-avatars.com/api/?name=MA&background=141827&color=79829B&size=104" alt="Magisk">
<div class="tp-player-info">
<span class="role">Rifler</span>
<b>Magisk</b>
<span class="name">Emil Reif · Дания</span>
<span class="joined">2021 — 2023</span>
</div>
</div>
</div>
</div>

<div class="tp-box">
<h3>Тренер</h3>
<div class="tp-player">
<img src="https://ui-avatars.com/api/?name=XT&background=D6FF3B&color=07080C&size=104" alt="XTQZZZ">
<div class="tp-player-info">
<span class="role">Coach</span>
<b>XTQZZZ</b>
<span class="name">Rémy Quoniam · с 13.10.2023</span>
</div>
</div>
</div>

<div class="tp-box">
<h3>Турниры 2026</h3>
<div class="tp-tour-item">
<div class="tp-tour-place">1</div>
<div class="tp-tour-info"><b>ESL Pro League Season 24</b><span>Катовице · 03.10 — 11.10.2026</span></div>
<div class="tp-tour-prize"><b>$295 000</b><span>из $1 000 000</span></div>
</div>
<div class="tp-tour-item">
<div class="tp-tour-place">1</div>
<div class="tp-tour-info"><b>StarLadder StarSeries Fall</b><span>17.09 — 20.09.2026</span></div>
<div class="tp-tour-prize"><b>$100 000</b><span>из $250 000</span></div>
</div>
<div class="tp-tour-item">
<div class="tp-tour-place">3</div>
<div class="tp-tour-info"><b>BLAST Open Fall 2026</b><span>26.08 — 06.09.2026</span></div>
<div class="tp-tour-prize"><b>$40 000</b><span>из $400 000</span></div>
</div>
<div class="tp-tour-item">
<div class="tp-tour-place">1</div>
<div class="tp-tour-info"><b>IEM Rio 2026</b><span>Рио-де-Жанейро · 13.04 — 19.04.2026</span></div>
<div class="tp-tour-prize"><b>$125 000</b><span>из $300 000</span></div>
</div>
<div class="tp-tour-item">
<div class="tp-tour-place">1</div>
<div class="tp-tour-info"><b>PGL Cluj-Napoca 2026</b><span>Румыния · 14.02 — 22.02.2026</span></div>
<div class="tp-tour-prize"><b>$225 000</b><span>из $625 000</span></div>
</div>
</div>

<div class="tp-box">
<h3>FAQ</h3>
<div class="tp-faq"><b>Кто капитан Team Vitality?</b><p>Капитан Team Vitality — apEX (Dan Madesclaire), французский IGL, который руководит командой с 29 сентября 2023 года.</p></div>
<div class="tp-faq"><b>Сколько Major выиграла Vitality?</b><p>Team Vitality выиграла 1 Major. Команда стабильно входит в топ-3 мирового рейтинга HLTV.</p></div>
<div class="tp-faq"><b>Какой винрейт у Vitality в 2026?</b><p>Team Vitality имеет винрейт 79% — 177 побед из 224 матчей. Это лучший показатель среди топ-команд CS2.</p></div>
<div class="tp-faq"><b>Кто лучший игрок Vitality?</b><p>ZywOo (Mathieu Herbaut) — лучший AWPer в мире по версии HLTV. Он является ключевым игроком команды с 2023 года.</p></div>
<div class="tp-faq"><b>Когда ropz присоединился к Vitality?</b><p>Эстонский lurker ropz (Robin Kool) присоединился к Team Vitality 10 января 2025 года, заменив Spinx.</p></div>
</div>

<div class="tp-links">
<a href="/prognozy/?s=vitality">Прогнозы на Vitality</a>
<a href="/?s=vitality">Новости Vitality</a>
</div>
</div>

<script type="application/ld+json">
{"@context":"https://schema.org","@type":"SportsTeam","name":"Team Vitality","sport":"CS2","url":"https://beteasy.ru/teams/cs2/vitality/","foundingDate":"2018","location":{"@type":"Place","name":"Франция"},"coach":{"@type":"Person","name":"XTQZZZ"},"member":[{"@type":"Person","name":"ZywOo"},{"@type":"Person","name":"apEX"},{"@type":"Person","name":"flameZ"},{"@type":"Person","name":"mezii"},{"@type":"Person","name":"ropz"}]}
</script>
<!-- /wp:html -->
'''

def main():
    with httpx.Client(timeout=60) as client:
        r = client.get(WP_URL + "/wp-json/wp/v2/pages", params={"slug": "vitality", "parent": 1404}, auth=AUTH)
        if r.status_code == 200 and r.json():
            pid = r.json()[0]["id"]
            r2 = client.post(WP_URL + "/wp-json/wp/v2/pages/" + str(pid), json={"content": PAGE}, auth=AUTH)
            print("OK" if r2.status_code in (200, 201) else "ERR")
        else:
            print("ERR: page not found")

if __name__ == "__main__":
    main()
