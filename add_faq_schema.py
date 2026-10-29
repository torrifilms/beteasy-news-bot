#!/usr/bin/env python3
"""Add FAQ and SportsTeam schema to team page."""

import os
import httpx
import re

WP_URL = os.environ.get("WP_URL", "https://beteasy.ru").rstrip("/")
AUTH = (os.environ.get("WP_USER", ""), os.environ.get("WP_APP_PASS", ""))

FAQ_HTML = '''
<div class="tp-box" itemscope itemtype="https://schema.org/FAQPage">
<h3>FAQ</h3>
<div class="tp-faq" itemscope itemprop="mainEntity" itemtype="https://schema.org/Question">
<b itemprop="name">Кто тренер Реала в 2026?</b>
<div itemscope itemprop="acceptedAnswer" itemtype="https://schema.org/Answer">
<p itemprop="text">Жозе Моуринью — главный тренер Реал Мадрид в сезоне 2026/27.</p>
</div>
</div>
<div class="tp-faq" itemscope itemprop="mainEntity" itemtype="https://schema.org/Question">
<b itemprop="name">Сколько титулов Лиги чемпионов у Реала?</b>
<div itemscope itemprop="acceptedAnswer" itemtype="https://schema.org/Answer">
<p itemprop="text">Реал Мадрид — рекордсмен по числу побед в Лиге чемпионов: 15 титулов.</p>
</div>
</div>
<div class="tp-faq" itemscope itemprop="mainEntity" itemtype="https://schema.org/Question">
<b itemprop="name">Какой стадион у Реал Мадрид?</b>
<div itemscope itemprop="acceptedAnswer" itemtype="https://schema.org/Answer">
<p itemprop="text">Домашний стадион — Сантьяго Бернабеу в Мадриде, вместимость около 81 000 зрителей.</p>
</div>
</div>
<div class="tp-faq" itemscope itemprop="mainEntity" itemtype="https://schema.org/Question">
<b itemprop="name">Кто капитан Реал Мадрид?</b>
<div itemscope itemprop="acceptedAnswer" itemtype="https://schema.org/Answer">
<p itemprop="text">Капитан команды — Начо Фернандес. Вице-капитаны: Модрич, Карвахаль.</p>
</div>
</div>
<div class="tp-faq" itemscope itemprop="mainEntity" itemtype="https://schema.org/Question">
<b itemprop="name">В какой лиге играет Реал?</b>
<div itemscope itemprop="acceptedAnswer" itemtype="https://schema.org/Answer">
<p itemprop="text">Реал Мадрид выступает в Ла Лиге (Испания) и Лиге чемпионов УЕФА.</p>
</div>
</div>
</div>
'''

SCHEMA_JSON = '''
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "SportsTeam",
  "name": "Реал Мадрид",
  "alternateName": "Real Madrid",
  "sport": "Football",
  "memberOf": {
    "@type": "SportsOrganization",
    "name": "Ла Лига"
  },
  "coach": {
    "@type": "Person",
    "name": "Жозе Моуринью"
  },
  "location": {
    "@type": "StadiumOrArena",
    "name": "Сантьяго Бернабеу",
    "address": "Мадрид, Испания"
  },
  "foundingDate": "1902",
  "url": "https://beteasy.ru/team-real-madrid/"
}
</script>
'''

CSS = '''
.tp-faq{margin:10px 0;padding:10px;background:#141827;border-radius:8px}
.tp-faq b{display:block;color:#EDF0F7;margin-bottom:6px;cursor:pointer}
.tp-faq p{margin:0;color:#79829B;font-size:14px;line-height:1.5}
'''

def main():
    with httpx.Client(timeout=60) as client:
        r = client.get(WP_URL + "/wp-json/wp/v2/pages", params={"slug": "team-real-madrid"}, auth=AUTH)
        if r.status_code != 200 or not r.json():
            print("ERR: page not found")
            return
        
        page = r.json()[0]
        content = page.get("content", {}).get("raw") or page.get("content", {}).get("rendered", "")
        
        # Add CSS for FAQ
        if ".tp-faq" not in content:
            content = content.replace("</style>", CSS + "</style>")
        
        # Add FAQ before closing tp div
        if 'itemtype="https://schema.org/FAQPage"' not in content:
            content = content.replace("</div>\n\n<script>", FAQ_HTML + "\n</div>\n\n<script>")
        
        # Add schema before closing body or at end
        if "SportsTeam" not in content:
            content = content + "\n" + SCHEMA_JSON
        
        r2 = client.post(WP_URL + "/wp-json/wp/v2/pages/" + str(page["id"]), 
                        json={"content": content}, auth=AUTH)
        print("OK" if r2.status_code in (200, 201) else "ERR")

if __name__ == "__main__":
    main()
