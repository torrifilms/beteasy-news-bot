#!/usr/bin/env python3
"""Add head-to-head history block."""

import os
import httpx

WP_URL = os.environ.get("WP_URL", "https://beteasy.ru").rstrip("/")
AUTH = (os.environ.get("WP_USER", ""), os.environ.get("WP_APP_PASS", ""))

H2H_HTML = '''
<div class="tp-box tp-h2h">
<h3>История встреч с Барселоной</h3>
<div class="tp-h2h-list">
<div class="tp-h2h-item">
<span class="tp-h2h-date">25.10.2026</span>
<span class="tp-h2h-score">1-2</span>
<span class="tp-h2h-result tp-win">Победа</span>
</div>
<div class="tp-h2h-item">
<span class="tp-h2h-date">10.05.2026</span>
<span class="tp-h2h-score">0-2</span>
<span class="tp-h2h-result tp-loss">Поражение</span>
</div>
<div class="tp-h2h-item">
<span class="tp-h2h-date">26.10.2025</span>
<span class="tp-h2h-score">2-1</span>
<span class="tp-h2h-result tp-win">Победа</span>
</div>
<div class="tp-h2h-item">
<span class="tp-h2h-date">21.04.2025</span>
<span class="tp-h2h-score">3-2</span>
<span class="tp-h2h-result tp-win">Победа</span>
</div>
<div class="tp-h2h-item">
<span class="tp-h2h-date">28.10.2024</span>
<span class="tp-h2h-score">0-4</span>
<span class="tp-h2h-result tp-loss">Поражение</span>
</div>
</div>
<div class="tp-h2h-summary">
<span>Последние 5: <b>3 победы, 2 поражения</b></span>
</div>
</div>
'''

H2H_CSS = '''
.tp-h2h{background:linear-gradient(145deg,#0E1016 0%,#141827 100%)}
.tp-h2h-list{display:flex;flex-direction:column;gap:6px}
.tp-h2h-item{display:flex;align-items:center;justify-content:space-between;padding:10px 14px;background:rgba(20,24,39,.5);border-radius:8px}
.tp-h2h-date{font-size:12px;color:#79829B;min-width:90px}
.tp-h2h-score{font-family:"JetBrains Mono",monospace;font-size:16px;color:#EDF0F7;font-weight:600}
.tp-h2h-result{font-size:11px;padding:4px 10px;border-radius:100px;font-weight:600;text-transform:uppercase}
.tp-win{background:rgba(39,174,96,.2);color:#27ae60}
.tp-loss{background:rgba(231,76,60,.2);color:#e74c3c}
.tp-draw{background:rgba(243,156,18,.2);color:#f39c12}
.tp-h2h-summary{margin-top:14px;padding-top:14px;border-top:1px solid rgba(121,130,155,.15);text-align:center;font-size:13px;color:#79829B}
.tp-h2h-summary b{color:#D6FF3B}
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
        if ".tp-h2h" not in content:
            content = content.replace("</style>", H2H_CSS + "</style>")
        
        # Add block before FAQ
        if "tp-h2h-list" not in content:
            faq_pos = content.find('<div class="tp-faq-wrap"')
            if faq_pos == -1:
                faq_pos = content.find('FAQPage')
            if faq_pos != -1:
                # Find the div start
                div_start = content.rfind('<div', 0, faq_pos)
                if div_start != -1:
                    content = content[:div_start] + H2H_HTML + "\n" + content[div_start:]
                    print("H2H block inserted before FAQ")
                else:
                    content = content[:faq_pos] + H2H_HTML + "\n" + content[faq_pos:]
                    print("H2H block inserted")
            else:
                content = content + H2H_HTML
                print("H2H block appended")
        else:
            print("H2H block already exists")
        
        r2 = client.post(WP_URL + "/wp-json/wp/v2/pages/" + str(page["id"]), 
                        json={"content": content}, auth=AUTH)
        print("OK" if r2.status_code in (200, 201) else "ERR")

if __name__ == "__main__":
    main()
