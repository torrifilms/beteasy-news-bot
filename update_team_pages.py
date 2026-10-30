#!/usr/bin/env python3
"""
Обновляет блоки на страницах команд CS2:
- Последние матчи
- Форма
- Статистика по картам
- Ближайшие матчи
Источник: PandaScore API.
"""

import os
import re
import httpx
from datetime import datetime
from collections import defaultdict

WP_URL = os.environ.get("WP_URL", "https://beteasy.ru").rstrip("/")
WP_AUTH = (os.environ.get("WP_USER", ""), os.environ.get("WP_APP_PASS", ""))
PANDASCORE_KEY = os.environ.get("PANDASCORE_API_KEY", "")

TEAMS = {
    "vitality": "Vitality",
    "navi": "Natus Vincere",
    "faze": "FaZe",
    "g2": "G2",
    "spirit": "Spirit",
    "mouz": "MOUZ",
    "liquid": "Liquid",
    "astralis": "Astralis",
}

CS2_PARENT_ID = 1404


def pandascore_get(path: str, params: dict | None = None) -> list | dict:
    if not PANDASCORE_KEY:
        print("WARN: PANDASCORE_API_KEY не задан")
        return []
    url = f"https://api.pandascore.co{path}"
    headers = {"Authorization": f"Bearer {PANDASCORE_KEY}"}
    try:
        r = httpx.get(url, headers=headers, params=params or {}, timeout=30)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"PandaScore error: {e}")
        return []


def find_team_id(name: str) -> int | None:
    data = pandascore_get("/csgo/teams", {"search[name]": name, "per_page": 5})
    if isinstance(data, list) and data:
        return data[0].get("id")
    return None


def get_recent_matches(team_id: int, limit: int = 10) -> list:
    data = pandascore_get(
        "/csgo/matches/past",
        {"filter[opponent_id]": team_id, "per_page": limit, "sort": "-scheduled_at"},
    )
    return data if isinstance(data, list) else []


def get_upcoming_matches(team_id: int, limit: int = 3) -> list:
    data = pandascore_get(
        "/csgo/matches/upcoming",
        {"filter[opponent_id]": team_id, "per_page": limit, "sort": "scheduled_at"},
    )
    return data if isinstance(data, list) else []


def parse_match(match: dict, team_id: int) -> dict:
    date = ""
    if match.get("scheduled_at"):
        try:
            dt = datetime.fromisoformat(match["scheduled_at"].replace("Z", "+00:00"))
            date = dt.strftime("%d.%m.%y")
        except Exception:
            date = match["scheduled_at"][:10]

    tour = ""
    if match.get("league") and match["league"].get("name"):
        tour = match["league"]["name"][:6].upper()
    elif match.get("tournament") and match["tournament"].get("name"):
        tour = match["tournament"]["name"][:6].upper()

    opponent = "Unknown"
    our_score = 0
    opp_score = 0
    for opp in match.get("opponents", []):
        oid = opp.get("opponent", {}).get("id")
        if oid and oid != team_id:
            opponent = opp.get("opponent", {}).get("name", "Unknown")
            break

    results = match.get("results", [])
    if len(results) >= 2:
        for res in results:
            if res.get("team_id") == team_id:
                our_score = res.get("score", 0)
            else:
                opp_score = res.get("score", 0)

    result = "W" if our_score > opp_score else "L" if our_score < opp_score else "D"

    # Map stats from games
    maps = []
    for game in match.get("games", []):
        map_name = game.get("map", {}).get("name", "") if isinstance(game.get("map"), dict) else ""
        if map_name:
            winner_id = game.get("winner", {}).get("id") if isinstance(game.get("winner"), dict) else None
            maps.append({"map": map_name, "win": winner_id == team_id})

    return {
        "date": date,
        "tour": tour,
        "opponent": opponent,
        "score": f"{our_score}:{opp_score}",
        "result": result,
        "maps": maps,
    }


def build_form_html(matches: list) -> str:
    colors = {"W": "#27ae60", "L": "#e74c3c", "D": "#f39c12"}
    items = []
    for m in matches[:5]:
        r = m["result"]
        items.append(f'<span class="tp-fb" style="background:{colors.get(r, "#79829B")}">{r}</span>')
    return "\n".join(items) if items else '<span class="tp-fb" style="background:#79829B">—</span>'


def build_matches_html(matches: list) -> str:
    rows = []
    for m in matches[:6]:
        cls = "win" if m["result"] == "W" else "loss" if m["result"] == "L" else ""
        rows.append(f'''<div class="tp-match">
<div class="tp-match-left"><span class="tp-match-date">{m["date"]}</span><span class="tp-match-tour">{m["tour"]}</span><span class="tp-match-opp">vs {m["opponent"]}</span></div>
<span class="tp-match-score {cls}">{m["score"]}</span>
</div>''')
    return "\n".join(rows) if rows else '<p class="muted">Нет данных</p>'


def build_upcoming_html(matches: list) -> str:
    rows = []
    for m in matches[:3]:
        rows.append(f'''<div class="tp-match">
<div class="tp-match-left"><span class="tp-match-date">{m["date"]}</span><span class="tp-match-tour">{m["tour"]}</span><span class="tp-match-opp">vs {m["opponent"]}</span></div>
<span class="tp-match-score">—</span>
</div>''')
    return "\n".join(rows) if rows else '<p class="muted">Нет ближайших матчей</p>'


def build_map_stats_html(matches: list) -> str:
    """Считает статистику по картам из последних матчей."""
    map_stats = defaultdict(lambda: {"played": 0, "wins": 0})
    for m in matches:
        for mp in m.get("maps", []):
            name = mp["map"]
            if name:
                map_stats[name]["played"] += 1
                if mp["win"]:
                    map_stats[name]["wins"] += 1

    if not map_stats:
        return '<p class="muted">Нет данных по картам</p>'

    sorted_maps = sorted(map_stats.items(), key=lambda x: x[1]["played"], reverse=True)[:8]
    rows = ['<table class="tp-map-table"><tr><th>#</th><th>Карта</th><th>И</th><th>В</th><th>П</th><th>%</th></tr>']
    for i, (name, stats) in enumerate(sorted_maps, 1):
        played = stats["played"]
        wins = stats["wins"]
        losses = played - wins
        pct = int(wins / played * 100) if played else 0
        rows.append(f'<tr><td>{i}</td><td>{name}</td><td>{played}</td><td class="win">{wins}</td><td class="loss">{losses}</td><td>{pct}%</td></tr>')
    rows.append('</table>')
    return "\n".join(rows)


def get_page_content(slug: str) -> tuple:
    with httpx.Client(timeout=30) as client:
        r = client.get(
            f"{WP_URL}/wp-json/wp/v2/pages",
            params={"slug": slug, "parent": CS2_PARENT_ID, "context": "edit"},
            auth=WP_AUTH,
        )
        if r.status_code == 200 and r.json():
            page = r.json()[0]
            return page["id"], page.get("content", {}).get("raw", "")
    return None, ""


def update_page(page_id: int, content: str) -> bool:
    with httpx.Client(timeout=60) as client:
        r = client.post(
            f"{WP_URL}/wp-json/wp/v2/pages/{page_id}",
            json={"content": content},
            auth=WP_AUTH,
        )
        return r.status_code in (200, 201)


def replace_block(content: str, marker_start: str, marker_end: str, new_inner: str) -> str:
    pattern = re.escape(marker_start) + r".*?" + re.escape(marker_end)
    replacement = marker_start + "\n" + new_inner + "\n" + marker_end
    if re.search(pattern, content, flags=re.DOTALL):
        return re.sub(pattern, replacement, content, count=1, flags=re.DOTALL)
    return content


def update_team(slug: str, search_name: str) -> str:
    team_id = find_team_id(search_name)
    if not team_id:
        return f"{slug}: team not found"

    matches_raw = get_recent_matches(team_id, limit=10)
    upcoming_raw = get_upcoming_matches(team_id, limit=3)

    if not matches_raw:
        return f"{slug}: no matches"

    matches = [parse_match(m, team_id) for m in matches_raw]
    upcoming = [parse_match(m, team_id) for m in upcoming_raw] if upcoming_raw else []

    form_html = build_form_html(matches)
    matches_html = build_matches_html(matches)
    upcoming_html = build_upcoming_html(upcoming)
    map_html = build_map_stats_html(matches)

    page_id, content = get_page_content(slug)
    if not page_id or not content:
        return f"{slug}: page not found"

    # Update blocks
    content = replace_block(content, '<h3>Форма</h3>', '</div>', f'<div class="tp-form">\n{form_html}\n</div>')
    content = replace_block(content, '<h3>Последние матчи</h3>', '</div>', matches_html)
    content = replace_block(content, '<h3>Ближайшие матчи</h3>', '</div>', upcoming_html)
    content = replace_block(content, '<h3>Статистика по картам</h3>', '</div>', map_html)

    if update_page(page_id, content):
        return f"{slug}: OK ({len(matches)} past, {len(upcoming)} upcoming)"
    return f"{slug}: update failed"


def main():
    print("=== update_team_pages.py ===")
    if not PANDASCORE_KEY:
        print("ERROR: задайте PANDASCORE_API_KEY")
        return
    for slug, name in TEAMS.items():
        status = update_team(slug, name)
        print(status)
    print("=== done ===")


if __name__ == "__main__":
    main()
