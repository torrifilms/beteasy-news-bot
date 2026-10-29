#!/usr/bin/env python3
"""Check existing team pages and their slugs."""

import os
import httpx

WP_URL = os.environ.get("WP_URL", "https://beteasy.ru").rstrip("/")
AUTH = (os.environ.get("WP_USER", ""), os.environ.get("WP_APP_PASS", ""))

def main():
    with httpx.Client(timeout=30) as client:
        # Get all pages with "team" in slug
        r = client.get(WP_URL + "/wp-json/wp/v2/pages", params={"search": "team", "per_page": 50, "_fields": "id,slug,parent,title"}, auth=AUTH)
        if r.status_code == 200:
            for p in r.json():
                slug = p.get("slug", "")
                parent = p.get("parent", 0)
                title = p.get("title", {}).get("rendered", "")
                print(f"ID:{p['id']} slug:{slug} parent:{parent} title:{title}")

if __name__ == "__main__":
    main()
