#!/usr/bin/env python3
"""
N64 Modding Asset Downloader
============================
Downloads free community assets, mods, and tools from cataloged sources.

Respects copyright:
- NO ROM downloads
- NO copyrighted game content
- ONLY mods, tools, open-source projects, and community assets
"""

import os
import json
import time
import argparse
from pathlib import Path
from urllib.parse import urlparse

import requests

SESSION = requests.Session()
SESSION.headers.update({
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
})

CATALOG_PATH = os.path.expanduser("~/HylianModding/ScraperBot/outputs/n64_all_sources.json")
DOWNLOAD_BASE = os.path.expanduser("~/HylianModding/Assets/Downloads")


def load_catalog() -> list:
    """Load catalog entries."""
    with open(CATALOG_PATH) as f:
        data = json.load(f)
    return data.get("entries", [])


def safe_filename(name: str) -> str:
    """Sanitize filename."""
    import re
    return re.sub(r'[<>:"/\\|?*]', '_', name)[:100]


def download_file(url: str, dest: str, max_size_mb: int = 500) -> bool:
    """Download file with size limit."""
    try:
        resp = SESSION.head(url, timeout=5, allow_redirects=True)
        size = int(resp.headers.get("content-length", 0))
        if size > max_size_mb * 1024 * 1024:
            print(f"  [Skip] Too large: {size / 1024 / 1024:.1f}MB")
            return False

        os.makedirs(os.path.dirname(dest), exist_ok=True)
        with SESSION.get(url, stream=True, timeout=30) as r:
            r.raise_for_status()
            with open(dest, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        print(f"  [OK] {os.path.basename(dest)}")
        return True
    except Exception as e:
        print(f"  [Error] {e}")
        return False


def download_archive_org(entries: list, dest_dir: str):
    """Download from Archive.org (tools, mods, open assets only)."""
    os.makedirs(dest_dir, exist_ok=True)
    count = 0
    for entry in entries:
        if entry["source"] != "archive.org":
            continue
        if count >= 5:  # Limit for testing
            break

        identifier = entry.get("extra", {}).get("identifier", "")
        if not identifier:
            continue

        # Get download links
        try:
            url = f"https://archive.org/metadata/{identifier}"
            resp = SESSION.get(url, timeout=10)
            data = resp.json()
            files = data.get("files", [])

            # Filter: only download safe file types
            safe_exts = {".zip", ".7z", ".tar.gz", ".txt", ".md", ".json", ".png", ".jpg"}
            for f in files[:2]:  # Max 2 files per item
                fname = f.get("name", "")
                ext = os.path.splitext(fname)[1]
                if ext.lower() in safe_exts:
                    dl_url = f"https://archive.org/download/{identifier}/{fname}"
                    dest = os.path.join(dest_dir, safe_filename(entry["title"]), fname)
                    if download_file(dl_url, dest, max_size_mb=100):  # Limit to 100MB
                        count += 1
                    time.sleep(0.5)
        except Exception as e:
            print(f"  [Archive.org] Error: {e}")

    print(f"[Archive.org] Downloaded {count} files")


def download_gamebanana(entries: list, dest_dir: str):
    """Download mods from GameBanana."""
    os.makedirs(dest_dir, exist_ok=True)
    count = 0
    for entry in entries:
        if entry["source"] != "gamebanana":
            continue
        if count >= 5:
            break

        url = entry.get("url", "")
        if not url:
            continue

        try:
            mod_id = url.rstrip("/").split("/")[-1]
            if not mod_id.isdigit():
                continue

            api_url = f"https://gamebanana.com/apiv11/Mod/{mod_id}/Files"
            resp = SESSION.get(api_url, timeout=10)
            if resp.status_code != 200:
                continue

            files = resp.json()
            if not isinstance(files, list):
                continue

            for f in files[:1]:
                if not isinstance(f, dict):
                    continue
                dl_url = f.get("_sDownloadUrl", "").replace("\\/", "/")
                fname = f.get("_sFile", "mod_file")
                if dl_url and dl_url.startswith("http"):
                    dest = os.path.join(dest_dir, safe_filename(entry["title"]), fname)
                    print(f"  Downloading {fname}...", flush=True)
                    if download_file(dl_url, dest, max_size_mb=100):
                        count += 1
                    time.sleep(1)
        except Exception as e:
            print(f"  [GameBanana] Error: {e}")

    print(f"[GameBanana] Downloaded {count} files")


def download_github_releases(entries: list, dest_dir: str):
    """Download release assets from GitHub repos."""
    os.makedirs(dest_dir, exist_ok=True)
    count = 0
    seen_repos = set()

    for entry in entries:
        if entry["source"] not in ("github", "n64.dev"):
            continue
        if count >= 10:
            break

        # Parse repo from URL
        url = entry.get("url", "")
        if "github.com" not in url:
            continue
        parts = url.rstrip("/").split("/")
        if len(parts) < 2:
            continue
        repo = f"{parts[-2]}/{parts[-1]}"
        if repo in seen_repos:
            continue
        seen_repos.add(repo)

        try:
            api_url = f"https://api.github.com/repos/{repo}/releases/latest"
            resp = SESSION.get(api_url, timeout=30)
            if resp.status_code != 200:
                continue

            release = resp.json()
            assets = release.get("assets", [])
            for asset in assets[:2]:  # Max 2 assets per release
                dl_url = asset.get("browser_download_url", "")
                fname = asset.get("name", "asset")
                # Only download safe file types
                ext = os.path.splitext(fname)[1]
                if ext.lower() in {".zip", ".tar.gz", ".tar.xz", ".deb", ".rpm", ".exe", ".py", ".js"}:
                    dest = os.path.join(dest_dir, safe_filename(repo), fname)
                    if download_file(dl_url, dest):
                        count += 1
                    time.sleep(1)
        except Exception as e:
            print(f"  [GitHub] Error: {e}")

    print(f"[GitHub] Downloaded {count} release assets")


def download_n64vault_tools(entries: list, dest_dir: str):
    """Download tools from N64 Vault."""
    os.makedirs(dest_dir, exist_ok=True)
    count = 0

    for entry in entries:
        if entry["source"] != "n64vault.com":
            continue
        if count >= 10:
            break

        url = entry.get("url", "")
        if not url:
            continue

        try:
            # N64 Vault links to external tools (GitHub, RomHacking.net, etc.)
            if "github.com" in url:
                # Extract repo and get releases
                parts = url.rstrip("/").split("/")
                if len(parts) >= 2:
                    repo = f"{parts[-2]}/{parts[-1]}"
                    api_url = f"https://api.github.com/repos/{repo}/releases/latest"
                    resp = SESSION.get(api_url, timeout=30)
                    if resp.status_code == 200:
                        release = resp.json()
                        assets = release.get("assets", [])
                        for asset in assets[:1]:
                            dl_url = asset.get("browser_download_url", "")
                            fname = asset.get("name", "tool")
                            dest = os.path.join(dest_dir, safe_filename(entry["title"]), fname)
                            if download_file(dl_url, dest):
                                count += 1
                            time.sleep(1)
            elif "romhacking.net" in url:
                # RomHacking.net has direct download links
                resp = SESSION.get(url, timeout=30)
                if resp.status_code == 200:
                    import re
                    links = re.findall(r'<a href="(/downloads/[^"]+)"', resp.text)
                    for link in links[:1]:
                        dl_url = f"https://www.romhacking.net{link}"
                        fname = link.split("/")[-1]
                        dest = os.path.join(dest_dir, safe_filename(entry["title"]), fname)
                        if download_file(dl_url, dest):
                            count += 1
                        time.sleep(1)
        except Exception as e:
            print(f"  [N64 Vault] Error: {e}")

    print(f"[N64 Vault] Downloaded {count} tools")


def main():
    global CATALOG_PATH, DOWNLOAD_BASE
    parser = argparse.ArgumentParser(description="N64 Asset Downloader")
    parser.add_argument("--catalog", default=CATALOG_PATH, help="Catalog JSON file")
    parser.add_argument("--dest", default=DOWNLOAD_BASE, help="Download directory")
    parser.add_argument("--source", choices=["archive.org", "gamebanana", "github", "n64vault.com", "all"],
                        default="all", help="Source to download from")
    parser.add_argument("--limit", type=int, default=5, help="Max downloads per source")
    args = parser.parse_args()

    CATALOG_PATH = args.catalog
    DOWNLOAD_BASE = args.dest

    entries = load_catalog()
    print(f"[Downloader] Loaded {len(entries)} catalog entries")

    if args.source in ("archive.org", "all"):
        download_archive_org(entries, os.path.join(DOWNLOAD_BASE, "archive.org"))
        time.sleep(1)

    if args.source in ("gamebanana", "all"):
        download_gamebanana(entries, os.path.join(DOWNLOAD_BASE, "gamebanana"))
        time.sleep(1)

    if args.source in ("github", "all"):
        download_github_releases(entries, os.path.join(DOWNLOAD_BASE, "github"))

    if args.source in ("n64vault.com", "all"):
        download_n64vault_tools(entries, os.path.join(DOWNLOAD_BASE, "n64vault"))

    print(f"\n[Downloader] Done. Files saved to: {DOWNLOAD_BASE}")


if __name__ == "__main__":
    main()
