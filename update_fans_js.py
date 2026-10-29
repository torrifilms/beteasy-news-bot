#!/usr/bin/env python3
"""Update team pages to use server-side fan counter."""

import os
import httpx
import re

WP_URL = os.environ.get("WP_URL", "https://beteasy.ru").rstrip("/")
AUTH = (os.environ.get("WP_USER", ""), os.environ.get("WP_APP_PASS", ""))

NEW_JS = '''
<script>
(function() {
    var slug = document.querySelector(".btn-fan")?.dataset.team;
    if (!slug) return;
    var countEl = document.getElementById("fans-" + slug);
    var btn = document.querySelector(".btn-fan");
    
    // Load current count
    fetch("/wp-json/beteasy/v1/fan/" + slug)
        .then(r => r.json())
        .then(d => { if (countEl) countEl.textContent = d.count || 0; })
        .catch(() => {});
    
    // Check local state
    if (localStorage.getItem("fan-" + slug) === "1" && btn) {
        btn.classList.add("active");
        btn.textContent = "❤️ Болею!";
    }
    
    window.toggleFan = function(el) {
        var team = el.dataset.team;
        var isActive = el.classList.contains("active");
        var action = isActive ? "remove" : "add";
        
        fetch("/wp-json/beteasy/v1/fan/" + team, {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({action: action})
        })
        .then(r => r.json())
        .then(d => {
            if (countEl) countEl.textContent = d.count || 0;
            if (d.status === "ok" || d.status === "already") {
                if (action === "add") {
                    el.classList.add("active");
                    el.textContent = "❤️ Болею!";
                    localStorage.setItem("fan-" + team, "1");
                } else {
                    el.classList.remove("active");
                    el.textContent = "❤️ Болею";
                    localStorage.setItem("fan-" + team, "0");
                }
            }
        })
        .catch(() => {
            // Fallback to local
            var c = parseInt(countEl.textContent) || 0;
            if (isActive) {
                el.classList.remove("active");
                el.textContent = "❤️ Болею";
                countEl.textContent = Math.max(0, c - 1);
                localStorage.setItem("fan-" + team, "0");
            } else {
                el.classList.add("active");
                el.textContent = "❤️ Болею!";
                countEl.textContent = c + 1;
                localStorage.setItem("fan-" + team, "1");
            }
        });
    };
})();
</script>
'''

def main():
    with httpx.Client(timeout=60) as client:
        slugs = ["team-real-madrid", "team-barselona", "team-manchester-siti", 
                 "team-zenit", "team-natus-vincere", "team-team-spirit"]
        updated = 0
        for slug in slugs:
            r = client.get(f"{WP_URL}/wp-json/wp/v2/pages", params={"slug": slug}, auth=AUTH)
            if r.status_code != 200 or not r.json():
                continue
            page = r.json()[0]
            content = page.get("content", {}).get("raw") or page.get("content", {}).get("rendered", "")
            # Remove old script
            content = re.sub(r'<script>.*?</script>', '', content, flags=re.DOTALL)
            content = content + NEW_JS
            r2 = client.post(
                f"{WP_URL}/wp-json/wp/v2/pages/{page['id']}",
                json={"content": content},
                auth=AUTH,
            )
            if r2.status_code in (200, 201):
                print(f"OK {slug}")
                updated += 1
        print(f"Updated: {updated}")

if __name__ == "__main__":
    main()
