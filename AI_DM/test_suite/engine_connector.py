#!/usr/bin/env python3
"""
EngineConnector — unified command and state interface to the AI DM engine.

Usage:
  from engine_connector import EngineConnector
  ec = EngineConnector()
  ec.send("quest.list")              # send command (if socket console exists)
  state = ec.get_state()             # read current_state.json
  log_tail = ec.tail_log(100)        # last 100 lines of engine.log
"""

import socket
import time
import json
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any, List


class EngineConnector:
    """Connects to the AI DM engine via multiple strategies."""

    def __init__(
        self,
        host: str = "127.0.0.1",
        console_port: int = 15555,
        log_path: str = "/home/donn/HylianModding/AI_DM/engine.log",
        state_path: str = "/home/donn/HylianModding/AI_DM/current_state.json",
    ):
        self.host = host
        self.console_port = console_port
        self.log_path = Path(log_path)
        self.state_path = Path(state_path)
        self._socket: Optional[socket.socket] = None
        self._log_cache: List[str] = []
        self._last_log_size = 0

    # ── Connection ────────────────────────────────────────────────────────────

    def connect(self) -> bool:
        """Try to connect to the engine console socket (if exposed)."""
        try:
            self._socket = socket.create_connection(
                (self.host, self.console_port), timeout=2
            )
            return True
        except Exception as e:
            self._socket = None
            # Port not open — fall back to log tailing
            return False

    # ── Command execution ─────────────────────────────────────────────────────

    def send(self, cmd: str, timeout: int = 2) -> str:
        """
        Send a command to the running engine.
        Returns command response or empty string if no socket console.
        """
        if self._socket:
            try:
                self._socket.sendall((cmd + "\n").encode())
                self._socket.settimeout(timeout)
                return self._socket.recv(4096).decode().strip()
            except Exception as e:
                return f"[ERROR] {e}"
        return ""  # No socket console — results live in logs

    # ── Log tailing ────────────────────────────────────────────────────────────

    def tail_log(self, lines: int = 50) -> str:
        """Return the last *lines* lines of engine.log (incremental read)."""
        if not self.log_path.exists():
            return ""
        try:
            stat = self.log_path.stat()
            if stat.st_size == self._last_log_size:
                return ""  # no change
            self._last_log_size = stat.st_size
        except:
            pass
        result = subprocess.run(
            ["tail", f"-{lines}", str(self.log_path)],
            capture_output=True, text=True
        )
        return result.stdout

    def wait_for_ready(self, timeout: int = 10) -> bool:
        """Block until the engine reports 'ENGINE READY' in the log."""
        start = time.time()
        while time.time() - start < timeout:
            if "ENGINE READY" in self.tail_log(200):
                return True
            time.sleep(0.5)
        return False

    # ── State persistence ─────────────────────────────────────────────────────

    def get_state(self) -> Optional[Dict[str, Any]]:
        """Read and return current_state.json as a dict."""
        if not self.state_path.exists():
            return None
        try:
            with open(self.state_path) as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return None

    def get_tick(self) -> int:
        """Return current engine tick counter."""
        state = self.get_state()
        return state.get("tick", 0) if state else -1

    def is_dm_active(self) -> bool:
        """Check whether the dungeon master daemon is running."""
        state = self.get_state()
        return state.get("dm_active", False) if state else False

    # ── Process introspection ─────────────────────────────────────────────────

    @staticmethod
    def is_engine_running() -> bool:
        result = subprocess.run(
            ["pgrep", "-f", "engine/main.py"], capture_output=True, text=True
        )
        return bool(result.stdout.strip())

    @staticmethod
    def is_sail_running() -> bool:
        result = subprocess.run(
            ["pgrep", "-f", "sail_server"], capture_output=True, text=True
        )
        return bool(result.stdout.strip())

    @staticmethod
    def is_anchor_running() -> bool:
        result = subprocess.run(
            ["pgrep", "-f", "anchor_server"], capture_output=True, text=True
        )
        return bool(result.stdout.strip())

    @staticmethod
    def is_game_running() -> bool:
        # SoH can appear as soh, soh.appimage, or the binary name
        result1 = subprocess.run(["pgrep", "-f", "soh.appimage"], capture_output=True, text=True)
        result2 = subprocess.run(["pgrep", "-f", "soh"], capture_output=True, text=True)
        r1 = bool(result1.stdout.strip())
        r2 = bool(result2.stdout.strip())
        # Deduplicate overlapping PIDs
        pids1 = set(result1.stdout.strip().split()) if result1.stdout.strip() else set()
        pids2 = set(result2.stdout.strip().split()) if result2.stdout.strip() else set()
        return len(pids1 | pids2) > 0

    # ── Log pattern helpers ────────────────────────────────────────────────────

    def find_pattern(self, pattern: str, recent_lines: int = 200) -> List[str]:
        """Return all lines matching *pattern* in the tail of engine.log."""
        tail = self.tail_log(recent_lines)
        return [l for l in tail.split("\n") if pattern.lower() in l.lower()]

    def has_pattern(self, pattern: str, recent_lines: int = 200) -> bool:
        return bool(self.find_pattern(pattern, recent_lines))


# Demo
if __name__ == "__main__":
    ec = EngineConnector()
    print("Engine running:", ec.is_engine_running())
    print("Sail running:", ec.is_sail_running())
    print("Game running:", ec.is_game_running())
    print("Engine ready?", ec.wait_for_ready(5))
    print("Current tick:", ec.get_tick())
    print("DM active:", ec.is_dm_active())
    tail = ec.tail_log(10)
    if tail:
        print("Log tail (10 lines):")
        for l in tail.split("\n")[:10]:
            print(" ", l)
