#!/usr/bin/env python3
"""Fix logos and remove duplicate breadcrumbs."""

import os
import httpx

WP_URL = os.environ.get("WP_URL", "https://beteasy.ru").rstrip("/")
AUTH = (os.environ.get("WP_USER", ""), os.environ.get("WP_APP_PASS", ""))

# Use clearbit or other CDN for logos
PAGE = '''<!-- wp:html -->
<style>
.teams-page{max-width:960px;margin:20px auto;padding:0 16px}
.teams-page h1{font-family:Unbounded,sans-serif;font-size:28px;margin:0 0 24px;text-transform:uppercase;color:#EDF0F7}
.teams-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:16px}
.team-card{display:flex;flex-direction:column;align-items:center;padding:20px;background:#0E1016;border:1px solid rgba(121,130,155,.2);border-radius:16px;text-decoration:none;transition:all .3s}
.team-card:hover{border-color:rgba(214,255,59,.4);transform:translateY(-4px)}
.team-card img{width:80px;height:80px;object-fit:contain;margin-bottom:12px;background:#fff;border-radius:8px;padding:8px}
.team-card span{font-family:Unbounded,sans-serif;font-size:13px;color:#EDF0F7;text-transform:uppercase;text-align:center}
.team-card small{font-size:11px;color:#79829B;margin-top:4px}
.section-title{font-family:Unbounded,sans-serif;font-size:16px;margin:32px 0 16px;text-transform:uppercase;color:#D6FF3B}
</style>

<div class="teams-page">
<h1>Команды</h1>

<div class="section-title">Футбол</div>
<div class="teams-grid">
<a href="/team/real-madrid/" class="team-card">
<img src="https://logo.clearbit.com/realmadrid.com" alt="Реал Мадрид">
<span>Реал Мадрид</span>
<small>Ла Лига</small>
</a>
<a href="/team/barcelona/" class="team-card">
<img src="https://logo.clearbit.com/fcbarcelona.com" alt="Барселона">
<span>Барселона</span>
<small>Ла Лига</small>
</a>
<a href="/team/manchester-city/" class="team-card">
<img src="https://logo.clearbit.com/mancity.com" alt="Манчестер Сити">
<span>Манчестер Сити</span>
<small>АПЛ</small>
</a>
<a href="/team/psg/" class="team-card">
<img src="https://logo.clearbit.com/psg.fr" alt="ПСЖ">
<span>ПСЖ</span>
<small>Лига 1</small>
</a>
<a href="/team/zenit/" class="team-card">
<img src="https://logo.clearbit.com/fc-zenit.ru" alt="Зенит">
<span>Зенит</span>
<small>РПЛ</small>
</a>
<a href="/team/spartak/" class="team-card">
<img src="https://logo.clearbit.com/spartak.com" alt="Спартак">
<span>Спартак</span>
<small>РПЛ</small>
</a>
</div>

<div class="section-title">CS2</div>
<div class="teams-grid">
<a href="/team/navi/" class="team-card">
<img src="https://logo.clearbit.com/navi.gg" alt="NaVi">
<span>Natus Vincere</span>
<small>CS2</small>
</a>
<a href="/team/faze/" class="team-card">
<img src="https://logo.clearbit.com/fazeclan.com" alt="FaZe Clan">
<span>FaZe Clan</span>
<small>CS2</small>
</a>
<a href="/team/g2/" class="team-card">
<img src="https://logo.clearbit.com/g2esports.com" alt="G2">
<span>G2 Esports</span>
<small>CS2</small>
</a>
<a href="/team/vitality/" class="team-card">
<img src="https://logo.clearbit.com/teamvitality.gg" alt="Vitality">
<span>Team Vitality</span>
<small>CS2</small>
</a>
<a href="/team/spirit-cs/" class="team-card">
<img src="https://logo.clearbit.com/teamspirit.gg" alt="Spirit">
<span>Team Spirit</span>
<small>CS2</small>
</a>
<a href="/team/mouz/" class="team-card">
<img src="https://logo.clearbit.com/mouz.gg" alt="MOUZ">
<span>MOUZ</span>
<small>CS2</small>
</a>
<a href="/team/liquid/" class="team-card">
<img src="https://logo.clearbit.com/teamliquid.com" alt="Liquid">
<span>Team Liquid</span>
<small>CS2</small>
</a>
<a href="/team/astralis/" class="team-card">
<img src="https://logo.clearbit.com/astralis.gg" alt="Astralis">
<span>Astralis</span>
<small>CS2</small>
</a>
<a href="/team/heroic/" class="team-card">
<img src="https://logo.clearbit.com/heroic.gg" alt="Heroic">
<span>Heroic</span>
<small>CS2</small>
</a>
<a href="/team/cloud9/" class="team-card">
<img src="https://logo.clearbit.com/cloud9.gg" alt="Cloud9">
<span>Cloud9</span>
<small>CS2</small>
</a>
</div>

<div class="section-title">Dota 2</div>
<div class="teams-grid">
<a href="/team/team-spirit/" class="team-card">
<img src="https://logo.clearbit.com/teamspirit.gg" alt="Team Spirit">
<span>Team Spirit</span>
<small>Dota 2</small>
</a>
</div>
</div>
<!-- /wp:html -->
'''

def main():
    with httpx.Client(timeout=60) as client:
        # Update parent page
        r = client.get(WP_URL + "/wp-json/wp/v2/pages", params={"slug": "team"}, auth=AUTH)
        if r.status_code == 200 and r.json():
            pid = r.json()[0]["id"]
            r2 = client.post(WP_URL + "/wp-json/wp/v2/pages/" + str(pid), json={"content": PAGE}, auth=AUTH)
            print(f"Parent: {'OK' if r2.status_code in (200, 201) else 'ERR'}")
        
        # Remove duplicate breadcrumbs from team pages
        parent_id = 1356
        teams = ["zenit", "spartak", "psg", "navi", "team-spirit", "faze"]
        
        for slug in teams:
            r = client.get(WP_URL + "/wp-json/wp/v2/pages", params={"slug": slug, "parent": parent_id, "context": "edit"}, auth=AUTH)
            if r.status_code == 200 and r.json():
                page = r.json()[0]
                content = page.get("content", {}).get("raw", "")
                
                # Remove my breadcrumb div
                import re
                content = re.sub(r'<div class="tp-bread">.*?</div>\n?', '', content, flags=re.DOTALL)
                
                r2 = client.post(WP_URL + "/wp-json/wp/v2/pages/" + str(page["id"]), json={"content": content}, auth=AUTH)
                print(f"{slug}: {'OK' if r2.status_code in (200, 201) else 'ERR'}")

if __name__ == "__main__":
    main()
