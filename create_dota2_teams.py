#!/usr/bin/env python3
"""Create current top Dota 2 teams for 2026."""

import os
import httpx

WP_URL = os.environ.get("WP_URL", "https://beteasy.ru").rstrip("/")
AUTH = (os.environ.get("WP_USER", ""), os.environ.get("WP_APP_PASS", ""))

def get_or_create(client, slug, title, content, parent):
    r = client.get(WP_URL + "/wp-json/wp/v2/pages", params={"slug": slug, "parent": parent}, auth=AUTH)
    if r.status_code == 200 and r.json():
        pid = r.json()[0]["id"]
        client.post(WP_URL + "/wp-json/wp/v2/pages/" + str(pid), json={"content": content}, auth=AUTH)
        return "updated"
    r = client.post(WP_URL + "/wp-json/wp/v2/pages", json={
        "title": title, "slug": slug, "status": "publish", "parent": parent, "content": content
    }, auth=AUTH)
    return "created" if r.status_code in (200, 201) else "error"

def make_page(name, slug, country, prize, rank):
    return f'''<!-- wp:html -->
<style>.tp{{max-width:960px;margin:20px auto;padding:0 16px}}.bread{{display:flex;gap:8px;margin-bottom:16px;font-size:13px}}.bread a{{color:#79829B;text-decoration:none}}.bread a:hover{{color:#D6FF3B}}.bread span{{color:#79829B}}.tp-hero{{display:flex;align-items:center;gap:16px;padding:24px;background:#0E1016;border:1px solid rgba(121,130,155,.2);border-radius:16px;margin-bottom:16px}}.tp-logo{{width:80px;height:80px;object-fit:contain;background:#fff;border-radius:8px;padding:8px}}.tp-hero h1{{font-family:Unbounded,sans-serif;font-size:24px;margin:0;text-transform:uppercase;color:#EDF0F7}}.tp-meta{{color:#79829B;font-size:13px;margin:4px 0}}.tp-titles{{color:#D6FF3B;font-weight:600;margin-top:8px;font-size:14px}}.tp-stats-row{{display:flex;gap:20px;margin-top:12px}}.tp-stat{{text-align:center}}.tp-stat b{{display:block;font-family:"JetBrains Mono",monospace;font-size:18px;color:#D6FF3B}}.tp-stat span{{font-size:10px;color:#79829B;text-transform:uppercase}}.tp-box{{background:#0E1016;border:1px solid rgba(121,130,155,.2);border-radius:12px;padding:18px;margin:12px 0}}.tp-box h3{{font-family:Unbounded,sans-serif;font-size:13px;margin:0 0 12px;text-transform:uppercase;color:#EDF0F7}}.tp-links{{display:flex;gap:12px;margin-top:16px}}.tp-links a{{padding:10px 16px;background:#D6FF3B;color:#07080C;text-decoration:none;border-radius:8px;font-size:13px;font-weight:600}}</style>
<div class="tp">
<div class="bread"><a href="/">Главная</a><span>→</span><a href="/teams/">Команды</a><span>→</span><a href="/teams/dota2/">Dota 2</a><span>→</span><span>{name}</span></div>
<div class="tp-hero">
<img src="https://logo.clearbit.com/{slug}.gg" alt="{name}" class="tp-logo">
<div>
<h1>{name.upper()}</h1>
<p class="tp-meta">Dota 2 · {country}</p>
<p class="tp-titles">#{rank} рейтинг · {prize} призовых</p>
</div>
</div>
<div class="tp-box"><h3>Состав 2026</h3><p class="muted">Обновляется</p></div>
<div class="tp-box"><h3>Последние матчи</h3><p class="muted">Обновляется автоматически</p></div>
<div class="tp-box"><h3>Турниры</h3><p class="muted">Обновляется</p></div>
<div class="tp-links">
<a href="/prognozy/?s={slug}">Прогнозы</a>
<a href="/?s={slug}">Новости</a>
</div>
</div>
<script type="application/ld+json">{{"@context":"https://schema.org","@type":"SportsTeam","name":"{name}","sport":"Dota 2","url":"https://beteasy.ru/teams/dota2/{slug}/"}}</script>
<!-- /wp:html -->'''

def main():
    # Get dota2 parent
    with httpx.Client(timeout=60) as client:
        r = client.get(WP_URL + "/wp-json/wp/v2/pages", params={"slug": "dota2"}, auth=AUTH)
        if not (r.status_code == 200 and r.json()):
            print("ERR: dota2 hub not found")
            return
        parent_id = r.json()[0]["id"]
        print(f"Dota2 parent: {parent_id}")

        # Top teams from dota2.ru and rankings (Oct 2026)
        teams = [
            ("PARIVISION", "parivision", "Россия", "$4.5M", 1),
            ("Team Spirit", "team-spirit", "Россия", "$33.3M", 2),
            ("Team Falcons", "falcons", "Саудовская Аравия", "$7.3M", 3),
            ("Team Yandex", "yandex", "Россия", "$2.8M", 4),
            ("Aurora Gaming", "aurora", "Россия", "$1.9M", 5),
            ("Team Liquid", "liquid", "Европа", "$34.2M", 6),
            ("Natus Vincere", "navi", "Украина", "$6.3M", 7),
            ("Nigma Galaxy", "nigma", "Европа", "$1.9M", 8),
            ("Xtreme Gaming", "xtreme", "Китай", "$3.8M", 9),
            ("1win Team", "1win", "Россия", "$0.7M", 10),
            ("BetBoom Team", "betboom", "Россия", "$2.1M", 11),
            ("OG", "og", "Европа", "$37.8M", 12),
        ]

        for name, slug, country, prize, rank in teams:
            content = make_page(name, slug, country, prize, rank)
            result = get_or_create(client, slug, name, content, parent_id)
            print(f"{name}: {result}")

if __name__ == "__main__":
    main()
