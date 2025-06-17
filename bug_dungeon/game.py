import pygame
import sys
import math
import random
import os
from pygame.locals import *

# Initialize pygame
pygame.init()
pygame.mixer.init()  # Initialize the mixer for audio

# Screen setup
WIDTH, HEIGHT = 1000, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bug Dungeon - Debug Your Way to Victory")

# Colors
BACKGROUND = (20, 12, 36)
PANEL_BG = (30, 22, 46)
TEXT_COLOR = (220, 220, 255)
HIGHLIGHT = (101, 223, 171)
BUTTON_COLOR = (72, 52, 112)
BUTTON_HOVER = (92, 72, 142)
MONSTER_COLOR = (200, 60, 60)
KEY_COLOR = (255, 215, 0)
WALL_COLOR = (60, 40, 80)
FLOOR_COLOR = (90, 70, 110)
DOOR_COLOR = (150, 120, 80)
CURSOR_COLOR = (255, 255, 255)

# Fonts
title_font = pygame.font.SysFont("Courier", 48, bold=True)
header_font = pygame.font.SysFont("Courier", 32, bold=True)
main_font = pygame.font.SysFont("Courier", 24)
small_font = pygame.font.SysFont("Courier", 18)

# Game states
MENU = 0
STORY = 1
MAP = 2
ROOM = 3
PUZZLE = 4
VICTORY = 5
current_state = MENU

# Game data
player_position = [1, 1]  # Starting position
visited_rooms = set()
completed_rooms = set()
monster_health = 0
player_keys = 0
fullscreen = False
music_playing = False
current_track = None
story_scroll_offset = 0
cursor_visible = True
cursor_timer = 0

# Load monster images
try:
    monster_images = {
        "Syntax Serpent": pygame.image.load("pixel_a_monster_01.png").convert_alpha(),
        "Infinite Loop Spider": pygame.image.load("pixel_a_monster_02.png").convert_alpha(),
        "Null Pointer Gremlin": pygame.image.load("pixel_a_monster_03.png").convert_alpha(),
        "Memory Leak Ooze": pygame.image.load("pixel_a_monster_01.png").convert_alpha(),  # Reuse image
        "The Kernel Kraken": pygame.image.load("pixel_a_monster_03.png").convert_alpha()  # Reuse image
    }
    
    # Scale images to 100x100
    for name, img in monster_images.items():
        monster_images[name] = pygame.transform.scale(img, (100, 100))
except:
    print("Warning: Could not load monster images. Using placeholder.")
    # Create placeholder images if real images not found
    monster_images = {}
    placeholder = pygame.Surface((100, 100))
    placeholder.fill((200, 0, 0))
    pygame.draw.circle(placeholder, (0, 0, 200), (50, 50), 40)
    for name in ["Syntax Serpent", "Infinite Loop Spider", "Null Pointer Gremlin", 
                "Memory Leak Ooze", "The Kernel Kraken"]:
        monster_images[name] = placeholder.copy()

# Dungeon map (5x5 grid)
# 0 = wall, 1 = empty room, 2 = monster room, 3 = key room, 4 = boss room
dungeon_map = [
    [0, 0, 0, 0, 0, 0, 0],
    [0, 1, 1, 2, 1, 3, 0],
    [0, 2, 0, 1, 0, 2, 0],
    [0, 1, 1, 2, 3, 1, 0],
    [0, 3, 0, 1, 0, 4, 0],
    [0, 1, 2, 1, 2, 1, 0],
    [0, 0, 0, 0, 0, 0, 0]
]

# Room types descriptions
room_types = {
    1: "Empty Chamber",
    2: "Monster Lair",
    3: "Treasure Vault",
    4: "Boss Arena"
}

# Monster data
monsters = [
    {"name": "Syntax Serpent", "health": 3, "strength": "Caesar Cipher", "art": """
  /^\\/^\\
 _|_O|  |_     Syntax Serpent
\/     \/     Hiss... I'll wrap around your code!
 \     /      Weakness: Shift ciphers
  \   /
   \ /
"""},
    {"name": "Infinite Loop Spider", "health": 4, "strength": "Complex Logic", "art": """
   /\\ _ /\\
  /  ' '  \\   Infinite Loop Spider
 (   >.<   )  I'll trap you in my web!
  \\  =v=  /   Weakness: Loop breakers
   \\_____/
"""},
    {"name": "Null Pointer Gremlin", "health": 2, "strength": "Unexpected Errors", "art": """
   (o   o)
  (   ^   )  Null Pointer Gremlin
 (  <(_)> )  I'll crash your programs!
  (       )  Weakness: Defensive checks
"""},
    {"name": "Memory Leak Ooze", "health": 5, "strength": "Resource Drain", "art": """
   .-~~~~~-.
  {         }  Memory Leak Ooze
  |  o   o |   I'll consume your RAM!
  \   ---   /  Weakness: Garbage collection
   '~~~~~~~'
"""},
    {"name": "The Kernel Kraken", "health": 10, "strength": "System-Level Attacks", "art": """
    .-~~~-.
   {       }
   |  O O  |  The Kernel Kraken
   \   W   /  I control the depths!
    '-----'   Weakness: Root access
"""}
]

# Story text
story_text = [
    "In the forgotten depths of the digital realm,",
    "lies the Bug Dungeon - home to malicious code",
    "creatures that corrupt programs and crash systems.",
    "",
    "You are a Debug Mage, armed with the arcane",
    "art of code manipulation. Your mission:",
    "",
    "1. Navigate the dungeon map",
    "2. Battle bug monsters with code puzzles",
    "3. Collect keys to access new areas",
    "4. Defeat the Kernel Kraken in the final chamber",
    "",
    "Each monster guards a cipher puzzle. Solve it",
    "by writing or fixing code to vanquish the creature.",
    "",
    "Game Controls:",
    "  - Arrow keys: Move on map",
    "  - SPACE: Interact with rooms",
    "  - ENTER: Test code in puzzles",
    "  - Mouse: Click buttons and select code lines",
    "  - F11: Toggle fullscreen",
    "  - Scroll wheel: Scroll through text",
    "",
    "Puzzle Solving Tips:",
    "  - Read the puzzle description carefully",
    "  - Look at the expected output format",
    "  - Test your code frequently with ENTER",
    "  - Successful solutions damage monsters",
    "",
    "Monster Weaknesses:",
    "  - Syntax Serpent: Caesar cipher shifts",
    "  - Infinite Loop Spider: Loop breakers",
    "  - Null Pointer Gremlin: Defensive checks",
    "  - Memory Leak Ooze: Garbage collection",
    "  - Kernel Kraken: Root access techniques",
    "",
    "Press any key to continue..."
]

# Puzzle templates
puzzles = [
    {
        "name": "Caesar Cipher",
        "description": "The ciphertext is encrypted with a Caesar shift. Find the shift value and decrypt the message.",
        "ciphertext": "PJD=LTGQNS",
        "expected": "KEY=GOBLIN",
        "code": [
            "def decrypt(msg):",
            "    shift = 5  # What's the correct shift?",
            "    result = ''",
            "    for char in msg:",
            "        if char.isalpha():",
            "            base = ord('A') if char.isupper() else ord('a')",
            "            result += chr((ord(char) - base - shift) % 26 + base)",
            "        else:",
            "            result += char",
            "    return result"
        ],
        "error": "Shift value is incorrect"
    },
    {
        "name": "Reverse String",
        "description": "The message has been reversed. Write a function to reverse it back.",
        "ciphertext": "NILBOG=YEK",
        "expected": "KEY=GOBLIN",
        "code": [
            "def decrypt(msg):",
            "    # Reverse the string",
            "    return msg  # Fix this line"
        ],
        "error": "String not reversed"
    },
    {
        "name": "Vowel Replacement",
        "description": "All vowels have been replaced with numbers: A=1, E=2, I=3, O=4, U=5. Decode the message.",
        "ciphertext": "K2Y=G4BL3N",
        "expected": "KEY=GOBLIN",
        "code": [
            "def decrypt(msg):",
            "    replacements = {'1': 'A', '2': 'E', '3': 'I', '4': 'O', '5': 'U'}",
            "    result = ''",
            "    for char in msg:",
            "        if char in '12345':",
            "            result += replacements[char]",
            "        else:",
            "            result += char",
            "    return result"
        ],
        "error": "Vowels not replaced correctly"
    }
]

current_puzzle = None
current_monster = None
user_code = []
selected_line = 0
cursor_x = 0  # Initialize cursor_x globally
result_message = ""
puzzle_solved = False

# Button class
class Button:
    def __init__(self, x, y, width, height, text, action=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.hovered = False
        self.visible = True
        
    def draw(self, surface):
        if not self.visible:
            return
            
        color = BUTTON_HOVER if self.hovered else BUTTON_COLOR
        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        pygame.draw.rect(surface, HIGHLIGHT, self.rect, 2, border_radius=8)
        
        text_surf = main_font.render(self.text, True, TEXT_COLOR)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
        
    def check_hover(self, pos):
        if not self.visible:
            return
        self.hovered = self.rect.collidepoint(pos)
        
    def handle_event(self, event):
        if not self.visible:
            return False
            
        if event.type == MOUSEBUTTONDOWN and event.button == 1:
            if self.hovered and self.action:
                self.action()
                return True
        return False

# Create buttons
start_button = Button(WIDTH//2 - 100, HEIGHT//2 + 50, 200, 50, "START GAME")
story_button = Button(WIDTH//2 - 100, HEIGHT//2 + 120, 200, 50, "HOW TO PLAY")
map_button = Button(WIDTH//2 - 100, HEIGHT - 100, 200, 50, "BACK TO MAP")
fullscreen_button = Button(WIDTH - 200, 20, 180, 40, "TOGGLE FULLSCREEN")
music_button = Button(WIDTH - 200, 70, 180, 40, "MUSIC: OFF")
back_to_menu_button = Button(WIDTH//2 - 100, HEIGHT - 100, 200, 50, "BACK TO MENU")

# Draw functions
def draw_menu():
    screen.fill(BACKGROUND)
    
    # Title
    title = title_font.render("BUG DUNGEON", True, HIGHLIGHT)
    subtitle = header_font.render("Debug Your Way to Victory", True, TEXT_COLOR)
    screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//4))
    screen.blit(subtitle, (WIDTH//2 - subtitle.get_width()//2, HEIGHT//4 + 70))
    
    # Decorative elements
    pygame.draw.line(screen, HIGHLIGHT, (WIDTH//2 - 150, HEIGHT//4 + 120), (WIDTH//2 + 150, HEIGHT//4 + 120), 2)
    
    # Buttons
    start_button.visible = True
    story_button.visible = True
    fullscreen_button.visible = True
    music_button.visible = True
    map_button.visible = False
    back_to_menu_button.visible = False
    
    start_button.draw(screen)
    story_button.draw(screen)
    fullscreen_button.draw(screen)
    music_button.draw(screen)
    
    # Character
    char_x, char_y = WIDTH//2, HEIGHT//4 - 120
    pygame.draw.circle(screen, (80, 160, 240), (char_x, char_y), 40)
    pygame.draw.rect(screen, (60, 140, 220), (char_x-30, char_y+40, 60, 80))
    pygame.draw.line(screen, (60, 140, 220), (char_x-30, char_y+80), (char_x-50, char_y+140), 5)
    pygame.draw.line(screen, (60, 140, 220), (char_x+30, char_y+80), (char_x+50, char_y+140), 5)
    pygame.draw.circle(screen, (200, 200, 100), (char_x, char_y+30), 10)  # Staff gem
    
    # Staff
    pygame.draw.line(screen, (200, 180, 100), (char_x, char_y+40), (char_x, char_y+120), 5)

def draw_story():
    global story_scroll_offset
    
    screen.fill(BACKGROUND)
    
    # Title
    title = title_font.render("THE BUG DUNGEON", True, HIGHLIGHT)
    screen.blit(title, (WIDTH//2 - title.get_width()//2, 40))
    
    # Create a surface for the story content that we can scroll
    story_surface = pygame.Surface((WIDTH, len(story_text) * 40 + 100))
    story_surface.fill(BACKGROUND)
    
    # Story text
    y_pos = 40
    for line in story_text:
        text = main_font.render(line, True, TEXT_COLOR)
        story_surface.blit(text, (WIDTH//2 - text.get_width()//2, y_pos))
        y_pos += 40
    
    # Apply scrolling offset
    visible_height = HEIGHT - 200
    max_scroll = max(0, story_surface.get_height() - visible_height)
    story_scroll_offset = max(0, min(story_scroll_offset, max_scroll))
    
    # Draw the visible portion of the story
    screen.blit(story_surface, (0, 80), (0, story_scroll_offset, WIDTH, visible_height))
    
    # Draw scrollbar if needed
    if max_scroll > 0:
        scrollbar_height = visible_height * visible_height // story_surface.get_height()
        scrollbar_pos = (HEIGHT - 120) * story_scroll_offset // max_scroll
        scrollbar_rect = pygame.Rect(WIDTH - 20, 80 + scrollbar_pos, 10, scrollbar_height)
        pygame.draw.rect(screen, HIGHLIGHT, scrollbar_rect, border_radius=5)
    
    # Draw back button
    back_to_menu_button.visible = True
    back_to_menu_button.draw(screen)
    
    # Scroll hint
    if max_scroll > 0:
        hint = small_font.render("Use mouse wheel to scroll", True, HIGHLIGHT)
        screen.blit(hint, (WIDTH//2 - hint.get_width()//2, HEIGHT - 40))

def draw_map():
    screen.fill(BACKGROUND)
    
    # Title
    title = title_font.render("DUNGEON MAP", True, HIGHLIGHT)
    screen.blit(title, (WIDTH//2 - title.get_width()//2, 20))
    
    # Stats
    keys_text = main_font.render(f"Keys: {player_keys}", True, KEY_COLOR)
    rooms_text = main_font.render(f"Rooms Cleared: {len(completed_rooms)}/12", True, TEXT_COLOR)
    screen.blit(keys_text, (30, 30))
    screen.blit(rooms_text, (WIDTH - rooms_text.get_width() - 30, 30))
    
    # Draw map grid
    cell_size = 70
    grid_width = len(dungeon_map[0]) * cell_size
    grid_height = len(dungeon_map) * cell_size
    grid_x = (WIDTH - grid_width) // 2
    grid_y = (HEIGHT - grid_height) // 2 + 20
    
    for y, row in enumerate(dungeon_map):
        for x, cell in enumerate(row):
            rect = pygame.Rect(grid_x + x * cell_size, grid_y + y * cell_size, cell_size, cell_size)
            
            # Draw walls and rooms
            if cell == 0:  # Wall
                pygame.draw.rect(screen, WALL_COLOR, rect)
                pygame.draw.rect(screen, (40, 30, 60), rect, 2)
            else:  # Room
                # Draw room base
                room_color = FLOOR_COLOR
                if (x, y) in completed_rooms:
                    room_color = (70, 150, 70)  # Completed room
                pygame.draw.rect(screen, room_color, rect, border_radius=8)
                pygame.draw.rect(screen, (120, 100, 140), rect, 2, border_radius=8)
                
                # Draw room type indicator
                if cell == 2:  # Monster
                    pygame.draw.circle(screen, MONSTER_COLOR, rect.center, 15)
                elif cell == 3:  # Key
                    pygame.draw.circle(screen, KEY_COLOR, rect.center, 15)
                elif cell == 4:  # Boss
                    pygame.draw.circle(screen, (200, 40, 40), rect.center, 18)
                    pygame.draw.circle(screen, (240, 180, 40), rect.center, 10)
            
            # Draw player position
            if [x, y] == player_position:
                pygame.draw.circle(screen, HIGHLIGHT, rect.center, 10)
                pygame.draw.circle(screen, (40, 180, 240), rect.center, 6)
    
    # Draw map key
    key_x = 50
    key_y = HEIGHT - 180
    pygame.draw.rect(screen, PANEL_BG, (key_x-10, key_y-10, 250, 170), border_radius=10)
    key_title = header_font.render("Map Key", True, HIGHLIGHT)
    screen.blit(key_title, (key_x + 125 - key_title.get_width()//2, key_y))
    
    key_y += 50
    pygame.draw.circle(screen, HIGHLIGHT, (key_x, key_y), 8)
    screen.blit(small_font.render("Player", True, TEXT_COLOR), (key_x + 20, key_y-10))
    
    key_y += 30
    pygame.draw.circle(screen, MONSTER_COLOR, (key_x, key_y), 8)
    screen.blit(small_font.render("Monster Room", True, TEXT_COLOR), (key_x + 20, key_y-10))
    
    key_y += 30
    pygame.draw.circle(screen, KEY_COLOR, (key_x, key_y), 8)
    screen.blit(small_font.render("Treasure Room", True, TEXT_COLOR), (key_x + 20, key_y-10))
    
    key_y += 30
    pygame.draw.circle(screen, (200, 40, 40), (key_x, key_y), 10)
    pygame.draw.circle(screen, (240, 180, 40), (key_x, key_y), 5)
    screen.blit(small_font.render("Boss Room", True, TEXT_COLOR), (key_x + 20, key_y-10))
    
    # Draw buttons
    map_button.visible = True
    fullscreen_button.visible = True
    music_button.visible = True
    map_button.draw(screen)
    fullscreen_button.draw(screen)
    music_button.draw(screen)

def draw_room():
    screen.fill(BACKGROUND)
    
    # Get current room type
    x, y = player_position
    room_type = dungeon_map[y][x]
    room_name = room_types.get(room_type, "Unknown Room")
    
    # Title
    title = title_font.render(room_name, True, HIGHLIGHT)
    screen.blit(title, (WIDTH//2 - title.get_width()//2, 20))
    
    # Room content
    content_rect = pygame.Rect(50, 80, WIDTH-100, HEIGHT-180)
    pygame.draw.rect(screen, PANEL_BG, content_rect, border_radius=12)
    pygame.draw.rect(screen, (80, 60, 100), content_rect, 3, border_radius=12)
    
    if room_type == 1:  # Empty room
        draw_empty_room(content_rect)
    elif room_type == 2:  # Monster room
        draw_monster_room(content_rect)
    elif room_type == 3:  # Key room
        draw_key_room(content_rect)
    elif room_type == 4:  # Boss room
        draw_boss_room(content_rect)
    
    # Draw buttons
    map_button.visible = True
    fullscreen_button.visible = True
    music_button.visible = True
    map_button.draw(screen)
    fullscreen_button.draw(screen)
    music_button.draw(screen)

def draw_empty_room(rect):
    title = header_font.render("Empty Chamber", True, TEXT_COLOR)
    screen.blit(title, (rect.x + rect.width//2 - title.get_width()//2, rect.y + 20))
    
    desc = main_font.render("This room appears to be empty.", True, TEXT_COLOR)
    screen.blit(desc, (rect.x + rect.width//2 - desc.get_width()//2, rect.y + 80))
    
    desc2 = main_font.render("No monsters or treasure here.", True, TEXT_COLOR)
    screen.blit(desc2, (rect.x + rect.width//2 - desc2.get_width()//2, rect.y + 120))
    
    # Draw decorative elements
    pygame.draw.rect(screen, WALL_COLOR, (rect.x + 100, rect.y + 180, rect.width - 200, 150), border_radius=10)
    
    # Draw cobwebs
    for i in range(3):
        web_x = rect.x + 150 + i * 200
        web_y = rect.y + 220
        pygame.draw.line(screen, (180, 180, 200), (web_x, web_y), (web_x-20, web_y-30), 2)
        pygame.draw.line(screen, (180, 180, 200), (web_x, web_y), (web_x+20, web_y-30), 2)
        pygame.draw.line(screen, (180, 180, 200), (web_x, web_y), (web_x, web_y+40), 2)
        pygame.draw.circle(screen, (180, 180, 200), (web_x, web_y), 20, 1)
    
    action_text = main_font.render("Press SPACE to continue exploring", True, HIGHLIGHT)
    screen.blit(action_text, (rect.x + rect.width//2 - action_text.get_width()//2, rect.y + rect.height - 60))

def draw_monster_room(rect):
    global current_monster
    
    if not current_monster:
        # Select a random monster that hasn't been defeated yet
        available_monsters = [m for m in monsters if m["name"] not in completed_rooms]
        if available_monsters:
            current_monster = random.choice(available_monsters)
        else:
            current_monster = monsters[-1]  # Default to boss if all defeated
    
    # Draw monster info
    title = header_font.render(current_monster["name"], True, MONSTER_COLOR)
    screen.blit(title, (rect.x + rect.width//2 - title.get_width()//2, rect.y + 20))
    
    # Draw health bar
    pygame.draw.rect(screen, (60, 20, 20), (rect.x + 150, rect.y + 70, rect.width - 300, 25))
    health_width = max(0, (rect.width - 300) * current_monster["health"] / 10)
    pygame.draw.rect(screen, MONSTER_COLOR, (rect.x + 150, rect.y + 70, health_width, 25))
    health_text = main_font.render(f"Health: {current_monster['health']}/10", True, TEXT_COLOR)
    screen.blit(health_text, (rect.x + rect.width//2 - health_text.get_width()//2, rect.y + 75))
    
    # Draw monster image
    if current_monster["name"] in monster_images:
        monster_img = monster_images[current_monster["name"]]
        img_rect = monster_img.get_rect(center=(rect.centerx, rect.centery - 20))
        screen.blit(monster_img, img_rect)
    
    # Draw strength
    strength = main_font.render(f"Strength: {current_monster['strength']}", True, (220, 150, 150))
    screen.blit(strength, (rect.x + rect.width//2 - strength.get_width()//2, rect.y + rect.height - 120))
    
    # Draw action button
    if (player_position[0], player_position[1]) in completed_rooms:
        action_text = main_font.render("Monster defeated! Press SPACE to leave", True, HIGHLIGHT)
    else:
        action_text = main_font.render("Press SPACE to battle the monster", True, HIGHLIGHT)
    screen.blit(action_text, (rect.x + rect.width//2 - action_text.get_width()//2, rect.y + rect.height - 60))

def draw_key_room(rect):
    # Draw room title
    title = header_font.render("Treasure Vault", True, KEY_COLOR)
    screen.blit(title, (rect.x + rect.width//2 - title.get_width()//2, rect.y + 20))
    
    # Draw chest
    pygame.draw.rect(screen, (150, 100, 50), (rect.centerx - 60, rect.y + 100, 120, 70), border_radius=10)
    pygame.draw.rect(screen, (180, 140, 60), (rect.centerx - 50, rect.y + 110, 100, 50))
    pygame.draw.arc(screen, (150, 100, 50), (rect.centerx - 60, rect.y + 70, 120, 60), 0, math.pi, 5)
    
    # Draw key inside chest if not collected
    if (player_position[0], player_position[1]) not in completed_rooms:
        pygame.draw.rect(screen, KEY_COLOR, (rect.centerx - 40, rect.y + 140, 80, 10), border_radius=5)
        pygame.draw.circle(screen, KEY_COLOR, (rect.centerx, rect.y + 130), 15)
        pygame.draw.rect(screen, KEY_COLOR, (rect.centerx - 5, rect.y + 130, 10, 20))
        
        action_text = main_font.render("Press SPACE to collect the key", True, HIGHLIGHT)
        screen.blit(action_text, (rect.x + rect.width//2 - action_text.get_width()//2, rect.y + rect.height - 60))
    else:
        action_text = main_font.render("Treasure collected! Press SPACE to leave", True, HIGHLIGHT)
        screen.blit(action_text, (rect.x + rect.width//2 - action_text.get_width()//2, rect.y + rect.height - 60))
    
    # Draw key count
    keys_text = main_font.render(f"You have {player_keys} keys", True, KEY_COLOR)
    screen.blit(keys_text, (rect.x + rect.width//2 - keys_text.get_width()//2, rect.y + 220))

def draw_boss_room(rect):
    # Draw boss info
    boss = monsters[-1]  # The Kernel Kraken
    
    title = header_font.render(boss["name"], True, (200, 40, 40))
    screen.blit(title, (rect.x + rect.width//2 - title.get_width()//2, rect.y + 20))
    
    # Draw health bar
    pygame.draw.rect(screen, (60, 20, 20), (rect.x + 100, rect.y + 70, rect.width - 200, 30))
    health_width = max(0, (rect.width - 200) * boss["health"] / 10)
    pygame.draw.rect(screen, (200, 40, 40), (rect.x + 100, rect.y + 70, health_width, 30))
    health_text = main_font.render(f"Health: {boss['health']}/10", True, TEXT_COLOR)
    screen.blit(health_text, (rect.x + rect.width//2 - health_text.get_width()//2, rect.y + 75))
    
    # Draw boss image
    if boss["name"] in monster_images:
        monster_img = monster_images[boss["name"]]
        # Scale boss image larger
        scaled_img = pygame.transform.scale(monster_img, (150, 150))
        img_rect = scaled_img.get_rect(center=(rect.centerx, rect.centery - 20))
        screen.blit(scaled_img, img_rect)
    
    # Draw strength
    strength = main_font.render(f"Strength: {boss['strength']}", True, (220, 100, 100))
    screen.blit(strength, (rect.x + rect.width//2 - strength.get_width()//2, rect.y + rect.height - 120))
    
    # Draw action button
    if boss["health"] <= 0:
        action_text = main_font.render("BOSS DEFEATED! Press SPACE to claim victory", True, HIGHLIGHT)
    elif player_keys < 3:
        action_text = main_font.render(f"You need 3 keys to fight the boss ({player_keys}/3)", True, (200, 150, 50))
    else:
        action_text = main_font.render("Press SPACE to battle the final boss", True, HIGHLIGHT)
    screen.blit(action_text, (rect.x + rect.width//2 - action_text.get_width()//2, rect.y + rect.height - 60))

def draw_puzzle():
    global current_puzzle, cursor_visible, cursor_x
    
    if not current_puzzle:
        current_puzzle = random.choice(puzzles)
        user_code[:] = current_puzzle["code"]
        cursor_x = len(user_code[selected_line])  # Initialize cursor position
    
    screen.fill(BACKGROUND)
    
    # Title
    title = title_font.render("CODE BATTLE", True, HIGHLIGHT)
    screen.blit(title, (WIDTH//2 - title.get_width()//2, 20))
    
    # Draw puzzle area
    puzzle_rect = pygame.Rect(50, 80, WIDTH-100, HEIGHT-180)
    pygame.draw.rect(screen, PANEL_BG, puzzle_rect, border_radius=12)
    pygame.draw.rect(screen, (80, 60, 100), puzzle_rect, 3, border_radius=12)
    
    # Puzzle info
    puzzle_title = header_font.render(current_puzzle["name"], True, TEXT_COLOR)
    screen.blit(puzzle_title, (puzzle_rect.x + 20, puzzle_rect.y + 20))
    
    # Ciphertext
    cipher_text = main_font.render(f"Ciphertext: {current_puzzle['ciphertext']}", True, HIGHLIGHT)
    screen.blit(cipher_text, (puzzle_rect.x + 20, puzzle_rect.y + 70))
    
    # Expected result
    expected_text = main_font.render(f"Expected: {current_puzzle['expected']}", True, HIGHLIGHT)
    screen.blit(expected_text, (puzzle_rect.x + 20, puzzle_rect.y + 110))
    
    # Description
    desc = small_font.render(current_puzzle["description"], True, TEXT_COLOR)
    screen.blit(desc, (puzzle_rect.x + 20, puzzle_rect.y + 150))
    
    # Code editor
    code_rect = pygame.Rect(puzzle_rect.x + 20, puzzle_rect.y + 200, puzzle_rect.width - 40, 200)
    pygame.draw.rect(screen, (20, 15, 30), code_rect)
    pygame.draw.rect(screen, (60, 50, 80), code_rect, 2)
    
    # Draw code lines
    y_pos = code_rect.y + 10
    for i, line in enumerate(user_code):
        color = HIGHLIGHT if i == selected_line else TEXT_COLOR
        code_line = small_font.render(line, True, color)
        screen.blit(code_line, (code_rect.x + 10, y_pos))
        
        # Draw cursor on the selected line
        if i == selected_line and cursor_visible:
            # Calculate cursor position
            prefix = line[:cursor_x]
            prefix_width = small_font.size(prefix)[0]
            cursor_rect = pygame.Rect(code_rect.x + 10 + prefix_width, y_pos, 2, 20)
            pygame.draw.rect(screen, CURSOR_COLOR, cursor_rect)
        
        y_pos += 22
    
    # Result message
    result_color = HIGHLIGHT if puzzle_solved else (220, 60, 60)
    result_text = main_font.render(result_message, True, result_color)
    screen.blit(result_text, (puzzle_rect.x + 20, puzzle_rect.y + 410))
    
    # Action button
    if puzzle_solved:
        action_text = main_font.render("Press SPACE to return and damage the monster", True, HIGHLIGHT)
        screen.blit(action_text, (puzzle_rect.x + puzzle_rect.width//2 - action_text.get_width()//2, 
                                puzzle_rect.y + puzzle_rect.height - 40))
    else:
        action_text = main_font.render("Press ENTER to test your code", True, TEXT_COLOR)
        screen.blit(action_text, (puzzle_rect.x + puzzle_rect.width//2 - action_text.get_width()//2, 
                                puzzle_rect.y + puzzle_rect.height - 40))
    
    # Draw buttons
    map_button.visible = True
    fullscreen_button.visible = True
    music_button.visible = True
    map_button.draw(screen)
    fullscreen_button.draw(screen)
    music_button.draw(screen)

def draw_victory():
    screen.fill(BACKGROUND)
    
    # Title
    title = title_font.render("VICTORY!", True, KEY_COLOR)
    screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//4))
    
    # Message
    msg = header_font.render("You have defeated the Kernel Kraken!", True, TEXT_COLOR)
    screen.blit(msg, (WIDTH//2 - msg.get_width()//2, HEIGHT//4 + 80))
    
    stats = [
        f"Rooms Explored: {len(visited_rooms)}",
        f"Monsters Defeated: {len(completed_rooms)}",
        f"Keys Collected: {player_keys}",
        "",
        "The Bug Dungeon has been cleansed of",
        "malicious code creatures... for now."
    ]
    
    y_pos = HEIGHT//2
    for line in stats:
        text = main_font.render(line, True, TEXT_COLOR)
        screen.blit(text, (WIDTH//2 - text.get_width()//2, y_pos))
        y_pos += 50
    
    # Play again button
    pygame.draw.rect(screen, BUTTON_COLOR, (WIDTH//2 - 100, HEIGHT - 100, 200, 50), border_radius=8)
    restart = main_font.render("PLAY AGAIN", True, TEXT_COLOR)
    screen.blit(restart, (WIDTH//2 - restart.get_width()//2, HEIGHT - 85))

# Game functions
def evaluate_code():
    global result_message, puzzle_solved, current_monster
    
    try:
        # Simulate code execution
        if current_puzzle["name"] == "Caesar Cipher":
            # Check if the shift value is correct
            shift_line = user_code[1]
            if "shift = 5" not in shift_line and "shift=5" not in shift_line:
                result_message = current_puzzle["error"]
                puzzle_solved = False
            else:
                result_message = "Decryption successful! KEY=GOBLIN"
                puzzle_solved = True
                
        elif current_puzzle["name"] == "Reverse String":
            # Check if the string is reversed
            if "return msg[::-1]" in user_code[1] or "return ''.join(reversed(msg))" in user_code[1]:
                result_message = "Decryption successful! KEY=GOBLIN"
                puzzle_solved = True
            else:
                result_message = current_puzzle["error"]
                puzzle_solved = False
                
        elif current_puzzle["name"] == "Vowel Replacement":
            # Check if the vowel replacement is implemented
            if "replacements" in user_code[1] and "result" in user_code[4]:
                result_message = "Decryption successful! KEY=GOBLIN"
                puzzle_solved = True
            else:
                result_message = current_puzzle["error"]
                puzzle_solved = False
        
        # If solved, damage the monster
        if puzzle_solved and current_monster:
            current_monster["health"] -= 3
            if current_monster["health"] <= 0:
                completed_rooms.add((player_position[0], player_position[1]))
    
    except Exception as e:
        result_message = f"Error: {str(e)}"
        puzzle_solved = False

def start_game():
    global current_state, player_position, visited_rooms, completed_rooms, player_keys
    current_state = MAP
    player_position = [1, 1]
    visited_rooms = set()
    completed_rooms = set()
    player_keys = 0
    visited_rooms.add((1, 1))
    
    # Reset monsters
    for monster in monsters:
        if monster["name"] == "The Kernel Kraken":
            monster["health"] = 10
        else:
            monster["health"] = random.randint(3, 6)

def show_story():
    global current_state, story_scroll_offset
    current_state = STORY
    story_scroll_offset = 0

def back_to_map():
    global current_state, current_puzzle, current_monster
    current_state = MAP
    current_puzzle = None
    current_monster = None

def back_to_menu():
    global current_state
    current_state = MENU

def toggle_fullscreen():
    global fullscreen, screen
    fullscreen = not fullscreen
    if fullscreen:
        screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
        fullscreen_button.text = "FULLSCREEN: ON"
    else:
        screen = pygame.display.set_mode((WIDTH, HEIGHT))
        fullscreen_button.text = "FULLSCREEN: OFF"

def toggle_music():
    global music_playing, music_button
    music_playing = not music_playing
    
    if music_playing:
        music_button.text = "MUSIC: ON"
        try:
            # Try to load and play music
            pygame.mixer.music.load("Broken PenWave.mp3")  # Load the music file
            pygame.mixer.music.set_volume(0.5)  # Set volume to 50%
            pygame.mixer.music.play(-1)  # -1 means loop indefinitely
        except:
            print("Could not load music file")
            music_playing = False
            music_button.text = "MUSIC: ERROR"
    else:
        music_button.text = "MUSIC: OFF"
        pygame.mixer.music.stop()

def handle_room_action():
    global current_state, player_keys, current_monster, puzzle_solved, result_message
    
    x, y = player_position
    room_type = dungeon_map[y][x]
    
    if room_type == 1:  # Empty room
        # Mark room as visited
        visited_rooms.add((x, y))
        back_to_map()
        
    elif room_type == 2:  # Monster room
        if (x, y) in completed_rooms:
            # Monster already defeated
            back_to_map()
        else:
            # Start battle
            current_state = PUZZLE
            puzzle_solved = False
            result_message = ""
            
    elif room_type == 3:  # Key room
        if (x, y) not in completed_rooms:
            player_keys += 1
            completed_rooms.add((x, y))
        back_to_map()
        
    elif room_type == 4:  # Boss room
        if monsters[-1]["health"] <= 0:
            # Boss already defeated
            current_state = VICTORY
        elif player_keys >= 3:
            # Start boss battle
            current_state = PUZZLE
            puzzle_solved = False
            result_message = ""
        else:
            # Not enough keys
            back_to_map()

def move_player(dx, dy):
    global player_position
    
    x, y = player_position
    new_x, new_y = x + dx, y + dy
    
    # Check if new position is valid
    if 0 <= new_x < len(dungeon_map[0]) and 0 <= new_y < len(dungeon_map):
        if dungeon_map[new_y][new_x] != 0:  # Not a wall
            player_position = [new_x, new_y]
            visited_rooms.add((new_x, new_y))

def reset_game():
    global current_state, player_position, visited_rooms, completed_rooms, player_keys
    global current_monster, current_puzzle, monster_health, puzzle_solved, result_message, cursor_x
    
    current_state = MENU
    player_position = [1, 1]
    visited_rooms = set()
    completed_rooms = set()
    player_keys = 0
    current_monster = None
    current_puzzle = None
    monster_health = 0
    puzzle_solved = False
    result_message = ""
    cursor_x = 0  # Reset cursor position
    
    # Reset monsters
    for monster in monsters:
        monster["health"] = 10 if monster["name"] == "The Kernel Kraken" else random.randint(3, 6)

# Main game loop
reset_game()
clock = pygame.time.Clock()

# Set button actions
start_button.action = start_game
story_button.action = show_story
map_button.action = back_to_map
fullscreen_button.action = toggle_fullscreen
music_button.action = toggle_music
back_to_menu_button.action = back_to_menu

# List of all buttons for easier handling
all_buttons = [start_button, story_button, map_button, fullscreen_button, 
               music_button, back_to_menu_button]

running = True
while running:
    mouse_pos = pygame.mouse.get_pos()
    dt = clock.tick(60)  # Delta time in milliseconds
    
    # Update cursor blink timer
    cursor_timer += dt
    if cursor_timer >= 500:  # Blink every 500ms
        cursor_visible = not cursor_visible
        cursor_timer = 0
    
    # Handle hover effects for all buttons
    for button in all_buttons:
        button.check_hover(mouse_pos)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        # Handle button clicks
        if event.type == MOUSEBUTTONDOWN and event.button == 1:
            for button in all_buttons:
                if button.visible and button.hovered:
                    button.action()
                    break  # Only handle one button click per event
            
            # Handle scrolling in story screen
            if current_state == STORY:
                if event.button == 4:  # Scroll up
                    story_scroll_offset = max(0, story_scroll_offset - 30)
                elif event.button == 5:  # Scroll down
                    story_scroll_offset += 30
        
        # Handle scrolling with mouse wheel
        if event.type == MOUSEWHEEL:
            if current_state == STORY:
                story_scroll_offset = max(0, story_scroll_offset - event.y * 30)
        
        # Handle keyboard events
        if event.type == KEYDOWN:
            if event.key == K_F11:  # F11 toggles fullscreen
                toggle_fullscreen()
                
            if current_state == MENU:
                if event.key == K_RETURN:
                    start_game()
                
            elif current_state == STORY:
                if event.key:
                    current_state = MAP
                
            elif current_state == MAP:
                if event.key == K_UP:
                    move_player(0, -1)
                elif event.key == K_DOWN:
                    move_player(0, 1)
                elif event.key == K_LEFT:
                    move_player(-1, 0)
                elif event.key == K_RIGHT:
                    move_player(1, 0)
                elif event.key == K_RETURN:
                    current_state = ROOM
                
            elif current_state == ROOM:
                if event.key == K_SPACE:
                    handle_room_action()
                
            elif current_state == PUZZLE:
                if event.key == K_UP:
                    if selected_line > 0:
                        selected_line -= 1
                        cursor_x = min(cursor_x, len(user_code[selected_line]))
                        cursor_visible = True
                        cursor_timer = 0
                elif event.key == K_DOWN:
                    if selected_line < len(user_code) - 1:
                        selected_line += 1
                        cursor_x = min(cursor_x, len(user_code[selected_line]))
                        cursor_visible = True
                        cursor_timer = 0
                elif event.key == K_LEFT:
                    if cursor_x > 0:
                        cursor_x -= 1
                        cursor_visible = True
                        cursor_timer = 0
                elif event.key == K_RIGHT:
                    if cursor_x < len(user_code[selected_line]):
                        cursor_x += 1
                        cursor_visible = True
                        cursor_timer = 0
                elif event.key == K_RETURN:
                    evaluate_code()
                elif event.key == K_SPACE and puzzle_solved:
                    back_to_map()
                elif event.key == K_BACKSPACE:
                    if cursor_x > 0:
                        # Remove character before cursor
                        line = user_code[selected_line]
                        user_code[selected_line] = line[:cursor_x-1] + line[cursor_x:]
                        cursor_x -= 1
                        cursor_visible = True
                        cursor_timer = 0
                    elif cursor_x == 0 and selected_line > 0:
                        # Merge with previous line
                        cursor_x = len(user_code[selected_line-1])
                        user_code[selected_line-1] += user_code[selected_line]
                        del user_code[selected_line]
                        selected_line -= 1
                        cursor_visible = True
                        cursor_timer = 0
                elif event.key == K_DELETE:
                    if cursor_x < len(user_code[selected_line]):
                        # Delete character at cursor
                        line = user_code[selected_line]
                        user_code[selected_line] = line[:cursor_x] + line[cursor_x+1:]
                        cursor_visible = True
                        cursor_timer = 0
                elif event.key == K_HOME:
                    cursor_x = 0
                    cursor_visible = True
                    cursor_timer = 0
                elif event.key == K_END:
                    cursor_x = len(user_code[selected_line])
                    cursor_visible = True
                    cursor_timer = 0
                elif event.key == K_TAB:
                    # Insert 4 spaces for indentation
                    line = user_code[selected_line]
                    user_code[selected_line] = line[:cursor_x] + "    " + line[cursor_x:]
                    cursor_x += 4
                    cursor_visible = True
                    cursor_timer = 0
                elif event.unicode:
                    # Insert typed character at cursor position
                    line = user_code[selected_line]
                    user_code[selected_line] = line[:cursor_x] + event.unicode + line[cursor_x:]
                    cursor_x += len(event.unicode)
                    cursor_visible = True
                    cursor_timer = 0
                
            elif current_state == VICTORY:
                if event.key == K_RETURN:
                    reset_game()
    
    # Draw current state
    if current_state == MENU:
        draw_menu()
    elif current_state == STORY:
        draw_story()
    elif current_state == MAP:
        draw_map()
    elif current_state == ROOM:
        draw_room()
    elif current_state == PUZZLE:
        draw_puzzle()
    elif current_state == VICTORY:
        draw_victory()
    
    pygame.display.flip()

pygame.quit()
sys.exit()