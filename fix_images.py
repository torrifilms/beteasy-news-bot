#!/usr/bin/env python3
"""Ищет реальные фото команд в Wikimedia (namespace=6) и обновляет посты."""

import os
import httpx
import time

WP_URL = os.environ.get("WP_BASE_URL", "https://beteasy.ru").rstrip("/")
AUTH = (os.environ["WP_USERNAME"], os.environ["WP_APP_PASSWORD"])
HEADERS = {"User-Agent": "BeteasyBot/1.0 (news@beteasy.ru)"}

QUERIES = {
    "komo-razgromil": "Como 1907 football stadium",
    "rays-spas-arsenal": "Arsenal FC players",
    "real-madrid-razgromil": "Real Madrid Bernabeu",
    "galatasaray-obygral": "Galatasaray football",
    "aston-villa": "Aston Villa Park",
    "inter-obygral": "Inter Milan San Siro",
    "lask-sensatsionno": "Sporting CP Lisbon stadium",
    "bryugge-razgromil": "Club Brugge stadium",
    "betis-obygral": "Real Betis Sevilla",
    "itogi-tretego": "Champions League trophy",
}

def search_file(query: str) -> str | None:
    try:
        # 1. Найти файл
        r = httpx.get(
            "https://commons.wikimedia.org/w/api.php",
            params={
                "action": "query",
                "format": "json",
                "list": "search",
                "srsearch": query,
                "srnamespace": 6,
                "srlimit": 3,
            },
            headers=HEADERS,
            timeout=12,
        )
        if r.status_code != 200:
            return None
        titles = [x["title"] for x in r.json().get("query", {}).get("search", [])]
        if not titles:
            return None
        # 2. Получить URL
        r2 = httpx.get(
            "https://commons.wikimedia.org/w/api.php",
            params={
                "action": "query",
                "format": "json",
                "titles": titles[0],
                "prop": "imageinfo",
                "iiprop": "url",
                "iiurlwidth": 1200,
            },
            headers=HEADERS,
            timeout=12,
        )
        pages = r2.json().get("query", {}).get("pages", {})
        for page in pages.values():
            info = page.get("imageinfo", [])
            if info:
                return info[0].get("thumburl") or info[0].get("url")
    except Exception as e:
        print(f"  search err: {e}")
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
                    print(f"\n→ {slug[:40]}")
                    print(f"  query: {query}")
                    img_url = search_file(query)
                    if not img_url:
                        print("  not found")
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
                    time.sleep(1.5)
                    break
        print(f"\nОбновлено: {updated}")

if __name__ == "__main__":
    main()
