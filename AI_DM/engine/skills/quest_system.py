"""Quest System Skill — accept, track, and complete missions across galaxies."""
import json
import os
import random
from typing import Dict, List, Any
try:
    from ..registry import reg
except ImportError:
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    from registry import reg

class QuestManager:
    """Manages quest lifecycle."""
    
    def __init__(self):
        self.quests_path = os.path.join(reg.config.get("mod_path", ""), "quests")
        os.makedirs(self.quests_path, exist_ok=True)
        
    def list_available(self, zone_id: str = None) -> List[Dict[str, Any]]:
        """List quests available for acceptance."""
        # For demo, generate random quests if none exist
        available = []
        # In real version, we'd read from self.quests_path / "available.json"
        # For now, let's create a few dummy ones
        templates = [
            {"id": "q_001", "name": "The Gohma Infestation", "desc": "Clear 10 Gohma from the Deku Spire.", "reward": 500, "difficulty": 2},
            {"id": "q_002", "name": "Triforce Shard Recovery", "desc": "Locate and retrieve the shard in the Fire Galaxy.", "reward": 2000, "difficulty": 5},
            {"id": "q_003", "name": "Nexus Upgrade", "desc": "Gather 5 Data Crystals for Nexus's AI core.", "reward": 1000, "difficulty": 3},
        ]
        return templates

    def accept_quest(self, quest_id: str) -> str:
        """Move quest to active list in player state."""
        state = reg.player_state
        active = state.setdefault("active_quests", [])
        
        # Check if already active
        if any(q["id"] == quest_id for q in active):
            return f"Quest {quest_id} is already active."
        
        # Find quest in available (mock)
        available = self.list_available()
        quest = next((q for q in available if q["id"] == quest_id), None)
        
        if not quest:
            return f"Quest {quest_id} not found."
        
        # Add to active
        quest["status"] = "in_progress"
        quest["progress"] = 0
        active.append(quest)
        return f"Accepted quest: {quest['name']}. Good luck!"

    def complete_quest(self, quest_id: str) -> str:
        """Complete a quest and grant rewards."""
        state = reg.player_state
        active = state.get("active_quests", [])
        
        quest = next((q for q in active if q["id"] == quest_id), None)
        if not quest:
            return f"Quest {quest_id} is not in your active list."
        
        # Remove from active
        state["active_quests"] = [q for q in active if q["id"] != quest_id]
        
        # Grant reward
        reward = quest.get("reward", 0)
        state["credits"] = state.get("credits", 0) + reward
        
        # Record as completed
        completed = state.setdefault("completed_quests", [])
        completed.append(quest_id)
        
        return f"Quest Completed: {quest['name']}! You received {reward} credits."

class Skill:
    """Quest System skill implementation."""
    
    def __init__(self):
        self.qm = QuestManager()
        self.commands = {
            "list": self.cmd_list,
            "accept": self.cmd_accept,
            "complete": self.cmd_complete,
            "active": self.cmd_active,
        }
    
    def cmd_list(self, *args):
        """quest list — Show available quests."""
        available = self.qm.list_available()
        lines = [f"{'ID':8} {'NAME':30} {'REWARD':8} {'DIF':3}"]
        for q in available:
            lines.append(f"{q['id']:8} {q['name']:30} {q['reward']:8} {q['difficulty']:3}")
        return "\n".join(lines)
    
    def cmd_accept(self, quest_id: str, *args):
        """quest accept <id> — Accept a new quest."""
        return self.qm.accept_quest(quest_id)
    
    def cmd_complete(self, quest_id: str, *args):
        """quest complete <id> — Turn in a completed quest."""
        return self.qm.complete_quest(quest_id)
    
    def cmd_active(self, *args):
        """quest active — Show currently tracked quests."""
        active = reg.player_state.get("active_quests", [])
        if not active:
            return "No active quests."
        lines = [f"{'ID':8} {'NAME':30} {'PROGRESS':8}"]
        for q in active:
            lines.append(f"{q['id']:8} {q['name']:30} {q['progress']}%")
        return "\n".join(lines)
