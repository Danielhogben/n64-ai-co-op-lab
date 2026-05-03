"""Dynamic skill loading and command dispatch."""
import importlib
import os
import sys
from typing import Dict, Callable

# Import registry using package-relative import when inside package,
# absolute import when run standalone
try:
    from .registry import reg
except ImportError:
    # Running as script directly from engine/ directory
    from registry import reg

class SkillLoader:
    def __init__(self):
        self.loaded_skills: Dict[str, Any] = {}
        self.command_map: Dict[str, Callable] = {}
        
    def load_skill(self, skill_name: str) -> bool:
        """Load a skill module from engine/skills/."""
        try:
            # Skills live in engine/skills/ as engine.skills.<name>
            module_name = f"engine.skills.{skill_name}"
            mod = importlib.import_module(module_name)
            skill = mod.Skill() if hasattr(mod, 'Skill') else mod
            # Register commands
            if hasattr(skill, 'commands'):
                for cmd_name, func in skill.commands.items():
                    full_cmd = f"{skill_name}.{cmd_name}"
                    self.command_map[full_cmd] = func
                    if cmd_name not in self.command_map:
                        self.command_map[cmd_name] = func
            # Register event hooks
            if hasattr(skill, 'hooks'):
                for event, callback in skill.hooks.items():
                    reg.on(event, callback)
            self.loaded_skills[skill_name] = skill
            print(f"[SkillLoader] Loaded skill: {skill_name}")
            return True
        except Exception as e:
            print(f"[SkillLoader] Failed to load {skill_name}: {e}")
            return False
    
    def dispatch(self, command_line: str, *args):
        """Parse and execute a command.
        
        Supports formats:
          <command>              — bare command (list, help, status)
          <skill> <command>      — prefixed: ship list, zone warp zone_1
          <skill>.<command>      — dotted: ship_management.list
        """
        parts = command_line.strip().split()
        if not parts:
            return "No command."
        
        # Try dotted form first: "ship_management.list"
        if '.' in parts[0]:
            skill_cmd = parts[0]
            if skill_cmd in self.command_map:
                return self.command_map[skill_cmd](*parts[1:])
            # Also try with args combined: "ship list" -> look for "ship.list"
            # handled below
        
        # Try two-part: "ship list"
        if len(parts) >= 2:
            # Check if first word is an alias for a loaded skill
            for skill_name in self.loaded_skills:
                if skill_name.split('_')[0] == parts[0]:  # 'ship' matches 'ship_management'
                    full_cmd = f"{skill_name}.{' '.join(parts[1:])}"
                    # But our command map uses underscores not spaces
                    alt_cmd = f"{skill_name}.{parts[1]}"
                    if alt_cmd in self.command_map:
                        return self.command_map[alt_cmd](*parts[2:])
        
        # Try bare command
        cmd = parts[0]
        if cmd in self.command_map:
            return self.command_map[cmd](*parts[1:])
        
        return f"Unknown command: {cmd}. Available: {list(sorted(self.command_map.keys()))}"
    def load_all_skills(self):
        """Load all skill modules from engine/skills/."""
        # Ensure engine package is on path
        ai_dm_root = os.path.expanduser("~/HylianModding/AI_DM")
        if ai_dm_root not in sys.path:
            sys.path.insert(0, ai_dm_root)
            
        skills_dir = os.path.join(os.path.dirname(__file__), "skills")
        if not os.path.exists(skills_dir):
            print(f"[SkillLoader] No skills directory at {skills_dir}")
            return
        
        print(f"[SkillLoader] Scanning {skills_dir}...")
        loaded = 0
        for fname in sorted(os.listdir(skills_dir)):
            if fname.endswith('.py') and not fname.startswith('_'):
                skill_name = fname[:-3]  # strip .py
                if self.load_skill(skill_name):
                    loaded += 1
        print(f"[SkillLoader] Loaded {loaded} skill modules")
