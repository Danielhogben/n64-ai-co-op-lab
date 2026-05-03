#!/usr/bin/env python3
"""
Hermes Reverse Engineering Agent (HREA)
Provides an API for the Hermes AI to fully automate reverse engineering tasks
using Ghidra Bridge, Splat, and local LLMs.
"""

import os
import subprocess
import time
import json
from pathlib import Path

class HermesREAgent:
    def __init__(self, workspace="/home/donn/HylianModding"):
        self.workspace = workspace
        self.ghidra_path = "/home/donn/hermes_repos/ghidra/Ghidra/RuntimeScripts/Linux/support/analyzeHeadless"
        self.ghidra_scripts = "/home/donn/hermes_repos/ghidra/Ghidra/Features/Python/ghidra_scripts"
        self.project_dir = os.path.join(self.workspace, "GhidraProjects")
        os.makedirs(self.project_dir, exist_ok=True)

    def start_ghidra_server(self, rom_path, project_name="HermesAuto"):
        """Starts the Ghidra Headless Analyzer in the background and injects the Bridge server."""
        print(f"[HREA] Starting Ghidra Headless Server for {rom_path}...")
        
        # If the project doesn't exist, this will create it and import the ROM.
        # If it does, it will just process it.
        import_flag = "-import" if not os.path.exists(os.path.join(self.project_dir, f"{project_name}.rep")) else "-process"
        
        cmd = [
            self.ghidra_path,
            self.project_dir,
            project_name,
            import_flag, rom_path,
            "-scriptPath", self.ghidra_scripts,
            "-postScript", "ghidra_bridge_server.py"
        ]
        
        # Start in background
        self.ghidra_process = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("[HREA] Ghidra Bridge Server is initializing. Please wait 10-15 seconds before connecting.")
        return self.ghidra_process

    def decompile_function_via_bridge(self, function_name_or_address):
        """Connects to the Ghidra bridge and extracts the decompiled C code of a function."""
        print("[HREA] Connecting to Ghidra Bridge...")
        try:
            import ghidra_bridge
        except ImportError:
            return "Error: ghidra_bridge not installed in this Python environment."
            
        try:
            with ghidra_bridge.GhidraBridge(namespace=globals()):
                fm = currentProgram.getFunctionManager()
                decomp_interface = ghidra.app.decompiler.DecompInterface()
                decomp_interface.openProgram(currentProgram)
                
                # Search by name
                funcs = fm.getFunctions(True)
                target_func = None
                for f in funcs:
                    if f.getName() == function_name_or_address or str(f.getEntryPoint()) == function_name_or_address:
                        target_func = f
                        break
                        
                if not target_func:
                    return f"Function {function_name_or_address} not found in binary."
                    
                print(f"[HREA] Decompiling {target_func.getName()}...")
                results = decomp_interface.decompileFunction(target_func, 0, monitor)
                return results.getDecompiledFunction().getC()
        except Exception as e:
            return f"Bridge connection failed: {e}"

    def split_n64_rom(self, rom_path, yaml_config):
        """Uses splat to split an N64 ROM into assembly and assets."""
        print(f"[HREA] Running splat on {rom_path}...")
        try:
            subprocess.run(["splat", "split", yaml_config], check=True)
            return "ROM successfully split by splat."
        except Exception as e:
            return f"Splat failed: {e}"

if __name__ == "__main__":
    agent = HermesREAgent()
    print("Hermes Reverse Engineering Automation Ready.")
    print("- To automate Ghidra: agent.start_ghidra_server(rom_path)")
    print("- To extract code: agent.decompile_function_via_bridge('main')")
