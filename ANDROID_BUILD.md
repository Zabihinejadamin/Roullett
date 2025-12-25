# How to Build and Run on Android (Windows Guide)

This guide will help you build an Android APK from your Kivy roulette game on Windows.

## Prerequisites for Windows

Since Buildozer doesn't work natively on Windows, you need to use **WSL (Windows Subsystem for Linux)**.

### Step 1: Install WSL (Windows Subsystem for Linux)

1. **Open PowerShell as Administrator** (Right-click Start → Windows PowerShell (Admin))

2. **Install WSL with Ubuntu**:
   ```powershell
   wsl --install
   ```
   
   Or if you have an older Windows version:
   ```powershell
   dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
   dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart
   ```
   Then restart and install Ubuntu from Microsoft Store.

3. **After installation, restart your computer**

4. **Open Ubuntu from Start Menu** and complete the initial setup (create username/password)

### Step 2: Set Up Buildozer in WSL

1. **Open Ubuntu (WSL)** from Start Menu

2. **Update packages**:
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

3. **Install required system dependencies**:
   ```bash
   sudo apt install -y git unzip openjdk-17-jdk python3-pip autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev
   ```

4. **Install Python dependencies and navigate to your project**:
   ```bash
   # First, check which Python/pip you're using
   which python3
   which pip3
   
   # Install buildozer and dependencies (try these in order)
   # Option 1: Install with --user flag
   pip3 install --user buildozer
   pip3 install --user Cython==0.29.33
   
   # Option 2: If that doesn't work, try without --user (requires sudo)
   # sudo pip3 install buildozer
   # sudo pip3 install Cython==0.29.33
   
   # Option 3: Use pip instead of pip3
   # pip install --user buildozer
   # pip install --user Cython==0.29.33
   
   # Verify installation location
   python3 -c "import sys; print('\n'.join(sys.path))"
   pip3 show buildozer
   
   # Add to PATH
   echo 'export PATH=$PATH:~/.local/bin' >> ~/.bashrc
   source ~/.bashrc
   
   # Navigate to your project directory
   cd /mnt/c/Users/aminz/Documents/GitHub/Roullett
   
   # Try different ways to run buildozer:
   # Method 1: Full path
   ~/.local/bin/buildozer --version
   
   # Method 2: Python module (if installed correctly)
   python3 -m buildozer --version
   
   # Method 3: Direct command (if PATH is set)
   buildozer --version
   ```
   
   **If still getting "No module named buildozer":**
   ```bash
   # Check if it's installed in a different location
   find ~ -name "buildozer" -type f 2>/dev/null
   
   # Reinstall with verbose output
   pip3 install --user --verbose buildozer
   
   # Or install globally (requires sudo)
   sudo pip3 install buildozer
   sudo pip3 install Cython==0.29.33
   ```

## Building the APK

### Step 3: Access Your Project in WSL

1. **In WSL Ubuntu, navigate to your Windows project folder**:
   ```bash
   # Your Windows C: drive is mounted at /mnt/c/
   cd /mnt/c/Users/aminz/Documents/GitHub/Roullett
   ```
   
   Or if your project is in a different location:
   ```bash
   cd /mnt/c/path/to/your/project
   ```

2. **Initialize buildozer** (if not already done):
   ```bash
   buildozer init
   ```
   (You already have buildozer.spec, so you can skip this)

3. **Build the APK**:
   ```bash
   buildozer android debug
   ```
   
   This will:
   - Download all dependencies
   - Compile Python for Android
   - Build the APK file
   - The APK will be created in `bin/roulette-0.1-arm64-v8a-debug.apk` (or similar path)

4. **For release build** (smaller file size):
   ```bash
   buildozer android release
   ```
   Note: Release builds require signing with a keystore.

## Installing on Android Device

### Method 1: Direct Transfer
1. Copy the APK file from `bin/` folder to your Android phone
2. On your phone, enable "Install from unknown sources" in Settings
3. Open the APK file and install

### Method 2: Using ADB (Android Debug Bridge)
1. Enable USB debugging on your Android phone
2. Connect phone via USB
3. Install ADB on your computer
4. Run:
   ```bash
   adb install bin/roulette-0.1-arm64-v8a-debug.apk
   ```

## Troubleshooting

### Common Issues:

1. **Build fails with "No module named 'buildozer'"**
   - Make sure buildozer is installed: `pip install buildozer`

2. **Sound files not included**
   - Make sure `source.include_exts` in buildozer.spec includes `mp3,wav`

3. **Build takes too long**
   - First build downloads many dependencies - this is normal and takes 30-60 minutes
   - Subsequent builds are much faster

4. **"Java not found" error**
   - Install Java JDK: `sudo apt install openjdk-17-jdk`

5. **Build on Windows**
   - ✅ Use WSL (Windows Subsystem for Linux) - **Recommended**
   - Use a Linux virtual machine (VirtualBox/VMware)
   - Use cloud build services
   - Buildozer doesn't work natively on Windows

### Alternative: Using WSL2 (Better Performance)

If you have WSL2 installed, it's faster:
```powershell
# Check WSL version
wsl --list --verbose

# Set default version to 2
wsl --set-default-version 2

# Convert existing WSL to version 2
wsl --set-version Ubuntu 2
```

### Alternative: Quick Test Without Building

You can also test your app on Android using **Kivy Launcher**:
1. Install "Kivy Launcher" from Google Play Store on your Android phone
2. Copy your `main.py` and `sounds/` folder to your phone
3. Open Kivy Launcher and select your main.py file
4. This is just for quick testing - not for distribution

## Alternative: Using GitHub Actions or CI/CD

You can also set up automated builds using GitHub Actions. This allows building on Linux servers without setting up your local environment.

## Notes

- The first build will take a long time (30-60 minutes) as it downloads Android SDK, NDK, and compiles Python
- The APK file will be quite large (50-100MB) as it includes Python and all dependencies
- Make sure your `sounds/` directory with audio files is in the project root

