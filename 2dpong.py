import curses
import random
import time
import math


# PowerUp class to extend paddle size upon collision with animated effect
class PowerUp:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.active = True

    def draw(self, stdscr, frame):
        if self.active:
            # Alternate color every frame for blinking effect
            color = curses.color_pair(3) if frame % 2 == 0 else curses.color_pair(5)
            stdscr.addch(self.y, self.x, 'P', color)  # Draw as blinking 'P'

    def collect(self):
        """Deactivate the power-up and apply its effect."""
        self.active = False
        return 3  # Amount by which to increase the paddle width


# Downgrade class to reduce paddle size upon collision with animated effect
class Downgrade:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.active = True

    def draw(self, stdscr, frame):
        if self.active:
            # Alternate color every frame for blinking effect
            color = curses.color_pair(4) if frame % 2 == 0 else curses.color_pair(5)
            stdscr.addch(self.y, self.x, '*', color)  # Draw as blinking '*'

    def collect(self):
        """Deactivate the downgrade and apply its effect."""
        self.active = False
        return -3  # Amount by which to reduce the paddle width


def draw_ball(stdscr, x, y, radius, color):
    # Draws a circular ball shape using "o" characters around a center point
    for angle in range(0, 360, 15):
        radian = math.radians(angle)
        ball_x = int(radius * math.cos(radian)) + x
        ball_y = int(radius * math.sin(radian)) + y

        # Check bounds before drawing
        if 0 <= ball_x < curses.COLS and 0 <= ball_y < curses.LINES:
            stdscr.addch(ball_y, ball_x, 'o', curses.color_pair(color))


def show_background_pattern(stdscr):
    # Make sure the color pair 5 is initialized
    curses.init_pair(5, curses.COLOR_BLUE, curses.COLOR_BLACK)

    # Draw background pattern with dots, ensuring bounds are respected
    screen_height, screen_width = stdscr.getmaxyx()
    for i in range(0, screen_height, 2):
        for j in range(0, screen_width, 4):
            # Check if coordinates are within the screen dimensions
            if 0 <= i < screen_height and 0 <= j < screen_width:
                try:
                    stdscr.addch(i, j, '.', curses.color_pair(5))
                except curses.error:
                    # Ignore errors if the terminal size changes dynamically
                    pass

def mini_game(stdscr):
    # Initialize colors
    curses.start_color()
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)  # Ball color
    curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)  # Paddle color
    curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)  # Power-up color
    curses.init_pair(4, curses.COLOR_RED, curses.COLOR_BLACK)  # Downgrade color
    curses.init_pair(5, curses.COLOR_BLACK, curses.COLOR_BLACK)  # Background effect

    screen_height, screen_width = stdscr.getmaxyx()
    curses.curs_set(0)
    stdscr.nodelay(1)

    while True:
        # Display start screen
        stdscr.clear()
        stdscr.addstr(screen_height // 2 - 1, screen_width // 2 - 7, "Welcome to Pong!")
        stdscr.addstr(screen_height // 2, screen_width // 2 - 9, "Press 's' to start")
        stdscr.addstr(screen_height // 2 + 1, screen_width // 2 - 9, "Press 'q' to quit")
        stdscr.refresh()

        key = stdscr.getch()
        if key == ord('s'):
            break
        elif key == ord('q'):
            return

    while True:
        # Initialize game variables
        stdscr.clear()
        stdscr.border('|', '|', '-', '-', '+', '+', '+', '+')
        stdscr.timeout(50)

        # Ball properties
        x, y = screen_width // 2, screen_height // 2
        radius = 2
        direction_x, direction_y = random.choice([-1, 1]), 1
        color = 1

        # Paddle properties
        original_paddle_width = min(15, screen_width - 1)
        paddle_width = original_paddle_width
        paddle_x = (screen_width - paddle_width) // 2
        paddle_y = screen_height - 2


        score = 0
        level = 1
        lives = 3
        game_over = False
        frame = 0
        next_level_threshold = 5  # Level increases every 5 points

        # Initialize power-ups and downgrades
        power_ups = []
        downgrades = []
        power_up_effect_end = 0

        while not game_over and lives > 0:
            stdscr.clear()
            stdscr.border('|', '|', '-', '-', '+', '+', '+', '+')

            # Draw background pattern
            show_background_pattern(stdscr)

            # Draw ball as a circle
            draw_ball(stdscr, x, y, radius, color)
            color = (color % 2) + 1

            # Ensure paddle width does not exceed screen width
            paddle_width = max(1, min(paddle_width, screen_width - 1))

            # Draw paddle with bounds checking
            stdscr.hline(paddle_y, max(0, paddle_x), '=', paddle_width, curses.color_pair(2))

            # Spawn power-ups or downgrades randomly
            if random.randint(1, 100) <= 20 and not power_ups:
                power_ups.append(PowerUp(random.randint(1, screen_width - 2), random.randint(1, screen_height // 2)))
            if random.randint(1, 100) <= 20 and not downgrades:
                downgrades.append(Downgrade(random.randint(1, screen_width - 2), random.randint(1, screen_height // 2)))

            # Draw and handle power-ups
            for power_up in power_ups:
                if power_up.active:
                    power_up.draw(stdscr, frame)
                    # Check for collision with ball
                    if power_up.x in range(x - radius, x + radius + 1) and power_up.y in range(y - radius,
                                                                                               y + radius + 1):
                        power_up_effect_end = time.time() + 5  # Extend paddle effect for 5 seconds
                        paddle_width = min(original_paddle_width + power_up.collect(), screen_width - 1)
                        power_ups.remove(power_up)

            # Draw and handle downgrades
            for downgrade in downgrades:
                if downgrade.active:
                    downgrade.draw(stdscr, frame)
                    # Check for collision with ball
                    if downgrade.x in range(x - radius, x + radius + 1) and downgrade.y in range(y - radius,
                                                                                                 y + radius + 1):
                        paddle_width = max(paddle_width + downgrade.collect(), 5)  # Reduce paddle width
                        downgrades.remove(downgrade)

            # Ball movement and collision logic
            # Bounce off paddle
            if (y + radius >= paddle_y - 1) and (paddle_x <= x <= paddle_x + paddle_width):
                direction_y *= -1
                y = paddle_y - radius - 1
                score += 1

            # Bounce off walls
            if x >= screen_width - radius:
                direction_x *= -1
                x = screen_width - radius - 1
            elif x <= radius:
                direction_x *= -1
                x = radius + 1

            # Bounce off top
            if y <= radius:
                direction_y *= -1
                y = radius + 1

            # Ball falls below screen
            if y >= screen_height - radius:
                lives -= 1
                if lives == 0:
                    game_over = True
                else:
                    x, y = screen_width // 2, screen_height // 2  # Reset ball position

            # Update ball position
            x += direction_x
            y += direction_y

            # User input for paddle movement
            key = stdscr.getch()
            if key == curses.KEY_LEFT and paddle_x > 0:
                paddle_x -= 2
            elif key == curses.KEY_RIGHT and paddle_x < screen_width - paddle_width:
                paddle_x += 2
            elif key == ord('q'):
                return

            # Level increase logic
            if score >= next_level_threshold:
                level += 1
                next_level_threshold += 5

            # Display score, level, and lives

            stdscr.addstr(0, 2, f"Score: {score} | Level: {level} | Lives: {lives}",
                          curses.color_pair(2) | curses.A_BOLD)
            stdscr.hline(1, 1, '-', screen_width - 2, curses.color_pair(2))

            # Revert paddle width if power-up effect expired
            if power_up_effect_end and time.time() > power_up_effect_end:
                paddle_width = original_paddle_width
                power_up_effect_end = 0

            stdscr.refresh()
            time.sleep(0.05)
            frame += 1

        # Game over screen
        stdscr.clear()
        stdscr.addstr(screen_height // 2, screen_width // 2 - 5, "GAME OVER!")
        stdscr.addstr(screen_height // 2 + 1, screen_width // 2 - 9, f"Final Score: {score}")
        stdscr.addstr(screen_height // 2 + 2, screen_width // 2 - 11, "Press 'q' to quit")
        stdscr.refresh()
        key = stdscr.getch()
        while key != ord('q'):
            key = stdscr.getch()


curses.wrapper(mini_game)
