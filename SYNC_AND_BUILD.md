# How to Sync and Build for Android

## Important: Always Sync Before Building!

Buildozer uses files in WSL (`~/Roullett`), NOT the Windows directory. You must sync your changes before building.

## Quick Sync and Build Commands

Run these commands in WSL:

```bash
# 1. Sync files from Windows to WSL
cp /mnt/c/Users/aminz/OneDrive/Documents/GitHub/Roullett/main.py ~/Roullett/
cp /mnt/c/Users/aminz/OneDrive/Documents/GitHub/Roullett/buildozer.spec ~/Roullett/
cp -r /mnt/c/Users/aminz/OneDrive/Documents/GitHub/Roullett/android_src ~/Roullett/ 2>/dev/null || true

# 2. Activate buildozer environment
source ~/buildozer_env/bin/activate

# 3. Build the APK
cd ~/Roullett
buildozer android debug

# 4. Copy APK back to Windows
cp bin/roulette-0.1-arm64-v8a_armeabi-v7a-debug.apk /mnt/c/Users/aminz/OneDrive/Documents/GitHub/Roullett/bin/
```

## What Gets Synced

- `main.py` - Your main application code
- `buildozer.spec` - Build configuration (IMPORTANT: contains entrypoint settings)
- `android_src/` - Custom Java activity for fullscreen (IMPORTANT: must be synced!)

## Verify Your Build

After building, check the build output for:
- `--android-entrypoint org.kivy.android.FullscreenPythonActivity` (should show this, NOT PythonActivity)
- No errors about missing Java files

If you see `--android-entrypoint org.kivy.android.PythonActivity`, the sync didn't work!

