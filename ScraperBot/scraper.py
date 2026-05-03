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

# GitHub API token (optional, increases rate limit)
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")

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
# GitHub — Search repos, releases, and assets
# =============================================================================

class GitHubScraper:
    BASE = "https://api.github.com"
    HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}

    def search_repos(self, query: str, limit: int = 100) -> List[CatalogEntry]:
        """Search GitHub repositories."""
        entries = []
        page = 1
        while len(entries) < limit:
            params = {"q": query, "sort": "stars", "order": "desc", "per_page": min(30, limit - len(entries)), "page": page}
            try:
                resp = SESSION.get(f"{self.BASE}/search/repositories", params=params, headers=self.HEADERS, timeout=30)
                if resp.status_code == 403:
                    print("[GitHub] Rate limited. Set GITHUB_TOKEN env var.")
                    break
                data = resp.json()
                items = data.get("items", [])
                if not items:
                    break
                for item in items:
                    entries.append(CatalogEntry(
                        source="github",
                        title=item.get("full_name", ""),
                        url=item.get("html_url", ""),
                        description=item.get("description", "")[:300],
                        author=item.get("owner", {}).get("login", ""),
                        date=item.get("updated_at", ""),
                        category="repository",
                        tags=item.get("topics", []),
                        extra={"stars": item.get("stargazers_count", 0), "language": item.get("language", "")},
                    ))
                page += 1
                time.sleep(0.5)
            except Exception as e:
                print(f"[GitHub] Error: {e}")
                break
        print(f"[GitHub] Found {len(entries)} repos for: {query}")
        return entries

    def get_releases(self, repo: str, limit: int = 20) -> List[CatalogEntry]:
        """Get releases for a repo."""
        entries = []
        try:
            resp = SESSION.get(f"{self.BASE}/repos/{repo}/releases", headers=self.HEADERS, timeout=30)
            if resp.status_code != 200:
                return entries
            releases = resp.json()[:limit]
            for rel in releases:
                entries.append(CatalogEntry(
                    source="github",
                    title=f"{repo} - {rel.get('tag_name', '')}",
                    url=rel.get("html_url", ""),
                    description=rel.get("body", "")[:500],
                    author=rel.get("author", {}).get("login", ""),
                    date=rel.get("published_at", ""),
                    category="release",
                    extra={"draft": rel.get("draft", False), "prerelease": rel.get("prerelease", False)},
                ))
        except Exception as e:
            print(f"[GitHub] Release error: {e}")
        return entries


# =============================================================================
# Models Resource — Web scraping
# =============================================================================

class ModelsResourceScraper:
    BASE = "https://models-resource.com"

    def get_n64_models(self) -> List[CatalogEntry]:
        """Get N64 model listings from Models Resource."""
        entries = []
        url = f"{self.BASE}/nintendo/n64/"
        try:
            resp = SESSION.get(url, timeout=30)
            html = resp.text
            import re
            games = re.findall(r'<a href="(/nintendo/n64/[^"]+)"[^>]*>\s*<img[^>]*>\s*<span[^>]*>([^<]+)</span>', html)
            for path, title in games[:100]:
                entries.append(CatalogEntry(
                    source="models-resource",
                    title=title.strip(),
                    url=f"{self.BASE}{path}",
                    category="n64_models",
                ))
        except Exception as e:
            print(f"[Models Resource] Error: {e}")
        print(f"[Models Resource] Found {len(entries)} N64 games")
        return entries


# =============================================================================
# Textures Resource — Scrape N64 textures
# =============================================================================

class TexturesResourceScraper:
    BASE = "https://www.textures-resource.com"

    def get_n64_textures(self) -> List[CatalogEntry]:
        """Get N64 texture listings."""
        entries = []
        url = f"{self.BASE}/nintendo_64/"
        try:
            resp = SESSION.get(url, timeout=30)
            html = resp.text
            import re
            # Match texture game links
            games = re.findall(r'<a href="(/nintendo_64/[^"]+)"[^>]*>\s*<img[^>]*>\s*<span[^>]*>([^<]+)</span>', html)
            for path, title in games[:100]:
                entries.append(CatalogEntry(
                    source="textures-resource",
                    title=title.strip(),
                    url=f"{self.BASE}{path}",
                    category="n64_textures",
                ))
        except Exception as e:
            print(f"[Textures Resource] Error: {e}")
        print(f"[Textures Resource] Found {len(entries)} N64 texture sets")
        return entries


# =============================================================================
# N64 Textures (n64textures.com) — Hi-Res Texture Packs
# =============================================================================

class N64TexturesScraper:
    BASE = "https://www.n64textures.com"

    def get_texture_packs(self) -> List[CatalogEntry]:
        """Get Hi-Res texture packs."""
        entries = []
        try:
            resp = SESSION.get(f"{self.BASE}/downloads/", timeout=30)
            html = resp.text
            import re
            # Match pack links
            packs = re.findall(r'<a href="([^"]*\.zip|[^"]*\.rar|[^"]*\.7z)"[^>]*>([^<]+)</a>', html)
            for url, title in packs[:50]:
                entries.append(CatalogEntry(
                    source="n64textures.com",
                    title=title.strip(),
                    url=url if url.startswith("http") else f"{self.BASE}{url}",
                    category="texture_pack",
                ))
        except Exception as e:
            print(f"[N64Textures.com] Error: {e}")
        print(f"[N64Textures.com] Found {len(entries)} texture packs")
        return entries


# =============================================================================
# RomHacking.net — ROM hacks and utilities
# =============================================================================

class RomHackingDotNetScraper:
    BASE = "https://www.romhacking.net"

    def get_n64_hacks(self) -> List[CatalogEntry]:
        """Get N64 ROM hacks."""
        entries = []
        url = f"{self.BASE}/?page=hacks&platform=3"  # Platform 3 = N64
        try:
            resp = SESSION.get(url, timeout=30)
            html = resp.text
            import re
            hacks = re.findall(r'<a href="(/hacks/\d+/[^"]+)"[^>]*>([^<]+)</a>', html)
            for path, title in hacks[:100]:
                entries.append(CatalogEntry(
                    source="romhacking.net",
                    title=title.strip(),
                    url=f"{self.BASE}{path}",
                    category="rom_hack",
                ))
        except Exception as e:
            print(f"[RomHacking.net] Error: {e}")
        print(f"[RomHacking.net] Found {len(entries)} N64 ROM hacks")
        return entries


# =============================================================================
# Nexus Mods — GoldenEye 007 mods
# =============================================================================

class NexusModsScraper:
    BASE = "https://www.nexusmods.com"

    def get_goldeneye_mods(self) -> List[CatalogEntry]:
        """Get GoldenEye 007 mods."""
        entries = []
        url = f"{self.BASE}/goldeneye007/mods/"
        try:
            resp = SESSION.get(url, timeout=30)
            html = resp.text
            import re
            mods = re.findall(r'<a href="(/goldeneye007/mods/\d+)"[^>]*>([^<]+)</a>', html)
            for path, title in mods[:50]:
                entries.append(CatalogEntry(
                    source="nexusmods",
                    title=title.strip(),
                    url=f"{self.BASE}{path}",
                    category="mod",
                ))
        except Exception as e:
            print(f"[Nexus Mods] Error: {e}")
        print(f"[Nexus Mods] Found {len(entries)} GoldenEye mods")
        return entries


# =============================================================================
# n64.dev — Development resources
# =============================================================================

class N64DevScraper:
    BASE = "https://n64.dev"

    def get_tools(self) -> List[CatalogEntry]:
        """Get N64 development tools."""
        entries = []
        try:
            resp = SESSION.get(self.BASE, timeout=30)
            html = resp.text
            import re
            # Find tool/library links
            links = re.findall(r'<a href="(https?://[^"]*(?:github\.com|n64\.dev|libdragon)[^"]*)"[^>]*>([^<]+)</a>', html)
            for url, title in links[:50]:
                entries.append(CatalogEntry(
                    source="n64.dev",
                    title=title.strip(),
                    url=url,
                    category="dev_tool",
                ))
        except Exception as e:
            print(f"[N64.dev] Error: {e}")
        print(f"[N64.dev] Found {len(entries)} dev resources")
        return entries


# =============================================================================
# Emulation64.com — Texture packs
# =============================================================================

class Emulation64Scraper:
    BASE = "https://www.emulation64.com"

    def get_texture_packs(self) -> List[CatalogEntry]:
        """Get N64 texture packs."""
        entries = []
        url = f"{self.BASE}/files/category/20/119/nintendo-64-texture-packs.html/"
        try:
            resp = SESSION.get(url, timeout=30)
            html = resp.text
            import re
            packs = re.findall(r'<a href="(/files/download/[^"]+)"[^>]*>([^<]+)</a>', html)
            for path, title in packs[:50]:
                entries.append(CatalogEntry(
                    source="emulation64.com",
                    title=title.strip(),
                    url=f"{self.BASE}{path}",
                    category="texture_pack",
                ))
        except Exception as e:
            print(f"[Emulation64] Error: {e}")
        print(f"[Emulation64] Found {len(entries)} texture packs")
        return entries


# =============================================================================
# N64 Vault — Modding tools wiki
# =============================================================================

class N64VaultScraper:
    BASE = "http://www.n64vault.com"

    def get_tools(self) -> List[CatalogEntry]:
        """Get N64 modding tools."""
        entries = []
        try:
            resp = SESSION.get(self.BASE, timeout=30)
            html = resp.text
            import re
            tools = re.findall(r'<a href="([^"]*(?:setup-editor|tool|hack)[^"]*)"[^>]*>([^<]+)</a>', html)
            for path, title in tools[:50]:
                url = path if path.startswith("http") else f"{self.BASE}{path}"
                entries.append(CatalogEntry(
                    source="n64vault.com",
                    title=title.strip(),
                    url=url,
                    category="modding_tool",
                ))
        except Exception as e:
            print(f"[N64 Vault] Error: {e}")
        print(f"[N64 Vault] Found {len(entries)} tools")
        return entries


# =============================================================================
# MAIN ORCHESTRATOR
# =============================================================================

def run_all_scrapers(tcrf_categories: List[str] = None,
                     archive_queries: List[str] = None,
                     gamebanana_pages: int = 1,
                     github_queries: List[str] = None,
                     output_name: str = "catalog",
                     include_sources: List[str] = None) -> dict:
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
    if github_queries is None:
        github_queries = [
            "n64 modding",
            "n64 tools",
            "zelda 64",
            "ocarina of time decomp",
            "n64 decompilation",
        ]
    if include_sources is None:
        include_sources = ["all"]

    all_entries: List[CatalogEntry] = []
    run_all = "all" in include_sources

    # TCRF
    if run_all or "tcrf" in include_sources:
        tcrf = TCRFScraper()
        for cat in tcrf_categories:
            pages = tcrf.get_category_pages(cat, limit=200)
            if pages:
                titles = [p.title for p in pages[:50]]
                extracts = tcrf.get_page_extracts(titles)
                for p in pages:
                    p.description = extracts.get(p.title, "")
            all_entries.extend(pages)
            time.sleep(1)

    # Archive.org
    if run_all or "archive.org" in include_sources:
        archive = ArchiveOrgScraper()
        for q in archive_queries:
            items = archive.search(q, rows=100)
            all_entries.extend(items)
            time.sleep(1)

    # GameBanana
    if run_all or "gamebanana" in include_sources:
        gb = GameBananaScraper()
        for p in range(1, gamebanana_pages + 1):
            mods = gb.get_mods(game_id=7060, page=p)
            all_entries.extend(mods)
            time.sleep(1)

    # Spriters Resource
    if run_all or "spriters-resource" in include_sources:
        sr = SpritersResourceScraper()
        games = sr.get_n64_models()
        all_entries.extend(games)

    # GitHub
    if run_all or "github" in include_sources:
        gh = GitHubScraper()
        for q in github_queries:
            repos = gh.search_repos(q, limit=50)
            all_entries.extend(repos)
            time.sleep(1)

    # Models Resource
    if run_all or "models-resource" in include_sources:
        mr = ModelsResourceScraper()
        models = mr.get_n64_models()
        all_entries.extend(models)

    # Textures Resource
    if run_all or "textures-resource" in include_sources:
        tr = TexturesResourceScraper()
        textures = tr.get_n64_textures()
        all_entries.extend(textures)

    # N64Textures.com
    if run_all or "n64textures.com" in include_sources:
        nt = N64TexturesScraper()
        packs = nt.get_texture_packs()
        all_entries.extend(packs)

    # RomHacking.net
    if run_all or "romhacking.net" in include_sources:
        rh = RomHackingDotNetScraper()
        hacks = rh.get_n64_hacks()
        all_entries.extend(hacks)

    # Nexus Mods
    if run_all or "nexusmods" in include_sources:
        nx = NexusModsScraper()
        mods = nx.get_goldeneye_mods()
        all_entries.extend(mods)

    # N64.dev
    if run_all or "n64.dev" in include_sources:
        nd = N64DevScraper()
        tools = nd.get_tools()
        all_entries.extend(tools)

    # Emulation64.com
    if run_all or "emulation64.com" in include_sources:
        em = Emulation64Scraper()
        packs = em.get_texture_packs()
        all_entries.extend(packs)

    # N64 Vault
    if run_all or "n64vault.com" in include_sources:
        nv = N64VaultScraper()
        tools = nv.get_tools()
        all_entries.extend(tools)

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
    global CATALOG_PATH, DOWNLOAD_BASE
    parser = argparse.ArgumentParser(description="N64 Modding Metadata Scraper")
    parser.add_argument("--tcrf", nargs="+", default=["July_2020_Nintendo_Leak"], help="TCRF categories")
    parser.add_argument("--archive", nargs="+", default=["nintendo 64 prototype", "ocarina of time beta"], help="Archive.org queries")
    parser.add_argument("--github", nargs="+", default=["n64 modding", "n64 tools", "zelda 64"], help="GitHub queries")
    parser.add_argument("--gb-pages", type=int, default=1, help="GameBanana pages to scrape")
    parser.add_argument("--output", default="catalog", help="Output filename")
    parser.add_argument("--sources", nargs="+", default=["all"], 
                        help="Sources to scrape: all, tcrf, archive.org, gamebanana, github, spriters-resource, models-resource, textures-resource, n64textures.com, romhacking.net, nexusmods, n64.dev, emulation64.com, n64vault.com")
    args = parser.parse_args()

    run_all_scrapers(
        tcrf_categories=args.tcrf,
        archive_queries=args.archive,
        github_queries=args.github,
        gamebanana_pages=args.gb_pages,
        output_name=args.output,
        include_sources=args.sources,
    )


if __name__ == "__main__":
    main()
