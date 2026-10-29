#!/usr/bin/env python3
"""Restyle team pages to match site dark theme."""

import os
import httpx
import re

WP_URL = os.environ.get("WP_URL", "https://beteasy.ru").rstrip("/")
AUTH = (os.environ.get("WP_USER", ""), os.environ.get("WP_APP_PASS", ""))

STYLE = '''
<style>
.team-page{max-width:900px;margin:40px auto;padding:0 20px}
.team-hero{display:flex;justify-content:space-between;align-items:flex-start;gap:30px;padding:32px;background:var(--panel);border:1px solid var(--line);border-radius:16px;margin-bottom:24px}
.team-hero h1{font-family:'Unbounded',sans-serif;font-size:32px;margin:0 0 12px;text-transform:uppercase;letter-spacing:.5px}
.team-hero .meta{color:var(--mut);font-size:14px;margin:6px 0}
.team-hero .titles{color:var(--lime);font-weight:600;margin-top:12px}
.fan-box{text-align:center;min-width:160px}
.btn-fan{background:var(--lime);color:#07080C;border:none;padding:14px 28px;border-radius:100px;font-weight:700;font-size:15px;cursor:pointer;transition:all .2s}
.btn-fan:hover{transform:scale(1.05);box-shadow:0 0 20px rgba(214,255,59,.4)}
.btn-fan.active{background:var(--violet);color:#fff}
.fan-count{margin-top:12px;font-size:13px;color:var(--mut)}
.fan-count span{font-family:'JetBrains Mono',monospace;font-size:22px;color:var(--lime);font-weight:700}
.team-section{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:24px;margin:16px 0}
.team-section h3{font-family:'Unbounded',sans-serif;font-size:16px;margin:0 0 16px;text-transform:uppercase;letter-spacing:.5px}
.form-row{display:flex;gap:8px}
.form-badge{width:36px;height:36px;display:flex;align-items:center;justify-content:center;border-radius:8px;font-weight:700;font-size:14px}
.stats-grid{display:grid;grid-template-columns:repeat(5,1fr);gap:12px}
.stat{text-align:center;background:var(--panel2);padding:16px 8px;border-radius:10px}
.stat b{display:block;font-family:'JetBrains Mono',monospace;font-size:24px;color:var(--lime)}
.stat span{font-size:11px;color:var(--mut);text-transform:uppercase;letter-spacing:.5px}
.squad-list{display:grid;grid-template-columns:repeat(2,1fr);gap:8px;list-style:none;padding:0;margin:0}
.squad-list li{background:var(--panel2);padding:12px 16px;border-radius:8px;font-size:14px}
.team-section a{color:var(--lime)}
.team-faq details{background:var(--panel2);border-radius:8px;margin:8px 0;padding:0}
.team-faq summary{padding:14px 16px;cursor:pointer;font-weight:600}
.team-faq details p{padding:0 16px 14px;color:var(--mut);margin:0}
@media(max-width:700px){
  .team-hero{flex-direction:column}
  .stats-grid{grid-template-columns:repeat(3,1fr)}
  .squad-list{grid-template-columns:1fr}
}
</style>
'''

JS = '''
<script>
(function(){
  var btn = document.querySelector(".btn-fan");
  if(!btn) return;
  var slug = btn.dataset.team;
  var countEl = document.getElementById("fans-" + slug);
  
  fetch("/wp-json/beteasy/v1/fan/" + slug)
    .then(function(r){return r.json()})
    .then(function(d){if(countEl && d.count !== undefined) countEl.textContent = d.count})
    .catch(function(){});
  
  if(localStorage.getItem("fan-"+slug)==="1"){
    btn.classList.add("active");
    btn.textContent = "❤️ Болею!";
  }
  
  btn.addEventListener("click", function(){
    var isActive = btn.classList.contains("active");
    var action = isActive ? "remove" : "add";
    fetch("/wp-json/beteasy/v1/fan/" + slug, {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({action: action})
    })
    .then(function(r){return r.json()})
    .then(function(d){
      if(countEl && d.count !== undefined) countEl.textContent = d.count;
      if(d.status === "ok"){
        if(action === "add"){
          btn.classList.add("active");
          btn.textContent = "❤️ Болею!";
          localStorage.setItem("fan-"+slug, "1");
        } else {
          btn.classList.remove("active");
          btn.textContent = "❤️ Болею";
          localStorage.setItem("fan-"+slug, "0");
        }
      } else if(d.status === "limited"){
        alert("Вы уже голосовали сегодня");
      }
    })
    .catch(function(){
      alert("Ошибка соединения");
    });
  });
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
            # Remove old style and script
            content = re.sub(r'<style>.*?</style>', '', content, flags=re.DOTALL)
            content = re.sub(r'<script>.*?</script>', '', content, flags=re.DOTALL)
            content = STYLE + content + JS
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
