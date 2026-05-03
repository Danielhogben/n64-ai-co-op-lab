"""Main Engine: bootstraps all systems and runs game loop."""
import os, sys, json, time, threading

# Import engine modules with package-relative imports when inside package,
# but also support direct execution (python engine/main.py)
try:
    from .registry import reg
    from .clock import GameClock
    from .skill_loader import SkillLoader
    from .events import *
except ImportError:
    # Running directly from engine/ directory as script
    from registry import reg
    from clock import GameClock
    from skill_loader import SkillLoader
    from events import *

class Engine:
    def __init__(self, config_path=None):
        self.running = False
        self.clock = GameClock(tick_rate=60)
        self.skills = SkillLoader()
        self.config = self._load_config(config_path)
        self._setup()
        
    def _load_config(self, path):
        if path and os.path.exists(path):
            with open(path) as f:
                return json.load(f)
        return {
            "mod_path": os.path.expanduser("~/HylianModding/ShipOfHarkinian/mods/ai_full_universe"),
            "rom_database": os.path.expanduser("~/HylianModding/AI_DM/rom_database.json"),
            "save_interval": 300,  # 5 minutes
            "autosave": True
        }
    
    def _setup(self):
        """Initialize engine: load data files, skills, state."""
        # Make engine importable from any location
        engine_dir = os.path.dirname(os.path.abspath(__file__))
        ai_dm_dir = os.path.dirname(engine_dir)
        if ai_dm_dir not in sys.path:
            sys.path.insert(0, ai_dm_dir)
        
        # Set global registry config early so skills can access it
        reg.config = self.config
        
        print("\n" + "="*60)
        print("🚀 UNIVERSE ENGINE — Initializing")
        print("="*60)
        
        # Auto-update content if database missing or requested
        self._auto_update_content()
        
        # Load ROM database
        rom_db_path = self.config.get("rom_database")
        if os.path.exists(rom_db_path):
            with open(rom_db_path) as f:
                reg.rom_database = json.load(f)
            total = reg.rom_database.get("total_roms", 0)
            print(f"✓ ROM Database loaded: {total} ROMs")
        else:
            print("⚠ ROM database not found. Run scan_all_data.py first.")

        # Load zones
        zones_path = os.path.join(self.config["mod_path"], "zones.json")
        if os.path.exists(zones_path):
            with open(zones_path) as f:
                reg.zones = json.load(f)
            print(f"✓ Zones loaded: {len(reg.zones)} zones")

        # Load player state
        state_path = os.path.expanduser("~/HylianModding/AI_DM/current_state.json")
        if os.path.exists(state_path):
            with open(state_path) as f:
                reg.player_state = json.load(f)
            print(f"✓ Player state loaded: Level {reg.player_state.get('level',1)}")
        else:
            reg.player_state = {"level": 1, "xp": 0, "inventory": {"slots_total":30,"slots_used":0,"items":[]}, "credits": 1000}

        # Load skills from ~/.hermes/skills/
        print("\n[Engine] Loading skills...")
        self.skills.load_all_skills()
        print(f"[Engine] {len(self.skills.command_map)} commands available")

        # Register core engine commands
        self._register_engine_commands()

        # Initialize subsystems
        self._init_subsystems()

        print("\n" + "="*60)
        print("✅ ENGINE READY — Type 'help' for commands")
        print("="*60)

        # Run startup commands if they exist
        self._run_startup_commands()

    def _auto_update_content(self):
        """Automatically run scan and integration if DB is missing."""
        rom_db_path = self.config.get("rom_database")
        if not os.path.exists(rom_db_path):
            print("[Engine] ROM database not found. Performing automatic scan...")
            try:
                import subprocess
                # Run scanner
                subprocess.run([sys.executable, "scan_all_data.py"], cwd=os.path.dirname(rom_db_path), check=True, timeout=3600)
                # Run mod generator
                subprocess.run([sys.executable, "mega_open_world.py"], cwd=os.path.dirname(rom_db_path), check=True, timeout=3600)
                # Run integrator
                subprocess.run([sys.executable, "run_integration.py"], cwd=os.path.dirname(rom_db_path), check=True, timeout=3600)
                print("[Engine] Automatic content generation complete.")
            except Exception as e:
                print(f"[Engine] Automatic content generation failed: {e}")
        # NOTE: Do NOT load zones/state/skills here — they are loaded by _setup after ROM DB is ready.

    def _run_startup_commands(self):
        """Execute commands from startup.cmd in project root."""
        startup_path = os.path.expanduser("~/HylianModding/AI_DM/startup.cmd")
        if os.path.exists(startup_path):
            print(f"\n[Engine] Running startup commands from {startup_path}...")
            with open(startup_path, 'r') as f:
                for line in f:
                    cmd = line.strip()
                    if not cmd or cmd.startswith("#"):
                        continue
                    print(f"  > {cmd}")
                    result = self.skills.dispatch(cmd)
                    if result:
                        print(f"    {result}")
            print("[Engine] Startup commands complete.\n")
    
    def _register_engine_commands(self):
        """Core engine commands (always available)."""
        self.skills.command_map.update({
            "help": self.cmd_help,
            "status": self.cmd_status,
            "save": self.cmd_save,
            "quit": self.cmd_quit,
            "reload_skills": self.cmd_reload_skills,
            "engine_stats": self.cmd_stats,
        })
    
    def _init_subsystems(self):
        """Initialize major subsystems (world, economy, combat, etc.)."""
        # For now, just print status — actual subsystem init will happen lazily
        # when their first command is called (deferred init for speed)
        pass
    
    # ─── Core commands ───
    def cmd_help(self, *args):
        lines = [
            "Universe Engine — Available command categories:",
            "  ship       — Ship management (ship list, ship info, swap parts)",
            "  zone       — Navigation (zones_list, warp_set, zone_info)",
            "  factory    — Production (factory_list, factory_start, collect)",
            "  base       — Building (base_build, base_upgrade, base_list)",
            "  ai         — Companion (ai_status, ai_ability, ai_quest_hint)",
            "  pokemon    — Creatures (pokemon list, pokemon capture, pokemon evolve)",
            "  reputation — Factions (reputation list, reputation add)",
            "  quest      — Missions (quest_board, quest_accept, quest_track)",
            "  inv        — Inventory (inv_list, inv_add, inv_transfer)",
            "  combat     — Battle (spawn, kill, enemy_info, loot)",
            "  economy    — Trade (market_list, buy, credits)",
            "  rom        — ROM tools (rom_run, rom_report, rom_audit)",
            "  test       — Validation (test zones, test enemies, test perf)",
            "  pentest    — Security (hardware_glitch, exploit)",
            "  engine     — Engine control (status, save, quit, reload_skills)",
            "",
            "Tip: Use '<category> <command> --help' for args (e.g., 'ship list --help')",
            "Or 'help <topic>' for detailed skill docs (e.g., 'help ship_management')"
        ]
        return "\n".join(lines)
    
    def cmd_status(self, *args):
        s = reg.player_state
        lines = [
            f"Player: Level {s.get('level',1)} — {s.get('xp',0)} / {s.get('xp_to_next',100)} XP",
            f"Credits: {s.get('credits',0)} | HP: {s.get('current_hp',0)} / {s.get('max_hp',0)}",
            f"Zones discovered: {len(s.get('zones_visited',[]))} | Ships owned: {len(s.get('ships_owned',[]))}",
            f"Active zone: {s.get('current_zone','none')}",
            f"Skills loaded: {len(self.skills.loaded_skills)}",
        ]
        if args and args[0] == "--full":
            lines.append(f"Full state: {json.dumps(s, indent=2)}")
        return "\n".join(lines)
    
    def cmd_save(self, *args):
        slot = args[0] if args else "auto"
        state_path = os.path.expanduser("~/HylianModding/AI_DM/current_state.json")
        with open(state_path, 'w') as f:
            json.dump(reg.player_state, f, indent=2)
        return f"✓ Game saved to slot '{slot}'."
    
    def cmd_quit(self, *args):
        self.running = False
        return "Engine shutting down. Save on exit."
    
    def cmd_reload_skills(self, *args):
        """Reload all skill modules (dev only)."""
        self.skills.loaded_skills.clear()
        self.skills.command_map.clear()
        self.skills.load_all_skills()
        return f"Skills reloaded. {len(self.skills.command_map)} commands loaded."
    
    def cmd_stats(self, *args):
        lines = [
            "Engine Statistics:",
            f"  Skills loaded: {len(self.skills.loaded_skills)}",
            f"  Commands registered: {len(self.skills.command_map)}",
            f"  Event handlers: {sum(len(h) for h in reg.event_handlers.values())}",
            f"  Entities in registry: {len(reg.entities)}",
            f"  Zones: {len(reg.zones)}",
            f"  ROMs cataloged: {reg.rom_database.get('total_roms',0)}",
        ]
        return "\n".join(lines)
    
    # ─── Main loop ───
    def run(self):
        """Start the engine main loop."""
        self.running = True
        self.clock.start()
        
        # Start subsystems (zone manager, combat, etc.)
        self._start_subsystems()
        
        print("\n[Engine] Main loop started. Press Ctrl+C to exit.")
        try:
            while self.running:
                if self.clock.tick():
                    self._tick()
                time.sleep(0.001)  # tiny sleep to yield
        except KeyboardInterrupt:
            print("\n[Engine] Shutting down...")
            self.running = False
    
    def _start_subsystems(self):
        """Start background threads / subsystems."""
        # Nothing critical needed for demo
        pass
    
    def _tick(self):
        """One game tick (60Hz)."""
        if not hasattr(self, 'ticks'):
            self.ticks = 0
            self.last_autosave = time.time()
            
        self.ticks += 1
        
        # Fire a 1Hz update event
        if self.ticks % 60 == 0:
            reg.emit("engine.second", tick=self.ticks)
            
            # Autosave logic
            now = time.time()
            if self.config.get("autosave", True) and (now - self.last_autosave) > self.config.get("save_interval", 300):
                self.cmd_save("auto")
                self.last_autosave = now
                print("\n[Engine] Game autosaved.")

def main():
    import argparse
    import threading
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", help="Path to engine config.yaml")
    args = parser.parse_args()
    
    engine = Engine(config_path=args.config)
    
    # Run the engine loop in a background daemon thread
    engine_thread = threading.Thread(target=engine.run, daemon=True)
    engine_thread.start()
    
    # Give the engine thread a moment to print its startup text
    time.sleep(0.1)
    
    # Interactive REPL in the main thread (only if interactive)
    if sys.stdin.isatty():
        print("\nEnter commands. Type 'help' for list, 'quit' to exit.")
        try:
            while engine.running:
                line = input("engine> ").strip()
                if not line: continue
                
                if line == "quit":
                    print(engine.cmd_quit())
                    break
                    
                result = engine.skills.dispatch(line)
                if result:
                    print(result)
        except (KeyboardInterrupt, EOFError):
            print(engine.cmd_quit())
        except Exception as e:
            print(f"Error: {e}")
            engine.running = False
    else:
        # Background mode: just wait for engine to stop
        print("\n[Engine] Running in background mode.")
        try:
            while engine.running:
                time.sleep(1)
        except KeyboardInterrupt:
            engine.running = False
        
    engine_thread.join(timeout=2.0)
    print("Exited.")

if __name__ == "__main__":
    main()
