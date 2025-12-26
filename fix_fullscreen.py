#!/usr/bin/env python3
"""
Post-build script to force fullscreen in AndroidManifest.xml
This script modifies the manifest to ensure fullscreen mode
"""
import os
import sys
import xml.etree.ElementTree as ET

def fix_manifest(manifest_path):
    """Modify AndroidManifest.xml to force fullscreen"""
    if not os.path.exists(manifest_path):
        print(f"Manifest not found: {manifest_path}")
        return False
    
    try:
        # Parse the manifest
        tree = ET.parse(manifest_path)
        root = tree.getroot()
        
        # Find the activity
        activity = root.find('.//{http://schemas.android.com/apk/res/android}activity')
        if activity is None:
            # Try without namespace
            activity = root.find('.//activity')
        
        if activity is None:
            print("Could not find activity in manifest")
            return False
        
        # Add or modify theme to force fullscreen
        activity.set('{http://schemas.android.com/apk/res/android}theme', 
                    '@android:style/Theme.NoTitleBar.Fullscreen')
        
        # Add windowSoftInputMode if not present
        if '{http://schemas.android.com/apk/res/android}windowSoftInputMode' not in activity.attrib:
            activity.set('{http://schemas.android.com/apk/res/android}windowSoftInputMode', 
                        'adjustResize')
        
        # Save the modified manifest
        tree.write(manifest_path, encoding='utf-8', xml_declaration=True)
        print(f"Successfully modified manifest: {manifest_path}")
        return True
        
    except Exception as e:
        print(f"Error modifying manifest: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    # Default manifest path (adjust if needed)
    manifest_path = sys.argv[1] if len(sys.argv) > 1 else None
    
    if manifest_path:
        fix_manifest(manifest_path)
    else:
        print("Usage: python fix_fullscreen.py <path_to_AndroidManifest.xml>")

