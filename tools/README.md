# Hylian Modding Tools

This directory contains tools and repositories cloned from @Danielhogben's starred list to support the AI DM and ROM Integration projects.

## Core Game & Recompilation
- **[Zelda64Recomp](./Zelda64Recomp)**: Static recompilation for Zelda N64 games.
- **[N64Recomp](./N64Recomp)**: Tool used to recompile N64 games into native executables.

## Multiplayer & Remote Control
- **[anchor](../CoOp/anchor)**: Co-op mod/server for Ship of Harkinian.
- **[sail](./sail)**: A networking protocol for remote control of the Ship of Harkinian client. **(Recommended: Use this to replace the current keypress-simulating bridge in `soh_bridge.py`)**

## AI & Audio
- **[legend-of-elya-n64](./legend-of-elya-n64)**: GPT-based AI NPC system for N64.
- **[KittenTTS](./KittenTTS)**: High-quality TTS model under 25MB. **(Recommended: Potential upgrade for the AI DM's voice system)**

## Asset Conversion
- **[fast64](./fast64)**: Blender plugin for editing N64 scenes and meshes.
- **[Obj2N64DL](./Obj2N64DL)** / **[objn64](./objn64)**: OBJ to N64 Display List converters.
- **[n64texconv](./n64texconv)**: PNG to N64 texture converter.

## Integration Suggestions
1. **Bridge Upgrade**: Use the `sail` protocol to send console commands to Ship of Harkinian programmatically, avoiding focus issues with the current simulated keypress method.
2. **Multiplayer Challenges**: Integrate `anchor` to allow the AI DM to interact with multiple players in a co-op session.
3. **Enhanced Voice**: Implement `KittenTTS` for a more natural-sounding AI DM without heavy dependencies.
