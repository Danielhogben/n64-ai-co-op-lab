"""Configuration for the AI Dungeon Master."""

import os

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SOH_PATH = os.path.expanduser("~/HylianModding/ShipOfHarkinian/soh.appimage")
TWOSHIP_PATH = os.path.expanduser("~/Downloads/2Ship-Satoko-Charlie-Linux/2ship.appimage")
ROM_HACKS_DIR = os.path.expanduser("~/HylianModding/ROM_Hacks")

# Current Game
CURRENT_GAME = "oot"  # "oot" or "mm"

# SoH Console key (default is backtick ` / tilde ~)
CONSOLE_KEY = '`'

# Timing
CHALLENGE_INTERVAL_MIN = 60       # seconds
CHALLENGE_INTERVAL_MAX = 300      # seconds
DM_INTRO_DELAY = 10               # seconds before first challenge

# TTS
TTS_ENABLED = True
TTS_VOICE = None                  # None = default
TTS_RATE = 150                    # words per minute

# Difficulty scaling
DIFFICULTY_START = 1
DIFFICULTY_MAX = 10

# SoH Console Commands Database
# These are known to work in Ship of Harkinian.
# The player can discover more by pressing ` in-game and typing 'help'.
COMMANDS = {
    "spawn_enemy": "spawn {enemy_id}",
    "kill_enemies": "kill",
    "set_time": "time {hour}",
    "heal": "heal",
    "hurt": "hurt {damage}",
    "give_rupees": "rupees {amount}",
    "remove_rupees": "rupees -{amount}",
    "give_item": "give {item_id}",
    "remove_item": "remove {item_id}",
    "teleport": "warp {scene_id} {entrance_id}",
    "set_weather": "weather {weather_type}",
    "speed_up": "speed {multiplier}",
    "slow_down": "speed {multiplier}",
    "invincible": "cheat invincible {on_off}",
    "infinite_magic": "cheat magic {on_off}",
    "no_ui": "no_ui {on_off}",
    "freecam": "freecam {on_off}",
    "save_state": "save {slot}",
    "load_state": "load {slot}",
    "reset": "reset",
    "quit": "quit",
}

# Enemy IDs commonly used in SoH (may vary by version)
ENEMIES = {
    "oot": {
        "keese": "1",
        "stalchild": "2",
        "octorok": "4",
        "wolfos": "14",
        "lizalfos": "16",
        "dodongo": "18",
        "tektite": "20",
        "peahat": "22",
        "skulltula": "24",
        "stalfo": "26",
        "bubble": "28",
        "wallmaster": "30",
        "floormaster": "31",
        "redead": "32",
        "gibdo": "33",
        "iron_knuckle": "40",
        "freezard": "46",
        "dark_link": "51",
        "ganon": "60",
    },
    "mm": {
        "deku_scrub": "1",
        "skulltula": "2",
        "wolfos": "3",
        "leever": "4",
        "takkuri": "5",
        "garo": "6",
        "redead": "7",
        "gomess": "8",
        "majora": "9",
    }
}

# Item IDs
ITEMS = {
    "oot": {
        "kokiri_sword": "0x3B",
        "master_sword": "0x3C",
        "deku_shield": "0x3E",
        "hylian_shield": "0x3F",
        "mirror_shield": "0x40",
        "bow": "0x4A",
        "hookshot": "0x4C",
        "longshot": "0x4D",
        "boomerang": "0x4E",
        "lens": "0x50",
        "hammer": "0x51",
        "ocarina": "0x58",
        "fire_arrow": "0x5A",
        "ice_arrow": "0x5B",
        "light_arrow": "0x5C",
        "farores_wind": "0x5E",
        "nayrus_love": "0x5F",
        "din_fire": "0x60",
        "bombs": "0x65",
        "bombchus": "0x6A",
        "magic_bean": "0x6F",
    },
    "mm": {
        "deku_mask": "0x32",
        "goron_mask": "0x33",
        "zora_mask": "0x34",
        "majoras_mask": "0x35",
        "fierce_deity_mask": "0x36",
    }
}
