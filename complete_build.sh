#!/bin/bash
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
export PATH=$JAVA_HOME/bin:~/buildozer_env/bin:/usr/local/bin:/usr/bin:/bin

echo "Starting build process..."
cd ~/Roullett

# The build will fail at pip install, but that's OK - it creates the dist
echo "Step 1: Running buildozer (will fail at pip install, but creates dist)..."
~/buildozer_env/bin/buildozer android debug 2>&1 | tee /tmp/build_attempt.log || true

# Wait a moment for files to be written
sleep 5

# Check if dist was created
DIST_DIR=~/.buildozer/android/platform/build-arm64-v8a_armeabi-v7a/dists/roulette
if [ -d "$DIST_DIR/src/main" ]; then
    echo "Step 2: Fixing manifest and copying Java file..."
    cd "$DIST_DIR/src/main"
    
    # Fix manifest
    python3 -c "
import re
with open('AndroidManifest.xml', 'r') as f:
    content = f.read()
content = content.replace(
    'android:theme=\"\"@android:style/Theme.NoTitleBar.Fullscreen\".Fullscreen\"',
    'android:theme=\"@android:style/Theme.NoTitleBar.Fullscreen\"'
)
with open('AndroidManifest.xml', 'w') as f:
    f.write(content)
print('Manifest fixed')
"
    
    # Copy Java file
    mkdir -p java/org/kivy/android
    cp ~/Roullett/android_src/org/kivy/android/FullscreenPythonActivity.java java/org/kivy/android/
    echo "Java file copied"
    
    # Step 3: Build with Gradle
    echo "Step 3: Building APK with Gradle..."
    cd "$DIST_DIR"
    ./gradlew assembleDebug
    
    # Step 4: Copy APK to bin
    if [ -f "build/outputs/apk/debug/roulette-debug.apk" ]; then
        mkdir -p ~/Roullett/bin
        cp build/outputs/apk/debug/roulette-debug.apk ~/Roullett/bin/roulette-0.1-arm64-v8a_armeabi-v7a-debug.apk
        echo "APK copied to bin directory!"
        ls -lh ~/Roullett/bin/*.apk
    fi
else
    echo "Dist directory not found. Checking build log..."
    tail -20 /tmp/build_attempt.log
fi

