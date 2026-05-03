# Contributing to HylianModding AI Co-op Lab

Thanks for your interest in contributing! This project covers N64 modding tools, an AI Dungeon Master, and a standalone 3D game.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/n64-ai-co-op-lab.git`
3. Create a branch: `git checkout -b feature/my-feature`

## Project Structure

- `Game3D/` — Project Nexus 3D game (Ursina Engine)
- `Game/` — Project Nexus 2D prototype (Pygame)
- `AI_DM/` — AI Dungeon Master framework
- `ScraperBot/` — Metadata scraper
- `MyWorld/`, `NuclearMon/`, `AI_World/` — World generation experiments

## Rules

- **Do NOT commit copyrighted material** — No ROMs, `.bps` patches, `.zobj` files, or extracted game assets.
- **Do NOT commit build artifacts** — No `venv/`, `__pycache__/`, `dist/`, `build/`, or `.log` files.
- **Keep bundled data small** — If adding JSON/text data, keep individual files under 5 MB.
- **Test your changes** — Run the game or tool before opening a PR.

## Code Style

- Python: PEP 8
- Shell scripts: `shellcheck` clean where possible
- Commit messages: concise present tense (`Add feature`, `Fix bug`)

## Opening a Pull Request

1. Ensure your branch is up to date with `main`
2. Fill out the PR template
3. Link any related issues
4. Wait for review — maintainers will respond within a few days

## Questions?

Open a [Discussion](https://github.com/Danielhogben/n64-ai-co-op-lab/discussions) or ping us in an issue.
