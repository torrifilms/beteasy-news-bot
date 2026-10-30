#!/usr/bin/env python3
"""Update Dota 2 hub with all teams."""

import os
import httpx

WP_URL = os.environ.get("WP_URL", "https://beteasy.ru").rstrip("/")
AUTH = (os.environ.get("WP_USER", ""), os.environ.get("WP_APP_PASS", ""))

HUB = '''<!-- wp:html -->
<style>.hub{max-width:960px;margin:20px auto;padding:0 16px}.hub h1{font-family:Unbounded,sans-serif;font-size:28px;margin:0 0 8px;text-transform:uppercase;color:#EDF0F7}.hub .sub{color:#79829B;margin-bottom:24px}.teams-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:16px}.team-card{display:flex;flex-direction:column;align-items:center;padding:20px 12px;background:#0E1016;border:1px solid rgba(121,130,155,.2);border-radius:16px;text-decoration:none;transition:all .3s}.team-card:hover{border-color:rgba(214,255,59,.4);transform:translateY(-4px)}.team-card img{width:64px;height:64px;object-fit:contain;margin-bottom:10px}.team-card b{font-family:Unbounded,sans-serif;font-size:12px;color:#EDF0F7;text-transform:uppercase;text-align:center}.team-card span{font-size:10px;color:#79829B;margin-top:4px}.bread{display:flex;gap:8px;margin-bottom:16px;font-size:13px}.bread a{color:#79829B;text-decoration:none}.bread a:hover{color:#D6FF3B}.bread span{color:#79829B}</style>
<div class="hub">
<div class="bread"><a href="/">Главная</a><span>→</span><a href="/teams/">Команды</a><span>→</span><span>Dota 2</span></div>
<h1>Команды Dota 2</h1>
<p class="sub">Топ-команды по рейтингу на октябрь 2026. Составы, статистика, турниры.</p>
<div class="teams-grid">
<a href="/teams/dota2/parivision/" class="team-card"><img src="https://logo.clearbit.com/parivision.gg" alt="PARIVISION"><b>PARIVISION</b><span>#1 · $4.5M</span></a>
<a href="/teams/dota2/team-spirit/" class="team-card"><img src="https://logo.clearbit.com/teamspirit.gg" alt="Team Spirit"><b>Team Spirit</b><span>#2 · $33.3M</span></a>
<a href="/teams/dota2/falcons/" class="team-card"><img src="https://logo.clearbit.com/teamfalcons.gg" alt="Falcons"><b>Team Falcons</b><span>#3 · $7.3M</span></a>
<a href="/teams/dota2/yandex/" class="team-card"><img src="https://logo.clearbit.com/yandex.ru" alt="Yandex"><b>Team Yandex</b><span>#4 · $2.8M</span></a>
<a href="/teams/dota2/aurora/" class="team-card"><img src="https://logo.clearbit.com/auroragaming.gg" alt="Aurora"><b>Aurora Gaming</b><span>#5 · $1.9M</span></a>
<a href="/teams/dota2/liquid/" class="team-card"><img src="https://logo.clearbit.com/teamliquid.com" alt="Liquid"><b>Team Liquid</b><span>#6 · $34.2M</span></a>
<a href="/teams/dota2/navi/" class="team-card"><img src="https://logo.clearbit.com/navi.gg" alt="NaVi"><b>Natus Vincere</b><span>#7 · $6.3M</span></a>
<a href="/teams/dota2/nigma/" class="team-card"><img src="https://logo.clearbit.com/nigma-galaxy.com" alt="Nigma"><b>Nigma Galaxy</b><span>#8 · $1.9M</span></a>
<a href="/teams/dota2/xtreme/" class="team-card"><img src="https://logo.clearbit.com/xtremegaming.gg" alt="Xtreme"><b>Xtreme Gaming</b><span>#9 · $3.8M</span></a>
<a href="/teams/dota2/1win/" class="team-card"><img src="https://logo.clearbit.com/1win.team" alt="1win"><b>1win Team</b><span>#10 · $0.7M</span></a>
<a href="/teams/dota2/betboom/" class="team-card"><img src="https://logo.clearbit.com/betboom.team" alt="BetBoom"><b>BetBoom Team</b><span>#11 · $2.1M</span></a>
<a href="/teams/dota2/og/" class="team-card"><img src="https://logo.clearbit.com/ogs.gg" alt="OG"><b>OG</b><span>#12 · $37.8M</span></a>
</div>
</div>
<!-- /wp:html -->'''

def main():
    with httpx.Client(timeout=30) as client:
        r = client.get(WP_URL + "/wp-json/wp/v2/pages", params={"slug": "dota2"}, auth=AUTH)
        if r.status_code == 200 and r.json():
            pid = r.json()[0]["id"]
            r2 = client.post(WP_URL + "/wp-json/wp/v2/pages/" + str(pid), json={"content": HUB}, auth=AUTH)
            print("OK" if r2.status_code in (200, 201) else "ERR")
        else:
            print("ERR: hub not found")

if __name__ == "__main__":
    main()
