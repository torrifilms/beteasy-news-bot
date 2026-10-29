#!/usr/bin/env python3
"""Add extended statistics block."""

import os
import httpx

WP_URL = os.environ.get("WP_URL", "https://beteasy.ru").rstrip("/")
AUTH = (os.environ.get("WP_USER", ""), os.environ.get("WP_APP_PASS", ""))

STATS_HTML = '''
<div class="tp-box tp-ext-stats">
<h3>Подробная статистика</h3>
<table class="tp-stats-table">
<tr><td>Матчей сыграно</td><td>10</td></tr>
<tr><td>Побед</td><td>8</td></tr>
<tr><td>Ничьих</td><td>0</td></tr>
<tr><td>Поражений</td><td>2</td></tr>
<tr><td>Голов забито</td><td>25</td></tr>
<tr><td>Голов пропущено</td><td>10</td></tr>
<tr><td>Разница мячей</td><td>+15</td></tr>
<tr><td>Очки</td><td>24</td></tr>
<tr><td>Место в таблице</td><td>3</td></tr>
<tr><td>Среднее голов за матч</td><td>2.5</td></tr>
</table>
</div>
'''

STATS_CSS = '''
.tp-ext-stats{background:#0E1016}
.tp-stats-table{width:100%;border-collapse:collapse}
.tp-stats-table tr{border-bottom:1px solid rgba(121,130,155,.15)}
.tp-stats-table tr:last-child{border-bottom:none}
.tp-stats-table td{padding:12px 8px;font-size:14px}
.tp-stats-table td:first-child{color:#79829B}
.tp-stats-table td:last-child{text-align:right;font-family:"JetBrains Mono",monospace;color:#D6FF3B;font-weight:600}
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
        if ".tp-ext-stats" not in content:
            content = content.replace("</style>", STATS_CSS + "</style>")
        
        # Add block after basic stats
        if "tp-ext-stats" not in content:
            # Find the basic stats section end
            stats_end = content.find('Пропущено</span></div>\n</div>\n</div>')
            if stats_end == -1:
                stats_end = content.find('Подробная статистика')
            if stats_end == -1:
                # Insert after form section
                form_end = content.find('</div>\n</div>\n\n<div class="tp-box">\n<h3>Статистика')
                if form_end != -1:
                    stats_end = content.find('</div>', form_end + 50)
            
            if stats_end != -1:
                insert_pos = content.find('</div>', stats_end) + 6
                content = content[:insert_pos] + "\n" + STATS_HTML + content[insert_pos:]
                print("Stats block inserted")
            else:
                # Insert before predictions or FAQ
                pred_pos = content.find('<div class="tp-box tp-predictions">')
                if pred_pos == -1:
                    pred_pos = content.find('<div class="tp-faq-wrap"')
                if pred_pos != -1:
                    content = content[:pred_pos] + STATS_HTML + "\n" + content[pred_pos:]
                    print("Stats block inserted before next section")
                else:
                    content = content + STATS_HTML
                    print("Stats block appended")
        else:
            print("Stats block already exists")
        
        r2 = client.post(WP_URL + "/wp-json/wp/v2/pages/" + str(page["id"]), 
                        json={"content": content}, auth=AUTH)
        print("OK" if r2.status_code in (200, 201) else "ERR")

if __name__ == "__main__":
    main()
