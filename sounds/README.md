# Casino Roulette Sound Effects

This directory should contain the sound files for authentic casino roulette audio.

## 🎵 Professional Sound Effects Available:

**Recommended Source:** [Casino Roulette Sound Effects](https://www.youtube.com/watch?v=eNvV87Cbmi0)
- High-quality casino audio from YouTube
- Contains authentic roulette wheel sounds, ball rolling, and settling effects
- Perfect for creating an immersive casino experience

### How to Extract Sounds from YouTube:
1. Use a YouTube video downloader (like `yt-dlp` or online converters)
2. Download the video as MP4
3. Extract audio using FFmpeg or online audio extractors:
   ```bash
   ffmpeg -i video.mp4 -vn -acodec pcm_s16le -ar 44100 -ac 2 output.wav
   ```
4. Edit the audio file to extract individual sound effects:
   - Wheel spinning sound (continuous loop)
   - Ball launch click
   - Ball rolling/dropping sounds
   - Final settling click

## Required Sound Files:

### `wheel_spin.wav`
- **Duration:** 3-5 seconds (will loop)
- **Description:** Continuous whirring/buzzing sound of the roulette wheel spinning
- **When played:** When wheel starts spinning, loops until wheel stops

### `ball_launch.wav`
- **Duration:** 0.5-1 second
- **Description:** Sound of the ball being launched onto the wheel
- **When played:** When ball is launched from the center

### `ball_drop.wav`
- **Duration:** 0.3-0.8 second
- **Description:** Sound of the ball dropping from the bumper track to the number section
- **When played:** When ball transitions from bumper to numbers

### `ball_settle.wav`
- **Duration:** 0.2-0.5 second
- **Description:** Final click or settling sound when ball lands in a pocket
- **When played:** When ball stops and settles in winning pocket

### `casino_ambiance.wav` (Optional)
- **Duration:** 30+ seconds (will loop)
- **Description:** Background casino sounds (murmur of crowd, chips clinking, etc.)
- **When played:** Starts when app launches, plays continuously at low volume

## Sound File Specifications:
- **Format:** WAV preferred (also supports MP3, OGG)
- **Sample Rate:** 44100 Hz recommended
- **Channels:** Stereo or Mono
- **Bit Depth:** 16-bit recommended

## How to Add Sounds:
1. Place sound files in this `sounds/` directory
2. Ensure filenames match exactly as listed above
3. The game will automatically load and play them at the appropriate times

## Current Status:
✅ **Professional ball sound ONLY:** `a-roulette-ball-429831.mp3` - Plays when ball drops to numbers
✅ **Clean audio setup:** All generated sounds removed, using only professional audio

**Note:** The game now uses only your professional ball sound effect for maximum authenticity!
