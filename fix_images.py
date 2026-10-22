#!/usr/bin/env python3
"""Обновляет картинки через Openverse (реальные фото команд)."""

import os
import httpx
import time

WP_URL = os.environ.get("WP_BASE_URL", "https://beteasy.ru").rstrip("/")
AUTH = (os.environ["WP_USERNAME"], os.environ["WP_APP_PASSWORD"])
HEADERS = {"User-Agent": "BeteasyBot/1.0 (news@beteasy.ru)"}

QUERIES = {
    "komo-razgromil": "Como 1907 football",
    "rays-spas-arsenal": "Arsenal FC",
    "real-madrid-razgromil": "Real Madrid football",
    "galatasaray-obygral": "Galatasaray football",
    "aston-villa": "Aston Villa football",
    "inter-obygral": "Inter Milan football",
    "lask-sensatsionno": "Sporting CP football",
    "bryugge-razgromil": "Club Brugge football",
    "betis-obygral": "Real Betis football",
    "itogi-tretego": "Champions League trophy",
}

def search_openverse(query: str) -> str | None:
    try:
        resp = httpx.get(
            "https://api.openverse.org/v1/images/",
            params={"q": query, "page_size": 5, "license_type": "commercial"},
            headers=HEADERS,
            timeout=15,
        )
        if resp.status_code == 200:
            for result in resp.json().get("results", []):
                url = result.get("url")
                if url and url.startswith("http"):
                    return url
    except Exception as e:
        print(f"  openverse err: {e}")
    return None

def upload(client, url, name):
    try:
        img = client.get(url, timeout=15, follow_redirects=True, headers=HEADERS)
        if img.status_code != 200 or len(img.content) < 5000:
            return None
        r = client.post(
            f"{WP_URL}/wp-json/wp/v2/media",
            content=img.content,
            headers={
                "Content-Disposition": f'attachment; filename="{name}.jpg"',
                "Content-Type": "image/jpeg",
            },
            auth=AUTH,
        )
        if r.status_code in (200, 201):
            return r.json().get("id")
    except Exception as e:
        print(f"  upload err: {e}")
    return None

def main():
    with httpx.Client(timeout=60) as client:
        r = client.get(f"{WP_URL}/wp-json/wp/v2/posts", params={"per_page": 50, "status": "publish"}, auth=AUTH)
        posts = r.json()
        updated = 0
        for post in posts:
            slug = post.get("slug", "")
            for key, query in QUERIES.items():
                if key in slug:
                    print(f"\n→ {slug[:45]}")
                    print(f"  query: {query}")
                    img_url = search_openverse(query)
                    if not img_url:
                        print("  no image")
                        continue
                    print(f"  found: {img_url[:70]}")
                    media_id = upload(client, img_url, slug[:30])
                    if media_id:
                        upd = client.post(
                            f"{WP_URL}/wp-json/wp/v2/posts/{post['id']}",
                            json={"featured_media": media_id},
                            auth=AUTH,
                        )
                        print(f"  media={media_id} status={upd.status_code}")
                        updated += 1
                    time.sleep(1)
                    break
        print(f"\nОбновлено: {updated}")

if __name__ == "__main__":
    main()
