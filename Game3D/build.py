#!/usr/bin/env python3
"""
Cross-platform standalone build script for Project Nexus.
Creates a single executable/folder using PyInstaller.
"""
import os, sys, subprocess, shutil

GAME_DIR = os.path.dirname(os.path.abspath(__file__))
BUILD_DIR = os.path.join(GAME_DIR, 'build')
DIST_DIR = os.path.join(GAME_DIR, 'dist')
VENV_DIR = os.path.join(GAME_DIR, '.build_venv')

EXE_NAME = "ProjectNexus"
MAIN_SCRIPT = "nexus_3d.py"

def run(cmd, cwd=None):
    print(f">>> {' '.join(cmd)}")
    subprocess.check_call(cmd, cwd=cwd or GAME_DIR)

def ensure_venv():
    python = sys.executable
    if not os.path.exists(VENV_DIR):
        print("Creating build virtual environment...")
        run([python, "-m", "venv", VENV_DIR])

    if sys.platform == "win32":
        pip = os.path.join(VENV_DIR, "Scripts", "pip.exe")
        py = os.path.join(VENV_DIR, "Scripts", "python.exe")
    else:
        pip = os.path.join(VENV_DIR, "bin", "pip")
        py = os.path.join(VENV_DIR, "bin", "python")
    return py, pip

def build():
    py, pip = ensure_venv()

    print("Installing dependencies + PyInstaller...")
    run([pip, "install", "--upgrade", "pip"])
    run([pip, "install", "-r", "requirements.txt"])
    run([pip, "install", "pyinstaller"])

    # Clean previous builds
    for d in (BUILD_DIR, DIST_DIR):
        if os.path.exists(d):
            shutil.rmtree(d)

    # Find ursina package path for built-in assets
    import importlib.util
    ursina_spec = importlib.util.find_spec('ursina')
    ursina_path = os.path.dirname(ursina_spec.origin) if ursina_spec else None

    # PyInstaller command (onedir is more reliable for games with assets)
    cmd = [
        py, "-m", "PyInstaller",
        "--name", EXE_NAME,
        "--onedir",
        "--clean",
        "--noconfirm",
        "--add-data", f"data{os.pathsep}data",
        "--add-data", f"textures{os.pathsep}textures",
    ]

    # Include Ursina's built-in models, textures and shaders
    if ursina_path:
        for asset_dir in ('models_compressed', 'textures', 'shaders'):
            src = os.path.join(ursina_path, asset_dir)
            if os.path.exists(src):
                cmd.extend(["--add-data", f"{src}{os.pathsep}ursina/{asset_dir}"])

    cmd.append(MAIN_SCRIPT)

    # On Windows, --console keeps the terminal open for errors/debug
    if sys.platform == "win32":
        cmd.append("--console")

    run(cmd)

    exe_ext = ".exe" if sys.platform == "win32" else ""
    exe_path = os.path.join(DIST_DIR, EXE_NAME, EXE_NAME + exe_ext)
    print(f"\n✅ Build complete!")
    print(f"   Folder: {DIST_DIR}/{EXE_NAME}/")
    print(f"   Executable: {exe_path}")
    print(f"\nYou can zip the folder and share it.")

if __name__ == "__main__":
    try:
        build()
    except Exception as e:
        print(f"\n❌ Build failed: {e}")
        sys.exit(1)
