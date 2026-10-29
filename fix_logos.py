#!/usr/bin/env python3
"""Fix logos and add CS2 teams."""

import os
import httpx

WP_URL = os.environ.get("WP_URL", "https://beteasy.ru").rstrip("/")
AUTH = (os.environ.get("WP_USER", ""), os.environ.get("WP_APP_PASS", ""))

PAGE = '''<!-- wp:html -->
<style>
.teams-page{max-width:960px;margin:20px auto;padding:0 16px}
.teams-page h1{font-family:Unbounded,sans-serif;font-size:28px;margin:0 0 24px;text-transform:uppercase;color:#EDF0F7}
.teams-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:16px}
.team-card{display:flex;flex-direction:column;align-items:center;padding:20px;background:#0E1016;border:1px solid rgba(121,130,155,.2);border-radius:16px;text-decoration:none;transition:all .3s}
.team-card:hover{border-color:rgba(214,255,59,.4);transform:translateY(-4px)}
.team-card img{width:80px;height:80px;object-fit:contain;margin-bottom:12px}
.team-card span{font-family:Unbounded,sans-serif;font-size:13px;color:#EDF0F7;text-transform:uppercase;text-align:center}
.team-card small{font-size:11px;color:#79829B;margin-top:4px}
.section-title{font-family:Unbounded,sans-serif;font-size:16px;margin:32px 0 16px;text-transform:uppercase;color:#D6FF3B}
</style>

<div class="teams-page">
<h1>Команды</h1>

<div class="section-title">Футбол</div>
<div class="teams-grid">
<a href="/team/real-madrid/" class="team-card">
<img src="https://upload.wikimedia.org/wikipedia/en/thumb/5/56/Real_Madrid_CF.svg/200px-Real_Madrid_CF.svg.png" alt="Реал Мадрид">
<span>Реал Мадрид</span>
<small>Ла Лига</small>
</a>
<a href="/team/barcelona/" class="team-card">
<img src="https://upload.wikimedia.org/wikipedia/en/thumb/4/47/FC_Barcelona_%28crest%29.svg/200px-FC_Barcelona_%28crest%29.svg.png" alt="Барселона">
<span>Барселона</span>
<small>Ла Лига</small>
</a>
<a href="/team/manchester-city/" class="team-card">
<img src="https://upload.wikimedia.org/wikipedia/en/thumb/e/eb/Manchester_City_FC_badge.svg/200px-Manchester_City_FC_badge.svg.png" alt="Манчестер Сити">
<span>Манчестер Сити</span>
<small>АПЛ</small>
</a>
<a href="/team/psg/" class="team-card">
<img src="https://upload.wikimedia.org/wikipedia/en/thumb/a/a7/Paris_Saint-Germain_F.C..svg/200px-Paris_Saint-Germain_F.C..svg.png" alt="ПСЖ">
<span>ПСЖ</span>
<small>Лига 1</small>
</a>
<a href="/team/zenit/" class="team-card">
<img src="https://upload.wikimedia.org/wikipedia/commons/thumb/8/8a/FC_Zenit_Saint_Petersburg_logo.svg/200px-FC_Zenit_Saint_Petersburg_logo.svg.png" alt="Зенит">
<span>Зенит</span>
<small>РПЛ</small>
</a>
<a href="/team/spartak/" class="team-card">
<img src="https://upload.wikimedia.org/wikipedia/commons/thumb/9/9a/FC_Spartak_Moscow_logo.svg/200px-FC_Spartak_Moscow_logo.svg.png" alt="Спартак">
<span>Спартак</span>
<small>РПЛ</small>
</a>
</div>

<div class="section-title">CS2</div>
<div class="teams-grid">
<a href="/team/navi/" class="team-card">
<img src="https://upload.wikimedia.org/wikipedia/commons/thumb/8/8a/Natus_Vincere_logo.svg/200px-Natus_Vincere_logo.svg.png" alt="NaVi">
<span>Natus Vincere</span>
<small>CS2</small>
</a>
<a href="/team/faze/" class="team-card">
<img src="https://upload.wikimedia.org/wikipedia/commons/thumb/4/4d/FaZe_Clan_logo.svg/200px-FaZe_Clan_logo.svg.png" alt="FaZe Clan">
<span>FaZe Clan</span>
<small>CS2</small>
</a>
<a href="/team/g2/" class="team-card">
<img src="https://upload.wikimedia.org/wikipedia/commons/thumb/6/6a/G2_Esports_logo.svg/200px-G2_Esports_logo.svg.png" alt="G2">
<span>G2 Esports</span>
<small>CS2</small>
</a>
<a href="/team/vitality/" class="team-card">
<img src="https://upload.wikimedia.org/wikipedia/commons/thumb/4/43/Team_Vitality_logo.svg/200px-Team_Vitality_logo.svg.png" alt="Vitality">
<span>Team Vitality</span>
<small>CS2</small>
</a>
<a href="/team/spirit-cs/" class="team-card">
<img src="https://upload.wikimedia.org/wikipedia/commons/thumb/8/8e/Team_Spirit_logo.svg/200px-Team_Spirit_logo.svg.png" alt="Spirit">
<span>Team Spirit</span>
<small>CS2</small>
</a>
<a href="/team/mouz/" class="team-card">
<img src="https://upload.wikimedia.org/wikipedia/commons/thumb/9/9a/MOUZ_logo.svg/200px-MOUZ_logo.svg.png" alt="MOUZ">
<span>MOUZ</span>
<small>CS2</small>
</a>
<a href="/team/liquid/" class="team-card">
<img src="https://upload.wikimedia.org/wikipedia/commons/thumb/f/f1/Team_Liquid_logo.svg/200px-Team_Liquid_logo.svg.png" alt="Liquid">
<span>Team Liquid</span>
<small>CS2</small>
</a>
<a href="/team/astralis/" class="team-card">
<img src="https://upload.wikimedia.org/wikipedia/commons/thumb/3/37/Astralis_logo.svg/200px-Astralis_logo.svg.png" alt="Astralis">
<span>Astralis</span>
<small>CS2</small>
</a>
<a href="/team/heroic/" class="team-card">
<img src="https://upload.wikimedia.org/wikipedia/commons/thumb/8/8e/Heroic_logo.svg/200px-Heroic_logo.svg.png" alt="Heroic">
<span>Heroic</span>
<small>CS2</small>
</a>
<a href="/team/cloud9/" class="team-card">
<img src="https://upload.wikimedia.org/wikipedia/commons/thumb/f/f7/Cloud9_logo.svg/200px-Cloud9_logo.svg.png" alt="Cloud9">
<span>Cloud9</span>
<small>CS2</small>
</a>
</div>

<div class="section-title">Dota 2</div>
<div class="teams-grid">
<a href="/team/team-spirit/" class="team-card">
<img src="https://upload.wikimedia.org/wikipedia/commons/thumb/8/8e/Team_Spirit_logo.svg/200px-Team_Spirit_logo.svg.png" alt="Team Spirit">
<span>Team Spirit</span>
<small>Dota 2</small>
</a>
</div>
</div>
<!-- /wp:html -->
'''

def main():
    with httpx.Client(timeout=60) as client:
        r = client.get(WP_URL + "/wp-json/wp/v2/pages", params={"slug": "team"}, auth=AUTH)
        if r.status_code == 200 and r.json():
            pid = r.json()[0]["id"]
            r2 = client.post(WP_URL + "/wp-json/wp/v2/pages/" + str(pid), json={"content": PAGE}, auth=AUTH)
            print("OK" if r2.status_code in (200, 201) else "ERR")
        else:
            print("ERR: page not found")

if __name__ == "__main__":
    main()
