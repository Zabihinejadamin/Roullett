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
import math
import random


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
            self.ball_angle = random.uniform(0, 2 * math.pi)
            self.ball_speed = random.uniform(8.0, 12.0)  # radians per second
            self.ball_rotations = 0.0  # Reset rotation counter
            print("Ball launched on bumper track!")
    
    def update(self, dt):
        """Update wheel and ball physics"""
        # Update wheel rotation
        if self.spinning:
            self.angle += self.spin_speed * dt
            self.spin_speed *= 0.995  # Friction
            
            if self.spin_speed < 0.05:
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

                # Only allow drop after at least 4 full rotations
                if self.ball_rotations >= 4.0:
                    # Chance to drop from bumper to number section (more likely as speed decreases)
                    drop_chance = (12.0 - self.ball_speed) / 12.0 * 0.02  # Small chance based on speed
                    if random.random() < drop_chance * dt * 60:  # Scale by framerate
                        self.ball_on_bumper = False
                        self.ball_speed *= 0.7  # Speed reduction when dropping
                        print(f"Ball dropped from bumper to number section after {self.ball_rotations:.1f} rotations!")

                self.ball_speed *= 0.995  # Light friction on bumper track
            else:
                # Ball on number section - moves with wheel and slows down
                self.ball_angle += (self.ball_speed + self.spin_speed) * dt  # Ball moves with wheel
                self.ball_speed *= 0.97  # More friction on number section

            # Ball only stops completely when wheel stops and ball is on number section
            if not self.spinning and not self.ball_on_bumper and self.ball_speed < 0.1:
                self.ball_active = False
                self.ball_speed = 0.0
                self.ball_settled = True  # Ball has settled in pocket
                self.determine_ball_pocket()
                # Lock the ball position to the winning pocket
                if self.winning_number is not None:
                    pocket_index = self.NUMBERS.index(self.winning_number)
                    self.ball_angle = pocket_index * self.angle_per_pocket
        
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
        
        # Draw casino green felt background
        with self.canvas:
            Color(0.05, 0.25, 0.1, 1)  # Casino green felt
            Rectangle(pos=(0, 0), size=(self.width, self.height))

        # Draw outer bumper track (raised margin)
        with self.canvas:
            # Bumper track base (dark wood)
            Color(0.2, 0.1, 0.05, 1)  # Dark wood
            Ellipse(pos=(center_x - bumper_outer, center_y - bumper_outer),
                   size=(bumper_outer * 2, bumper_outer * 2))
            # Bumper track top (lighter wood with slight curve)
            Color(0.4, 0.2, 0.1, 1)  # Medium wood
            Line(circle=(center_x, center_y, bumper_outer), width=8)
            Line(circle=(center_x, center_y, bumper_inner), width=6)

        # Draw outer wheel rim (polished wood)
        with self.canvas:
            Color(0.35, 0.18, 0.12, 1)  # Rich brown wood
            Ellipse(pos=(center_x - radius, center_y - radius), 
                   size=(radius * 2, radius * 2))
            # Rim highlight
            Color(0.45, 0.25, 0.15, 1)
            Line(circle=(center_x, center_y, radius), width=3)
        
        # Draw inner center circle
        with self.canvas:
            Color(0.25, 0.12, 0.08, 1)  # Darker wood center
            Ellipse(pos=(center_x - inner_radius, center_y - inner_radius),
                   size=(inner_radius * 2, inner_radius * 2))
        
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
                
                # Draw pocket divider (golden separator)
                Color(0.85, 0.65, 0.13, 1)  # Gold
                x1 = center_x + math.cos(angle_start) * pocket_outer
                y1 = center_y + math.sin(angle_start) * pocket_outer
                x2 = center_x + math.cos(angle_start) * pocket_inner
                y2 = center_y + math.sin(angle_start) * pocket_inner
                Line(points=[x1, y1, x2, y2], width=2)
                
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
                    # Ball settled in pocket - position it in the winning pocket
                    ball_track_radius = pocket_inner + 8  # Position inside the pocket
                    # Calculate angle for the winning pocket relative to wheel rotation
                    if self.winning_number is not None:
                        pocket_index = self.NUMBERS.index(self.winning_number)
                        # Position ball at the winning pocket's angle relative to current wheel position
                        ball_angle = self.angle + (pocket_index * self.angle_per_pocket)
                    else:
                        ball_angle = self.ball_angle
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
                
                # Ball shadow
                Color(0, 0, 0, 0.3)
                Ellipse(pos=(ball_x - ball_size/2 + 2, ball_y - ball_size/2 - 2), 
                        size=(ball_size, ball_size))
                
                # Ball body (ivory/white)
                Color(0.98, 0.98, 0.95, 1)  # Ivory white
                Ellipse(pos=(ball_x - ball_size/2, ball_y - ball_size/2), 
                       size=(ball_size, ball_size))
                
                # Ball highlight
                Color(1, 1, 1, 0.6)
                Ellipse(pos=(ball_x - ball_size/3, ball_y + ball_size/6), 
                       size=(ball_size/2, ball_size/2))
        
        # Draw center marker (pointer)
        with self.canvas:
            Color(1, 0.2, 0.2, 1)  # Red pointer
            pointer_size = 20
            # Draw triangle pointer
            pointer_points = [
                center_x, center_y + inner_radius + 5,
                center_x - pointer_size/2, center_y + inner_radius - 10,
                center_x + pointer_size/2, center_y + inner_radius - 10
            ]
            Triangle(points=pointer_points)


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
        
        # Create wheel
        self.wheel = RouletteWheel()
        
        # Create UI
        self.create_ui()
        
        # Start update loop
        Clock.schedule_interval(self.update, 1.0 / 60.0)  # 60 FPS

        # Bind keyboard events
        Window.bind(on_key_down=self.on_key_down)
    
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
            elif self.wheel.spinning and not self.wheel.ball_active:
                # Launch ball if wheel is spinning but ball isn't active
                self.wheel.launch_ball()
    
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
    
    def on_pause(self):
        """Called when app is paused (mobile)"""
        return True
    
    def on_resume(self):
        """Called when app resumes (mobile)"""
        pass


if __name__ == '__main__':
    RouletteApp().run()

