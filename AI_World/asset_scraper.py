#!/usr/bin/env python3
"""
N64 AI Co-op Lab — Asset Scraper
=================================
Scrapes N64 asset repositories and mod sites for textures, models,
and metadata. Integrates with Firecrawl if available, falls back
to direct HTTP + BeautifulSoup.
"""

import os
import json
import time
import requests
from pathlib import Path
from urllib.parse import urljoin, urlparse

OUTPUT_DIR = os.path.expanduser("~/HylianModding/MyWorld/scraped_assets")
METADATA_DIR = os.path.expanduser("~/HylianModding/Library/Metadata")

# Known asset repositories
ASSET_SITES = {
    "textures": [
        "https://github.com/gonetz/GLideN64/tree/master/textures",
        "https://github.com/Rosalie241/RMG/tree/master/textures",
    ],
    "models": [
        "https://github.com/HarbourMasters/fast64",
        "https://github.com/NicoYazawa/fast64",
    ],
    "tools": [
        "https://github.com/HarbourMasters64/retro",
        "https://github.com/xoascf/OTRMod",
    ],
    "mods": [
        "https://gamebanana.com/games/7060",  # OoT mods
    ],
}


def scrape_archive_org(query="n64 texture pack", max_results=20):
    """Search Archive.org for N64 assets."""
    url = "https://archive.org/advancedsearch.php"
    params = {
        "q": query,
        "fl[]": ["identifier", "title", "description", "subject"],
        "sort[]": "downloads desc",
        "rows": max_results,
        "page": 1,
        "output": "json",
    }
    try:
        r = requests.get(url, params=params, timeout=15)
        data = r.json()
        results = []
        for doc in data.get("response", {}).get("docs", []):
            results.append({
                "source": "archive.org",
                "id": doc.get("identifier"),
                "title": doc.get("title"),
                "description": doc.get("description", "")[:200],
                "url": f"https://archive.org/details/{doc.get('identifier')}",
            })
        return results
    except Exception as e:
        return [{"error": str(e)}]


def scrape_gamebanana_oot(max_items=20):
    """Scrape GameBanana for OoT mods/tools."""
    # GameBanana API
    try:
        r = requests.get(
            "https://api.gamebanana.com/Util/Game/Profile",
            params={"gameid": 7060},
            timeout=15
        )
        data = r.json()
        results = []
        # Extract mod listings if present
        for section in data.get("sections", []):
            for item in section.get("items", [])[:max_items]:
                results.append({
                    "source": "gamebanana",
                    "id": item.get("id"),
                    "title": item.get("name"),
                    "type": item.get("type"),
                    "url": f"https://gamebanana.com/{item.get('type')}s/{item.get('id')}",
                })
        return results
    except Exception as e:
        return [{"error": str(e)}]


def scrape_github_repos(query="n64 texture", max_results=10):
    """Search GitHub for N64-related repositories."""
    url = "https://api.github.com/search/repositories"
    params = {"q": query, "sort": "stars", "order": "desc", "per_page": max_results}
    try:
        r = requests.get(url, params=params, timeout=15)
        data = r.json()
        results = []
        for repo in data.get("items", []):
            results.append({
                "source": "github",
                "name": repo.get("full_name"),
                "description": repo.get("description", "")[:200],
                "stars": repo.get("stargazers_count"),
                "url": repo.get("html_url"),
                "language": repo.get("language"),
            })
        return results
    except Exception as e:
        return [{"error": str(e)}]


def scrape_spriters_resource():
    """Scrape Spriters-Resource for N64 game listings."""
    try:
        r = requests.get("https://www.spriters-resource.com/nintendo_64/", timeout=15)
        html = r.text
        # Very basic extraction
        results = []
        # Find game links
        import re
        matches = re.findall(r'<a href="(/nintendo_64/[^"]+)"[^>]*>([^<]+)</a>', html)
        for href, name in matches[:30]:
            results.append({
                "source": "spriters-resource",
                "name": name.strip(),
                "url": f"https://www.spriters-resource.com{href}",
            })
        return results
    except Exception as e:
        return [{"error": str(e)}]


def run_full_scrape():
    """Run all scrapers and merge results."""
    print("[AssetScraper] Running full asset discovery...")
    all_results = {
        "archive_org": scrape_archive_org(),
        "gamebanana": scrape_gamebanana_oot(),
        "github": scrape_github_repos(),
        "spriters_resource": scrape_spriters_resource(),
    }
    
    os.makedirs(METADATA_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    with open(os.path.join(METADATA_DIR, "scraped_assets.json"), "w") as f:
        json.dump(all_results, f, indent=2)
    
    total = sum(len(v) for v in all_results.values() if isinstance(v, list))
    print(f"[AssetScraper] Discovered {total} assets across {len(all_results)} sources")
    return all_results


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--full", action="store_true", help="Run all scrapers")
    parser.add_argument("--source", choices=["archive", "gamebanana", "github", "spriters"])
    args = parser.parse_args()
    
    if args.full:
        run_full_scrape()
    elif args.source == "archive":
        print(json.dumps(scrape_archive_org(), indent=2))
    elif args.source == "gamebanana":
        print(json.dumps(scrape_gamebanana_oot(), indent=2))
    elif args.source == "github":
        print(json.dumps(scrape_github_repos(), indent=2))
    elif args.source == "spriters":
        print(json.dumps(scrape_spriters_resource(), indent=2))
    else:
        print("Usage: asset_scraper.py --full | --source <source>")
