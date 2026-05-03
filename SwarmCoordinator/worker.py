#!/usr/bin/env python3
"""
N64 AI Co-op Lab — Swarm Worker
================================
Runs on any node (this PC or swarm member). Registers with coordinator,
polls for tasks, executes them, reports back.

Capabilities:
  dm       — AI Dungeon Master challenge generation
  assets   — Procedural asset generation (Python, no Blender)
  blender  — Blender-based mesh export (.blend / .obj)
  llm      — Local LLM inference via llama-cpp-python
  scraper  — Metadata scraping (Archive.org, GameBanana)
  soh      — Ship of Harkinian bridge (keyboard commands)

Usage:
  python worker.py --coordinator http://192.168.1.100:7373 --caps dm assets llm
"""

import os
import sys
import json
import time
import uuid
import argparse
import socket
import importlib.util
import requests

COORD = "http://localhost:7373"
WORKER_ID = None
HEARTBEAT_INTERVAL = 30
POLL_INTERVAL = 5

# ---------------------------------------------------------------------------
# Capability detection
# ---------------------------------------------------------------------------

def detect_capabilities(args_caps):
    caps = set(args_caps or [])
    # Auto-detect if none specified
    if not caps:
        caps.add("dm")
        caps.add("assets")
        caps.add("scraper")
        try:
            import bpy
            caps.add("blender")
        except ImportError:
            pass
        try:
            from llama_cpp import Llama
            caps.add("llm")
        except ImportError:
            pass
        try:
            from pynput.keyboard import Controller
            caps.add("soh")
        except ImportError:
            pass
    return sorted(caps)


# ---------------------------------------------------------------------------
# Task executors
# ---------------------------------------------------------------------------

def run_dm_challenge(payload):
    sys.path.insert(0, os.path.expanduser("~/HylianModding/AI_DM"))
    try:
        import dm_engine
        dm = dm_engine.AIDungeonMaster()
        dm.difficulty = payload.get("difficulty", 1)
        challenge = dm.generate_challenge()
        return {"challenge": challenge, "player_hp": dm.player_hp}
    except Exception as e:
        return {"error": str(e)}


def run_generate_asset(payload):
    sys.path.insert(0, os.path.expanduser("~/HylianModding/AI_Assets"))
    try:
        import procedural_engine
        asset_type = payload.get("type", "crystal")
        theme = payload.get("theme", "shadow")
        seed = payload.get("seed")
        if asset_type == "crystal":
            data = procedural_engine.generate_crystal(theme, seed)
        elif asset_type == "tree":
            data = procedural_engine.generate_tree(seed)
        elif asset_type == "terrain":
            data = procedural_engine.generate_terrain(seed)
        elif asset_type == "dungeon_room":
            data = procedural_engine.generate_dungeon_room(theme, seed)
        else:
            return {"error": f"Unknown asset type: {asset_type}"}
        # Save JSON for reference
        out_dir = os.path.expanduser("~/HylianModding/MyWorld/swarm_out")
        os.makedirs(out_dir, exist_ok=True)
        path = os.path.join(out_dir, f"{asset_type}_{theme}_{seed or 'rand'}.json")
        with open(path, "w") as f:
            json.dump(data, f)
        return {"asset_type": asset_type, "saved_to": path, "vertices": len(data.get("vertices", []))}
    except Exception as e:
        return {"error": str(e)}


def run_blender_export(payload):
    mesh_path = payload.get("mesh_json")
    out_blend = payload.get("out_blend")
    out_obj = payload.get("out_obj")
    if not mesh_path or not os.path.exists(mesh_path):
        return {"error": "mesh_json missing or not found"}
    script = f'''
import bpy, json, sys
with open("{mesh_path}") as f:
    data = json.load(f)
mesh = bpy.data.meshes.new(data["name"])
mesh.from_pydata(data["vertices"], [], data["faces"])
obj = bpy.data.objects.new(data["name"], mesh)
bpy.context.collection.objects.link(obj)
if "{out_blend}":
    bpy.ops.wm.save_as_mainfile(filepath="{out_blend}")
if "{out_obj}":
    bpy.ops.wm.obj_export(filepath="{out_obj}")
'''
    import subprocess
    blend = out_blend or os.path.expanduser("~/HylianModding/MyWorld/swarm_out/export.blend")
    os.makedirs(os.path.dirname(blend), exist_ok=True)
    result = subprocess.run(
        ["blender", "--background", "--python-expr", script],
        capture_output=True, text=True, timeout=120
    )
    return {"returncode": result.returncode, "stderr": result.stderr[-500:]}


def run_llm_prompt(payload):
    try:
        from llama_cpp import Llama
    except ImportError:
        return {"error": "llama-cpp-python not installed"}
    model_path = payload.get("model_path")
    if not model_path:
        # Pick first available GGUF
        models_dir = os.path.expanduser("~/HylianModding/Models")
        candidates = [os.path.join(models_dir, f) for f in os.listdir(models_dir) if f.endswith(".gguf")]
        if not candidates:
            return {"error": "No model_path provided and no .gguf found"}
        model_path = candidates[0]
    prompt = payload.get("prompt", "Hello!")
    max_tokens = payload.get("max_tokens", 256)
    try:
        llm = Llama(model_path=model_path, n_ctx=2048, verbose=False)
        output = llm(prompt, max_tokens=max_tokens, stop=["</s>", "User:", "\n\n"])
        return {"text": output["choices"][0]["text"], "model": os.path.basename(model_path)}
    except Exception as e:
        return {"error": str(e)}


def run_scraper(payload):
    sys.path.insert(0, os.path.expanduser("~/HylianModding/ScraperBot"))
    try:
        import scraper
        query = payload.get("query", "zelda n64 mod")
        results = scraper.scrape_archive_org(query)
        return {"results": results}
    except Exception as e:
        return {"error": str(e)}


def run_soh_command(payload):
    sys.path.insert(0, os.path.expanduser("~/HylianModding/AI_DM"))
    try:
        import soh_bridge
        cmds = payload.get("commands", [])
        for cmd in cmds:
            soh_bridge.send_command(cmd)
            time.sleep(0.3)
        return {"commands_sent": len(cmds)}
    except Exception as e:
        return {"error": str(e)}


TASK_ROUTER = {
    "dm_challenge": run_dm_challenge,
    "generate_asset": run_generate_asset,
    "blender_export": run_blender_export,
    "llm_prompt": run_llm_prompt,
    "scrape": run_scraper,
    "soh_command": run_soh_command,
}


# ---------------------------------------------------------------------------
# Worker loop
# ---------------------------------------------------------------------------

def worker_loop(coord_url, caps):
    global WORKER_ID
    WORKER_ID = str(uuid.uuid4())[:8]
    hostname = socket.gethostname()

    # Register
    r = requests.post(f"{coord_url}/register", json={
        "id": WORKER_ID,
        "hostname": hostname,
        "capabilities": caps,
    }, timeout=10)
    print(f"[Worker {WORKER_ID}] Registered with {coord_url} — caps: {caps}")

    last_hb = 0
    while True:
        now = time.time()
        if now - last_hb > HEARTBEAT_INTERVAL:
            try:
                requests.post(f"{coord_url}/heartbeat", json={"id": WORKER_ID}, timeout=5)
                last_hb = now
            except requests.RequestException as e:
                print(f"[Worker {WORKER_ID}] Heartbeat failed: {e}")

        try:
            resp = requests.post(f"{coord_url}/poll_task", json={
                "id": WORKER_ID,
                "capabilities": caps,
            }, timeout=10)
            task = resp.json()
        except requests.RequestException as e:
            print(f"[Worker {WORKER_ID}] Poll error: {e}")
            time.sleep(POLL_INTERVAL)
            continue

        if task.get("status") == "assigned":
            tid = task["task_id"]
            ttype = task["task_type"]
            payload = task["payload"]
            print(f"[Worker {WORKER_ID}] Got task {tid} ({ttype})")

            executor = TASK_ROUTER.get(ttype)
            if executor:
                try:
                    result = executor(payload)
                    status = "completed" if "error" not in result else "failed"
                except Exception as e:
                    result = {"error": str(e)}
                    status = "failed"
            else:
                result = {"error": f"No executor for {ttype}"}
                status = "failed"

            try:
                requests.post(f"{coord_url}/complete_task", json={
                    "task_id": tid,
                    "status": status,
                    "result": result,
                }, timeout=10)
                print(f"[Worker {WORKER_ID}] Task {tid} -> {status}")
            except requests.RequestException as e:
                print(f"[Worker {WORKER_ID}] Complete failed: {e}")

        time.sleep(POLL_INTERVAL)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="N64 AI Swarm Worker")
    parser.add_argument("--coordinator", default="http://localhost:7373",
                        help="Coordinator base URL")
    parser.add_argument("--caps", nargs="*", default=None,
                        help="Capabilities (auto-detect if omitted)")
    args = parser.parse_args()

    caps = detect_capabilities(args.caps)
    print(f"[Worker] Detected capabilities: {caps}")
    worker_loop(args.coordinator, caps)
