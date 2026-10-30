#!/usr/bin/env python3
"""Add match and stats links to all team pages."""

import os
import httpx
import re

WP_URL = os.environ.get("WP_URL", "https://beteasy.ru").rstrip("/")
AUTH = (os.environ.get("WP_USER", ""), os.environ.get("WP_APP_PASS", ""))

# Links by sport
LINKS = {
    "cs2": {
        "hltv": "https://www.hltv.org/team/{slug}",
        "liquipedia": "https://liquipedia.net/counterstrike/{slug}",
    },
    "dota2": {
        "liquipedia": "https://liquipedia.net/dota2/{slug}",
        "opendota": "https://www.opendota.com/teams/{slug}",
    },
    "football": {
        "flashscore": "https://www.flashscore.com/team/{slug}/",
        "sofascore": "https://www.sofascore.com/team/{slug}",
    },
}

def get_pages(client, parent_slug):
    r = client.get(WP_URL + "/wp-json/wp/v2/pages", params={"slug": parent_slug}, auth=AUTH)
    if not (r.status_code == 200 and r.json()):
        return []
    parent_id = r.json()[0]["id"]
    r = client.get(WP_URL + "/wp-json/wp/v2/pages", params={"parent": parent_id, "per_page": 50, "context": "edit"}, auth=AUTH)
    return r.json() if r.status_code == 200 else []

def add_links_block(content, sport, slug):
    """Insert links block before closing </div> of .tp"""
    links = LINKS.get(sport, {})
    if not links:
        return content
    
    links_html = '<div class="tp-box"><h3>Ссылки</h3><div class="tp-links-ext">'
    for name, url_tpl in links.items():
        url = url_tpl.replace("{slug}", slug)
        links_html += f'<a href="{url}" target="_blank" rel="nofollow">{name.upper()}</a>'
    links_html += '</div></div>'
    
    # Insert before the last </div> of .tp
    if '<div class="tp-links">' in content:
        content = content.replace('<div class="tp-links">', links_html + '\n<div class="tp-links">')
    return content

def update_page(client, page_id, content):
    r = client.post(WP_URL + f"/wp-json/wp/v2/pages/{page_id}", json={"content": content}, auth=AUTH)
    return r.status_code in (200, 201)

def main():
    sports = [
        ("cs2", "cs2"),
        ("dota2", "dota2"),
        ("football", "football"),
    ]
    
    with httpx.Client(timeout=120) as client:
        for parent_slug, sport in sports:
            pages = get_pages(client, parent_slug)
            print(f"=== {sport}: {len(pages)} pages ===")
            for page in pages:
                slug = page.get("slug", "")
                content = page.get("content", {}).get("raw", "")
                if not content or "tp-links-ext" in content:
                    continue
                new_content = add_links_block(content, sport, slug)
                if new_content != content:
                    if update_page(client, page["id"], new_content):
                        print(f"  {slug}: OK")
                    else:
                        print(f"  {slug}: ERR")

if __name__ == "__main__":
    main()
