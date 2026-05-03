"""Challenge database focused on N64 and 3DS themes."""

import random
from dataclasses import dataclass
from typing import Callable, Optional
from config import CURRENT_GAME


@dataclass
class Challenge:
    name: str
    description: str
    difficulty: int          # 1-10
    category: str            # combat, exploration, puzzle, survival, chaos, transformation
    duration_sec: int        # how long the player has
    soh_commands: list[str]  # commands to execute
    dm_intro: str            # what the DM says to introduce it
    dm_success: str          # what the DM says on success
    dm_fail: str             # what the DM says on fail
    check_success: Optional[Callable] = None


# Helper to get the right IDs based on the current game
def g_id(game, type, key):
    from config import ENEMIES, ITEMS
    if type == "enemy":
        return ENEMIES.get(game, {}).get(key, "1")
    elif type == "item":
        return ITEMS.get(game, {}).get(key, "0x0")
    return key

CHALLENGES: list[Challenge] = [
    # -- N64 CORE CHALLENGES --
    Challenge(
        name="Ticking Clock",
        description="Defeat enemies before the sun sets.",
        difficulty=3,
        category="combat",
        duration_sec=120,
        soh_commands=["time 18", f"spawn {g_id(CURRENT_GAME, 'enemy', 'skulltula')}"],
        dm_intro="The N64 clocks are ticking. You have until sunset to prove your worth!",
        dm_success="The clocks fall silent. You have bested time itself.",
        dm_fail="Time claims all. The crystals shatter into dust.",
    ),
    Challenge(
        name="Midnight Sprint",
        description="Reach a safe zone before midnight strikes.",
        difficulty=4,
        category="exploration",
        duration_sec=90,
        soh_commands=["time 23", "speed 1.5"],
        dm_intro="Run, hero, run before the N64 shadows swallow you whole!",
        dm_success="You escaped the witching hour. For now.",
        dm_fail="The bell tolls twelve. Shadows swallow you whole.",
    ),
    Challenge(
        name="Demon's Gauntlet",
        description="Survive a wave of demons without healing.",
        difficulty=6,
        category="survival",
        duration_sec=180,
        soh_commands=[f"spawn {g_id(CURRENT_GAME, 'enemy', 'redead')}", "cheat invincible off"],
        dm_intro="A portal to the N64 Demon Realm opens! Survive or perish!",
        dm_success="The demons bow to your strength. The gate seals shut.",
        dm_fail="The demons feast upon your courage.",
    ),
]

# Add 3DS themed challenges (Note: These are mostly for the "world travel" logic or if we add a 3DS bridge)
CHALLENGES.extend([
    Challenge(
        name="StreetPass Shadow",
        description="A shadow of another player appears. Defeat them!",
        difficulty=5,
        category="combat",
        duration_sec=180,
        soh_commands=[f"spawn {g_id(CURRENT_GAME, 'enemy', 'dark_link' if CURRENT_GAME=='oot' else 'garo')}"],
        dm_intro="A StreetPass signal! Your shadow reflection has crossed over!",
        dm_success="The signal fades. The reflection is gone.",
        dm_fail="You have been bested by a ghost of another world.",
    ),
    Challenge(
        name="Stereoscopic Chaos",
        description="Reality shifts in and out of focus.",
        difficulty=4,
        category="chaos",
        duration_sec=60,
        soh_commands=["speed 2.0", "weather rain"], # Placeholder for "shift"
        dm_intro="The 3D depth slider is malfunctioning! Hold steady!",
        dm_success="Reality stabilizes.",
        dm_fail="You fell through the cracks of the third dimension.",
    ),
])

if CURRENT_GAME == "mm":
    CHALLENGES.extend([
        Challenge(
            name="Lunar Fall",
            description="The moon is falling! Survive the final 60 seconds.",
            difficulty=10,
            category="survival",
            duration_sec=60,
            soh_commands=["time 6", "weather storm", f"spawn {g_id('mm', 'enemy', 'majora')}"],
            dm_intro="Dawn of the Final Day. The Moon is falling! Survive Majora's final gambit!",
            dm_success="The moon disappears. A new day begins.",
            dm_fail="You met with a terrible fate, didn't you?",
        ),
    ])

def pick_challenge(difficulty: int = 0, category: Optional[str] = None) -> Challenge:
    pool = CHALLENGES
    if category:
        pool = [c for c in pool if c.category == category]
    if difficulty > 0:
        pool = [c for c in pool if abs(c.difficulty - difficulty) <= 2]
    if not pool:
        pool = CHALLENGES
    return random.choice(pool)

def get_challenge_by_name(name: str) -> Optional[Challenge]:
    for c in CHALLENGES:
        if c.name.lower() == name.lower():
            return c
    return None

import os
import json

# --- GAMEFORGE INTEGRATION ---
# Only load GameForge outputs that are Zelda-themed.
_SKIP_FORGE_KEYWORDS = ["nuclearmon", "stellarmon", "pokemon", "pallet", "rad-rattata"]
FORGE_OUTPUTS = os.path.expanduser("~/HylianModding/GameForge/outputs")
if os.path.exists(FORGE_OUTPUTS):
    for f in os.listdir(FORGE_OUTPUTS):
        if not f.endswith(".json"):
            continue
        if any(kw in f.lower() for kw in _SKIP_FORGE_KEYWORDS):
            continue
            
        try:
            with open(os.path.join(FORGE_OUTPUTS, f), "r") as jf:
                data = json.load(jf)
                
                if "concept" in f:
                    for i, ch in enumerate(data.get("chapters", [])):
                        diff = min(3 + i, 10)
                        boss = ch.get("boss", "Unknown Boss")
                        title = ch.get("title", "Unknown")
                        summary = ch.get("summary", "")
                        loc = ch.get("location", "the unknown")
                        
                        c = Challenge(
                            name=f"{data['title']} - {title}",
                            description=f"Defeat {boss}. {summary}",
                            difficulty=diff,
                            category="gameforge_story",
                            duration_sec=300,
                            soh_commands=[f"spawn {g_id(CURRENT_GAME, 'enemy', 'iron_knuckle')}"],
                            dm_intro=f"Entering {loc}... {summary}",
                            dm_success=f"You have cleared {title}!",
                            dm_fail=f"You have fallen in {title}."
                        )
                        CHALLENGES.append(c)
                        
                elif "crossover" in f:
                    for i, phase in enumerate(data.get("phases", [])):
                        p_name = phase.get("name", "Unknown Phase")
                        p_desc = phase.get("description", "")
                        c = Challenge(
                            name=f"Big Bang Phase {i+1}: {p_name}",
                            description=p_desc,
                            difficulty=min(5 + i, 10),
                            category="chaos",
                            duration_sec=240,
                            soh_commands=["speed 2.0", f"spawn {g_id(CURRENT_GAME, 'enemy', 'dark_link')}"],
                            dm_intro=f"The crossover begins! Phase {i+1}: {p_name}. {p_desc}",
                            dm_success=f"Phase {i+1} complete. The timelines hold.",
                            dm_fail="The paradox consumes you."
                        )
                        CHALLENGES.append(c)
        except Exception as e:
            print(f"[GameForge Load Error] {f}: {e}")

