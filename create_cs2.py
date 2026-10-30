#!/usr/bin/env python3
"""Create CS2 hub and team pages with proper URL structure."""

import os
import httpx

WP_URL = os.environ.get("WP_URL", "https://beteasy.ru").rstrip("/")
AUTH = (os.environ.get("WP_USER", ""), os.environ.get("WP_APP_PASS", ""))

def get_or_create_page(client, slug, title, content, parent=0):
    """Get or create page, return ID."""
    r = client.get(WP_URL + "/wp-json/wp/v2/pages", params={"slug": slug, "parent": parent}, auth=AUTH)
    if r.status_code == 200 and r.json():
        return r.json()[0]["id"]
    r = client.post(WP_URL + "/wp-json/wp/v2/pages", json={
        "title": title, "slug": slug, "status": "publish", "parent": parent, "content": content
    }, auth=AUTH)
    return r.json()["id"] if r.status_code in (200, 201) else None

def main():
    with httpx.Client(timeout=60) as client:
        # Create /teams/ parent if not exists
        teams_id = get_or_create_page(client, "teams", "Команды", "<p>Все команды</p>", 0)
        print(f"Teams hub: {teams_id}")
        
        # Create /teams/cs2/ hub
        cs2_hub = '''<!-- wp:html -->
<style>
.cs2-hub{max-width:960px;margin:20px auto;padding:0 16px}
.cs2-hub h1{font-family:Unbounded,sans-serif;font-size:28px;margin:0 0 8px;text-transform:uppercase;color:#EDF0F7}
.cs2-hub .sub{color:#79829B;margin-bottom:24px}
.teams-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:16px}
.team-card{display:flex;flex-direction:column;align-items:center;padding:24px 16px;background:#0E1016;border:1px solid rgba(121,130,155,.2);border-radius:16px;text-decoration:none;transition:all .3s}
.team-card:hover{border-color:rgba(214,255,59,.4);transform:translateY(-4px)}
.team-card img{width:72px;height:72px;object-fit:contain;margin-bottom:12px}
.team-card b{font-family:Unbounded,sans-serif;font-size:14px;color:#EDF0F7;text-transform:uppercase}
.team-card span{font-size:11px;color:#79829B;margin-top:4px}
.bread{display:flex;gap:8px;margin-bottom:16px;font-size:13px}
.bread a{color:#79829B;text-decoration:none}
.bread a:hover{color:#D6FF3B}
.bread span{color:#79829B}
</style>
<div class="cs2-hub">
<div class="bread"><a href="/">Главная</a><span>→</span><a href="/teams/">Команды</a><span>→</span><span>CS2</span></div>
<h1>Команды CS2</h1>
<p class="sub">Топ-команды по Counter-Strike 2. Составы, статистика, результаты матчей.</p>
<div class="teams-grid">
<a href="/teams/cs2/navi/" class="team-card"><img src="https://logo.clearbit.com/navi.gg" alt="NaVi"><b>Natus Vincere</b><span>Украина</span></a>
<a href="/teams/cs2/faze/" class="team-card"><img src="https://logo.clearbit.com/fazeclan.com" alt="FaZe"><b>FaZe Clan</b><span>США</span></a>
<a href="/teams/cs2/g2/" class="team-card"><img src="https://logo.clearbit.com/g2esports.com" alt="G2"><b>G2 Esports</b><span>Европа</span></a>
<a href="/teams/cs2/vitality/" class="team-card"><img src="https://logo.clearbit.com/teamvitality.gg" alt="Vitality"><b>Team Vitality</b><span>Франция</span></a>
<a href="/teams/cs2/spirit/" class="team-card"><img src="https://logo.clearbit.com/teamspirit.gg" alt="Spirit"><b>Team Spirit</b><span>Россия</span></a>
<a href="/teams/cs2/mouz/" class="team-card"><img src="https://logo.clearbit.com/mouz.gg" alt="MOUZ"><b>MOUZ</b><span>Германия</span></a>
<a href="/teams/cs2/liquid/" class="team-card"><img src="https://logo.clearbit.com/teamliquid.com" alt="Liquid"><b>Team Liquid</b><span>США</span></a>
<a href="/teams/cs2/astralis/" class="team-card"><img src="https://logo.clearbit.com/astralis.gg" alt="Astralis"><b>Astralis</b><span>Дания</span></a>
</div>
</div>
<!-- /wp:html -->'''
        
        cs2_id = get_or_create_page(client, "cs2", "Команды CS2", cs2_hub, teams_id)
        print(f"CS2 hub: {cs2_id}")
        
        # Create NaVi page
        navi_page = '''<!-- wp:html -->
<style>
.tp{max-width:960px;margin:20px auto;padding:0 16px}
.bread{display:flex;gap:8px;margin-bottom:16px;font-size:13px}
.bread a{color:#79829B;text-decoration:none}
.bread a:hover{color:#D6FF3B}
.bread span{color:#79829B}
.tp-hero{display:flex;justify-content:space-between;align-items:center;gap:20px;padding:24px;background:#0E1016;border:1px solid rgba(121,130,155,.2);border-radius:16px;margin-bottom:16px}
.tp-hero-left{display:flex;align-items:center;gap:16px}
.tp-logo{width:80px;height:80px;object-fit:contain}
.tp-hero h1{font-family:Unbounded,sans-serif;font-size:24px;margin:0;text-transform:uppercase;color:#EDF0F7}
.tp-meta{color:#79829B;font-size:13px;margin:4px 0}
.tp-titles{color:#D6FF3B;font-weight:600;margin-top:8px;font-size:14px}
.tp-stats-row{display:flex;gap:24px;margin-top:12px}
.tp-stat{text-align:center}
.tp-stat b{display:block;font-family:"JetBrains Mono",monospace;font-size:20px;color:#D6FF3B}
.tp-stat span{font-size:10px;color:#79829B;text-transform:uppercase}
.tp-box{background:#0E1016;border:1px solid rgba(121,130,155,.2);border-radius:12px;padding:18px;margin:12px 0}
.tp-box h3{font-family:Unbounded,sans-serif;font-size:13px;margin:0 0 12px;text-transform:uppercase;color:#EDF0F7}
.tp-form{display:flex;gap:6px}
.tp-fb{width:32px;height:32px;display:flex;align-items:center;justify-content:center;border-radius:6px;font-weight:700;font-size:12px;color:#fff}
.tp-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:12px}
.tp-player{display:flex;align-items:center;gap:12px;padding:12px;background:#141827;border-radius:10px}
.tp-player img{width:48px;height:48px;border-radius:50%}
.tp-player b{display:block;color:#EDF0F7;font-size:14px}
.tp-player span{font-size:11px;color:#79829B}
.tp-player .role{font-size:10px;color:#D6FF3B;text-transform:uppercase}
.tp-faq{margin:0 0 12px;padding:16px;background:#141827;border-radius:10px}
.tp-faq b{display:block;color:#EDF0F7;margin-bottom:8px}
.tp-faq p{margin:0;color:#9AA3B8;font-size:14px;line-height:1.6}
</style>
<div class="tp">
<div class="bread"><a href="/">Главная</a><span>→</span><a href="/teams/">Команды</a><span>→</span><a href="/teams/cs2/">CS2</a><span>→</span><span>NaVi</span></div>
<div class="tp-hero">
<div class="tp-hero-left">
<img src="https://logo.clearbit.com/navi.gg" alt="NaVi" class="tp-logo">
<div>
<h1>NATUS VINCERE</h1>
<p class="tp-meta">CS2 · Украина · Основан в 2009</p>
<p class="tp-titles">2 Major · #6 HLTV</p>
<div class="tp-stats-row">
<div class="tp-stat"><b>59%</b><span>Винрейт</span></div>
<div class="tp-stat"><b>$13.6M</b><span>Призовые</span></div>
<div class="tp-stat"><b>2</b><span>Major</span></div>
</div>
</div>
</div>
</div>
<div class="tp-box">
<h3>Форма</h3>
<div class="tp-form">
<span class="tp-fb" style="background:#27ae60">W</span>
<span class="tp-fb" style="background:#27ae60">W</span>
<span class="tp-fb" style="background:#e74c3c">L</span>
<span class="tp-fb" style="background:#e74c3c">L</span>
<span class="tp-fb" style="background:#27ae60">W</span>
</div>
</div>
<div class="tp-box">
<h3>Состав 2026</h3>
<div class="tp-grid">
<div class="tp-player"><img src="https://ui-avatars.com/api/?name=AL&background=141827&color=EDF0F7&size=96" alt="Aleksib"><div><span class="role">IGL</span><b>Aleksib</b><span>Aleksi Virolainen · Финляндия</span></div></div>
<div class="tp-player"><img src="https://ui-avatars.com/api/?name=B1&background=141827&color=EDF0F7&size=96" alt="b1t"><div><span class="role">Rifler</span><b>b1t</b><span>Valeriy Vakhovskiy · Украина</span></div></div>
<div class="tp-player"><img src="https://ui-avatars.com/api/?name=IM&background=141827&color=EDF0F7&size=96" alt="iM"><div><span class="role">Entry</span><b>iM</b><span>Ivan Mihai · Румыния</span></div></div>
<div class="tp-player"><img src="https://ui-avatars.com/api/?name=W0&background=141827&color=EDF0F7&size=96" alt="w0nderful"><div><span class="role">AWPer</span><b>w0nderful</b><span>Igor Zhdanov · Украина</span></div></div>
<div class="tp-player"><img src="https://ui-avatars.com/api/?name=MA&background=141827&color=EDF0F7&size=96" alt="makazze"><div><span class="role">Rifler</span><b>makazze</b><span>Drin Shaqiri · Косово</span></div></div>
</div>
</div>
<div class="tp-box">
<h3>Тренер</h3>
<div class="tp-player"><img src="https://ui-avatars.com/api/?name=B1&background=D6FF3B&color=07080C&size=96" alt="B1ad3"><div><span class="role">Coach</span><b>B1ad3</b><span>Главный тренер</span></div></div>
</div>
<div class="tp-box">
<h3>FAQ</h3>
<div class="tp-faq"><b>Кто капитан NaVi в 2026?</b><p>Капитан Natus Vincere — Aleksib (Aleksi Virolainen), финский IGL, который руководит командой с 2023 года.</p></div>
<div class="tp-faq"><b>Сколько Major выиграла NaVi?</b><p>NaVi выиграла 2 Major: PGL Major Stockholm 2021 (с s1mple) и PGL Major Copenhagen 2024.</p></div>
<div class="tp-faq"><b>Какой рейтинг HLTV у NaVi?</b><p>NaVi занимает 6 место в мировом рейтинге HLTV по состоянию на октябрь 2026.</p></div>
</div>
</div>
<script type="application/ld+json">{"@context":"https://schema.org","@type":"SportsTeam","name":"Natus Vincere","alternateName":"NaVi","sport":"CS2","url":"https://beteasy.ru/teams/cs2/navi/","foundingDate":"2009"}</script>
<!-- /wp:html -->'''
        
        navi_id = get_or_create_page(client, "navi", "Natus Vincere", navi_page, cs2_id)
        print(f"NaVi: {navi_id}")

if __name__ == "__main__":
    main()
