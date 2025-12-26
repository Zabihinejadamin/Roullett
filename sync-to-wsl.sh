#!/bin/bash
# Quick sync command - run this in WSL
WIN_DIR="/mnt/c/Users/aminz/OneDrive/Documents/GitHub/Roullett"
WSL_DIR="$HOME/Roullett"
echo "Syncing files..."
cp -v "$WIN_DIR/main.py" "$WSL_DIR/" && echo "✓ main.py"
cp -v "$WIN_DIR/buildozer.spec" "$WSL_DIR/" && echo "✓ buildozer.spec"
[ -d "$WIN_DIR/android_src" ] && rm -rf "$WSL_DIR/android_src" && cp -rv "$WIN_DIR/android_src" "$WSL_DIR/" && echo "✓ android_src/" || echo "✗ android_src/ missing"
[ -d "$WIN_DIR/sounds" ] && cp -rv "$WIN_DIR/sounds" "$WSL_DIR/" 2>/dev/null && echo "✓ sounds/" || true
[ -d "$WIN_DIR/roulette_game" ] && cp -rv "$WIN_DIR/roulette_game" "$WSL_DIR/" 2>/dev/null && echo "✓ roulette_game/" || true
[ -f "$WIN_DIR/requirements.txt" ] && cp -v "$WIN_DIR/requirements.txt" "$WSL_DIR/" && echo "✓ requirements.txt" || true
echo "Sync complete!"

