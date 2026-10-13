
import math
import random
import pygame

pygame.init()

WIDTH, HEIGHT = 1200, 760
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("BLACK HOLE SIMULATOR | NEBULA X")
clock = pygame.time.Clock()

FONT = pygame.font.SysFont("consolas", 17)
SMALL = pygame.font.SysFont("consolas", 13)
TITLE = pygame.font.SysFont("consolas", 27, bold=True)

BLACK = (3, 5, 15)
CYAN = (50, 220, 255)
PURPLE = (160, 70, 255)
WHITE = (235, 245, 255)

cx, cy = WIDTH // 2, HEIGHT // 2
mouse_gravity = 1.0
paused = False
show_trails = True
particles = []
stars = []

for _ in range(250):
    stars.append((
        random.randrange(WIDTH),
        random.randrange(HEIGHT),
        random.choice([1, 1, 1, 2]),
        random.uniform(0.3, 1.0)
    ))


class Particle:
    def __init__(self):
        self.reset()

    def reset(self):
        self.angle = random.uniform(0, math.tau)
        self.radius = random.uniform(100, 410)
        self.speed = random.uniform(0.003, 0.012)
        self.size = random.choice([1, 1, 2, 2, 3])
        self.color = random.choice([
            (40, 190, 255),
            (110, 90, 255),
            (220, 70, 255),
            (255, 160, 240),
            (255, 220, 245)
        ])

    def update(self):
        self.angle += self.speed * (440 / max(self.radius, 25))
        self.radius -= 0.18 + 0.6 * mouse_gravity

        if self.radius < 28:
            self.reset()

    def position(self):
        x = cx + math.cos(self.angle) * self.radius
        y = cy + math.sin(self.angle) * self.radius * 0.42
        return int(x), int(y)


particles = [Particle() for _ in range(800)]


def draw_background():
    screen.fill(BLACK)

    for x, y, size, brightness in stars:
        value = int(100 * brightness * random.uniform(0.65, 1.0))
        pygame.draw.circle(
            screen,
            (value, value, min(255, value + 35)),
            (x, y),
            size
        )

    for i in range(5):
        rect = pygame.Rect(
            22 + i * 9,
            22 + i * 9,
            WIDTH - 44 - i * 18,
            HEIGHT - 44 - i * 18
        )
        pygame.draw.rect(screen, (15, 35, 60), rect, 1)


def glow(surface, pos, color, radius):
    x, y = pos

    for r, alpha in [
        (radius * 4, 12),
        (radius * 2.5, 22),
        (radius * 1.5, 45)
    ]:
        r = max(1, int(r))
        layer = pygame.Surface(
            (r * 2 + 2, r * 2 + 2),
            pygame.SRCALPHA
        )

        pygame.draw.circle(
            layer,
            (*color, alpha),
            (r + 1, r + 1),
            r
        )

        surface.blit(layer, (int(x - r), int(y - r)))


def draw_black_hole():
    # Gravitational lensing rings
    for radius, color in [
        (104, (35, 95, 180)),
        (91, (85, 50, 190)),
        (77, (40, 175, 255))
    ]:
        pygame.draw.circle(
            screen, color, (cx, cy), radius, 2
        )

    # Accretion disk
    for i in range(42):
        radius = 55 + i * 2.25
        color = (
            min(255, 20 + i * 2),
            min(255, 65 + i * 2),
            min(255, 130 + i * 3)
        )

        rect = pygame.Rect(
            cx - radius,
            cy - radius * 0.32,
            radius * 2,
            radius * 0.64
        )

        pygame.draw.ellipse(screen, color, rect, 2)

    # Purple light arcs
    for i in range(14):
        radius = 65 + i * 2

        rect = pygame.Rect(
            cx - radius,
            cy - radius * 0.36,
            radius * 2,
            radius * 0.72
        )

        pygame.draw.arc(
            screen,
            (100 + i * 5, 40, 255),
            rect,
            math.pi,
            math.tau,
            2
        )

    # Event horizon
    glow(screen, (cx, cy), (30, 130, 255), 52)

    pygame.draw.circle(screen, (1, 2, 8), (cx, cy), 47)
    pygame.draw.circle(screen, (10, 14, 35), (cx, cy), 43, 2)


def draw_particles():
    for p in particles:
        x, y = p.position()

        if 0 <= x < WIDTH and 0 <= y < HEIGHT:
            pygame.draw.circle(
                screen, p.color, (x, y), p.size
            )

            if p.size >= 2:
                glow(screen, (x, y), p.color, p.size)


def draw_hud():
    pygame.draw.rect(screen, (5, 10, 25), (35, 35, 350, 175))
    pygame.draw.rect(screen, (30, 100, 155), (35, 35, 350, 175), 1)

    # FIX: render the font before blitting it
    title_surface = TITLE.render(
        "BLACK HOLE SIMULATOR", True, CYAN
    )
    screen.blit(title_surface, (48, 48))

    subtitle = SMALL.render(
        "GRAVITATIONAL FIELD MONITOR", True, PURPLE
    )
    screen.blit(subtitle, (50, 84))

    lines = [
        f"PARTICLES : {len(particles)}",
        f"GRAVITY   : {mouse_gravity:.1f}x",
        "CORE      : ACTIVE",
        f"STATUS    : {'PAUSED' if paused else 'SIMULATING'}"
    ]

    for i, line in enumerate(lines):
        color = CYAN if i == 1 else WHITE
        text_surface = FONT.render(line, True, color)
        screen.blit(text_surface, (50, 110 + i * 21))

    panel = pygame.Rect(35, HEIGHT - 160, 340, 126)
    pygame.draw.rect(screen, (5, 10, 25), panel)
    pygame.draw.rect(screen, (30, 100, 155), panel, 1)

    help_text = [
        "MOUSE   - Move black hole",
        "UP/DOWN - Adjust gravity",
        "SPACE   - Pause / Resume",
        "T       - Toggle trails",
        "R       - Reset particles",
        "ESC     - Exit"
    ]

    for i, line in enumerate(help_text):
        text_surface = SMALL.render(line, True, (120, 190, 220))
        screen.blit(text_surface, (49, HEIGHT - 148 + i * 19))

    footer = SMALL.render(
        "NEBULA X / BLACK HOLE LAB", True, PURPLE
    )
    screen.blit(footer, (WIDTH - 280, HEIGHT - 29))


running = True

while running:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

            elif event.key == pygame.K_SPACE:
                paused = not paused

            elif event.key == pygame.K_UP:
                mouse_gravity = min(3.0, mouse_gravity + 0.2)

            elif event.key == pygame.K_DOWN:
                mouse_gravity = max(0.2, mouse_gravity - 0.2)

            elif event.key == pygame.K_t:
                show_trails = not show_trails

            elif event.key == pygame.K_r:
                particles = [Particle() for _ in range(800)]

    # Smoothly move the black hole toward the mouse
    mx, my = pygame.mouse.get_pos()
    cx += int((mx - cx) * 0.018)
    cy += int((my - cy) * 0.018)

    if not paused:
        for p in particles:
            p.update()

    draw_background()

    if show_trails:
        # Subtle transparent overlay for particle trails
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((3, 5, 15, 35))
        screen.blit(overlay, (0, 0))

    draw_particles()
    draw_black_hole()
    draw_hud()

    pygame.display.flip()

pygame.quit()