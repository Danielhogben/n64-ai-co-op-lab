# 🗡️ HylianModding AI Co-op Lab

[![Build Standalone](https://github.com/Danielhogben/n64-ai-co-op-lab/actions/workflows/build.yml/badge.svg)](https://github.com/Danielhogben/n64-ai-co-op-lab/actions/workflows/build.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

> **N64 modding tools + AI-powered co-op experiences + a standalone 3D open-world game.**

Everything from [hylianmodding.com](https://hylianmodding.com) — supercharged with AI agents for real-time modding, procedural world generation, and a D&D-style dungeon master that runs alongside your ROM hacks.

---

## 🎮 Project Nexus — Standalone 3D Game

The flagship of this repo: a **GTA-style third-person open-world game** built in Python with the Ursina engine.

- **Explore** 8 galaxies and 64 zones across a 362-ROM universe
- **Fight** enemies with a day/night cycle that makes them sleep at night
- **Build** bases, summon vehicles, mine minerals, trade with shops
- **Quest** system with NPCs, loot crates, dungeons, and boss arenas
- **Save** your progress locally — fully standalone, no internet required

| | |
|:---:|:---:|
| 🌍 Procedural Terrain | 🏰 Dungeon Generator |
| 🛸 Vehicle Summoning | 🌗 Day/Night Cycle |
| ⚔️ Boss Arenas | 🎒 Loot & Crafting |

### Play Now

**Linux / macOS**
```bash
cd Game3D
./play.sh
```

**Windows**
```batch
cd Game3D
play.bat
```

Or grab a **pre-built executable** from the [Releases](https://github.com/Danielhogben/n64-ai-co-op-lab/releases) page — no Python required.

---

## 🤖 AI Dungeon Master

An AI-powered DM inspired by **all your ROM hacks**. It speaks challenges, spawns enemies, changes time/weather, and scales difficulty as you play.

```bash
cd AI_DM
python run_dm.py --cli
```

**Modes:** auto-campaign | interactive | instant encounter | boon | curse

---

## 🛠️ N64 Modding Toolkit

| Tool | Purpose |
|------|---------|
| **Ship of Harkinian** | PC port of OoT with mods, randomizer, cheats, console |
| **ModLoader64** | N64 mod framework + netplay (TypeScript) |
| **SharpOcarina** | Custom map maker for OoT/MM |
| **Fast64** | Blender addon for OoT decomp |
| **z64rom** | Project manager for MQ Debug ROM |

---

## 📁 Repository Layout

```
HylianModding/
├── Game3D/              🎮 Standalone 3D game (Ursina)
├── Game/                🕹️ 2D pygame prototype
├── AI_DM/               🤖 AI Dungeon Master
├── ScraperBot/          🕷️ Metadata scraper
├── MyWorld/             🌐 Procedural world experiments
├── NuclearMon/          ☢️ Post-apocalyptic mod concept
├── AI_World/            🗺️ AI world architect
├── n64lab               🚀 Unified launcher script
└── setup.sh             ⚙️ One-time environment setup
```

> **Note:** ROMs, patches, and copyrighted assets are **not** included in this repository. You must supply your own legally obtained backups.

---

## 🚀 Quick Start

```bash
# 1. Clone
git clone https://github.com/Danielhogben/n64-ai-co-op-lab.git
cd n64-ai-co-op-lab

# 2. Setup (makes scripts executable)
./setup.sh

# 3. Launch what you want
./n64lab              # interactive menu
./n64lab play         # Ship of Harkinian
./n64lab dm           # AI Dungeon Master
```

---

## 🏗️ Building Standalone Executables

```bash
cd Game3D
python build.py
```

Builds are handled automatically by [GitHub Actions](https://github.com/Danielhogben/n64-ai-co-op-lab/actions) for both **Linux** and **Windows** on every tag.

---

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). In short:

- Don't commit copyrighted ROMs/assets
- Don't commit build artifacts or logs
- Open an issue before major changes

---

## 📜 License

Code is released under the [MIT License](LICENSE).

Nintendo 64 ROMs, game assets, patches, and derivative works are property of their respective copyright holders and are **not** included.

---

*Built with Ursina Engine, Python, and a love for Hyrule.*
