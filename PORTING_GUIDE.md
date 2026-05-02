# PC → N64 Porting Pipeline

You want to **play on PC** (fast iteration, AI co-op, testing) and then **port to N64** (real hardware, shareable ROM). Here's the full workflow.

---

## 🖥️ Phase 1: Play on PC

### Launch Ship of Harkinian

```bash
~/HylianModding/launch_soh.sh
```

On first run, it will ask for your ROM (already placed at `ShipOfHarkinian/OoT.z64`) and generate `oot.otr`.

### Enable AI Co-op

```bash
cd ~/HylianModding/AI_DM
../venv/bin/python run_dm.py --cli
```

Type `encounter`, `boon`, `curse` while playing. The DM injects commands live into SoH.

### Why PC first?
- **Instant load times** — no N64 emulator overhead
- **Debug console** (`\`` key) — spawn anything, teleport anywhere
- **60+ FPS** — smooth testing
- **Randomizer built-in** — test ideas instantly
- **AI DM** — prototype challenge concepts before hardcoding them

---

## 🎮 Phase 2: Build N64-Compatible Content

### Path A: SharpOcarina (Custom Maps)

Best for: **new dungeons, arenas, overworld areas**

```
1. Open Blender (2.79 or 3.x)
2. Install SharpOcarina addon from Tools/SharpOcarina/BlenderScripts/
3. Build your map
4. Export as OoT scene (.zscene + .zmap)
5. Inject into a base ROM using z64rom or the SharpOcarina exporter
6. Test in ModLoader64 or SoH
7. Distribute as .bps patch
```

### Path B: Fast64 + OoT Decomp (Deep Mods)

Best for: **new actors, custom code, behavior changes**

```
1. Install Fast64 Blender addon: Tools/Fast64/fast64/
2. Blender → Edit → Preferences → Add-ons → Install → select fast64 folder
3. Export assets compatible with OoT decompilation
4. Copy exported files into Tools/oot-main/oot-main/
5. Use z64rom (Tools/z64rom/linux/z64rom) to build a custom ROM
6. Compile with gcc + mips toolchain
7. Output: custom .z64 ROM
```

### Path C: ModLoader64 (TypeScript Mods)

Best for: **multiplayer, live memory editing, scripted events**

```
cd ~/HylianModding/ModLoader64/ModLoader
./start.sh
```

Write mods in TypeScript that:
- Read/write live memory
- Sync state across networked players
- Trigger events based on game state

These mods run on **real N64 emulation** (Mupen64Plus), so they're closer to hardware than SoH.

---

## 🔧 Phase 3: The Porting Pipeline

### PC Playground → N64 ROM

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Ship of Harkin │     │  SharpOcarina   │     │   ModLoader64   │
│   (PC Testbed)  │────→│   or Fast64     │────→│  (N64 Verify)   │
│  AI DM tests    │     │  (Build Assets) │     │  (Netplay Test) │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                                          │
                                                          ▼
                                                  ┌───────────────┐
                                                  │    z64rom     │
                                                  │  (Compile)    │
                                                  └───────┬───────┘
                                                          │
                                                          ▼
                                                  ┌───────────────┐
                                                  │    flips      │
                                                  │ (Make .bps)   │
                                                  └───────┬───────┘
                                                          │
                                                          ▼
                                                  ┌───────────────┐
                                                  │  Shareable    │
                                                  │  N64 ROM Hack │
                                                  └───────────────┘
```

### Step-by-Step Example: Port a DM Challenge to N64

Let's say your AI DM invented a great challenge: *"Fight Dark Link at midnight with no shield."*

**1. Prototype in SoH (PC)**
```bash
# DM already tested this live:
spawn 51      # Dark Link
remove 0x3E   # Remove Deku Shield
remove 0x3F   # Remove Hylian Shield
remove 0x40   # Remove Mirror Shield
time 0        # Midnight
```

**2. Build the N64 version**

Create a new scene in SharpOcarina:
- Dark arena room
- Place Dark Link actor
- Remove shield pickup from the room
- Set time-of-day trigger to midnight

Export as `.zscene` + `.zmap`.

**3. Inject into ROM**

```bash
cd ~/HylianModding/Tools/z64rom/linux
./z64rom --inject ~/HylianModding/ROM_Hacks/MyHack/scene.zscene
./z64rom --build --output ~/HylianModding/ROM_Hacks/MyHack/MyHack.z64
```

**4. Create patch**

```bash
flips --create OoT.z64 MyHack.z64 ~/HylianModding/ROM_Hacks/MyHack/MyHack.bps
```

**5. Test on real N64 hardware or emulator**

```bash
# Test with ModLoader64
cd ~/HylianModding/ModLoader64/ModLoader
# Copy MyHack.bps to ModLoader/mods/ or patch the ROM directly
./start.sh
```

**6. Share**

Upload `MyHack.bps` to hylianmodding.com or Discord.

---

## 📦 Phase 4: Cross-Platform Distribution

| Platform | Format | How |
|----------|--------|-----|
| **PC (Linux/Win/Mac)** | SoH mod OTR | Place `.otr` or `.json` in SoH mods folder |
| **N64 Emulator** | `.bps` patch | Apply with `flips` |
| **N64 Flashcart** | `.z64` ROM | Patch + copy to SD card |
| **Switch / Wii U** | SoH port | Use SoH's console builds |

---

## 🛠️ Recommended Toolchain

| Task | Tool | Location |
|------|------|----------|
| PC Play + Test | Ship of Harkinian | `ShipOfHarkinian/soh.appimage` |
| AI Challenges | AI DM | `AI_DM/run_dm.py` |
| Map Creation | SharpOcarina | `Tools/SharpOcarina/` |
| Blender Export | Fast64 | `Tools/Fast64/fast64/` |
| Code Injection | z64rom | `Tools/z64rom/linux/z64rom` |
| N64 Emulation + Netplay | ModLoader64 | `ModLoader64/ModLoader/start.sh` |
| Patch Creation | flips | `ModLoader64/ModLoader/flips` (or system `flips`) |

---

## ⚡ Quick Commands

```bash
# Play on PC
~/HylianModding/launch_soh.sh

# AI DM
~/HylianModding/venv/bin/python ~/HylianModding/AI_DM/run_dm.py --cli

# Launch N64 emulator with mod support
cd ~/HylianModding/ModLoader64/ModLoader && ./start.sh

# Patch a ROM
cd ~/HylianModding/ROM_Hacks/MyHack
flips --create OoT.z64 MyHack.z64 MyHack.bps

# Apply a patch
flips --apply MyHack.bps OoT.z64 output.z64
```

---

## 🎯 Your Next Steps

1. **Play** SoH with the AI DM to find fun challenge ideas
2. **Prototype** maps in SharpOcarina or Fast64
3. **Build** a custom ROM with z64rom
4. **Test** in ModLoader64 (closest to real N64)
5. **Patch** with flips and share

The PC is your canvas. The N64 is your gallery.
