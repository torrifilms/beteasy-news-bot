#!/usr/bin/env python3
import os, httpx, json

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

def inject(client, pid, ptype):
    r = client.get(f"{WP_URL}/wp-json/wp/v2/{ptype}/{pid}", auth=AUTH)
    if r.status_code != 200:
        return False
    content = r.json().get("content", {}).get("raw") or r.json().get("content", {}).get("rendered", "")
    if "FAQPage" in content:
        return True
    r = client.post(f"{WP_URL}/wp-json/wp/v2/{ptype}/{pid}", json={"content": content + "\n" + TAG}, auth=AUTH)
    return r.status_code in (200, 201)

def main():
    with httpx.Client(timeout=40) as client:
        # List all pages
        r = client.get(f"{WP_URL}/wp-json/wp/v2/pages", params={"per_page": 50}, auth=AUTH)
        pages = r.json() if r.status_code == 200 else []
        print(f"Pages: {len(pages)}")
        for p in pages:
            slug = p.get("slug", "")
            if any(x in slug for x in ["prognoz", "bukmeker", "fribet", "liga", "apl", "rpl"]):
                print(f"  injecting page {p['id']} {slug}")
                inject(client, p["id"], "pages")

        # Recent predictions
        r = client.get(f"{WP_URL}/wp-json/wp/v2/prediction", params={"per_page": 20, "orderby": "date", "order": "desc"}, auth=AUTH)
        preds = r.json() if r.status_code == 200 else []
        print(f"Predictions: {len(preds)}")
        done = 0
        for p in preds[:15]:
            if inject(client, p["id"], "prediction"):
                done += 1
        print(f"Schema added to {done} predictions")

if __name__ == "__main__":
    main()
