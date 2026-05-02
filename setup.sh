#!/bin/bash
# One-time setup for the HylianModding AI Co-op Lab

echo "=== HylianModding AI Co-op Lab Setup ==="

# Make SoH executable
chmod +x ~/HylianModding/ShipOfHarkinian/soh.appimage

# Make ModLoader64 start script executable
chmod +x ~/HylianModding/ModLoader64/ModLoader/start.sh

echo ""
echo "✅ Setup complete!"
echo ""
echo "NEXT STEPS:"
echo "1. Launch Ship of Harkinian:"
echo "   ~/HylianModding/ShipOfHarkinian/soh.appimage"
echo ""
echo "2. On first run, select your OoT ROM to generate oot.otr"
echo ""
echo "3. Start the AI Dungeon Master:"
echo "   cd ~/HylianModding/AI_DM"
echo "   ../venv/bin/python run_dm.py --cli"
echo ""
echo "4. (Optional) Launch ModLoader64:"
echo "   cd ~/HylianModding/ModLoader64/ModLoader"
echo "   ./start.sh"
echo ""
echo "Read ~/HylianModding/AI_DM/README.md for full docs."
