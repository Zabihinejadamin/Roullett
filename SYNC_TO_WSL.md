# How to Sync Code from Windows to WSL

When you edit code in Windows (e.g., in Cursor/VS Code), you need to sync it to WSL before building with buildozer.

## Quick Sync Commands

### Option 1: Manual Copy (One-time)

In WSL, run:
```bash
cp /mnt/c/Users/aminz/OneDrive/Documents/GitHub/Roullett/main.py ~/Roullett/
cp /mnt/c/Users/aminz/OneDrive/Documents/GitHub/Roullett/buildozer.spec ~/Roullett/
```

### Option 2: Sync Script (Recommended)

1. **Create the sync script** (already created: `sync_to_wsl.sh`)

2. **Run it before building:**
   ```bash
   # In WSL:
   bash /mnt/c/Users/aminz/OneDrive/Documents/GitHub/Roullett/sync_to_wsl.sh
   cd ~/Roullett
   buildozer android debug
   ```

### Option 3: One-Line Sync Command

Add this to your WSL `~/.bashrc` for easy access:
```bash
alias sync-roulette='cp /mnt/c/Users/aminz/OneDrive/Documents/GitHub/Roullett/{main.py,buildozer.spec} ~/Roullett/ && echo "Files synced!"'
```

Then just run:
```bash
sync-roulette
cd ~/Roullett
buildozer android debug
```

## What Gets Synced

The sync script copies:
- `main.py` - Your main application code
- `buildozer.spec` - Build configuration
- `requirements.txt` - Python dependencies (if exists)
- `sounds/` - Sound files directory
- `roulette_game/` - Game assets directory

## Important Notes

⚠️ **Always sync before building!** Buildozer uses files in the WSL directory (`~/Roullett`), NOT the Windows directory.

⚠️ **File locations:**
- **Windows:** `C:\Users\aminz\OneDrive\Documents\GitHub\Roullett\`
- **WSL:** `/home/aminz/Roullett/` (or `~/Roullett/`)

## Alternative: Work Directly in WSL

If you prefer, you can edit files directly in WSL using:
- `nano ~/Roullett/main.py`
- `vim ~/Roullett/main.py`
- Or use VS Code with WSL extension to edit WSL files directly

