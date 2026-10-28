#!/usr/bin/env python3
"""Add unique content blocks to more predictions."""

import os
import httpx
import time

WP_URL = os.environ.get("WP_URL", "https://beteasy.ru").rstrip("/")
AUTH = (os.environ.get("WP_USER", ""), os.environ.get("WP_APP_PASS", ""))

def add_blocks(content: str, title: str) -> str:
    if "Ключевой фактор" in content or "key-factor" in content:
        return content
    block = f'''
<div class="seo-block">
<h3>Ключевой фактор матча</h3>
<p>В матче «{title}» важны текущая форма команд, мотивация в турнирной таблице и статистика последних встреч. Домашняя команда чаще создаёт моменты, гости играют на контратаках.</p>
<h3>Статистика и форма</h3>
<p>Перед ставкой смотрите результаты последних 5 матчей, количество забитых и пропущенных голов, а также травмы ключевых игроков. Команды с высокой реализацией моментов чаще проходят тотал больше.</p>
<h3>Что учитывать при ставке</h3>
<ul>
<li>Составы и возможные ротации</li>
<li>Мотивация (борьба за чемпионство, еврокубки или выживание)</li>
<li>Коэффициенты на тотал и обе забьют</li>
<li>Погодные условия</li>
</ul>
</div>
'''
    return content + block

def main():
    with httpx.Client(timeout=60) as client:
        page = 1
        updated = 0
        skipped = 0
        while page <= 6:  # up to ~300 predictions
            r = client.get(
                f"{WP_URL}/wp-json/wp/v2/prediction",
                params={"per_page": 50, "page": page, "orderby": "date", "order": "desc", "_fields": "id,title,content"},
                auth=AUTH,
            )
            if r.status_code != 200:
                print(f"page {page}: {r.status_code}")
                break
            items = r.json()
            if not items:
                break
            print(f"Page {page}: {len(items)}")
            for item in items:
                title = item.get("title", {}).get("rendered", "")
                content = item.get("content", {}).get("rendered", "")
                if "Ключевой фактор" in content:
                    skipped += 1
                    continue
                new_content = add_blocks(content, title)
                r2 = client.post(
                    f"{WP_URL}/wp-json/wp/v2/prediction/{item['id']}",
                    json={"content": new_content},
                    auth=AUTH,
                )
                if r2.status_code in (200, 201):
                    updated += 1
                time.sleep(0.2)
            if len(items) < 50:
                break
            page += 1
        print(f"\nUpdated: {updated} | Already had blocks: {skipped}")

if __name__ == "__main__":
    main()
