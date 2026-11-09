#MAS JADINYA YANG INI YAA, INI YANG PALING LUCU OKKAYY
import pygame
import random
import math
import os
import json
import wave
import struct
import time
import array

# ==================================================
# INITIALIZATION
# ==================================================

pygame.mixer.pre_init(22050, -16, 1, 512)
pygame.init()

WIDTH, HEIGHT = 800, 600
FPS = 60

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("♡ Pastel Block Breaker ♡")

clock = pygame.time.Clock()

# ==================================================
# PASTEL COLOR PALETTE
# ==================================================

BG_TOP = (255, 235, 244)
BG_BOTTOM = (229, 226, 255)

PINK = (255, 174, 204)
BABY_PINK = (255, 210, 224)
LAVENDER = (202, 184, 255)
BABY_BLUE = (177, 220, 255)
MINT = (181, 235, 215)
CREAM = (255, 239, 190)
PEACH = (255, 197, 169)

WHITE = (255, 255, 255)
DARK = (105, 91, 125)
SOFT_PURPLE = (153, 132, 180)

PASTEL_COLORS = [
    PINK,
    LAVENDER,
    BABY_BLUE,
    MINT,
    CREAM,
    PEACH
]

# ==================================================
# FONTS
# ==================================================

font_tiny = pygame.font.SysFont("arial", 15)
font_small = pygame.font.SysFont("arial", 18)
font_medium = pygame.font.SysFont("arial", 25, bold=True)
font_large = pygame.font.SysFont("arial", 38, bold=True)
font_title = pygame.font.SysFont("arial", 53, bold=True)

# ==================================================
# FILES
# ==================================================

AUDIO_FOLDER = "game_audio"
LEADERBOARD_FILE = "leaderboard.json"

# ==================================================
# BACKGROUND DECORATION
# ==================================================

stars = []

for i in range(55):
    stars.append({
        "x": random.randint(0, WIDTH),
        "y": random.randint(0, HEIGHT),
        "size": random.randint(2, 4),
        "phase": random.random() * 6.28
    })

def draw_background():
    for y in range(HEIGHT):
        ratio = y / HEIGHT

        r = int(
            BG_TOP[0] * (1 - ratio)
            + BG_BOTTOM[0] * ratio
        )
        g = int(
            BG_TOP[1] * (1 - ratio)
            + BG_BOTTOM[1] * ratio
        )
        b = int(
            BG_TOP[2] * (1 - ratio)
            + BG_BOTTOM[2] * ratio
        )

        pygame.draw.line(
            screen,
            (r, g, b),
            (0, y),
            (WIDTH, y)
        )

    for star in stars:
        brightness = (
            math.sin(
                pygame.time.get_ticks() / 500
                + star["phase"]
            ) + 1
        ) / 2

        color_value = int(180 + brightness * 65)

        color = (
            color_value,
            color_value - 10,
            255
        )

        pygame.draw.circle(
            screen,
            color,
            (star["x"], star["y"]),
            star["size"]
        )

    # Decorative circles
    pygame.draw.circle(
        screen,
        (255, 218, 232),
        (30, 80),
        55
    )

    pygame.draw.circle(
        screen,
        (255, 218, 232),
        (770, 510),
        70
    )

# ==================================================
# DRAWING UTILITIES
# ==================================================

def draw_text(
    text,
    font,
    color,
    x,
    y,
    center=True
):
    surface = font.render(str(text), True, color)

    if center:
        rect = surface.get_rect(center=(x, y))
    else:
        rect = surface.get_rect(topleft=(x, y))

    screen.blit(surface, rect)

def draw_panel(x, y, width, height):
    shadow = pygame.Rect(
        x + 5,
        y + 6,
        width,
        height
    )

    pygame.draw.rect(
        screen,
        (218, 205, 237),
        shadow,
        border_radius=25
    )

    pygame.draw.rect(
        screen,
        WHITE,
        (x, y, width, height),
        border_radius=25
    )

    pygame.draw.rect(
        screen,
        (245, 225, 245),
        (x, y, width, height),
        3,
        border_radius=25
    )

def draw_button(text, x, y, width, height, color):
    rect = pygame.Rect(
        x, y, width, height
    )

    mouse_pos = pygame.mouse.get_pos()
    hovered = rect.collidepoint(mouse_pos)

    shadow = rect.copy()
    shadow.y += 5

    pygame.draw.rect(
        screen,
        (190, 175, 210),
        shadow,
        border_radius=18
    )

    button_color = color

    if hovered:
        button_color = tuple(
            min(255, c + 12)
            for c in color
        )

    pygame.draw.rect(
        screen,
        button_color,
        rect,
        border_radius=18
    )

    pygame.draw.rect(
        screen,
        WHITE,
        rect,
        3,
        border_radius=18
    )

    draw_text(
        text,
        font_medium,
        DARK,
        rect.centerx,
        rect.centery
    )

    return rect

def draw_heart(x, y, size=18):
    pygame.draw.circle(
        screen,
        PINK,
        (x - size // 4, y),
        size // 2
    )

    pygame.draw.circle(
        screen,
        PINK,
        (x + size // 4, y),
        size // 2
    )

    points = [
        (x - size // 2, y),
        (x + size // 2, y),
        (x, y + size)
    ]

    pygame.draw.polygon(
        screen,
        PINK,
        points
    )

# ==================================================
# CUTE AUDIO SYSTEM
# ==================================================

audio_enabled = True
audio_available = False
sounds = {}

def create_audio_folder():
    os.makedirs(
        AUDIO_FOLDER,
        exist_ok=True
    )

def create_sound_file(
    filename,
    notes,
    duration=0.12,
    volume=0.25
):
    filepath = os.path.join(
        AUDIO_FOLDER,
        filename
    )

    if os.path.exists(filepath):
        return filepath

    sample_rate = 22050
    frames = int(sample_rate * duration)

    with wave.open(filepath, "w") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)

        for i in range(frames):
            t = i / sample_rate
            ratio = i / frames

            note_index = min(
                int(ratio * len(notes)),
                len(notes) - 1
            )

            frequency = notes[note_index]

            # Soft bell-like sound
            tone = (
                math.sin(2 * math.pi * frequency * t)
                * 0.75
                + math.sin(
                    2 * math.pi * frequency * 2 * t
                ) * 0.15
            )

            envelope = (1 - ratio) ** 1.5

            sample = int(
                tone * envelope * volume * 32767
            )

            wav.writeframes(
                struct.pack("<h", sample)
            )

    return filepath

def create_background_music():
    filepath = os.path.join(
        AUDIO_FOLDER,
        "background_music.wav"
    )

    if os.path.exists(filepath):
        return filepath

    sample_rate = 22050

    # Gentle, happy pastel melody
    melody = [
        523, 659, 784, 659,
        587, 698, 880, 698,
        523, 659, 784, 880,
        784, 698, 659, 523,
        587, 698, 784, 698,
        659, 784, 880, 1046,
        880, 784, 698, 659,
        523, 659, 784, 523
    ]

    note_duration = 0.20
    duration = len(melody) * note_duration

    frames = int(sample_rate * duration)

    with wave.open(filepath, "w") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)

        for i in range(frames):
            t = i / sample_rate

            step = int(t / note_duration)
            step = min(step, len(melody) - 1)

            frequency = melody[step]

            local_time = t % note_duration

            # Soft sine melody
            main_tone = math.sin(
                2 * math.pi * frequency * t
            )

            # Gentle lower harmony
            harmony = math.sin(
                2 * math.pi * (frequency / 2) * t
            )

            # Soft pluck envelope
            envelope = min(
                1,
                local_time / 0.025
            )

            envelope *= math.exp(
                -local_time * 2.5
            )

            sample = int(
                (
                    main_tone * 0.18
                    + harmony * 0.06
                )
                * envelope
                * 32767
            )

            sample = max(
                -32767,
                min(32767, sample)
            )

            wav.writeframes(
                struct.pack("<h", sample)
            )

    return filepath

def initialize_audio():
    global audio_available, sounds

    try:
        create_audio_folder()

        music_path = create_background_music()

        sound_files = {
            "click": create_sound_file(
                "click.wav",
                [700, 900, 1100],
                0.10,
                0.20
            ),

            "paddle": create_sound_file(
                "paddle.wav",
                [500, 700, 850],
                0.13,
                0.28
            ),

            "brick": create_sound_file(
                "brick.wav",
                [900, 1100, 1300, 1500],
                0.16,
                0.30
            ),

            "life": create_sound_file(
                "life.wav",
                [600, 450, 300],
                0.30,
                0.25
            ),

            "win": create_sound_file(
                "win.wav",
                [523, 659, 784, 1046, 1318],
                0.65,
                0.30
            ),

            "gameover": create_sound_file(
                "gameover.wav",
                [500, 400, 300, 220],
                0.60,
                0.25
            )
        }

        for name, path in sound_files.items():
            sounds[name] = pygame.mixer.Sound(path)

        pygame.mixer.music.load(music_path)
        pygame.mixer.music.set_volume(0.35)
        pygame.mixer.music.play(-1)

        audio_available = True

    except pygame.error:
        audio_available = False
        sounds = {}

def play_sound(name):
    if audio_enabled and audio_available:
        if name in sounds:
            sounds[name].play()

def toggle_sound():
    global audio_enabled

    audio_enabled = not audio_enabled

    if audio_available:
        if audio_enabled:
            pygame.mixer.music.unpause()
        else:
            pygame.mixer.music.pause()

# ==================================================
# LEADERBOARD
# ==================================================

def load_leaderboard():
    if not os.path.exists(LEADERBOARD_FILE):
        return []

    try:
        with open(LEADERBOARD_FILE, "r") as file:
            data = json.load(file)

        return data if isinstance(data, list) else []

    except (json.JSONDecodeError, OSError):
        return []

def save_leaderboard(data):
    with open(LEADERBOARD_FILE, "w") as file:
        json.dump(data, file, indent=4)

def add_player_result(
    name,
    score,
    difficulty,
    duration
):
    leaderboard = load_leaderboard()

    leaderboard.append({
        "name": name,
        "score": score,
        "difficulty": difficulty,
        "time": round(duration, 2),
        "date": time.strftime("%d-%m-%Y")
    })

    leaderboard.sort(
        key=lambda player: player["score"],
        reverse=True
    )

    leaderboard = leaderboard[:100]

    save_leaderboard(leaderboard)

# ==================================================
# DIFFICULTY
# ==================================================

DIFFICULTIES = {
    "Easy": {
        "lives": 5,
        "ball_speed": 4,
        "paddle_width": 150,
        "paddle_speed": 9,
        "block_health": 1
    },

    "Normal": {
        "lives": 3,
        "ball_speed": 5,
        "paddle_width": 120,
        "paddle_speed": 8,
        "block_health": 1
    },

    "Hard": {
        "lives": 2,
        "ball_speed": 7,
        "paddle_width": 85,
        "paddle_speed": 7,
        "block_health": 2
    }
}

# ==================================================
# NAME INPUT SCREEN
# ==================================================

def name_input_screen():
    name = ""

    while True:
        draw_background()

        draw_panel(
            120, 120, 560, 360
        )

        draw_text(
            "♡ Welcome Player! ♡",
            font_title,
            PINK,
            WIDTH // 2,
            185
        )

        draw_text(
            "What's your name?",
            font_medium,
            DARK,
            WIDTH // 2,
            260
        )

        input_rect = pygame.Rect(
            210, 295, 380, 55
        )

        pygame.draw.rect(
            screen,
            (255, 240, 247),
            input_rect,
            border_radius=15
        )

        pygame.draw.rect(
            screen,
            LAVENDER,
            input_rect,
            3,
            border_radius=15
        )

        shown_name = name if name else "Type your name..."

        draw_text(
            shown_name,
            font_medium,
            DARK if name else (180, 165, 190),
            WIDTH // 2,
            323
        )

        draw_text(
            "Press ENTER to continue ♡",
            font_small,
            SOFT_PURPLE,
            WIDTH // 2,
            395
        )

        pygame.display.flip()

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_RETURN:
                    if name.strip():
                        play_sound("click")
                        return name.strip()

                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]

                elif len(name) < 15:
                    if event.unicode.isprintable():
                        if event.unicode not in "\r\n\t":
                            name += event.unicode

        clock.tick(FPS)

# ==================================================
# CLASS STRIKER
# ==================================================

class Striker:

    def __init__(self, width):
        self.width = width
        self.height = 17

        self.x = WIDTH // 2 - width // 2
        self.y = HEIGHT - 60

        self.speed = 8

        self.rect = pygame.Rect(
            self.x,
            self.y,
            self.width,
            self.height
        )

    def move(self, direction):
        self.x += direction * self.speed

        self.x = max(
            0,
            min(WIDTH - self.width, self.x)
        )

        self.rect.x = self.x

    def draw(self):
        # Paddle shadow
        shadow = self.rect.copy()
        shadow.y += 4

        pygame.draw.rect(
            screen,
            (205, 177, 217),
            shadow,
            border_radius=12
        )

        pygame.draw.rect(
            screen,
            PINK,
            self.rect,
            border_radius=12
        )

        pygame.draw.rect(
            screen,
            WHITE,
            self.rect,
            3,
            border_radius=12
        )

# ==================================================
# CLASS BLOCK
# ==================================================

class Block:

    def __init__(self, x, y, color, health):
        self.rect = pygame.Rect(
            x, y, 70, 27
        )

        self.color = color
        self.health = health

    def draw(self):
        shadow = self.rect.copy()
        shadow.y += 3

        pygame.draw.rect(
            screen,
            (205, 190, 220),
            shadow,
            border_radius=8
        )

        pygame.draw.rect(
            screen,
            self.color,
            self.rect,
            border_radius=8
        )

        pygame.draw.rect(
            screen,
            WHITE,
            self.rect,
            2,
            border_radius=8
        )

        # Small shine
        pygame.draw.circle(
            screen,
            WHITE,
            (self.rect.x + 10, self.rect.y + 7),
            3
        )

# ==================================================
# CLASS BALL
# ==================================================

class Ball:

    def __init__(self, speed):
        self.radius = 10

        self.x = WIDTH // 2
        self.y = HEIGHT // 2

        self.speed_x = speed
        self.speed_y = -speed

        self.rect = pygame.Rect(
            self.x - self.radius,
            self.y - self.radius,
            self.radius * 2,
            self.radius * 2
        )

    def move(self):
        self.x += self.speed_x
        self.y += self.speed_y

        self.rect.center = (
            int(self.x),
            int(self.y)
        )

    def draw(self):
        # Soft glow
        pygame.draw.circle(
            screen,
            (255, 220, 239),
            (int(self.x), int(self.y)),
            15
        )

        pygame.draw.circle(
            screen,
            WHITE,
            (int(self.x), int(self.y)),
            self.radius
        )

        pygame.draw.circle(
            screen,
            PINK,
            (int(self.x - 3), int(self.y - 3)),
            3
        )

# ==================================================
# CREATE BLOCKS
# ==================================================

def populateBlocks(health):
    blocks = []

    for row in range(5):
        for col in range(9):

            x = 35 + col * 81
            y = 100 + row * 39

            color = PASTEL_COLORS[
                row % len(PASTEL_COLORS)
            ]

            blocks.append(
                Block(
                    x,
                    y,
                    color,
                    health
                )
            )

    return blocks

# ==================================================
# COLLISION
# ==================================================

def collisionChecker(ball, striker, blocks):

    # Left and right walls
    if ball.rect.left <= 0:
        ball.speed_x = abs(ball.speed_x)

    if ball.rect.right >= WIDTH:
        ball.speed_x = -abs(ball.speed_x)

    # Top wall
    if ball.rect.top <= 0:
        ball.speed_y = abs(ball.speed_y)

    # Paddle collision
    if ball.rect.colliderect(striker.rect):

        if ball.speed_y > 0:

            ball.speed_y = -abs(ball.speed_y)

            hit_position = (
                ball.rect.centerx - striker.rect.centerx
            ) / (striker.width / 2)

            ball.speed_x = hit_position * 6

            play_sound("paddle")

    # Block collision
    for block in blocks:

        if ball.rect.colliderect(block.rect):

            ball.speed_y *= -1

            block.health -= 1

            play_sound("brick")

            if block.health <= 0:
                blocks.remove(block)

            return 10

    return 0

# ==================================================
# LEADERBOARD SCREEN
# ==================================================

def leaderboard_screen():
    active = True

    while active:
        draw_background()

        draw_panel(
            45, 35, 710, 525
        )

        draw_text(
            "♡ TOP PLAYERS ♡",
            font_title,
            PINK,
            WIDTH // 2,
            90
        )

        headers = [
            ("RANK", 105),
            ("NAME", 245),
            ("SCORE", 390),
            ("MODE", 520),
            ("TIME", 670)
        ]

        for label, x in headers:
            draw_text(
                label,
                font_small,
                SOFT_PURPLE,
                x,
                160
            )

        leaderboard = load_leaderboard()

        if not leaderboard:
            draw_text(
                "No players yet!",
                font_medium,
                DARK,
                WIDTH // 2,
                280
            )

        else:
            for index, player in enumerate(
                leaderboard[:10]
            ):

                y = 200 + index * 31

                color = (
                    (255, 165, 100)
                    if index == 0
                    else DARK
                )

                draw_text(
                    index + 1,
                    font_small,
                    color,
                    105,
                    y
                )

                draw_text(
                    player["name"][:15],
                    font_small,
                    color,
                    245,
                    y
                )

                draw_text(
                    player["score"],
                    font_small,
                    color,
                    390,
                    y
                )

                draw_text(
                    player["difficulty"],
                    font_small,
                    color,
                    520,
                    y
                )

                draw_text(
                    f'{player["time"]:.1f}s',
                    font_small,
                    color,
                    670,
                    y
                )

        draw_text(
            "Press ESC to go back ♡",
            font_small,
            SOFT_PURPLE,
            WIDTH // 2,
            525
        )

        pygame.display.flip()

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_ESCAPE:
                    active = False

        clock.tick(FPS)

# ==================================================
# MAIN MENU
# ==================================================

def main_menu(player_name):

    while True:
        draw_background()

        draw_panel(
            150, 55, 500, 500
        )

        draw_text(
            "♡ BLOCK BREAKER ♡",
            font_title,
            PINK,
            WIDTH // 2,
            120
        )

        draw_text(
            f"Player: {player_name}",
            font_medium,
            DARK,
            WIDTH // 2,
            180
        )

        draw_text(
            "Choose your difficulty!",
            font_small,
            SOFT_PURPLE,
            WIDTH // 2,
            220
        )

        easy_button = draw_button(
            "♡ EASY ♡",
            280, 255, 240, 48,
            MINT
        )

        normal_button = draw_button(
            "♡ NORMAL ♡",
            280, 320, 240, 48,
            BABY_BLUE
        )

        hard_button = draw_button(
            "♡ HARD ♡",
            280, 385, 240, 48,
            BABY_PINK
        )

        leaderboard_button = draw_button(
            "★ LEADERBOARD ★",
            280, 450, 240, 45,
            CREAM
        )

        sound_text = (
            "Sound: ON"
            if audio_enabled
            else "Sound: OFF"
        )

        draw_text(
            sound_text + "  |  Press S to toggle",
            font_tiny,
            SOFT_PURPLE,
            WIDTH // 2,
            525
        )

        pygame.display.flip()

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    raise SystemExit

                if event.key == pygame.K_s:
                    toggle_sound()

            if event.type == pygame.MOUSEBUTTONDOWN:

                if easy_button.collidepoint(event.pos):
                    play_sound("click")
                    return "Easy"

                if normal_button.collidepoint(event.pos):
                    play_sound("click")
                    return "Normal"

                if hard_button.collidepoint(event.pos):
                    play_sound("click")
                    return "Hard"

                if leaderboard_button.collidepoint(event.pos):
                    play_sound("click")
                    leaderboard_screen()

        clock.tick(FPS)

# ==================================================
# PAUSE SCREEN
# ==================================================

def pause_screen():
    paused = True

    if audio_available:
        pygame.mixer.music.pause()

    while paused:
        draw_background()

        draw_panel(
            150, 170, 500, 260
        )

        draw_text(
            "♡ PAUSED ♡",
            font_title,
            PINK,
            WIDTH // 2,
            240
        )

        draw_text(
            "Press ESC to continue",
            font_medium,
            DARK,
            WIDTH // 2,
            320
        )

        draw_text(
            "S = Toggle sound",
            font_small,
            SOFT_PURPLE,
            WIDTH // 2,
            370
        )

        pygame.display.flip()

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_ESCAPE:
                    paused = False

                    if audio_available and audio_enabled:
                        pygame.mixer.music.unpause()

                if event.key == pygame.K_s:
                    toggle_sound()

        clock.tick(FPS)

# ==================================================
# RESULT SCREEN
# ==================================================

def result_screen(
    player_name,
    score,
    difficulty,
    duration,
    won
):
    active = True

    if won:
        title = "♡ YOU WIN! ♡"
        title_color = (110, 190, 145)
        play_sound("win")
    else:
        title = "GAME OVER"
        title_color = (230, 135, 160)
        play_sound("gameover")

    while active:
        draw_background()

        draw_panel(
            100, 65, 600, 475
        )

        draw_text(
            title,
            font_title,
            title_color,
            WIDTH // 2,
            135
        )

        draw_text(
            f"Player: {player_name}",
            font_medium,
            DARK,
            WIDTH // 2,
            220
        )

        draw_text(
            f"Score: {score}",
            font_large,
            SOFT_PURPLE,
            WIDTH // 2,
            275
        )

        draw_text(
            f"Difficulty: {difficulty}",
            font_medium,
            DARK,
            WIDTH // 2,
            330
        )

        if won:
            time_label = "Winning time"
        else:
            time_label = "Playing time"

        draw_text(
            f"{time_label}: {duration:.2f} seconds",
            font_medium,
            DARK,
            WIDTH // 2,
            380
        )

        draw_text(
            "Your result has been saved! ♡",
            font_small,
            SOFT_PURPLE,
            WIDTH // 2,
            425
        )

        draw_text(
            "ENTER = Main Menu",
            font_small,
            DARK,
            WIDTH // 2,
            475
        )

        draw_text(
            "L = Leaderboard",
            font_small,
            DARK,
            WIDTH // 2,
            505
        )

        pygame.display.flip()

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_RETURN:
                    active = False

                elif event.key == pygame.K_l:
                    leaderboard_screen()

        clock.tick(FPS)

# ==================================================
# MAIN GAME
# ==================================================

def main():

    initialize_audio()

    while True:

        player_name = name_input_screen()

        difficulty = main_menu(player_name)

        settings = DIFFICULTIES[difficulty]

        striker = Striker(
            settings["paddle_width"]
        )

        striker.speed = settings["paddle_speed"]

        ball = Ball(
            settings["ball_speed"]
        )

        blocks = populateBlocks(
            settings["block_health"]
        )

        score = 0
        lives = settings["lives"]

        game_running = True
        won = False

        start_time = time.time()

        while game_running:

            clock.tick(FPS)

            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    pygame.quit()
                    raise SystemExit

                if event.type == pygame.KEYDOWN:

                    if event.key == pygame.K_ESCAPE:
                        pause_screen()

                    if event.key == pygame.K_s:
                        toggle_sound()

            # Paddle movement
            keys = pygame.key.get_pressed()

            if (
                keys[pygame.K_LEFT]
                or keys[pygame.K_a]
            ):
                striker.move(-1)

            if (
                keys[pygame.K_RIGHT]
                or keys[pygame.K_d]
            ):
                striker.move(1)

            # Ball movement
            ball.move()

            # Ball falls
            if ball.rect.bottom >= HEIGHT:

                lives -= 1

                play_sound("life")

                if lives <= 0:
                    game_running = False
                    won = False

                else:
                    ball = Ball(
                        settings["ball_speed"]
                    )

            # Collision detection
            score += collisionChecker(
                ball,
                striker,
                blocks
            )

            # Win condition
            if len(blocks) == 0:
                game_running = False
                won = True

            # ======================================
            # DRAW GAME
            # ======================================

            draw_background()

            # Blocks
            for block in blocks:
                block.draw()

            # Paddle and ball
            striker.draw()
            ball.draw()

            # HUD panel
            pygame.draw.rect(
                screen,
                WHITE,
                (10, 10, 250, 80),
                border_radius=15
            )

            pygame.draw.rect(
                screen,
                WHITE,
                (550, 10, 240, 80),
                border_radius=15
            )

            draw_text(
                f"♡ {player_name}",
                font_small,
                DARK,
                25,
                20,
                center=False
            )

            draw_text(
                f"Score: {score}",
                font_small,
                SOFT_PURPLE,
                25,
                45,
                center=False
            )

            draw_text(
                f"Lives: {lives}",
                font_small,
                DARK,
                155,
                45,
                center=False
            )

            draw_text(
                difficulty,
                font_small,
                DARK,
                565,
                20,
                center=False
            )

            elapsed = time.time() - start_time

            draw_text(
                f"Time: {elapsed:.1f}s",
                font_small,
                SOFT_PURPLE,
                565,
                48,
                center=False
            )

            draw_text(
                "ESC = Pause    S = Sound",
                font_small,
                DARK,
                WIDTH // 2,
                HEIGHT - 20
            )

            pygame.display.flip()

        # ======================================
        # SAVE RESULT
        # ======================================

        final_duration = time.time() - start_time

        add_player_result(
            player_name,
            score,
            difficulty,
            final_duration
        )

        # ======================================
        # SHOW RESULT
        # ======================================

        result_screen(
            player_name,
            score,
            difficulty,
            final_duration,
            won
        )

# ==================================================
# RUN PROGRAM
# ==================================================

if __name__ == "__main__":
    main()
