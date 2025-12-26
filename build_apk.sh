#!/bin/bash
# Complete build script - Syncs files and builds APK
# Run in WSL: bash build_apk.sh

set -e  # Exit on error

WIN_DIR="/mnt/c/Users/aminz/Documents/GitHub/Roullett"
WSL_DIR="$HOME/Roullett"

echo "=========================================="
echo "COMPLETE BUILD PROCESS"
echo "=========================================="
echo ""

# Step 1: Sync files from Windows
echo "Step 1: Syncing files from Windows to WSL..."
mkdir -p "$WSL_DIR"
cp -f "$WIN_DIR/buildozer.spec" "$WSL_DIR/buildozer.spec" && echo "  ✓ buildozer.spec"
cp -f "$WIN_DIR/main.py" "$WSL_DIR/main.py" && echo "  ✓ main.py"
rm -rf "$WSL_DIR/android_src" 2>/dev/null
cp -rf "$WIN_DIR/android_src" "$WSL_DIR/android_src" && echo "  ✓ android_src/"
echo ""

# Step 2: Set up environment
echo "Step 2: Setting up build environment..."
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
export PATH=$JAVA_HOME/bin:~/buildozer_env/bin:/usr/local/bin:/usr/bin:/bin
export VIRTUAL_ENV=/home/aminz/buildozer_env

# Verify Java
echo "  Java version:"
javac -version 2>&1 | sed 's/^/    /'
echo ""

# Step 3: Build APK
echo "Step 3: Building APK (this will take 10-20 minutes)..."
cd "$WSL_DIR"
~/buildozer_env/bin/buildozer android debug 2>&1 | tee /tmp/build_output.log

echo ""
echo "=========================================="
echo "BUILD COMPLETE"
echo "=========================================="

# Check for APK
if [ -f "$WSL_DIR/bin"/*.apk ]; then
    echo "✓ APK found in: $WSL_DIR/bin/"
    ls -lh "$WSL_DIR/bin"/*.apk
elif [ -f "$WSL_DIR/.buildozer/android/platform/build-arm64-v8a_armeabi-v7a/dists/roulette/build/outputs/apk/debug/roulette-debug.apk" ]; then
    echo "✓ APK found in build directory"
    mkdir -p "$WSL_DIR/bin"
    cp "$WSL_DIR/.buildozer/android/platform/build-arm64-v8a_armeabi-v7a/dists/roulette/build/outputs/apk/debug/roulette-debug.apk" \
       "$WSL_DIR/bin/roulette-0.1-arm64-v8a_armeabi-v7a-debug.apk"
    ls -lh "$WSL_DIR/bin"/*.apk
else
    echo "✗ APK not found. Check build log: /tmp/build_output.log"
    echo "  Last 20 lines:"
    tail -20 /tmp/build_output.log | sed 's/^/    /'
fi

