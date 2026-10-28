#!/usr/bin/env python3
"""Check for duplicate predictions by title and teams."""

import os
import httpx
import re
from collections import defaultdict

WP_URL = os.environ.get("WP_URL", "https://beteasy.ru").rstrip("/")
AUTH = (os.environ.get("WP_USER", ""), os.environ.get("WP_APP_PASS", ""))

def normalize(title: str) -> str:
    t = title.lower()
    t = re.sub(r'[^\w\s\-]', '', t)
    t = re.sub(r'\s+', ' ', t).strip()
    # remove common suffixes
    for s in [': прогноз', ' прогноз', ' — прогноз']:
        t = t.replace(s, '')
    return t

def main():
    with httpx.Client(timeout=60) as client:
        all_preds = []
        page = 1
        while page <= 10:
            r = client.get(
                f"{WP_URL}/wp-json/wp/v2/prediction",
                params={"per_page": 50, "page": page, "orderby": "date", "order": "desc",
                        "_fields": "id,title,slug,date,link"},
                auth=AUTH,
            )
            if r.status_code != 200:
                print(f"page {page}: {r.status_code}")
                break
            items = r.json()
            if not items:
                break
            all_preds.extend(items)
            if len(items) < 50:
                break
            page += 1

        print(f"Total predictions: {len(all_preds)}")

        # Group by normalized title
        by_title = defaultdict(list)
        for p in all_preds:
            title = p.get("title", {}).get("rendered", "")
            key = normalize(title)
            by_title[key].append({
                "id": p["id"],
                "title": title,
                "slug": p.get("slug", ""),
                "date": p.get("date", "")[:10],
                "link": p.get("link", ""),
            })

        dupes = {k: v for k, v in by_title.items() if len(v) > 1}
        print(f"Duplicate groups: {len(dupes)}")
        print()
        for key, items in sorted(dupes.items(), key=lambda x: -len(x[1]))[:30]:
            print(f"[{len(items)}x] {key[:60]}")
            for it in items:
                print(f"  id={it['id']} {it['date']} {it['slug'][:40]}")
            print()

if __name__ == "__main__":
    main()
