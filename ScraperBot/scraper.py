#!/usr/bin/env python3
"""
N64 Modding Metadata Scraper Bot
================================
Scrapes metadata (titles, descriptions, URLs, authors) from various sources.
Does NOT download copyrighted files — only indexes what exists.

Sources:
- TCRF (The Cutting Room Floor) — MediaWiki API
- Archive.org — Internet Archive API
- GameBanana — Web/API scraping
- Spriters Resource — Page listings
"""

import os
import sys
import json
import time
import argparse
from dataclasses import dataclass, asdict
from typing import List, Optional
from urllib.parse import urlencode, quote

import requests

OUTPUT_DIR = os.path.expanduser("~/HylianModding/ScraperBot/outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

SESSION = requests.Session()
SESSION.headers.update({
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
})


@dataclass
class CatalogEntry:
    source: str
    title: str
    url: str
    description: str = ""
    author: str = ""
    date: str = ""
    category: str = ""
    tags: List[str] = None
    extra: dict = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.extra is None:
            self.extra = {}


# =============================================================================
# TCRF (The Cutting Room Floor) — MediaWiki API
# =============================================================================

class TCRFScraper:
    BASE = "https://tcrf.net"
    API = "https://tcrf.net/api.php"

    def get_category_pages(self, category: str, limit: int = 500) -> List[CatalogEntry]:
        """Get all pages in a TCRF category."""
        entries = []
        cmcontinue = None

        while True:
            params = {
                "action": "query",
                "list": "categorymembers",
                "cmtitle": f"Category:{category}",
                "cmlimit": min(limit, 50),
                "format": "json",
                "origin": "*",
            }
            if cmcontinue:
                params["cmcontinue"] = cmcontinue

            try:
                resp = SESSION.get(self.API, params=params, timeout=30)
                data = resp.json()
            except Exception as e:
                print(f"[TCRF] Error: {e}")
                break

            members = data.get("query", {}).get("categorymembers", [])
            for m in members:
                title = m.get("title", "")
                page_id = m.get("pageid", "")
                ns = m.get("ns", 0)
                # Skip category pages themselves
                if title.startswith("Category:"):
                    continue
                entries.append(CatalogEntry(
                    source="tcrf",
                    title=title,
                    url=f"{self.BASE}/{quote(title.replace(' ', '_'))}",
                    description="",
                    category=category,
                    extra={"pageid": page_id, "ns": ns},
                ))

            if len(entries) >= limit:
                break

            cmcontinue = data.get("continue", {}).get("cmcontinue")
            if not cmcontinue:
                break
            time.sleep(0.5)

        print(f"[TCRF] Found {len(entries)} pages in Category:{category}")
        return entries

    def get_page_extracts(self, titles: List[str]) -> dict:
        """Get page extracts (descriptions) for a batch of titles."""
        title_str = "|".join(t.replace(" ", "_") for t in titles[:50])
        params = {
            "action": "query",
            "prop": "extracts",
            "titles": title_str,
            "exintro": True,
            "explaintext": True,
            "exlimit": 50,
            "format": "json",
            "origin": "*",
        }
        try:
            resp = SESSION.get(self.API, params=params, timeout=30)
            data = resp.json()
            pages = data.get("query", {}).get("pages", {})
            extracts = {}
            for page_id, page_data in pages.items():
                title = page_data.get("title", "")
                extract = page_data.get("extract", "")
                extracts[title] = extract[:500]  # First 500 chars
            return extracts
        except Exception as e:
            print(f"[TCRF] Extract error: {e}")
            return {}


# =============================================================================
# Archive.org — Metadata API
# =============================================================================

class ArchiveOrgScraper:
    BASE = "https://archive.org"
    API = "https://archive.org/advancedsearch.php"

    def search(self, query: str, mediatype: str = "software", rows: int = 100) -> List[CatalogEntry]:
        """Search Archive.org for items matching query."""
        entries = []
        page = 1

        while len(entries) < rows:
            params = {
                "q": query,
                "fl[]": ["identifier", "title", "description", "creator", "date", "subject"],
                "sort[]": "date desc",
                "rows": min(50, rows - len(entries)),
                "page": page,
                "output": "json",
                "save": "yes",
            }
            try:
                resp = SESSION.get(self.API, params=params, timeout=30)
                data = resp.json()
            except Exception as e:
                print(f"[Archive.org] Error: {e}")
                break

            docs = data.get("response", {}).get("docs", [])
            if not docs:
                break

            for doc in docs:
                entries.append(CatalogEntry(
                    source="archive.org",
                    title=doc.get("title", "Untitled"),
                    url=f"{self.BASE}/details/{doc.get('identifier', '')}",
                    description=doc.get("description", "")[:300] if doc.get("description") else "",
                    author=doc.get("creator", "") if isinstance(doc.get("creator"), str) else ", ".join(doc.get("creator", [])[:3]),
                    date=doc.get("date", ""),
                    category=mediatype,
                    tags=doc.get("subject", [])[:10] if isinstance(doc.get("subject"), list) else [],
                    extra={"identifier": doc.get("identifier")},
                ))

            page += 1
            time.sleep(0.5)

        print(f"[Archive.org] Found {len(entries)} items for query: {query}")
        return entries


# =============================================================================
# GameBanana — Web scraping with API fallback
# =============================================================================

class GameBananaScraper:
    BASE = "https://gamebanana.com"

    def get_mods(self, game_id: int = 7060, page: int = 1, per_page: int = 30) -> List[CatalogEntry]:
        """Get mod listings from GameBanana."""
        entries = []
        url = f"{self.BASE}/apiv11/Game/{game_id}/Subfeed"
        params = {
            "_csvProperties": "_sName,_sProfileUrl,_sDescription,_aSubmitter,_tsDateAdded,_nViewCount,_nLikeCount,_nDownloadCount,_sModelName,_aTags",
            "_sSort": "default",
            "_nPage": page,
            "_nPerpage": per_page,
        }
        try:
            resp = SESSION.get(url, params=params, timeout=30)
            if resp.status_code == 200:
                data = resp.json()
                for item in data.get("_aRecords", []):
                    author = item.get("_aSubmitter", {}).get("_sName", "")
                    entries.append(CatalogEntry(
                        source="gamebanana",
                        title=item.get("_sName", "Untitled"),
                        url=item.get("_sProfileUrl", ""),
                        description=item.get("_sDescription", "")[:300] if item.get("_sDescription") else "",
                        author=author,
                        date=str(item.get("_tsDateAdded", "")),
                        category=item.get("_sModelName", ""),
                        tags=item.get("_aTags", []),
                        extra={
                            "mod_id": item.get("_idRow"),
                            "views": item.get("_nViewCount", 0),
                            "likes": item.get("_nLikeCount", 0),
                            "downloads": item.get("_nDownloadCount", 0),
                        },
                    ))
            else:
                print(f"[GameBanana] API returned {resp.status_code}: {resp.text[:200]}")
        except Exception as e:
            print(f"[GameBanana] Error: {e}")

        print(f"[GameBanana] Found {len(entries)} mods/tools")
        return entries


# =============================================================================
# Spriters Resource — Page scraping
# =============================================================================

class SpritersResourceScraper:
    BASE = "https://www.spriters-resource.com"

    def get_n64_models(self) -> List[CatalogEntry]:
        """Get N64 model listings."""
        entries = []
        url = f"{self.BASE}/nintendo_64/"
        try:
            resp = SESSION.get(url, timeout=30)
            html = resp.text
            # Parse game listings
            import re
            games = re.findall(r'<a href="(/nintendo_64/[^"]+)"[^>]*>([^<]+)</a>', html)
            for path, title in games[:100]:
                if path == "/nintendo_64/":
                    continue
                entries.append(CatalogEntry(
                    source="spriters-resource",
                    title=title.strip(),
                    url=f"{self.BASE}{path}",
                    category="n64_models",
                ))
        except Exception as e:
            print(f"[Spriters Resource] Error: {e}")

        print(f"[Spriters Resource] Found {len(entries)} N64 games with models")
        return entries


# =============================================================================
# MAIN ORCHESTRATOR
# =============================================================================

def run_all_scrapers(tcrf_categories: List[str] = None,
                     archive_queries: List[str] = None,
                     gamebanana_pages: int = 1,
                     output_name: str = "catalog") -> dict:
    """Run all scrapers and merge results."""
    if tcrf_categories is None:
        tcrf_categories = ["July_2020_Nintendo_Leak"]
    if archive_queries is None:
        archive_queries = [
            "nintendo 64 prototype",
            "ocarina of time beta",
            "zelda 64 debug",
            "n64 source code",
        ]

    all_entries: List[CatalogEntry] = []

    # TCRF
    tcrf = TCRFScraper()
    for cat in tcrf_categories:
        pages = tcrf.get_category_pages(cat, limit=200)
        # Fetch extracts for first batch
        if pages:
            titles = [p.title for p in pages[:50]]
            extracts = tcrf.get_page_extracts(titles)
            for p in pages:
                p.description = extracts.get(p.title, "")
        all_entries.extend(pages)
        time.sleep(1)

    # Archive.org
    archive = ArchiveOrgScraper()
    for q in archive_queries:
        items = archive.search(q, rows=100)
        all_entries.extend(items)
        time.sleep(1)

    # GameBanana
    gb = GameBananaScraper()
    for p in range(1, gamebanana_pages + 1):
        mods = gb.get_mods(game_id=7060, page=p)
        all_entries.extend(mods)
        time.sleep(1)

    # Spriters Resource
    sr = SpritersResourceScraper()
    games = sr.get_n64_models()
    all_entries.extend(games)

    # Save
    result = {
        "total_entries": len(all_entries),
        "sources": {},
        "entries": [asdict(e) for e in all_entries],
    }
    for e in all_entries:
        result["sources"][e.source] = result["sources"].get(e.source, 0) + 1

    output_path = os.path.join(OUTPUT_DIR, f"{output_name}.json")
    with open(output_path, 'w') as f:
        json.dump(result, f, indent=2)

    print(f"\n[Scraper] Total cataloged: {len(all_entries)} entries")
    for src, count in result["sources"].items():
        print(f"  {src}: {count}")
    print(f"[Scraper] Saved to: {output_path}")

    return result


def main():
    parser = argparse.ArgumentParser(description="N64 Modding Metadata Scraper")
    parser.add_argument("--tcrf", nargs="+", default=["July_2020_Nintendo_Leak"], help="TCRF categories")
    parser.add_argument("--archive", nargs="+", default=["nintendo 64 prototype", "ocarina of time beta"], help="Archive.org queries")
    parser.add_argument("--gb-pages", type=int, default=1, help="GameBanana pages to scrape")
    parser.add_argument("--output", default="catalog", help="Output filename")
    args = parser.parse_args()

    run_all_scrapers(
        tcrf_categories=args.tcrf,
        archive_queries=args.archive,
        gamebanana_pages=args.gb_pages,
        output_name=args.output,
    )


if __name__ == "__main__":
    main()
