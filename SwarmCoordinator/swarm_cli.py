#!/usr/bin/env python3
"""
N64 AI Co-op Lab — Swarm CLI
=============================
Command-line interface to interact with the swarm coordinator.
Submit tasks, view fleet status, inspect results, manage world state.

Usage:
  ./swarm_cli.py status          # Show active workers and recent tasks
  ./swarm_cli.py fleet           # Alias for status
  ./swarm_cli.py task <type>     # Submit a task
  ./swarm_cli.py tasks           # List last 50 tasks
  ./swarm_cli.py world           # Show shared world state
  ./swarm_cli.py world-set KEY VALUE  # Update world state
  ./swarm_cli.py campaign        # Start a distributed campaign round
"""

import os
import sys
import json
import time
import argparse
import requests

COORD = os.environ.get("SWARM_COORD", "http://localhost:7373")


def api_post(path, payload=None):
    r = requests.post(f"{COORD}{path}", json=payload or {}, timeout=10)
    r.raise_for_status()
    return r.json()


def api_get(path):
    r = requests.get(f"{COORD}{path}", timeout=10)
    r.raise_for_status()
    return r.json()


def cmd_status(args):
    fleet = api_get("/fleet")
    tasks = api_get("/tasks")
    print("═" * 60)
    print("  🛰️  N64 AI SWARM — FLEET STATUS")
    print("═" * 60)
    if fleet["workers"]:
        for w in fleet["workers"]:
            ago = int(time.time() - w["last_seen"])
            print(f"  • {w['id']:>8}  {w['hostname']:<20}  caps: {', '.join(w['capabilities']):<30}  (last seen {ago}s ago)")
    else:
        print("  (no active workers)")
    print("─" * 60)
    print("  RECENT TASKS")
    for t in tasks["tasks"][:10]:
        ts = time.strftime("%H:%M:%S", time.localtime(t["created_at"]))
        print(f"  [{ts}] #{t['id']:>4} {t['task_type']:<18} {t['status']:<12} worker={t['assigned_to'] or '—'}")
    print("═" * 60)


def cmd_task(args):
    payload = {"task_type": args.type, "payload": {}}
    # Parse extra key=val args
    for kv in args.kwargs:
        if "=" in kv:
            k, v = kv.split("=", 1)
            try:
                v = json.loads(v)
            except json.JSONDecodeError:
                pass
            payload["payload"][k] = v
    resp = api_post("/submit_task", payload)
    print(f"[Swarm] Task submitted → ID {resp['task_id']}")


def cmd_tasks(args):
    tasks = api_get("/tasks")
    for t in tasks["tasks"]:
        ts = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(t["created_at"]))
        print(f"#{t['id']:>4}  {ts}  {t['task_type']:<18}  {t['status']:<12}  worker={t['assigned_to'] or '—'}")


def cmd_world(args):
    state = api_get("/world_state")
    print(json.dumps(state, indent=2))


def cmd_world_set(args):
    api_post("/world_state", {args.key: args.value})
    print(f"[Swarm] World state updated: {args.key} = {args.value}")


def cmd_campaign(args):
    """Submit a batch of tasks that together form one game round."""
    print("[Campaign] Launching distributed campaign round...")
    tasks = [
        ("dm_challenge", {"difficulty": args.difficulty}),
        ("generate_asset", {"type": "crystal", "theme": "shadow"}),
        ("generate_asset", {"type": "tree", "theme": "forest"}),
        ("generate_asset", {"type": "terrain", "seed": args.seed}),
        ("llm_prompt", {"prompt": f"Describe a mysterious N64 dungeon room with difficulty {args.difficulty}. Keep it under 100 words.", "max_tokens": 150}),
    ]
    ids = []
    for ttype, payload in tasks:
        r = api_post("/submit_task", {"task_type": ttype, "payload": payload})
        ids.append(r["task_id"])
        print(f"  Queued {ttype} → #{r['task_id']}")
    print(f"[Campaign] {len(ids)} tasks queued. Run 'status' to watch progress.")


# ---------------------------------------------------------------------------
# Argparse wiring
# ---------------------------------------------------------------------------

parser = argparse.ArgumentParser(description="N64 AI Swarm CLI")
parser.add_argument("--coord", default=COORD, help="Coordinator URL")
sub = parser.add_subparsers(dest="command")

sub.add_parser("status", help="Show fleet and task status")
sub.add_parser("fleet", help="Alias for status")

p_task = sub.add_parser("task", help="Submit a task")
p_task.add_argument("type", choices=["dm_challenge", "generate_asset", "blender_export", "llm_prompt", "scrape", "soh_command"])
p_task.add_argument("kwargs", nargs="*", default=[], help="key=value pairs")

sub.add_parser("tasks", help="List recent tasks")

sub.add_parser("world", help="Show world state")

p_ws = sub.add_parser("world-set", help="Set a world state key")
p_ws.add_argument("key")
p_ws.add_argument("value")

p_campaign = sub.add_parser("campaign", help="Launch a campaign round")
p_campaign.add_argument("--difficulty", type=int, default=3)
p_campaign.add_argument("--seed", type=int, default=42)

args = parser.parse_args()

if args.coord:
    COORD = args.coord

if args.command in ("status", "fleet"):
    cmd_status(args)
elif args.command == "task":
    cmd_task(args)
elif args.command == "tasks":
    cmd_tasks(args)
elif args.command == "world":
    cmd_world(args)
elif args.command == "world-set":
    cmd_world_set(args)
elif args.command == "campaign":
    cmd_campaign(args)
else:
    parser.print_help()
