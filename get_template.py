#!/usr/bin/env python3
"""Get Real Madrid page template."""

import os
import httpx

WP_URL = os.environ.get("WP_URL", "https://beteasy.ru").rstrip("/")
AUTH = (os.environ.get("WP_USER", ""), os.environ.get("WP_APP_PASS", ""))

def main():
    with httpx.Client(timeout=30) as client:
        r = client.get(WP_URL + "/wp-json/wp/v2/pages", params={"slug": "team-real-madrid", "context": "edit"}, auth=AUTH)
        if r.status_code == 200 and r.json():
            content = r.json()[0].get("content", {}).get("raw", "")
            # Save first 3000 chars to see structure
            print(content[:3000])
            print("...")
            print(f"Total length: {len(content)}")

if __name__ == "__main__":
    main()
