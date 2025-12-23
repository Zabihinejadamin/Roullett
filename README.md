# 2D Mobile Roulette Casino Game

A beautiful 2D European roulette simulation game for Android and iOS built with Kivy.

## Features

- **2D Roulette Wheel**: Beautiful circular roulette wheel with 37 pockets (0-36)
- **Color-Coded Pockets**: Red, black, and green pockets matching real roulette
- **Smooth Animations**: Realistic wheel spinning and ball physics
- **Mobile-Optimized**: Designed for touch screens and mobile devices
- **Cross-Platform**: Works on Android, iOS, Windows, macOS, and Linux

## Installation

### Desktop Testing

1. Install Python 3.8 or higher
2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the game:
```bash
python main.py
```

### Mobile Deployment (Android)

1. Install Buildozer:
```bash
pip install buildozer
```

2. Create `buildozer.spec` configuration (see below)

3. Build APK:
```bash
buildozer android debug
```

### Mobile Deployment (iOS)

1. Install Kivy iOS toolchain:
```bash
pip install kivy-ios
toolchain build python3 kivy
```

2. Create Xcode project and build

## Controls

- **SPIN Button**: Start spinning the roulette wheel
- **LAUNCH BALL Button**: Launch the ball onto the spinning wheel
- The wheel will automatically determine the winning number when it stops

## Game Rules

- European Roulette: 37 pockets (0, 1-36)
- 0 is green
- Red numbers: 1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36
- Black numbers: All other numbers (2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35)

## Project Structure

```
.
├── main.py              # Main game application
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## Building for Mobile

### Android (Buildozer)

Create a `buildozer.spec` file:

```ini
[app]
title = Roulette Casino
package.name = roulette
package.domain = com.roulette
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1
requirements = python3,kivy
orientation = portrait

[android]
permissions = INTERNET
```

Then run:
```bash
buildozer android debug
```

### iOS

Use Kivy iOS toolchain to create an Xcode project and build for iOS devices.

## License

Free to use and modify.


