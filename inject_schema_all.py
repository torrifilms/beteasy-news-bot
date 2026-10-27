#!/usr/bin/env python3
"""Add FAQ schema to ALL predictions."""

import os
import httpx
import json
import time

WP_URL = os.environ.get("WP_URL", "https://beteasy.ru").rstrip("/")
AUTH = (os.environ.get("WP_USER", ""), os.environ.get("WP_APP_PASS", ""))

FAQ = {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    "mainEntity": [
        {"@type": "Question", "name": "Где смотреть прогнозы на спорт?",
         "acceptedAnswer": {"@type": "Answer", "text": "Актуальные прогнозы публикуются в разделе Прогнозы на beteasy.ru."}},
        {"@type": "Question", "name": "Как выбрать букмекера?",
         "acceptedAnswer": {"@type": "Answer", "text": "Смотрите рейтинг лицензированных БК и условия фрибета в разделе Букмекеры."}},
        {"@type": "Question", "name": "Что такое фрибет?",
         "acceptedAnswer": {"@type": "Answer", "text": "Фрибет — бесплатная ставка за регистрацию. Выигрыш выводится после отыгрыша."}}
    ]
}
TAG = f'<script type="application/ld+json">{json.dumps(FAQ, ensure_ascii=False)}</script>'

def inject(client, pid):
    r = client.get(f"{WP_URL}/wp-json/wp/v2/prediction/{pid}", auth=AUTH)
    if r.status_code != 200:
        return False
    data = r.json()
    content = data.get("content", {}).get("raw") or data.get("content", {}).get("rendered", "")
    if "FAQPage" in content:
        return "skip"
    r = client.post(
        f"{WP_URL}/wp-json/wp/v2/prediction/{pid}",
        json={"content": content + "\n" + TAG},
        auth=AUTH,
    )
    return r.status_code in (200, 201)

def main():
    with httpx.Client(timeout=60) as client:
        page = 1
        total_ok = 0
        total_skip = 0
        total_err = 0
        while True:
            r = client.get(
                f"{WP_URL}/wp-json/wp/v2/prediction",
                params={"per_page": 50, "page": page, "orderby": "date", "order": "desc", "_fields": "id"},
                auth=AUTH,
            )
            if r.status_code != 200:
                print(f"page {page}: {r.status_code}")
                break
            items = r.json()
            if not items:
                break
            print(f"Page {page}: {len(items)} items")
            for item in items:
                pid = item["id"]
                res = inject(client, pid)
                if res is True:
                    total_ok += 1
                elif res == "skip":
                    total_skip += 1
                else:
                    total_err += 1
                time.sleep(0.15)
            # check if more pages
            if len(items) < 50:
                break
            page += 1
            if page > 20:  # safety
                break
        print(f"\nDone. Added: {total_ok} | Skipped: {total_skip} | Errors: {total_err}")

if __name__ == "__main__":
    main()
