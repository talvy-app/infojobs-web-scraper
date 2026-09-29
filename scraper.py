#!/usr/bin/env python3
"""Demo scraper for the InfoJobs web search API (Schibsted webapp endpoint).

    GET https://www.infojobs.net/webapp/offers/search?keyword={kw}&page={n}

Usage:
    python3 scraper.py developer
    python3 scraper.py developer "data engineer" --page 2
    python3 scraper.py developer --output jobs.json
"""

import argparse
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

BASE_URL = "https://www.infojobs.net/webapp/offers/search"
TIMEOUT = 30
RETRIES = 3
# InfoJobs blocks default script UAs (HTTP 456); a browser UA is required.
# The Schibsted/Adevinta headers mirror the web app but are optional in practice.
HEADERS = {
    "Accept": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "X-Schibsted-Tenant": "infojobs",
    "X-Adevinta-Channel": "web",
    "Portalid": "0",
}


def search(keyword: str, page: int = 1) -> dict:
    """GET one page of offers for a keyword. Returns the raw payload with
    `offers`, `navigation` (totalPages/totalElements), `aggregation`, etc.

    Raises ValueError after exhausting retries.
    """
    qs = urllib.parse.urlencode({"keyword": keyword, "page": page})
    url = f"{BASE_URL}?{qs}"
    last_error = None
    for attempt in range(1, RETRIES + 1):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=TIMEOUT) as res:
                return json.load(res)
        except urllib.error.HTTPError as e:
            last_error = f"HTTP {e.code}"
            if e.code in (400, 404):
                raise ValueError(f"search failed: {keyword} page {page}: {last_error}") from e
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as e:
            last_error = str(e)
        if attempt < RETRIES:
            time.sleep(2 * attempt)
    raise ValueError(f"{keyword} page {page} failed after {RETRIES} attempts: {last_error}")


def scrape(keywords, page=1):
    results = {}
    for kw in keywords:
        try:
            payload = search(kw, page)
        except ValueError as e:
            print(f"warn: {e}", file=sys.stderr)
            results[kw] = []
            continue
        offers = payload.get("offers", [])
        results[kw] = offers
        total_pages = payload.get("navigation", {}).get("totalPages", "?")
        print(f"{kw} (page {page}/{total_pages}): {len(offers)} offers", file=sys.stderr)
        if page > 1 and not offers:
            print(f"warn: page {page} beyond range for '{kw}' (max {total_pages})", file=sys.stderr)
    return results


def main():
    p = argparse.ArgumentParser(description="Scrape InfoJobs web search (demo).")
    p.add_argument("keywords", nargs="+", help='search keyword, e.g. developer, "data engineer"')
    p.add_argument("--page", type=int, default=1, help="page number (default: 1)")
    p.add_argument("--output", metavar="FILE", help="write JSON to FILE instead of stdout")
    args = p.parse_args()

    result = scrape(args.keywords, page=args.page)
    out = json.dumps(result, indent=2, ensure_ascii=False)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(out + "\n")
        print(f"wrote {args.output}", file=sys.stderr)
    else:
        print(out)


if __name__ == "__main__":
    main()
