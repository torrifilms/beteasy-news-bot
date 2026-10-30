#!/usr/bin/env python3
"""Create/update CS2 team pages with full template."""

import os
import httpx

WP_URL = os.environ.get("WP_URL", "https://beteasy.ru").rstrip("/")
AUTH = (os.environ.get("WP_USER", ""), os.environ.get("WP_APP_PASS", ""))
CS2_PARENT = 1404

def create_or_update(client, slug, title, content, parent):
    r = client.get(WP_URL + "/wp-json/wp/v2/pages", params={"slug": slug, "parent": parent}, auth=AUTH)
    if r.status_code == 200 and r.json():
        pid = r.json()[0]["id"]
        r2 = client.post(WP_URL + "/wp-json/wp/v2/pages/" + str(pid), json={"content": content}, auth=AUTH)
        return "updated" if r2.status_code in (200, 201) else "error"
    r = client.post(WP_URL + "/wp-json/wp/v2/pages", json={
        "title": title, "slug": slug, "status": "publish", "parent": parent, "content": content
    }, auth=AUTH)
    return "created" if r.status_code in (200, 201) else "error"

def make_page(name, slug, country, founded, major, hltv, matches, wins, winrate, prize, logo_domain):
    return f'''<!-- wp:html -->
<style>.tp{{max-width:960px;margin:20px auto;padding:0 16px}}.bread{{display:flex;gap:8px;margin-bottom:16px;font-size:13px}}.bread a{{color:#79829B;text-decoration:none}}.bread a:hover{{color:#D6FF3B}}.bread span{{color:#79829B}}.tp-hero{{display:flex;align-items:center;gap:16px;padding:24px;background:#0E1016;border:1px solid rgba(121,130,155,.2);border-radius:16px;margin-bottom:16px}}.tp-logo{{width:80px;height:80px;object-fit:contain;background:#fff;border-radius:8px;padding:8px}}.tp-hero h1{{font-family:Unbounded,sans-serif;font-size:24px;margin:0;text-transform:uppercase;color:#EDF0F7}}.tp-meta{{color:#79829B;font-size:13px;margin:4px 0}}.tp-titles{{color:#D6FF3B;font-weight:600;margin-top:8px;font-size:14px}}.tp-stats-row{{display:flex;gap:20px;margin-top:12px}}.tp-stat{{text-align:center}}.tp-stat b{{display:block;font-family:"JetBrains Mono",monospace;font-size:18px;color:#D6FF3B}}.tp-stat span{{font-size:10px;color:#79829B;text-transform:uppercase}}.tp-box{{background:#0E1016;border:1px solid rgba(121,130,155,.2);border-radius:12px;padding:18px;margin:12px 0}}.tp-box h3{{font-family:Unbounded,sans-serif;font-size:13px;margin:0 0 12px;text-transform:uppercase;color:#EDF0F7}}.tp-form{{display:flex;gap:6px}}.tp-fb{{width:32px;height:32px;display:flex;align-items:center;justify-content:center;border-radius:6px;font-weight:700;font-size:12px;color:#fff}}.tp-match{{display:flex;justify-content:space-between;align-items:center;padding:12px;background:#141827;border-radius:8px;margin-bottom:8px}}.tp-match-left{{display:flex;align-items:center;gap:12px}}.tp-match-date{{font-size:11px;color:#79829B;min-width:70px}}.tp-match-tour{{font-size:11px;color:#D6FF3B;min-width:50px}}.tp-match-opp{{color:#EDF0F7;font-size:13px}}.tp-match-score{{font-family:"JetBrains Mono",monospace;font-weight:700;font-size:14px}}.tp-match-score.win{{color:#27ae60}}.tp-match-score.loss{{color:#e74c3c}}.tp-map-table{{width:100%;border-collapse:collapse}}.tp-map-table th,.tp-map-table td{{padding:10px 8px;text-align:left;font-size:13px;border-bottom:1px solid rgba(121,130,155,.15)}}.tp-map-table th{{color:#79829B;font-weight:500;font-size:11px;text-transform:uppercase}}.tp-map-table td{{color:#EDF0F7}}.tp-map-table .win{{color:#27ae60}}.tp-map-table .loss{{color:#e74c3c}}.tp-links{{display:flex;gap:12px;margin-top:16px}}.tp-links a{{padding:10px 16px;background:#D6FF3B;color:#07080C;text-decoration:none;border-radius:8px;font-size:13px;font-weight:600}}</style>
<div class="tp">
<div class="bread"><a href="/">Главная</a><span>→</span><a href="/teams/">Команды</a><span>→</span><a href="/teams/cs2/">CS2</a><span>→</span><span>{name}</span></div>
<div class="tp-hero">
<img src="https://logo.clearbit.com/{logo_domain}" alt="{name}" class="tp-logo">
<div>
<h1>{name.upper()}</h1>
<p class="tp-meta">CS2 · {country} · Основан в {founded}</p>
<p class="tp-titles">{major} Major · #{hltv} HLTV · {prize}</p>
<div class="tp-stats-row">
<div class="tp-stat"><b>{matches}</b><span>Матчей</span></div>
<div class="tp-stat"><b>{wins}</b><span>Побед</span></div>
<div class="tp-stat"><b>{winrate}%</b><span>Винрейт</span></div>
</div>
</div>
</div>
<div class="tp-box"><h3>Форма</h3><div class="tp-form"><span class="tp-fb" style="background:#79829B">—</span></div></div>
<div class="tp-box"><h3>Последние матчи</h3><p class="muted">Обновляется автоматически</p></div>
<div class="tp-box"><h3>Ближайшие матчи</h3><p class="muted">Обновляется автоматически</p></div>
<div class="tp-box"><h3>Статистика по картам</h3><p class="muted">Обновляется автоматически</p></div>
<div class="tp-links">
<a href="/prognozy/?s={slug}">Прогнозы</a>
<a href="/?s={slug}">Новости</a>
</div>
</div>
<script type="application/ld+json">{{"@context":"https://schema.org","@type":"SportsTeam","name":"{name}","sport":"CS2","url":"https://beteasy.ru/teams/cs2/{slug}/"}}</script>
<!-- /wp:html -->'''

def main():
    teams = [
        ("Team Liquid", "liquid", "США", "2000", "0", "7", "180", "98", "54", "$4.2M", "teamliquid.com"),
        ("Astralis", "astralis", "Дания", "2016", "4", "12", "150", "82", "55", "$12.5M", "astralis.gg"),
    ]
    with httpx.Client(timeout=60) as client:
        for name, slug, country, founded, major, hltv, matches, wins, wr, prize, domain in teams:
            content = make_page(name, slug, country, founded, major, hltv, matches, wins, wr, prize, domain)
            result = create_or_update(client, slug, name, content, CS2_PARENT)
            print(f"{name}: {result}")

if __name__ == "__main__":
    main()
