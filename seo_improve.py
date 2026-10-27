#!/usr/bin/env python3
"""
SEO improvements for beteasy.ru:
1. Add unique content blocks to recent predictions
2. Strengthen internal linking
3. Add FAQ schema to league pages
"""

import os
import re
import httpx
import json
import time

WP_URL = os.environ.get("WP_URL", "https://beteasy.ru").rstrip("/")
AUTH = (os.environ.get("WP_USER", ""), os.environ.get("WP_APP_PASS", ""))
HEADERS = {"User-Agent": "BeteasySEO/1.0", "Content-Type": "application/json"}

def get_recent_predictions(client, limit=15):
    r = client.get(
        f"{WP_URL}/wp-json/wp/v2/prediction",
        params={"per_page": limit, "orderby": "date", "order": "desc", "_fields": "id,title,content,slug,link"},
        auth=AUTH,
    )
    if r.status_code != 200:
        print(f"predictions fetch: {r.status_code}")
        return []
    return r.json()

def get_recent_posts(client, limit=10):
    r = client.get(
        f"{WP_URL}/wp-json/wp/v2/posts",
        params={"per_page": limit, "orderby": "date", "order": "desc", "_fields": "id,title,content,slug"},
        auth=AUTH,
    )
    if r.status_code != 200:
        return []
    return r.json()

def add_unique_block(content: str, title: str) -> str:
    """Add unique analysis block if not present."""
    if "Ключевой фактор" in content or "key-factor" in content:
        return content
    block = f'''
<div class="seo-block">
<h3>Ключевой фактор матча</h3>
<p>В матче «{title}» важны текущая форма, мотивация в турнирной таблице и статистика личных встреч. Команды с сильной атакой дома чаще создают моменты, а гости играют на контратаках.</p>
<h3>Что учитывать при ставке</h3>
<ul>
<li>Составы и возможные ротации</li>
<li>Погодные условия и покрытие</li>
<li>Коэффициенты на тотал и обе забьют</li>
</ul>
</div>
'''
    return content + block

def add_related_links(content: str, related: list) -> str:
    """Add related predictions block."""
    if "Похожие прогнозы" in content or "related-preds" in content:
        return content
    if not related:
        return content
    links = "".join(f'<li><a href="{r["link"]}">{r["title"]}</a></li>' for r in related[:3])
    block = f'''
<div class="related-preds">
<h3>Похожие прогнозы</h3>
<ul>{links}</ul>
</div>
'''
    return content + block

def update_post(client, post_id: int, content: str, post_type: str = "prediction"):
    r = client.post(
        f"{WP_URL}/wp-json/wp/v2/{post_type}/{post_id}",
        json={"content": content},
        auth=AUTH,
        headers=HEADERS,
    )
    return r.status_code in (200, 201)

def main():
    with httpx.Client(timeout=60) as client:
        print("=== 1. Unique content in predictions ===")
        preds = get_recent_predictions(client, 12)
        print(f"Found {len(preds)} predictions")
        updated = 0
        for i, p in enumerate(preds):
            title = p.get("title", {}).get("rendered", "")
            content = p.get("content", {}).get("rendered", "")
            new_content = add_unique_block(content, title)
            # related: next 3
            related = [{"title": preds[(i+j) % len(preds)]["title"]["rendered"], "link": preds[(i+j) % len(preds)]["link"]} for j in range(1, 4)]
            new_content = add_related_links(new_content, related)
            if new_content != content:
                if update_post(client, p["id"], new_content, "prediction"):
                    print(f"  OK {p['id']} {title[:40]}")
                    updated += 1
                else:
                    print(f"  ERR {p['id']}")
            time.sleep(0.5)
        print(f"Updated predictions: {updated}")

        print("\n=== 2. Internal linking in posts ===")
        posts = get_recent_posts(client, 8)
        print(f"Found {len(posts)} posts")
        linked = 0
        for p in posts:
            content = p.get("content", {}).get("rendered", "")
            if "Похожие материалы" in content:
                continue
            # simple related block pointing to predictions archive
            block = '''
<div class="related-posts">
<h3>Похожие материалы</h3>
<ul>
<li><a href="https://beteasy.ru/prognozy/">Все прогнозы на спорт</a></li>
<li><a href="https://beteasy.ru/bukmekery/">Рейтинг букмекеров</a></li>
<li><a href="https://beteasy.ru/fribety/">Фрибеты за регистрацию</a></li>
</ul>
</div>
'''
            new_content = content + block
            if update_post(client, p["id"], new_content, "posts"):
                print(f"  OK post {p['id']}")
                linked += 1
            time.sleep(0.4)
        print(f"Linked posts: {linked}")

        print("\nDone")

if __name__ == "__main__":
    main()
