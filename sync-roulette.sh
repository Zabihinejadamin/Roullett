#!/bin/bash
# Quick sync script for Roulette project
# Run this in WSL before building: bash sync-roulette.sh

WINDOWS_DIR="/mnt/c/Users/aminz/OneDrive/Documents/GitHub/Roullett"
WSL_DIR="$HOME/Roullett"

echo "Syncing files from Windows to WSL..."
echo "From: $WINDOWS_DIR"
echo "To: $WSL_DIR"
echo ""

# Copy main files
if [ -f "$WINDOWS_DIR/main.py" ]; then
    cp -v "$WINDOWS_DIR/main.py" "$WSL_DIR/" && echo "✓ main.py synced"
else
    echo "✗ main.py not found in Windows directory"
fi

if [ -f "$WINDOWS_DIR/buildozer.spec" ]; then
    cp -v "$WINDOWS_DIR/buildozer.spec" "$WSL_DIR/" && echo "✓ buildozer.spec synced"
else
    echo "✗ buildozer.spec not found in Windows directory"
fi

# Copy other files if they exist
[ -f "$WINDOWS_DIR/requirements.txt" ] && cp -v "$WINDOWS_DIR/requirements.txt" "$WSL_DIR/" && echo "✓ requirements.txt synced"
[ -d "$WINDOWS_DIR/sounds" ] && cp -rv "$WINDOWS_DIR/sounds" "$WSL_DIR/" 2>/dev/null && echo "✓ sounds/ synced"
[ -d "$WINDOWS_DIR/roulette_game" ] && cp -rv "$WINDOWS_DIR/roulette_game" "$WSL_DIR/" 2>/dev/null && echo "✓ roulette_game/ synced"

echo ""
echo "Sync complete! Ready to build."
echo "Run: cd ~/Roullett && buildozer android debug"

