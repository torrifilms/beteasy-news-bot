#!/usr/bin/env python3
"""Fix H2H with real El Clasico results."""

import os
import httpx
import re

WP_URL = os.environ.get("WP_URL", "https://beteasy.ru").rstrip("/")
AUTH = (os.environ.get("WP_USER", ""), os.environ.get("WP_APP_PASS", ""))

# Real results from search:
# 25.10.2026: Barcelona 1-2 Real Madrid (W)
# 10.05.2026: Barcelona 2-0 Real Madrid (L)
# 11.01.2026: Barcelona 3-2 Real Madrid (L) - Supercopa
# 26.10.2025: Real Madrid 2-1 Barcelona (W)
# 11.05.2025: Barcelona 4-3 Real Madrid (L)

REAL_H2H = '''<div class="tp-h2h-list">
<div class="tp-h2h-item"><span class="tp-h2h-date">25.10.2026</span><span class="tp-h2h-score">1-2</span><span class="tp-h2h-result tp-win">Победа</span></div>
<div class="tp-h2h-item"><span class="tp-h2h-date">10.05.2026</span><span class="tp-h2h-score">2-0</span><span class="tp-h2h-result tp-loss">Поражение</span></div>
<div class="tp-h2h-item"><span class="tp-h2h-date">11.01.2026</span><span class="tp-h2h-score">3-2</span><span class="tp-h2h-result tp-loss">Поражение</span></div>
<div class="tp-h2h-item"><span class="tp-h2h-date">26.10.2025</span><span class="tp-h2h-score">2-1</span><span class="tp-h2h-result tp-win">Победа</span></div>
<div class="tp-h2h-item"><span class="tp-h2h-date">11.05.2025</span><span class="tp-h2h-score">4-3</span><span class="tp-h2h-result tp-loss">Поражение</span></div>
</div>
<div class="tp-h2h-summary"><span>Последние 5: <b>2 победы, 3 поражения</b></span></div>'''

def main():
    with httpx.Client(timeout=60) as client:
        r = client.get(WP_URL + "/wp-json/wp/v2/pages", params={"slug": "team-real-madrid", "context": "edit"}, auth=AUTH)
        if r.status_code != 200 or not r.json():
            print("ERR: page not found")
            return
        
        page = r.json()[0]
        content = page.get("content", {}).get("raw", "")
        
        content = re.sub(
            r'<div class="tp-h2h-list">.*?</div>\s*<div class="tp-h2h-summary">.*?</div>',
            REAL_H2H,
            content,
            flags=re.DOTALL
        )
        
        r2 = client.post(WP_URL + "/wp-json/wp/v2/pages/" + str(page["id"]), 
                        json={"content": content}, auth=AUTH)
        print("OK" if r2.status_code in (200, 201) else "ERR")

if __name__ == "__main__":
    main()
