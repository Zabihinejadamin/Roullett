#!/usr/bin/env python3
import re
import sys

manifest_path = sys.argv[1] if len(sys.argv) > 1 else '.buildozer/android/platform/build-arm64-v8a_armeabi-v7a/dists/roulette/src/main/AndroidManifest.xml'

try:
    with open(manifest_path, 'r') as f:
        content = f.read()
    
    # Fix the malformed theme attribute - use simple string replace
    original = content
    # Replace the exact malformed pattern
    bad_pattern = 'android:theme=""@android:style/Theme.NoTitleBar.Fullscreen".Fullscreen"'
    good_pattern = 'android:theme="@android:style/Theme.NoTitleBar.Fullscreen"'
    content = content.replace(bad_pattern, good_pattern)
    
    if content != original:
        with open(manifest_path, 'w') as f:
            f.write(content)
        print(f'✓ Fixed manifest: {manifest_path}')
    else:
        print(f'✓ Manifest already correct: {manifest_path}')
except Exception as e:
    print(f'✗ Error: {e}')
    sys.exit(1)

