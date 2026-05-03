class ROMScanner:
    """Scans all sources: Library/ROMs, Downloads archives, 7z/zip/.part files."""
    
    def __init__(self):
        self.found_roms: List[Dict] = []
        self.bps_patches = []
        
    def scan_library(self):
        """Scan ~/HylianModding/Library/ROMs (flat directory of ROM files)."""
        count = 0
        for f in LIBRARY_ROMS.iterdir():
            if f.suffix.lower() in ['.z64', '.n64', '.v64', '.cia', '.gba', '.gbc', '.gb', '.nds', '.ds', '.3ds']:
                info = self._categorize(f.name)
                self.found_roms.append({
                    "path": str(f),
                    "filename": f.name,
                    "size_mb": f.stat().st_size / (1024*1024),
                    "source": "library_roms",
                    **info,
                })
                count += 1
        print(f"[Scanner] Library/ROMs: {count} ROMs")
    
    def scan_downloads_archives(self):
        """Scan Downloads for .zip, .7z, .rar split archives."""
        archives = list(DOWNLOADS.glob("*.zip")) + list(DOWNLOADS.glob("*.7z")) + list(DOWNLOADS.glob("*.rar"))
        print(f"[Scanner] Found {len(archives)} archives in Downloads")
        # In full mode, we queue these for extraction. Here we just catalog.
        for arc in archives:
            self.found_roms.append({
                "path": str(arc),
                "filename": arc.name,
                "size_mb": arc.stat().st_size / (1024*1024),
                "source": "downloads_archive",
                "format": arc.suffix[1:],
                "categorized": {"unknown": 1},
            })
    
    def scan_bps_patches(self):
        """Find all BPS patch files (29 known patches)."""
        for bps in BPS_PATCHES:
            self.bps_patches.append({
                "path": str(bps),
                "name": bps.name,
                "size_kb": bps.stat().st_size / 1024,
            })
        print(f"[Scanner] BPS patches: {len(self.bps_patches)}")
    
    def _categorize(self, filename: str) -> Dict[str, Any]:
        """Guess franchise/category from filename."""
        low = filename.lower()
        for franchise, keywords in FRANCHISE_PATTERNS.items():
            if any(kw in low for kw in keywords):
                return {"franchise": franchise, "console": self._detect_console(low)}
        return {"franchise": "unknown", "console": self._detect_console(low)}
    
    def _detect_console(self, name: str) -> str:
        if any(x in name for x in ['.z64', '.n64', '.v64']): return "n64"
        if '.cia' in name: return "3ds"
        if '.gba' in name: return "gba"
        if '.gbc' in name: return "gbc"
        if '.gb' in name: return "gb"
        if '.nds' in name or '.ds' in name: return "nds"
        if '.iso' in name: return "gamecube" if 'gc' in name else "wii"
        return "unknown"
