# Test utilities and assertions
import json, time, subprocess
from pathlib import Path

def assert_true(condition, message):
    if condition:
        print(f"  ✓ {message}")
        return True
    else:
        print(f"  ✗ {message}")
        return False

def wait_for(condition_fn, timeout=10, interval=0.5):
    start = time.time()
    while time.time() - start < timeout:
        if condition_fn():
            return True
        time.sleep(interval)
    return False

def read_json_safe(path):
    try:
        with open(path) as f:
            return json.load(f)
    except:
        return None
