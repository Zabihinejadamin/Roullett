#!/usr/bin/env python3
"""
2D Mobile Roulette Casino Game
A beautiful 2D European roulette simulation for Android and iOS using Kivy.
"""

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse, Line, Rectangle, PushMatrix, PopMatrix, Rotate, Triangle
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.core.text import Label as CoreLabel
from kivy.core.audio import SoundLoader
import math
import random
import os
try:
    import wave
    import struct
    WAVE_AVAILABLE = True
except ImportError:
    WAVE_AVAILABLE = False


class RouletteWheel(Widget):
    """2D Roulette Wheel Widget"""
    
    # European roulette numbers in proper order
    NUMBERS = [
        0, 32, 15, 19, 4, 21, 2, 25, 17, 34, 6, 27, 13, 36, 11, 30, 8, 23,
        10, 5, 24, 16, 33, 1, 20, 14, 31, 9, 22, 18, 29, 7, 28, 12, 35, 3, 26
    ]
    
    # Color mapping
    RED_NUMBERS = [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]
    BLACK_NUMBERS = [2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.angle = 0.0
        self.spinning = False
        self.spin_speed = 0.0
        self.winning_number = None
        self.ball_angle = 0.0
        self.ball_active = False
        self.ball_speed = 0.0
        self.ball_on_bumper = True  # Ball starts on bumper track
        self.ball_rotations = 0.0  # Track rotations on bumper
        self.ball_settled = False  # Ball has settled in pocket
        self.wheel_rotations_after_drop = 0.0  # Track wheel rotations after ball drops
        self.ball_has_dropped = False  # Flag when ball drops from bumper
        self.angle_per_pocket = 2 * math.pi / len(self.NUMBERS)  # Pre-calculate angle per pocket
        
    def get_pocket_color(self, number):
        """Get color for a pocket number - casino realistic colors"""
        if number == 0:
            return (0.0, 0.6, 0.0)  # Bright green for zero
        elif number in self.RED_NUMBERS:
            return (0.85, 0.15, 0.15)  # Casino red
        else:
            return (0.15, 0.15, 0.15)  # Deep black
    
    def start_spin(self):
        """Start spinning the wheel"""
        if not self.spinning:
            self.spinning = True
            self.spin_speed = random.uniform(5.0, 8.0)  # radians per second
            print("Wheel spinning!")
    
    def launch_ball(self):
        """Launch the ball on the bumper track"""
        if not self.ball_active:
            self.ball_active = True
            self.ball_on_bumper = True  # Start on bumper track
            self.ball_settled = False  # Reset settled flag
            self.ball_has_dropped = False  # Reset drop flag
            self.wheel_rotations_after_drop = 0.0  # Reset wheel rotation counter
            self.ball_angle = random.uniform(0, 2 * math.pi)
            self.ball_speed = random.uniform(8.0, 12.0)  # radians per second
            self.ball_rotations = 0.0  # Reset rotation counter
            print("Ball launched on bumper track!")
    
    def update(self, dt):
        """Update wheel and ball physics"""
        # Update wheel rotation
        if self.spinning:
            old_angle = self.angle
            self.angle += self.spin_speed * dt
            self.spin_speed *= 0.995  # Friction

            # Track wheel rotations after ball drops
            if self.ball_has_dropped:
                angle_diff = self.angle - old_angle
                if angle_diff < 0:  # Handle angle wraparound
                    angle_diff += 2 * math.pi
                self.wheel_rotations_after_drop += angle_diff / (2 * math.pi)

                # Stop wheel after exactly 1 rotation
                if self.wheel_rotations_after_drop >= 1.0:
                    self.spinning = False
                    self.spin_speed = 0.0

                    # Stop ball at the same time and determine winning pocket
                    if self.ball_active and not self.ball_on_bumper:
                        self.ball_active = False
                        self.ball_speed = 0.0
                        self.ball_settled = True
                        self.determine_ball_pocket()
                        # Snap ball to the exact center of the winning pocket
                        if self.winning_number is not None:
                            pocket_index = self.NUMBERS.index(self.winning_number)
                            self.ball_angle = self.angle + (pocket_index * self.angle_per_pocket)

                        # Play ball settle sound
                        if hasattr(self, 'game') and self.game.ball_settle_sound:
                            self.game.ball_settle_sound.play()

                    print(f"Wheel and ball stopped after {self.wheel_rotations_after_drop:.1f} rotations!")

                    # Stop wheel spinning sound
                    if hasattr(self, 'game') and self.game.wheel_spin_sound:
                        self.game.wheel_spin_sound.stop()
            elif self.spin_speed < 0.05:  # Fallback if ball hasn't dropped yet
                self.spinning = False
                self.spin_speed = 0.0
                print("Wheel stopped!")
        
        # Update ball
        if self.ball_active:
            # Ball drops from bumper to number section after some time
            if self.ball_on_bumper:
                old_angle = self.ball_angle
                self.ball_angle += self.ball_speed * dt

                # Track rotations on bumper
                angle_diff = self.ball_angle - old_angle
                if angle_diff < 0:  # Handle angle wraparound
                    angle_diff += 2 * math.pi
                self.ball_rotations += angle_diff / (2 * math.pi)

                # Only allow drop after at least 3 full rotations
                if self.ball_rotations >= 3.0:
                    # Chance to drop from bumper to number section (more likely as speed decreases)
                    drop_chance = (12.0 - self.ball_speed) / 12.0 * 0.02  # Small chance based on speed
                    if random.random() < drop_chance * dt * 60:  # Scale by framerate
                        self.ball_on_bumper = False
                        self.ball_has_dropped = True  # Mark that ball has dropped
                        self.ball_speed *= 0.7  # Speed reduction when dropping
                        print(f"Ball dropped from bumper to number section after {self.ball_rotations:.1f} rotations!")

                        # Play ball drop sound
                        if hasattr(self, 'game') and self.game.ball_drop_sound:
                            self.game.ball_drop_sound.play()

                self.ball_speed *= 0.995  # Light friction on bumper track
            else:
                # Ball on number section - moves with wheel and slows down
                self.ball_angle += (self.ball_speed + self.spin_speed) * dt  # Ball moves with wheel
                self.ball_speed *= 0.97  # More friction on number section

            # Ball stops only when wheel stops after 4 rotations (handled above)
            # No separate ball stopping condition needed
        
        self.canvas.clear()
        self.draw()
    
    def determine_winning_number(self):
        """Determine winning number based on wheel angle"""
        # Normalize angle to 0-2π
        normalized_angle = self.angle % (2 * math.pi)
        if normalized_angle < 0:
            normalized_angle += 2 * math.pi

        # Calculate which pocket (accounting for rotation direction)
        num_pockets = len(self.NUMBERS)
        pocket_index = int((normalized_angle / (2 * math.pi)) * num_pockets)
        pocket_index = num_pockets - pocket_index - 1  # Reverse for clockwise
        pocket_index = pocket_index % num_pockets

        self.winning_number = self.NUMBERS[pocket_index]
        return self.winning_number

    def determine_ball_pocket(self):
        """Determine which pocket the ball settled in based on ball angle relative to wheel"""
        # Calculate relative angle between ball and wheel
        relative_angle = (self.ball_angle - self.angle) % (2 * math.pi)
        if relative_angle < 0:
            relative_angle += 2 * math.pi

        # Calculate which pocket the ball is in
        num_pockets = len(self.NUMBERS)
        pocket_index = int((relative_angle / (2 * math.pi)) * num_pockets)
        pocket_index = pocket_index % num_pockets

        self.winning_number = self.NUMBERS[pocket_index]
        print(f"Ball settled in pocket: {self.winning_number}")
        return self.winning_number
    
    def draw(self):
        """Draw the roulette wheel with casino-style realism"""
        center_x = self.width / 2
        center_y = self.height / 2
        radius = min(self.width, self.height) * 0.38  # Wheel size
        bumper_outer = radius * 1.15  # Outer bumper track
        bumper_inner = radius * 0.98  # Inner edge of bumper
        inner_radius = radius * 0.65  # Inner circle
        pocket_outer = radius * 0.90  # Pocket outer edge (moved inward)
        pocket_inner = radius * 0.70  # Pocket inner edge
        
        num_pockets = len(self.NUMBERS)
        
        # Draw casino green felt background with texture
        with self.canvas:
            # Base felt color
            Color(0.05, 0.25, 0.1, 1)  # Casino green felt
            Rectangle(pos=(0, 0), size=(self.width, self.height))

            # Felt texture (subtle pattern)
            Color(0.08, 0.3, 0.12, 0.3)  # Slightly lighter green
            for i in range(0, int(self.width), 20):
                for j in range(0, int(self.height), 20):
                    Ellipse(pos=(i, j), size=(2, 2))

            # Table border
            Color(0.4, 0.25, 0.1, 1)  # Wood border
            Line(rectangle=(0, 0, self.width, self.height), width=8)

            # Inner border highlight
            Color(0.5, 0.35, 0.15, 1)  # Lighter wood
            Line(rectangle=(4, 4, self.width-8, self.height-8), width=2)

        # Draw outer bumper track (raised margin) with wood grain
        with self.canvas:
            # Bumper track base (dark mahogany wood)
            Color(0.15, 0.08, 0.04, 1)  # Deep mahogany
            Ellipse(pos=(center_x - bumper_outer, center_y - bumper_outer),
                   size=(bumper_outer * 2, bumper_outer * 2))

            # Wood grain layers for texture
            Color(0.25, 0.12, 0.06, 1)  # Medium mahogany
            Line(circle=(center_x, center_y, bumper_outer), width=6)
            Line(circle=(center_x, center_y, bumper_inner + 2), width=4)

            # Wood highlights
            Color(0.35, 0.18, 0.08, 1)  # Lighter mahogany
            Line(circle=(center_x, center_y, bumper_outer - 1), width=2)
            Line(circle=(center_x, center_y, bumper_inner + 1), width=2)

            # Metallic rim
            Color(0.6, 0.5, 0.3, 1)  # Antique brass
            Line(circle=(center_x, center_y, bumper_outer), width=1)
            Line(circle=(center_x, center_y, bumper_inner), width=1)

        # Draw outer wheel rim (polished mahogany wood)
        with self.canvas:
            # Base wood layer
            Color(0.22, 0.12, 0.06, 1)  # Rich mahogany base
            Ellipse(pos=(center_x - radius, center_y - radius),
                   size=(radius * 2, radius * 2))

            # Wood grain rings for texture
            Color(0.28, 0.16, 0.08, 1)  # Medium mahogany
            Line(circle=(center_x, center_y, radius), width=4)
            Line(circle=(center_x, center_y, radius * 0.95), width=3)

            # Wood highlights and grain
            Color(0.38, 0.22, 0.10, 1)  # Light mahogany
            Line(circle=(center_x, center_y, radius - 1), width=2)
            Line(circle=(center_x, center_y, radius * 0.96), width=1)

            # Polished wood shine
            Color(0.5, 0.3, 0.15, 0.8)  # Warm highlight
            Line(circle=(center_x, center_y, radius - 0.5), width=1)
        
        # Draw inner center circle with wood inlay
        with self.canvas:
            # Dark wood center
            Color(0.18, 0.09, 0.05, 1)  # Very dark mahogany
            Ellipse(pos=(center_x - inner_radius, center_y - inner_radius),
                   size=(inner_radius * 2, inner_radius * 2))

            # Decorative wood inlay
            Color(0.3, 0.15, 0.07, 1)  # Medium dark mahogany
            Line(circle=(center_x, center_y, inner_radius), width=2)
            Line(circle=(center_x, center_y, inner_radius * 0.8), width=2)

            # Center hub detail
            Color(0.4, 0.2, 0.08, 1)  # Lighter wood
            Ellipse(pos=(center_x - inner_radius * 0.3, center_y - inner_radius * 0.3),
                   size=(inner_radius * 0.6, inner_radius * 0.6))
        
        # Draw pockets with rotation
        with self.canvas:
            PushMatrix()
            Rotate(angle=math.degrees(self.angle), origin=(center_x, center_y))
            
            for i, number in enumerate(self.NUMBERS):
                angle = i * self.angle_per_pocket
                angle_start = angle - self.angle_per_pocket / 2
                angle_end = angle + self.angle_per_pocket / 2
                
                # Get pocket color
                color = self.get_pocket_color(number)
                
                # Draw pocket filled segment using multiple small rectangles
                Color(*color, 0.95)
                # Draw pocket as filled arc using multiple segments
                segments = 12
                for j in range(segments):
                    a1 = angle_start + (angle_end - angle_start) * (j / segments)
                    a2 = angle_start + (angle_end - angle_start) * ((j + 1) / segments)
                    
                    # Outer points
                    x1_outer = center_x + math.cos(a1) * pocket_outer
                    y1_outer = center_y + math.sin(a1) * pocket_outer
                    x2_outer = center_x + math.cos(a2) * pocket_outer
                    y2_outer = center_y + math.sin(a2) * pocket_outer
                    
                    # Inner points
                    x1_inner = center_x + math.cos(a1) * pocket_inner
                    y1_inner = center_y + math.sin(a1) * pocket_inner
                    x2_inner = center_x + math.cos(a2) * pocket_inner
                    y2_inner = center_y + math.sin(a2) * pocket_inner
                    
                    # Draw as quad using two triangles
                    Triangle(points=[x1_outer, y1_outer, x2_outer, y2_outer, x1_inner, y1_inner])
                    Triangle(points=[x2_outer, y2_outer, x2_inner, y2_inner, x1_inner, y1_inner])
                
                # Draw pocket divider (metallic gold separator)
                # Main gold divider
                Color(0.9, 0.75, 0.2, 1)  # Bright gold
                x1 = center_x + math.cos(angle_start) * pocket_outer
                y1 = center_y + math.sin(angle_start) * pocket_outer
                x2 = center_x + math.cos(angle_start) * pocket_inner
                y2 = center_y + math.sin(angle_start) * pocket_inner
                Line(points=[x1, y1, x2, y2], width=3)

                # Gold highlight
                Color(1.0, 0.9, 0.4, 1)  # Light gold highlight
                Line(points=[x1, y1, x2, y2], width=1)

                # Metallic shadow
                Color(0.6, 0.45, 0.1, 0.8)  # Darker gold
                offset_x = math.cos(angle_start + math.pi/2) * 0.5
                offset_y = math.sin(angle_start + math.pi/2) * 0.5
                Line(points=[x1 + offset_x, y1 + offset_y, x2 + offset_x, y2 + offset_y], width=1)
                
                # Draw number on pocket
                number_angle = angle
                number_radius = (pocket_outer + pocket_inner) / 2
                number_x = center_x + math.cos(number_angle) * number_radius
                number_y = center_y + math.sin(number_angle) * number_radius
                
                # Create text label for number
                text_label = CoreLabel(text=str(number), font_size=14, 
                                     color=(1, 1, 1, 1) if number != 0 else (1, 1, 0.5, 1))
                text_label.refresh()
                text_texture = text_label.texture
                
                # Draw number background circle
                Color(0.2, 0.2, 0.2, 0.8)  # Dark background
                Ellipse(pos=(number_x - 12, number_y - 12), size=(24, 24))
                
                # Draw number text
                Color(1, 1, 1, 1)
                Rectangle(texture=text_texture, 
                         pos=(number_x - text_texture.width/2, number_y - text_texture.height/2),
                         size=text_texture.size)
            
            PopMatrix()
        
        # Draw ball with realistic appearance
        if self.ball_active or self.ball_settled:
            with self.canvas:
                if self.ball_settled:
                    # Ball settled in pocket - keep it at its final position
                    ball_track_radius = pocket_inner + 8  # Position inside the pocket
                    ball_angle = self.ball_angle  # Keep ball at its settled position
                elif self.ball_on_bumper:
                    # Ball on bumper track (outer margin)
                    ball_track_radius = (bumper_outer + bumper_inner) / 2  # Middle of bumper track
                    ball_angle = self.ball_angle
                else:
                    # Ball on inner track (pockets section) - moves between pocket edges
                    # Ball gradually moves inward as it slows down
                    progress_to_stop = max(0, (self.ball_speed - 0.1) / 2.0)  # 0 to 1 as ball slows
                    ball_track_radius = pocket_outer - (pocket_outer - pocket_inner) * (1 - progress_to_stop)
                    ball_angle = self.ball_angle

                ball_x = center_x + math.cos(ball_angle) * ball_track_radius
                ball_y = center_y + math.sin(ball_angle) * ball_track_radius
                ball_size = 18
                
                # Ball shadow (more realistic)
                Color(0, 0, 0, 0.4)
                Ellipse(pos=(ball_x - ball_size/2 + 3, ball_y - ball_size/2 - 1),
                        size=(ball_size, ball_size))

                # Ball base (warm ivory)
                Color(0.95, 0.92, 0.85, 1)  # Warm ivory base
                Ellipse(pos=(ball_x - ball_size/2, ball_y - ball_size/2),
                       size=(ball_size, ball_size))

                # Ball main body (polished ivory)
                Color(0.98, 0.96, 0.92, 1)  # Polished ivory
                Ellipse(pos=(ball_x - ball_size/2 + 0.5, ball_y - ball_size/2 + 0.5),
                       size=(ball_size - 1, ball_size - 1))

                # Primary highlight (top-left)
                Color(1.0, 1.0, 1.0, 0.8)
                Ellipse(pos=(ball_x - ball_size/3, ball_y - ball_size/4),
                       size=(ball_size/3, ball_size/3))

                # Secondary highlight (brighter spot)
                Color(1.0, 1.0, 1.0, 0.9)
                Ellipse(pos=(ball_x - ball_size/4, ball_y - ball_size/6),
                       size=(ball_size/6, ball_size/6))

                # Subtle shadow on the bottom
                Color(0.8, 0.75, 0.7, 0.3)
                Ellipse(pos=(ball_x - ball_size/4, ball_y + ball_size/6),
                       size=(ball_size/4, ball_size/4))
        
        # Draw center marker (metallic pointer)
        with self.canvas:
            pointer_size = 22

            # Pointer shadow
            Color(0, 0, 0, 0.4)
            shadow_points = [
                center_x, center_y + inner_radius + 6,
                center_x - pointer_size/2 + 1, center_y + inner_radius - 9,
                center_x + pointer_size/2 + 1, center_y + inner_radius - 9
            ]
            Triangle(points=shadow_points)

            # Main pointer body (brass/metal)
            Color(0.8, 0.6, 0.2, 1)  # Antique brass
            pointer_points = [
                center_x, center_y + inner_radius + 5,
                center_x - pointer_size/2, center_y + inner_radius - 10,
                center_x + pointer_size/2, center_y + inner_radius - 10
            ]
            Triangle(points=pointer_points)

            # Metallic highlight
            Color(0.95, 0.8, 0.3, 1)  # Bright brass highlight
            highlight_points = [
                center_x, center_y + inner_radius + 4,
                center_x - pointer_size/4, center_y + inner_radius - 5,
                center_x + pointer_size/4, center_y + inner_radius - 5
            ]
            Triangle(points=highlight_points)

            # Pointer tip accent
            Color(1.0, 0.9, 0.1, 1)  # Gold tip
            tip_points = [
                center_x, center_y + inner_radius + 3,
                center_x - pointer_size/6, center_y + inner_radius - 2,
                center_x + pointer_size/6, center_y + inner_radius - 2
            ]
            Triangle(points=tip_points)


class RouletteGame(BoxLayout):
    """Main game layout"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 10
        self.spacing = 10
        
        # Game state (must be set before create_ui)
        self.balance = 1000
        self.last_win = None

        # Initialize casino sounds
        self.load_sounds()
        
        # Create wheel
        self.wheel = RouletteWheel()
        self.wheel.game = self  # Give wheel reference to game for sound access
        
        # Create UI
        self.create_ui()
        
        # Start update loop
        Clock.schedule_interval(self.update, 1.0 / 60.0)  # 60 FPS

        # Bind keyboard events
        Window.bind(on_key_down=self.on_key_down)

    def load_sounds(self):
        """Load casino sound effects"""
        # Try to load sound files first
        self.wheel_spin_sound = SoundLoader.load('sounds/wheel_spin.wav')
        self.ball_launch_sound = SoundLoader.load('sounds/ball_launch.wav')
        self.ball_drop_sound = SoundLoader.load('sounds/ball_drop.wav')
        self.ball_settle_sound = SoundLoader.load('sounds/ball_settle.wav')
        self.casino_ambiance = SoundLoader.load('sounds/casino_ambiance.wav')

        # If sound files don't exist, create simple beep sounds
        if not all([self.wheel_spin_sound, self.ball_launch_sound, self.ball_drop_sound, self.ball_settle_sound]):
            print("Sound files not found, using system beep sounds...")
            self.create_beep_functions()

        # Set sound properties for loaded sounds
        if self.wheel_spin_sound:
            self.wheel_spin_sound.loop = True
        if self.casino_ambiance:
            self.casino_ambiance.loop = True
            self.casino_ambiance.volume = 0.3

    def create_simple_sounds(self):
        """Create simple beep sounds programmatically"""
        # Create sounds directory if it doesn't exist
        os.makedirs('sounds', exist_ok=True)

        # Try to create WAV files, fallback to system beeps
        if WAVE_AVAILABLE:
            try:
                # Create simple beep sounds
                self.create_beep_sound('sounds/wheel_spin.wav', frequency=200, duration=2.0, volume=0.3)
                self.create_beep_sound('sounds/ball_launch.wav', frequency=800, duration=0.2, volume=0.5)
                self.create_beep_sound('sounds/ball_drop.wav', frequency=600, duration=0.3, volume=0.4)
                self.create_beep_sound('sounds/ball_settle.wav', frequency=1000, duration=0.1, volume=0.6)
                self.create_beep_sound('sounds/casino_ambiance.wav', frequency=150, duration=1.0, volume=0.1)

                # Reload the sounds after creating them
                self.wheel_spin_sound = SoundLoader.load('sounds/wheel_spin.wav')
                self.ball_launch_sound = SoundLoader.load('sounds/ball_launch.wav')
                self.ball_drop_sound = SoundLoader.load('sounds/ball_drop.wav')
                self.ball_settle_sound = SoundLoader.load('sounds/ball_settle.wav')
                self.casino_ambiance = SoundLoader.load('sounds/casino_ambiance.wav')

                print("Generated casino sound effects!")
                return
            except Exception as e:
                print(f"Failed to generate WAV files: {e}")

        # Fallback: Create simple system beep functions
        print("Using system beep sounds...")
        self.create_beep_functions()

    def create_beep_sound(self, filename, frequency=440, duration=0.5, volume=0.5):
        """Create a simple beep sound programmatically"""
        sample_rate = 44100
        num_samples = int(sample_rate * duration)

        # Create sine wave
        samples = []
        for i in range(num_samples):
            # Create a fading envelope to avoid clicks
            envelope = min(i / 1000, (num_samples - i) / 1000, 1.0)
            sample = volume * envelope * math.sin(2 * math.pi * frequency * i / sample_rate)
            samples.append(int(sample * 32767))

        # Write WAV file
        with wave.open(filename, 'wb') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(sample_rate)

            # Convert to bytes
            for sample in samples:
                wav_file.writeframes(struct.pack('<h', sample))

    def create_beep_functions(self):
        """Create beep functions using system sounds"""
        import platform

        def system_beep(frequency=800, duration=200):
            """Play a system beep asynchronously"""
            try:
                if platform.system() == 'Windows':
                    import winsound
                    import threading
                    # Play beep in a separate thread to avoid blocking
                    threading.Thread(target=winsound.Beep, args=(frequency, duration), daemon=True).start()
                else:
                    # For other systems, use a simple print (could be extended)
                    print(f"\\a")  # ASCII bell
            except:
                print(f"\\a")  # Fallback to ASCII bell

        # Create mock sound objects
        class MockSound:
            def __init__(self, play_func, loop=False):
                self.play_func = play_func
                self.loop = loop

            def play(self):
                self.play_func()

            def stop(self):
                pass

        self.wheel_spin_sound = MockSound(lambda: system_beep(200, 1000), loop=True)
        self.ball_launch_sound = MockSound(lambda: system_beep(1000, 150))
        self.ball_drop_sound = MockSound(lambda: system_beep(800, 200))
        self.ball_settle_sound = MockSound(lambda: system_beep(1200, 100))
        self.casino_ambiance = None  # No ambiance for system beeps
    
    def create_ui(self):
        """Create casino-style game UI"""
        # Set background color to casino green
        with self.canvas.before:
            Color(0.05, 0.25, 0.1, 1)  # Casino green felt
            Rectangle(pos=self.pos, size=self.size)

        # Result display at top
        result_container = BoxLayout(size_hint_y=0.15, padding=20)
        self.result_label = Label(text='PRESS SPACE TO START', font_size=32,
                                 color=(1, 1, 0.8, 1), bold=True,  # Bright gold
                                 halign='center', valign='middle')
        self.result_label.bind(size=self.result_label.setter('text_size'))
        result_container.add_widget(self.result_label)
        self.add_widget(result_container)

        # Wheel container (takes up most of the screen)
        wheel_container = BoxLayout(size_hint_y=0.85, padding=5)
        wheel_container.add_widget(self.wheel)
        self.add_widget(wheel_container)
    
    def on_spin(self, instance):
        """Handle spin button press"""
        self.wheel.start_spin()
    
    def on_launch_ball(self, instance):
        """Handle launch ball button press"""
        self.wheel.launch_ball()

    def on_key_down(self, window, key, scancode, codepoint, modifier):
        """Handle keyboard input"""
        if key == 32:  # Spacebar
            if not self.wheel.spinning and not self.wheel.ball_active:
                # Start the sequence: spin wheel and launch ball
                self.wheel.start_spin()
                self.wheel.launch_ball()
                self.result_label.text = 'SPINNING...'
                self.result_label.color = (1, 1, 0.8, 1)  # Gold

                # Play wheel spin sound
                if self.wheel_spin_sound:
                    self.wheel_spin_sound.play()
            elif self.wheel.spinning and not self.wheel.ball_active:
                # Launch ball if wheel is spinning but ball isn't active
                self.wheel.launch_ball()

                # Play ball launch sound
                if self.ball_launch_sound:
                    self.ball_launch_sound.play()
    
    def update(self, dt):
        """Update game loop"""
        self.wheel.update(dt)

        # Update result display
        if self.wheel.winning_number is not None and self.wheel.winning_number != self.last_win:
            self.last_win = self.wheel.winning_number
            color = self.wheel.get_pocket_color(self.last_win)
            color_name = "GREEN" if self.last_win == 0 else ("RED" if self.last_win in self.wheel.RED_NUMBERS else "BLACK")

            # Update result label prominently
            self.result_label.text = f'WINNING NUMBER: {self.last_win} ({color_name})'
            # Set text color based on pocket color
            if self.last_win == 0:
                self.result_label.color = (0.3, 1.0, 0.3, 1)  # Bright green
            elif self.last_win in self.wheel.RED_NUMBERS:
                self.result_label.color = (1.0, 0.3, 0.3, 1)  # Bright red
            else:
                self.result_label.color = (0.9, 0.9, 0.9, 1)  # Light gray/white
        elif self.wheel.spinning or self.wheel.ball_active:
            # Show spinning status
            if self.wheel.ball_on_bumper:
                rotations = int(self.wheel.ball_rotations)
                self.result_label.text = f'BALL SPINNING... {rotations} ROTATIONS'
                self.result_label.color = (1, 1, 0.8, 1)  # Gold
            else:
                self.result_label.text = 'BALL ON NUMBERS...'
                self.result_label.color = (1, 1, 0.8, 1)  # Gold


class RouletteApp(App):
    """Main Kivy App"""
    
    def build(self):
        # Set window size for mobile (can be fullscreen on actual device)
        Window.size = (450, 700)  # Portrait mode for mobile - larger for better visibility
        Window.clearcolor = (0.05, 0.25, 0.1, 1)  # Casino green background
        
        # Create game
        game = RouletteGame()
        return game
    
    def on_start(self):
        """Called when app starts"""
        print("Roulette game started!")

        # Start casino ambiance
        if hasattr(self, 'casino_ambiance') and self.casino_ambiance:
            self.casino_ambiance.play()
    
    def on_pause(self):
        """Called when app is paused (mobile)"""
        return True
    
    def on_resume(self):
        """Called when app resumes (mobile)"""
        pass


if __name__ == '__main__':
    RouletteApp().run()

