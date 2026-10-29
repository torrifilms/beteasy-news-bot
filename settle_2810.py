#!/usr/bin/env python3
"""Settle 28.10 predictions with real results."""

import os
import httpx

WP_URL = os.environ.get("WP_URL", "https://beteasy.ru").rstrip("/")
AUTH = (os.environ.get("WP_USER", ""), os.environ.get("WP_APP_PASS", ""))

# Real results (home-away)
RESULTS = {
    # Serie A 28.10
    ("монца", "наполи"): ("1-4", 1, 4),
    ("дженоа", "ювентус"): ("2-0", 2, 0),
    ("венеция", "интер"): ("0-2", 0, 2),
    ("парма", "удинезе"): ("0-0", 0, 0),
    ("милан", "болонья"): ("2-4", 2, 4),
    # NBA 28.10
    ("chicago bulls", "new york knicks"): ("127-133", 127, 133),
    ("minnesota timberwolves", "golden state warriors"): ("114-119", 114, 119),
    ("toronto raptors", "orlando magic"): ("129-99", 129, 99),
    ("washington capitals", "philadelphia flyers"): ("5-2", 5, 2),
    ("indiana pacers", "philadelphia 76ers"): ("109-114", 109, 114),
    ("detroit pistons", "charlotte hornets"): ("97-89", 97, 89),
    ("cleveland cavaliers", "washington wizards"): ("121-111", 121, 111),
    ("atlanta hawks", "miami heat"): ("117-129", 117, 129),
    ("new york knicks", "detroit pistons"): ("111-97", 111, 97),
    ("boston celtics", "brooklyn nets"): ("125-124", 125, 124),
    # NHL 27-28.10
    ("vegas golden knights", "ottawa senators"): ("4-1", 4, 1),
    ("utah mammoth", "minnesota wild"): ("1-3", 1, 3),
    ("winnipeg jets", "florida panthers"): ("1-5", 1, 5),
    ("dallas stars", "new jersey devils"): ("1-5", 1, 5),
    ("nashville predators", "new york islanders"): ("3-4", 3, 4),
}

def normalize(s):
    return (s or "").lower().strip()

def evaluate(bet, h, a, team1, team2):
    bet_l = (bet or "").lower()
    total = h + a
    if "тотал" in bet_l or "больше" in bet_l:
        if "2.5" in bet_l or "25" in bet_l:
            return "won" if total > 2.5 else "lost"
        if "5.5" in bet_l or "55" in bet_l:
            return "won" if total > 5.5 else "lost"
        if "1.5" in bet_l:
            return "won" if total > 1.5 else "lost"
    if "меньше" in bet_l:
        if "2.5" in bet_l:
            return "won" if total < 2.5 else "lost"
    if "победа" in bet_l:
        t1 = normalize(team1)
        t2 = normalize(team2)
        if t1 and t1 in bet_l:
            return "won" if h > a else "lost"
        if t2 and t2 in bet_l:
            return "won" if a > h else "lost"
    return None

def main():
    with httpx.Client(timeout=60) as client:
        # Get all predictions
        all_preds = []
        page = 1
        while page <= 6:
            r = client.get(
                f"{WP_URL}/wp-json/wp/v2/prediction",
                params={"per_page": 50, "page": page, "orderby": "date", "order": "desc",
                        "_fields": "id,title,acf"},
                auth=AUTH,
            )
            if r.status_code != 200:
                break
            items = r.json()
            if not items:
                break
            all_preds.extend(items)
            if len(items) < 50:
                break
            page += 1

        settled = 0
        for p in all_preds:
            acf = p.get("acf") or {}
            status = (acf.get("prediction_status") or "").lower()
            if status in ("won", "lost"):
                continue
            dt = acf.get("match_datetime") or ""
            if "28.10" not in dt and "27.10" not in dt:
                continue

            t1 = normalize(acf.get("pr_team1") or "")
            t2 = normalize(acf.get("pr_team2") or "")
            bet = acf.get("bet_type") or ""

            # Find matching result
            key = None
            for k in RESULTS:
                if (k[0] in t1 or t1 in k[0]) and (k[1] in t2 or t2 in k[1]):
                    key = k
                    break
                if (k[1] in t1 or t1 in k[1]) and (k[0] in t2 or t2 in k[0]):
                    key = k
                    break
            if not key:
                continue

            score_str, h, a = RESULTS[key]
            result = evaluate(bet, h, a, acf.get("pr_team1"), acf.get("pr_team2"))
            if not result:
                continue

            r = client.post(
                f"{WP_URL}/wp-json/wp/v2/prediction/{p['id']}",
                auth=AUTH,
                json={"acf": {"prediction_status": result, "final_score": score_str}},
            )
            if r.status_code in (200, 201):
                title = p.get("title", {}).get("rendered", "")[:45]
                print(f"OK id={p['id']} {title} → {result} ({score_str})")
                settled += 1

        print(f"\nSettled: {settled}")

if __name__ == "__main__":
    main()
