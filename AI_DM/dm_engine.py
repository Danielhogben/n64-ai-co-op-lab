"""AI Dungeon Master engine for N64 co-op adventures."""

import time
import random
import threading
from typing import Optional

# Advanced TTS
try:
    from kitten_tts_provider import KittenTTSProvider
    KITTEN_AVAILABLE = True
except ImportError:
    KITTEN_AVAILABLE = False

# Legacy TTS as fallback
try:
    import pyttsx3
    LEGACY_TTS_AVAILABLE = True
except Exception:
    LEGACY_TTS_AVAILABLE = False

# Advanced Bridge
try:
    from sail_bridge import SailBridge
    SAIL_AVAILABLE = True
except ImportError:
    SAIL_AVAILABLE = False

from config import TTS_ENABLED, TTS_VOICE, TTS_RATE, CHALLENGE_INTERVAL_MIN, CHALLENGE_INTERVAL_MAX, DIFFICULTY_START, DIFFICULTY_MAX, CURRENT_GAME
from challenges import Challenge, pick_challenge
import soh_bridge
from storyteller import Storyteller

class AIDungeonMaster:
    """The DM that watches, speaks, and torments the player with challenges."""

    def __init__(self):
        self.difficulty = DIFFICULTY_START
        self.active_challenge: Optional[Challenge] = None
        self.challenge_start_time: float = 0.0
        self.running = False
        self.tts = None
        self.bridge = None
        self.game = CURRENT_GAME
        self.storyteller = Storyteller()
        self._setup_tts()
        self._setup_bridge()

    def _setup_tts(self):
        if not TTS_ENABLED:
            return
        
        if KITTEN_AVAILABLE:
            try:
                print("[DM] Initializing KittenTTS...")
                self.tts = KittenTTSProvider()
                return
            except Exception as e:
                print(f"[DM] KittenTTS init failed: {e}")

        if LEGACY_TTS_AVAILABLE:
            try:
                print("[DM] Falling back to Legacy TTS...")
                self.tts = pyttsx3.init()
                self.tts.setProperty('rate', TTS_RATE)
                if TTS_VOICE:
                    self.tts.setProperty('voice', TTS_VOICE)
            except Exception as e:
                print(f"[DM] Legacy TTS init failed: {e}")

    def _setup_bridge(self):
        if SAIL_AVAILABLE:
            print("[DM] Initializing SailBridge...")
            self.bridge = SailBridge()
            if not self.bridge.connect():
                print("[DM] Sail server not reachable. Falling back to keypress bridge.")
                self.bridge = None

    def _send_command(self, cmd: str):
        if self.bridge:
            self.bridge.send_command(cmd)
        else:
            soh_bridge.send_command(cmd, game=self.game)

    def _send_commands(self, commands: list[str]):
        if self.bridge:
            self.bridge.send_commands(commands)
        else:
            soh_bridge.send_commands(commands, game=self.game)

    def speak(self, text: str, event_type: Optional[str] = None, context: str = ""):
        """Queue text for TTS and print it. If event_type is provided, use Storyteller."""
        if event_type:
            text = self.storyteller.generate_dialogue(event_type, context)
            
        print(f"\n[DM] 🎲 {text}\n")
        if self.tts:
            if hasattr(self.tts, 'speak'):  # KittenTTSProvider
                self.tts.speak(text)
            else:  # Legacy pyttsx3
                def _legacy_speak():
                    self.tts.say(text)
                    self.tts.runAndWait()
                threading.Thread(target=_legacy_speak, daemon=True).start()

    def say_intro(self):
        self.speak(
            "Greetings, hero. I am your Dungeon Master. "
            "I have seen the Chaos of Time, the Sands that shift, and the Shadows of Eldoria. "
            "Together we shall forge a legend... or a tragedy. Let us begin."
        )

    def wait_for_tts(self):
        """Wait until all TTS speech has finished playing."""
        if self.tts and hasattr(self.tts, 'wait'):
            self.tts.wait()
        else:
            time.sleep(0.5)

    def say_status(self):
        self.speak(
            f"Current difficulty is {self.difficulty} out of {DIFFICULTY_MAX}. "
            f"The world grows {'kinder' if self.difficulty < 4 else 'crueler' if self.difficulty > 7 else 'unpredictable'} with each trial."
        )

    def start_campaign(self):
        """Begin the endless challenge loop."""
        self.running = True
        self.say_intro()
        self._challenge_thread = threading.Thread(target=self._campaign_loop, daemon=True)
        self._challenge_thread.start()

    def stop_campaign(self):
        self.running = False
        self.speak("The campaign pauses. Rest, hero. The world will wait... but not forever.")
        if hasattr(self.tts, 'stop'):
            self.tts.stop()

    def _campaign_loop(self):
        while self.running:
            wait = random.randint(CHALLENGE_INTERVAL_MIN, CHALLENGE_INTERVAL_MAX)
            time.sleep(wait)
            if not self.running:
                break
            self._launch_challenge()

    def _launch_challenge(self):
        challenge = pick_challenge(difficulty=self.difficulty)
        self.active_challenge = challenge
        self.challenge_start_time = time.time()

        self.speak(challenge.dm_intro)
        print(f"[DM] Challenge: {challenge.name} ({challenge.category}, diff {challenge.difficulty})")
        print(f"[DM] Description: {challenge.description}")
        print(f"[DM] Duration: {challenge.duration_sec}s")

        # Execute commands
        if challenge.soh_commands:
            self._send_commands(challenge.soh_commands)

        # Start challenge timer thread
        timer = threading.Thread(target=self._challenge_timer, args=(challenge,), daemon=True)
        timer.start()

    def _challenge_timer(self, challenge: Challenge):
        time.sleep(challenge.duration_sec)
        if self.active_challenge == challenge and self.running:
            # Time's up — assume failure unless player reports success manually
            self.speak(challenge.dm_fail)
            self._adjust_difficulty(success=False)
            self.active_challenge = None

    def report_success(self):
        """Call this when the player completes the active challenge."""
        if self.active_challenge:
            self.speak(self.active_challenge.dm_success)
            self._adjust_difficulty(success=True)
            self.active_challenge = None
        else:
            self.speak("There is no active challenge to complete... but I admire your enthusiasm.")

    def report_fail(self):
        """Call this when the player explicitly gives up or dies."""
        if self.active_challenge:
            self.speak(self.active_challenge.dm_fail)
            self._adjust_difficulty(success=False)
            self.active_challenge = None

    def _adjust_difficulty(self, success: bool):
        if success:
            self.difficulty = min(self.difficulty + 1, DIFFICULTY_MAX)
            self.speak(f"You grow stronger. Difficulty rises to {self.difficulty}.")
        else:
            self.difficulty = max(self.difficulty - 1, 1)
            self.speak(f"The world takes pity. Difficulty falls to {self.difficulty}.")

    def spawn_random_encounter(self):
        """Instant random combat event."""
        from config import ENEMIES
        game_enemies = list(ENEMIES.get(self.game, {}).values())
        if not game_enemies:
            game_enemies = ["1", "2", "4"]
            
        count = random.randint(1, min(self.difficulty, 5))
        cmds = [f"spawn {random.choice(game_enemies)}" for _ in range(count)]
        self._send_commands(cmds)
        self.speak("", event_type="encounter", context=f"{count} enemies spawned")

    def grant_boon(self):
        """Random helpful reward."""
        from config import ITEMS
        game_items = ITEMS.get(self.game, {})
        boons = [
            ("heal", "heal"),
            ("rupees 50", "rupees 50"),
        ]
        if game_items:
            random_item = random.choice(list(game_items.values()))
            boons.append((f"give {random_item}", f"give {random_item}"))
            
        cmd, desc = random.choice(boons)
        self._send_command(cmd)
        self.speak("", event_type="boon", context=desc)

    def curse_player(self):
        """Random harmful effect."""
        curses = [
            ("hurt 2", "hurt 2"),
            ("rupees -30", "rupees -30"),
            ("time 0", "time 0"),
        ]
        if self.game == "oot":
            curses.append(("spawn 30", "spawn 30"))
            
        cmd, desc = random.choice(curses)
        self._send_command(cmd)
        self.speak("", event_type="curse", context=desc)

    def get_active_challenge_info(self) -> Optional[dict]:
        if not self.active_challenge:
            return None
        elapsed = time.time() - self.challenge_start_time
        remaining = max(0, self.active_challenge.duration_sec - int(elapsed))
        return {
            "name": self.active_challenge.name,
            "description": self.active_challenge.description,
            "remaining": remaining,
            "difficulty": self.active_challenge.difficulty,
            "category": self.active_challenge.category,
        }
