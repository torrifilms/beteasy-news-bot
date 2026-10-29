#!/usr/bin/env python3
"""Find predictions about Real Madrid."""

import os
import httpx

WP_URL = os.environ.get("WP_URL", "https://beteasy.ru").rstrip("/")
AUTH = (os.environ.get("WP_USER", ""), os.environ.get("WP_APP_PASS", ""))

def main():
    with httpx.Client(timeout=30) as client:
        # Search for predictions with Real Madrid
        for kw in ["Реал Мадрид", "Real Madrid", "Мбаппе"]:
            r = client.get(WP_URL + "/wp-json/wp/v2/prediction",
                          params={"search": kw, "per_page": 5, "_fields": "id,title,link,meta"},
                          auth=AUTH)
            if r.status_code == 200 and r.json():
                print(f"=== {kw} ===")
                for p in r.json()[:5]:
                    title = p.get("title", {}).get("rendered", "")[:60]
                    link = p.get("link", "")
                    print(f"{title}")
                    print(f"  {link}")
                print()
                break

if __name__ == "__main__":
    main()
