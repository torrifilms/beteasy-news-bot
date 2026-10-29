#!/usr/bin/env python3
"""Add breadcrumbs to team pages."""

import os
import httpx

WP_URL = os.environ.get("WP_URL", "https://beteasy.ru").rstrip("/")
AUTH = (os.environ.get("WP_USER", ""), os.environ.get("WP_APP_PASS", ""))

PARENT_ID = 1356

BREADCRUMB_CSS = '''
.tp-bread{display:flex;align-items:center;gap:8px;margin-bottom:16px;font-size:13px}
.tp-bread a{color:#79829B;text-decoration:none}
.tp-bread a:hover{color:#D6FF3B}
.tp-bread span{color:#79829B}
.tp-bread .current{color:#EDF0F7}
'''

def add_breadcrumbs(content, team_name):
    """Add breadcrumbs to page content."""
    breadcrumb = f'''<div class="tp-bread">
<a href="/">Главная</a>
<span>→</span>
<a href="/team/">Команды</a>
<span>→</span>
<span class="current">{team_name}</span>
</div>'''
    
    # Add CSS
    if ".tp-bread" not in content:
        content = content.replace("</style>", BREADCRUMB_CSS + "</style>")
    
    # Add breadcrumb after <div class="tp">
    if 'class="tp-bread"' not in content:
        content = content.replace('<div class="tp">', '<div class="tp">\n' + breadcrumb)
    
    return content

def main():
    teams = [
        ("zenit", "Зенит"),
        ("spartak", "Спартак"),
        ("psg", "ПСЖ"),
        ("navi", "Natus Vincere"),
        ("team-spirit", "Team Spirit"),
        ("faze", "FaZe Clan"),
    ]
    
    with httpx.Client(timeout=60) as client:
        for slug, name in teams:
            r = client.get(WP_URL + "/wp-json/wp/v2/pages", params={"slug": slug, "parent": PARENT_ID, "context": "edit"}, auth=AUTH)
            if r.status_code == 200 and r.json():
                page = r.json()[0]
                content = page.get("content", {}).get("raw", "")
                new_content = add_breadcrumbs(content, name)
                
                r2 = client.post(WP_URL + "/wp-json/wp/v2/pages/" + str(page["id"]), json={"content": new_content}, auth=AUTH)
                print(f"{name}: {'OK' if r2.status_code in (200, 201) else 'ERR'}")
            else:
                print(f"{name}: not found")

if __name__ == "__main__":
    main()
