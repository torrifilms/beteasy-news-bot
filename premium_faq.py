#!/usr/bin/env python3
"""Make FAQ visually premium."""

import os
import httpx
import re

WP_URL = os.environ.get("WP_URL", "https://beteasy.ru").rstrip("/")
AUTH = (os.environ.get("WP_USER", ""), os.environ.get("WP_APP_PASS", ""))

PREMIUM_CSS = '''
.tp-faq-wrap{background:linear-gradient(145deg,#0E1016 0%,#141827 100%);border:1px solid rgba(214,255,59,.15);border-radius:16px;padding:24px;margin:16px 0}
.tp-faq-wrap h3{font-family:Unbounded,sans-serif;font-size:16px;margin:0 0 20px;text-transform:uppercase;color:#EDF0F7;letter-spacing:1px}
.tp-faq{margin:0 0 12px;padding:16px 20px;background:rgba(20,24,39,.6);border:1px solid rgba(121,130,155,.15);border-radius:12px;transition:all .3s ease}
.tp-faq:hover{border-color:rgba(214,255,59,.3);background:rgba(20,24,39,.9);transform:translateX(4px)}
.tp-faq b{display:flex;align-items:center;gap:12px;color:#EDF0F7;font-size:15px;font-weight:600;cursor:pointer}
.tp-faq b::before{content:"→";color:#D6FF3B;font-size:18px;transition:transform .3s}
.tp-faq:hover b::before{transform:translateX(4px)}
.tp-faq p{margin:10px 0 0 30px;color:#9AA3B8;font-size:14px;line-height:1.7}
'''

def main():
    with httpx.Client(timeout=60) as client:
        r = client.get(WP_URL + "/wp-json/wp/v2/pages", params={"slug": "team-real-madrid", "context": "edit"}, auth=AUTH)
        if r.status_code != 200 or not r.json():
            print("ERR: page not found")
            return
        
        page = r.json()[0]
        content = page.get("content", {}).get("raw", "")
        
        # Replace old FAQ CSS with premium
        content = re.sub(
            r'\.tp-faq\{[^}]+\}',
            '',
            content
        )
        content = re.sub(
            r'\.tp-faq b\{[^}]+\}',
            '',
            content
        )
        content = re.sub(
            r'\.tp-faq p\{[^}]+\}',
            '',
            content
        )
        
        # Add premium CSS
        if ".tp-faq-wrap" not in content:
            content = content.replace("</style>", PREMIUM_CSS + "</style>")
        
        # Wrap FAQ in premium container
        content = content.replace(
            '<div class="tp-box" itemscope itemtype="https://schema.org/FAQPage">',
            '<div class="tp-faq-wrap" itemscope itemtype="https://schema.org/FAQPage">'
        )
        
        r2 = client.post(WP_URL + "/wp-json/wp/v2/pages/" + str(page["id"]), 
                        json={"content": content}, auth=AUTH)
        print("OK" if r2.status_code in (200, 201) else "ERR")

if __name__ == "__main__":
    main()
