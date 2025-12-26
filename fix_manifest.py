#!/usr/bin/env python3
"""Fix AndroidManifest.xml malformed theme attribute"""

import sys
import os

manifest_path = os.path.expanduser("~/Roullett/.buildozer/android/platform/build-arm64-v8a_armeabi-v7a/dists/roulette/src/main/AndroidManifest.xml")

if not os.path.exists(manifest_path):
    print(f"ERROR: Manifest not found at {manifest_path}")
    sys.exit(1)

with open(manifest_path, 'r') as f:
    content = f.read()

# Fix the malformed theme attribute
old_pattern = 'android:theme=""@android:style/Theme.NoTitleBar.Fullscreen".Fullscreen"'
new_pattern = 'android:theme="@android:style/Theme.NoTitleBar.Fullscreen"'

if old_pattern in content:
    content = content.replace(old_pattern, new_pattern)
    with open(manifest_path, 'w') as f:
        f.write(content)
    print("✓ Manifest fixed!")
else:
    print("Manifest doesn't contain the malformed pattern (may already be fixed)")

