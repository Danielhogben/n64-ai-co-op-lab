#!/usr/bin/env python3
"""Entry point for the AI Dungeon Master.

Usage:
    python run_dm.py              # Start campaign
    python run_dm.py --encounter  # Random encounter
    python run_dm.py --boon       # Grant boon
    python run_dm.py --curse      # Curse player
    python run_dm.py --success    # Report challenge success
    python run_dm.py --fail       # Report challenge fail
    python run_dm.py --status     # Show DM status
    python run_dm.py --challenge "Name"  # Launch specific challenge
    python run_dm.py --cli        # Interactive CLI mode
"""

import sys
import time
import threading
from dm_engine import AIDungeonMaster
from challenges import get_challenge_by_name


def main():
    args = sys.argv[1:]
    dm = AIDungeonMaster()

    if not args:
        dm.start_campaign()
        print("[DM] Campaign started. Press Ctrl+C to stop.")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            dm.stop_campaign()
            print("\n[DM] Campaign ended.")
        return

    cmd = args[0]

    if cmd == "--encounter":
        dm.spawn_random_encounter()
    elif cmd == "--boon":
        dm.grant_boon()
    elif cmd == "--curse":
        dm.curse_player()
    elif cmd == "--success":
        dm.report_success()
    elif cmd == "--fail":
        dm.report_fail()
    elif cmd == "--status":
        info = dm.get_active_challenge_info()
        if info:
            print(f"Active: {info['name']} ({info['category']}, diff {info['difficulty']})")
            print(f"Description: {info['description']}")
            print(f"Time remaining: {info['remaining']}s")
        else:
            print("No active challenge.")
        print(f"Current world difficulty: {dm.difficulty}")
    elif cmd == "--challenge":
        if len(args) < 2:
            print("Usage: python run_dm.py --challenge 'Challenge Name'")
            return
        name = " ".join(args[1:])
        challenge = get_challenge_by_name(name)
        if challenge:
            dm.active_challenge = challenge
            dm.challenge_start_time = time.time()
            dm.speak(challenge.dm_intro)
            from soh_bridge import send_commands
            if challenge.soh_commands:
                send_commands(challenge.soh_commands)
            timer = threading.Thread(target=dm._challenge_timer, args=(challenge,), daemon=True)
            timer.start()
        else:
            print(f"Challenge '{name}' not found.")
    elif cmd == "--cli":
        dm.say_intro()
        print("\n[DM] Interactive mode. Commands: encounter, boon, curse, success, fail, status, quit")
        while True:
            try:
                line = input("> ").strip().lower()
            except (EOFError, KeyboardInterrupt):
                break
            if line == "quit":
                break
            elif line == "encounter":
                dm.spawn_random_encounter()
            elif line == "boon":
                dm.grant_boon()
            elif line == "curse":
                dm.curse_player()
            elif line == "success":
                dm.report_success()
            elif line == "fail":
                dm.report_fail()
            elif line == "status":
                info = dm.get_active_challenge_info()
                if info:
                    print(f"  Active: {info['name']} | Remaining: {info['remaining']}s")
                else:
                    print("  No active challenge.")
                print(f"  Difficulty: {dm.difficulty}")
            else:
                print("Unknown command.")
        dm.stop_campaign()
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
