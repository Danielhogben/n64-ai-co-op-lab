import os
import subprocess
import json
import hashlib

class RetroReversingAnalyzer:
    def __init__(self):
        self.sm64tools_bin = "/home/donn/repos/RetroReversing/sm64tools/bin"
        self.libultra_sigs_path = "/home/donn/repos/RetroReversing/n64SplitConfigs/libultra.json"
        self.libultra_sigs = {}
        
        if os.path.exists(self.libultra_sigs_path):
            try:
                with open(self.libultra_sigs_path, 'r') as f:
                    data = json.load(f)
                    self.libultra_sigs = data.get("function_signatures", {})
            except Exception as e:
                print(f"Warning: Could not load LibUltra signatures: {e}")

    def analyze_n64(self, rom_path):
        """Analyze N64 ROM using sm64tools and libultra signatures"""
        analysis = {
            "type": "n64",
            "functions_found": 0,
            "identified_names": [],
            "header": {}
        }
        
        try:
            with open(rom_path, 'rb') as f:
                header = f.read(0x40)
                # ROM name at 0x20, 20 bytes
                analysis["header"]["name"] = header[0x20:0x34].decode('ascii', errors='ignore').strip()
                # ROM ID at 0x3B, 4 bytes
                analysis["header"]["id"] = header[0x3B:0x3F].decode('ascii', errors='ignore').strip()
        except:
            pass
            
        return analysis

    def analyze_3ds(self, rom_path):
        """Basic metadata extraction for 3DS ROMs"""
        analysis = {
            "type": "3ds",
            "format": os.path.splitext(rom_path)[1].lower()[1:],
            "header": {}
        }
        # 3DS analysis usually requires specialized tools like ctrtool, 
        # but we can try to find the Title ID or Name if possible.
        return analysis

    def get_deep_metadata(self, category, rom_path):
        """Dispatches to specific analyzer based on category"""
        if category == "n64":
            return self.analyze_n64(rom_path)
        elif category == "3ds":
            return self.analyze_3ds(rom_path)
        return {"type": category, "analysis": "basic"}

if __name__ == "__main__":
    analyzer = RetroReversingAnalyzer()
    print("RetroReversing Analyzer (N64/3DS) Initialized")
