#!/usr/bin/env python3
"""Update team pages to use admin-ajax for fan counter."""

import os
import httpx
import re

WP_URL = os.environ.get("WP_URL", "https://beteasy.ru").rstrip("/")
AUTH = (os.environ.get("WP_USER", ""), os.environ.get("WP_APP_PASS", ""))

NEW_JS = '''
<script>
(function(){
  var btn = document.querySelector(".btn-fan");
  if(!btn) return;
  var slug = btn.dataset.team;
  var countEl = document.getElementById("fans-" + slug);
  var ajaxUrl = "/wp-admin/admin-ajax.php";
  
  // Load count
  var fd = new FormData();
  fd.append("action", "beteasy_fan");
  fd.append("slug", slug);
  fd.append("do", "get");
  fetch(ajaxUrl, {method:"POST", body:fd})
    .then(function(r){return r.json()})
    .then(function(d){if(d.success && countEl) countEl.textContent = d.data.count})
    .catch(function(){});
  
  if(localStorage.getItem("fan-"+slug)==="1"){
    btn.classList.add("active");
    btn.textContent = "❤️ Болею!";
  }
  
  btn.addEventListener("click", function(e){
    e.preventDefault();
    var isActive = btn.classList.contains("active");
    var doAction = isActive ? "remove" : "add";
    var fd2 = new FormData();
    fd2.append("action", "beteasy_fan");
    fd2.append("slug", slug);
    fd2.append("do", doAction);
    fetch(ajaxUrl, {method:"POST", body:fd2})
      .then(function(r){return r.json()})
      .then(function(d){
        if(d.success){
          if(countEl) countEl.textContent = d.data.count;
          if(d.data.status === "ok"){
            if(doAction === "add"){
              btn.classList.add("active");
              btn.textContent = "❤️ Болею!";
              localStorage.setItem("fan-"+slug, "1");
            } else {
              btn.classList.remove("active");
              btn.textContent = "❤️ Болею";
              localStorage.setItem("fan-"+slug, "0");
            }
          } else if(d.data.status === "limited"){
            alert("Вы уже голосовали сегодня");
          }
        }
      })
      .catch(function(err){console.log(err)});
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
