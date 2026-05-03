"""Dungeon Master System — bring the AI DM into the unified engine."""
import os, sys, time
from typing import Dict, List, Any

# Ensure project root is in path for imports from parent dir
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

try:
    from ..registry import reg
    from ..events import ENGINE_SECOND
except ImportError:
    from engine.registry import reg
    from engine.events import ENGINE_SECOND

try:
    from dm_engine import AIDungeonMaster
    from challenges import get_challenge_by_name
except ImportError:
    # Handle if running from different context
    sys.path.insert(0, os.path.expanduser("~/HylianModding/AI_DM"))
    from dm_engine import AIDungeonMaster
    from challenges import get_challenge_by_name

class DungeonMasterSkill:
    """Wraps the AIDungeonMaster for use within the unified engine."""
    
    def __init__(self):
        self.dm = AIDungeonMaster()
        self.campaign_active = False
        
        # Hooks
        self.hooks = {
            ENGINE_SECOND: self.on_engine_second
        }

    def on_engine_second(self, **data):
        """Tick the DM logic once per second if active."""
        if not self.campaign_active:
            return
        
        # The original DM uses its own campaign_loop thread, 
        # but we could eventually migrate it to this tick.
        # For now, we'll just check if it's running.
        pass

    def cmd_start(self, *args):
        """dm start — begin the AI Dungeon Master campaign."""
        if self.campaign_active:
            return "Campaign is already running!"
        
        self.dm.start_campaign()
        self.campaign_active = True
        return "🎲 AI Dungeon Master Campaign STARTED. Watch the SoH console for challenges!"

    def cmd_stop(self, *args):
        """dm stop — end the AI Dungeon Master campaign."""
        if not self.campaign_active:
            return "Campaign is not running."
        
        self.dm.stop_campaign()
        self.campaign_active = False
        return "Campaign ended. The world rests."

    def cmd_encounter(self, *args):
        """dm encounter — trigger a random enemy encounter immediately."""
        self.dm.spawn_random_encounter()
        return "🎲 Random encounter triggered!"

    def cmd_boon(self, *args):
        """dm boon — grant a random helpful reward."""
        self.dm.grant_boon()
        return "🎲 Fairy boon granted!"

    def cmd_curse(self, *args):
        """dm curse — inflict a random misfortune."""
        self.dm.curse_player()
        return "🎲 Dark curse inflicted!"

    def cmd_success(self, *args):
        """dm success — manually report challenge completion."""
        self.dm.report_success()
        return "🎲 Challenge reported as SUCCESS."

    def cmd_fail(self, *args):
        """dm fail — manually report challenge failure."""
        self.dm.report_fail()
        return "🎲 Challenge reported as FAILURE."

    def cmd_status(self, *args):
        """dm status — show current DM and challenge status."""
        info = self.dm.get_active_challenge_info()
        lines = [f"Dungeon Master: {'ACTIVE' if self.campaign_active else 'IDLE'}"]
        lines.append(f"Difficulty: {self.dm.difficulty}/10")
        
        if info:
            lines.append(f"Active Challenge: {info['name']}")
            lines.append(f"Time Remaining: {info['remaining']}s")
        else:
            lines.append("No active challenge.")
            
        return "\n".join(lines)

class Skill:
    def __init__(self):
        self.dms = DungeonMasterSkill()
        self.commands = {
            "start": self.dms.cmd_start,
            "stop": self.dms.cmd_stop,
            "encounter": self.dms.cmd_encounter,
            "boon": self.dms.cmd_boon,
            "curse": self.dms.cmd_curse,
            "success": self.dms.cmd_success,
            "fail": self.dms.cmd_fail,
            "status": self.dms.cmd_status,
        }
        self.hooks = self.dms.hooks
