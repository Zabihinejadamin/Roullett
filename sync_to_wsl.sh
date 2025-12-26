#!/bin/bash
# Quick sync from Windows to WSL
# Run in WSL: bash sync_to_wsl.sh

WIN_DIR="/mnt/c/Users/aminz/Documents/GitHub/Roullett"
WSL_DIR="$HOME/Roullett"

echo "Syncing files from Windows to WSL..."
mkdir -p "$WSL_DIR"

cp -f "$WIN_DIR/buildozer.spec" "$WSL_DIR/buildozer.spec" && echo "✓ buildozer.spec"
cp -f "$WIN_DIR/main.py" "$WSL_DIR/main.py" && echo "✓ main.py"
rm -rf "$WSL_DIR/android_src" 2>/dev/null
cp -rf "$WIN_DIR/android_src" "$WSL_DIR/android_src" && echo "✓ android_src/"

echo ""
echo "Sync complete! Files synced to: $WSL_DIR"
