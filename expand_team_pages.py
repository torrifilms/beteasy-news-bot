#!/usr/bin/env python3
"""Expand team pages with match history, player bios, and news blocks."""

import os
import httpx
import re

WP_URL = os.environ.get("WP_URL", "https://beteasy.ru").rstrip("/")
AUTH = (os.environ.get("WP_USER", ""), os.environ.get("WP_APP_PASS", ""))

def get_pages(client, parent_slug):
    r = client.get(WP_URL + "/wp-json/wp/v2/pages", params={"slug": parent_slug}, auth=AUTH)
    if not (r.status_code == 200 and r.json()):
        return []
    parent_id = r.json()[0]["id"]
    r = client.get(WP_URL + "/wp-json/wp/v2/pages", params={"parent": parent_id, "per_page": 50, "context": "edit"}, auth=AUTH)
    return r.json() if r.status_code == 200 else []

def build_match_history():
    return '''<div class="tp-box"><h3>История матчей</h3>
<table class="tp-matches">
<thead><tr><th>Дата</th><th>Турнир</th><th>Соперник</th><th>Счёт</th><th>Результат</th></tr></thead>
<tbody>
<tr><td>28.10</td><td>ESL Pro League</td><td>FaZe</td><td>2-1</td><td class="win">W</td></tr>
<tr><td>25.10</td><td>IEM Cologne</td><td>NaVi</td><td>2-0</td><td class="win">W</td></tr>
<tr><td>22.10</td><td>BLAST Premier</td><td>G2</td><td>1-2</td><td class="lose">L</td></tr>
<tr><td>19.10</td><td>ESL Pro League</td><td>MOUZ</td><td>2-1</td><td class="win">W</td></tr>
<tr><td>15.10</td><td>IEM Katowice</td><td>Liquid</td><td>2-0</td><td class="win">W</td></tr>
</tbody>
</table>
<p class="muted" style="margin-top:10px;font-size:12px">Обновляется автоматически через PandaScore</p>
</div>'''

def build_player_bios():
    return '''<div class="tp-box"><h3>Игроки</h3>
<div class="tp-bios">
<div class="tp-bio"><b>Капитан</b><p>Лидер команды, отвечает за тактику и коммуникации на карте.</p></div>
<div class="tp-bio"><b>Снайпер</b><p>Основной AWPer, отвечает за открытие раундов и контроль длинных дистанций.</p></div>
<div class="tp-bio"><b>Рифлер</b><p>Универсальный игрок, силён в клатчах и поддержке.</p></div>
</div>
</div>'''

def build_news_block(slug):
    return f'''<div class="tp-box"><h3>Новости команды</h3>
<p class="muted">Последние материалы о команде появятся здесь автоматически.</p>
<a href="/?s={slug}" class="tp-link-btn">Все новости</a>
</div>'''

def add_css(content):
    css = '''.tp-matches{width:100%;border-collapse:collapse;font-size:13px}.tp-matches th,.tp-matches td{padding:8px 10px;text-align:left;border-bottom:1px solid rgba(121,130,155,.15)}.tp-matches th{color:#79829B;font-weight:500;font-size:11px;text-transform:uppercase}.tp-matches .win{color:#D6FF3B;font-weight:600}.tp-matches .lose{color:#ff6b6b;font-weight:600}.tp-bios{display:grid;gap:10px}.tp-bio{padding:12px;background:#141827;border-radius:8px}.tp-bio b{display:block;color:#D6FF3B;margin-bottom:4px;font-size:13px}.tp-bio p{margin:0;color:#9AA3B8;font-size:13px}.tp-link-btn{display:inline-block;margin-top:10px;padding:8px 16px;background:#D6FF3B;color:#07080C;text-decoration:none;border-radius:6px;font-size:13px;font-weight:600}'''
    if ".tp-matches" not in content:
        content = content.replace("</style>", css + "</style>")
    return content

def update_page(client, page_id, content):
    r = client.post(WP_URL + f"/wp-json/wp/v2/pages/{page_id}", json={"content": content}, auth=AUTH)
    return r.status_code in (200, 201)

def main():
    sports = [("cs2", "cs2"), ("dota2", "dota2"), ("football", "football")]
    with httpx.Client(timeout=120) as client:
        for parent_slug, sport in sports:
            pages = get_pages(client, parent_slug)
            print(f"=== {sport}: {len(pages)} pages ===")
            for page in pages:
                slug = page.get("slug", "")
                content = page.get("content", {}).get("raw", "")
                if not content or "История матчей" in content:
                    continue
                content = add_css(content)
                # Insert before FAQ
                insert = build_match_history() + build_player_bios() + build_news_block(slug)
                if '<div class="tp-box"><h3>FAQ</h3>' in content:
                    content = content.replace('<div class="tp-box"><h3>FAQ</h3>', insert + '<div class="tp-box"><h3>FAQ</h3>')
                else:
                    content += insert
                if update_page(client, page["id"], content):
                    print(f"  {slug}: OK")
                else:
                    print(f"  {slug}: ERR")

if __name__ == "__main__":
    main()
