# ☢️ NUCLEARMON — Post-Nuclear Pokémon War
## N64 Game Design Document

---

## Elevator Pitch
*Fallout meets Pokémon on the N64.* 30 years after the Great War, mutated Pokémon roam irradiated wastelands. You are a **Wasteland Tamer** — scavenging ruins, capturing mutated Pokémon, and battling rival factions for survival in a world where Poké Balls are scarce and radiation is everywhere.

---

## Setting

**Year:** 20XX — 30 years after "The Flash" (nuclear exchange between Kanto and Johto)

**World:** The former Kanto region is now **The Ashlands** — a sprawling nuclear wasteland of:
- **Viridian Crater** — Ground Zero, highly irradiated, home to legendary mutated Pokémon
- **Pallet Ruins** — Your starting village, a shanty-town built in the ruins of Professor Oak's lab
- **Mt. Moon Mine** — A raider-controlled uranium mine, home to mutated Geodude and Onix
- **Cerulean Canal** — Flooded, toxic waterways where water-type Pokémon have become bioluminescent horrors
- **Saffron Scrapyard** — A massive junkyard city run by the **Silph Remnant** faction
- **Cinnabar Reactor** — Meltdown site, the final dungeon, home to the legendary **Nuclear Charizard**

---

## Factions

| Faction | Goal | Relationship |
|---------|------|-------------|
| **The Silph Remnant** | Rebuild pre-war technology, control Poké Ball manufacturing | Neutral/Trader |
| **The Rad Cult** | Worship radiation, believe mutations are evolution's next step | Hostile |
| **The Oak Enclave** | Preserve pure (non-mutated) Pokémon species | Friendly |
| **The Rocket Reborn** | Raiders and slavers, capture Pokémon for blood sport | Hostile |
| **The Vault Dwellers** | Underground survivors, hoard pre-war knowledge | Neutral |

---

## Core Mechanics (N64-Style)

### 1. Wasteland Exploration (Third-Person)
- Traverse the overworld in real-time (like OoT)
- **Geiger Counter** HUD element — radiation zones require RadSuits or anti-rad Pokémon
- **Day/Night Cycle** — Mutated Pokémon are more aggressive at night
- **Random Encounters** — Trigger when wandering into tall (irradiated) grass

### 2. Capture System
- **Poké Balls** are scarce crafting items
- Weaken mutated Pokémon in real-time combat, then throw a ball
- Capture rate affected by: HP, radiation level, type of ball

### 3. Real-Time Combat (Action RPG, not turn-based)
- You fight alongside your lead Pokémon
- **Player:** Uses scavenged weapons (pipe rifles, nail boards, thrown rocks)
- **Pokémon:** Uses moves mapped to C-buttons (N64 controller)
  - C-Left: Move 1 (e.g., Tackle)
  - C-Up: Move 2 (e.g., Ember)
  - C-Right: Move 3 (e.g., Growl)
  - C-Down: Switch Pokémon / Item
- **Z-Target** locks on (like OoT)

### 4. Mutation System
- Pokémon have a **Mutation Meter** (0-100%)
- Higher mutation = stronger attacks but harder to control
- **Radiation Exposure** can force mutations
- **Purification** at Oak Enclave shrines reduces mutation
- Some mutations grant new types (e.g., Fire → Nuclear/Fire)

### 5. Base Building
- Claim ruined buildings as safe houses
- Craft workbenches for: Poké Ball smithing, weapon repair, rad-away brewing
- Deploy captured Pokémon as guards

---

## Pokémon Roster (Mutated Forms)

### Starter Options (Pure-Strain, rare)
1. **Bulbasaur** → Ivysaur → Venusaur (Radiation type added)
2. **Charmander** → Charmeleon → Charizard (Nuclear Fire final form)
3. **Squirtle** → Wartortle → Blastoise (Toxic/Water type)

### Common Wasteland Pokémon
| Pokémon | Mutation | Type | Behavior |
|---------|----------|------|----------|
| Rattata | Giant, hairless, glowing eyes | Normal/Radiation | Packs |
| Pidgey | Featherless, leathery wings | Flying/Radiation | Scavengers |
| Geodude | Uranium-infused, glows green | Rock/Radiation | Territorial |
| Grimer | Massive, corrosive puddles | Poison/Nuclear | Aggressive |
| Voltorb | Unstable, explodes randomly | Electric/Nuclear | Suicidal |
| Ghastly | Visible radiation aura | Ghost/Radiation | Nocturnal |

### Legendary Bosses
| Boss | Location | Type |
|------|----------|------|
| **Nuclear Charizard** | Cinnabar Reactor | Fire/Nuclear |
| **Toxic Mewtwo** | Saffron Scrapyard (deep) | Psychic/Nuclear |
| **Glowing Onix** | Mt. Moon Mine | Rock/Radiation |
| **The Hive Queen** (Beedrill swarm) | Viridian Crater | Bug/Nuclear |

---

## Items (Scavenged/Crafted)

| Item | Function |
|------|----------|
| **Scrap Poké Ball** | Low capture rate, crafted from junk |
| **Military Ball** | Pre-war, high capture rate, very rare |
| **RadAway** | Reduces player radiation sickness |
| **Mutagen Syringe** | Forces Pokémon mutation +20% |
| **Purification Chip** | Reduces mutation, Oak Enclave tech |
| **Nuka-Cherry** | Health restore, may cause mutation |
| **Stimpak** | Instant HP restore |
| **Geiger Counter** | Equippable, shows radiation levels |

---

## Controls (N64 Controller)

| Input | Action |
|-------|--------|
| Analog Stick | Move |
| A | Jump / Interact / Throw Poké Ball |
| B | Attack (melee weapon) |
| Z | Z-Target lock-on |
| R | Block / Raise shield |
| L | Toggle Geiger Counter overlay |
| C-Left | Pokémon Move 1 |
| C-Up | Pokémon Move 2 |
| C-Right | Pokémon Move 3 |
| C-Down | Pokémon Move 4 / Switch |
| D-Pad Up | Use item |
| D-Pad Down | Crouch / Sneak |
| Start | Pause / Menu (Pokémon party, items, map, radio) |

---

## Art Style
- **Low-poly N64 aesthetic** — 500-1500 tris per character
- **Muddy, desaturated palette** — browns, grays, sickly greens, occasional neon radiation glow
- **Fog density** — heavy draw-distance fog (authentic N64 feel + atmospheric)
- **Texture filtering** — point-filtered for retro look
- **CRT scanline option** — for authentic feel

---

## Audio
- **Ambient:** Wind, Geiger counter clicks, distant Pokémon cries
- **Music:** Sparse, industrial-tinged ambient (think OoT Shadow Temple + Fallout radio static)
- **Radio:** Scavenged pre-war holotapes with Professor Oak's final broadcast

---

## Development Roadmap

### Phase 1: Prototype (SoH Mod)
- Retexture Hyrule Field as Ashlands
- Replace Link with Wasteland Tamer model
- Add Pokémon companion following player
- Basic real-time combat with 3 moves

### Phase 2: Full Mod
- All 6 major regions as custom maps
- 15+ mutated Pokémon models
- Full mutation/capture system
- Faction questlines

### Phase 3: Standalone (Optional)
- Port to libdragon for true N64 homebrew
- Or ModLoader64 for true N64 mod

---

*"Gotta catch 'em all... before they catch you."*
