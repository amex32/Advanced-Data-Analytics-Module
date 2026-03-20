import pygame
import math
import random

pygame.init()

# Screen
WIDTH, HEIGHT = 1000, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Advanced Car Racing")

clock = pygame.time.Clock()

# Colors
WHITE = (255, 255, 255)
GREEN = (34, 177, 76)
GRAY = (100, 100, 100)
RED = (200, 0, 0)
BLUE = (0, 0, 255)

# Track
track_rect = pygame.Rect(100, 100, 800, 500)

# Car class
class Car:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.angle = 0
        self.speed = 0
        self.max_speed = 6
        self.acceleration = 0.2
        self.rotation_speed = 4
        self.friction = 0.05
        self.color = color
        self.width = 40
        self.height = 20

    def move(self, forward=True):
        if forward:
            self.speed += self.acceleration
        else:
            self.speed -= self.acceleration

        self.speed = max(-self.max_speed/2, min(self.speed, self.max_speed))

    def rotate(self, left=True):
        if left:
            self.angle += self.rotation_speed
        else:
            self.angle -= self.rotation_speed

    def update(self):
        rad = math.radians(self.angle)
        dx = math.cos(rad) * self.speed
        dy = -math.sin(rad) * self.speed

        self.x += dx
        self.y += dy

        # friction
        if self.speed > 0:
            self.speed -= self.friction
        elif self.speed < 0:
            self.speed += self.friction

        # keep inside track
        if not track_rect.collidepoint(self.x, self.y):
            self.speed *= -0.5  # bounce effect

    def draw(self, surface):
        rect = pygame.Surface((self.width, self.height))
        rect.fill(self.color)
        rotated = pygame.transform.rotate(rect, self.angle)
        surface.blit(rotated, (self.x - rotated.get_width() // 2,
                               self.y - rotated.get_height() // 2))


# AI Car
class AICar(Car):
    def __init__(self, x, y, color):
        super().__init__(x, y, color)
        self.target = (random.randint(200, 800), random.randint(200, 600))

    def update_ai(self):
        tx, ty = self.target
        angle_to_target = math.degrees(math.atan2(-(ty - self.y), (tx - self.x)))

        if self.angle < angle_to_target:
            self.angle += self.rotation_speed
        else:
            self.angle -= self.rotation_speed

        self.move(True)

        if math.hypot(self.x - tx, self.y - ty) < 50:
            self.target = (random.randint(200, 800), random.randint(200, 600))


# Player
player = Car(200, 200, BLUE)

# AI opponents
ai_cars = [AICar(random.randint(300, 700), random.randint(300, 500), RED) for _ in range(3)]

# Game loop
running = True
while running:
    clock.tick(60)
    screen.fill(GREEN)

    # Draw track
    pygame.draw.rect(screen, GRAY, track_rect)

    keys = pygame.key.get_pressed()

    # Controls
    if keys[pygame.K_UP]:
        player.move(True)
    if keys[pygame.K_DOWN]:
        player.move(False)
    if keys[pygame.K_LEFT]:
        player.rotate(True)
    if keys[pygame.K_RIGHT]:
        player.rotate(False)

    # Update player
    player.update()

    # Update AI
    for ai in ai_cars:
        ai.update_ai()
        ai.update()

    # Draw cars
    player.draw(screen)
    for ai in ai_cars:
        ai.draw(screen)

    # Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    pygame.display.update()

pygame.quit()