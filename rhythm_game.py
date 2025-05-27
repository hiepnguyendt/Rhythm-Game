import pygame
import sys
import time
import random
import os
import math
import json

# Initialize Pygame
pygame.init()
pygame.mixer.pre_init(44100, -16, 2, 512)  # Reduce audio latency
pygame.mixer.init()

# Get the user's screen resolution
info = pygame.display.Info()
user_screen_width = info.current_w
user_screen_height = info.current_h

# Constants - Base resolution for calculations
BASE_WIDTH = 800
BASE_HEIGHT = 600

# Set the game resolution based on the user's screen
# Use 80% of the screen size by default, but ensure minimum size
SCREEN_WIDTH = max(800, int(user_screen_width * 0.8))
SCREEN_HEIGHT = max(600, int(user_screen_height * 0.8))

# Calculate scaling factors for responsive design
SCALE_X = SCREEN_WIDTH / BASE_WIDTH
SCALE_Y = SCREEN_HEIGHT / BASE_HEIGHT

# Game settings
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (50, 50, 50)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)

# High scores file
HIGH_SCORES_FILE = "rhythm_game_scores.json"

# Game settings
DIFFICULTY_SETTINGS = {
    'easy': {
        'note_speed': 3 * SCALE_Y,
        'spawn_rate_min': 1.0,
        'spawn_rate_max': 2.0,
        'perfect_threshold': 20 * SCALE_Y,
        'good_threshold': 40 * SCALE_Y,
        'notes_to_pass': 50,  # Number of notes to hit to pass this level
        'accuracy_to_pass': 70  # Minimum accuracy percentage to pass
    },
    'normal': {
        'note_speed': 5 * SCALE_Y,
        'spawn_rate_min': 0.5,
        'spawn_rate_max': 1.5,
        'perfect_threshold': 15 * SCALE_Y,
        'good_threshold': 30 * SCALE_Y,
        'notes_to_pass': 100,
        'accuracy_to_pass': 75
    },
    'hard': {
        'note_speed': 7 * SCALE_Y,
        'spawn_rate_min': 0.3,
        'spawn_rate_max': 1.0,
        'perfect_threshold': 10 * SCALE_Y,
        'good_threshold': 20 * SCALE_Y,
        'notes_to_pass': 150,
        'accuracy_to_pass': 80
    },
    'expert': {
        'note_speed': 9 * SCALE_Y,
        'spawn_rate_min': 0.2,
        'spawn_rate_max': 0.8,
        'perfect_threshold': 8 * SCALE_Y,
        'good_threshold': 15 * SCALE_Y,
        'notes_to_pass': 200,
        'accuracy_to_pass': 85
    },
    'master': {
        'note_speed': 12 * SCALE_Y,
        'spawn_rate_min': 0.1,
        'spawn_rate_max': 0.5,
        'perfect_threshold': 5 * SCALE_Y,
        'good_threshold': 10 * SCALE_Y,
        'notes_to_pass': 300,
        'accuracy_to_pass': 90
    }
}

# Difficulty progression
DIFFICULTY_PROGRESSION = ['easy', 'normal', 'hard', 'expert', 'master']

# Level progression settings
LEVEL_THRESHOLDS = [
    0,      # Level 1
    1000,   # Level 2
    3000,   # Level 3
    6000,   # Level 4
    10000,  # Level 5
    15000,  # Level 6
    21000,  # Level 7
    28000,  # Level 8
    36000,  # Level 9
    45000   # Level 10
]

NOTE_SPEED = 5 * SCALE_Y  # Default speed at which notes fall
TRACK_COUNT = 4  # Number of tracks/lanes
TRACK_WIDTH = SCREEN_WIDTH // (TRACK_COUNT + 1)
TARGET_Y = SCREEN_HEIGHT - int(100 * SCALE_Y)  # Y position of the target line
PERFECT_THRESHOLD = 15 * SCALE_Y  # Default timing threshold for perfect hit
GOOD_THRESHOLD = 30 * SCALE_Y     # Default timing threshold for good hit
class AnimalAnimation:
    def __init__(self, x, y, track):
        self.x = x
        self.y = y
        self.track = track
        self.lifetime = 1.0  # Animation duration in seconds
        self.scale = 1.0
        self.rotation = 0
        
        # Select animal based on track
        self.animal_type = ["bird", "frog", "rabbit", "cat"][track]
        self.color = [RED, GREEN, BLUE, YELLOW][track]
        
        # Animation properties
        self.frames = 0
        self.max_frames = 20
        self.jump_height = 0
        
    def update(self):
        self.lifetime -= 0.02
        self.frames += 1
        
        # Different animation for each animal
        if self.animal_type == "bird":
            # Bird flies up in an arc
            self.y -= 3 * SCALE_Y
            self.x += math.sin(self.frames / 5) * 3 * SCALE_X
            self.rotation = math.sin(self.frames / 3) * 15
        elif self.animal_type == "frog":
            # Frog jumps up and down
            self.jump_height = math.sin(self.frames / 10) * 30 * SCALE_Y
            if self.frames > self.max_frames / 2:
                self.y -= 1 * SCALE_Y  # Gradually move up
        elif self.animal_type == "rabbit":
            # Rabbit hops to the right
            self.x += 2 * SCALE_X
            self.jump_height = abs(math.sin(self.frames / 5) * 20 * SCALE_Y)
        elif self.animal_type == "cat":
            # Cat pounces to the left
            self.x -= 2 * SCALE_X
            self.jump_height = abs(math.sin(self.frames / 5) * 15 * SCALE_Y)
            
        # Scale down slightly as animation progresses
        self.scale = 1.0 - (0.3 * (1.0 - self.lifetime))
        
        return self.lifetime > 0
        
    def draw(self, screen):
        # Base size for animal shapes
        size = 30 * SCALE_Y * self.scale
        
        # Draw different animal shapes based on type
        if self.animal_type == "bird":
            # Bird - triangular wings with a round body
            body_pos = (self.x, self.y - self.jump_height)
            
            # Rotate the bird
            wing_points = [
                (self.x - size, self.y - self.jump_height),
                (self.x, self.y - size/2 - self.jump_height),
                (self.x + size, self.y - self.jump_height)
            ]
            
            # Apply rotation to wing points
            rotated_wings = []
            for px, py in wing_points:
                dx, dy = px - self.x, py - self.y + self.jump_height
                rx = dx * math.cos(math.radians(self.rotation)) - dy * math.sin(math.radians(self.rotation))
                ry = dx * math.sin(math.radians(self.rotation)) + dy * math.cos(math.radians(self.rotation))
                rotated_wings.append((rx + self.x, ry + self.y - self.jump_height))
            
            # Draw bird
            pygame.draw.polygon(screen, self.color, rotated_wings)
            pygame.draw.circle(screen, self.color, body_pos, size/2)
            
            # Draw eye
            eye_pos = (self.x + size/4 * math.cos(math.radians(self.rotation)), 
                       self.y - self.jump_height - size/4 * math.sin(math.radians(self.rotation)))
            pygame.draw.circle(screen, WHITE, (int(eye_pos[0]), int(eye_pos[1])), int(size/6))
            pygame.draw.circle(screen, BLACK, (int(eye_pos[0]), int(eye_pos[1])), int(size/10))
            
        elif self.animal_type == "frog":
            # Frog - round body with eyes on top
            body_pos = (self.x, self.y - self.jump_height)
            
            # Draw frog body
            pygame.draw.circle(screen, self.color, body_pos, size/1.5)
            
            # Draw legs
            leg_spread = self.frames % 10 < 5  # Alternate leg positions
            leg_width = size/4
            
            if leg_spread:
                # Legs spread out
                pygame.draw.ellipse(screen, self.color, 
                                   (self.x - size, self.y - self.jump_height + size/3, 
                                    size/1.5, size/3))
                pygame.draw.ellipse(screen, self.color, 
                                   (self.x + size/2, self.y - self.jump_height + size/3, 
                                    size/1.5, size/3))
            else:
                # Legs tucked in
                pygame.draw.ellipse(screen, self.color, 
                                   (self.x - size/2, self.y - self.jump_height + size/3, 
                                    size/2, size/4))
                pygame.draw.ellipse(screen, self.color, 
                                   (self.x, self.y - self.jump_height + size/3, 
                                    size/2, size/4))
            
            # Draw eyes
            eye_spacing = size/2
            pygame.draw.circle(screen, WHITE, (int(self.x - eye_spacing/2), int(self.y - self.jump_height - size/4)), int(size/5))
            pygame.draw.circle(screen, WHITE, (int(self.x + eye_spacing/2), int(self.y - self.jump_height - size/4)), int(size/5))
            pygame.draw.circle(screen, BLACK, (int(self.x - eye_spacing/2), int(self.y - self.jump_height - size/4)), int(size/8))
            pygame.draw.circle(screen, BLACK, (int(self.x + eye_spacing/2), int(self.y - self.jump_height - size/4)), int(size/8))
            
        elif self.animal_type == "rabbit":
            # Rabbit - oval body with long ears
            body_pos = (self.x, self.y - self.jump_height)
            
            # Draw rabbit body
            pygame.draw.ellipse(screen, self.color, 
                               (self.x - size/2, self.y - size/2 - self.jump_height, 
                                size, size/1.5))
            
            # Draw ears
            ear_height = size * 1.2
            ear_width = size/3
            ear_spacing = size/3
            
            # Left ear
            pygame.draw.ellipse(screen, self.color, 
                               (self.x - ear_spacing, self.y - ear_height - self.jump_height, 
                                ear_width, ear_height))
            
            # Right ear
            pygame.draw.ellipse(screen, self.color, 
                               (self.x + ear_spacing - ear_width, self.y - ear_height - self.jump_height, 
                                ear_width, ear_height))
            
            # Draw face
            pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y - size/4 - self.jump_height)), int(size/3))
            
            # Draw eyes
            eye_spacing = size/4
            pygame.draw.circle(screen, BLACK, (int(self.x - eye_spacing/2), int(self.y - size/4 - self.jump_height)), int(size/10))
            pygame.draw.circle(screen, BLACK, (int(self.x + eye_spacing/2), int(self.y - size/4 - self.jump_height)), int(size/10))
            
            # Draw nose
            pygame.draw.circle(screen, PURPLE, (int(self.x), int(self.y - size/6 - self.jump_height)), int(size/12))
            
        elif self.animal_type == "cat":
            # Cat - round head with pointed ears
            head_pos = (self.x, self.y - self.jump_height)
            
            # Draw cat head
            pygame.draw.circle(screen, self.color, head_pos, size/1.5)
            
            # Draw ears
            ear_size = size/2
            ear_spacing = size/1.5
            
            # Left ear - triangle
            pygame.draw.polygon(screen, self.color, [
                (self.x - ear_spacing/2, self.y - size/2 - self.jump_height),
                (self.x - ear_spacing, self.y - size - self.jump_height),
                (self.x, self.y - size - self.jump_height)
            ])
            
            # Right ear - triangle
            pygame.draw.polygon(screen, self.color, [
                (self.x + ear_spacing/2, self.y - size/2 - self.jump_height),
                (self.x + ear_spacing, self.y - size - self.jump_height),
                (self.x, self.y - size - self.jump_height)
            ])
            
            # Draw eyes
            eye_spacing = size/2
            eye_shape = self.frames % 20 < 10  # Blink animation
            
            if eye_shape:
                # Open eyes
                pygame.draw.ellipse(screen, WHITE, 
                                   (self.x - eye_spacing/2 - size/6, self.y - size/2 - self.jump_height, 
                                    size/3, size/4))
                pygame.draw.ellipse(screen, WHITE, 
                                   (self.x + eye_spacing/2 - size/6, self.y - size/2 - self.jump_height, 
                                    size/3, size/4))
                pygame.draw.ellipse(screen, BLACK, 
                                   (self.x - eye_spacing/2 - size/12, self.y - size/2 - self.jump_height, 
                                    size/6, size/6))
                pygame.draw.ellipse(screen, BLACK, 
                                   (self.x + eye_spacing/2 - size/12, self.y - size/2 - self.jump_height, 
                                    size/6, size/6))
            else:
                # Closed eyes (lines)
                pygame.draw.line(screen, BLACK, 
                               (self.x - eye_spacing/2 - size/6, self.y - size/2 - self.jump_height), 
                               (self.x - eye_spacing/2 + size/6, self.y - size/2 - self.jump_height), 2)
                pygame.draw.line(screen, BLACK, 
                               (self.x + eye_spacing/2 - size/6, self.y - size/2 - self.jump_height), 
                               (self.x + eye_spacing/2 + size/6, self.y - size/2 - self.jump_height), 2)
            
            # Draw nose
            pygame.draw.polygon(screen, PURPLE, [
                (self.x, self.y - size/3 - self.jump_height),
                (self.x - size/10, self.y - size/4 - self.jump_height),
                (self.x + size/10, self.y - size/4 - self.jump_height)
            ])
            
            # Draw whiskers
            whisker_length = size/1.2
            whisker_y = self.y - size/3 - self.jump_height
            
            # Left whiskers
            pygame.draw.line(screen, WHITE, 
                           (self.x - size/6, whisker_y), 
                           (self.x - whisker_length, whisker_y - size/6), 1)
            pygame.draw.line(screen, WHITE, 
                           (self.x - size/6, whisker_y), 
                           (self.x - whisker_length, whisker_y), 1)
            pygame.draw.line(screen, WHITE, 
                           (self.x - size/6, whisker_y), 
                           (self.x - whisker_length, whisker_y + size/6), 1)
            
            # Right whiskers
            pygame.draw.line(screen, WHITE, 
                           (self.x + size/6, whisker_y), 
                           (self.x + whisker_length, whisker_y - size/6), 1)
            pygame.draw.line(screen, WHITE, 
                           (self.x + size/6, whisker_y), 
                           (self.x + whisker_length, whisker_y), 1)
            pygame.draw.line(screen, WHITE, 
                           (self.x + size/6, whisker_y), 
                           (self.x + whisker_length, whisker_y + size/6), 1)
class Note:
    def __init__(self, track, speed=NOTE_SPEED, note_type="normal"):
        self.track = track  # Which track/lane the note is in (0-3)
        self.x = (track + 1) * TRACK_WIDTH - TRACK_WIDTH // 2
        self.y = 0
        self.speed = speed
        self.width = int(50 * SCALE_X)
        self.height = int(20 * SCALE_Y)
        self.active = True
        self.hit = False
        self.missed = False
        self.note_type = note_type  # "normal", "hold", or "special"
        self.color = [RED, GREEN, BLUE, YELLOW][track]
        
        # Special note properties
        if note_type == "special":
            self.color = PURPLE
            self.width = int(60 * SCALE_X)
            self.height = int(30 * SCALE_Y)
        elif note_type == "hold":
            self.color = CYAN
            self.height = int(60 * SCALE_Y)
    
    def update(self):
        self.y += self.speed
        # Check if note has passed the target area without being hit
        if self.y > TARGET_Y + GOOD_THRESHOLD and not self.hit:
            self.missed = True
            self.active = False
    
    def draw(self, screen):
        if self.active:
            if self.note_type == "normal":
                # Draw note with 3D effect
                pygame.draw.rect(screen, self.color, 
                                (self.x - self.width // 2, self.y - self.height // 2, 
                                 self.width, self.height))
                # Add highlight on top edge
                pygame.draw.line(screen, WHITE, 
                               (self.x - self.width // 2, self.y - self.height // 2),
                               (self.x + self.width // 2, self.y - self.height // 2), int(2 * SCALE_Y))
                # Add shadow on bottom edge
                pygame.draw.line(screen, BLACK, 
                               (self.x - self.width // 2, self.y + self.height // 2),
                               (self.x + self.width // 2, self.y + self.height // 2), int(2 * SCALE_Y))
                
                # Draw arrow triangle icon matching the track
                if self.track == 0:  # Up arrow
                    # Draw triangle pointing up
                    pygame.draw.polygon(screen, BLACK, [
                        (self.x, self.y - int(10 * SCALE_Y)),  # Top point
                        (self.x - int(8 * SCALE_X), self.y + int(5 * SCALE_Y)),  # Bottom left
                        (self.x + int(8 * SCALE_X), self.y + int(5 * SCALE_Y))   # Bottom right
                    ])
                elif self.track == 1:  # Down arrow
                    # Draw triangle pointing down
                    pygame.draw.polygon(screen, BLACK, [
                        (self.x, self.y + int(10 * SCALE_Y)),  # Bottom point
                        (self.x - int(8 * SCALE_X), self.y - int(5 * SCALE_Y)),  # Top left
                        (self.x + int(8 * SCALE_X), self.y - int(5 * SCALE_Y))   # Top right
                    ])
                elif self.track == 2:  # Right arrow
                    # Draw triangle pointing right
                    pygame.draw.polygon(screen, BLACK, [
                        (self.x + int(10 * SCALE_X), self.y),  # Right point
                        (self.x - int(5 * SCALE_X), self.y - int(8 * SCALE_Y)),  # Top left
                        (self.x - int(5 * SCALE_X), self.y + int(8 * SCALE_Y))   # Bottom left
                    ])
                elif self.track == 3:  # Left arrow
                    # Draw triangle pointing left
                    pygame.draw.polygon(screen, BLACK, [
                        (self.x - int(10 * SCALE_X), self.y),  # Left point
                        (self.x + int(5 * SCALE_X), self.y - int(8 * SCALE_Y)),  # Top right
                        (self.x + int(5 * SCALE_X), self.y + int(8 * SCALE_Y))   # Bottom right
                    ])
                
            elif self.note_type == "special":
                # Draw special note with glow effect
                pygame.draw.rect(screen, self.color, 
                                (self.x - self.width // 2, self.y - self.height // 2, 
                                 self.width, self.height))
                
                # Add star effect
                pygame.draw.polygon(screen, YELLOW, [
                    (self.x, self.y - self.height // 2),
                    (self.x + int(10 * SCALE_X), self.y - int(5 * SCALE_Y)),
                    (self.x + int(20 * SCALE_X), self.y - self.height // 2),
                    (self.x + int(10 * SCALE_X), self.y + int(5 * SCALE_Y))
                ])
                
                # Draw arrow triangle icon matching the track - slightly larger for special notes
                if self.track == 0:  # Up arrow
                    pygame.draw.polygon(screen, BLACK, [
                        (self.x, self.y - int(12 * SCALE_Y)),  # Top point
                        (self.x - int(10 * SCALE_X), self.y + int(6 * SCALE_Y)),  # Bottom left
                        (self.x + int(10 * SCALE_X), self.y + int(6 * SCALE_Y))   # Bottom right
                    ])
                elif self.track == 1:  # Down arrow
                    pygame.draw.polygon(screen, BLACK, [
                        (self.x, self.y + int(12 * SCALE_Y)),  # Bottom point
                        (self.x - int(10 * SCALE_X), self.y - int(6 * SCALE_Y)),  # Top left
                        (self.x + int(10 * SCALE_X), self.y - int(6 * SCALE_Y))   # Top right
                    ])
                elif self.track == 2:  # Right arrow
                    pygame.draw.polygon(screen, BLACK, [
                        (self.x + int(12 * SCALE_X), self.y),  # Right point
                        (self.x - int(6 * SCALE_X), self.y - int(10 * SCALE_Y)),  # Top left
                        (self.x - int(6 * SCALE_X), self.y + int(10 * SCALE_Y))   # Bottom left
                    ])
                elif self.track == 3:  # Left arrow
                    pygame.draw.polygon(screen, BLACK, [
                        (self.x - int(12 * SCALE_X), self.y),  # Left point
                        (self.x + int(6 * SCALE_X), self.y - int(10 * SCALE_Y)),  # Top right
                        (self.x + int(6 * SCALE_X), self.y + int(10 * SCALE_Y))   # Bottom right
                    ])
                
            elif self.note_type == "hold":
                # Draw hold note
                pygame.draw.rect(screen, self.color, 
                                (self.x - self.width // 2, self.y - self.height // 2, 
                                 self.width, self.height))
                
                # Add hold line indicators
                pygame.draw.line(screen, WHITE, 
                                (self.x - self.width // 2, self.y), 
                                (self.x + self.width // 2, self.y), int(2 * SCALE_Y))
                
                # Draw arrow triangle icon for hold notes
                if self.track == 0:  # Up arrow
                    pygame.draw.polygon(screen, BLACK, [
                        (self.x, self.y - int(10 * SCALE_Y)),  # Top point
                        (self.x - int(8 * SCALE_X), self.y + int(5 * SCALE_Y)),  # Bottom left
                        (self.x + int(8 * SCALE_X), self.y + int(5 * SCALE_Y))   # Bottom right
                    ])
                elif self.track == 1:  # Down arrow
                    pygame.draw.polygon(screen, BLACK, [
                        (self.x, self.y + int(10 * SCALE_Y)),  # Bottom point
                        (self.x - int(8 * SCALE_X), self.y - int(5 * SCALE_Y)),  # Top left
                        (self.x + int(8 * SCALE_X), self.y - int(5 * SCALE_Y))   # Top right
                    ])
                elif self.track == 2:  # Right arrow
                    pygame.draw.polygon(screen, BLACK, [
                        (self.x + int(10 * SCALE_X), self.y),  # Right point
                        (self.x - int(5 * SCALE_X), self.y - int(8 * SCALE_Y)),  # Top left
                        (self.x - int(5 * SCALE_X), self.y + int(8 * SCALE_Y))   # Bottom left
                    ])
                elif self.track == 3:  # Left arrow
                    pygame.draw.polygon(screen, BLACK, [
                        (self.x - int(10 * SCALE_X), self.y),  # Left point
                        (self.x + int(5 * SCALE_X), self.y - int(8 * SCALE_Y)),  # Top right
                        (self.x + int(5 * SCALE_X), self.y + int(8 * SCALE_Y))   # Bottom right
                    ])
                
                # Add "HOLD" text below the arrow
                hold_font = pygame.font.SysFont(None, int(18 * SCALE_Y))
                hold_surf = hold_font.render("HOLD", True, BLACK)
                hold_rect = hold_surf.get_rect(center=(self.x, self.y + int(15 * SCALE_Y)))
                screen.blit(hold_surf, hold_rect)
class ComboEffect:
    def __init__(self, x, y, combo, font):
        self.x = x
        self.y = y
        self.combo = combo
        self.font = pygame.font.SysFont(None, 48)  # Larger font for combo
        self.lifetime = 1.0
        self.scale = 1.0
        
        # Different colors based on combo milestones
        if combo >= 50:
            self.color = PURPLE
        elif combo >= 30:
            self.color = ORANGE
        elif combo >= 20:
            self.color = CYAN
        elif combo >= 10:
            self.color = YELLOW
        else:
            self.color = WHITE
            
        self.text_surface = self.font.render(f"{combo} COMBO!", True, self.color)
        self.text_rect = self.text_surface.get_rect(center=(x, y - 50))  # Position above hit area
        
    def update(self):
        self.lifetime -= 0.02
        
        # Pulsating effect
        self.scale = 1.0 + 0.2 * math.sin(self.lifetime * 10)
        
        return self.lifetime > 0
        
    def draw(self, screen):
        # Scale the text for pulsating effect
        scaled_surface = pygame.transform.scale(
            self.text_surface, 
            (int(self.text_surface.get_width() * self.scale), 
             int(self.text_surface.get_height() * self.scale))
        )
        
        scaled_rect = scaled_surface.get_rect(center=self.text_rect.center)
        
        # Apply fade out
        alpha = int(self.lifetime * 255)
        temp_surface = pygame.Surface(scaled_surface.get_size(), pygame.SRCALPHA)
        temp_surface.fill((0, 0, 0, 0))  # Transparent
        temp_surface.blit(scaled_surface, (0, 0))
        temp_surface.set_alpha(alpha)
        
        screen.blit(temp_surface, scaled_rect)

class HitEffect:
    def __init__(self, x, y, text, color, font):
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.font = font
        self.lifetime = 1.0  # 1.0 to 0.0
        self.text_surface = self.font.render(text, True, color)
        self.text_rect = self.text_surface.get_rect(center=(x, y))
        
    def update(self):
        self.y -= 2  # Move up
        self.lifetime -= 0.02
        self.text_rect.center = (self.x, self.y)
        return self.lifetime > 0
        
    def draw(self, screen):
        alpha = int(self.lifetime * 255)
        temp_surface = pygame.Surface(self.text_surface.get_size(), pygame.SRCALPHA)
        temp_surface.fill((0, 0, 0, 0))  # Transparent
        temp_surface.blit(self.text_surface, (0, 0))
        temp_surface.set_alpha(alpha)
        screen.blit(temp_surface, self.text_rect)
class RhythmGame:
    def __init__(self):
        # Create a fullscreen or windowed display based on screen size
        if user_screen_width >= 1920 and user_screen_height >= 1080:
            # For large screens, use a windowed mode with the calculated size
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        else:
            # For smaller screens, use a resizable window
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
            
        pygame.display.set_caption("Rhythm Master")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, int(36 * SCALE_Y))
        
        # Game state
        self.running = True
        self.score = 0
        self.level = 1
        self.combo = 0
        self.max_combo = 0
        self.health = 100
        self.notes = []
        self.hit_effects = []
        self.combo_effects = []
        self.animal_animations = []  # List to store active animal animations
        self.start_time = time.time()
        self.elapsed_time = 0
        self.next_note_time = 1.0  # Time until next note spawn
        # Difficulty settings
        self.difficulty = 'normal'  # Default difficulty
        self.apply_difficulty_settings()
        
        # Load sound effects
        self.load_sounds()
        
        # Key mappings (Up, Down, Right, Left for 4 tracks)
        self.key_mappings = [pygame.K_UP, pygame.K_DOWN, pygame.K_RIGHT, pygame.K_LEFT]
        
        # Game state
        self.paused = False
        self.perfect_streak = 0
        self.total_notes = 0
        self.notes_hit = 0
        self.perfect_hits = 0
        self.good_hits = 0
        self.misses = 0
        
        # Level up effect
        self.level_up_time = 0
        self.show_level_up = False
    def load_sounds(self):
        # Create dictionary for sound effects
        self.sound_effects = {}
        
        # Create funny sound effects using pygame's synthesizer capabilities
        try:
            import numpy as np
            
            # Create a perfect hit sound (ascending happy tones)
            perfect_buffer = np.zeros((44100,), dtype=np.int16)
            for i in range(5000):
                perfect_buffer[i] = int(32767 * np.sin(i/10) * np.exp(-i/4000))
                perfect_buffer[i+5000] = int(32767 * np.sin(i/8) * np.exp(-i/4000))
                perfect_buffer[i+10000] = int(32767 * np.sin(i/6) * np.exp(-i/4000))
            self.sound_effects['perfect'] = pygame.mixer.Sound(buffer=perfect_buffer)
            
            # Create a good hit sound (medium tone)
            good_buffer = np.zeros((44100,), dtype=np.int16)
            for i in range(8000):
                good_buffer[i] = int(32767 * np.sin(i/12) * np.exp(-i/4000))
            self.sound_effects['good'] = pygame.mixer.Sound(buffer=good_buffer)
            
            # Create a miss sound (descending sad tones)
            miss_buffer = np.zeros((44100,), dtype=np.int16)
            for i in range(10000):
                miss_buffer[i] = int(32767 * np.sin((10000-i)/8) * np.exp(-i/8000))
            self.sound_effects['miss'] = pygame.mixer.Sound(buffer=miss_buffer)
            
            # Create a level up sound (triumphant fanfare)
            level_up_buffer = np.zeros((44100,), dtype=np.int16)
            for i in range(5000):
                level_up_buffer[i] = int(20000 * np.sin(i/4) * np.exp(-i/10000))
            for i in range(5000):
                level_up_buffer[i+5000] = int(20000 * np.sin(i/3) * np.exp(-i/10000))
            for i in range(10000):
                level_up_buffer[i+10000] = int(20000 * np.sin(i/2) * np.exp(-i/10000))
            self.sound_effects['level_up'] = pygame.mixer.Sound(buffer=level_up_buffer)
            
            # Create a combo sound (quick ascending notes)
            combo_buffer = np.zeros((44100,), dtype=np.int16)
            for i in range(2000):
                combo_buffer[i] = int(20000 * np.sin(i/10) * np.exp(-i/2000))
            for i in range(2000):
                combo_buffer[i+2000] = int(20000 * np.sin(i/8) * np.exp(-i/2000))
            for i in range(2000):
                combo_buffer[i+4000] = int(20000 * np.sin(i/6) * np.exp(-i/2000))
            self.sound_effects['combo'] = pygame.mixer.Sound(buffer=combo_buffer)
            
            # Create a game over sound (dramatic descending tones)
            game_over_buffer = np.zeros((44100,), dtype=np.int16)
            for i in range(20000):
                game_over_buffer[i] = int(20000 * np.sin((20000-i)/2) * np.exp(-i/15000))
                if i % 1000 < 500:  # Add pulsing effect
                    game_over_buffer[i] = int(game_over_buffer[i] * 0.7)
            self.sound_effects['game_over'] = pygame.mixer.Sound(buffer=game_over_buffer)
            
            # Create animal sounds
            # Bird chirp
            bird_buffer = np.zeros((44100,), dtype=np.int16)
            for i in range(1000):
                bird_buffer[i] = int(20000 * np.sin(i/2) * np.exp(-i/500))
            for i in range(1000):
                bird_buffer[i+1500] = int(20000 * np.sin(i/1.5) * np.exp(-i/500))
            self.sound_effects['bird'] = pygame.mixer.Sound(buffer=bird_buffer)
            
            # Frog ribbit
            frog_buffer = np.zeros((44100,), dtype=np.int16)
            for i in range(3000):
                frog_buffer[i] = int(20000 * np.sin(i/20) * np.exp(-i/2000))
                if i % 200 < 100:  # Add warble
                    frog_buffer[i] = int(frog_buffer[i] * 0.7)
            self.sound_effects['frog'] = pygame.mixer.Sound(buffer=frog_buffer)
            
            # Rabbit hop
            rabbit_buffer = np.zeros((44100,), dtype=np.int16)
            for i in range(1000):
                rabbit_buffer[i] = int(10000 * np.sin(i/8) * np.exp(-i/500))
            self.sound_effects['rabbit'] = pygame.mixer.Sound(buffer=rabbit_buffer)
            
            # Cat meow
            cat_buffer = np.zeros((44100,), dtype=np.int16)
            for i in range(5000):
                cat_buffer[i] = int(15000 * np.sin((5000-i)/15) * np.exp(-i/4000))
                if i % 500 < 250:  # Add warble
                    cat_buffer[i] = int(cat_buffer[i] * 1.2)
            self.sound_effects['cat'] = pygame.mixer.Sound(buffer=cat_buffer)
            
            # Set appropriate volumes
            self.sound_effects['perfect'].set_volume(0.4)
            self.sound_effects['good'].set_volume(0.3)
            self.sound_effects['miss'].set_volume(0.3)
            self.sound_effects['level_up'].set_volume(0.5)
            self.sound_effects['combo'].set_volume(0.4)
            self.sound_effects['game_over'].set_volume(0.6)
            self.sound_effects['bird'].set_volume(0.3)
            self.sound_effects['frog'].set_volume(0.3)
            self.sound_effects['rabbit'].set_volume(0.3)
            self.sound_effects['cat'].set_volume(0.3)
            
            print("Custom sound effects created successfully!")
        except Exception as e:
            print(f"Error creating custom sounds: {e}")
            print("Using fallback sounds...")
            
            # Create simple fallback sounds using basic pygame functionality
            try:
                # Create simple tones of different lengths
                self.sound_effects['perfect'] = pygame.mixer.Sound(buffer=bytes([128] * 5000))
                self.sound_effects['good'] = pygame.mixer.Sound(buffer=bytes([128] * 3000))
                self.sound_effects['miss'] = pygame.mixer.Sound(buffer=bytes([128] * 8000))
                self.sound_effects['level_up'] = pygame.mixer.Sound(buffer=bytes([128] * 10000))
                self.sound_effects['combo'] = pygame.mixer.Sound(buffer=bytes([128] * 4000))
                self.sound_effects['game_over'] = pygame.mixer.Sound(buffer=bytes([128] * 15000))
                self.sound_effects['bird'] = pygame.mixer.Sound(buffer=bytes([128] * 2000))
                self.sound_effects['frog'] = pygame.mixer.Sound(buffer=bytes([128] * 3000))
                self.sound_effects['rabbit'] = pygame.mixer.Sound(buffer=bytes([128] * 1000))
                self.sound_effects['cat'] = pygame.mixer.Sound(buffer=bytes([128] * 4000))
                
                # Set volumes
                for key in self.sound_effects:
                    self.sound_effects[key].set_volume(0.3)
                
                print("Created simple fallback sounds")
            except Exception as e2:
                print(f"Could not create fallback sounds: {e2}")
                print("Game will run without sound effects")
    def apply_difficulty_settings(self):
        settings = DIFFICULTY_SETTINGS[self.difficulty]
        self.note_speed = settings['note_speed']
        self.spawn_rate_min = settings['spawn_rate_min']
        self.spawn_rate_max = settings['spawn_rate_max']
        self.perfect_threshold = settings['perfect_threshold']
        self.good_threshold = settings['good_threshold']
    
    def spawn_note(self):
        track = random.randint(0, TRACK_COUNT - 1)
        
        # Randomly decide if this will be a special note (10% chance)
        note_type = "normal"
        rand_val = random.random()
        if rand_val < 0.1:
            note_type = "special"
        elif rand_val < 0.2:
            note_type = "hold"
            
        self.notes.append(Note(track, self.note_speed, note_type))
        self.total_notes += 1
    
    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            # Handle window resize events
            if event.type == pygame.VIDEORESIZE:
                # Update screen size
                global SCREEN_WIDTH, SCREEN_HEIGHT, SCALE_X, SCALE_Y, TRACK_WIDTH, TARGET_Y
                SCREEN_WIDTH = event.w
                SCREEN_HEIGHT = event.h
                SCALE_X = SCREEN_WIDTH / BASE_WIDTH
                SCALE_Y = SCREEN_HEIGHT / BASE_HEIGHT
                TRACK_WIDTH = SCREEN_WIDTH // (TRACK_COUNT + 1)
                TARGET_Y = SCREEN_HEIGHT - int(100 * SCALE_Y)
                
                # Update difficulty settings with new scaling
                self.apply_difficulty_settings()
            
            if event.type == pygame.KEYDOWN:
                # Check if a track key was pressed
                for i, key in enumerate(self.key_mappings):
                    if event.key == key:
                        self.check_note_hit(i)
                
                # Escape key to pause/unpause
                if event.key == pygame.K_ESCAPE:
                    self.paused = not self.paused
                    
                # Difficulty change keys (1, 2, 3)
                if event.key == pygame.K_1:
                    self.difficulty = 'easy'
                    self.apply_difficulty_settings()
                elif event.key == pygame.K_2:
                    self.difficulty = 'normal'
                    self.apply_difficulty_settings()
                elif event.key == pygame.K_3:
                    self.difficulty = 'hard'
                    self.apply_difficulty_settings()
                    
                # Toggle fullscreen with F11
                if event.key == pygame.K_F11:
                    pygame.display.toggle_fullscreen()
    def check_note_hit(self, track):
        # Find the closest active note in the pressed track
        closest_note = None
        min_distance = float('inf')
        
        for note in self.notes:
            if note.active and note.track == track and not note.hit:
                distance = abs(note.y - TARGET_Y)
                if distance < min_distance:
                    min_distance = distance
                    closest_note = note
        
        # Check if we found a note and it's within the hit threshold
        if closest_note is not None:
            x = (track + 1) * TRACK_WIDTH - TRACK_WIDTH // 2
            
            # Calculate score multiplier based on note type and level
            score_multiplier = 1 * (1 + (self.level - 1) * 0.1)  # 10% increase per level
            if closest_note.note_type == "special":
                score_multiplier *= 2
            elif closest_note.note_type == "hold":
                score_multiplier *= 1.5
            
            if min_distance <= self.perfect_threshold:
                points = int(100 * score_multiplier)
                self.score += points
                self.combo += 1
                self.perfect_streak += 1
                self.perfect_hits += 1
                self.notes_hit += 1
                self.health = min(100, self.health + 2)
                
                # Show different text for streaks
                if self.perfect_streak >= 5:
                    self.hit_effects.append(HitEffect(x, TARGET_Y, f"PERFECT x{self.perfect_streak}!", GREEN, self.font))
                else:
                    self.hit_effects.append(HitEffect(x, TARGET_Y, "PERFECT!", GREEN, self.font))
                
                # Create animal animation for perfect hit
                self.animal_animations.append(AnimalAnimation(x, TARGET_Y - 20, track))
                
                # Play animal sound based on track
                animal_sound = ["bird", "frog", "rabbit", "cat"][track]
                if animal_sound in self.sound_effects:
                    self.sound_effects[animal_sound].play()
                
                closest_note.hit = True
                closest_note.active = False
                
                # Play perfect sound
                if 'perfect' in self.sound_effects:
                    self.sound_effects['perfect'].play()
                
            elif min_distance <= self.good_threshold:
                points = int(50 * score_multiplier)
                self.score += points
                self.combo += 1
                self.perfect_streak = 0
                self.good_hits += 1
                self.notes_hit += 1
                self.health = min(100, self.health + 1)
                self.hit_effects.append(HitEffect(x, TARGET_Y, "GOOD!", BLUE, self.font))
                
                # Create smaller animal animation for good hit
                animal = AnimalAnimation(x, TARGET_Y - 10, track)
                animal.scale = 0.7  # Make it smaller
                self.animal_animations.append(animal)
                
                closest_note.hit = True
                closest_note.active = False
                
                # Play good sound
                if 'good' in self.sound_effects:
                    self.sound_effects['good'].play()
                
            else:
                self.combo = 0
                self.perfect_streak = 0
                self.health -= 5
                self.misses += 1
                self.hit_effects.append(HitEffect(x, TARGET_Y, "MISS!", RED, self.font))
                
                # Play miss sound
                if 'miss' in self.sound_effects:
                    self.sound_effects['miss'].play()
            
            # Update max combo
            if self.combo > self.max_combo:
                self.max_combo = self.combo
                
            # Show combo effect at certain thresholds
            if self.combo > 0 and self.combo % 10 == 0:
                self.combo_effects.append(ComboEffect(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, self.combo, self.font))
                
                # Play combo sound
                if 'combo' in self.sound_effects:
                    self.sound_effects['combo'].play()
            
            # Check for level up
            self.check_level_up()
    def check_level_up(self):
        # Find the current level based on score
        new_level = 1
        for i, threshold in enumerate(LEVEL_THRESHOLDS):
            if self.score >= threshold:
                new_level = i + 1
        
        # If level increased, show level up effect
        if new_level > self.level:
            self.level = new_level
            self.show_level_up = True
            self.level_up_time = 2.0  # Show level up message for 2 seconds
            
            # Play level up sound
            if 'level_up' in self.sound_effects:
                self.sound_effects['level_up'].play()
    
    def update(self):
        if self.paused:
            return
            
        # Update elapsed time
        current_time = time.time()
        frame_time = current_time - self.start_time - self.elapsed_time
        self.elapsed_time += frame_time
        
        # Update level up effect
        if self.show_level_up:
            self.level_up_time -= frame_time
            if self.level_up_time <= 0:
                self.show_level_up = False
        
        # Spawn new notes based on timing
        self.next_note_time -= frame_time
        if self.next_note_time <= 0:
            self.spawn_note()
            # Random time until next note based on difficulty
            self.next_note_time = random.uniform(self.spawn_rate_min, self.spawn_rate_max)
        
        # Update all notes
        for note in self.notes[:]:
            note.update()
            if note.missed:
                self.combo = 0
                self.perfect_streak = 0
                self.health -= 10
                self.misses += 1
                self.notes.remove(note)
            elif not note.active:
                self.notes.remove(note)
        
        # Update hit effects
        self.hit_effects = [effect for effect in self.hit_effects if effect.update()]
        
        # Update combo effects
        self.combo_effects = [effect for effect in self.combo_effects if effect.update()]
        
        # Update animal animations
        self.animal_animations = [animal for animal in self.animal_animations if animal.update()]
        
        # Check game over condition
        if self.health <= 0:
            self.show_game_over()
    def calculate_grade(self):
        if self.total_notes == 0:
            return "N/A"
            
        accuracy = (self.perfect_hits * 100 + self.good_hits * 50) / (self.total_notes * 100)
        
        if accuracy >= 0.95 and self.max_combo >= self.total_notes * 0.9:
            return "S"
        elif accuracy >= 0.9:
            return "A"
        elif accuracy >= 0.8:
            return "B"
        elif accuracy >= 0.7:
            return "C"
        elif accuracy >= 0.6:
            return "D"
        else:
            return "F"
    
    def draw(self):
        # Clear screen
        self.screen.fill(BLACK)
        
        # Draw tracks
        for i in range(TRACK_COUNT):
            x = (i + 1) * TRACK_WIDTH
            pygame.draw.line(self.screen, GRAY, (x, 0), (x, SCREEN_HEIGHT), int(2 * SCALE_Y))
        
        # Draw target line
        pygame.draw.line(self.screen, WHITE, (0, TARGET_Y), (SCREEN_WIDTH, TARGET_Y), int(3 * SCALE_Y))
        
        # Draw track hit buttons with clearer icons
        for i in range(TRACK_COUNT):
            x = (i + 1) * TRACK_WIDTH - TRACK_WIDTH // 2
            color = [RED, GREEN, BLUE, YELLOW][i]
            
            # Draw larger circle with fill and outline
            circle_radius = int(35 * SCALE_Y)
            pygame.draw.circle(self.screen, color, (x, TARGET_Y), circle_radius)
            pygame.draw.circle(self.screen, WHITE, (x, TARGET_Y), circle_radius, int(3 * SCALE_Y))
            
            # Draw custom icons instead of arrow text
            if i == 0:  # Up arrow
                # Draw triangle pointing up
                pygame.draw.polygon(self.screen, BLACK, [
                    (x, TARGET_Y - int(15 * SCALE_Y)),  # Top point
                    (x - int(12 * SCALE_X), TARGET_Y + int(5 * SCALE_Y)),  # Bottom left
                    (x + int(12 * SCALE_X), TARGET_Y + int(5 * SCALE_Y))   # Bottom right
                ])
            elif i == 1:  # Down arrow
                # Draw triangle pointing down
                pygame.draw.polygon(self.screen, BLACK, [
                    (x, TARGET_Y + int(15 * SCALE_Y)),  # Bottom point
                    (x - int(12 * SCALE_X), TARGET_Y - int(5 * SCALE_Y)),  # Top left
                    (x + int(12 * SCALE_X), TARGET_Y - int(5 * SCALE_Y))   # Top right
                ])
            elif i == 2:  # Right arrow
                # Draw triangle pointing right
                pygame.draw.polygon(self.screen, BLACK, [
                    (x + int(15 * SCALE_X), TARGET_Y),  # Right point
                    (x - int(5 * SCALE_X), TARGET_Y - int(12 * SCALE_Y)),  # Top left
                    (x - int(5 * SCALE_X), TARGET_Y + int(12 * SCALE_Y))   # Bottom left
                ])
            elif i == 3:  # Left arrow
                # Draw triangle pointing left
                pygame.draw.polygon(self.screen, BLACK, [
                    (x - int(15 * SCALE_X), TARGET_Y),  # Left point
                    (x + int(5 * SCALE_X), TARGET_Y - int(12 * SCALE_Y)),  # Top right
                    (x + int(5 * SCALE_X), TARGET_Y + int(12 * SCALE_Y))   # Bottom right
                ])
        
        # Draw all notes
        for note in self.notes:
            note.draw(self.screen)
        
        # Draw hit effects
        for effect in self.hit_effects:
            effect.draw(self.screen)
            
        # Draw combo effects
        for effect in self.combo_effects:
            effect.draw(self.screen)
            
        # Draw animal animations
        for animal in self.animal_animations:
            animal.draw(self.screen)
        
        # Draw UI elements
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (int(10 * SCALE_X), int(10 * SCALE_Y)))
        
        # Draw level indicator
        level_text = self.font.render(f"Level: {self.level}", True, ORANGE)
        self.screen.blit(level_text, (int(10 * SCALE_X), int(50 * SCALE_Y)))
        
        # Draw next level threshold
        if self.level < len(LEVEL_THRESHOLDS):
            next_level = LEVEL_THRESHOLDS[self.level]
            progress = min(1.0, (self.score - LEVEL_THRESHOLDS[self.level-1]) / 
                          (next_level - LEVEL_THRESHOLDS[self.level-1]))
            
            # Draw level progress bar
            bar_width = int(150 * SCALE_X)
            pygame.draw.rect(self.screen, GRAY, (int(170 * SCALE_X), int(55 * SCALE_Y), bar_width, int(20 * SCALE_Y)), 1)
            pygame.draw.rect(self.screen, ORANGE, (int(170 * SCALE_X), int(55 * SCALE_Y), int(bar_width * progress), int(20 * SCALE_Y)))
        
        combo_text = self.font.render(f"Combo: {self.combo}", True, WHITE)
        self.screen.blit(combo_text, (int(10 * SCALE_X), int(90 * SCALE_Y)))
        
        # Draw difficulty indicator
        difficulty_color = GREEN if self.difficulty == 'easy' else YELLOW if self.difficulty == 'normal' else RED
        difficulty_text = self.font.render(f"Difficulty: {self.difficulty.upper()}", True, difficulty_color)
        self.screen.blit(difficulty_text, (int(10 * SCALE_X), int(130 * SCALE_Y)))
        
        # Draw perfect streak if active
        if self.perfect_streak >= 3:
            streak_text = self.font.render(f"Perfect Streak: {self.perfect_streak}", True, PURPLE)
            self.screen.blit(streak_text, (int(10 * SCALE_X), int(170 * SCALE_Y)))
        
        # Draw health bar
        health_bar_width = int(200 * SCALE_X)
        health_bar_height = int(20 * SCALE_Y)
        health_bar_x = SCREEN_WIDTH - int(210 * SCALE_X)
        pygame.draw.rect(self.screen, RED, (health_bar_x, int(10 * SCALE_Y), health_bar_width, health_bar_height), 1)
        pygame.draw.rect(self.screen, RED, (health_bar_x, int(10 * SCALE_Y), int(self.health * health_bar_width / 100), health_bar_height))
        
        # Draw current grade
        grade = self.calculate_grade()
        grade_text = self.font.render(f"Grade: {grade}", True, WHITE)
        self.screen.blit(grade_text, (SCREEN_WIDTH - int(100 * SCALE_X), int(40 * SCALE_Y)))
        
        # Draw level up effect if active
        if self.show_level_up:
            # Create semi-transparent overlay
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 128))
            self.screen.blit(overlay, (0, 0))
            
            # Draw level up text with pulsating effect
            pulse = 1.0 + 0.2 * math.sin(time.time() * 10)
            level_font = pygame.font.SysFont(None, int(72 * pulse))
            level_up_text = level_font.render(f"LEVEL UP! {self.level-1} → {self.level}", True, ORANGE)
            level_up_rect = level_up_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(level_up_text, level_up_rect)
            
            # Draw bonus info
            bonus_font = pygame.font.SysFont(None, 36)
            bonus_text = bonus_font.render(f"Score Multiplier: +{(self.level-1)*10}%", True, YELLOW)
            bonus_rect = bonus_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
            self.screen.blit(bonus_text, bonus_rect)
        
        # Draw pause indicator if paused
        if self.paused:
            pause_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            pause_surface.fill((0, 0, 0, 128))  # Semi-transparent black
            self.screen.blit(pause_surface, (0, 0))
            
            pause_text = self.font.render("PAUSED", True, WHITE)
            self.screen.blit(pause_text, (SCREEN_WIDTH // 2 - pause_text.get_width() // 2, SCREEN_HEIGHT // 2))
            
            controls_text = self.font.render("Press ESC to resume, 1-2-3 to change difficulty", True, WHITE)
            self.screen.blit(controls_text, (SCREEN_WIDTH // 2 - controls_text.get_width() // 2, SCREEN_HEIGHT // 2 + 40))
            
            key_text = self.font.render("Controls: ↑ ↓ → ←", True, WHITE)
            self.screen.blit(key_text, (SCREEN_WIDTH // 2 - key_text.get_width() // 2, SCREEN_HEIGHT // 2 + 80))
        
        # Update display
        pygame.display.flip()
    def show_game_over(self):
        # Play game over sound
        if 'game_over' in self.sound_effects:
            self.sound_effects['game_over'].play()
            
        # Create animated game over sequence
        animation_frames = 60
        for frame in range(animation_frames):
            # Clear screen
            self.screen.fill(BLACK)
            
            # Calculate animation progress (0.0 to 1.0)
            progress = frame / animation_frames
            
            # Create pulsating red background
            pulse_intensity = 0.3 + 0.2 * math.sin(progress * 10)
            bg_color = (int(128 * pulse_intensity), 0, 0)
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill(bg_color + (100,))  # Add alpha
            self.screen.blit(overlay, (0, 0))
            
            # Animate "GAME OVER" text growing from center
            size_factor = 0.1 + 2.9 * min(1.0, progress * 2)  # Grow to full size by halfway
            game_over_font = pygame.font.SysFont(None, int(100 * size_factor))
            game_over_text = game_over_font.render("GAME OVER", True, RED)
            game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 140))
            self.screen.blit(game_over_text, game_over_rect)
            
            # Fade in other elements after text grows
            if progress > 0.5:
                fade_in = min(1.0, (progress - 0.5) * 2)  # 0.0 to 1.0 in second half
                
                # Create stats elements with fade in
                score_text = self.font.render(f"Final Score: {self.score}", True, WHITE)
                level_text = self.font.render(f"Level Reached: {self.level}", True, ORANGE)
                combo_text = self.font.render(f"Max Combo: {self.max_combo}", True, WHITE)
                
                # Calculate and display accuracy
                if self.total_notes > 0:
                    accuracy = (self.notes_hit / self.total_notes) * 100
                    accuracy_text = self.font.render(f"Accuracy: {accuracy:.1f}%", True, WHITE)
                else:
                    accuracy_text = self.font.render("Accuracy: N/A", True, WHITE)
                    
                # Calculate and display grade
                grade = self.calculate_grade()
                grade_color = WHITE
                if grade == "S":
                    grade_color = PURPLE
                elif grade == "A":
                    grade_color = YELLOW
                elif grade == "B":
                    grade_color = GREEN
                elif grade == "C":
                    grade_color = BLUE
                elif grade == "D":
                    grade_color = ORANGE
                
                # Make grade text larger and animated
                grade_pulse = 1.0 + 0.2 * math.sin(frame / 3)
                grade_font = pygame.font.SysFont(None, int(72 * grade_pulse))
                grade_text = grade_font.render(f"Grade: {grade}", True, grade_color)
                
                # Display hit statistics
                stats_text = self.font.render(f"Perfect: {self.perfect_hits} | Good: {self.good_hits} | Miss: {self.misses}", True, WHITE)
                
                restart_text = self.font.render("Press R to restart or ESC to quit", True, WHITE)
                
                # Apply fade in effect to all elements
                for text_surface in [score_text, level_text, combo_text, accuracy_text, grade_text, stats_text, restart_text]:
                    text_surface.set_alpha(int(255 * fade_in))
                
                # Position and draw all elements
                self.screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, SCREEN_HEIGHT // 2 - 80))
                self.screen.blit(level_text, (SCREEN_WIDTH // 2 - level_text.get_width() // 2, SCREEN_HEIGHT // 2 - 40))
                self.screen.blit(combo_text, (SCREEN_WIDTH // 2 - combo_text.get_width() // 2, SCREEN_HEIGHT // 2))
                self.screen.blit(accuracy_text, (SCREEN_WIDTH // 2 - accuracy_text.get_width() // 2, SCREEN_HEIGHT // 2 + 40))
                
                # Position grade in center with special effect
                grade_rect = grade_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100))
                self.screen.blit(grade_text, grade_rect)
                
                # Draw glowing effect around grade based on grade value
                if grade in ["S", "A"]:
                    glow_radius = int(20 * grade_pulse)
                    glow_surface = pygame.Surface((grade_rect.width + glow_radius*2, grade_rect.height + glow_radius*2), pygame.SRCALPHA)
                    pygame.draw.rect(glow_surface, grade_color + (100,), 
                                    (glow_radius, glow_radius, grade_rect.width, grade_rect.height), 
                                    border_radius=10)
                    glow_rect = glow_surface.get_rect(center=grade_rect.center)
                    self.screen.blit(glow_surface, (glow_rect.x - glow_radius, glow_rect.y - glow_radius))
                
                self.screen.blit(stats_text, (SCREEN_WIDTH // 2 - stats_text.get_width() // 2, SCREEN_HEIGHT // 2 + 160))
                self.screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 200))
            
            # Update display
            pygame.display.flip()
            pygame.time.delay(33)  # ~30 FPS animation
            
            # Check for early exit from animation
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key in [pygame.K_ESCAPE, pygame.K_r, pygame.K_SPACE, pygame.K_RETURN]:
                        animation_frames = frame  # End animation early
        
        # After animation, wait for restart or quit
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self.__init__()  # Reset the game
                        waiting = False
                    elif event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
            self.clock.tick(FPS)
    
    def run(self):
        while self.running:
            self.clock.tick(FPS)
            self.handle_input()
            self.update()
            self.draw()
        
        pygame.quit()

# Run the game
if __name__ == "__main__":
    game = RhythmGame()
    game.run()
# High score management functions
def load_high_scores():
    """Load high scores from file"""
    try:
        if os.path.exists(HIGH_SCORES_FILE):
            with open(HIGH_SCORES_FILE, 'r') as f:
                return json.load(f)
        else:
            return []
    except Exception as e:
        print(f"Error loading high scores: {e}")
        return []

def save_high_score(name, score, difficulty, max_combo, accuracy):
    """Save a new high score"""
    try:
        scores = load_high_scores()
        
        # Add new score
        new_score = {
            'name': name,
            'score': score,
            'difficulty': difficulty,
            'max_combo': max_combo,
            'accuracy': accuracy,
            'date': time.strftime("%Y-%m-%d %H:%M")
        }
        
        scores.append(new_score)
        
        # Sort by score (highest first) and keep only top 5
        scores.sort(key=lambda x: x['score'], reverse=True)
        scores = scores[:5]
        
        # Save to file
        with open(HIGH_SCORES_FILE, 'w') as f:
            json.dump(scores, f)
            
        return scores
    except Exception as e:
        print(f"Error saving high score: {e}")
        return []
