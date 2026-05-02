#!/bin/bash
# Build script: MyWorld → N64 ROM
# Run this after creating assets in Blender

set -e

PROJECT="$HOME/HylianModding/MyWorld"
TOOLS="$HOME/HylianModding/Tools"
BASE_ROM="$HOME/HylianModding/Base_ROMs/OoT.z64"

echo "=== MyWorld Build Pipeline ==="
echo ""

# Check base ROM
if [ ! -f "$BASE_ROM" ]; then
    echo "❌ Base ROM not found at $BASE_ROM"
    echo "   Extract your OoT ROM to Base_ROMs/OoT.z64"
    exit 1
fi

# Check Blender addons
echo "✅ Blender addons installed:"
blender --background --python-expr "
import bpy
for a in ['fast64', 'io_export_so2']:
    print(f'  {a}: {a in bpy.context.preferences.addons}')
" 2>&1 | grep -E "fast64|io_export_so2" || true

echo ""
echo "📁 Project folders:"
ls -1 "$PROJECT"

echo ""
echo "=== Build Steps ==="
echo ""
echo "1. Open Blender and create your map in:"
echo "   $PROJECT/blender/"
echo ""
echo "2. Export with Fast64 (for decomp) or io_export_so2 (for SharpOcarina):"
echo "   - Fast64 → Export to $PROJECT/scenes/"
echo "   - SharpOcarina → Export .zscene + .zmap to $PROJECT/scenes/"
echo ""
echo "3. Place custom actors in:"
echo "   $PROJECT/actors/"
echo ""
echo "4. Build the ROM:"
echo "   Option A: z64rom (if libcurl-gnutls is installed)"
echo "     $TOOLS/z64rom/linux/z64rom --build --output $PROJECT/builds/MyWorld.z64"
echo ""
echo "   Option B: ModLoader64 + patch"
echo "     # Use ModLoader64 to inject scenes at runtime"
echo "     # Then use flips to create a .bps patch"
echo ""
echo "   Option C: Ship of Harkinian (PC only)"
echo "     # Place custom OTRs in SoH mods folder"
echo "     # Play instantly on PC without building a ROM"
echo ""
echo "5. Create patch for distribution:"
echo "   flips --create $BASE_ROM $PROJECT/builds/MyWorld.z64 $PROJECT/patches/MyWorld.bps"
echo ""
echo "=== Quick Launch ==="
echo "Play on PC:     ~/HylianModding/launch_soh.sh"
echo "AI DM:          cd ~/HylianModding/AI_DM && ../venv/bin/python run_dm.py --cli"
echo "N64 Emulator:   cd ~/HylianModding/ModLoader64/ModLoader && ./start.sh"
