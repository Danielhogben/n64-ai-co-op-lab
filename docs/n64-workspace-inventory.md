# N64 Workspace Inventory

Date: 2026-05-03

## Canonical source roots

- `AI_DM/`
- `AI_Assets/`
- `AI_World/`
- `Game/`
- `Game3D/`
- `ScraperBot/`
- `SwarmCoordinator/`
- `NuclearMon/src/`
- `ModLoader64/ModLoader/src/`
- `Tools/oot-main/`
- `Tools/Fast64/fast64/`
- `Tools/z64rom/linux/src/`

## Runtime and ROM data

- `Base_ROMs/`
- `ROM_Hacks/`
- `Assets/`
- `Library/ROMs/`
- `Metadata/`
- `ShipOfHarkinian/`
- `N64/roms`
- `N64/emulators`
- `n64dev/roms`

## Generated output

- `Game3D/build/`
- `Game3D/dist/`
- `AI_DM/__pycache__/`
- `AI_Assets/__pycache__/`
- `AI_World/__pycache__/`
- `ScraperBot/__pycache__/`
- `tools/aur-build/`
- `disasm/`
- `ShipOfHarkinian/{logs,Save,oot.o2r,imgui.ini}`
- `n64dev/projects/hello/build/`
- `n64dev/projects/hello/hello.z64`

## Active launch points

- `n64lab`
- `setup.sh`
- `build_world.sh`
- `launch_soh.sh`
- `AI_DM/run_dm.py`
- `AI_DM/run_engine.sh`
- `AI_DM/run_engine_cli.py`
- `Game3D/play.sh`
- `Game3D/build.py`
- `ModLoader64/ModLoader/start.sh`
- `ShipOfHarkinian/soh.appimage`

## Keep / archive / ignore

Keep:
- `HylianModding/AI_DM`
- `HylianModding/AI_Assets`
- `HylianModding/AI_World`
- `HylianModding/Game3D`
- `HylianModding/ScraperBot`
- `HylianModding/NuclearMon/src`
- `HylianModding/ModLoader64/ModLoader/src`
- `HylianModding/Tools/oot-main`
- `HylianModding/Tools/Fast64/fast64`
- `HylianModding/Tools/z64rom/linux/src`

Archive:
- `repos/n64-ai-co-op-lab` as a mirror copy
- `N64` as runtime state, not source
- `n64dev` as a sandbox, not canonical project state

Ignore:
- `~/~/HylianModding`
- build caches and extracted runtime payloads
- duplicate ROM/runtime stores
