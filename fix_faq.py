#!/usr/bin/env python3
"""Fix FAQ insertion into team page."""

import os
import httpx

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

def main():
    with httpx.Client(timeout=60) as client:
        r = client.get(WP_URL + "/wp-json/wp/v2/pages", params={"slug": "team-real-madrid", "context": "edit"}, auth=AUTH)
        if r.status_code != 200 or not r.json():
            print("ERR: page not found")
            return
        
        page = r.json()[0]
        content = page.get("content", {}).get("raw", "")
        
        # Find the news section and insert FAQ after it
        news_end = content.find('</div>\n</div>\n\n<script>')
        if news_end == -1:
            # Try alternative pattern
            news_end = content.find('Последние новости')
            if news_end != -1:
                # Find the closing of news section
                news_end = content.find('</div>', news_end + 100)
                if news_end != -1:
                    news_end = content.find('</div>', news_end + 1)
        
        if news_end != -1 and "FAQPage" not in content:
            content = content[:news_end] + FAQ_HTML + content[news_end:]
            print("FAQ inserted at position", news_end)
        elif "FAQPage" in content:
            print("FAQ already exists")
        else:
            # Append before script
            script_pos = content.find('<script>')
            if script_pos != -1:
                content = content[:script_pos] + FAQ_HTML + "\n" + content[script_pos:]
                print("FAQ appended before script")
            else:
                content = content + FAQ_HTML
                print("FAQ appended at end")
        
        r2 = client.post(WP_URL + "/wp-json/wp/v2/pages/" + str(page["id"]), 
                        json={"content": content}, auth=AUTH)
        print("OK" if r2.status_code in (200, 201) else "ERR")

if __name__ == "__main__":
    main()
