import pygame
from .player import Player
from .platform import Platform
from .hazard import Hazard
from .sounds import SoundManager

# Game Engine

WHITE = (255, 255, 255)
BROWN = (150, 100, 60)
RED = (220, 60, 60)
GREEN = (0, 200, 0)
YELLOW = (255, 220, 80)

JUMP_KEYS = (pygame.K_SPACE, pygame.K_UP, pygame.K_w)

# Terminal velocity (px/frame). Capping the fall speed keeps single-frame
# movement bounded; the swept landing check below is what guarantees that
# no platform can be skipped, whatever the speed.
MAX_FALL_SPEED = 18

# Difficulty presets: gravity (px/frame^2) and jump strength (initial vy).
# Hard is "heavier but snappier": stronger gravity with a stronger jump so
# the level (hazard gap) is still beatable on every difficulty.
DIFFICULTIES = {
    "Easy":   {"gravity": 0.50, "jump": -12},
    "Medium": {"gravity": 0.60, "jump": -12},
    "Hard":   {"gravity": 0.70, "jump": -13},
}
# Key -> difficulty, used on the Game Over screen
DIFFICULTY_KEYS = {
    pygame.K_1: "Easy", pygame.K_KP1: "Easy",
    pygame.K_2: "Medium", pygame.K_KP2: "Medium",
    pygame.K_3: "Hard", pygame.K_KP3: "Hard",
}
# Letter shortcuts and character fallback (works on any keyboard layout)
DIFFICULTY_KEYS.update({pygame.K_e: "Easy", pygame.K_m: "Medium", pygame.K_h: "Hard"})
DIFFICULTY_CHARS = {"1": "Easy", "2": "Medium", "3": "Hard"}
REPLAY_KEYS = (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_r)   # same difficulty
EXIT_KEYS = (pygame.K_ESCAPE, pygame.K_q)


class GameEngine:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.start_x, self.start_y = 40, height - 120

        # A simple hand-built level: platforms with gaps between them
        # (falling into a gap means falling off the bottom of the
        # screen), one hazard, and a goal near the right edge.
        ground_y = height - 40
        self.platforms = [
            Platform(0, ground_y, 160),
            Platform(220, ground_y, 200),
            Platform(420, ground_y - 60, 120),
            Platform(600, ground_y, 180),
        ]
        # Second platform widened (140 -> 200) and the hazard shrunk (100 -> 40px)
        # so a normal jump clears it; the original layout was nearly unbeatable.
        self.hazards = [Hazard(290, ground_y - 14, 40)]
        self.goal_x = 740

        self.font = pygame.font.SysFont("Arial", 30)
        self.small_font = pygame.font.SysFont("Arial", 22)
        self.title_font = pygame.font.SysFont("Arial", 72, bold=True)

        # Clickable buttons on the Game Over screen: (rect, action, label)
        cy = height // 2
        self.buttons = []
        for i, name in enumerate(("Easy", "Medium", "Hard")):
            rect = pygame.Rect(0, 0, 150, 46)
            rect.center = (width // 2 + (i - 1) * 170, cy + 55)
            self.buttons.append((rect, name, f"[{i + 1}] {name}"))
        exit_rect = pygame.Rect(0, 0, 150, 40)
        exit_rect.center = (width // 2, cy + 120)
        self.buttons.append((exit_rect, "exit", "[Esc] Exit"))

        self.sounds = SoundManager()
        self.should_quit = False      # main loop exits when this is True
        self.difficulty = "Medium"
        self.start_game(self.difficulty)

    # ------------------------------------------------------------------
    # Game lifecycle
    # ------------------------------------------------------------------
    def start_game(self, difficulty):
        """(Re)start a run with the chosen difficulty."""
        settings = DIFFICULTIES[difficulty]
        self.difficulty = difficulty
        self.gravity = settings["gravity"]

        self.player = Player(self.start_x, self.start_y)
        self.player.jump_strength = settings["jump"]

        self.score = 0
        self.game_over = False

    def end_game(self):
        if not self.game_over:
            self.game_over = True
            self.player.vx = 0
            self.sounds.play("die")

    # ------------------------------------------------------------------
    # Input
    # ------------------------------------------------------------------
    def _game_over_action(self, action):
        if action == "exit":
            self.should_quit = True
        else:
            self.start_game(action)

    def handle_event(self, event):
        if self.game_over:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for rect, action, _label in self.buttons:
                    if rect.collidepoint(event.pos):
                        self._game_over_action(action)
                        return
            elif event.type == pygame.KEYDOWN:
                if event.key in EXIT_KEYS:
                    self._game_over_action("exit")
                elif event.key in REPLAY_KEYS:
                    self.start_game(self.difficulty)
                elif event.key in DIFFICULTY_KEYS:
                    self.start_game(DIFFICULTY_KEYS[event.key])
                elif event.unicode in DIFFICULTY_CHARS:
                    self.start_game(DIFFICULTY_CHARS[event.unicode])
            return

        if event.type == pygame.KEYDOWN and event.key in JUMP_KEYS:
            if self.player.jump():
                self.sounds.play("jump")

    def handle_input(self):
        if self.game_over:
            return
        keys = pygame.key.get_pressed()
        self.player.vx = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.player.vx = -self.player.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.player.vx = self.player.speed

    # ------------------------------------------------------------------
    # Physics
    # ------------------------------------------------------------------
    def _land_on_platforms(self, prev_bottom):
        """Swept (continuous) landing check.

        A platform counts as landed on if the player's feet were at or
        above its top surface last frame and are at or below it now, while
        overlapping it horizontally. Because it compares *where the feet
        were* with *where they are*, a fast fall can no longer skip a thin
        platform, and touching a platform from the side or from below no
        longer snaps the player on top of it.
        """
        p = self.player
        if p.vy < 0:                       # moving up: pass through (one-way)
            return
        new_bottom = p.y + p.height

        landing = None
        for platform in self.platforms:
            overlaps_x = (p.x < platform.x + platform.width
                          and p.x + p.width > platform.x)
            crossed_top = prev_bottom <= platform.y <= new_bottom
            if overlaps_x and crossed_top:
                # If several are crossed in one frame, take the highest one
                if landing is None or platform.y < landing.y:
                    landing = platform

        if landing is not None:
            p.y = landing.y - p.height
            p.vy = 0
            p.on_ground = True

    def update(self):
        if self.game_over:
            return

        p = self.player
        p.vy = min(p.vy + self.gravity, MAX_FALL_SPEED)
        p.x = max(0, p.x + p.vx)

        prev_bottom = p.y + p.height
        p.y += p.vy
        p.on_ground = False
        self._land_on_platforms(prev_bottom)

        for hazard in self.hazards:
            if p.rect().colliderect(hazard.rect()):
                self.end_game()
                return

        if p.y > self.height:               # fell off the bottom
            self.end_game()
            return

        if p.x >= self.goal_x:              # reached the goal
            self.score += 1
            self.sounds.play("goal")
            p.x, p.y = self.start_x, self.start_y
            p.vy = 0

    # ------------------------------------------------------------------
    # Rendering
    # ------------------------------------------------------------------
    def _draw_centered(self, screen, font, text, color, y):
        surf = font.render(text, True, color)
        screen.blit(surf, surf.get_rect(center=(self.width // 2, y)))

    def _render_game_over(self, screen):
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 170))
        screen.blit(overlay, (0, 0))

        cy = self.height // 2
        self._draw_centered(screen, self.title_font, "GAME OVER", RED, cy - 120)
        self._draw_centered(screen, self.font, f"Final Score: {self.score}", WHITE, cy - 50)
        self._draw_centered(screen, self.small_font,
                            "Click a difficulty or press 1 / 2 / 3  (Enter = same again)", WHITE, cy + 5)
        mouse = pygame.mouse.get_pos()
        for rect, action, label in self.buttons:
            hover = rect.collidepoint(mouse)
            pygame.draw.rect(screen, (90, 90, 120) if hover else (50, 50, 80), rect, border_radius=8)
            pygame.draw.rect(screen, YELLOW if action != "exit" else WHITE, rect, 2, border_radius=8)
            text = self.small_font.render(label, True, YELLOW if action != "exit" else WHITE)
            screen.blit(text, text.get_rect(center=rect.center))

    def render(self, screen):
        for platform in self.platforms:
            pygame.draw.rect(screen, BROWN, platform.rect())
        for hazard in self.hazards:
            pygame.draw.rect(screen, RED, hazard.rect())

        goal_rect = pygame.Rect(self.goal_x, 0, 6, self.height)
        pygame.draw.rect(screen, GREEN, goal_rect)

        pygame.draw.rect(screen, WHITE, self.player.rect())

        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        screen.blit(score_text, (10, 10))
        diff_text = self.small_font.render(f"Difficulty: {self.difficulty}", True, WHITE)
        screen.blit(diff_text, (self.width - diff_text.get_width() - 20, 14))

        if self.game_over:
            self._render_game_over(screen)