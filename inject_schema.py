#!/usr/bin/env python3
"""Inject FAQ schema into key pages via content."""

import os
import httpx
import json

WP_URL = os.environ.get("WP_URL", "https://beteasy.ru").rstrip("/")
AUTH = (os.environ.get("WP_USER", ""), os.environ.get("WP_APP_PASS", ""))

FAQ_JSON = {
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
            "acceptedAnswer": {"@type": "Answer", "text": "Смотрите рейтинг лицензированных букмекеров, размер бонуса и условия фрибета в разделе Букмекеры."}
        },
        {
            "@type": "Question",
            "name": "Что такое фрибет?",
            "acceptedAnswer": {"@type": "Answer", "text": "Фрибет — бесплатная ставка от букмекера за регистрацию. Выигрыш можно вывести после выполнения условий отыгрыша."}
        }
    ]
}

SCHEMA_TAG = f'<script type="application/ld+json">{json.dumps(FAQ_JSON, ensure_ascii=False)}</script>'

def inject(client, post_id, post_type="pages"):
    r = client.get(f"{WP_URL}/wp-json/wp/v2/{post_type}/{post_id}", auth=AUTH)
    if r.status_code != 200:
        print(f"  get {post_id}: {r.status_code}")
        return False
    data = r.json()
    content = data.get("content", {}).get("raw", data.get("content", {}).get("rendered", ""))
    if "FAQPage" in content:
        print(f"  {post_id}: already has schema")
        return True
    new_content = content + "\n" + SCHEMA_TAG
    r = client.post(
        f"{WP_URL}/wp-json/wp/v2/{post_type}/{post_id}",
        json={"content": new_content},
        auth=AUTH,
    )
    ok = r.status_code in (200, 201)
    print(f"  {post_id}: {'OK' if ok else r.status_code}")
    return ok

def main():
    with httpx.Client(timeout=30) as client:
        # Find pages by slug
        targets = ["prognozy", "bukmekery", "fribety"]
        for slug in targets:
            r = client.get(f"{WP_URL}/wp-json/wp/v2/pages", params={"slug": slug}, auth=AUTH)
            if r.status_code == 200 and r.json():
                pid = r.json()[0]["id"]
                print(f"Page {slug} id={pid}")
                inject(client, pid, "pages")
            else:
                # try posts
                r = client.get(f"{WP_URL}/wp-json/wp/v2/posts", params={"slug": slug}, auth=AUTH)
                if r.status_code == 200 and r.json():
                    pid = r.json()[0]["id"]
                    print(f"Post {slug} id={pid}")
                    inject(client, pid, "posts")
                else:
                    print(f"{slug}: not found")

        # Also inject into a recent prediction for testing
        r = client.get(f"{WP_URL}/wp-json/wp/v2/prediction", params={"per_page": 1}, auth=AUTH)
        if r.status_code == 200 and r.json():
            pid = r.json()[0]["id"]
            print(f"Sample prediction {pid}")
            inject(client, pid, "prediction")

if __name__ == "__main__":
    main()
