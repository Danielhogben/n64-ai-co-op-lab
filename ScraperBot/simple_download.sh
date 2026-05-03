#!/bin/bash
# Simple N64 Asset Downloader
# Downloads from cataloged URLs using wget

CATALOG="/home/donn/HylianModding/ScraperBot/outputs/n64_all_sources.json"
DEST_BASE="/home/donn/HylianModding/Assets/Downloads"

echo "[Downloader] Loading catalog..."
total=$(jq '.entries | length' "$CATALOG")
echo "[Downloader] Found $total entries"

# Download from Archive.org
echo "[Archive.org] Downloading..."
jq -r '.entries[] | select(.source=="archive.org") | .extra.identifier' "$CATALOG" | head -5 | while read id; do
    [ -z "$id" ] && continue
    echo "  Fetching metadata for $id..."
    curl -s "https://archive.org/metadata/$id" | jq -r '.files[] | select(.name | endswith(".zip") or endswith(".txt") or endswith(".png")) | .name' | head -2 | while read fname; do
        echo "    Downloading $fname..."
        wget -q -P "$DEST_BASE/archive.org/$id" "https://archive.org/download/$id/$fname" 2>/dev/null &
    done
done
wait

# Download from GameBanana
echo "[GameBanana] Downloading..."
jq -r '.entries[] | select(.source=="gamebanana") | .url' "$CATALOG" | head -5 | while read url; do
    [ -z "$url" ] && continue
    mod_id=$(basename "$url")
    echo "  Fetching mod $mod_id..."
    curl -s "https://gamebanana.com/apiv11/Mod/$mod_id/Files" | jq -r '.[0]._sDownloadUrl' 2>/dev/null | sed 's/\\//g' | while read dl_url; do
        [ -z "$dl_url" ] && continue
        echo "    Downloading from $dl_url..."
        wget -q -P "$DEST_BASE/gamebanana" "$dl_url" 2>/dev/null &
    done
done
wait

# Download from GitHub
echo "[GitHub] Downloading..."
jq -r '.entries[] | select(.source=="github" or .source=="n64.dev") | .url' "$CATALOG" | head -5 | while read url; do
    [ -z "$url" ] && continue
    echo "  Fetching release from $url..."
    repo=$(echo "$url" | grep -oP 'github\.com/\K[^/]+/[^/]+')
    [ -z "$repo" ] && continue
    curl -s "https://api.github.com/repos/$repo/releases/latest" | jq -r '.assets[] | select(.name | endswith(".zip") or endswith(".tar.gz")) | .browser_download_url' | head -1 | while read dl_url; do
        [ -z "$dl_url" ] && continue
        fname=$(basename "$dl_url")
        echo "    Downloading $fname..."
        wget -q -P "$DEST_BASE/github/$repo" "$dl_url" 2>/dev/null &
    done
done
wait

echo "[Downloader] Done! Files saved to: $DEST_BASE"
