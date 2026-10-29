#!/usr/bin/env python3
"""Add team logo to hero section."""

import os
import httpx
import re

WP_URL = os.environ.get("WP_URL", "https://beteasy.ru").rstrip("/")
AUTH = (os.environ.get("WP_USER", ""), os.environ.get("WP_APP_PASS", ""))

# Official Real Madrid logo from Wikipedia
LOGO_URL = "https://upload.wikimedia.org/wikipedia/en/5/56/Real_Madrid_CF.svg"

LOGO_CSS = '''
.tp-logo{width:80px;height:80px;object-fit:contain;margin-right:16px}
.tp-hero-left{display:flex;align-items:center}
'''

def main():
    with httpx.Client(timeout=60) as client:
        r = client.get(WP_URL + "/wp-json/wp/v2/pages", params={"slug": "team-real-madrid", "context": "edit"}, auth=AUTH)
        if r.status_code != 200 or not r.json():
            print("ERR: page not found")
            return
        
        page = r.json()[0]
        content = page.get("content", {}).get("raw", "")
        
        # Add CSS
        if ".tp-logo" not in content:
            content = content.replace("</style>", LOGO_CSS + "</style>")
        
        # Add logo to hero
        if 'class="tp-logo"' not in content:
            # Wrap hero content and add logo
            content = content.replace(
                '<div class="tp-hero">\n<div>',
                '<div class="tp-hero">\n<div class="tp-hero-left">\n<img src="' + LOGO_URL + '" alt="Real Madrid" class="tp-logo">\n<div>'
            )
            # Close the extra div
            content = content.replace(
                '</div>\n<div class="tp-fan">',
                '</div>\n</div>\n<div class="tp-fan">'
            )
            print("Logo added")
        else:
            print("Logo already exists")
        
        r2 = client.post(WP_URL + "/wp-json/wp/v2/pages/" + str(page["id"]), 
                        json={"content": content}, auth=AUTH)
        print("OK" if r2.status_code in (200, 201) else "ERR")

if __name__ == "__main__":
    main()
