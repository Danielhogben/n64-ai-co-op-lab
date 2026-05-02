#!/bin/bash
# Launch Ship of Harkinian with the OoT ROM

cd ~/HylianModding/ShipOfHarkinian

ROM="OoT.z64"

if [ ! -f "$ROM" ]; then
    echo "ROM not found at $PWD/$ROM"
    echo "Place your Ocarina of Time ROM here and name it OoT.z64"
    exit 1
fi

# On first run, SoH will auto-extract assets and create oot.otr
echo "Launching Ship of Harkinian..."
./soh.appimage
