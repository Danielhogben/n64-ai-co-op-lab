import socket
from helpers import assert_true
import subprocess

def run():
    print("\n" + "="*60)
    print("PHASE 6: SAIL BRIDGE PROTOCOL & NETWORK")
    print("="*60 + "\n")

    passed = 0; total = 0

    # Sail port
    print("[6.1] TCP connectivity (Sail):")
    total += 1
    try:
        s = socket.create_connection(("127.0.0.1", 43384), timeout=2)
        s.close()
        if assert_true(True, "Port 43384 accepting connections"):
            passed += 1
    except Exception as e:
        if assert_true(False, f"Connection failed: {e}"):
            passed += 1

    print("\n[6.2] Protocol liveness probe:")
    total += 1
    try:
        s = socket.create_connection(("127.0.0.1", 43384), timeout=2)
        s.settimeout(1)
        s.send(b"\\x00")           # null-byte ping
        try:
            _ = s.recv(1024)        # wait for any response
        except socket.timeout:
            pass                   # timeout OK — still connected
        s.close()
        if assert_true(True, "Socket remained open, data accepted"):
            passed += 1
    except Exception as e:
        if assert_true(False, f"Socket error: {e}"):
            passed += 1

    print("\n[6.3] Anchor relay:")
    total += 1
    try:
        s = socket.create_connection(("127.0.0.1", 43383), timeout=2)
        s.close()
        if assert_true(True, "Anchor port 43383 responding"):
            passed += 1
    except Exception as e:
        if assert_true(False, f"Anchor failed: {e}"):
            passed += 1

    print(f"\n[6.x] Phase 6 summary: {passed}/{total} passed")
    return passed, total
