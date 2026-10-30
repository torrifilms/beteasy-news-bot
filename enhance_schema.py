#!/usr/bin/env python3
"""Add rich Schema.org to all team pages and predictions."""

import os
import httpx
import json
import re

WP_URL = os.environ.get("WP_URL", "https://beteasy.ru").rstrip("/")
AUTH = (os.environ.get("WP_USER", ""), os.environ.get("WP_APP_PASS", ""))

def get_pages(client, parent_slug):
    r = client.get(WP_URL + "/wp-json/wp/v2/pages", params={"slug": parent_slug}, auth=AUTH)
    if not (r.status_code == 200 and r.json()):
        return []
    parent_id = r.json()[0]["id"]
    r = client.get(WP_URL + "/wp-json/wp/v2/pages", params={"parent": parent_id, "per_page": 50, "context": "edit"}, auth=AUTH)
    return r.json() if r.status_code == 200 else []

def build_schema(name, sport, url, founding=None):
    schema = {
        "@context": "https://schema.org",
        "@type": "SportsTeam",
        "name": name,
        "sport": sport,
        "url": url,
    }
    if founding:
        schema["foundingDate"] = founding
    return f'<script type="application/ld+json">{json.dumps(schema, ensure_ascii=False)}</script>'

def build_faq_schema(faqs):
    if not faqs:
        return ""
    entities = []
    for q, a in faqs:
        entities.append({
            "@type": "Question",
            "name": q,
            "acceptedAnswer": {"@type": "Answer", "text": a}
        })
    schema = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": entities
    }
    return f'<script type="application/ld+json">{json.dumps(schema, ensure_ascii=False)}</script>'

def extract_faqs(content):
    """Extract FAQ Q&A from existing HTML."""
    faqs = []
    matches = re.findall(r'<div class="tp-faq"><b>(.*?)</b><p>(.*?)</p></div>', content, re.DOTALL)
    for q, a in matches[:5]:
        faqs.append((q.strip(), a.strip()))
    return faqs

def update_page(client, page_id, content):
    r = client.post(WP_URL + f"/wp-json/wp/v2/pages/{page_id}", json={"content": content}, auth=AUTH)
    return r.status_code in (200, 201)

def main():
    sports = [
        ("cs2", "CS2"),
        ("dota2", "Dota 2"),
        ("football", "Football"),
    ]
    with httpx.Client(timeout=120) as client:
        for parent_slug, sport_name in sports:
            pages = get_pages(client, parent_slug)
            print(f"=== {sport_name}: {len(pages)} pages ===")
            for page in pages:
                slug = page.get("slug", "")
                content = page.get("content", {}).get("raw", "")
                if not content or "FAQPage" in content:
                    continue
                # Extract name from content
                name_match = re.search(r'<h1>([^<]+)</h1>', content)
                name = name_match.group(1).strip() if name_match else slug.replace("-", " ").title()
                url = f"https://beteasy.ru/teams/{parent_slug}/{slug}/"
                faqs = extract_faqs(content)
                # Build enhanced schema
                team_schema = build_schema(name, sport_name, url)
                faq_schema = build_faq_schema(faqs)
                # Replace old simple schema or append
                if 'application/ld+json' in content and 'SportsTeam' in content:
                    content = re.sub(r'<script type="application/ld\+json">.*?</script>', team_schema, content, count=1, flags=re.DOTALL)
                else:
                    content += "\n" + team_schema
                if faq_schema:
                    content += "\n" + faq_schema
                if update_page(client, page["id"], content):
                    print(f"  {slug}: OK")
                else:
                    print(f"  {slug}: ERR")

if __name__ == "__main__":
    main()
