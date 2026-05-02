"""Challenge database inspired by the user's ROM hack collection."""

import random
from dataclasses import dataclass
from typing import Callable, Optional


@dataclass
class Challenge:
    name: str
    description: str
    difficulty: int          # 1-10
    category: str            # combat, exploration, puzzle, survival, chaos, transformation
    duration_sec: int        # how long the player has
    soh_commands: list[str]  # commands to execute
    dm_intro: str            # what the DM says to introduce it
    dm_success: str          # what the DM says on success (manual trigger)
    dm_fail: str             # what the DM says on fail (manual trigger)
    check_success: Optional[Callable] = None  # future: automated win detection


# ---------------------------------------------------------------------------
# CHALLENGE POOL — generated from ROM hack themes
# ---------------------------------------------------------------------------

CHALLENGES: list[Challenge] = [
    # -- CRYSTAL CLOCKS (time-based) --
    Challenge(
        name="Ticking Clock",
        description="Defeat 5 enemies before the sun sets.",
        difficulty=3,
        category="combat",
        duration_sec=120,
        soh_commands=["time 18", "spawn 24"],
        dm_intro="The Crystal Clocks have started to tick. You have until sunset to prove your worth!",
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
        dm_intro="The Sands of Time pour faster. Run, hero, run before midnight claims you!",
        dm_success="You escaped the witching hour. For now.",
        dm_fail="The bell tolls twelve. Shadows swallow you whole.",
    ),

    # -- DEMON'S QUEST (dungeon combat) --
    Challenge(
        name="Demon's Gauntlet",
        description="Survive a wave of demons without healing.",
        difficulty=6,
        category="survival",
        duration_sec=180,
        soh_commands=["spawn 33", "spawn 32", "spawn 28", "cheat invincible off"],
        dm_intro="A portal to the Demon Realm opens! No healing — survive or perish!",
        dm_success="The demons bow to your strength. The gate seals shut.",
        dm_fail="The demons feast upon your courage. Try again, mortal.",
    ),
    Challenge(
        name="Iron Trial",
        description="Defeat an Iron Knuckle using only your sword.",
        difficulty=7,
        category="combat",
        duration_sec=300,
        soh_commands=["spawn 40", "remove 0x4A", "remove 0x4E", "remove 0x51"],
        dm_intro="An Iron Knuckle blocks your path. Steel yourself — only blade against blade!",
        dm_success="The armor crumbles. You are worthy of the Master Sword.",
        dm_fail="The knuckle's axe rings true. You are not yet ready.",
    ),

    # -- OoT CHAOS (random effects) --
    Challenge(
        name="Chaos Surge",
        description="Survive 60 seconds of chaos effects.",
        difficulty=5,
        category="chaos",
        duration_sec=60,
        soh_commands=[
            "speed 2.0", "spawn 22", "rupees -50",
            "weather rain", "spawn 1", "spawn 1"
        ],
        dm_intro="The Chaos Mod awakens! Reality bends — survive the surge!",
        dm_success="Order is restored. You tamed the chaos.",
        dm_fail="Chaos consumes all. The world laughs at your attempt.",
    ),
    Challenge(
        name="Rupee Roulette",
        description="Keep your rupee count above zero while enemies steal them.",
        difficulty=4,
        category="survival",
        duration_sec=120,
        soh_commands=["rupees 10", "spawn 2", "spawn 2", "spawn 2"],
        dm_intro="The Chaos spirits hunger for your wealth. Guard your rupees with your life!",
        dm_success="Your purse remains heavy. Greed is your ally today.",
        dm_fail="Bankrupt! The spirits dance on your empty pockets.",
    ),

    # -- ULTIMATE TRIAL (trials / boss rushes) --
    Challenge(
        name="Trial of Fire",
        description="Defeat a Dodongo without using bombs.",
        difficulty=6,
        category="combat",
        duration_sec=300,
        soh_commands=["spawn 18", "remove 0x65", "remove 0x6A"],
        dm_intro="The first Trial beckons — slay the Dodongo without explosives!",
        dm_success="The beast falls to raw skill. The Trial is complete.",
        dm_fail="Fire and failure. Return when you are stronger.",
    ),
    Challenge(
        name="Trial of Shadows",
        description="Navigate darkness with only your lens.",
        difficulty=5,
        category="exploration",
        duration_sec=180,
        soh_commands=["time 0", "weather dark", "give 0x50", "remove 0x3E", "remove 0x3F", "remove 0x40"],
        dm_intro="Shadows of Eldoria surround you. Trust only the Lens of Truth!",
        dm_success="Light pierces the dark. You see what others cannot.",
        dm_fail="Lost in the abyss. The shadows whisper your name.",
    ),

    # -- SANDS OF TIME (time manipulation) --
    Challenge(
        name="Time Loop",
        description="Complete a task before time rewinds.",
        difficulty=8,
        category="puzzle",
        duration_sec=45,
        soh_commands=["speed 3.0", "spawn 14"],
        dm_intro="The Sands of Time flow backward! Act before the hourglass turns!",
        dm_success="You broke the loop. Time marches forward once more.",
        dm_fail="The sands reset. You are trapped in eternity.",
    ),

    # -- TRANSFORMATION MASKS (form shifting) --
    Challenge(
        name="Masked Warrior",
        description="Fight as a Deku Scrub — no sword, no shield.",
        difficulty=7,
        category="transformation",
        duration_sec=240,
        soh_commands=[
            "remove 0x3B", "remove 0x3C", "remove 0x3E",
            "remove 0x3F", "remove 0x40", "spawn 4"
        ],
        dm_intro="A Mask falls upon your face! You are no longer Link — you are something else!",
        dm_success="The mask slips away. You have mastered the form.",
        dm_fail="The mask controls you. You are merely a puppet.",
    ),

    # -- MAJORA'S MASK CHAOS (MM effects on OoT) --
    Challenge(
        name="Moon's Wrath",
        description="Survive under the crushing pressure of the moon.",
        difficulty=9,
        category="chaos",
        duration_sec=120,
        soh_commands=[
            "time 5", "spawn 32", "spawn 33", "spawn 31",
            "hurt 2", "rupees -99", "weather storm"
        ],
        dm_intro="The Moon descends! Majora's chaos infects this world! SURVIVE!",
        dm_success="The moon retreats. You have defied apocalypse.",
        dm_fail="Dawn never comes. The moon smiles upon your defeat.",
    ),

    # -- MASTER OF TIME REVISITED (time travel / new areas) --
    Challenge(
        name="Paradox Duel",
        description="Defeat your past self — a Dark Link clone.",
        difficulty=8,
        category="combat",
        duration_sec=300,
        soh_commands=["spawn 51", "remove 0x5F", "remove 0x5E"],
        dm_intro="A rift in time opens — your dark reflection steps forth! Defeat yourself!",
        dm_success="The paradox resolves. You are whole once more.",
        dm_fail="You have been bested by yourself. How ironic.",
    ),

    # -- SHADOWS OF ELDORIA (dark fantasy) --
    Challenge(
        name="Eldorian Night",
        description="Survive a night in Eldoria with no map.",
        difficulty=5,
        category="exploration",
        duration_sec=300,
        soh_commands=["time 0", "no_ui on", "spawn 30", "spawn 24"],
        dm_intro="Welcome to Eldoria. No map. No compass. Only instinct. Survive the night.",
        dm_success="The sun rises over Eldoria. You are legend.",
        dm_fail="Eldoria claims another soul. Rest in shadow.",
    ),

    # -- OUTSET ISLAND (island exploration) --
    Challenge(
        name="Stranded",
        description="Reach the highest point with only a stick and courage.",
        difficulty=3,
        category="exploration",
        duration_sec=180,
        soh_commands=[
            "remove 0x4C", "remove 0x4D", "remove 0x4E",
            "remove 0x50", "remove 0x51", "give 0x3B"
        ],
        dm_intro="You wash ashore on a forgotten island. Only a stick and your wits remain.",
        dm_success="From the peak, you see home. Escape is possible.",
        dm_fail="The island keeps its secrets. You remain lost.",
    ),

    # -- GENERAL D&D STYLE --
    Challenge(
        name="Dragon's Hoard",
        description="Collect 100 rupees without taking damage.",
        difficulty=6,
        category="survival",
        duration_sec=240,
        soh_commands=["rupees 0", "spawn 20", "spawn 20"],
        dm_intro="A dragon sleeps nearby. Fill your pockets, but do not wake the beast!",
        dm_success="Rich and unscathed! The dragon snores on.",
        dm_fail="The dragon stirs. Your greed has consequences.",
    ),
    Challenge(
        name="Fairy's Gambit",
        description="Complete a dungeon room with only 1 heart.",
        difficulty=7,
        category="survival",
        duration_sec=300,
        soh_commands=["hurt 19", "spawn 16", "spawn 16", "spawn 28"],
        dm_intro="A mischievous fairy curses you! One heart, many foes. Good luck!",
        dm_success="The fairy claps in delight. You have entertained her.",
        dm_fail="The fairy sighs. Another hero falls to her game.",
    ),
    Challenge(
        name="Thunderstruck",
        description="Fight in a thunderstorm with metal equipment.",
        difficulty=4,
        category="chaos",
        duration_sec=120,
        soh_commands=["weather storm", "give 0x3C", "give 0x40", "spawn 22"],
        dm_intro="The gods are angry! Metal attracts lightning — fight if you dare!",
        dm_success="The storm passes. You are grounded and glorious.",
        dm_fail="ZAP! Thor himself could not save you.",
    ),
]


def pick_challenge(difficulty: int = 0, category: Optional[str] = None) -> Challenge:
    """Pick a random challenge, optionally filtered by difficulty or category."""
    pool = CHALLENGES
    if category:
        pool = [c for c in pool if c.category == category]
    if difficulty > 0:
        # Allow ±2 difficulty tolerance
        pool = [c for c in pool if abs(c.difficulty - difficulty) <= 2]
    if not pool:
        pool = CHALLENGES
    return random.choice(pool)


def get_challenge_by_name(name: str) -> Optional[Challenge]:
    for c in CHALLENGES:
        if c.name.lower() == name.lower():
            return c
    return None
