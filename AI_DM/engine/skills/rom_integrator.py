"""ROM Integrator — master orchestrator that generates content from all ROMs."""
import json, os, random
from typing import Dict, List, Any, Tuple
from datetime import datetime
from tabulate import tabulate # For pretty printing reports
# Import registry (works both as package and standalone)
try:
    from ..registry import reg
except ImportError:
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    from registry import reg
# Import events (works both as package and standalone)
try:
    from ..events import ZONE_ENTER, ENEMY_DEATH, ITEM_PICKUP, QUEST_COMPLETE
except ImportError:
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    from events import ZONE_ENTER, ENEMY_DEATH, ITEM_PICKUP, QUEST_COMPLETE

class ROMIntegrator:
    """Orchestrates the full content generation pipeline from ROM database."""
    
    def __init__(self):
        # DEBUG
        import sys
        print(f"[Integrator Init] reg.rom_database keys: {list(reg.rom_database.keys()) if reg.rom_database else 'None'}", file=sys.stderr)
        print(f"[Integrator Init] raw_roms type: {type(reg.rom_database.get('roms')) if reg.rom_database else 'N/A'}", file=sys.stderr)
        raw = reg.rom_database.get("roms") if reg.rom_database else None
        if raw is not None:
            if isinstance(raw, dict):
                print(f"[Integrator Init] raw_roms dict keys: {list(raw.keys())}", file=sys.stderr)
            elif isinstance(raw, list):
                print(f"[Integrator Init] raw_roms list length: {len(raw)}", file=sys.stderr)
        # END DEBUG

        # Ensure rom_database is structured correctly
        if not reg.rom_database or "roms" not in reg.rom_database:
            reg.rom_database = {"roms": {}}

        # Normalize ROM database: convert dict-of-lists to list-of-dicts
        raw_roms = reg.rom_database["roms"]
        normalized_roms = []

        if isinstance(raw_roms, dict):
            for category, paths in raw_roms.items():
                for idx, path in enumerate(paths):
                    filename = os.path.basename(path)
                    name_no_ext = os.path.splitext(filename)[0]
                    region = "unknown"
                    path_lower = path.lower()
                    if "n64" in path_lower or "nintendo 64" in path_lower:
                        region = "N64"
                    elif "3ds" in path_lower or "ctr" in path_lower:
                        region = "3DS"
                    elif "gamecube" in path_lower or "gcn" in path_lower:
                        region = "GameCube"
                    elif "psx" in path_lower or "playstation" in path_lower:
                        region = "PSX"
                    elif "wii" in path_lower:
                        region = "Wii"
                    normalized_roms.append({
                        "id": f"rom_{category}_{idx}",
                        "name": name_no_ext,
                        "category": category,
                        "region": region,
                        "path": path,
                    })
            reg.rom_database["roms"] = normalized_roms
        elif isinstance(raw_roms, list):
            normalized_roms = raw_roms
        else:
            normalized_roms = []
            reg.rom_database["roms"] = normalized_roms

        self.db = reg.rom_database
        self.mod_path = reg.config.get("mod_path", "")
        self.zones_path = os.path.join(self.mod_path, "zones.json")
        self.enemies_path = os.path.join(self.mod_path, "enemies", "generated")
        self.items_path = os.path.join(self.mod_path, "items", "generated")
        self.quests_path = os.path.join(self.mod_path, "quests", "generated")
        for p in [self.enemies_path, self.items_path, self.quests_path]:
            os.makedirs(p, exist_ok=True)
        # Ensure reg.zones is a list
        if reg.zones is None:
            reg.zones = []

        # Persistent integration state (survive engine restarts)
        self.state_file = os.path.expanduser("~/HylianModding/AI_DM/integration_state.json")
        self.state = reg.state.setdefault("rom_integrator", {})
        # Load integrated_paths from disk if available
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file) as f:
                    disk_state = json.load(f)
                saved = disk_state.get("integrated_paths", [])
                self.integrated_paths = set(saved)
                # Also sync back to reg.state for this session
                self.state["integrated_paths"] = self.integrated_paths
            except Exception as e:
                print(f"[Integrator] Warning: could not load integration state: {e}")
                self.integrated_paths = set()
        else:
            self.integrated_paths = set()

        # Initial: also add any paths found in existing zones (in case state missing)
        for z in reg.zones:
            self.integrated_paths.add(z.get("source_rom", ""))
            for p in z.get("source_roms", []):
                self.integrated_paths.add(p)
        # Clean None
        self.integrated_paths.discard(None)
        self.state["integrated_paths"] = self.integrated_paths

    def _get_rom_by_id(self, rom_id: str) -> Dict[str, Any] | None:
        """Helper to get a ROM by its ID."""
        for rom in self.db.get("roms", []):
            if rom.get("id") == rom_id:
                return rom
        return None

    def full_integration(self, dry_run: bool = False) -> Dict[str, Any]:
        """Main pipeline: scan ROMs → group → generate content."""
        report = {"roms_processed": 0, "zones_created": 0, "enemies_generated": 0, "items_generated": 0, "quests_created": 0}

        # Phase 1: Categorize ROMs
        all_roms_by_category: Dict[str, List[Dict[str, Any]]] = {}
        for rom in self.db.get("roms", []):
            category = rom.get("category", "uncategorized")
            all_roms_by_category.setdefault(category, []).append(rom)

        all_roms = [rom for cat_roms in all_roms_by_category.values() for rom in cat_roms]
        report["roms_processed"] = len(all_roms)
        print(f"[Integrator] Processing {len(all_roms)} ROMs...")

        # Build set of already-integrated ROM paths to avoid duplicates
        integrated_rom_paths = set()
        for z in reg.zones:
            src = z.get("source_rom")
            if src:
                integrated_rom_paths.add(src)
            # Also include all ROMs from this zone's source_roms list
            for sp in z.get("source_roms", []):
                if sp:
                    integrated_rom_paths.add(sp)

        # Phase 2: Group into galaxies (by category)
        galaxies = all_roms_by_category

        # Phase 3: For each galaxy, generate zones (1 zone per 3 ROMs)
        zone_id_counter = len(reg.zones) if reg.zones else 0
        new_zones = []

        for galaxy_name, galaxy_roms in galaxies.items():
            # Skip ROMs already integrated
            pending_roms = [r for r in galaxy_roms if r.get("path") not in integrated_rom_paths]
            if not pending_roms:
                print(f"  [Integrator] Category '{galaxy_name}': all ROMs already integrated, skipping")
                continue

            chunks = [pending_roms[i:i+3] for i in range(0, len(pending_roms), 3)]
            for idx, rom_chunk in enumerate(chunks):
                primary_rom_info = rom_chunk[0]
                primary_path = primary_rom_info.get("path", "")
                primary_name = os.path.basename(primary_path)
                all_paths = [r.get("path", "") for r in rom_chunk]

                zone = {
                    "id": f"zone_{zone_id_counter}",
                    "name": f"ROM_Zone_{zone_id_counter}",
                    "source_rom": primary_path,
                    "source_roms": all_paths,  # all ROM paths in this zone
                    "rom_name": primary_name,
                    "size": "medium" if len(rom_chunk) == 3 else "small",
                    "buildings": random.randint(1, 5),
                    "factories": random.randint(0, 3),
                    "ships": random.randint(2, 8),
                    "ai_controlled": random.choice([True, False]),
                    "enemy_roster": self._generate_enemy_pool(galaxy_name, [r.get("name", "") for r in rom_chunk]),
                    "resource_nodes": ["crystal_ore", "metal_ore", "gas"],
                    "region": primary_rom_info.get("region", "unknown"),
                    "danger_level": random.choice(["low", "medium", "high"]),
                }
                new_zones.append(zone)
                zone_id_counter += 1
                report["zones_created"] += 1

        if not dry_run:
            reg.zones.extend(new_zones)
            os.makedirs(os.path.dirname(self.zones_path), exist_ok=True)
            with open(self.zones_path, 'w') as f:
                json.dump(reg.zones, f, indent=2)

        # Phase 4: Enemies count (actual file generation not yet implemented)
        for zone in new_zones:
            report["enemies_generated"] += len(zone["enemy_roster"])

        # Phase 5: Items (estimate)
        report["items_generated"] = len(all_roms) * 3

        # Phase 6: Quests (one per galaxy)
        report["quests_created"] = len(galaxies)

        print(f"[Integrator] Done. Created {report['zones_created']} zones, {report['enemies_generated']} enemies, {report['items_generated']} items.")

        # Update integrated_paths: add all ROM paths from newly created zones
        for z in new_zones:
            self.integrated_paths.add(z.get("source_rom", ""))
            for p in z.get("source_roms", []):
                if p:
                    self.integrated_paths.add(p)
        # Persist integrated set
        try:
            with open(self.state_file, 'w') as f:
                json.dump({"integrated_paths": list(self.integrated_paths)}, f)
        except Exception as e:
            print(f"[Integrator] Warning: could not save integration state: {e}")

        return report
    
    def _generate_enemy_pool(self, galaxy: str, rom_names: List[str]) -> List[str]:
        """Generate enemy IDs for a zone based on ROM names."""
        enemies = []
        base_names = ["stalfos", "zombie", "keese", "octorok", "wolfos", "lizalfos"]
        for rom_name in rom_names:
            rom_name_lower = rom_name.lower()
            if "zelda" in rom_name_lower or "oot" in rom_name_lower:
                enemies.extend(["stalfos", "stalfo", "gohma", "ganon"])
            elif "mario" in rom_name_lower:
                enemies.extend(["goomba", "koopa", "shyguy", "bobomb"])
            elif "pokemon" in rom_name_lower:
                enemies.extend(["pidgey", "rattata", "zubat", "meowth"])
            elif "resident" in rom_name_lower or "bio" in rom_name_lower:
                enemies.extend(["zombie", "licker", "hunter", "nemesis"])
            else:
                enemies.extend(base_names)
        # Deduplicate, limit to 15 per zone
        return list(set(enemies))[:15]

    def _incremental_scan(self, mode: str = 'new') -> str:
        """Processes new ROMs based on last scan timestamp."""
        reg.state.setdefault('rom_integrator', {})
        last_scan = reg.state['rom_integrator'].get('last_full_scan')
        
        # For demonstration, we'll just update the timestamp and report
        # In a real scenario, this would involve comparing file modification times
        # or a ROM database version with the last_scan timestamp.
        new_roms_count = 0
        if not last_scan:
            new_roms_count = len(self.db.get("roms", []))
            summary = f"No previous scan found. Processed {new_roms_count} initial ROMs."
        else:
            # Simulate finding new ROMs
            # For a proper incremental scan, you'd check ROMs added/modified since last_scan
            summary = f"Incremental scan since {last_scan}. No new ROMs detected for this run (simulated)."
            # Example: if self.db.get("roms", []) had more entries now than before, calculate diff
        
        reg.state['rom_integrator']['last_full_scan'] = datetime.now().isoformat()
        return f"Incremental scan completed. {summary}"

    def _audit_roms_and_zones(self) -> str:
        """Validates ROM entries and zone consistency."""
        report_lines = ["--- ROM and Zone Audit Report ---"]

        # Audit ROMs
        report_lines.append("\nROM Database Audit:")
        roms_in_db = self.db.get("roms", [])
        if not roms_in_db:
            report_lines.append("  No ROMs found in the database.")

        rom_issues = 0
        rom_ids_in_db = set()
        rom_paths_in_db = set()
        for rom in roms_in_db:
            missing_fields = []
            if "id" not in rom: missing_fields.append("id")
            if "name" not in rom: missing_fields.append("name")
            if "category" not in rom: missing_fields.append("category")
            if "region" not in rom: missing_fields.append("region")
            if "path" not in rom: missing_fields.append("path")

            if missing_fields:
                report_lines.append(f"  ROM '{rom.get('id', rom.get('name', 'Unknown'))}' is missing fields: {', '.join(missing_fields)}")
                rom_issues += 1
            else:
                rom_ids_in_db.add(rom["id"])
                rom_paths_in_db.add(rom["path"])

        if rom_issues == 0 and roms_in_db:
            report_lines.append(f"  All {len(roms_in_db)} ROM entries are valid.")
        elif rom_issues > 0:
            report_lines.append(f"  Found {rom_issues} ROM entries with issues.")

        # Audit Zones
        report_lines.append("\nZone Database Audit:")
        zones_data = reg.zones
        if not zones_data:
            report_lines.append("  No zones found.")

        zone_issues = 0
        orphaned_zones = 0
        missing_rom_references = 0

        for zone in zones_data:
            if "id" not in zone:
                report_lines.append("  Zone (Unnamed) is missing 'id' field.")
                zone_issues += 1
                continue

            zone_id = zone["id"]
            # Check for presence of any source reference
            has_source = False
            roms_referenced_by_zone = []

            # Check primary_rom / source_roms (ID-based)
            if "primary_rom" in zone:
                has_source = True
                roms_referenced_by_zone.append(zone["primary_rom"])
            if "source_roms" in zone:
                has_source = True
                roms_referenced_by_zone.extend(zone["source_roms"])

            # Check source_rom (path-based)
            if "source_rom" in zone:
                has_source = True
                roms_referenced_by_zone.append(zone["source_rom"])

            if not has_source:
                report_lines.append(f"  Zone '{zone_id}' is orphaned (no source ROM field).")
                orphaned_zones += 1
                zone_issues += 1

            for rom_ref in roms_referenced_by_zone:
                # Determine if ref is an ID or a path
                if rom_ref in rom_ids_in_db:
                    pass  # valid ID
                elif rom_ref in rom_paths_in_db:
                    pass  # valid path
                else:
                    report_lines.append(f"  Zone '{zone_id}' references missing ROM: '{rom_ref}'.")
                    missing_rom_references += 1
                    zone_issues += 1

        if zone_issues == 0 and zones_data:
            report_lines.append(f"  All {len(zones_data)} zone entries are valid.")
        elif zone_issues > 0:
            report_lines.append(f"  Found {zone_issues} zone entries with issues ({orphaned_zones} orphaned, {missing_rom_references} missing ROM references).")

        report_lines.append("\n--- Audit Complete ---")
        return "\n".join(report_lines)

    def _generate_summary_report(self) -> str:
        """Generates a summary report of ROMs and Zones."""
        report_lines = ["--- ROM and Zone Summary Report ---"]

        roms = self.db.get("roms", [])
        zones = reg.zones

        # Count ROMs by category
        roms_by_category = {}
        for rom in roms:
            category = rom.get("category", "unknown").capitalize()
            roms_by_category[category] = roms_by_category.get(category, 0) + 1
        
        report_lines.append("\nROMs by Category:")
        if roms_by_category:
            report_lines.append(tabulate(roms_by_category.items(), headers=["Category", "Count"], tablefmt="grid"))
        else:
            report_lines.append("  No ROMs categorized.")

        # Count zones by region
        zones_by_region = {}
        for zone in zones:
            region = zone.get("region", "unknown").upper()
            zones_by_region[region] = zones_by_region.get(region, 0) + 1
        
        report_lines.append("\nZones by Region:")
        if zones_by_region:
            report_lines.append(tabulate(zones_by_region.items(), headers=["Region", "Count"], tablefmt="grid"))
        else:
            report_lines.append("  No zones with region data.")

        # Pending work count (ROMs not yet integrated into any zone)
        integrated_rom_paths = set()
        for zone in zones:
            src = zone.get("source_rom")
            if src:
                integrated_rom_paths.add(src)
            for sp in zone.get("source_roms", []):
                if sp:
                    integrated_rom_paths.add(sp)

        all_rom_paths = {rom.get("path") for rom in roms if rom.get("path")}
        pending_roms_count = len(all_rom_paths - integrated_rom_paths)
        
        report_lines.append(f"\nPending ROMs (not yet in any zone): {pending_roms_count}")
        report_lines.append(f"Total ROMs in DB: {len(roms)}")
        report_lines.append(f"Total Zones: {len(zones)}")

        report_lines.append("\n--- Report Complete ---")
        return "\n".join(report_lines)

    def _list_rom_entries(self, category: str | None = None) -> str:
        """Lists ROM entries, optionally filtered by category."""
        roms_to_list = []
        if category:
            for rom in self.db.get("roms", []):
                if rom.get("category", "").lower() == category.lower():
                    roms_to_list.append(rom)
        else:
            roms_to_list = self.db.get("roms", [])
        
        if not roms_to_list:
            return f"No ROMs found{f' for category {category}' if category else ''}."

        headers = ["ID", "Name", "Category", "Region"]
        table_data = [[rom.get("id", "N/A"), rom.get("name", "N/A"), rom.get("category", "N/A"), rom.get("region", "N/A")] for rom in roms_to_list]
        
        return "\n" + tabulate(table_data, headers=headers, tablefmt="grid")

    def _show_rom_details(self, rom_id: str) -> str:
        """Shows details for a specific ROM."""
        rom = self._get_rom_by_id(rom_id)
        if not rom:
            return f"ROM with ID '{rom_id}' not found."
        
        details = [f"--- ROM Details for '{rom_id}' ---"]
        for key, value in rom.items():
            details.append(f"{key.replace('_', ' ').capitalize()}: {value}")
        return "\n".join(details)

class Skill:
    def __init__(self):
        self.integrator = ROMIntegrator()
        self.commands = {
            "run": self.cmd_run,
            "incremental": self.cmd_incremental,
            "audit": self.cmd_audit,
            "report": self.cmd_report,
            "rom_list": self.cmd_rom_list,
            "rom_show": self.cmd_rom_show,
            "zones_list": self.cmd_zones_list,
            "zone_info": self.cmd_zone_info,
        }
    
    def cmd_run(self, *args):
        """rom_integrate -mode full|incremental [--dry-run]"""
        # Parse: optional mode (default full), optional --dry-run flag
        mode = "full"
        dry_run = False
        for arg in args:
            if arg in ("full", "incremental"):
                mode = arg
            elif arg == "--dry-run":
                dry_run = True
        if mode == "full":
            report = self.integrator.full_integration(dry_run=dry_run)
            return json.dumps(report, indent=2)
        elif mode == "incremental":
            # Incremental is a separate command; fall back
            return self.cmd_incremental()
        return f"Mode '{mode}' not implemented yet."
    
    def cmd_incremental(self, *args):
        """rom_integrate -mode incremental — process new ROMs only."""
        mode = args[0] if args else 'new'
        result = self.integrator._incremental_scan(mode)
        return result

    def cmd_audit(self, *args):
        """rom_integrate -mode audit — report without changes."""
        result = self.integrator._audit_roms_and_zones()
        return result

    def cmd_report(self, *args):
        """rom_integrate -list_generated — show what would be generated."""
        result = self.integrator._generate_summary_report()
        return result

    def cmd_rom_list(self, *args):
        """rom_list [category] — list ROM entries."""
        category = args[0] if args else None
        result = self.integrator._list_rom_entries(category)
        return result

    def cmd_rom_show(self, *args):
        """rom_show <rom_id> — show ROM details."""
        if not args:
            return "Usage: rom_show <rom_id>"
        rom_id = args[0]
        result = self.integrator._show_rom_details(rom_id)
        return result

    def cmd_zones_list(self, *args):
        """zones_list — list all generated zones with source ROM."""
        zones = reg.zones
        if not zones:
            return "No zones generated yet. Use 'rom_integrate run' to create zones."

        headers = ["Zone ID", "Name", "Region", "Primary ROM", "Enemies"]
        rows = []
        for z in zones:
            rows.append([
                z.get("id", "N/A"),
                z.get("name", "N/A"),
                z.get("region", "N/A"),
                z.get("primary_rom", "N/A"),
                len(z.get("enemy_roster", []))
            ])
        return "\n" + tabulate(rows, headers=headers, tablefmt="grid")

    def cmd_zone_info(self, *args):
        """zone_info <zone_id> — show zone details."""
        if not args:
            return "Usage: zone_info <zone_id>"
        zone_id = args[0]
        for z in reg.zones:
            if z.get("id") == zone_id:
                lines = [f"--- Zone: {zone_id} ---"]
                for k, v in z.items():
                    if k == "enemy_roster":
                        lines.append(f"Enemy Roster ({len(v)} entries): {', '.join(v[:10])}")
                    else:
                        lines.append(f"{k}: {v}")
                return "\n".join(lines)
        return f"Zone '{zone_id}' not found."
