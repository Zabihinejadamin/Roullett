#!/usr/bin/env python3
"""
2D Mobile Roulette Casino Game
A beautiful 2D European roulette simulation for Android and iOS using Kivy.
"""

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse, Line, Rectangle, PushMatrix, PopMatrix, Rotate, Triangle, InstructionGroup, Translate, Scale
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.popup import Popup
from kivy.core.text import Label as CoreLabel
from kivy.core.audio import SoundLoader
from kivy.core.image import Image as CoreImage
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
        self.spin_start_time = 0.0  # Track when spinning started (for timeout)
        self.max_spin_time = 30.0  # Maximum spin time in seconds (safety timeout)
        self.prev_ball_angle = 0.0  # Previous ball angle for interpolation
        self.prev_wheel_angle = 0.0  # Previous wheel angle for interpolation

        # Create win text box in center of roulette frame
        self.create_win_text_box()

        # Previous numbers data and cached textures
        self.previous_numbers_data = []
        self.previous_numbers_textures = []
        
        # Load background texture for roulette frame
        self.background_texture = None
        texture_path = r'C:\Users\aminz\OneDrive\Documents\GitHub\Roullett\roulette_game\assets\textures\close-up-wood-texture.jpg'
        
        if os.path.exists(texture_path):
            try:
                img = CoreImage(texture_path)
                self.background_texture = img.texture
                print(f"✓✓✓ SUCCESS: Loaded roulette background texture from: {os.path.abspath(texture_path)}")
                print(f"  Texture size: {self.background_texture.size}")
            except Exception as e:
                print(f"✗ Failed to load texture from {texture_path}: {e}")
        else:
            print(f"✗✗✗ WARNING: Texture file not found at: {texture_path}")
            print("  Falling back to solid blue-gray color.")


    def create_win_text_box(self):
        """Create a text box in the center of the roulette frame"""
        # Create a label positioned in the center of the wheel
        self.win_text_label = Label(
            text="",
            font_size=36,
            color=(1, 0.9, 0, 1),  # Bright gold color
            bold=True,
            halign='center',
            valign='middle',
            size_hint=(None, None),
            size=(200, 60),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        self.win_text_label.bind(size=self.win_text_label.setter('text_size'))

        # Add to wheel widget
        self.add_widget(self.win_text_label)




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
            self.spin_start_time = 0.0  # Will be set in update() with Clock.get_time()
            print("Wheel spinning!")
    
    def launch_ball(self):
        """Launch the ball on the bumper track"""
        if not self.ball_active:
            self.ball_active = True
            self.ball_on_bumper = True  # Start on bumper track
            self.ball_settled = False  # Reset settled flag
            self.ball_has_dropped = False  # Reset drop flag
            self.wheel_rotations_after_drop = 0.0  # Reset wheel rotation counter
            self.spin_start_time = 0.0  # Reset spin timer
            self.ball_angle = random.uniform(0, 2 * math.pi)
            self.ball_speed = random.uniform(8.0, 12.0)  # radians per second
            self.ball_rotations = 0.0  # Reset rotation counter
            print("Ball launched on bumper track!")
    
    def update(self, dt):
        """Update wheel and ball physics"""
        # Track spin start time for timeout
        if self.spinning and self.spin_start_time == 0.0:
            self.spin_start_time = Clock.get_time()
        
        # Emergency timeout: Force stop if spinning too long (30 seconds)
        if self.spinning and self.spin_start_time > 0.0:
            elapsed_time = Clock.get_time() - self.spin_start_time
            if elapsed_time > self.max_spin_time:
                print(f"⚠️ EMERGENCY STOP: Spinning for {elapsed_time:.1f} seconds, forcing stop!")
                self.spinning = False
                self.spin_speed = 0.0
                if self.ball_active:
                    self.ball_active = False
                    self.ball_speed = 0.0
                    self.ball_settled = True
                    if not self.ball_has_dropped:
                        self.ball_has_dropped = True
                        self.ball_on_bumper = False
                    self.determine_ball_pocket()
                    if self.winning_number is not None:
                        pocket_index = self.NUMBERS.index(self.winning_number)
                        self.ball_angle = (self.angle + (pocket_index * self.angle_per_pocket)) % (2 * math.pi)
        
        # Update wheel rotation
        if self.spinning:
            old_angle = self.angle
            self.prev_wheel_angle = self.angle
            self.angle += self.spin_speed * dt
            self.spin_speed *= 0.99938  # Adjusted friction for 480 FPS

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
                            self.ball_angle = (self.angle + (pocket_index * self.angle_per_pocket)) % (2 * math.pi)

                        # Play ball settle sound (disabled - only using ball sound)
                        # if hasattr(self, 'game') and self.game.ball_settle_sound:
                        #     self.game.ball_settle_sound.play()

                    print(f"Wheel and ball stopped after {self.wheel_rotations_after_drop:.1f} rotations!")
                    self.spin_start_time = 0.0  # Reset spin timer

                    # Stop wheel spinning sound (disabled - only using ball sound)
                    # if hasattr(self, 'game') and self.game.wheel_spin_sound:
                    #     self.game.wheel_spin_sound.stop()
            elif self.spin_speed < 0.05:  # Fallback if ball hasn't dropped yet
                self.spinning = False
                self.spin_speed = 0.0
                self.spin_start_time = 0.0  # Reset spin timer
                print("Wheel stopped!")
        
        # Update ball
        if self.ball_active:
            # Ball drops from bumper to number section after some time
            if self.ball_on_bumper:
                old_angle = self.ball_angle
                self.prev_ball_angle = self.ball_angle
                self.ball_angle += self.ball_speed * dt

                # Normalize ball angle to prevent precision issues
                self.ball_angle = self.ball_angle % (2 * math.pi)

                # Track rotations on bumper
                angle_diff = self.ball_angle - old_angle
                if angle_diff < 0:  # Handle angle wraparound
                    angle_diff += 2 * math.pi
                self.ball_rotations += angle_diff / (2 * math.pi)

                # Force drop after exactly 4 rotations (maximum limit)
                if self.ball_rotations >= 4.0:
                    # FORCE drop after 4 rotations - no random chance needed
                    self.ball_on_bumper = False
                    self.ball_has_dropped = True  # Mark that ball has dropped
                    self.ball_speed *= 0.7  # Speed reduction when dropping
                    print(f"Ball dropped from bumper to number section after {self.ball_rotations:.1f} rotations! (forced at 4.0 limit)")
                    
                    # Stop the sound when ball drops
                    if hasattr(self, 'game') and self.game.ball_drop_sound:
                        self.game.ball_drop_sound.stop()
                elif self.ball_rotations >= 3.0:
                    # Chance to drop from bumper to number section (more likely as speed decreases)
                    # But only between 3.0 and 4.0 rotations
                    drop_chance = (12.0 - self.ball_speed) / 12.0 * 0.03  # Increased chance
                    if random.random() < drop_chance * dt * 240:  # Scale by framerate (480 FPS)
                        self.ball_on_bumper = False
                        self.ball_has_dropped = True  # Mark that ball has dropped
                        self.ball_speed *= 0.7  # Speed reduction when dropping
                        print(f"Ball dropped from bumper to number section after {self.ball_rotations:.1f} rotations!")

                        # Stop the sound when ball drops
                        if hasattr(self, 'game') and self.game.ball_drop_sound:
                            self.game.ball_drop_sound.stop()

                self.ball_speed *= 0.99938  # Adjusted friction for 480 FPS
            else:
                # Ball on number section - moves with wheel and slows down
                self.prev_ball_angle = self.ball_angle
                self.ball_angle += (self.ball_speed + self.spin_speed) * dt  # Ball moves with wheel
                # Normalize ball angle to prevent precision issues
                self.ball_angle = self.ball_angle % (2 * math.pi)
                self.ball_speed *= 0.99625  # Adjusted friction for 480 FPS

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
        
        # Draw blue-gray felt background with texture and 3D depth
        with self.canvas:
            # Wheel shadow removed - no shadow on roulette

            # Draw background texture or fallback to solid color
            if self.background_texture:
                # Use texture if available - darker tint for more subdued appearance
                Color(0.7, 0.7, 0.7, 1)  # Darker gray tint to darken the texture
                Rectangle(texture=self.background_texture, pos=(0, 0), size=(self.width, self.height))
            else:
                # Fallback to solid blue-gray color if texture not found
                Color(0.15, 0.15, 0.2, 1)  # Very dark blue-gray felt
                Rectangle(pos=(0, 0), size=(self.width, self.height))
                
                # Felt texture (subtle pattern) - only if no texture loaded
                Color(0.2, 0.2, 0.25, 0.3)  # Slightly lighter very dark blue-gray
                for i in range(0, int(self.width), 20):
                    for j in range(0, int(self.height), 20):
                        Ellipse(pos=(i, j), size=(2, 2))

            # Draw previous winning numbers on the blue-gray background using cached textures
            if hasattr(self, 'previous_numbers_textures') and self.previous_numbers_textures:
                # Position on left side of wheel, within the blue-gray felt area
                start_x = 25  # Left margin - moved a little more left
                start_y = self.height * 0.3  # Start from 30% up the wheel height
                line_height = 40  # Space between numbers

                for i, texture_data in enumerate(self.previous_numbers_textures):
                    # White background for each number
                    Color(1, 1, 1, 1.0)  # White background
                    bg_x = start_x - 15
                    # Most recent number (i=0) at bottom (y=40), older numbers above it
                    bg_y = i * line_height + 40  # Add 40 pixels space at bottom
                    Rectangle(pos=(bg_x, bg_y), size=(70, 40))

                    # Add a black border around each number area for definition
                    Color(0, 0, 0, 1.0)  # Black border
                    Line(rectangle=(bg_x, bg_y, 70, 40), width=2)

                    # Draw cached texture for stable rendering
                    num_x = start_x
                    # Most recent number (i=0) at bottom (y=40), older numbers above it
                    num_y = i * line_height + 40  # Add 40 pixels space at bottom
                    if texture_data['texture']:
                        # Ensure proper blending for colored text
                        Color(1, 1, 1, 1)  # White tint to preserve original colors
                        Rectangle(texture=texture_data['texture'], pos=(num_x, num_y), size=texture_data['texture'].size)

            # Table border
            Color(0.4, 0.25, 0.1, 1)  # Wood border
            Line(rectangle=(0, 0, self.width, self.height), width=8)

            # Inner border highlight
            Color(0.5, 0.35, 0.15, 1)  # Lighter wood
            Line(rectangle=(4, 4, self.width-8, self.height-8), width=2)

        # Draw outer bumper track (raised margin) with enhanced wood grain and 3D depth
        with self.canvas:
            # Bumper track shadow removed

            # Bumper track base (dark mahogany wood) - raised effect
            Color(0.12, 0.06, 0.03, 1)  # Even deeper mahogany for base
            Ellipse(pos=(center_x - bumper_outer, center_y - bumper_outer),
                   size=(bumper_outer * 2, bumper_outer * 2))

            # Main bumper surface
            Color(0.15, 0.08, 0.04, 1)  # Deep mahogany
            Ellipse(pos=(center_x - bumper_outer + 1, center_y - bumper_outer + 1),
                   size=(bumper_outer * 2 - 2, bumper_outer * 2 - 2))

            # Enhanced wood grain layers for realistic texture
            for grain_radius in [bumper_outer, bumper_outer * 0.99, bumper_inner + 2, (bumper_inner + 2) * 0.99]:
                Color(0.25, 0.12, 0.06, 1)  # Medium mahogany
                Line(circle=(center_x, center_y, grain_radius), width=3)
            
            # Additional radial wood grain for texture
            for i in range(0, 360, 20):  # Every 20 degrees
                grain_angle = math.radians(i)
                grain_start = bumper_inner + 3
                grain_end = bumper_outer - 1
                x1 = center_x + math.cos(grain_angle) * grain_start
                y1 = center_y + math.sin(grain_angle) * grain_start
                x2 = center_x + math.cos(grain_angle) * grain_end
                y2 = center_y + math.sin(grain_angle) * grain_end
                Color(0.22, 0.11, 0.05, 0.5)  # Subtle grain lines
                Line(points=[x1, y1, x2, y2], width=1)

            # Inner shadow for depth
            Color(0.1, 0.05, 0.02, 0.8)  # Dark inner shadow
            Ellipse(pos=(center_x - bumper_inner - 2, center_y - bumper_inner - 2),
                   size=(bumper_inner * 2 + 4, bumper_inner * 2 + 4))

            # Wood highlights for raised effect
            Color(0.35, 0.18, 0.08, 1)  # Lighter mahogany highlights
            Line(circle=(center_x, center_y, bumper_outer - 1), width=2)
            Line(circle=(center_x, center_y, bumper_inner + 1), width=2)

            # Top highlight for 3D effect
            Color(0.45, 0.25, 0.12, 0.6)  # Bright highlight
            Ellipse(pos=(center_x - bumper_outer + 2, center_y - bumper_outer + 2),
                   size=(bumper_outer * 1.8, bumper_outer * 1.8))

            # Enhanced metallic rim with depth and polish
            Color(0.6, 0.5, 0.3, 1)  # Antique brass
            Line(circle=(center_x, center_y, bumper_outer), width=2)
            Line(circle=(center_x, center_y, bumper_inner), width=2)
            
            # Rim polish highlights
            Color(0.85, 0.75, 0.45, 1)  # Bright brass highlight
            Line(circle=(center_x, center_y, bumper_outer - 0.5), width=1)
            Line(circle=(center_x, center_y, bumper_inner + 0.5), width=1)
            
            # Rim shine effect
            Color(0.95, 0.85, 0.5, 0.6)  # Very bright shine
            Line(circle=(center_x, center_y, bumper_outer - 1), width=0.5)

        # Draw outer wheel rim (polished mahogany wood) with enhanced 3D depth and material detail
        with self.canvas:
            # Wheel rim shadow removed

            # Base wood layer - recessed effect
            Color(0.18, 0.09, 0.04, 1)  # Darker mahogany base
            Ellipse(pos=(center_x - radius, center_y - radius),
                   size=(radius * 2, radius * 2))

            # Main wood surface - raised with texture
            Color(0.22, 0.12, 0.06, 1)  # Rich mahogany
            Ellipse(pos=(center_x - radius + 2, center_y - radius + 2),
                   size=(radius * 2 - 4, radius * 2 - 4))

            # Enhanced wood grain rings for realistic texture
            for grain_ring in [radius, radius * 0.98, radius * 0.96, radius * 0.94]:
                Color(0.28, 0.16, 0.08, 1)  # Medium mahogany grain
                Line(circle=(center_x, center_y, grain_ring), width=2)
            
            # Additional wood grain detail - radial lines for realistic wood texture
            for i in range(0, 360, 15):  # Every 15 degrees
                grain_angle = math.radians(i)
                grain_start = radius * 0.92
                grain_end = radius * 0.98
                x1 = center_x + math.cos(grain_angle) * grain_start
                y1 = center_y + math.sin(grain_angle) * grain_start
                x2 = center_x + math.cos(grain_angle) * grain_end
                y2 = center_y + math.sin(grain_angle) * grain_end
                Color(0.25, 0.14, 0.07, 0.6)  # Subtle grain lines
                Line(points=[x1, y1, x2, y2], width=1)

            # Inner shadow for depth
            Color(0.15, 0.08, 0.04, 0.7)  # Inner shadow
            Ellipse(pos=(center_x - pocket_outer - 2, center_y - pocket_outer - 2),
                   size=(pocket_outer * 2 + 4, pocket_outer * 2 + 4))

            # Wood highlights and grain for raised effect
            Color(0.38, 0.22, 0.10, 1)  # Light mahogany highlights
            Line(circle=(center_x, center_y, radius - 1), width=2)
            Line(circle=(center_x, center_y, radius * 0.96), width=1)

            # Polished wood shine with 3D effect
            Color(0.5, 0.3, 0.15, 0.8)  # Warm highlight
            Line(circle=(center_x, center_y, radius - 0.5), width=1)

            # Top surface highlight for 3D raised effect
            Color(0.6, 0.4, 0.2, 0.4)  # Bright surface highlight
            Ellipse(pos=(center_x - radius + 3, center_y - radius + 3),
                   size=(radius * 1.5, radius * 1.5))
            
            # Metallic rim detail - polished brass edge
            Color(0.7, 0.55, 0.25, 1)  # Polished brass
            Line(circle=(center_x, center_y, radius), width=2)
            Color(0.9, 0.75, 0.35, 1)  # Bright brass highlight
            Line(circle=(center_x, center_y, radius - 0.5), width=1)
        
        # Draw inner center circle with enhanced wood inlay and 3D depth
        with self.canvas:
            # Center hub shadow for depth
            Color(0, 0, 0, 0.6)  # Deep shadow
            Ellipse(pos=(center_x - inner_radius + 3, center_y - inner_radius + 3),
                   size=(inner_radius * 2, inner_radius * 2))

            # Dark wood center - recessed
            Color(0.12, 0.06, 0.03, 1)  # Very dark mahogany base
            Ellipse(pos=(center_x - inner_radius, center_y - inner_radius),
                   size=(inner_radius * 2, inner_radius * 2))

            # Main center surface - raised
            Color(0.18, 0.09, 0.05, 1)  # Very dark mahogany
            Ellipse(pos=(center_x - inner_radius + 1, center_y - inner_radius + 1),
                   size=(inner_radius * 2 - 2, inner_radius * 2 - 2))

            # Enhanced decorative wood inlay with multiple rings
            for inlay_radius in [inner_radius, inner_radius * 0.9, inner_radius * 0.8, inner_radius * 0.7]:
                Color(0.25, 0.12, 0.06, 1)  # Medium mahogany for inlay base
                Line(circle=(center_x, center_y, inlay_radius), width=2)
                Color(0.35, 0.18, 0.08, 0.6)  # Light mahogany highlight
                Line(circle=(center_x, center_y, inlay_radius - 0.5), width=1)

            # Radial inlay details for decorative effect
            for i in range(0, 360, 30):  # Every 30 degrees
                inlay_angle = math.radians(i)
                inlay_start = inner_radius * 0.65
                inlay_end = inner_radius * 0.95
                x1 = center_x + math.cos(inlay_angle) * inlay_start
                y1 = center_y + math.sin(inlay_angle) * inlay_start
                x2 = center_x + math.cos(inlay_angle) * inlay_end
                y2 = center_y + math.sin(inlay_angle) * inlay_end
                Color(0.3, 0.15, 0.07, 0.7)  # Decorative radial lines
                Line(points=[x1, y1, x2, y2], width=1.5)

            # Center hub detail - deeply recessed with metallic accent
            Color(0.08, 0.04, 0.02, 1)  # Very dark hub base
            Ellipse(pos=(center_x - inner_radius * 0.3, center_y - inner_radius * 0.3),
                   size=(inner_radius * 0.6, inner_radius * 0.6))

            # Hub surface - polished wood
            Color(0.4, 0.2, 0.08, 1)  # Lighter wood hub
            Ellipse(pos=(center_x - inner_radius * 0.25, center_y - inner_radius * 0.25),
                   size=(inner_radius * 0.5, inner_radius * 0.5))

            # Hub decorative ring
            Color(0.5, 0.3, 0.12, 1)  # Medium wood ring
            Line(circle=(center_x, center_y, inner_radius * 0.25), width=2)
            
            # Hub highlight for 3D effect
            Color(0.6, 0.35, 0.15, 0.6)  # Bright hub highlight
            Ellipse(pos=(center_x - inner_radius * 0.2, center_y - inner_radius * 0.2),
                   size=(inner_radius * 0.3, inner_radius * 0.3))
            
            # Hub center - metallic accent
            Color(0.7, 0.55, 0.25, 1)  # Polished brass center
            Ellipse(pos=(center_x - inner_radius * 0.1, center_y - inner_radius * 0.1),
                   size=(inner_radius * 0.2, inner_radius * 0.2))
            
            # Hub center highlight
            Color(0.9, 0.75, 0.35, 0.8)  # Bright brass highlight
            Ellipse(pos=(center_x - inner_radius * 0.08, center_y - inner_radius * 0.08),
                   size=(inner_radius * 0.16, inner_radius * 0.16))
        
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
                
                # Draw pocket depth effects
                # Pocket shadow for depth
                Color(0, 0, 0, 0.3)  # Subtle shadow
                segments = 12
                for j in range(segments):
                    a1 = angle_start + (angle_end - angle_start) * (j / segments)
                    a2 = angle_start + (angle_end - angle_start) * ((j + 1) / segments)

                    # Shadow points (slightly offset)
                    x1_outer_shadow = center_x + math.cos(a1) * (pocket_outer + 1) + 1
                    y1_outer_shadow = center_y + math.sin(a1) * (pocket_outer + 1) + 1
                    x2_outer_shadow = center_x + math.cos(a2) * (pocket_outer + 1) + 1
                    y2_outer_shadow = center_y + math.sin(a2) * (pocket_outer + 1) + 1

                    x1_inner_shadow = center_x + math.cos(a1) * (pocket_inner + 1) + 1
                    y1_inner_shadow = center_y + math.sin(a1) * (pocket_inner + 1) + 1
                    x2_inner_shadow = center_x + math.cos(a2) * (pocket_inner + 1) + 1
                    y2_inner_shadow = center_y + math.sin(a2) * (pocket_inner + 1) + 1

                    Triangle(points=[x1_outer_shadow, y1_outer_shadow, x2_outer_shadow, y2_outer_shadow, x1_inner_shadow, y1_inner_shadow])
                    Triangle(points=[x2_outer_shadow, y2_outer_shadow, x2_inner_shadow, y2_inner_shadow, x1_inner_shadow, y1_inner_shadow])

                # Draw pocket filled segment using multiple small rectangles with depth
                # Base pocket color (slightly darker for depth)
                base_color = [max(0, c * 0.8) for c in color]
                Color(*base_color, 0.95)
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

                # Main pocket surface with slight highlight
                Color(*color, 0.98)
                for j in range(segments):
                    a1 = angle_start + (angle_end - angle_start) * (j / segments)
                    a2 = angle_start + (angle_end - angle_start) * ((j + 1) / segments)

                    # Slightly inset surface for raised effect
                    inset_factor = 0.97
                    x1_outer = center_x + math.cos(a1) * (pocket_outer * inset_factor)
                    y1_outer = center_y + math.sin(a1) * (pocket_outer * inset_factor)
                    x2_outer = center_x + math.cos(a2) * (pocket_outer * inset_factor)
                    y2_outer = center_y + math.sin(a2) * (pocket_outer * inset_factor)

                    x1_inner = center_x + math.cos(a1) * (pocket_inner * inset_factor)
                    y1_inner = center_y + math.sin(a1) * (pocket_inner * inset_factor)
                    x2_inner = center_x + math.cos(a2) * (pocket_inner * inset_factor)
                    y2_inner = center_y + math.sin(a2) * (pocket_inner * inset_factor)

                    Triangle(points=[x1_outer, y1_outer, x2_outer, y2_outer, x1_inner, y1_inner])
                    Triangle(points=[x2_outer, y2_outer, x2_inner, y2_inner, x1_inner, y1_inner])
                
                # Draw pocket divider (enhanced metallic gold separator with 3D detail)
                x1 = center_x + math.cos(angle_start) * pocket_outer
                y1 = center_y + math.sin(angle_start) * pocket_outer
                x2 = center_x + math.cos(angle_start) * pocket_inner
                y2 = center_y + math.sin(angle_start) * pocket_inner
                
                # Divider shadow for depth
                Color(0.4, 0.3, 0.1, 0.6)  # Dark shadow
                shadow_offset = 1
                Line(points=[x1 + shadow_offset, y1 + shadow_offset, 
                            x2 + shadow_offset, y2 + shadow_offset], width=4)
                
                # Main gold divider base
                Color(0.7, 0.55, 0.15, 1)  # Darker gold base
                Line(points=[x1, y1, x2, y2], width=4)

                # Main gold divider
                Color(0.9, 0.75, 0.2, 1)  # Bright gold
                Line(points=[x1, y1, x2, y2], width=3)

                # Gold highlight - metallic shine
                Color(1.0, 0.9, 0.4, 1)  # Light gold highlight
                Line(points=[x1, y1, x2, y2], width=1.5)
                
                # Bright metallic edge
                Color(1.0, 0.95, 0.5, 1)  # Very bright gold edge
                Line(points=[x1, y1, x2, y2], width=0.5)

                # Metallic shadow for 3D effect
                Color(0.6, 0.45, 0.1, 0.8)  # Darker gold shadow
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
                    # Ball on bumper track (outer margin) - ensure ball never extends beyond track
                    ball_visual_radius = 9  # ball_size/2 = 18/2 = 9 pixels

                    # Position ball so its outer edge is at bumper_outer minus safety margin
                    # This ensures the ball never visually extends beyond the track
                    max_ball_radius = bumper_outer - ball_visual_radius - 2  # 2 pixel safety margin
                    min_ball_radius = bumper_inner + ball_visual_radius + 2  # 2 pixel safety margin

                    # Position ball in the middle of the safe zone
                    ball_track_radius = (max_ball_radius + min_ball_radius) / 2

                    # Ensure it stays within absolute bounds
                    ball_track_radius = max(min_ball_radius, min(max_ball_radius, ball_track_radius))

                    ball_angle = self.ball_angle
                else:
                    # Ball on inner track (pockets section) - moves between pocket edges
                    # Ball gradually moves inward as it slows down
                    progress_to_stop = max(0, min(1, (self.ball_speed - 0.1) / 2.0))  # Clamp to 0-1
                    ball_track_radius = pocket_outer - (pocket_outer - pocket_inner) * (1 - progress_to_stop)

                    # Ensure ball stays within wheel bounds
                    max_safe_radius = radius - 5  # Stay well within wheel
                    ball_track_radius = max(pocket_inner + 2, min(max_safe_radius, ball_track_radius))

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
        
        # Draw center dolly (decorative marker/pointer) with enhanced 3D detail
        with self.canvas:
            dolly_base_radius = inner_radius * 0.15  # Base circle size
            dolly_pointer_length = inner_radius * 0.35  # Pointer extends outward
            pointer_width = 18  # Width of pointer at base
            
            # Dolly base shadow for depth
            Color(0, 0, 0, 0.5)
            Ellipse(pos=(center_x - dolly_base_radius - 2, center_y - dolly_base_radius - 2),
                   size=(dolly_base_radius * 2 + 4, dolly_base_radius * 2 + 4))
            
            # Dolly base - polished brass/metal base
            Color(0.6, 0.45, 0.2, 1)  # Dark brass base
            Ellipse(pos=(center_x - dolly_base_radius, center_y - dolly_base_radius),
                   size=(dolly_base_radius * 2, dolly_base_radius * 2))
            
            # Dolly base highlight - raised center
            Color(0.75, 0.6, 0.25, 1)  # Medium brass
            Ellipse(pos=(center_x - dolly_base_radius * 0.8, center_y - dolly_base_radius * 0.8),
                   size=(dolly_base_radius * 1.6, dolly_base_radius * 1.6))
            
            # Dolly center - polished gold center
            Color(0.9, 0.75, 0.3, 1)  # Bright brass
            Ellipse(pos=(center_x - dolly_base_radius * 0.5, center_y - dolly_base_radius * 0.5),
                   size=(dolly_base_radius, dolly_base_radius))
            
            # Dolly center highlight - shiny top
            Color(1.0, 0.9, 0.4, 0.8)  # Very bright highlight
            Ellipse(pos=(center_x - dolly_base_radius * 0.3, center_y - dolly_base_radius * 0.3),
                   size=(dolly_base_radius * 0.6, dolly_base_radius * 0.6))
            
            # Decorative rings on dolly base
            for ring_radius in [dolly_base_radius * 0.9, dolly_base_radius * 0.7]:
                Color(0.5, 0.35, 0.15, 0.8)  # Darker ring
                Line(circle=(center_x, center_y, ring_radius), width=1)
                Color(0.85, 0.7, 0.3, 0.6)  # Lighter ring highlight
                Line(circle=(center_x, center_y, ring_radius - 0.5), width=0.5)
            
            # Pointer shadow for depth
            Color(0, 0, 0, 0.4)
            pointer_angle = math.pi / 2  # Points upward (toward top)
            shadow_offset = 2
            shadow_points = [
                center_x, center_y + dolly_base_radius + shadow_offset,
                center_x - pointer_width/2 + shadow_offset, center_y + dolly_base_radius + dolly_pointer_length + shadow_offset,
                center_x + pointer_width/2 + shadow_offset, center_y + dolly_base_radius + dolly_pointer_length + shadow_offset
            ]
            Triangle(points=shadow_points)
            
            # Pointer base (darker metal)
            Color(0.65, 0.5, 0.18, 1)  # Dark brass
            pointer_base_points = [
                center_x, center_y + dolly_base_radius,
                center_x - pointer_width/2, center_y + dolly_base_radius + dolly_pointer_length,
                center_x + pointer_width/2, center_y + dolly_base_radius + dolly_pointer_length
            ]
            Triangle(points=pointer_base_points)
            
            # Main pointer body (polished brass)
            Color(0.85, 0.65, 0.25, 1)  # Bright brass
            pointer_points = [
                center_x, center_y + dolly_base_radius + 1,
                center_x - pointer_width/2 * 0.9, center_y + dolly_base_radius + dolly_pointer_length - 2,
                center_x + pointer_width/2 * 0.9, center_y + dolly_base_radius + dolly_pointer_length - 2
            ]
            Triangle(points=pointer_points)
            
            # Pointer highlight - metallic shine
            Color(0.95, 0.8, 0.35, 1)  # Very bright brass
            highlight_points = [
                center_x, center_y + dolly_base_radius + 2,
                center_x - pointer_width/4, center_y + dolly_base_radius + dolly_pointer_length * 0.6,
                center_x + pointer_width/4, center_y + dolly_base_radius + dolly_pointer_length * 0.6
            ]
            Triangle(points=highlight_points)
            
            # Pointer tip - sharp gold tip
            Color(1.0, 0.9, 0.2, 1)  # Gold tip
            tip_points = [
                center_x, center_y + dolly_base_radius + dolly_pointer_length - 1,
                center_x - pointer_width/6, center_y + dolly_base_radius + dolly_pointer_length - 3,
                center_x + pointer_width/6, center_y + dolly_base_radius + dolly_pointer_length - 3
            ]
            Triangle(points=tip_points)
            
            # Bright tip highlight
            Color(1.0, 1.0, 0.5, 0.9)  # Very bright tip
            bright_tip_points = [
                center_x, center_y + dolly_base_radius + dolly_pointer_length - 0.5,
                center_x - pointer_width/8, center_y + dolly_base_radius + dolly_pointer_length - 2,
                center_x + pointer_width/8, center_y + dolly_base_radius + dolly_pointer_length - 2
            ]
            Triangle(points=bright_tip_points)
            
            # Decorative side details on pointer
            Color(0.7, 0.55, 0.2, 0.8)  # Side accent
            for side_offset in [-pointer_width/3, pointer_width/3]:
                side_points = [
                    center_x + side_offset, center_y + dolly_base_radius + dolly_pointer_length * 0.3,
                    center_x + side_offset * 0.7, center_y + dolly_base_radius + dolly_pointer_length * 0.5,
                    center_x + side_offset * 0.7, center_y + dolly_base_radius + dolly_pointer_length * 0.7
                ]
                Line(points=side_points, width=1.5)



    def update_previous_numbers_display(self):
        """Update the previous numbers data and cache textures for stable rendering"""
        if not hasattr(self, 'game') or not hasattr(self.game, 'previous_numbers'):
            return

        # Store the previous numbers data
        if self.game.previous_numbers:
            self.previous_numbers_data = self.game.previous_numbers[-15:] if len(self.game.previous_numbers) > 15 else self.game.previous_numbers[:]
        else:
            self.previous_numbers_data = []

        # Cache textures for stable rendering (no blinking)
        self.previous_numbers_textures = []
        font_size = 28

        if self.previous_numbers_data:
            recent_numbers = self.previous_numbers_data[-15:] if len(self.previous_numbers_data) > 15 else self.previous_numbers_data
            recent_numbers.reverse()  # Most recent first

            for number in recent_numbers:
                # Determine text color based on roulette rules
                if number == 0:
                    text_color = (0, 1, 0, 1)  # Bright green for zero
                elif number in RouletteWheel.RED_NUMBERS:
                    text_color = (1, 0, 0, 1)  # Bright red for red numbers
                else:
                    text_color = (0, 0, 0, 1)  # Black for black numbers

                # Create and cache texture
                label = CoreLabel(text=str(number), font_size=font_size, bold=True, color=text_color)
                label.refresh()
                texture = label.texture

                self.previous_numbers_textures.append({
                    'texture': texture,
                    'number': number,
                    'color': text_color
                })

    def draw_text(self, text, x, y, font_size=16, bold=False):
        """Draw text on the canvas using Kivy's Label rendering"""
        label = CoreLabel(text=text, font_size=font_size, bold=bold)
        label.refresh()
        texture = label.texture

        if texture:
            # Draw the texture at the specified position
            return Rectangle(texture=texture, pos=(x, y), size=texture.size)


class RouletteGame(BoxLayout):
    """Main game layout"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 0  # Remove all padding to eliminate gaps
        self.spacing = 0  # Remove spacing between wheel and betting table
        
        # CRITICAL: Ensure this widget fills the entire screen
        self.size_hint = (1, 1)
        
        # Game state (must be set before create_ui)
        self.balance = 1000
        self.last_win = None

        # Track previous winning numbers - initialize with 15 random numbers
        self.previous_numbers = [random.randint(0, 36) for _ in range(15)]

        # Initialize casino sounds
        self.load_sounds()
        
        # Create wheel
        self.wheel = RouletteWheel()
        self.wheel.game = self  # Give wheel reference to game for sound access

        # Initialize betting system
        self.current_chip = 5
        self.bets = {}
        self.total_bet = 0
        self.balance = 1000
        
        # Load background texture for betting table
        self.betting_texture = None
        texture_path = r'C:\Users\aminz\OneDrive\Documents\GitHub\Roullett\roulette_game\assets\textures\2696.jpg'
        
        if os.path.exists(texture_path):
            try:
                img = CoreImage(texture_path)
                self.betting_texture = img.texture
                print(f"✓✓✓ SUCCESS: Loaded betting table background texture from: {os.path.abspath(texture_path)}")
                print(f"  Texture size: {self.betting_texture.size}")
            except Exception as e:
                print(f"✗ Failed to load texture from {texture_path}: {e}")
        else:
            print(f"✗✗✗ WARNING: Texture file not found at: {texture_path}")
            print("  Falling back to solid blue-gray color.")
        self.last_bet = 0  # Track the last total bet value
        self.last_bets = {}  # Track the last bets dictionary for rebet


        # Store references to betting buttons for updating bet amounts
        self.betting_buttons = {}

        # Create UI
        self.create_ui()

        # Initialize previous numbers display
        self.wheel.update_previous_numbers_display()

        # Start update loop - Maximum FPS for ultra-smooth ball animation
        Clock.schedule_interval(self.update, 1.0 / 480.0)  # 480 FPS for ultra-smooth animation

        # Bind keyboard events
        Window.bind(on_key_down=self.on_key_down)



    def load_sounds(self):
        """Load casino sound effects - professional ball sound and coin drop sound"""
        print("Loading professional casino sound...")

        # Load the professional ball sound
        professional_sound = SoundLoader.load('sounds/a-roulette-ball-429831.mp3')
        if professional_sound:
            # Use the professional sound for ball drop effect
            self.ball_drop_sound = professional_sound
            print("Professional ball sound loaded successfully!")
        else:
            print("Professional sound file not found, no sound will play.")
            self.ball_drop_sound = None

        # Load the coin drop sound for betting
        coin_sound = SoundLoader.load('sounds/coin-dropped.mp3')
        if coin_sound:
            self.coin_drop_sound = coin_sound
            print("Coin drop sound loaded successfully!")
        else:
            print("Coin drop sound file not found.")
            self.coin_drop_sound = None

        # Load the win sound for winning money
        win_sound = SoundLoader.load('sounds/win-sound.mp3')
        if win_sound:
            self.winning_sound = win_sound
            print("Win sound loaded successfully!")
        else:
            print("Win sound file not found.")
            self.winning_sound = None

        # Don't use any other sounds - only the professional ball sound, win sound, and coin sound
        self.wheel_spin_sound = None
        self.ball_launch_sound = None
        self.ball_settle_sound = None
        self.casino_ambiance = None

    def create_simple_sounds(self):
        """Create realistic casino sound effects programmatically"""
        # Create sounds directory if it doesn't exist
        os.makedirs('sounds', exist_ok=True)

        if WAVE_AVAILABLE:
            try:
                # Create more sophisticated casino sounds
                self.create_wheel_spin_sound('sounds/wheel_spin.wav')
                self.create_ball_launch_sound('sounds/ball_launch.wav')
                self.create_ball_drop_sound('sounds/ball_drop.wav')
                self.create_ball_settle_sound('sounds/ball_settle.wav')
                self.create_casino_ambiance('sounds/casino_ambiance.wav')

                # Reload the sounds after creating them
                self.wheel_spin_sound = SoundLoader.load('sounds/wheel_spin.wav')
                self.ball_launch_sound = SoundLoader.load('sounds/ball_launch.wav')

                # Try to load the user's professional ball sound first
                user_ball_sound = SoundLoader.load('sounds/a-roulette-ball-429831.mp3')
                if user_ball_sound:
                    self.ball_drop_sound = user_ball_sound
                    print("Using professional ball sound effect!")
                else:
                    self.ball_drop_sound = SoundLoader.load('sounds/ball_drop.wav')

                self.ball_settle_sound = SoundLoader.load('sounds/ball_settle.wav')
                self.casino_ambiance = SoundLoader.load('sounds/casino_ambiance.wav')

                if self.wheel_spin_sound and self.ball_launch_sound and self.ball_drop_sound and self.ball_settle_sound:
                    print("Realistic casino sound effects generated successfully!")
                    return
                else:
                    print("Sound generation failed, using system beeps...")
            except Exception as e:
                print(f"Failed to generate WAV files: {e}")

        # Fallback: Create simple system beep functions
        print("Using system beep sounds as fallback...")
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

    def create_wheel_spin_sound(self, filename):
        """Create a realistic wheel spinning sound with mechanical whirring"""
        sample_rate = 44100
        duration = 3.0  # Longer for looping
        num_samples = int(sample_rate * duration)

        samples = []
        for i in range(num_samples):
            # Create a complex mechanical sound with multiple frequencies
            t = i / sample_rate

            # Base low frequency rumble
            base_freq = 80 + 20 * math.sin(2 * math.pi * 0.5 * t)
            base_wave = 0.3 * math.sin(2 * math.pi * base_freq * t)

            # Higher frequency whirring that changes pitch
            whir_freq = 200 + 50 * math.sin(2 * math.pi * 2 * t)
            whir_wave = 0.2 * math.sin(2 * math.pi * whir_freq * t)

            # Add some mechanical clicking/rumbling
            click_freq = 1500 * (1 + 0.5 * math.sin(2 * math.pi * 3 * t))
            click_wave = 0.1 * math.sin(2 * math.pi * click_freq * t) * math.exp(-t * 2)

            # Combine waves with fade envelope
            envelope = min(0.8, i / (sample_rate * 0.1))  # Quick fade in
            envelope *= max(0.1, 1 - (i / num_samples) * 0.5)  # Slow fade out

            sample = envelope * (base_wave + whir_wave + click_wave)
            samples.append(int(sample * 32767))

        # Write WAV file
        with wave.open(filename, 'wb') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)
            for sample in samples:
                wav_file.writeframes(struct.pack('<h', sample))

    def create_ball_launch_sound(self, filename):
        """Create a realistic ball launch sound - sharp mechanical click"""
        sample_rate = 44100
        duration = 0.15
        num_samples = int(sample_rate * duration)

        samples = []
        for i in range(num_samples):
            t = i / sample_rate

            # Sharp attack with metallic ring
            attack = math.exp(-t * 50)  # Quick decay
            metallic = 0.7 * math.sin(2 * math.pi * 2500 * t) * attack
            click = 0.3 * (1 if i < sample_rate * 0.01 else 0)  # Sharp click

            sample = metallic + click
            samples.append(int(sample * 32767))

        with wave.open(filename, 'wb') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)
            for sample in samples:
                wav_file.writeframes(struct.pack('<h', sample))

    def create_ball_drop_sound(self, filename):
        """Create a realistic ball drop sound - cascading metallic bounces"""
        sample_rate = 44100
        duration = 0.4
        num_samples = int(sample_rate * duration)

        samples = []
        for i in range(num_samples):
            t = i / sample_rate

            # Multiple bouncing frequencies
            bounce1 = 0.4 * math.sin(2 * math.pi * 800 * t) * math.exp(-t * 8)
            bounce2 = 0.2 * math.sin(2 * math.pi * 1200 * t) * math.exp(-(t-0.1) * 12) if t > 0.1 else 0
            bounce3 = 0.1 * math.sin(2 * math.pi * 600 * t) * math.exp(-(t-0.2) * 15) if t > 0.2 else 0

            sample = bounce1 + bounce2 + bounce3
            samples.append(int(sample * 32767))

        with wave.open(filename, 'wb') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)
            for sample in samples:
                wav_file.writeframes(struct.pack('<h', sample))

    def create_ball_settle_sound(self, filename):
        """Create a realistic ball settling sound - final metallic click"""
        sample_rate = 44100
        duration = 0.08
        num_samples = int(sample_rate * duration)

        samples = []
        for i in range(num_samples):
            t = i / sample_rate

            # Sharp metallic ping with quick decay
            ping = 0.8 * math.sin(2 * math.pi * 1800 * t) * math.exp(-t * 80)
            undertone = 0.2 * math.sin(2 * math.pi * 900 * t) * math.exp(-t * 40)

            sample = ping + undertone
            samples.append(int(sample * 32767))

        with wave.open(filename, 'wb') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)
            for sample in samples:
                wav_file.writeframes(struct.pack('<h', sample))

    def create_casino_ambiance(self, filename):
        """Create subtle casino background ambiance"""
        sample_rate = 44100
        duration = 2.0
        num_samples = int(sample_rate * duration)

        samples = []
        for i in range(num_samples):
            t = i / sample_rate

            # Subtle crowd murmur simulation
            noise1 = 0.05 * math.sin(2 * math.pi * random.uniform(100, 200) * t)
            noise2 = 0.03 * math.sin(2 * math.pi * random.uniform(150, 250) * t)

            # Occasional chip sounds
            chip_sound = 0.02 * math.sin(2 * math.pi * 800 * t) * math.exp(-(t % 0.5) * 20) if random.random() < 0.01 else 0

            sample = (noise1 + noise2 + chip_sound) * 0.3
            samples.append(int(sample * 32767))

        with wave.open(filename, 'wb') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)
            for sample in samples:
                wav_file.writeframes(struct.pack('<h', sample))

    def create_winning_sound(self):
        """Create a celebratory winning sound effect"""
        if not WAVE_AVAILABLE:
            print("Wave module not available, no winning sound will play.")
            self.winning_sound = None
            return

        try:
            sample_rate = 44100
            duration = 1.5
            num_samples = int(sample_rate * duration)

            samples = []
            for i in range(num_samples):
                t = i / sample_rate

                # Create a triumphant chord with multiple frequencies
                # Major chord: C4, E4, G4
                freq1, freq2, freq3 = 261.63, 329.63, 392.00  # C4, E4, G4

                # Create ascending arpeggio effect
                if t < 0.5:
                    # First note (C4)
                    wave1 = 0.3 * math.sin(2 * math.pi * freq1 * t)
                elif t < 1.0:
                    # Second note (E4)
                    wave1 = 0.3 * math.sin(2 * math.pi * freq2 * (t - 0.5))
                else:
                    # Third note (G4)
                    wave1 = 0.3 * math.sin(2 * math.pi * freq3 * (t - 1.0))

                # Add some sparkle with higher harmonics
                sparkle = 0.1 * math.sin(2 * math.pi * freq3 * 2 * t) * math.exp(-t * 2)

                # Add a celebratory "ta-da" ending
                if t > 1.2:
                    tada_freq = 523.25  # C5
                    tada = 0.2 * math.sin(2 * math.pi * tada_freq * (t - 1.2)) * math.exp(-(t - 1.2) * 5)
                else:
                    tada = 0

                # Combine waves with envelope
                envelope = min(1.0, i / (sample_rate * 0.1))  # Quick attack
                envelope *= max(0.0, 1.0 - (i / num_samples) * 0.3)  # Slow release

                sample = envelope * (wave1 + sparkle + tada)
                samples.append(int(sample * 32767))

            # Write winning sound file
            filename = 'sounds/winning_sound.wav'
            with wave.open(filename, 'wb') as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)
                wav_file.setframerate(sample_rate)
                for sample in samples:
                    wav_file.writeframes(struct.pack('<h', sample))

            # Load the sound
            self.winning_sound = SoundLoader.load(filename)
            if self.winning_sound:
                print("Winning sound created successfully!")
            else:
                print("Failed to load winning sound.")

        except Exception as e:
            print(f"Failed to create winning sound: {e}")
            self.winning_sound = None

    def create_beep_functions(self):
        """Create beep functions using system sounds"""
        import platform

        def system_beep(frequency=800, duration=200):
            """Play a system beep"""
            try:
                if platform.system() == 'Windows':
                    import winsound
                    winsound.Beep(frequency, duration)
                else:
                    print(f"\\a")  # ASCII bell
            except Exception as e:
                print(f"\\a")  # Fallback to ASCII bell

        # Create mock sound objects with user's professional sound if available
        class MockSound:
            def __init__(self, play_func, loop=False):
                self.play_func = play_func
                self.loop = loop

            def play(self):
                self.play_func()

            def stop(self):
                pass

        # Try to load the user's professional ball sound
        user_ball_sound = SoundLoader.load('sounds/a-roulette-ball-429831.mp3')

        self.wheel_spin_sound = MockSound(lambda: system_beep(200, 1000), loop=True)
        self.ball_launch_sound = MockSound(lambda: system_beep(1000, 150))

        if user_ball_sound:
            self.ball_drop_sound = user_ball_sound
            print("Using professional ball sound effect!")
        else:
            self.ball_drop_sound = MockSound(lambda: system_beep(800, 200))

        self.ball_settle_sound = MockSound(lambda: system_beep(1200, 100))
        self.casino_ambiance = None  # No ambiance for system beeps

        print("Sound system initialized")
    
    def create_announcement_overlay(self):
        """Create an invisible overlay frame matching the roulette frame size for announcements"""
        # Create a RelativeLayout that will overlay the wheel
        # RelativeLayout has NO background by default - completely invisible/transparent
        overlay = RelativeLayout(size_hint=(1, 1))
        
        # No canvas drawing on overlay - it's completely transparent
        # Only the labels inside will have visible backgrounds for readability
        # The overlay itself is invisible and doesn't block the roulette frame
        
        # Create label for "YOU WON" text in center (no background - fully transparent)
        self.winning_number_label = Label(
            text="",
            font_size=36,
            color=(1, 0.9, 0, 1),  # Gold color
            bold=True,
            halign='center',
            valign='middle',
            size_hint=(None, None),
            size=(150, 50),
        )
        self.winning_number_label.bind(size=self.winning_number_label.setter('text_size'))
        
        # Position in center
        def update_winning_number_pos(instance, value):
            if overlay.width > 0 and overlay.height > 0:
                # Center horizontally and vertically
                center_x = (overlay.width - self.winning_number_label.width) / 2
                center_y = (overlay.height - self.winning_number_label.height) / 2 + 15  # Slightly above center to make room for win amount
                self.winning_number_label.pos = (center_x, center_y)
        
        overlay.bind(size=update_winning_number_pos, pos=update_winning_number_pos)
        overlay.add_widget(self.winning_number_label)
        
        # Create label for win amount in center (below winning number, no background - fully transparent)
        self.win_amount_label = Label(
            text="",
            font_size=28,
            color=(1, 0.9, 0, 1),  # Gold color
            bold=True,
            halign='center',
            valign='middle',
            size_hint=(None, None),
            size=(100, 40),
        )
        self.win_amount_label.bind(size=self.win_amount_label.setter('text_size'))
        
        # Position below winning number in center
        def update_win_amount_pos(instance, value):
            if overlay.width > 0 and overlay.height > 0:
                # Center horizontally, position below winning number
                center_x = (overlay.width - self.win_amount_label.width) / 2
                center_y = (overlay.height - self.win_amount_label.height) / 2 - 25  # Below center, below winning number
                self.win_amount_label.pos = (center_x, center_y)
        
        overlay.bind(size=update_win_amount_pos, pos=update_win_amount_pos)
        overlay.add_widget(self.win_amount_label)
        
        return overlay
    
    def create_ui(self):
        """Create casino-style game UI"""
        # Betting table at top with blue-gray background
        betting_container_outer = BoxLayout(size_hint_y=0.4, orientation='vertical')
        self.create_betting_table_in_container(betting_container_outer)
        self.add_widget(betting_container_outer)

        # Wheel container at bottom - use FloatLayout for absolute positioning
        wheel_container = FloatLayout(size_hint_y=0.6)  # Take 60% from bottom
        
        # Add wheel - it will fill the container
        self.wheel.size_hint = (1, 1)
        self.wheel.pos_hint = {'x': 0, 'y': 0}
        wheel_container.add_widget(self.wheel)
        
        # Create invisible overlay frame positioned exactly on top of the wheel
        self.announcement_overlay = self.create_announcement_overlay()
        # Position overlay to match wheel exactly (same size and position)
        self.announcement_overlay.size_hint = (1, 1)
        self.announcement_overlay.pos_hint = {'x': 0, 'y': 0}
        wheel_container.add_widget(self.announcement_overlay)  # Add last so it's on top
        
        self.add_widget(wheel_container)

    def create_betting_table(self):
        """Create the betting table interface"""
        betting_container = BoxLayout(size_hint_y=0.4, orientation='vertical', spacing=3, padding=[3, 0, 3, 3])  # no top padding

        # Set blue-gray background for betting table
        with betting_container.canvas.before:
            Color(0.15, 0.15, 0.2, 1)  # Very dark blue-gray felt
            self.bg_rect = Rectangle(pos=betting_container.pos, size=betting_container.size)

        # Bind the rectangle to update when container size changes
        def update_bg(instance, value):
            self.bg_rect.pos = instance.pos
            self.bg_rect.size = instance.size

        betting_container.bind(pos=update_bg, size=update_bg)

        # Balance and bet display row
        info_row = BoxLayout(size_hint_y=0.08, spacing=10)
        self.balance_label = Label(text=f'BALANCE: ${self.balance}', font_size=12, color=(1,1,0.8,1),
                                 halign='left', valign='middle')
        self.balance_label.bind(size=self.balance_label.setter('text_size'))
        info_row.add_widget(self.balance_label)

        self.bet_label = Label(text=f'TOTAL BET: ${self.total_bet}', font_size=12, color=(1,0.8,1,1),
                             halign='right', valign='middle')
        self.bet_label.bind(size=self.bet_label.setter('text_size'))
        info_row.add_widget(self.bet_label)

        betting_container.add_widget(info_row)

        # Chip selection row
        chip_row = BoxLayout(size_hint_y=0.12, spacing=3)
        chip_label = Label(text='CHIP:', font_size=12, color=(1,1,1,1), size_hint_x=0.15)
        chip_row.add_widget(chip_label)

        self.chip_buttons = []
        chip_values = [1, 5, 10, 25, 50, 100]
        for value in chip_values:
            bg_color, text_color = self.get_chip_color(value)
            btn = Button(text=f'${value}', font_size=10, size_hint_x=1/len(chip_values),
                        background_color=bg_color, color=text_color)
            btn.bind(on_press=lambda instance, val=value: self.select_chip(val))
            self.chip_buttons.append(btn)
            chip_row.add_widget(btn)

        betting_container.add_widget(chip_row)

        # Outside bets row
        outside_row = BoxLayout(size_hint_y=0.15, spacing=2)

        # Red/Black
        red_btn = Button(text='RED', font_size=10, background_color=(0.8, 0.1, 0.1, 1), color=(1,1,1,1))
        red_btn.bind(on_press=lambda instance: self.place_bet('red'))
        outside_row.add_widget(red_btn)

        black_btn = Button(text='BLACK', font_size=10, background_color=(0.1, 0.1, 0.1, 1), color=(1,1,1,1))
        black_btn.bind(on_press=lambda instance: self.place_bet('black'))
        outside_row.add_widget(black_btn)

        # Even/Odd
        even_btn = Button(text='EVEN', font_size=10, background_color=(0.4, 0.4, 0.8, 1), color=(1,1,1,1))
        even_btn.bind(on_press=lambda instance: self.place_bet('even'))
        outside_row.add_widget(even_btn)

        odd_btn = Button(text='ODD', font_size=10, background_color=(0.4, 0.4, 0.8, 1), color=(1,1,1,1))
        odd_btn.bind(on_press=lambda instance: self.place_bet('odd'))
        outside_row.add_widget(odd_btn)

        # High/Low
        low_btn = Button(text='1-18', font_size=10, background_color=(0.2, 0.4, 0.8, 1), color=(1,1,1,1))  # Blue
        low_btn.bind(on_press=lambda instance: self.place_bet('low'))
        outside_row.add_widget(low_btn)

        high_btn = Button(text='19-36', font_size=10, background_color=(0.8, 0.4, 0.2, 1), color=(1,1,1,1))  # Orange/Red
        high_btn.bind(on_press=lambda instance: self.place_bet('high'))
        outside_row.add_widget(high_btn)

        betting_container.add_widget(outside_row)

        # Dozens row
        dozens_row = BoxLayout(size_hint_y=0.15, spacing=2)

        doz1_btn = Button(text='1st 12', font_size=9, background_color=(0.6, 0.4, 0.8, 1), color=(1,1,1,1))
        doz1_btn.bind(on_press=lambda instance: self.place_bet('dozen1'))
        dozens_row.add_widget(doz1_btn)

        doz2_btn = Button(text='2nd 12', font_size=9, background_color=(0.6, 0.4, 0.8, 1), color=(1,1,1,1))
        doz2_btn.bind(on_press=lambda instance: self.place_bet('dozen2'))
        dozens_row.add_widget(doz2_btn)

        doz3_btn = Button(text='3rd 12', font_size=9, background_color=(0.6, 0.4, 0.8, 1), color=(1,1,1,1))
        doz3_btn.bind(on_press=lambda instance: self.place_bet('dozen3'))
        dozens_row.add_widget(doz3_btn)

        zero_btn = Button(text='0', font_size=10, background_color=(0.0, 0.6, 0.0, 1), color=(1,1,1,1))
        zero_btn.bind(on_press=lambda instance: self.place_bet('zero'))
        dozens_row.add_widget(zero_btn)

        betting_container.add_widget(dozens_row)

        # Number grid (simplified - just a few key numbers for demo)
        numbers_row = BoxLayout(size_hint_y=0.15, spacing=1)
        key_numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]

        for num in key_numbers:
            color = (0.8, 0.1, 0.1, 1) if num in self.wheel.RED_NUMBERS else (0.1, 0.1, 0.1, 1)
            num_btn = Button(text=str(num), font_size=16, background_color=color, color=(1,1,1,1),
                           size_hint_x=1/len(key_numbers))
            num_btn.bind(on_press=lambda instance, n=num: self.place_bet(f'number_{n}'))
            numbers_row.add_widget(num_btn)

        betting_container.add_widget(numbers_row)

        # Control buttons row
        control_row = BoxLayout(size_hint_y=0.2, spacing=5)

        clear_btn = Button(text='CLEAR', font_size=12, background_color=(0.6, 0.2, 0.2, 1), color=(1,1,1,1))
        clear_btn.bind(on_press=self.clear_bets)
        control_row.add_widget(clear_btn)

        spin_btn = Button(text='SPIN', font_size=14, background_color=(0.2, 0.6, 0.2, 1), color=(1,1,1,1), bold=True)
        spin_btn.bind(on_press=self.spin_wheel)
        control_row.add_widget(spin_btn)

        betting_container.add_widget(control_row)

        self.add_widget(betting_container)

        # Update chip button colors to show selection
        self.update_chip_buttons()

    def create_betting_table_in_container(self, container):
        """Create a traditional European roulette betting table interface"""
        betting_container = BoxLayout(size_hint_y=1.0, orientation='vertical', spacing=0, padding=0)

        # Set background texture or fallback to solid color for betting table
        with betting_container.canvas.before:
            if hasattr(self, 'betting_texture') and self.betting_texture:
                # Use texture if available - darker tint for more subdued appearance
                Color(0.7, 0.7, 0.7, 1)  # Darker gray tint to darken the texture
                self.bg_rect = Rectangle(texture=self.betting_texture, pos=betting_container.pos, size=betting_container.size)
            else:
                # Fallback to solid blue-gray color if texture not found
                Color(0.15, 0.15, 0.2, 1)  # Very dark blue-gray felt
                self.bg_rect = Rectangle(pos=betting_container.pos, size=betting_container.size)

        def update_bg(instance, value):
            self.bg_rect.pos = instance.pos
            self.bg_rect.size = instance.size
        betting_container.bind(pos=update_bg, size=update_bg)

        # Top info bar
        info_row = BoxLayout(size_hint_y=0.08, spacing=5, padding=[5, 2, 5, 2])
        
        # Add spacer to push balance label to the right (equivalent to 4 characters)
        # For font size 18, 4 characters ≈ 40-50 pixels
        spacer = Widget(size_hint_x=None, width=50)
        info_row.add_widget(spacer)
        
        self.balance_label = Label(text=f'BALANCE: ${self.balance}', font_size=18, color=(1,1,0.8,1),
                                 halign='left', valign='middle')
        self.balance_label.bind(size=self.balance_label.setter('text_size'))
        info_row.add_widget(self.balance_label)

        # Last bet label in the center - make it bigger to fit at least 23 characters
        self.last_bet_label = Label(text=f'LAST BET: ${self.last_bet}', font_size=18, color=(1,1,1,1),
                                   halign='center', valign='middle', size_hint_x=0.7)
        self.last_bet_label.bind(size=self.last_bet_label.setter('text_size'))
        info_row.add_widget(self.last_bet_label)

        # Add spacer to push total bet label to the left (equivalent to 4 characters)
        # For font size 18, 4 characters ≈ 40-50 pixels
        spacer_bet = Widget(size_hint_x=None, width=50)
        info_row.add_widget(spacer_bet)

        self.bet_label = Label(text=f'TOTAL BET: ${self.total_bet}', font_size=18, color=(1,0.8,1,1),
                             halign='right', valign='middle')
        self.bet_label.bind(size=self.bet_label.setter('text_size'))
        info_row.add_widget(self.bet_label)
        
        # Add spacer on the right side of total bet label (equivalent to 4 characters)
        spacer_right = Widget(size_hint_x=None, width=50)
        info_row.add_widget(spacer_right)
        betting_container.add_widget(info_row)

        # Chip selection
        chip_row = BoxLayout(size_hint_y=0.08, spacing=2, padding=[5, 2, 5, 2])
        chip_label = Label(text='CHIP:', font_size=20, color=(1,1,1,1), size_hint_x=0.12)
        chip_row.add_widget(chip_label)

        self.chip_buttons = []
        chip_values = [1, 5, 10, 25, 50, 100]
        for value in chip_values:
            bg_color, text_color = self.get_chip_color(value)
            btn = Button(text=f'${value}', font_size=20, size_hint_x=1/len(chip_values),
                        background_color=bg_color, color=text_color)
            btn.bind(on_press=lambda instance, val=value: self.select_chip(val))
            self.chip_buttons.append(btn)
            chip_row.add_widget(btn)
        betting_container.add_widget(chip_row)

        # Main betting table area
        table_area = BoxLayout(size_hint_y=0.74, orientation='vertical', spacing=2, padding=[5, 2, 5, 2])

        # Top row: Zero pocket + Number grid (3 rows x 12 columns)
        top_section = BoxLayout(size_hint_y=0.7, spacing=3)

        # Zero pocket (green oval at left end)
        zero_container = BoxLayout(size_hint_x=0.08, orientation='vertical')
        zero_btn = Button(text='0', font_size=20, background_color=(0.0, 0.6, 0.0, 1), color=(1,1,1,1),
                         bold=True, size_hint_y=1.0)
        zero_btn.bind(on_press=lambda instance: self.place_bet('zero'))
        self.betting_buttons['zero'] = zero_btn
        zero_container.add_widget(zero_btn)
        top_section.add_widget(zero_container)

        # Number grid (3 rows x 12 columns = 36 numbers)
        numbers_container = BoxLayout(size_hint_x=0.92, orientation='vertical', spacing=2)

        # Define the exact European roulette number layout
        number_rows = [
            [3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36],  # Top row (red: 3,9,12,18,21,27,30,36)
            [2, 5, 8, 11, 14, 17, 20, 23, 26, 29, 32, 35],  # Middle row (red: 5,14,17,23,26,32)
            [1, 4, 7, 10, 13, 16, 19, 22, 25, 28, 31, 34]   # Bottom row (red: 1,7,10,16,19,25,28,31,34)
        ]

        for row_nums in number_rows:
            row_container = BoxLayout(size_hint_y=1/3, spacing=1)
            for num in row_nums:
                # Determine color: red or black
                is_red = num in self.wheel.RED_NUMBERS
                bg_color = (0.85, 0.15, 0.15, 1) if is_red else (0.15, 0.15, 0.15, 1)  # Casino red/black

                num_btn = Button(text=str(num), font_size=18, background_color=bg_color,
                               color=(1,1,1,1), bold=True, size_hint_x=1/12)
                num_btn.bind(on_press=lambda instance, n=num: self.place_bet(f'number_{n}'))
                self.betting_buttons[f'number_{num}'] = num_btn
                row_container.add_widget(num_btn)
            numbers_container.add_widget(row_container)

        top_section.add_widget(numbers_container)
        table_area.add_widget(top_section)

        # Dozens row - align with number columns (1st 12 with cols 1-4, 2nd 12 with cols 5-8, 3rd 12 with cols 9-12)
        dozens_row = BoxLayout(size_hint_y=0.15, spacing=2)
        
        # Empty spacer to match zero column width (0.08)
        zero_spacer = BoxLayout(size_hint_x=0.08)
        dozens_row.add_widget(zero_spacer)
        
        # Dozens container to match numbers container width (0.92)
        dozens_container = BoxLayout(size_hint_x=0.92, spacing=2)

        # 1st 12 aligns with columns 1-4 (4/12 of 0.92 = 0.3067)
        doz1_btn = Button(text='1st 12', font_size=17, background_color=(0.2, 0.6, 0.8, 1),  # Blue
                         color=(1,1,1,1), bold=True, size_hint_x=4/12)
        doz1_btn.bind(on_press=lambda instance: self.place_bet('dozen1'))
        self.betting_buttons['dozen1'] = doz1_btn
        dozens_container.add_widget(doz1_btn)

        # 2nd 12 aligns with columns 5-8 (4/12 of 0.92 = 0.3067)
        doz2_btn = Button(text='2nd 12', font_size=17, background_color=(0.2, 0.7, 0.3, 1),  # Green
                         color=(1,1,1,1), bold=True, size_hint_x=4/12)
        doz2_btn.bind(on_press=lambda instance: self.place_bet('dozen2'))
        self.betting_buttons['dozen2'] = doz2_btn
        dozens_container.add_widget(doz2_btn)

        # 3rd 12 aligns with columns 9-12 (4/12 of 0.92 = 0.3067)
        doz3_btn = Button(text='3rd 12', font_size=17, background_color=(0.6, 0.4, 0.8, 1),  # Purple
                         color=(1,1,1,1), bold=True, size_hint_x=4/12)
        doz3_btn.bind(on_press=lambda instance: self.place_bet('dozen3'))
        self.betting_buttons['dozen3'] = doz3_btn
        dozens_container.add_widget(doz3_btn)
        
        dozens_row.add_widget(dozens_container)
        table_area.add_widget(dozens_row)

        # Bottom row: Six sections (each spanning 2 columns)
        bottom_row = BoxLayout(size_hint_y=0.15, spacing=2)

        # 1to18 (blue background)
        low_btn = Button(text='1 to 18', font_size=16, background_color=(0.2, 0.4, 0.8, 1),  # Blue
                        color=(1,1,1,1), bold=True, size_hint_x=1/6)
        low_btn.bind(on_press=lambda instance: self.place_bet('low'))
        self.betting_buttons['low'] = low_btn
        bottom_row.add_widget(low_btn)

        # EVEN (neutral background)
        even_btn = Button(text='EVEN', font_size=16, background_color=(0.3, 0.3, 0.3, 1),
                         color=(1,1,1,1), bold=True, size_hint_x=1/6)
        even_btn.bind(on_press=lambda instance: self.place_bet('even'))
        self.betting_buttons['even'] = even_btn
        bottom_row.add_widget(even_btn)

        # RED (red background)
        red_btn = Button(text='RED', font_size=16, background_color=(0.8, 0.1, 0.1, 1),
                        color=(1,1,1,1), bold=True, size_hint_x=1/6)
        red_btn.bind(on_press=lambda instance: self.place_bet('red'))
        self.betting_buttons['red'] = red_btn
        bottom_row.add_widget(red_btn)

        # BLACK (black background)
        black_btn = Button(text='BLACK', font_size=16, background_color=(0.1, 0.1, 0.1, 1),
                          color=(1,1,1,1), bold=True, size_hint_x=1/6)
        black_btn.bind(on_press=lambda instance: self.place_bet('black'))
        self.betting_buttons['black'] = black_btn
        bottom_row.add_widget(black_btn)

        # ODD (neutral background)
        odd_btn = Button(text='ODD', font_size=16, background_color=(0.3, 0.3, 0.3, 1),
                        color=(1,1,1,1), bold=True, size_hint_x=1/6)
        odd_btn.bind(on_press=lambda instance: self.place_bet('odd'))
        self.betting_buttons['odd'] = odd_btn
        bottom_row.add_widget(odd_btn)

        # 19to36 (orange/red background)
        high_btn = Button(text='19 to 36', font_size=16, background_color=(0.8, 0.4, 0.2, 1),  # Orange/Red
                         color=(1,1,1,1), bold=True, size_hint_x=1/6)
        high_btn.bind(on_press=lambda instance: self.place_bet('high'))
        self.betting_buttons['high'] = high_btn
        bottom_row.add_widget(high_btn)

        table_area.add_widget(bottom_row)
        betting_container.add_widget(table_area)

        # Bottom control buttons
        control_row = BoxLayout(size_hint_y=0.1, spacing=10, padding=[10, 5, 10, 5])

        clear_btn = Button(text='CLEAR BETS', font_size=16, background_color=(0.6, 0.2, 0.2, 1),
                          color=(1,1,1,1), bold=True)
        clear_btn.bind(on_press=self.clear_bets)
        control_row.add_widget(clear_btn)

        rebet_btn = Button(text='REBET', font_size=16, background_color=(0.4, 0.4, 0.8, 1),
                          color=(1,1,1,1), bold=True)
        rebet_btn.bind(on_press=self.rebet)
        control_row.add_widget(rebet_btn)

        double_btn = Button(text='2X', font_size=16, background_color=(0.2, 0.7, 0.7, 1),  # Teal/Cyan
                          color=(1,1,1,1), bold=True)
        double_btn.bind(on_press=self.double_bets)
        control_row.add_widget(double_btn)

        spin_btn = Button(text='SPIN', font_size=18, background_color=(0.2, 0.6, 0.2, 1),
                         color=(1,1,1,1), bold=True)
        spin_btn.bind(on_press=self.spin_wheel)
        control_row.add_widget(spin_btn)

        betting_container.add_widget(control_row)

        container.add_widget(betting_container)
        self.update_chip_buttons()
        self.update_betting_buttons()

    def get_chip_color(self, value):
        """Get casino-standard color for chip value"""
        chip_colors = {
            1: ((1.0, 1.0, 1.0, 1), (0, 0, 0, 1)),      # White chip, black text
            5: ((0.8, 0.2, 0.2, 1), (1, 1, 1, 1)),       # Red chip, white text
            10: ((0.2, 0.4, 0.8, 1), (1, 1, 1, 1)),      # Blue chip, white text
            25: ((0.2, 0.6, 0.2, 1), (1, 1, 1, 1)),      # Green chip, white text
            50: ((0.9, 0.7, 0.2, 1), (0, 0, 0, 1)),      # Orange/Yellow chip, black text
            100: ((0.1, 0.1, 0.1, 1), (1, 1, 1, 1))      # Black chip, white text
        }
        return chip_colors.get(value, ((0.8, 0.6, 0.2, 1), (0, 0, 0, 1)))  # Default fallback

    def select_chip(self, value):
        """Select chip value for betting"""
        self.current_chip = value
        self.update_chip_buttons()
        print(f"Selected chip: ${value}")

    def update_chip_buttons(self):
        """Update chip button colors to show selected chip"""
        for i, btn in enumerate(self.chip_buttons):
            value = [1, 5, 10, 25, 50, 100][i]
            bg_color, text_color = self.get_chip_color(value)
            if value == self.current_chip:
                # Highlight selected chip with a brighter/lighter version
                r, g, b = bg_color[0], bg_color[1], bg_color[2]
                # Make it brighter by increasing each component
                highlighted_r = min(1.0, r * 1.3 if r < 0.5 else r + 0.2)
                highlighted_g = min(1.0, g * 1.3 if g < 0.5 else g + 0.2)
                highlighted_b = min(1.0, b * 1.3 if b < 0.5 else b + 0.2)
                btn.background_color = (highlighted_r, highlighted_g, highlighted_b, 1.0)
                btn.color = text_color
            else:
                btn.background_color = bg_color
                btn.color = text_color

    def update_betting_buttons(self):
        """Update all betting button text to show current bet amounts"""
        for bet_type, button in self.betting_buttons.items():
            bet_amount = self.bets.get(bet_type, 0)

            # Get the base text for the button
            if bet_type == 'zero':
                base_text = '0'
            elif bet_type.startswith('number_'):
                base_text = bet_type.split('_')[1]
            elif bet_type == 'dozen1':
                base_text = '1st 12'
            elif bet_type == 'dozen2':
                base_text = '2nd 12'
            elif bet_type == 'dozen3':
                base_text = '3rd 12'
            elif bet_type == 'red':
                base_text = 'RED'
            elif bet_type == 'black':
                base_text = 'BLACK'
            elif bet_type == 'even':
                base_text = 'EVEN'
            elif bet_type == 'odd':
                base_text = 'ODD'
            elif bet_type == 'low':
                base_text = '1 to 18'
            elif bet_type == 'high':
                base_text = '19 to 36'
            else:
                base_text = bet_type.upper()

            # Update button text with bet amount
            if bet_amount > 0:
                button.text = f'{base_text}\n${bet_amount}'
            else:
                button.text = base_text

    def place_bet(self, bet_type):
        """Place a bet on the specified type"""
        if self.balance >= self.current_chip:
            if bet_type not in self.bets:
                self.bets[bet_type] = 0
            self.bets[bet_type] += self.current_chip
            self.total_bet += self.current_chip
            self.balance -= self.current_chip

            # Play coin drop sound when placing a bet
            if self.coin_drop_sound:
                self.coin_drop_sound.play()

            self.update_display()
            self.update_betting_buttons()
            print(f"Placed ${self.current_chip} on {bet_type}. Total bet: ${self.total_bet}, Balance: ${self.balance}")
        else:
            print("Insufficient balance!")

    def rebet(self, instance=None):
        """Repeat the last bet"""
        if self.last_bets:
            # Check if we have enough balance for the last bets
            last_total = sum(self.last_bets.values())
            if self.balance >= last_total:
                # Clear current bets first
                self.balance += self.total_bet
                self.bets = {}
                self.total_bet = 0
                
                # Restore last bets
                self.bets = self.last_bets.copy()
                self.total_bet = last_total
                self.balance -= self.total_bet
                
                self.update_display()
                self.update_betting_buttons()
                print(f"Rebet: ${self.total_bet}")
            else:
                print("Insufficient balance to rebet!")
    
    def double_bets(self, instance=None):
        """Double all current bets"""
        if self.bets:
            # Need enough balance to double (need to add the same amount again)
            if self.balance >= self.total_bet:
                # Double all bet amounts
                for bet_type in self.bets:
                    self.bets[bet_type] *= 2
                # Subtract only the additional amount (the original total_bet)
                self.balance -= self.total_bet
                self.total_bet *= 2
                
                self.update_display()
                self.update_betting_buttons()
                print(f"Doubled bets: ${self.total_bet}")
            else:
                print("Insufficient balance to double bets!")
    
    def clear_bets(self, instance=None):
        """Clear all bets"""
        # Refund bets to balance
        self.balance += self.total_bet
        # Don't update last_bet when manually clearing - it should keep the previous spin's total
        self.bets = {}
        self.total_bet = 0
        self.update_display()
        self.update_betting_buttons()
        print("Bets cleared")

    def update_display(self):
        """Update balance and bet displays"""
        self.balance_label.text = f'BALANCE: ${self.balance}'
        self.last_bet_label.text = f'LAST BET: ${self.last_bet}'
        self.bet_label.text = f'TOTAL BET: ${self.total_bet}'

    def spin_wheel(self, instance=None):
        """Handle spin button - only spin if there are bets"""
        if self.total_bet > 0:
            if not self.wheel.spinning and not self.wheel.ball_active:
                # Clear previous winning announcements
                if hasattr(self, 'winning_number_label'):
                    self.winning_number_label.text = ""
                if hasattr(self, 'win_amount_label'):
                    self.win_amount_label.text = ""
                if hasattr(self.wheel, 'win_text_label'):
                    self.wheel.win_text_label.text = ""
                
                # Start the sequence: spin wheel and launch ball
                self.wheel.start_spin()
                self.wheel.launch_ball()

                # Play ball sound immediately when spinning starts
                if self.ball_drop_sound:
                    self.ball_drop_sound.play()

                print(f"Spinning with ${self.total_bet} in bets!")
            else:
                print("Wheel is already spinning!")
        else:
            print("Place some bets first!")
    
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

                # Play ball sound immediately when spinning starts
                if self.ball_drop_sound:
                    self.ball_drop_sound.play()
            elif self.wheel.spinning and not self.wheel.ball_active:
                # Launch ball if wheel is spinning but ball isn't active
                self.wheel.launch_ball()
    
    def update(self, dt):
        """Update game loop"""
        self.wheel.update(dt)

        # Check for spin completion and handle payouts
        if not self.wheel.spinning and self.wheel.winning_number is not None and self.wheel.winning_number != self.last_win:
            self.last_win = self.wheel.winning_number
            self.process_payouts()
            print(f"Winning number: {self.wheel.winning_number}")


    def show_win_in_existing_labels(self, win_amount):
        """Show win information in the center of roulette frame"""
        if hasattr(self.wheel, 'win_text_label'):
            # Show "you win!!" in the center text box
            self.wheel.win_text_label.text = "YOU WIN!!"

            # Schedule clearing after 5 seconds
            def clear_win_text(dt):
                if hasattr(self.wheel, 'win_text_label'):
                    self.wheel.win_text_label.text = ""

            Clock.schedule_once(clear_win_text, 5)
    
    def show_winning_announcement(self, winning_number, win_amount=None):
        """Show winning announcement in the overlay frame"""
        # Only show "YOU WON" and win amount if there's actually a win
        if win_amount is not None and win_amount > 0:
            if hasattr(self, 'winning_number_label'):
                # Show "YOU WON" text
                self.winning_number_label.text = "YOU WON"
                self.winning_number_label.color = (1, 0.9, 0, 1)  # Gold color
            
            if hasattr(self, 'win_amount_label'):
                # Show win amount
                self.win_amount_label.text = f"${win_amount}"
                self.win_amount_label.color = (1, 0.9, 0, 1)  # Gold color
            
            # Schedule clearing both after 5 seconds
            def clear_win_announcement(dt):
                if hasattr(self, 'winning_number_label'):
                    self.winning_number_label.text = ""
                if hasattr(self, 'win_amount_label'):
                    self.win_amount_label.text = ""
            Clock.schedule_once(clear_win_announcement, 5)
        else:
            # No win - clear any existing text
            if hasattr(self, 'winning_number_label'):
                self.winning_number_label.text = ""
            if hasattr(self, 'win_amount_label'):
                self.win_amount_label.text = ""

    def process_payouts(self):
        """Process betting payouts based on winning number"""
        win_number = self.wheel.winning_number
        total_payout = 0

        for bet_type, amount in self.bets.items():
            payout = 0

            if bet_type == 'red' and win_number in self.wheel.RED_NUMBERS:
                payout = amount * 2
            elif bet_type == 'black' and win_number not in self.wheel.RED_NUMBERS and win_number != 0:
                payout = amount * 2
            elif bet_type == 'even' and win_number != 0 and win_number % 2 == 0:
                payout = amount * 2
            elif bet_type == 'odd' and win_number != 0 and win_number % 2 == 1:
                payout = amount * 2
            elif bet_type == 'low' and win_number >= 1 and win_number <= 18:
                payout = amount * 2
            elif bet_type == 'high' and win_number >= 19 and win_number <= 36:
                payout = amount * 2
            elif bet_type == 'dozen1' and win_number >= 1 and win_number <= 12:
                payout = amount * 3
            elif bet_type == 'dozen2' and win_number >= 13 and win_number <= 24:
                payout = amount * 3
            elif bet_type == 'dozen3' and win_number >= 25 and win_number <= 36:
                payout = amount * 3
            elif bet_type == 'zero' and win_number == 0:
                payout = amount * 36  # House edge makes this payout high
            elif bet_type.startswith('number_'):
                bet_num = int(bet_type.split('_')[1])
                if win_number == bet_num:
                    payout = amount * 36

            if payout > 0:
                total_payout += payout
                print(f"WIN! {bet_type}: bet ${amount}, payout ${payout}")

        if total_payout > 0:
            self.balance += total_payout
            print(f"Total payout: ${total_payout}, New balance: ${self.balance}")
        else:
            print("No winning bets this round")

        # Add winning number to previous numbers list
        self.previous_numbers.append(win_number)
        if len(self.previous_numbers) > 15:
            self.previous_numbers.pop(0)  # Keep only last 15 numbers


        # Update the previous numbers display
        self.wheel.update_previous_numbers_display()

        print(f"Winning number: {win_number}")

        # Show winning announcement in overlay (always show number, show amount if win)
        if hasattr(self, 'show_winning_announcement'):
            self.show_winning_announcement(win_number, total_payout if total_payout > 0 else None)

        if total_payout > 0:
            self.show_win_in_existing_labels(total_payout)
            if self.winning_sound:
                self.winning_sound.play()

            # Clear bets after showing the win result (5 seconds)
            def clear_bets_after_win(dt):
                self.last_bet = self.total_bet  # Save total bet as last bet before clearing
                self.last_bets = self.bets.copy()  # Save bets dictionary for rebet
                self.bets = {}
                self.total_bet = 0
                self.update_display()
                self.update_betting_buttons()
                if hasattr(self, 'betting_container') and self.betting_container:
                    self.draw_coins_on_table(self.betting_container)

            Clock.schedule_once(clear_bets_after_win, 5)
        else:
            # No win - clear bets immediately
            self.last_bet = self.total_bet  # Save total bet as last bet before clearing
            self.last_bets = self.bets.copy()  # Save bets dictionary for rebet
            self.bets = {}
            self.total_bet = 0
            self.update_display()
            self.update_betting_buttons()
            if hasattr(self, 'betting_container') and self.betting_container:
                self.draw_coins_on_table(self.betting_container)


class RouletteApp(App):
    """Main Kivy App"""
    
    def build(self):
        # NEVER set Window.size on Android - it breaks fullscreen
        # Only set window size for desktop testing
        try:
            from kivy.utils import platform
            if platform != 'android':
                Window.size = (450, 700)  # Desktop testing size
        except:
            pass
        
        Window.clearcolor = (0.0, 0.0, 0.0, 1)  # Black background for wheel area
        
        # Create game - ensure it fills screen
        game = RouletteGame()
        game.size_hint = (1, 1)  # Force fullscreen
        
        return game
    
    def on_start(self):
        """Called when app starts"""
        print("Roulette game started!")
        
        # On Android, force fullscreen immediately
        try:
            from kivy.utils import platform
            if platform == 'android':
                # Force fullscreen using Android APIs
                from jnius import autoclass
                # Try to use our custom FullscreenPythonActivity, fallback to PythonActivity
                try:
                    Activity = autoclass('org.kivy.android.FullscreenPythonActivity')
                except:
                    Activity = autoclass('org.kivy.android.PythonActivity')
                activity = Activity.mActivity
                WindowManager = autoclass('android.view.WindowManager$LayoutParams')
                View = autoclass('android.view.View')
                
                DisplayMetrics = autoclass('android.util.DisplayMetrics')
                
                def force_fullscreen():
                    try:
                        window = activity.getWindow()
                        
                        # Get actual screen size
                        display = activity.getWindowManager().getDefaultDisplay()
                        metrics = DisplayMetrics()
                        display.getRealMetrics(metrics)
                        screen_width = metrics.widthPixels
                        screen_height = metrics.heightPixels
                        
                        print(f"DEBUG: Screen size detected: {screen_width}x{screen_height}")
                        print(f"DEBUG: Window size before fix: {Window.size}")
                        
                        # Clear any windowed mode flags FIRST
                        window.clearFlags(WindowManager.FLAG_FORCE_NOT_FULLSCREEN)
                        
                        # Set fullscreen flags
                        window.addFlags(
                            WindowManager.FLAG_FULLSCREEN |
                            WindowManager.FLAG_LAYOUT_IN_SCREEN |
                            WindowManager.FLAG_LAYOUT_NO_LIMITS
                        )
                        
                        # Force window to fill screen
                        params = window.getAttributes()
                        params.width = WindowManager.MATCH_PARENT
                        params.height = WindowManager.MATCH_PARENT
                        params.x = 0
                        params.y = 0
                        window.setAttributes(params)
                        
                        # Also set decor view layout params
                        decor_view = window.getDecorView()
                        current_params = decor_view.getLayoutParams()
                        if current_params:
                            current_params.width = WindowManager.MATCH_PARENT
                            current_params.height = WindowManager.MATCH_PARENT
                            decor_view.setLayoutParams(current_params)
                        
                        # Immersive fullscreen
                        decor_view.setSystemUiVisibility(
                            View.SYSTEM_UI_FLAG_FULLSCREEN |
                            View.SYSTEM_UI_FLAG_HIDE_NAVIGATION |
                            View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY |
                            View.SYSTEM_UI_FLAG_LAYOUT_STABLE |
                            View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN |
                            View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION
                        )
                        
                        print(f"DEBUG: Fullscreen applied! Screen: {screen_width}x{screen_height}")
                    except Exception as e:
                        print(f"DEBUG: Error in force_fullscreen: {e}")
                        import traceback
                        traceback.print_exc()
                
                # Apply immediately - try both direct and on UI thread
                try:
                    force_fullscreen()  # Try direct call
                except:
                    pass
                activity.runOnUiThread(force_fullscreen)  # Also on UI thread
                
                # Also ensure root widget fills screen
                if hasattr(self, 'root') and self.root:
                    self.root.size_hint = (1, 1)
                    # Schedule multiple checks to ensure it stays fullscreen
                    Clock.schedule_once(lambda dt: self._ensure_fullscreen(), 0.1)
                    Clock.schedule_once(lambda dt: self._ensure_fullscreen(), 0.5)
                    Clock.schedule_once(lambda dt: self._ensure_fullscreen(), 1.0)
                    Window.bind(size=self._on_window_size)
        except Exception as e:
            print(f"Fullscreen setup error: {e}")
            import traceback
            traceback.print_exc()

        # Start casino ambiance (disabled - only using ball sound)
        # if hasattr(self, 'casino_ambiance') and self.casino_ambiance:
        #     self.casino_ambiance.play()
    
    def _ensure_fullscreen(self):
        """Ensure root widget fills screen"""
        if hasattr(self, 'root') and self.root:
            self.root.size_hint = (1, 1)
    
    def _on_window_size(self, instance, size):
        """Handle window size changes"""
        if hasattr(self, 'root') and self.root:
            self.root.size_hint = (1, 1)
    
    def on_pause(self):
        """Called when app is paused (mobile)"""
        return True
    
    def on_resume(self):
        """Called when app resumes (mobile)"""
        pass


if __name__ == '__main__':
    RouletteApp().run()

