# ⚠️ URGENT: Files Not Synced!

Your WSL buildozer.spec is **OUTDATED**. The sync didn't work!

## Current WSL Status (WRONG):
- `fullscreen = 0` ❌
- `android.entrypoint` is commented out ❌
- `android.add_src` is commented out ❌

## What It Should Be:
- `fullscreen = 1` ✅
- `android.entrypoint = org.kivy.android.FullscreenPythonActivity` ✅
- `android.add_src = android_src` ✅

## Fix It Now - Run This in WSL:

```bash
# Sync ALL files
WIN_DIR="/mnt/c/Users/aminz/OneDrive/Documents/GitHub/Roullett"
WSL_DIR="$HOME/Roullett"

echo "Syncing buildozer.spec..."
cp -v "$WIN_DIR/buildozer.spec" "$WSL_DIR/" || echo "FAILED!"

echo "Syncing main.py..."
cp -v "$WIN_DIR/main.py" "$WSL_DIR/" || echo "FAILED!"

echo "Syncing android_src/..."
[ -d "$WIN_DIR/android_src" ] && rm -rf "$WSL_DIR/android_src" && cp -rv "$WIN_DIR/android_src" "$WSL_DIR/" && echo "✓ android_src synced" || echo "✗ android_src FAILED!"

echo ""
echo "Verifying sync..."
echo "Checking fullscreen setting:"
grep "^fullscreen" "$WSL_DIR/buildozer.spec"
echo "Checking entrypoint:"
grep "^android.entrypoint" "$WSL_DIR/buildozer.spec"
echo "Checking add_src:"
grep "^android.add_src" "$WSL_DIR/buildozer.spec"
echo ""
echo "If you see the correct values above, sync worked!"
```

## After Syncing:

1. **Clean the build** (important!):
   ```bash
   cd ~/Roullett
   buildozer android clean
   ```

2. **Rebuild**:
   ```bash
   source ~/buildozer_env/bin/activate
   buildozer android debug
   ```

3. **Check the build output** for:
   ```
   --android-entrypoint org.kivy.android.FullscreenPythonActivity
   ```
   
   If you see `PythonActivity` instead, the sync still didn't work!

