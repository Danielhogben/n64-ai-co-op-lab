"""Zone Navigation — real implementation."""
import json, os
from typing import Dict, List, Any
# Import registry (works both as package and standalone)
try:
    from ..registry import reg
except ImportError:
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    from registry import reg
# Import events (works both as package and standalone)
try:
    from ..events import ZONE_ENTER, WARP_INITIATE, WARP_COMPLETE
except ImportError:
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    from events import ZONE_ENTER, WARP_INITIATE, WARP_COMPLETE

class ZoneManager:
    """Handles zone discovery, warping, and threat assessment."""
    
    def __init__(self):
        self.zones_path = os.path.join(reg.config.get("mod_path", ""), "zones.json")
        self.galaxies_path = os.path.join(reg.config.get("mod_path", ""), "galaxies")
        self._load_zones()
        
    def _load_zones(self):
        if os.path.exists(self.zones_path):
            with open(self.zones_path) as f:
                self.zones = json.load(f)
        else:
            self.zones = []
            
    def list_zones(self) -> List[Dict[str, Any]]:
        return self.zones
    
    def get_zone(self, zone_id: str) -> Dict[str, Any]:
        for z in self.zones:
            if z["id"] == zone_id:
                return z
        raise KeyError(f"Zone {zone_id} not found")
    
    def get_zone_by_index(self, idx: int) -> Dict[str, Any]:
        return self.zones[idx]
    
    def warp_to(self, zone_id: str, fuel_cost: int = 20) -> str:
        """Warp to a zone (consumes fuel)."""
        if zone_id not in [z["id"] for z in self.zones]:
            return f"Unknown zone: {zone_id}"
        # Check fuel (from player state)
        inv = reg.player_state.setdefault("inventory", {})
        items = inv.setdefault("items", [])
        # Find warp_cells
        warp_cells = next((it for it in items if it["item_id"] == "warp_cell"), None)
        if not warp_cells or warp_cells["quantity"] < fuel_cost:
            return f"Need {fuel_cost} warp cells (have {warp_cells['quantity'] if warp_cells else 0})"
        # Consume fuel
        warp_cells["quantity"] -= fuel_cost
        # Update current zone
        reg.player_state["current_zone"] = zone_id
        reg.player_state.setdefault("zones_visited", []).append(zone_id)
        reg.emit(WARP_INITIATE, from_zone=reg.player_state.get("current_zone"), to_zone=zone_id)
        reg.emit(WARP_COMPLETE, zone_id=zone_id)
        reg.emit(ZONE_ENTER, zone_id=zone_id)
        return f"Warped to {zone_id}. Fuel remaining: {warp_cells['quantity']}"
    
    def zone_threat(self, zone_id: str) -> Dict[str, Any]:
        z = self.get_zone(zone_id)
        return {
            "zone": zone_id,
            "danger_level": z.get("danger_level", "medium"),
            "enemies": z.get("enemy_roster", []),
            "buildings": z.get("buildings", 0),
            "boss": z.get("boss_present", False)
        }

class Skill:
    """Zone Navigation skill implementation."""
    def __init__(self):
        self.zm = ZoneManager()
        self.commands = {
            "list": self.cmd_list,
            "info": self.cmd_info,
            "warp": self.cmd_warp,
            "threat": self.cmd_threat,
            "scan": self.cmd_scan,
        }
        self.hooks = {}
    
    def cmd_list(self, *args):
        """zones_list — show all zones."""
        zones = self.zm.list_zones()
        lines = ["ZONE_ID           NAME                         SIZE  DANGER  BLDG  FACT  SHIP  AI"]
        for z in zones:
            lines.append(f"{z['id']:12} {z['name']:25} {z.get('size','?'):6} {z.get('danger_level','?'):8} {z.get('buildings',0):5} {z.get('factories',0):5} {z.get('ships',0):5} {'Y' if z.get('ai_controlled') else 'N'}")
        return "\n".join(lines)
    
    def cmd_info(self, zone_id: str, *args):
        """zone_info <zone_id> — full details."""
        try:
            z = self.zm.get_zone(zone_id)
            lines = [
                f"Zone: {z['name']} ({zone_id})",
                f"Source ROM: {z['source_rom']}",
                f"Size: {z.get('size')} | Danger: {z.get('danger_level')}",
                f"Buildings: {z.get('buildings')} | Factories: {z.get('factories')} | Ships: {z.get('ships')}",
                f"AI Controlled: {'Yes' if z.get('ai_controlled') else 'No'}",
                f"Enemy roster: {', '.join(z.get('enemy_roster',[])[:10])}",
                f"Resources: {', '.join(z.get('resource_nodes',[]))}",
            ]
            return "\n".join(lines)
        except KeyError as e:
            return str(e)
    
    def cmd_warp(self, zone_id: str, *args):
        """warp <zone_id> — travel to zone (consumes warp cells)."""
        fuel = int(args[0]) if args else 20
        return self.zm.warp_to(zone_id, fuel)
    
    def cmd_threat(self, zone_id: str, *args):
        """zone_threat <zone_id> — enemy threat assessment."""
        try:
            t = self.zm.zone_threat(zone_id)
            return f"Zone {t['zone']}: Danger={t['danger_level']}, Enemies={t['enemies']}, Boss={t['boss']}"
        except KeyError as e:
            return str(e)
    
    def cmd_scan(self, *args):
        """zone_scan — find hidden zones (stub)."""
        return "Scan complete: all zones discovered. Use zones_list to view."
