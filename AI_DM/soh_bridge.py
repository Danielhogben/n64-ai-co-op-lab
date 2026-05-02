"""Bridge to send commands to Ship of Harkinian via keyboard simulation."""

import time
import subprocess
from pynput.keyboard import Controller, Key
from config import CONSOLE_KEY

keyboard = Controller()


def _is_soh_running() -> bool:
    """Check if soh.appimage process is active."""
    try:
        result = subprocess.run(
            ["pgrep", "-f", "soh.appimage"],
            capture_output=True, text=True
        )
        return result.returncode == 0 and result.stdout.strip() != ""
    except Exception:
        return False


def send_command(cmd: str, delay: float = 0.05) -> bool:
    """Open the SoH console, type a command, and submit it.

    Returns True if the command was sent, False if SoH is not running.
    """
    if not _is_soh_running():
        print(f"[SoH Bridge] SoH not running — manual command: {cmd}")
        return False

    # Open console
    keyboard.press(CONSOLE_KEY)
    keyboard.release(CONSOLE_KEY)
    time.sleep(delay)

    # Clear any existing text (Ctrl+A then Delete)
    with keyboard.pressed(Key.ctrl):
        keyboard.press('a')
        keyboard.release('a')
    keyboard.press(Key.delete)
    keyboard.release(Key.delete)
    time.sleep(delay * 0.5)

    # Type command
    keyboard.type(cmd)
    time.sleep(delay)

    # Submit
    keyboard.press(Key.return)
    keyboard.release(Key.return)
    time.sleep(delay)

    # Close console
    keyboard.press(CONSOLE_KEY)
    keyboard.release(CONSOLE_KEY)
    time.sleep(delay)

    print(f"[SoH Bridge] Sent: {cmd}")
    return True


def send_commands(commands: list[str], delay: float = 0.05) -> bool:
    """Send multiple commands in sequence."""
    ok = True
    for cmd in commands:
        ok = send_command(cmd, delay) and ok
        time.sleep(delay * 2)
    return ok
