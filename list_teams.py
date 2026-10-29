#!/usr/bin/env python3
"""List existing team pages."""

import os
import httpx

WP_URL = os.environ.get("WP_URL", "https://beteasy.ru").rstrip("/")
AUTH = (os.environ.get("WP_USER", ""), os.environ.get("WP_APP_PASS", ""))

def main():
    with httpx.Client(timeout=30) as client:
        r = client.get(WP_URL + "/wp-json/wp/v2/pages", 
                      params={"search": "team-", "per_page": 50, "_fields": "slug,title"},
                      auth=AUTH)
        if r.status_code == 200:
            for p in r.json():
                slug = p.get("slug", "")
                if slug.startswith("team-"):
                    print(slug)

if __name__ == "__main__":
    main()
