"""Generic bridge to send commands to Ship of Harkinian or 2Ship2Harkinian."""

import time
import subprocess
from pynput.keyboard import Controller, Key
from config import CONSOLE_KEY

keyboard = Controller()

# Map games to their appimage/binary name
GAME_PROCESSES = {
    "oot": "soh.appimage",
    "mm": "2ship.appimage"
}

def _is_game_running(game: str = "oot") -> bool:
    """Check if the specific game process is active."""
    proc_name = GAME_PROCESSES.get(game, "soh.appimage")
    try:
        result = subprocess.run(
            ["pgrep", "-f", proc_name],
            capture_output=True, text=True
        )
        return result.returncode == 0 and result.stdout.strip() != ""
    except Exception:
        return False


def send_command(cmd: str, game: str = "oot", delay: float = 0.05) -> bool:
    """Open the console, type a command, and submit it."""
    if not _is_game_running(game):
        print(f"[{game.upper()} Bridge] {game} not running — manual command: {cmd}")
        return False

    # Open console
    keyboard.press(CONSOLE_KEY)
    keyboard.release(CONSOLE_KEY)
    time.sleep(delay)

    # Clear existing text
    with keyboard.pressed(Key.ctrl):
        keyboard.press('a')
        keyboard.release('a')
    keyboard.press(Key.delete)
    keyboard.release(Key.delete)
    time.sleep(delay * 0.5)

    keyboard.type(cmd)
    time.sleep(delay)

    keyboard.press(Key.enter)
    keyboard.release(Key.enter)
    time.sleep(delay)

    keyboard.press(CONSOLE_KEY)
    keyboard.release(CONSOLE_KEY)
    time.sleep(delay)

    print(f"[{game.upper()} Bridge] Sent: {cmd}")
    return True


def send_commands(commands: list[str], game: str = "oot", delay: float = 0.05) -> bool:
    """Send multiple commands in sequence."""
    ok = True
    for cmd in commands:
        ok = send_command(cmd, game, delay) and ok
        time.sleep(delay * 2)
    return ok
