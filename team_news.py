#!/usr/bin/env python3
"""Update team pages with news specifically about that team."""

import os
import httpx
import re

WP_URL = os.environ.get("WP_URL", "https://beteasy.ru").rstrip("/")
AUTH = (os.environ.get("WP_USER", ""), os.environ.get("WP_APP_PASS", ""))

TEAMS = {
    "team-real-madrid": ["Реал Мадрид", "Real Madrid", "Мбаппе", "Mbappe"],
    "team-barselona": ["Барселона", "Barcelona", "Ямаль", "Yamal"],
    "team-natus-vincere": ["NaVi", "Natus Vincere", "s1mple"],
    "team-team-spirit": ["Team Spirit", "Spirit", "Yatoro"],
}

def fetch_team_news(client, keywords):
    """Fetch posts matching team keywords."""
    for kw in keywords:
        r = client.get(WP_URL + "/wp-json/wp/v2/posts",
                      params={"search": kw, "per_page": 5, "_fields": "title,link,date"},
                      auth=AUTH)
        if r.status_code == 200 and r.json():
            return r.json()[:3]
    return []

def build_news_html(posts):
    if not posts:
        return '<p style="color:#79829B">Новостей пока нет</p>'
    html = ""
    for p in posts:
        title = p.get("title", {}).get("rendered", "")
        link = p.get("link", "")
        date = p.get("date", "")[:10]
        html += f'<a href="{link}"><span>{date}</span><b>{title}</b></a>\n'
    return html

def update_page(client, slug, news_html):
    r = client.get(WP_URL + "/wp-json/wp/v2/pages", params={"slug": slug}, auth=AUTH)
    if r.status_code != 200 or not r.json():
        return False
    
    page = r.json()[0]
    content = page.get("content", {}).get("raw") or page.get("content", {}).get("rendered", "")
    
    # Replace news section content
    content = re.sub(
        r'(<div class="tp-box tp-news">.*?<h3>Последние новости</h3>).*?(</div>\s*</div>)',
        r'\1\n' + news_html + r'\2',
        content,
        flags=re.DOTALL
    )
    
    r2 = client.post(WP_URL + "/wp-json/wp/v2/pages/" + str(page["id"]),
                    json={"content": content}, auth=AUTH)
    return r2.status_code in (200, 201)

def main():
    with httpx.Client(timeout=60) as client:
        for slug, keywords in TEAMS.items():
            posts = fetch_team_news(client, keywords)
            news_html = build_news_html(posts)
            ok = update_page(client, slug, news_html)
            print(f"{'OK' if ok else 'ERR'} {slug}: {len(posts)} news")

if __name__ == "__main__":
    main()
