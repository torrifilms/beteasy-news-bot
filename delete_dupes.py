#!/usr/bin/env python3
"""Delete duplicate predictions, keep the newest in each group."""

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
                        "_fields": "id,title,date"},
                auth=AUTH,
            )
            if r.status_code != 200:
                break
            items = r.json()
            if not items:
                break
            all_preds.extend(items)
            if len(items) < 50:
                break
            page += 1

        print(f"Total: {len(all_preds)}")

        by_title = defaultdict(list)
        for p in all_preds:
            title = p.get("title", {}).get("rendered", "")
            key = normalize(title)
            by_title[key].append({
                "id": p["id"],
                "title": title,
                "date": p.get("date", ""),
            })

        deleted = 0
        for key, items in by_title.items():
            if len(items) <= 1:
                continue
            # sort by date desc, keep first (newest)
            items.sort(key=lambda x: x["date"], reverse=True)
            keep = items[0]
            to_delete = items[1:]
            print(f"\n[{len(items)}x] {key[:50]}")
            print(f"  KEEP id={keep['id']} {keep['date'][:10]}")
            for it in to_delete:
                r = client.delete(
                    f"{WP_URL}/wp-json/wp/v2/prediction/{it['id']}",
                    params={"force": "true"},
                    auth=AUTH,
                )
                if r.status_code in (200, 204):
                    print(f"  DEL  id={it['id']} {it['date'][:10]}")
                    deleted += 1
                else:
                    print(f"  ERR  id={it['id']} {r.status_code}")

        print(f"\nDeleted: {deleted}")

if __name__ == "__main__":
    main()
