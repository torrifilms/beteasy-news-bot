#!/usr/bin/env python3
"""Обновляет картинки у существующих постов ЛЧ на уникальные."""

import os
import re
import httpx

WP_URL = os.environ.get("WP_BASE_URL", "https://beteasy.ru").rstrip("/")
AUTH = (os.environ["WP_USERNAME"], os.environ["WP_APP_PASSWORD"])
HEADERS = {"User-Agent": "BeteasyBot/1.0"}

# Разные картинки для каждого поста
IMAGES = {
    "komo-razgromil": "https://images.unsplash.com/photo-1508098682722-e99c43a406b2?w=1200&h=800&fit=crop",
    "rays-spas-arsenal": "https://images.unsplash.com/photo-1522778119026-d647f0596c20?w=1200&h=800&fit=crop",
    "real-madrid-razgromil": "https://images.unsplash.com/photo-1517466787929-bc90951d0974?w=1200&h=800&fit=crop",
    "galatasaray-obygral": "https://images.unsplash.com/photo-1431324155629-1a6deb1dec8d?w=1200&h=800&fit=crop",
    "aston-villa": "https://images.unsplash.com/photo-1489944440615-453fc2b6a9a9?w=1200&h=800&fit=crop",
    "inter-obygral": "https://images.unsplash.com/photo-1522778526097-ce0a22ceb253?w=1200&h=800&fit=crop",
    "lask-sensatsionno": "https://images.unsplash.com/photo-1517927033932-b3d18e8100b0?w=1200&h=800&fit=crop",
    "bryugge-razgromil": "https://images.unsplash.com/photo-1560272564-c83b66b1ad12?w=1200&h=800&fit=crop",
    "betis-obygral": "https://images.unsplash.com/photo-1543326727-cf6c39e8f84c?w=1200&h=800&fit=crop",
    "itogi-tretego": "https://images.unsplash.com/photo-1579952363873-27f3bade9f55?w=1200&h=800&fit=crop",
}

def upload(client, url, name):
    try:
        img = client.get(url, timeout=15, follow_redirects=True, headers=HEADERS)
        if img.status_code != 200:
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
        # Получаем все посты
        r = client.get(f"{WP_URL}/wp-json/wp/v2/posts", params={"per_page": 50, "status": "publish"}, auth=AUTH)
        posts = r.json()
        updated = 0
        for post in posts:
            slug = post.get("slug", "")
            for key, img_url in IMAGES.items():
                if key in slug:
                    print(f"→ {slug[:50]}")
                    media_id = upload(client, img_url, slug[:30])
                    if media_id:
                        upd = client.post(
                            f"{WP_URL}/wp-json/wp/v2/posts/{post['id']}",
                            json={"featured_media": media_id},
                            auth=AUTH,
                        )
                        print(f"  media={media_id} status={upd.status_code}")
                        updated += 1
                    break
        print(f"\nОбновлено: {updated}")

if __name__ == "__main__":
    main()
