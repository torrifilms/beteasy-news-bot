#!/usr/bin/env python3
"""Обновляет картинки на релевантные по командам (Wikimedia поиск)."""

import os
import re
import httpx
import time

WP_URL = os.environ.get("WP_BASE_URL", "https://beteasy.ru").rstrip("/")
AUTH = (os.environ["WP_USERNAME"], os.environ["WP_APP_PASSWORD"])
HEADERS = {"User-Agent": "BeteasyBot/1.0 (news@beteasy.ru)"}

# Конкретные запросы для Wikimedia
QUERIES = {
    "komo-razgromil": "Como 1907 football",
    "rays-spas-arsenal": "Arsenal FC players",
    "real-madrid-razgromil": "Real Madrid CF Bernabeu",
    "galatasaray-obygral": "Galatasaray SK football",
    "aston-villa": "Aston Villa FC",
    "inter-obygral": "Inter Milan San Siro",
    "lask-sensatsionno": "Sporting CP Lisbon",
    "bryugge-razgromil": "Club Brugge",
    "betis-obygral": "Real Betis",
    "itogi-tretego": "UEFA Champions League trophy",
}

def search_wikimedia(query: str) -> str | None:
    try:
        resp = httpx.get(
            "https://commons.wikimedia.org/w/api.php",
            params={
                "action": "query",
                "format": "json",
                "generator": "search",
                "gsrsearch": f"{query} filetype:bitmap",
                "gsrlimit": 5,
                "prop": "imageinfo",
                "iiprop": "url|size",
                "iiurlwidth": 1200,
            },
            headers=HEADERS,
            timeout=12,
        )
        if resp.status_code == 200:
            pages = resp.json().get("query", {}).get("pages", {})
            for page in pages.values():
                info = page.get("imageinfo", [])
                if info:
                    url = info[0].get("thumburl") or info[0].get("url")
                    size = info[0].get("size", 0)
                    if url and url.startswith("http") and ".svg" not in url.lower() and size > 10000:
                        return url
    except Exception as e:
        print(f"  wiki err: {e}")
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
                    img_url = search_wikimedia(query)
                    if not img_url:
                        print("  no image found")
                        continue
                    print(f"  found: {img_url[:65]}")
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
