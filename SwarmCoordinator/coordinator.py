#!/usr/bin/env python3
"""
N64 AI Co-op Lab — Swarm Coordinator
=====================================
Central hub that distributes tasks across a fleet of worker nodes.
Runs on the command node (this PC). Workers connect via HTTP.

Endpoints:
  POST /register       — Worker registers its capabilities
  POST /heartbeat      — Worker keeps its lease alive
  POST /submit_task    — Client submits a new task
  GET  /poll_task      — Worker polls for next task
  POST /complete_task  — Worker reports task completion
  GET  /fleet          — List all active workers
  GET  /tasks          — List task queue and history
  GET  /world_state    — Get shared campaign world state
  POST /world_state    — Update shared campaign world state
"""

import os
import sys
import json
import time
import sqlite3
import threading
from datetime import datetime
from flask import Flask, request, jsonify

DB_PATH = os.path.expanduser("~/HylianModding/SwarmCoordinator/swarm.db")
app = Flask(__name__)

# ---------------------------------------------------------------------------
# DB setup
# ---------------------------------------------------------------------------

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS workers (
            id TEXT PRIMARY KEY,
            hostname TEXT,
            capabilities TEXT,  -- JSON array: ["dm", "assets", "llm", "blender", "soh"]
            last_seen REAL,
            status TEXT DEFAULT 'active'
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_type TEXT,      -- "dm_challenge", "generate_asset", "llm_prompt", "scrape"
            payload TEXT,        -- JSON task parameters
            status TEXT DEFAULT 'pending',  -- pending | assigned | running | completed | failed
            assigned_to TEXT,
            result TEXT,
            created_at REAL,
            started_at REAL,
            completed_at REAL
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS world_state (
            key TEXT PRIMARY KEY,
            value TEXT,
            updated_at REAL
        )
    """)

    conn.commit()
    conn.close()


def db_conn():
    return sqlite3.connect(DB_PATH)


# ---------------------------------------------------------------------------
# Background janitor — prune dead workers
# ---------------------------------------------------------------------------

def janitor_loop(interval=30):
    while True:
        time.sleep(interval)
        cutoff = time.time() - 120  # 2 minutes without heartbeat = dead
        conn = db_conn()
        c = conn.cursor()
        c.execute("UPDATE workers SET status='dead' WHERE last_seen < ?", (cutoff,))
        conn.commit()
        conn.close()


# ---------------------------------------------------------------------------
# HTTP API
# ---------------------------------------------------------------------------

@app.route("/register", methods=["POST"])
def register():
    data = request.get_json(force=True)
    worker_id = data.get("id") or f"worker_{int(time.time()*1000)}"
    conn = db_conn()
    c = conn.cursor()
    c.execute("""
        INSERT OR REPLACE INTO workers (id, hostname, capabilities, last_seen, status)
        VALUES (?, ?, ?, ?, 'active')
    """, (worker_id, data.get("hostname", "unknown"),
          json.dumps(data.get("capabilities", [])), time.time()))
    conn.commit()
    conn.close()
    return jsonify({"status": "registered", "id": worker_id})


@app.route("/heartbeat", methods=["POST"])
def heartbeat():
    data = request.get_json(force=True)
    wid = data.get("id")
    conn = db_conn()
    c = conn.cursor()
    c.execute("UPDATE workers SET last_seen=?, status='active' WHERE id=?", (time.time(), wid))
    conn.commit()
    conn.close()
    return jsonify({"status": "ok"})


@app.route("/submit_task", methods=["POST"])
def submit_task():
    data = request.get_json(force=True)
    conn = db_conn()
    c = conn.cursor()
    c.execute("""
        INSERT INTO tasks (task_type, payload, status, created_at)
        VALUES (?, ?, 'pending', ?)
    """, (data.get("task_type"), json.dumps(data.get("payload", {})), time.time()))
    task_id = c.lastrowid
    conn.commit()
    conn.close()
    return jsonify({"status": "queued", "task_id": task_id})


@app.route("/poll_task", methods=["POST"])
def poll_task():
    data = request.get_json(force=True)
    wid = data.get("id")
    caps = data.get("capabilities", [])

    conn = db_conn()
    c = conn.cursor()

    # Find oldest pending task that matches worker capabilities
    # For now, any pending task goes to any capable worker
    c.execute("""
        SELECT id, task_type, payload FROM tasks
        WHERE status='pending'
        ORDER BY created_at ASC LIMIT 1
    """)
    row = c.fetchone()

    if row:
        task_id, ttype, payload = row
        c.execute("""
            UPDATE tasks SET status='assigned', assigned_to=?, started_at=?
            WHERE id=?
        """, (wid, time.time(), task_id))
        conn.commit()
        conn.close()
        return jsonify({
            "status": "assigned",
            "task_id": task_id,
            "task_type": ttype,
            "payload": json.loads(payload) if payload else {},
        })

    conn.close()
    return jsonify({"status": "empty"})


@app.route("/complete_task", methods=["POST"])
def complete_task():
    data = request.get_json(force=True)
    conn = db_conn()
    c = conn.cursor()
    c.execute("""
        UPDATE tasks SET status=?, result=?, completed_at=?
        WHERE id=?
    """, (data.get("status", "completed"),
          json.dumps(data.get("result", {})),
          time.time(), data.get("task_id")))
    conn.commit()
    conn.close()
    return jsonify({"status": "recorded"})


@app.route("/fleet", methods=["GET"])
def fleet():
    conn = db_conn()
    c = conn.cursor()
    c.execute("SELECT id, hostname, capabilities, last_seen, status FROM workers WHERE status='active'")
    rows = c.fetchall()
    conn.close()
    return jsonify({
        "workers": [
            {"id": r[0], "hostname": r[1], "capabilities": json.loads(r[2]),
             "last_seen": r[3], "status": r[4]}
            for r in rows
        ]
    })


@app.route("/tasks", methods=["GET"])
def tasks():
    conn = db_conn()
    c = conn.cursor()
    c.execute("SELECT id, task_type, status, assigned_to, created_at FROM tasks ORDER BY created_at DESC LIMIT 50")
    rows = c.fetchall()
    conn.close()
    return jsonify({
        "tasks": [
            {"id": r[0], "task_type": r[1], "status": r[2],
             "assigned_to": r[3], "created_at": r[4]}
            for r in rows
        ]
    })


@app.route("/world_state", methods=["GET"])
def get_world_state():
    conn = db_conn()
    c = conn.cursor()
    c.execute("SELECT key, value, updated_at FROM world_state")
    rows = c.fetchall()
    conn.close()
    return jsonify({r[0]: {"value": json.loads(r[1]), "updated_at": r[2]} for r in rows})


@app.route("/world_state", methods=["POST"])
def post_world_state():
    data = request.get_json(force=True)
    conn = db_conn()
    c = conn.cursor()
    for k, v in data.items():
        c.execute("""
            INSERT OR REPLACE INTO world_state (key, value, updated_at)
            VALUES (?, ?, ?)
        """, (k, json.dumps(v), time.time()))
    conn.commit()
    conn.close()
    return jsonify({"status": "updated"})


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    init_db()
    t = threading.Thread(target=janitor_loop, daemon=True)
    t.start()
    print("[Coordinator] Starting on http://0.0.0.0:7373")
    app.run(host="0.0.0.0", port=7373, threaded=True)
