#!/usr/bin/env python3
"""Add predictions block to team page."""

import os
import httpx

WP_URL = os.environ.get("WP_URL", "https://beteasy.ru").rstrip("/")
AUTH = (os.environ.get("WP_USER", ""), os.environ.get("WP_APP_PASS", ""))

PREDICTIONS_HTML = '''
<div class="tp-box tp-predictions">
<h3>Прогнозы на матчи</h3>
<div class="tp-pred-list">
<a href="https://beteasy.ru/prognozy/" class="tp-pred-item">
<span class="tp-pred-date">Все прогнозы</span>
<b>Смотреть прогнозы на матчи Реал Мадрид →</b>
</a>
</div>
<p class="tp-pred-note">Прогнозы обновляются автоматически перед каждым матчем</p>
</div>
'''

PREDICTIONS_CSS = '''
.tp-predictions{background:linear-gradient(145deg,#0E1016 0%,#1a1d2e 100%)}
.tp-pred-list{display:flex;flex-direction:column;gap:8px}
.tp-pred-item{display:flex;flex-direction:column;padding:14px 16px;background:rgba(20,24,39,.6);border:1px solid rgba(214,255,59,.15);border-radius:10px;text-decoration:none;transition:all .3s}
.tp-pred-item:hover{border-color:rgba(214,255,59,.4);background:rgba(20,24,39,.9);transform:translateX(4px)}
.tp-pred-date{font-size:11px;color:#79829B;text-transform:uppercase;letter-spacing:.5px}
.tp-pred-item b{color:#EDF0F7;font-size:14px;margin-top:4px}
.tp-pred-note{margin:12px 0 0;font-size:12px;color:#79829B;text-align:center}
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
        if ".tp-predictions" not in content:
            content = content.replace("</style>", PREDICTIONS_CSS + "</style>")
        
        # Add block before FAQ
        if "tp-predictions" not in content:
            faq_pos = content.find('<div class="tp-faq-wrap"')
            if faq_pos == -1:
                faq_pos = content.find('<div class="tp-box" itemscope')
            if faq_pos != -1:
                content = content[:faq_pos] + PREDICTIONS_HTML + "\n" + content[faq_pos:]
                print("Block inserted before FAQ")
            else:
                content = content + PREDICTIONS_HTML
                print("Block appended")
        else:
            print("Block already exists")
        
        r2 = client.post(WP_URL + "/wp-json/wp/v2/pages/" + str(page["id"]), 
                        json={"content": content}, auth=AUTH)
        print("OK" if r2.status_code in (200, 201) else "ERR")

if __name__ == "__main__":
    main()
