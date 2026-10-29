#!/usr/bin/env python3
"""Migrate old team pages to new URL structure."""

import os
import httpx

WP_URL = os.environ.get("WP_URL", "https://beteasy.ru").rstrip("/")
AUTH = (os.environ.get("WP_USER", ""), os.environ.get("WP_APP_PASS", ""))

PARENT_ID = 1356

# Map old pages to new slugs
MIGRATIONS = [
    (1273, "real-madrid", "Реал Мадрид"),  # team-real-madrid
    (1274, "barcelona", "Барселона"),       # team-barselona
    (1275, "manchester-city", "Манчестер Сити"),  # team-manchester-siti
]

def main():
    with httpx.Client(timeout=60) as client:
        for page_id, new_slug, title in MIGRATIONS:
            r = client.post(WP_URL + "/wp-json/wp/v2/pages/" + str(page_id), json={
                "parent": PARENT_ID,
                "slug": new_slug
            }, auth=AUTH)
            print(f"{title}: {'OK' if r.status_code in (200, 201) else 'ERR'}")

if __name__ == "__main__":
    main()
