# 🤖 AI Dungeon Master for N64 & 3DS

An AI-driven Dungeon Master that plays **Ship of Harkinian** (OoT) and **2Ship2Harkinian** (MM) with you, and supports 3DS world integration.

## What It Does

- **Speaks to you** via text-to-speech
- **Monitors the game** and launches timed challenges from an N64/3DS focused database
- **Controls the world** by sending console commands to Harkinian engines
- **Scales difficulty** based on your successes and failures
- **Cross-World Travel** between N64 and 3DS game contexts

## Quick Start

### 1. Launch Ship of Harkinian

```bash
~/HylianModding/ShipOfHarkinian/soh.appimage
```

On first run, point it at your OoT ROM to generate `oot.otr`.

### 2. Start the AI DM (auto-campaign mode)

```bash
cd ~/HylianModding/AI_DM
../venv/bin/python run_dm.py
```

The DM will introduce itself and begin launching challenges every 60–300 seconds.

### 3. Interactive CLI Mode

```bash
../venv/bin/python run_dm.py --cli
```

Commands:
- `encounter` — instant enemy spawn
- `boon` — random helpful reward
- `curse` — random harmful effect
- `success` — you completed the active challenge
- `fail` — you failed the active challenge
- `status` — show current challenge & difficulty
- `quit` — exit

### 4. One-Off Commands

```bash
../venv/bin/python run_dm.py --encounter   # Random fight
../venv/bin/python run_dm.py --boon        # Fairy blessing
../venv/bin/python run_dm.py --curse       # Dark curse
../venv/bin/python run_dm.py --success     # Report win
../venv/bin/python run_dm.py --fail        # Report loss
```

## How It Works

1. **Screenshot / Console Bridge** (`soh_bridge.py`)  
   Detects if SoH is running and simulates console keypresses (`\``) to inject commands.

2. **Challenge Database** (`challenges.py`)  
   15+ challenges drawn from the themes of your ROM hacks:
   - **Crystal Clocks** → time-based races
   - **Demon's Quest** → demon gauntlets, iron knuckle duels
   - **OoT Chaos** → random effect surges, rupee roulette
   - **Ultimate Trial** → boss rushes, trial rooms
   - **Sands of Time** → speed/rewind mechanics
   - **Transformation Masks** → restricted-loadout fights
   - **Majora's Mask Chaos** → apocalyptic events
   - **Master of Time** → Dark Link paradox duels
   - **Shadows of Eldoria** → no-UI survival nights
   - **Outset Island** → stranded exploration

3. **DM Engine** (`dm_engine.py`)  
   Manages campaign state, TTS queue, difficulty scaling, and challenge timers.

## Co-Op Multiplayer

SoH has **Ivan the Fairy** local co-op (second player helps/hinders). For online co-op, install the **Anchor** mod server:

```bash
# Download from https://github.com/garrettjoecox/anchor/releases
# Or use the public server: anchor.hm64.org:43383
```

With Anchor, you and a friend (or an AI bot) can explore the same world. The DM can then issue **group challenges**.

## Extending the DM

### Add New Challenges

Edit `challenges.py` and append to `CHALLENGES`:

```python
Challenge(
    name="My Custom Trial",
    description="Do something impossible.",
    difficulty=10,
    category="combat",
    duration_sec=300,
    soh_commands=["spawn 60", "remove 0x3C"],
    dm_intro="The DM speaks!",
    dm_success="You win!",
    dm_fail="You lose!",
)
```

### Discover More SoH Commands

In Ship of Harkinian, press `` ` `` to open the console and type `help`.  
Add useful commands to `config.py` under `COMMANDS`.

### Add Screen Reading (OCR)

Install Tesseract OCR:
```bash
sudo pacman -S tesseract tesseract-data-eng
```

Then modify `dm_engine.py` to use `mss` + `pytesseract` to read hearts/rupees from the screen for automated win/loss detection.

## Architecture

```
run_dm.py          → CLI entry point
 dm_engine.py      → Campaign loop, TTS, difficulty scaling
 challenges.py     → Challenge database
 soh_bridge.py     → SoH console command injector
 config.py         → Settings, command maps, enemy/item IDs
```

## Known Limitations

- **Console commands** require SoH to be focused (or you can run them manually).  
  If SoH is not running, commands are printed to terminal for copy-paste.
- **TTS** requires `espeak` on Linux. If missing, the DM prints text only.
- **Win detection** is currently manual (`--success` / `--fail`).  
  Future: OCR or memory-reading for automatic detection.

## Tips for the Best Experience

1. **Enable the Cheat Menu** in SoH settings for maximum DM control.
2. **Turn on Randomizer** — the DM works great with shuffled items and enemies.
3. **Use a second monitor** — keep the DM terminal visible while playing.
4. **Stream it** — the TTS voice makes for great content.

---

*May the RNG gods smile upon you... or not.*
