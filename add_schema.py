#!/usr/bin/env python3
"""Add FAQ schema to key pages via Rank Math or content."""

import os
import httpx
import json

WP_URL = os.environ.get("WP_URL", "https://beteasy.ru").rstrip("/")
AUTH = (os.environ.get("WP_USER", ""), os.environ.get("WP_APP_PASS", ""))

FAQ_SCHEMA = {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    "mainEntity": [
        {
            "@type": "Question",
            "name": "Где смотреть прогнозы на спорт?",
            "acceptedAnswer": {"@type": "Answer", "text": "Актуальные прогнозы на футбол, киберспорт и другие виды спорта публикуются в разделе Прогнозы на сайте beteasy.ru."}
        },
        {
            "@type": "Question",
            "name": "Как выбрать букмекера?",
            "acceptedAnswer": {"@type": "Answer", "text": "Смотрите рейтинг лицензированных букмекеров, размер бонуса и условия фрибета. Все обзоры есть в разделе Букмекеры."}
        },
        {
            "@type": "Question",
            "name": "Что такое фрибет?",
            "acceptedAnswer": {"@type": "Answer", "text": "Фрибет — бесплатная ставка от букмекера за регистрацию. Выигрыш можно вывести после выполнения условий отыгрыша."}
        }
    ]
}

def main():
    with httpx.Client(timeout=30) as client:
        # Try to update a page with schema in content (fallback)
        # First find pages
        r = client.get(f"{WP_URL}/wp-json/wp/v2/pages", params={"per_page": 10, "search": "прогноз"}, auth=AUTH)
        print(f"pages search: {r.status_code}")
        if r.status_code == 200:
            for p in r.json()[:3]:
                print(f"  page {p['id']}: {p['title']['rendered'][:40]}")

        # Add schema script to homepage via options or just note
        # For Rank Math, schema is usually managed in plugin settings
        print("\nSchema FAQ prepared. To enable:")
        print("1. In Rank Math → Schema → add FAQ schema to key pages")
        print("2. Or inject via theme functions.php")
        print(json.dumps(FAQ_SCHEMA, ensure_ascii=False, indent=2)[:400])

if __name__ == "__main__":
    main()
