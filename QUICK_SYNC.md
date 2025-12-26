# Quick Sync Guide

## ⚠️ IMPORTANT: Always Sync After Code Changes!

Every time code is changed in Windows, you MUST sync to WSL before building.

## Quick Sync Command (Copy-Paste This)

Run this in WSL:

```bash
cp /mnt/c/Users/aminz/OneDrive/Documents/GitHub/Roullett/main.py ~/Roullett/ && cp /mnt/c/Users/aminz/OneDrive/Documents/GitHub/Roullett/buildozer.spec ~/Roullett/ && [ -d /mnt/c/Users/aminz/OneDrive/Documents/GitHub/Roullett/android_src ] && rm -rf ~/Roullett/android_src && cp -r /mnt/c/Users/aminz/OneDrive/Documents/GitHub/Roullett/android_src ~/Roullett/ && echo "✓ Synced!" || echo "✗ Sync failed!"
```

## Or Use the Sync Script

```bash
bash /mnt/c/Users/aminz/OneDrive/Documents/GitHub/Roullett/sync-to-wsl.sh
```

## Set Up a Permanent Alias (One-Time Setup)

Add this to your WSL `~/.bashrc`:

```bash
echo 'alias sync-roulette="cp /mnt/c/Users/aminz/OneDrive/Documents/GitHub/Roullett/{main.py,buildozer.spec} ~/Roullett/ && [ -d /mnt/c/Users/aminz/OneDrive/Documents/GitHub/Roullett/android_src ] && rm -rf ~/Roullett/android_src && cp -r /mnt/c/Users/aminz/OneDrive/Documents/GitHub/Roullett/android_src ~/Roullett/ && echo \"✓ Synced!\""' >> ~/.bashrc
source ~/.bashrc
```

Then just run: `sync-roulette`

## What Gets Synced

- `main.py` - Your Python code
- `buildozer.spec` - Build configuration (CRITICAL for entrypoint!)
- `android_src/` - Custom Java activity (CRITICAL for fullscreen!)

## Build After Syncing

```bash
cd ~/Roullett
source ~/buildozer_env/bin/activate
buildozer android debug
```

