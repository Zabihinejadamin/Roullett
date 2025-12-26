#!/bin/bash
# FORCE SYNC - This will definitely work
# Run in WSL: bash /mnt/c/Users/aminz/OneDrive/Documents/GitHub/Roullett/FORCE_SYNC.sh

set -e  # Exit on error

WIN_DIR="/mnt/c/Users/aminz/OneDrive/Documents/GitHub/Roullett"
WSL_DIR="$HOME/Roullett"

echo "=========================================="
echo "FORCING SYNC FROM WINDOWS TO WSL"
echo "=========================================="
echo ""

# Check Windows directory exists
if [ ! -d "$WIN_DIR" ]; then
    echo "ERROR: Windows directory not found: $WIN_DIR"
    echo "Please check the path!"
    exit 1
fi

# Ensure WSL directory exists
mkdir -p "$WSL_DIR"

# 1. SYNC buildozer.spec
echo "1. Syncing buildozer.spec..."
if [ -f "$WIN_DIR/buildozer.spec" ]; then
    cp -f "$WIN_DIR/buildozer.spec" "$WSL_DIR/buildozer.spec"
    echo "   ✓ Copied buildozer.spec"
else
    echo "   ✗ ERROR: buildozer.spec not found!"
    exit 1
fi

# 2. SYNC main.py
echo "2. Syncing main.py..."
if [ -f "$WIN_DIR/main.py" ]; then
    cp -f "$WIN_DIR/main.py" "$WSL_DIR/main.py"
    echo "   ✓ Copied main.py"
else
    echo "   ✗ ERROR: main.py not found!"
    exit 1
fi

# 3. SYNC android_src
echo "3. Syncing android_src/..."
if [ -d "$WIN_DIR/android_src" ]; then
    rm -rf "$WSL_DIR/android_src" 2>/dev/null || true
    cp -rf "$WIN_DIR/android_src" "$WSL_DIR/android_src"
    echo "   ✓ Copied android_src/"
else
    echo "   ✗ ERROR: android_src/ not found in Windows!"
    exit 1
fi

echo ""
echo "=========================================="
echo "VERIFICATION"
echo "=========================================="

# Verify fullscreen
FULLSCREEN=$(grep "^fullscreen" "$WSL_DIR/buildozer.spec" 2>/dev/null | head -1)
echo "Fullscreen: $FULLSCREEN"
if [[ "$FULLSCREEN" == *"fullscreen = 1"* ]]; then
    echo "   ✓ CORRECT"
else
    echo "   ✗ WRONG! Should be 'fullscreen = 1'"
    echo "   Current value: $FULLSCREEN"
fi

# Verify entrypoint
ENTRYPOINT=$(grep "^android.entrypoint" "$WSL_DIR/buildozer.spec" 2>/dev/null | head -1)
echo "Entrypoint: $ENTRYPOINT"
if [[ "$ENTRYPOINT" == *"FullscreenPythonActivity"* ]]; then
    echo "   ✓ CORRECT"
else
    echo "   ✗ WRONG! Should contain 'FullscreenPythonActivity'"
    echo "   Current value: $ENTRYPOINT"
fi

# Verify add_src
ADD_SRC=$(grep "^android.add_src" "$WSL_DIR/buildozer.spec" 2>/dev/null | head -1)
echo "Add src: $ADD_SRC"
if [[ "$ADD_SRC" == *"android_src"* ]]; then
    echo "   ✓ CORRECT"
else
    echo "   ✗ WRONG! Should contain 'android_src'"
    echo "   Current value: $ADD_SRC"
fi

# Verify Java file
if [ -f "$WSL_DIR/android_src/org/kivy/android/FullscreenPythonActivity.java" ]; then
    echo "Java file: EXISTS"
    echo "   ✓ CORRECT"
else
    echo "Java file: MISSING"
    echo "   ✗ WRONG! File should exist"
fi

echo ""
echo "=========================================="
echo "NEXT: Clean and rebuild"
echo "=========================================="
echo "Run these commands:"
echo "  cd ~/Roullett"
echo "  source ~/buildozer_env/bin/activate"
echo "  buildozer android clean"
echo "  buildozer android debug"
echo ""

