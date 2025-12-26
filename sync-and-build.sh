#!/bin/bash
# Complete sync and build script for Roulette Android app
# Run this in WSL: bash sync-and-build.sh

WINDOWS_DIR="/mnt/c/Users/aminz/OneDrive/Documents/GitHub/Roullett"
WSL_DIR="$HOME/Roullett"

echo "=========================================="
echo "Syncing files from Windows to WSL..."
echo "From: $WINDOWS_DIR"
echo "To: $WSL_DIR"
echo "=========================================="
echo ""

# Create WSL directory if it doesn't exist
mkdir -p "$WSL_DIR"

# Sync main files
echo "Syncing main.py..."
cp -v "$WINDOWS_DIR/main.py" "$WSL_DIR/" && echo "✓ main.py synced" || echo "✗ main.py FAILED"

echo "Syncing buildozer.spec..."
cp -v "$WINDOWS_DIR/buildozer.spec" "$WSL_DIR/" && echo "✓ buildozer.spec synced" || echo "✗ buildozer.spec FAILED"

# Sync android_src directory (CRITICAL for fullscreen!)
echo "Syncing android_src/..."
if [ -d "$WINDOWS_DIR/android_src" ]; then
    rm -rf "$WSL_DIR/android_src" 2>/dev/null
    cp -rv "$WINDOWS_DIR/android_src" "$WSL_DIR/" && echo "✓ android_src/ synced" || echo "✗ android_src/ FAILED"
else
    echo "⚠ android_src/ not found in Windows directory!"
fi

# Sync other files
[ -f "$WINDOWS_DIR/requirements.txt" ] && cp -v "$WINDOWS_DIR/requirements.txt" "$WSL_DIR/" && echo "✓ requirements.txt synced"
[ -d "$WINDOWS_DIR/sounds" ] && cp -rv "$WINDOWS_DIR/sounds" "$WSL_DIR/" 2>/dev/null && echo "✓ sounds/ synced"
[ -d "$WINDOWS_DIR/roulette_game" ] && cp -rv "$WINDOWS_DIR/roulette_game" "$WSL_DIR/" 2>/dev/null && echo "✓ roulette_game/ synced"

echo ""
echo "=========================================="
echo "Verifying critical files..."
echo "=========================================="

# Verify buildozer.spec has correct entrypoint
if grep -q "android.entrypoint = org.kivy.android.FullscreenPythonActivity" "$WSL_DIR/buildozer.spec"; then
    echo "✓ buildozer.spec has correct entrypoint"
else
    echo "✗ WARNING: buildozer.spec entrypoint is NOT set to FullscreenPythonActivity!"
    echo "  This will cause the app to NOT be fullscreen!"
fi

# Verify android_src exists
if [ -f "$WSL_DIR/android_src/org/kivy/android/FullscreenPythonActivity.java" ]; then
    echo "✓ FullscreenPythonActivity.java found"
else
    echo "✗ ERROR: FullscreenPythonActivity.java NOT FOUND!"
    echo "  The app will NOT be fullscreen without this file!"
fi

echo ""
echo "=========================================="
echo "Ready to build!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. cd ~/Roullett"
echo "2. source ~/buildozer_env/bin/activate"
echo "3. buildozer android debug"
echo ""
echo "After build completes, copy APK with:"
echo "cp bin/roulette-0.1-arm64-v8a_armeabi-v7a-debug.apk $WINDOWS_DIR/bin/"

