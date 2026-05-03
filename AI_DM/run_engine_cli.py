#!/usr/bin/env python3
"""Bridge: let Gemini execute engine commands and capture output."""
import sys
import os
import json

# Add project root to path
sys.path.insert(0, os.path.expanduser("~/HylianModding/AI_DM"))

from engine.registry import reg
from engine.skill_loader import SkillLoader
from engine.main import Engine

def execute_command(cmd_line: str) -> str:
    """Execute a command through the engine's skill dispatch and return output."""
    # Initialize engine (lazy — only once)
    if not hasattr(execute_command, 'engine'):
        print("[Bridge] Initializing engine...", file=sys.stderr)
        execute_command.engine = Engine()
        execute_command.skills = execute_command.engine.skills
        print(f"[Bridge] Engine ready. {len(execute_command.skills.command_map)} commands loaded", file=sys.stderr)

    # Dispatch the command
    try:
        result = execute_command.skills.dispatch(cmd_line)
        return str(result)
    except Exception as e:
        return f"ERROR: {type(e).__name__}: {e}"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: run_engine_cli.py '<command>'")
        sys.exit(1)

    cmd = " ".join(sys.argv[1:])
    output = execute_command(cmd)
    print(output)
