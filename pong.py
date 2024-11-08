import pygame
import random
import math
import time

# Initialize Pygame
pygame.init()

# Define constants
WIDTH, HEIGHT = 800, 600
FPS = 60
BALL_RADIUS = 15
PADDLE_HEIGHT = 20
PADDLE_WIDTH = 100
PADDLE_COLOR = (255, 0, 255)  # Neon Purple
BACKGROUND_COLOR = (0, 0, 0)  # Black

# Define colors
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# Set up the screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pong Game")

# Load background image
background_image = pygame.image.load("background.jpg")  # Use your own background image file
background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))

# PowerUp and Downgrade classes
class PowerUp:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.active = True

    def draw(self):
        if self.active:
            pygame.draw.circle(screen, GREEN, (self.x, self.y), 10)

    def collect(self):
        self.active = False
        return 30  # Increase paddle width

class Downgrade:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.active = True

    def draw(self):
        if self.active:
            pygame.draw.circle(screen, RED, (self.x, self.y), 10)

    def collect(self):
        self.active = False
        return -30  # Decrease paddle width

# Ball class with angle-based movement
class Ball:
    def __init__(self, x, y, radius, speed):
        self.x = x
        self.y = y
        self.radius = radius
        self.speed = speed
        self.angle = random.uniform(0.3, 0.8)  # Random angle between 15 and 75 degrees
        self.velocity_x = math.cos(self.angle) * self.speed
        self.velocity_y = math.sin(self.angle) * self.speed

    def move(self):
        self.x += self.velocity_x
        self.y += self.velocity_y

    def draw(self):
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), self.radius)

    def bounce(self, normal_angle):
        """Bounce the ball based on the collision angle"""
        angle_diff = normal_angle - self.angle
        self.angle = normal_angle + angle_diff
        self.velocity_x = math.cos(self.angle) * self.speed
        self.velocity_y = math.sin(self.angle) * self.speed

    def check_collision_with_paddle(self, paddle_rect):
        """Check if the ball collides with the paddle"""
        if paddle_rect.colliderect(
                pygame.Rect(self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2)):
            ball_center_y = self.y
            paddle_center_y = paddle_rect.centery
            angle = (ball_center_y - paddle_center_y) / (paddle_rect.height / 2)
            return angle
        return None

    def check_collision_with_item(self, item_x, item_y, item_radius):
        """Check for collision with power-ups or downgrades (circles)"""
        distance = math.sqrt((self.x - item_x) ** 2 + (self.y - item_y) ** 2)
        return distance < self.radius + item_radius

def reset_game():
    global score, level, lives, paddle_width, ball, power_ups, downgrades
    score = 0
    level = 1
    lives = 3
    paddle_width = PADDLE_WIDTH
    ball = Ball(WIDTH // 2, HEIGHT // 2, BALL_RADIUS, 5)
    power_ups = []
    downgrades = []

# Initialize game variables
clock = pygame.time.Clock()
score = 0
level = 1
lives = 3

# Create ball, paddle, power-ups, and downgrades
ball = Ball(WIDTH // 2, HEIGHT // 2, BALL_RADIUS, 5)
paddle_x = WIDTH // 2 - PADDLE_WIDTH // 2
paddle_y = HEIGHT - PADDLE_HEIGHT - 10
paddle_width = PADDLE_WIDTH
paddle_height = PADDLE_HEIGHT
paddle_color = PADDLE_COLOR

power_ups = []
downgrades = []

# Game loop
running = True
game_over = False

while running:
    screen.fill(BACKGROUND_COLOR)
    screen.blit(background_image, (0, 0))  # Draw the background image

    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if game_over:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:  # Restart
                    game_over = False
                    reset_game()
                elif event.key == pygame.K_q:  # Quit
                    running = False

    if not game_over:
        # Paddle movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and paddle_x > 0:
            paddle_x -= 10
        if keys[pygame.K_RIGHT] and paddle_x < WIDTH - paddle_width:
            paddle_x += 10

        # Power-ups and downgrades logic
        if random.randint(1, 100) <= 2 and len(power_ups) == 0:
            power_ups.append(PowerUp(random.randint(50, WIDTH - 50), random.randint(50, HEIGHT // 2)))
        if random.randint(1, 100) <= 2 and len(downgrades) == 0:
            downgrades.append(Downgrade(random.randint(50, WIDTH - 50), random.randint(50, HEIGHT // 2)))

        # Handle power-ups and downgrades collection first
        for power_up in power_ups[:]:
            power_up.draw()
            if ball.check_collision_with_item(power_up.x, power_up.y, 10):
                paddle_width += power_up.collect()
                power_ups.remove(power_up)

        for downgrade in downgrades[:]:
            downgrade.draw()
            if ball.check_collision_with_item(downgrade.x, downgrade.y, 10):
                paddle_width += downgrade.collect()
                downgrades.remove(downgrade)

        # Update ball and check for collision
        ball.move()
        ball.draw()

        # Ball and wall collision logic (horizontal and vertical walls)
        if ball.x >= WIDTH - ball.radius or ball.x <= ball.radius:
            ball.velocity_x = -ball.velocity_x
        if ball.y <= ball.radius:
            ball.velocity_y = -ball.velocity_y

        # Ball and paddle collision
        paddle_rect = pygame.Rect(paddle_x, paddle_y, paddle_width, paddle_height)
        collision_angle = ball.check_collision_with_paddle(paddle_rect)
        if collision_angle is not None:
            ball.bounce(math.radians(90 * collision_angle))
            score += 1

        # Ball falls below screen
        if ball.y >= HEIGHT - ball.radius:
            lives -= 1
            if lives <= 0:
                game_over = True
            else:
                ball = Ball(WIDTH // 2, HEIGHT // 2, BALL_RADIUS, 5)

        # Draw paddle
        pygame.draw.rect(screen, paddle_color, paddle_rect)

        # Display score, level, and lives
        font = pygame.font.SysFont(None, 36)
        score_text = font.render(f"Score: {score}", True, WHITE)
        level_text = font.render(f"Level: {level}", True, WHITE)
        lives_text = font.render(f"Lives: {lives}", True, WHITE)
        screen.blit(score_text, (10, 10))
        screen.blit(level_text, (WIDTH - level_text.get_width() - 10, 10))
        screen.blit(lives_text, (WIDTH // 2 - lives_text.get_width() // 2, 10))

    else:
        # Display "Game Over" and options to restart or quit
        font = pygame.font.SysFont(None, 48)
        game_over_text = font.render("GAME OVER", True, WHITE)
        restart_text = font.render("Press R to Restart or Q to Quit", True, WHITE)
        screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 50))
        screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 10))

    pygame.display.update()
    clock.tick(FPS)

pygame.quit()
