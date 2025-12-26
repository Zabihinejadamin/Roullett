#!/usr/bin/env python3
"""Patch buildozer to remove --user flag from pip install"""

file_path = '/home/aminz/buildozer_env/lib/python3.12/site-packages/buildozer/targets/android.py'

with open(file_path, 'r') as f:
    content = f.read()

# Replace the problematic line
old_pattern = 'options = ["--user"]'
new_pattern = 'options = []  # Patched: removed --user for venv compatibility'

if old_pattern in content:
    content = content.replace(old_pattern, new_pattern)
    with open(file_path, 'w') as f:
        f.write(content)
    print('SUCCESS: Patched buildozer to remove --user flag')
else:
    print('WARNING: Pattern not found. File may have been patched already or changed.')

