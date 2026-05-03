import socket
import json
import threading
import time
from typing import List, Optional

class SailBridge:
    def __init__(self, host="127.0.0.1", port=43384):
        self.host = host
        self.port = port
        self.sock: Optional[socket.socket] = None
        self.connected = False
        self._lock = threading.Lock()

    def connect(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.host, self.port))
            self.connected = True
            print(f"[SailBridge] Connected to Sail server at {self.host}:{self.port}")
            return True
        except Exception as e:
            print(f"[SailBridge] Failed to connect: {e}")
            self.connected = False
            return False

    def send_command(self, cmd: str):
        if not self.connected:
            if not self.connect():
                return False
        
        packet = {
            "id": str(time.time()),
            "type": "command",
            "command": cmd
        }
        try:
            with self._lock:
                # Sail protocol uses null-terminated JSON strings
                self.sock.sendall((json.dumps(packet) + "\0").encode("utf-8"))
            return True
        except Exception as e:
            print(f"[SailBridge] Send error: {e}")
            self.connected = False
            return False

    def send_commands(self, commands: List[str]):
        success = True
        for cmd in commands:
            if not self.send_command(cmd):
                success = False
        return success

    def close(self):
        if self.sock:
            self.sock.close()
            self.connected = False

if __name__ == "__main__":
    # Test
    bridge = SailBridge()
    if bridge.connect():
        bridge.send_command("heal")
        bridge.close()
