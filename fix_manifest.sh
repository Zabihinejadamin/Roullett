#!/bin/bash
# Fix AndroidManifest.xml and complete build

MANIFEST="$HOME/Roullett/.buildozer/android/platform/build-arm64-v8a_armeabi-v7a/dists/roulette/src/main/AndroidManifest.xml"

if [ ! -f "$MANIFEST" ]; then
    echo "ERROR: Manifest not found at $MANIFEST"
    exit 1
fi

echo "Fixing AndroidManifest.xml..."
python3 << 'PYEOF'
import re
import sys

manifest_path = sys.argv[1]

with open(manifest_path, 'r') as f:
    content = f.read()

# Fix the malformed theme attribute
content = content.replace(
    'android:theme=""@android:style/Theme.NoTitleBar.Fullscreen".Fullscreen"',
    'android:theme="@android:style/Theme.NoTitleBar.Fullscreen"'
)

with open(manifest_path, 'w') as f:
    f.write(content)

print('Manifest fixed!')
PYEOF "$MANIFEST"

echo ""
echo "Building APK with Gradle..."
cd "$HOME/Roullett/.buildozer/android/platform/build-arm64-v8a_armeabi-v7a/dists/roulette"
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
export PATH=$JAVA_HOME/bin:~/buildozer_env/bin:/usr/local/bin:/usr/bin:/bin

./gradlew assembleDebug

# Copy APK to bin
if [ -f "build/outputs/apk/debug/roulette-debug.apk" ]; then
    mkdir -p "$HOME/Roullett/bin"
    cp build/outputs/apk/debug/roulette-debug.apk "$HOME/Roullett/bin/roulette-0.1-arm64-v8a_armeabi-v7a-debug.apk"
    echo ""
    echo "✓ APK built successfully!"
    ls -lh "$HOME/Roullett/bin"/*.apk
else
    echo "✗ APK not found after build"
fi

