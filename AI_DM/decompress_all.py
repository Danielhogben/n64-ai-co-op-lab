import os
import subprocess
import glob
from concurrent.futures import ThreadPoolExecutor

ROM_DIRS = [
    "/home/donn/HylianModding/ROM_Hacks",
    "/home/donn/HylianModding/Base_ROMs"
]

Z64DECOMPRESS = "/home/donn/HylianModding/Tools/SharpOcarina/ndec/z64decompress.exe"

def decompress_rom(rom_path):
    if ".decompressed." in rom_path:
        return
        
    output_path = rom_path + ".decompressed.z64"
    if os.path.exists(output_path):
        return
        
    print(f"Decompressing {os.path.basename(rom_path)}...")
    try:
        # Run wine z64decompress.exe
        subprocess.run(
            ["wine", Z64DECOMPRESS, rom_path, output_path],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        
        # Replace original file if decompressed file was created
        if os.path.exists(output_path):
            os.replace(output_path, rom_path)
            print(f"✓ Decompressed: {os.path.basename(rom_path)}")
    except subprocess.CalledProcessError:
        print(f"✗ Failed to decompress (or already decompressed): {os.path.basename(rom_path)}")

def main():
    rom_files = set()
    for d in ROM_DIRS:
        for ext in ("*.z64", "*.n64", "*.v64"):
            rom_files.update(glob.glob(os.path.join(d, "**", ext), recursive=True))
            
    print(f"Found {len(rom_files)} ROMs. Starting batch decompression...")
    
    # Use ThreadPoolExecutor to run up to 8 wine instances in parallel
    with ThreadPoolExecutor(max_workers=8) as executor:
        executor.map(decompress_rom, rom_files)
        
    print("\nAll ROMs have been processed.")

if __name__ == "__main__":
    main()
