#!/bin/bash
# CRITICAL FIX: This will properly sync all files
# Run this in WSL: bash /mnt/c/Users/aminz/OneDrive/Documents/GitHub/Roullett/FIX_SYNC.sh

WIN_DIR="/mnt/c/Users/aminz/OneDrive/Documents/GitHub/Roullett"
WSL_DIR="$HOME/Roullett"

echo "=========================================="
echo "FIXING SYNC - Copying files..."
echo "=========================================="

# Ensure WSL directory exists
mkdir -p "$WSL_DIR"

# Sync buildozer.spec (CRITICAL!)
echo "1. Syncing buildozer.spec..."
if [ -f "$WIN_DIR/buildozer.spec" ]; then
    cp -f "$WIN_DIR/buildozer.spec" "$WSL_DIR/buildozer.spec"
    echo "   ✓ buildozer.spec copied"
else
    echo "   ✗ ERROR: buildozer.spec not found in Windows!"
    exit 1
fi

# Sync main.py
echo "2. Syncing main.py..."
if [ -f "$WIN_DIR/main.py" ]; then
    cp -f "$WIN_DIR/main.py" "$WSL_DIR/main.py"
    echo "   ✓ main.py copied"
else
    echo "   ✗ ERROR: main.py not found in Windows!"
    exit 1
fi

# Sync android_src (CRITICAL!)
echo "3. Syncing android_src/..."
if [ -d "$WIN_DIR/android_src" ]; then
    rm -rf "$WSL_DIR/android_src" 2>/dev/null
    cp -rf "$WIN_DIR/android_src" "$WSL_DIR/android_src"
    echo "   ✓ android_src/ copied"
else
    echo "   ✗ ERROR: android_src/ not found in Windows!"
    exit 1
fi

echo ""
echo "=========================================="
echo "VERIFYING SYNC..."
echo "=========================================="

# Verify fullscreen
FULLSCREEN=$(grep "^fullscreen" "$WSL_DIR/buildozer.spec" | head -1)
echo "Fullscreen setting: $FULLSCREEN"
if [[ "$FULLSCREEN" == *"fullscreen = 1"* ]]; then
    echo "   ✓ fullscreen = 1 (CORRECT)"
else
    echo "   ✗ fullscreen is WRONG! Should be 'fullscreen = 1'"
fi

# Verify entrypoint
ENTRYPOINT=$(grep "^android.entrypoint" "$WSL_DIR/buildozer.spec" | head -1)
echo "Entrypoint setting: $ENTRYPOINT"
if [[ "$ENTRYPOINT" == *"FullscreenPythonActivity"* ]]; then
    echo "   ✓ Entrypoint is CORRECT"
else
    echo "   ✗ Entrypoint is WRONG! Should be 'android.entrypoint = org.kivy.android.FullscreenPythonActivity'"
fi

# Verify add_src
ADD_SRC=$(grep "^android.add_src" "$WSL_DIR/buildozer.spec" | head -1)
echo "Add src setting: $ADD_SRC"
if [[ "$ADD_SRC" == *"android_src"* ]]; then
    echo "   ✓ android.add_src is CORRECT"
else
    echo "   ✗ android.add_src is WRONG! Should be 'android.add_src = android_src'"
fi

# Verify Java file exists
if [ -f "$WSL_DIR/android_src/org/kivy/android/FullscreenPythonActivity.java" ]; then
    echo "   ✓ FullscreenPythonActivity.java exists"
else
    echo "   ✗ FullscreenPythonActivity.java MISSING!"
fi

echo ""
echo "=========================================="
echo "NEXT STEPS:"
echo "=========================================="
echo "1. If all checks passed (✓), run:"
echo "   cd ~/Roullett"
echo "   source ~/buildozer_env/bin/activate"
echo "   buildozer android clean"
echo "   buildozer android debug"
echo ""
echo "2. After build, check output for:"
echo "   --android-entrypoint org.kivy.android.FullscreenPythonActivity"
echo "   (NOT PythonActivity!)"
echo ""

