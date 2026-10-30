#!/usr/bin/env python3
"""Add match and stats links to all team pages."""

import os
import httpx

WP_URL = os.environ.get("WP_URL", "https://beteasy.ru").rstrip("/")
AUTH = (os.environ.get("WP_USER", ""), os.environ.get("WP_APP_PASS", ""))

LINKS = {
    "cs2": [
        ("HLTV", "https://www.hltv.org/team/{slug}"),
        ("Liquipedia", "https://liquipedia.net/counterstrike/{slug}"),
    ],
    "dota2": [
        ("Liquipedia", "https://liquipedia.net/dota2/{slug}"),
        ("OpenDota", "https://www.opendota.com/teams/{slug}"),
    ],
    "football": [
        ("Flashscore", "https://www.flashscore.com/team/{slug}/"),
        ("Sofascore", "https://www.sofascore.com/team/{slug}"),
    ],
}

CSS = '''.tp-links-ext{display:flex;gap:10px;flex-wrap:wrap}.tp-links-ext a{padding:8px 14px;background:#141827;border:1px solid rgba(214,255,59,.3);color:#D6FF3B;text-decoration:none;border-radius:6px;font-size:12px;font-weight:600;transition:all .2s}.tp-links-ext a:hover{background:rgba(214,255,59,.1)}'''

def get_pages(client, parent_slug):
    r = client.get(WP_URL + "/wp-json/wp/v2/pages", params={"slug": parent_slug}, auth=AUTH)
    if not (r.status_code == 200 and r.json()):
        return []
    parent_id = r.json()[0]["id"]
    r = client.get(WP_URL + "/wp-json/wp/v2/pages", params={"parent": parent_id, "per_page": 50, "context": "edit"}, auth=AUTH)
    return r.json() if r.status_code == 200 else []

def add_links(content, sport, slug):
    links = LINKS.get(sport, [])
    if not links or "tp-links-ext" in content:
        return content
    
    # Add CSS if not present
    if ".tp-links-ext" not in content:
        content = content.replace("</style>", CSS + "</style>")
    
    # Build links HTML
    links_html = '<div class="tp-box"><h3>Матчи и статистика</h3><div class="tp-links-ext">'
    for name, url_tpl in links:
        url = url_tpl.replace("{slug}", slug)
        links_html += f'<a href="{url}" target="_blank" rel="nofollow">{name}</a>'
    links_html += '</div></div>'
    
    # Insert before tp-links
    if '<div class="tp-links">' in content:
        content = content.replace('<div class="tp-links">', links_html + '\n<div class="tp-links">')
    return content

def update_page(client, page_id, content):
    r = client.post(WP_URL + f"/wp-json/wp/v2/pages/{page_id}", json={"content": content}, auth=AUTH)
    return r.status_code in (200, 201)

def main():
    sports = [("cs2", "cs2"), ("dota2", "dota2"), ("football", "football")]
    with httpx.Client(timeout=120) as client:
        for parent_slug, sport in sports:
            pages = get_pages(client, parent_slug)
            print(f"=== {sport}: {len(pages)} pages ===")
            for page in pages:
                slug = page.get("slug", "")
                content = page.get("content", {}).get("raw", "")
                if not content:
                    continue
                new_content = add_links(content, sport, slug)
                if new_content != content:
                    if update_page(client, page["id"], new_content):
                        print(f"  {slug}: OK")
                    else:
                        print(f"  {slug}: ERR")

if __name__ == "__main__":
    main()
