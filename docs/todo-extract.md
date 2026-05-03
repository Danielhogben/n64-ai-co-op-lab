# Extracted TODOs

Date: 2026-05-03

Source: Hermes sessions, gateway logs, OpenCode health checks, and CLI config state.

## Priority 1

- Repair OpenCode config schema in `/home/donn/.config/opencode/config.json`.
- Stabilize Hermes gateway logins and message transports.
- Decide whether `HylianModding` or `repos/n64-ai-co-op-lab` is the canonical working tree.

## Priority 2

- Consolidate duplicated agent configuration across `.hermes`, `.kimi`, `.openclaw`, `.spawn`, `.t3`, `.claude`, `.codex`, `.gemini`, `.junie`, and `.pi`.
- Reduce stray runtime/state duplication in `HylianModding` and `N64`.
- Separate source trees from generated assets and ROM/runtime stores.

## Priority 3

- Continue the `Game3D` / Project Nexus 3D path as the main active build.
- Keep SoH runtime state in one place.
- Decide which launcher path is actually authoritative for `claude` and `codex` in T3.
