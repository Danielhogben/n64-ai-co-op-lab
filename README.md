# HylianModding AI Co-op Lab

Everything from [hylianmodding.com](https://hylianmodding.com) — plus AI tools for co-op adventures, real-time modding, and a D&D-style dungeon master.

Run `~/HylianModding/setup.sh` after reading this.

---

## 📁 Folder Structure

```
HylianModding/
├── AI_DM/                  # 🤖 AI Dungeon Master framework
│   ├── run_dm.py           # Launch the DM
│   ├── dm_engine.py        # Campaign engine + TTS
│   ├── challenges.py       # 15+ D&D challenges from your ROM hacks
│   ├── soh_bridge.py       # SoH console command injector
│   ├── config.py           # Settings, enemy/item IDs
│   └── README.md           # DM docs
│
├── Archives/               # Original downloaded zip/tar/7z files
├── Assets/                 # Empty — for screenshots, textures, etc.
├── Base_ROMs/              # Original N64 ROMs
├── ROM_Hacks/              # Extracted patches & hacks
├── Tools/                  # Extracted modding tools
│   ├── SharpOcarina/       # Custom map tool (exe + Blender scripts)
│   ├── Fast64/             # Blender addon for OoT decomp
│   ├── z64rom/             # Project manager (linux + windows)
│   ├── ActorPack/          # Hylian Modding actor pack
│   └── oot-main/           # OoT decomp source
│
├── ShipOfHarkinian/        # 🚢 PC port of OoT (best platform for AI co-op)
│   └── soh.appimage        # Ready to run
│
├── ModLoader64/            # 🎮 N64 mod framework (TypeScript + netplay)
│   └── ModLoader/start.sh  # Launch script
│
├── venv/                   # Python virtual environment
├── setup.sh                # One-time setup script
└── README.md               # This file
```

---

## 🚀 Quick Start (3 Steps)

### 1. Launch Ship of Harkinian

```bash
~/HylianModding/ShipOfHarkinian/soh.appimage
```

On first run, select your OoT ROM. It will generate `oot.otr` automatically.

> **Why SoH?** It's a native PC port with built-in randomizer, cheat menu, Crowd Control, **Ivan the Fairy co-op**, 60+ FPS, custom model support, and a debug console the AI can inject commands into. Much easier to mod and script than emulating hardware.

### 2. Start the AI Dungeon Master

```bash
cd ~/HylianModding/AI_DM
../venv/bin/python run_dm.py --cli
```

The DM will speak challenges, spawn enemies, change time/weather, and scale difficulty as you play.

### 3. (Optional) True N64 Modding / Netplay

```bash
cd ~/HylianModding/ModLoader64/ModLoader
./start.sh
```

ModLoader64 wraps Mupen64Plus and lets you write mods in TypeScript with multiplayer networking.

---

## 🤖 AI Dungeon Master

The DM is inspired by **all your ROM hacks**. It turns them into live D&D challenges:

| ROM Hack Theme | DM Challenge Examples |
|----------------|----------------------|
| **Crystal Clocks** | Time-limited races before sunset |
| **Demon's Quest** | Demon gauntlets, Iron Knuckle duels |
| **OoT Chaos** | Random effect surges, rupee roulette |
| **Ultimate Trial** | Boss rushes, trial rooms |
| **Sands of Time** | Speed-up/rewind mechanics |
| **Transformation Masks** | Restricted-loadout fights |
| **Majora's Mask Chaos** | Apocalyptic moon events |
| **Master of Time** | Dark Link paradox duels |
| **Shadows of Eldoria** | No-UI survival nights |
| **Outset Island** | Stranded exploration |

### DM Commands

```bash
../venv/bin/python run_dm.py              # Auto-campaign mode
../venv/bin/python run_dm.py --cli        # Interactive mode
../venv/bin/python run_dm.py --encounter  # Instant fight
../venv/bin/python run_dm.py --boon       # Fairy blessing
../venv/bin/python run_dm.py --curse      # Dark curse
../venv/bin/python run_dm.py --success    # You won the challenge
../venv/bin/python run_dm.py --fail       # You lost
```

In **interactive mode**, type: `encounter`, `boon`, `curse`, `success`, `fail`, `status`, `quit`

### Co-Op Multiplayer

- **Local:** Enable *Ivan the Fairy* in SoH settings (second player on controller 2)
- **Online:** Install [Anchor](https://github.com/garrettjoecox/anchor) for true networked co-op

---

## 🛠️ Tools Reference

| Tool | What It Does | How to Use |
|------|--------------|------------|
| **Ship of Harkinian** | PC port of OoT with mods, randomizer, cheats, console | Run `soh.appimage` |
| **ModLoader64** | N64 mod framework + netplay (TypeScript) | Run `start.sh` |
| **SharpOcarina** | Custom map maker for OoT/MM | Open `SharpOcarina.exe` in Wine, or use Blender scripts |
| **Fast64** | Blender addon for OoT decomp | Install `.zip` in Blender → Preferences → Add-ons |
| **z64rom** | Project manager for MQ Debug ROM | Use Linux build in `z64rom/linux/` |
| **ActorPack** | Pre-made actors for decomp | Import into your decomp project |

---

## 🎮 Base ROMs

| File | Game |
|------|------|
| `Legend of Zelda, The - Ocarina of Time (USA) (Rev 2).zip` | OoT (base ROM) |
| `Legend of Zelda, The_ Majora's Mask.zip` | Majora's Mask (base ROM) |
| `Mario Kart 64 (USA).zip` | Mario Kart 64 |
| `Super Smash Bros. (USA).zip` | Super Smash Bros. |
| `NINTENDO 64-20260502T030921Z-3-00*.zip` | Full N64 ROM set (3 parts) |

---

## 🧩 ROM Hacks

All `.bps` patches are extracted and ready. Apply with `flips`:

```bash
flips --apply patch.bps original.z64 output.z64
```

| Mod | Folder | Base ROM |
|-----|--------|----------|
| Crystal Clocks | `ROM_Hacks/Crystal_Clocks/` | OoT |
| Demon's Quest | `ROM_Hacks/Demons_Quest/` | OoT |
| Majora's Mask: Chaos Edition | `ROM_Hacks/Majoras_Mask_Chaos_Edition/` | MM |
| Master of Time Revisited | `ROM_Hacks/Master_of_Time_Revisited/` | OoT |
| OoT: Chaos Mod | `ROM_Hacks/OoT_Chaos/` | OoT |
| Outset Island | `ROM_Hacks/Outset_Island/` | OoT |
| Sands of Time | `ROM_Hacks/Sands_of_Time/` | OoT |
| Shadows of Eldoria (DEMO) | `ROM_Hacks/Shadows_of_Eldoria/` | OoT |
| Transformation Masks in OoT | `ROM_Hacks/Transformation_Masks_in_OoT/` | OoT |
| Ultimate Trial | `ROM_Hacks/Ultimate_Trial/` | OoT |

---

## 🧙 Creating Your Own N64 World

1. **Play** a ROM hack with the AI DM to get ideas
2. **Build** custom maps in SharpOcarina or Fast64 + Blender
3. **Code** new behaviors in ModLoader64 (TypeScript) or SoH (C++)
4. **Write** new DM challenges in `AI_DM/challenges.py`
5. **Share** your `.bps` or mod with the world

---

## 🌐 Missing Mods (Available on hylianmodding.com)

You have 10 of 44 mods. Notable missing ones:

- **Dawn & Dusk** — new story campaign
- **The Missing Link** — post-OoT adventure
- **Spaceworld '97 Experience** — beta restoration
- **Nimpize Adventure** — dungeon-focused
- **Time Lost** — time-travel puzzle
- **Silent Hill in OoT** — horror conversion
- **Voyager of Time** — open world
- **Zelda's Birthday** — lighthearted quest

Download them from [hylianmodding.com/mods](https://hylianmodding.com/mods) and drop them into `ROM_Hacks/`.

---

## 💡 Tips

- **Best DM experience:** Enable SoH's randomizer + cheat menu, then let the DM wreak havoc
- **Streaming:** The DM's TTS voice makes for great content
- **Second monitor:** Keep the DM terminal visible while playing
- **Expand:** Edit `AI_DM/challenges.py` to add challenges from newly downloaded ROM hacks

---

## 🔗 Links

- **GitHub Repo:** https://github.com/Danielhogben/n64-ai-co-op-lab
- **Hylian Modding:** https://hylianmodding.com
- **Ship of Harkinian:** https://www.shipofharkinian.com

---

*Organized & augmented on 2026-05-02*
