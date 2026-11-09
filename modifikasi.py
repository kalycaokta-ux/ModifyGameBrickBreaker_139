
import pygame
import random
import os
import math

pygame.init()

# ==========================================
# 1. PENGATURAN LAYAR
# ==========================================

WIDTH, HEIGHT = 800, 600
FPS = 60

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Block Breaker - Pastel Edition")

clock = pygame.time.Clock()

# ==========================================
# 2. WARNA PASTEL
# ==========================================

BACKGROUND = (250, 244, 248)
WHITE = (255, 255, 255)
PINK = (255, 183, 197)
PURPLE = (202, 184, 230)
BLUE = (173, 216, 230)
YELLOW = (255, 224, 160)
MINT = (180, 230, 210)
DARK = (91, 79, 105)
GRAY = (180, 170, 190)

PASTEL_COLORS = [
    PINK, PURPLE, BLUE, YELLOW, MINT
]

# ==========================================
# 3. FONT
# ==========================================

font_small = pygame.font.SysFont("arial", 16)
font_medium = pygame.font.SysFont("arial", 24, bold=True)
font_large = pygame.font.SysFont("arial", 45, bold=True)
font_title = pygame.font.SysFont("arial", 58, bold=True)

# ==========================================
# 4. HIGH SCORE
# ==========================================

HIGH_SCORE_FILE = "highscore.txt"


def load_high_score():
    try:
        with open(HIGH_SCORE_FILE, "r") as file:
            return int(file.read())
    except (FileNotFoundError, ValueError):
        return 0


def save_high_score(score):
    high_score = load_high_score()

    if score > high_score:
        with open(HIGH_SCORE_FILE, "w") as file:
            file.write(str(score))


# ==========================================
# 5. FUNGSI TEKS
# ==========================================

def draw_text(text, font, color, x, y, center=True):
    text_surface = font.render(str(text), True, color)
    text_rect = text_surface.get_rect()

    if center:
        text_rect.center = (x, y)
    else:
        text_rect.topleft = (x, y)

    screen.blit(text_surface, text_rect)


# ==========================================
# 6. FUNGSI TOMBOL
# ==========================================

def draw_button(text, rect, color):
    mouse_pos = pygame.mouse.get_pos()

    button_color = color

    if rect.collidepoint(mouse_pos):
        button_color = tuple(
            min(255, c + 15) for c in color
        )

    pygame.draw.rect(
        screen, button_color, rect, border_radius=15
    )

    pygame.draw.rect(
        screen, WHITE, rect, 2, border_radius=15
    )

    draw_text(
        text, font_medium, DARK,
        rect.centerx, rect.centery
    )


# ==========================================
# 7. STRIKER / PADDLE CLASS
# ==========================================

class Striker:

    def __init__(self, width, speed):

        self.width = width
        self.height = 16
        self.speed = speed

        self.posx = (WIDTH - width) // 2
        self.posy = HEIGHT - 55

        self.rect = pygame.Rect(
            self.posx, self.posy,
            self.width, self.height
        )

        self.color = PURPLE

    def update(self, direction):

        self.posx += self.speed * direction

        self.posx = max(
            0, min(WIDTH - self.width, self.posx)
        )

        self.rect.x = self.posx

    def display(self):

        pygame.draw.rect(
            screen,
            self.color,
            self.rect,
            border_radius=10
        )

        pygame.draw.rect(
            screen,
            WHITE,
            self.rect,
            2,
            border_radius=10
        )

    def getRect(self):
        return self.rect


# ==========================================
# 8. BLOCK CLASS
# ==========================================

class Block:

    def __init__(self, x, y, width, height, color, health):

        self.rect = pygame.Rect(
            x, y, width, height
        )

        self.color = color
        self.health = health
        self.max_health = health

    def display(self):

        if self.health > 0:

            pygame.draw.rect(
                screen,
                self.color,
                self.rect,
                border_radius=6
            )

            pygame.draw.rect(
                screen,
                WHITE,
                self.rect,
                2,
                border_radius=6
            )

            if self.max_health > 1:

                bar_width = self.rect.width - 12

                pygame.draw.rect(
                    screen,
                    DARK,
                    (self.rect.x + 6,
                     self.rect.y + self.rect.height - 5,
                     bar_width, 3),
                    border_radius=2
                )

                pygame.draw.rect(
                    screen,
                    WHITE,
                    (self.rect.x + 6,
                     self.rect.y + self.rect.height - 5,
                     bar_width * self.health / self.max_health,
                     3),
                    border_radius=2
                )

    def hit(self):
        self.health -= 1

    def getRect(self):
        return self.rect


# ==========================================
# 9. BALL CLASS
# ==========================================

class Ball:

    def __init__(self, speed):

        self.radius = 9
        self.speed = speed

        self.posx = WIDTH // 2
        self.posy = HEIGHT - 100

        self.xFac = random.choice([-1, 1])
        self.yFac = -1

        self.color = PINK

        self.rect = pygame.Rect(
            self.posx - self.radius,
            self.posy - self.radius,
            self.radius * 2,
            self.radius * 2
        )

    def update(self):

        self.posx += self.xFac * self.speed
        self.posy += self.yFac * self.speed

        if self.posx - self.radius <= 0:
            self.posx = self.radius
            self.xFac = abs(self.xFac)

        elif self.posx + self.radius >= WIDTH:
            self.posx = WIDTH - self.radius
            self.xFac = -abs(self.xFac)

        if self.posy - self.radius <= 0:
            self.posy = self.radius
            self.yFac = abs(self.yFac)

        self.rect.center = (
            int(self.posx), int(self.posy)
        )

        if self.posy - self.radius > HEIGHT:
            return True

        return False

    def hit_paddle(self, paddle):

        if self.rect.colliderect(paddle.getRect()) and self.yFac > 0:

            offset = (
                self.posx - paddle.rect.centerx
            ) / (paddle.width / 2)

            offset = max(-0.85, min(0.85, offset))

            angle = offset * math.radians(60)

            self.xFac = math.sin(angle)
            self.yFac = -math.cos(angle)

            self.posy = paddle.rect.top - self.radius

            return True

        return False

    def hit_block(self, block):

        if self.rect.colliderect(block.getRect()):

            overlap_left = self.rect.right - block.rect.left
            overlap_right = block.rect.right - self.rect.left
            overlap_top = self.rect.bottom - block.rect.top
            overlap_bottom = block.rect.bottom - self.rect.top

            min_overlap = min(
                overlap_left,
                overlap_right,
                overlap_top,
                overlap_bottom
            )

            if min_overlap in (overlap_left, overlap_right):
                self.xFac *= -1
            else:
                self.yFac *= -1

            block.hit()

            return True

        return False

    def display(self):

        pygame.draw.circle(
            screen,
            self.color,
            (int(self.posx), int(self.posy)),
            self.radius
        )

    def reset(self):

        self.posx = WIDTH // 2
        self.posy = HEIGHT - 100

        self.xFac = random.choice([-1, 1])
        self.yFac = -1

        self.rect.center = (
            int(self.posx), int(self.posy)
        )

    def getRect(self):
        return self.rect


# ==========================================
# 10. PENGATURAN DIFFICULTY
# ==========================================

DIFFICULTY = {

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


# ==========================================
# 11. MEMBUAT BALOK
# ==========================================

def populate_blocks(difficulty):

    blocks = []

    block_width = 65
    block_height = 22

    horizontal_gap = 12
    vertical_gap = 12

    columns = 9
    rows = 5

    total_width = (
        columns * block_width
        + (columns - 1) * horizontal_gap
    )

    start_x = (WIDTH - total_width) // 2

    for row in range(rows):

        for col in range(columns):

            x = start_x + col * (
                block_width + horizontal_gap
            )

            y = 75 + row * (
                block_height + vertical_gap
            )

            color = PASTEL_COLORS[
                row % len(PASTEL_COLORS)
            ]

            health = difficulty["block_health"]

            blocks.append(
                Block(
                    x, y,
                    block_width,
                    block_height,
                    color,
                    health
                )
            )

    return blocks


# ==========================================
# 12. BACKGROUND
# ==========================================

def draw_background():

    screen.fill(BACKGROUND)

    pygame.draw.circle(
        screen, (255, 226, 235),
        (40, 50), 25
    )

    pygame.draw.circle(
        screen, (226, 218, 250),
        (750, 100), 35
    )

    pygame.draw.circle(
        screen, (218, 242, 232),
        (750, 550), 25
    )


# ==========================================
# 13. HUD / INFORMASI GAME
# ==========================================

def draw_hud(score, lives, difficulty):

    pygame.draw.rect(
        screen,
        WHITE,
        (0, 0, WIDTH, 45)
    )

    draw_text(
        f"Score: {score}",
        font_medium, DARK, 20, 22, False
    )

    draw_text(
        f"Lives: {lives}",
        font_medium, DARK, 300, 22
    )

    draw_text(
        f"Mode: {difficulty}",
        font_medium, DARK, 700, 22
    )


# ==========================================
# 14. MEMULAI PERMAINAN
# ==========================================

def start_game(mode):

    settings = DIFFICULTY[mode]

    striker = Striker(
        settings["paddle_width"],
        settings["paddle_speed"]
    )

    ball = Ball(settings["ball_speed"])

    blocks = populate_blocks(settings)

    return {
        "striker": striker,
        "ball": ball,
        "blocks": blocks,
        "score": 0,
        "lives": settings["lives"],
        "mode": mode
    }


# ==========================================
# 15. GAME MANAGER
# ==========================================

def main():

    running = True

    game_state = "menu"

    game = None

    high_score = load_high_score()

    easy_button = pygame.Rect(250, 260, 300, 55)
    normal_button = pygame.Rect(250, 330, 300, 55)
    hard_button = pygame.Rect(250, 400, 300, 55)

    restart_button = pygame.Rect(250, 350, 300, 55)
    menu_button = pygame.Rect(250, 420, 300, 55)

    while running:

        clock.tick(FPS)

        mouse_clicked = False

        # EVENT HANDLING

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_clicked = True

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_ESCAPE:

                    if game_state == "playing":
                        game_state = "paused"

                    elif game_state == "paused":
                        game_state = "playing"

                if event.key == pygame.K_r:

                    if game_state in ("gameover", "win"):
                        game = start_game(game["mode"])
                        game_state = "playing"

                if event.key == pygame.K_m:

                    if game_state in ("gameover", "win", "paused"):
                        game_state = "menu"

        # MAIN MENU

        if game_state == "menu":

            draw_background()

            draw_text(
                "BLOCK BREAKER",
                font_title, DARK,
                WIDTH // 2, 120
            )

            draw_text(
                "PASTEL EDITION",
                font_medium, PURPLE,
                WIDTH // 2, 180
            )

            draw_text(
                "Choose Your Difficulty",
                font_medium, DARK,
                WIDTH // 2, 225
            )

            draw_button(
                "EASY",
                easy_button,
                MINT
            )

            draw_button(
                "NORMAL",
                normal_button,
                YELLOW
            )

            draw_button(
                "HARD",
                hard_button,
                PINK
            )

            draw_text(
                f"High Score: {high_score}",
                font_small, DARK,
                WIDTH // 2, 510
            )

            draw_text(
                "Use LEFT / RIGHT arrows to move",
                font_small, GRAY,
                WIDTH // 2, 550
            )

            if mouse_clicked:

                if easy_button.collidepoint(
                    pygame.mouse.get_pos()
                ):

                    game = start_game("Easy")
                    game_state = "playing"

                elif normal_button.collidepoint(
                    pygame.mouse.get_pos()
                ):

                    game = start_game("Normal")
                    game_state = "playing"

                elif hard_button.collidepoint(
                    pygame.mouse.get_pos()
                ):

                    game = start_game("Hard")
                    game_state = "playing"

        # GAME PLAYING

        elif game_state == "playing":

            draw_background()

            striker = game["striker"]
            ball = game["ball"]
            blocks = game["blocks"]

            keys = pygame.key.get_pressed()

            direction = 0

            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                direction = -1

            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                direction = 1

            striker.update(direction)

            life_lost = ball.update()

            ball.hit_paddle(striker)

            for block in blocks[:]:

                if ball.hit_block(block):

                    if block.health <= 0:

                        blocks.remove(block)
                        game["score"] += 10

                    break

            if life_lost:

                game["lives"] -= 1
                ball.reset()

                if game["lives"] <= 0:

                    save_high_score(game["score"])
                    high_score = load_high_score()

                    game_state = "gameover"

            if not blocks:

                save_high_score(game["score"])
                high_score = load_high_score()

                game_state = "win"

            draw_hud(
                game["score"],
                game["lives"],
                game["mode"]
            )

            for block in blocks:
                block.display()

            striker.display()
            ball.display()

            draw_text(
                "ESC = Pause",
                font_small, DARK,
                WIDTH // 2, HEIGHT - 15
            )

        # PAUSE MENU

        elif game_state == "paused":

            draw_background()

            draw_text(
                "GAME PAUSED",
                font_title, DARK,
                WIDTH // 2, 230
            )

            draw_text(
                "Press ESC to Continue",
                font_medium, PURPLE,
                WIDTH // 2, 310
            )

            draw_text(
                "Press M to Main Menu",
                font_small, DARK,
                WIDTH // 2, 360
            )

        # GAME OVER

        elif game_state == "gameover":

            draw_background()

            draw_text(
                "GAME OVER!",
                font_title, PINK,
                WIDTH // 2, 180
            )

            draw_text(
                f"Your Score: {game['score']}",
                font_large, DARK,
                WIDTH // 2, 260
            )

            draw_text(
                f"High Score: {high_score}",
                font_medium, PURPLE,
                WIDTH // 2, 305
            )

            draw_button(
                "PLAY AGAIN",
                restart_button,
                MINT
            )

            draw_button(
                "MAIN MENU",
                menu_button,
                YELLOW
            )

            if mouse_clicked:

                if restart_button.collidepoint(
                    pygame.mouse.get_pos()
                ):

                    game = start_game(game["mode"])
                    game_state = "playing"

                elif menu_button.collidepoint(
                    pygame.mouse.get_pos()
                ):

                    game_state = "menu"

            draw_text(
                "Press R to Restart | M for Menu",
                font_small, GRAY,
                WIDTH // 2, 510
            )

        # YOU WIN

        elif game_state == "win":

            draw_background()

            draw_text(
                "YOU WIN!",
                font_title, MINT,
                WIDTH // 2, 180
            )

            draw_text(
                "Congratulations!",
                font_medium, PURPLE,
                WIDTH // 2, 235
            )

            draw_text(
                f"Your Score: {game['score']}",
                font_large, DARK,
                WIDTH // 2, 290
            )

            draw_button(
                "PLAY AGAIN",
                restart_button,
                MINT
            )

            draw_button(
                "MAIN MENU",
                menu_button,
                YELLOW
            )

            if mouse_clicked:

                if restart_button.collidepoint(
                    pygame.mouse.get_pos()
                ):

                    game = start_game(game["mode"])
                    game_state = "playing"

                elif menu_button.collidepoint(
                    pygame.mouse.get_pos()
                ):

                    game_state = "menu"

            draw_text(
                "Press R to Play Again | M for Menu",
                font_small, GRAY,
                WIDTH // 2, 510
            )

        # UPDATE DISPLAY

        pygame.display.flip()

    pygame.quit()


# ==========================================
# 16. MENJALANKAN PROGRAM
# ==========================================

if __name__ == "__main__":
    main()
