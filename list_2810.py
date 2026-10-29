#!/usr/bin/env python3
import os, httpx, re

WP_URL = os.environ.get("WP_URL", "https://beteasy.ru").rstrip("/")
AUTH = (os.environ.get("WP_USER", ""), os.environ.get("WP_APP_PASS", ""))

def main():
    with httpx.Client(timeout=60) as client:
        page = 1
        found = []
        while page <= 6:
            r = client.get(
                f"{WP_URL}/wp-json/wp/v2/prediction",
                params={"per_page": 50, "page": page, "orderby": "date", "order": "desc",
                        "_fields": "id,title,acf,date"},
                auth=AUTH,
            )
            if r.status_code != 200:
                break
            items = r.json()
            if not items:
                break
            for p in items:
                acf = p.get("acf") or {}
                dt = acf.get("match_datetime") or ""
                status = acf.get("prediction_status") or ""
                if "28.10" in dt or "28/10" in dt or "2026-10-28" in p.get("date", ""):
                    found.append({
                        "id": p["id"],
                        "title": p.get("title", {}).get("rendered", "")[:50],
                        "dt": dt,
                        "status": status,
                        "team1": acf.get("pr_team1", ""),
                        "team2": acf.get("pr_team2", ""),
                        "bet": acf.get("bet_type", ""),
                    })
            if len(items) < 50:
                break
            page += 1

        print(f"Found {len(found)} predictions for 28.10")
        for f in found[:20]:
            print(f"id={f['id']} status={f['status'] or '-'} dt={f['dt']} | {f['team1']} — {f['team2']} | {f['bet'][:30]}")

if __name__ == "__main__":
    main()
