#!/usr/bin/env python3
"""
PROJECT NEXUS: AI COMMAND CENTER DASHBOARD
The central entry point for the N64/3DS AI DM, GameForge, and Hermes Agent.
"""

import os
import sys
import subprocess
import time

def print_banner():
    print("\n" + "═"*60)
    print(" ☤  PROJECT NEXUS: AI COMMAND CENTER (N64 & 3DS Edition)  ☤ ")
    print("    Local LLM Optimized | RetroReversing Powered")
    print("═"*60 + "\n")

def check_services():
    print("[*] Checking local services...")
    
    # Check Ollama
    try:
        subprocess.run(["pgrep", "ollama"], check=True, stdout=subprocess.DEVNULL)
        print("  ✅ Ollama (Local Brain) is running.")
    except:
        print("  ❌ Ollama is NOT running. Run 'ollama serve' first.")
        
    # Check vLLM / llama.cpp (optional)
    try:
        subprocess.run(["pgrep", "-f", "vllm|llama-server"], check=True, stdout=subprocess.DEVNULL)
        print("  ✅ Secondary LLM Server is active.")
    except:
        print("  ℹ️  Secondary LLM Server is idle.")

def main_menu():
    print_banner()
    check_services()
    
    print("\n[ COMMANDS ]")
    print("  1.  Start Hermes Agent (Autonomous PC Control & RE)")
    print("  2.  Run AI Dungeon Master (N64 Co-Op Challenge Engine)")
    print("  3.  Launch GameForge (Generate New Franchise Data)")
    print("  4.  Scan for ROMs (Deep N64/3DS Analysis)")
    print("  5.  Open Manual Reverse Engineering Toolkit (ImHex, ares)")
    print("  6.  Hermes Control Center (Workspaces & Mission Control)")
    print("  7.  Exit")
    
    choice = input("\nSelect an operation (1-7): ")
    
    if choice == '1':
        print("\n[*] Launching Hermes Agent...")
        subprocess.run(["hermes"])
    elif choice == '2':
        print("\n[*] Starting AI Dungeon Master...")
        subprocess.run(["python3", "/home/donn/HylianModding/AI_DM/run_dm.py"])
    elif choice == '3':
        print("\n[*] Launching GameForge...")
        subprocess.run(["python3", "/home/donn/HylianModding/GameForge/gameforge.py", "--help"])
    elif choice == '4':
        print("\n[*] Running Ultimate Scanner...")
        subprocess.run(["python3", "/home/donn/HylianModding/AI_DM/ultimate_scanner.py"])
    elif choice == '5':
        print("\n[ RE TOOLKIT ]")
        print("  a. Launch ImHex (Hex Editor)")
        print("  b. Launch Azahar (3DS Emulator)")
        print("  c. Launch Ghidra (RE Environment)")
        re_choice = input("Select a tool (a-c): ")
        if re_choice == 'a':
            subprocess.Popen(["/home/donn/Downloads/drivers/ImHex.AppImage"])
        elif re_choice == 'b':
            subprocess.Popen(["/home/donn/Downloads/drivers/azahar.AppImage"])
        elif re_choice == 'c':
            subprocess.Popen(["/home/donn/hermes_repos/ghidra/ghidraRun"])
    elif choice == '6':
        print("\n[ HERMES CONTROL CENTER ]")
        print("  a. Launch Hermes Workspace (GUI Chat & Skills)")
        print("  b. Launch Mission Control (Fleet Management)")
        print("  c. List All Installed Skills")
        h_choice = input("Select an action (a-c): ")
        if h_choice == 'a':
            print("[*] Starting Hermes Workspace at http://localhost:5173")
            subprocess.Popen(["npm", "run", "dev"], cwd="/home/donn/repos/hermes-workspace")
        elif h_choice == 'b':
            print("[*] Starting Mission Control at http://localhost:3000")
            subprocess.Popen(["npm", "run", "dev"], cwd="/home/donn/repos/mission-control")
        elif h_choice == 'c':
            subprocess.run(["hermes", "skills", "list"])
    elif choice == '7':
        print("Goodbye, Commander.")
        sys.exit(0)

if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\nExiting...")
