import pygame
import random
import cairo
import math

# Variables
SPEED = 10
GRAVITY = 1
GAME_SPEED = 5
PIPE_WIDTH = 80
PIPE_GAP = 120
BIRD_RADIUS = 20
LIVES = 3

# Screen dimensions (You can adjust these)
SCREEN_WIDTH = 800  # Adjust screen width
SCREEN_HEIGHT = 600  # Adjust screen height

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))  # Use set dimensions
pygame.display.set_caption('OG Flappy Bird')
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 30)

# Load background image and scale to fit screen
background_image = pygame.image.load("newyork.jpg")
background_image = pygame.transform.scale(background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))  # Adjust to fit screen

# Bird (Sphere) Class with 3D gradient effect
class Bird:
    def __init__(self):
        self.x = SCREEN_WIDTH // 6
        self.y = SCREEN_HEIGHT // 2
        self.speed = 0

    def update(self):
        self.speed += GRAVITY
        self.y += self.speed

    def bump(self):
        self.speed = -SPEED

    def draw(self, screen):
        # Create a Cairo surface for the bird shape
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 2 * BIRD_RADIUS, 2 * BIRD_RADIUS)
        cr = cairo.Context(surface)
        
        # Body of the bird - Use an ellipse for the body
        cr.set_source_rgb(0.114, 0.631, 0.949)  # Blue color (Twitter blue: #1DA1F2)
        cr.arc(BIRD_RADIUS, BIRD_RADIUS, BIRD_RADIUS, 0, 2 * math.pi)  # Body as a circle
        cr.fill()

        # Wings - Draw two polygons representing wings
        cr.set_source_rgb(0.114, 0.631, 0.949)  # Same blue color for the wings
        cr.move_to(BIRD_RADIUS, BIRD_RADIUS)  # Start point at the center
        cr.line_to(BIRD_RADIUS - 15, BIRD_RADIUS - 25)  # Top left wing
        cr.line_to(BIRD_RADIUS + 15, BIRD_RADIUS - 25)  # Top right wing
        cr.close_path()
        cr.fill()

        # Head of the bird - Smaller circle at the top of the body
        cr.set_source_rgb(0.114, 0.631, 0.949)  # Same blue color for the head
        cr.arc(BIRD_RADIUS, BIRD_RADIUS - BIRD_RADIUS // 2, BIRD_RADIUS // 2, 0, 2 * math.pi)  # Head
        cr.fill()

        # Beak of the bird - Triangle
        cr.set_source_rgb(1, 0.6, 0)  # Orange color for the beak
        cr.move_to(BIRD_RADIUS + BIRD_RADIUS // 2, BIRD_RADIUS - BIRD_RADIUS // 2)  # Beak start position
        cr.line_to(BIRD_RADIUS + BIRD_RADIUS, BIRD_RADIUS - BIRD_RADIUS // 2 - 10)  # Right point of the beak
        cr.line_to(BIRD_RADIUS + BIRD_RADIUS, BIRD_RADIUS - BIRD_RADIUS // 2 + 10)  # Left point of the beak
        cr.close_path()
        cr.fill()

        # Convert Cairo surface to Pygame surface and blit
        bird_surface = pygame.image.frombuffer(surface.get_data(), (2 * BIRD_RADIUS, 2 * BIRD_RADIUS), "ARGB")
        screen.blit(bird_surface, (self.x - BIRD_RADIUS, int(self.y) - BIRD_RADIUS))


# Pipe Class with shading for 3D effect
class Pipe:
    def __init__(self, x, height, inverted):
        self.x = x
        self.width = PIPE_WIDTH
        self.height = height
        self.inverted = inverted

    def update(self):
        self.x -= GAME_SPEED

    def draw(self, screen):
        # Use Cairo for shading effect on the pipes
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, PIPE_WIDTH, SCREEN_HEIGHT)
        cr = cairo.Context(surface)
        
        # Draw pipe with shading for 3D effect
        cr.rectangle(0, 0, PIPE_WIDTH, SCREEN_HEIGHT)
        gradient = cairo.LinearGradient(0, 0, PIPE_WIDTH, 0)
        gradient.add_color_stop_rgba(0, 140.2, 140.8, 140.2, 1)  # Left side
        gradient.add_color_stop_rgba(1, 255, 255, 0.8, 1)      # Right side
        cr.set_source(gradient)
        cr.fill()

        # Convert Cairo surface to Pygame surface
        pipe_surface = pygame.image.frombuffer(surface.get_data(), (PIPE_WIDTH, SCREEN_HEIGHT), "ARGB")

        # Draw pipe in the correct position
        if self.inverted:
            screen.blit(pipe_surface, (self.x, 0), (0, SCREEN_HEIGHT - self.height, PIPE_WIDTH, self.height))
        else:
            screen.blit(pipe_surface, (self.x, SCREEN_HEIGHT - self.height))

    def collide(self, bird):
        if bird.x + BIRD_RADIUS > self.x and bird.x - BIRD_RADIUS < self.x + self.width:
            if self.inverted and bird.y - BIRD_RADIUS < self.height:
                return True
            if not self.inverted and bird.y + BIRD_RADIUS > SCREEN_HEIGHT - self.height:
                return True
        return False

# Functions
def create_pipes():
    height = random.randint(100, SCREEN_HEIGHT - PIPE_GAP - 100)
    top_pipe = Pipe(SCREEN_WIDTH, height, True)
    bottom_pipe = Pipe(SCREEN_WIDTH, SCREEN_HEIGHT - height - PIPE_GAP, False)
    return top_pipe, bottom_pipe

# Modified display_lives function to use black text color
def display_lives(lives):
    lives_text = font.render(f"Lives: {lives}", True, (0, 0, 0))  # Black color for text
    screen.blit(lives_text, (10, 10))

# Display the number of completed pipes
def display_completed_pipes(completed_pipes):
    completed_text = font.render(f"Pipes: {completed_pipes}", True, (0, 0, 0))  # Black color for text
    screen.blit(completed_text, (SCREEN_WIDTH - 120, 10))

# Game variables
bird = Bird()
pipes = list(create_pipes())
lives = LIVES
game_started = False
paused = False  # Track if the game is paused
running = True
completed_pipes = 0  # To track the number of pipes passed

# Main game loop
while running:
    # Draw background image
    screen.blit(background_image, (0, 0))

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if not game_started:
                    game_started = True
                    bird = Bird()  # Reset bird position
                    pipes = list(create_pipes())  # Reset pipes
                    lives = LIVES  # Reset lives
                else:
                    bird.bump()
            if event.key == pygame.K_p:
                paused = not paused  # Toggle pause state

    if paused:
        # Display paused message
        pause_message = font.render("Game Paused. Press 'P' to Resume", True, (255, 255, 255))
        screen.blit(pause_message, (SCREEN_WIDTH // 2 - pause_message.get_width() // 2, SCREEN_HEIGHT // 2 - pause_message.get_height() // 2))
        
        # Display current score below the paused message
        score_message = font.render(f"Your current score is: {completed_pipes}", True, (255, 255, 255))
        screen.blit(score_message, (SCREEN_WIDTH // 2 - score_message.get_width() // 2, SCREEN_HEIGHT // 2 + 30))

        pygame.display.flip()
        clock.tick(10)  # Slow down the game loop when paused
        continue

    if not game_started:
        # Display start screen or message
        start_message = font.render("Press SPACE to start", True, (255, 255, 255))
        screen.blit(start_message, (SCREEN_WIDTH // 2 - start_message.get_width() // 2, SCREEN_HEIGHT // 2 - start_message.get_height() // 2))
        pygame.display.flip()
        clock.tick(30)
        continue

    # Update game state
    bird.update()
    for pipe in pipes:
        pipe.update()

    # Check for collisions
    if any(pipe.collide(bird) for pipe in pipes) or bird.y >= SCREEN_HEIGHT - BIRD_RADIUS:
        lives -= 1
        if lives <= 0:
            game_started = False  # Return to start screen
            completed_pipes = 0   # Reset completed pipes counter
        else:
            bird = Bird()  # Reset bird position
            pipes = list(create_pipes())  # Reset pipes

    # Remove pipes that have moved off-screen
    pipes = [pipe for pipe in pipes if pipe.x + PIPE_WIDTH > 0]

    # Add new pipes if necessary
    if pipes[-1].x < SCREEN_WIDTH - 300:
        pipes.extend(create_pipes())

    # Check if the bird passed a pipe (completed a pipe)
    if pipes[0].x + PIPE_WIDTH < bird.x:
        completed_pipes += 1
        pipes.pop(0)  # Remove the pipe from the list

    # Draw everything
    for pipe in pipes:
        pipe.draw(screen) 
    bird.draw(screen)
    display_lives(lives)
    display_completed_pipes(completed_pipes)

    pygame.display.flip()
    clock.tick(30)

pygame.quit()
