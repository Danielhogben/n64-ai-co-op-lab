# Agent Audit Summary

Date: 2026-05-03

This summary consolidates the current CLI and agent state on this machine.

## Main findings

- `HylianModding` is the canonical live workspace for the N64/game-mod stack.
- `repos/n64-ai-co-op-lab` is a cleaner duplicate mirror of the same project.
- `N64` is a runtime/media stash with ROMs, saves, logs, and SoH runtime data.
- `n64dev` is a small isolated N64 dev sandbox.
- `~/~/HylianModding` is stray and should not be treated as canonical.

## CLI status

- `opencode` is installed but failing health checks because `/home/donn/.config/opencode/config.json` no longer matches the current schema.
- `claude` and `codex` exist on disk, but T3’s health checks report them as unavailable in that launcher context.
- `kimi` is available but rate-limited/quota-limited.
- `openclaw` is installed and configured for local gateway mode.
- `zeroclaw` is configured with local autonomy settings and openrouter-backed models.

## Hermes focus

Recent Hermes activity centers on:

- `HylianModding/Game3D/` and “Project Nexus 3D”
- session recovery and reconstruction
- asset validation and build checks
- N64/SoH tooling and runtime probing

## Recent failures

- IMAP auth failures in Hermes gateway logs
- Telegram DNS/network failure in Hermes gateway logs
- shutdown-time asyncio/prompt-toolkit errors in Hermes logs
- OpenCode schema validation failure

## Immediate cleanup targets

1. Repair OpenCode config to match the installed version.
2. Consolidate duplicated agent state across `.hermes`, `.kimi`, `.openclaw`, `.spawn`, `.t3`, `.claude`, `.codex`, `.gemini`, `.junie`, and `.pi`.
3. Keep the canonical N64 workspace in `HylianModding` and treat `repos/n64-ai-co-op-lab` as a mirror or archive.
