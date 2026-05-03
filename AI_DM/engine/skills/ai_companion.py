"""AI Companion Skill — manage Nexus AI companion."""
import json, os, time, random
from typing import Dict, List, Any
try:
    from ..registry import reg
except ImportError:
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    from registry import reg
try:
    from ..events import AI_SPEAK, LEVEL_UP, ZONE_ENTER, ENGINE_SECOND
except ImportError:
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    from events import AI_SPEAK, LEVEL_UP, ZONE_ENTER, ENGINE_SECOND

class AISkillCore:
    """Manages Nexus AI companion: mood, abilities, quest hints."""
    
    def __init__(self):
        # Ensure player_state has mood and cooldowns
        self.state = reg.player_state
        self.state.setdefault('nexus_mood', 50)  # 0-100
        self.state.setdefault('ability_cooldowns', {})
        self.state.setdefault('tracked_quest', None)
        # Register event hooks
        self.hooks = {
            LEVEL_UP: self.on_levelup,
            ZONE_ENTER: self.on_zone_enter,
            ENGINE_SECOND: self.on_engine_second,
        }
        # Define abilities and their cooldown seconds
        self.abilities = {
            'heal': {'cooldown': 60, 'desc': 'Heal player for 50 HP'},
            'scan': {'cooldown': 30, 'desc': 'Scan current zone for points of interest'},
            'translate': {'cooldown': 120, 'desc': 'Translate alien text'},
            'summon_pokemon': {'cooldown': 180, 'desc': 'Summon a Pokemon ally'},
            'analyze': {'cooldown': 45, 'desc': 'Analyze enemy weakness'},
        }
    
    # ── Event hooks ──
    def on_engine_second(self, **data):
        """Randomly comment occasionally."""
        if random.random() < 0.02:  # 2% chance per second to say something
            messages = [
                "Nexus: Systems optimal.",
                "Nexus: I'm picking up anomalous readings nearby.",
                "Nexus: Don't forget to track your active quests.",
                "Nexus: Shield generators are operating at standard capacity.",
                "Nexus: Feeling good about our progress!"
            ]
            msg = random.choice(messages)
            # Use carriage return/newline trick so it prints nicely over the REPL prompt
            print(f"\n{msg}\nengine> ", end="", flush=True)
    def on_levelup(self, **data):
        """Mood increases on level up."""
        mood = self.state.get('nexus_mood', 50) + 10
        self.state['nexus_mood'] = min(100, mood)
        reg.emit(AI_SPEAK, message="Level up! I'm feeling more confident.")
    
    def on_zone_enter(self, zone_id=None, **data):
        """Mood adjustments based on zone danger level."""
        mood = self.state.get('nexus_mood', 50)
        # Look up zone danger
        zones = reg.zones
        danger = 'medium'
        for z in zones:
            if z.get('id') == zone_id:
                danger = z.get('danger_level', 'medium')
                break
        if danger == 'low':
            mood += 5
        elif danger == 'high':
            mood -= 10
        self.state['nexus_mood'] = max(0, min(100, mood))
    
    # ── Commands ──
    def cmd_status(self, *args):
        """ai_status — show Nexus status, mood, cooldowns."""
        mood = self.state.get('nexus_mood', 50)
        cds = self.state.get('ability_cooldowns', {})
        lines = [
            f"Nexus AI — Mood: {mood}/100",
            f"Tracked quest: {self.state.get('tracked_quest', 'none')}",
            "Abilities:",
        ]
        for ab, info in self.abilities.items():
            ready = "ready"
            if ab in cds:
                remaining = int(cds[ab] - time.time())
                if remaining > 0:
                    ready = f"cooldown {remaining}s"
                else:
                    del cds[ab]
            lines.append(f"  {ab}: {info['desc']} — {ready}")
        return "\n".join(lines)
    
    def cmd_say(self, *args):
        """ai_say <message> — make Nexus speak."""
        if not args:
            return "Nexus: ..."
        msg = " ".join(args).strip('"')
        reg.emit(AI_SPEAK, message=msg)
        return f'Nexus says: "{msg}"'

    
    def cmd_ability(self, ability: str, target: str = None, *args):
        """ai_ability <ability> [target] — use an ability."""
        cds = self.state.setdefault('ability_cooldowns', {})
        now = time.time()
        if ability not in self.abilities:
            return f"Unknown ability: {ability}. Available: {', '.join(self.abilities)}"
        # Check cooldown
        if ability in cds and now < cds[ability]:
            return f"{ability} on cooldown ({int(cds[ability]-now)}s remaining)"
        # Apply ability effect
        effect = ""
        if ability == 'heal':
            amount = 50
            cur = reg.player_state.get('current_hp', 0)
            max_hp = reg.player_state.get('max_hp', 100)
            new = min(max_hp, cur + amount)
            reg.player_state['current_hp'] = new
            effect = f"Healed {new-cur} HP."
        elif ability == 'scan':
            effect = "Scanning zone... (no immediate effect)"
        elif ability == 'translate':
            effect = "Translating unknown glyphs... (simulated)"
        elif ability == 'summon_pokemon':
            effect = "Summoned a Pokemon ally!"
        elif ability == 'analyze':
            effect = "Analyzing enemies... (simulated)"
        else:
            effect = "Ability used."
        # Set cooldown
        cds[ability] = now + self.abilities[ability]['cooldown']
        reg.emit(AI_SPEAK, message=f"Used {ability}!")
        return f"Nexus uses {ability} on {target + ' ' if target else ''}— {effect}"
    
    def cmd_quest_hint(self, *args):
        """ai_quest_hint — provide hint for current tracked quest."""
        quest_id = self.state.get('tracked_quest')
        if not quest_id:
            return "No quest being tracked. Use 'quest_track <id>' first."
        # Load quest if exists
        quests_dir = os.path.join(reg.config.get('mod_path', ''), 'quests', 'generated')
        qfile = os.path.join(quests_dir, f"{quest_id}.json")
        if not os.path.exists(qfile):
            return f"Tracked quest {quest_id} data not found."
        with open(qfile) as f:
            quest = json.load(f)
        # Generate simple hint based on objective
        obj = quest.get('objectives', [{}])[0]
        otype = obj.get('type')
        target = obj.get('target')
        count = obj.get('count')
        prog = reg.player_state.get('quest_progress', {}).get(quest_id, {})
        # Assuming single objective index 0
        current = prog.get('0', 0) if isinstance(prog, dict) else 0
        if otype == 'kill':
            return f"Hint: Find and defeat {target} enemies. Need {max(0, count - current)} more."
        elif otype == 'collect':
            return f"Hint: Collect {target} items. Need {max(0, count - current)} more."
        else:
            return f"Quest goal: {quest.get('description','No description')}"

class Skill:
    def __init__(self):
        self.ai = AISkillCore()
        self.commands = {
            "ai_status": self.ai.cmd_status,
            "ai_say": self.ai.cmd_say,
            "ai_ability": self.ai.cmd_ability,
            "ai_quest_hint": self.ai.cmd_quest_hint,
        }
        self.hooks = self.ai.hooks
