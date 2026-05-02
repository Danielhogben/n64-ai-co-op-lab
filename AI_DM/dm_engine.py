"""AI Dungeon Master engine for N64 co-op adventures."""

import time
import random
import threading
import queue
from typing import Optional

try:
    import pyttsx3
    TTS_AVAILABLE = True
except Exception:
    TTS_AVAILABLE = False

from config import TTS_ENABLED, TTS_VOICE, TTS_RATE, CHALLENGE_INTERVAL_MIN, CHALLENGE_INTERVAL_MAX, DIFFICULTY_START, DIFFICULTY_MAX
from challenges import Challenge, pick_challenge
from soh_bridge import send_command, send_commands


class AIDungeonMaster:
    """The DM that watches, speaks, and torments the player with challenges."""

    def __init__(self):
        self.difficulty = DIFFICULTY_START
        self.active_challenge: Optional[Challenge] = None
        self.challenge_start_time: float = 0.0
        self.running = False
        self.tts = None
        self._speech_queue: queue.Queue[str] = queue.Queue()
        self._speech_thread: Optional[threading.Thread] = None
        self._challenge_thread: Optional[threading.Thread] = None
        self._setup_tts()

    def _setup_tts(self):
        if not TTS_ENABLED or not TTS_AVAILABLE:
            return
        try:
            self.tts = pyttsx3.init()
            self.tts.setProperty('rate', TTS_RATE)
            if TTS_VOICE:
                self.tts.setProperty('voice', TTS_VOICE)
            self._speech_thread = threading.Thread(target=self._speech_loop, daemon=True)
            self._speech_thread.start()
        except Exception as e:
            print(f"[DM] TTS init failed: {e}")
            self.tts = None

    def _speech_loop(self):
        while True:
            text = self._speech_queue.get()
            if text is None:
                break
            if self.tts:
                self.tts.say(text)
                self.tts.runAndWait()

    def speak(self, text: str):
        """Queue text for TTS and print it."""
        print(f"\n[DM] 🎲 {text}\n")
        if self.tts:
            self._speech_queue.put(text)

    def say_intro(self):
        self.speak(
            "Greetings, hero. I am your Dungeon Master. "
            "I have seen the Chaos of Time, the Sands that shift, and the Shadows of Eldoria. "
            "Together we shall forge a legend... or a tragedy. Let us begin."
        )

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
        if self._speech_thread:
            self._speech_queue.put(None)

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

        # Execute SoH commands
        if challenge.soh_commands:
            send_commands(challenge.soh_commands)

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
        enemies = ["2", "4", "14", "16", "20", "24", "28", "32"]
        count = random.randint(1, min(self.difficulty, 5))
        cmds = [f"spawn {random.choice(enemies)}" for _ in range(count)]
        send_commands(cmds)
        self.speak("An unexpected encounter! Draw your blade!")

    def grant_boon(self):
        """Random helpful reward."""
        boons = [
            ("heal", "heal"),
            ("rupees 50", "rupees 50"),
            ("give 0x5E", "give 0x5E"),  # Farore's Wind
            ("give 0x5F", "give 0x5F"),  # Nayru's Love
        ]
        cmd, desc = random.choice(boons)
        send_command(cmd)
        self.speak("A fairy smiles upon you. A boon is granted!")

    def curse_player(self):
        """Random harmful effect."""
        curses = [
            ("hurt 2", "hurt 2"),
            ("rupees -30", "rupees -30"),
            ("spawn 30", "spawn 30"),  # Wallmaster
            ("time 0", "time 0"),       # Midnight
        ]
        cmd, desc = random.choice(curses)
        send_command(cmd)
        self.speak("A dark curse takes hold! Misfortune follows!")

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
