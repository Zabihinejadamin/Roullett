#!/bin/bash
# Sync files from Windows to WSL for buildozer
# Usage: ./sync_to_wsl.sh

# Adjust these paths to match your setup
WINDOWS_DIR="/mnt/c/Users/aminz/Documents/GitHub/Roullett"
WSL_DIR="$HOME/Roullett"

echo "Syncing files from Windows to WSL..."
echo "From: $WINDOWS_DIR"
echo "To: $WSL_DIR"

# Copy main files
cp -v "$WINDOWS_DIR/main.py" "$WSL_DIR/"
cp -v "$WINDOWS_DIR/buildozer.spec" "$WSL_DIR/"

# Copy android_src directory
[ -d "$WINDOWS_DIR/android_src" ] && cp -rv "$WINDOWS_DIR/android_src" "$WSL_DIR/" 2>/dev/null || true

# Copy other important files if they exist
[ -f "$WINDOWS_DIR/requirements.txt" ] && cp -v "$WINDOWS_DIR/requirements.txt" "$WSL_DIR/"
[ -d "$WINDOWS_DIR/sounds" ] && cp -rv "$WINDOWS_DIR/sounds" "$WSL_DIR/" 2>/dev/null || true
[ -d "$WINDOWS_DIR/roulette_game" ] && cp -rv "$WINDOWS_DIR/roulette_game" "$WSL_DIR/" 2>/dev/null || true

# Copy roulette_game from OneDrive if it exists there
ONEDRIVE_DIR="/mnt/c/Users/aminz/OneDrive/Documents/GitHub/Roullett"
[ -d "$ONEDRIVE_DIR/roulette_game" ] && cp -rv "$ONEDRIVE_DIR/roulette_game" "$WSL_DIR/" 2>/dev/null || true
[ -d "$ONEDRIVE_DIR/sounds" ] && cp -rv "$ONEDRIVE_DIR/sounds" "$WSL_DIR/" 2>/dev/null || true

echo "Sync complete!"
echo "Now you can run: cd ~/Roullett && buildozer android debug"

