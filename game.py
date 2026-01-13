import pygame
import random
import sys

# -------------------- Configuration --------------------
GRID_SIZE = 20  # size of each cell in pixels
GRID_WIDTH = 30  # number of cells horizontally
GRID_HEIGHT = 20  # number of cells vertically
FPS_START = 10  # initial frames per second

SNAKE_COLOR = (0, 255, 0)
FOOD_COLOR = (255, 0, 0)
BG_COLOR = (0, 0, 0)
TEXT_COLOR = (255, 255, 255)

FONT_NAME = None  # default font
POINTS_PER_FOOD = 10


# -------------------- Helper Functions --------------------
def draw_rect(surface, color, pos):
    rect = pygame.Rect(pos[0] * GRID_SIZE, pos[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE)
    pygame.draw.rect(surface, color, rect)


def random_food_position(snake_body):
    while True:
        pos = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
        if pos not in snake_body:
            return pos


# -------------------- Main Game Class --------------------
class SnakeGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(
            (GRID_WIDTH * GRID_SIZE, GRID_HEIGHT * GRID_SIZE + 40)
        )
        pygame.display.set_caption("Snake")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(FONT_NAME, 24)

        self.high_score = 0
        self.reset()

    def reset(self):
        mid_x = GRID_WIDTH // 2
        mid_y = GRID_HEIGHT // 2
        self.snake_body = [(mid_x, mid_y), (mid_x - 1, mid_y), (mid_x - 2, mid_y)]
        self.direction = (1, 0)  # moving right initially
        self.next_direction = self.direction
        self.food_pos = random_food_position(self.snake_body)
        self.score = 0
        self.fps = FPS_START
        self.game_over = False

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                # Map arrow keys and WASD to directions
                if event.key in (pygame.K_UP, pygame.K_w):
                    new_dir = (0, -1)
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    new_dir = (0, 1)
                elif event.key in (pygame.K_LEFT, pygame.K_a):
                    new_dir = (-1, 0)
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    new_dir = (1, 0)
                else:
                    continue

                # Prevent reversing direction
                if new_dir[0] != -self.direction[0] or new_dir[1] != -self.direction[1]:
                    self.next_direction = new_dir

    def update(self):
        if self.game_over:
            return

        # Move snake
        head_x, head_y = self.snake_body[0]
        dir_x, dir_y = self.next_direction
        new_head = (head_x + dir_x, head_y + dir_y)

        # Check wall collision
        if not (0 <= new_head[0] < GRID_WIDTH and 0 <= new_head[1] < GRID_HEIGHT):
            self.game_over = True
            return

        # Check self collision
        if new_head in self.snake_body:
            self.game_over = True
            return

        # Insert new head
        self.snake_body.insert(0, new_head)
        self.direction = self.next_direction

        # Check food consumption
        if new_head == self.food_pos:
            self.score += POINTS_PER_FOOD
            self.food_pos = random_food_position(self.snake_body)
            # Increase speed slightly after each food
            self.fps = min(30, self.fps + 0.5)
        else:
            # Remove tail segment
            self.snake_body.pop()

    def render(self):
        self.screen.fill(BG_COLOR)

        # Draw snake
        for segment in self.snake_body:
            draw_rect(self.screen, SNAKE_COLOR, segment)

        # Draw food
        draw_rect(self.screen, FOOD_COLOR, self.food_pos)

        # Draw score
        score_surf = self.font.render(f"Score: {self.score}", True, TEXT_COLOR)
        high_surf = self.font.render(f"High Score: {self.high_score}", True, TEXT_COLOR)
        self.screen.blit(score_surf, (10, GRID_HEIGHT * GRID_SIZE + 5))
        self.screen.blit(high_surf, (200, GRID_HEIGHT * GRID_SIZE + 5))

        # Game over message
        if self.game_over:
            over_surf = self.font.render(
                "Game Over! Press R to restart", True, TEXT_COLOR
            )
            rect = over_surf.get_rect(
                center=(GRID_WIDTH * GRID_SIZE // 2, (GRID_HEIGHT * GRID_SIZE) // 2)
            )
            self.screen.blit(over_surf, rect)

        pygame.display.flip()

    def run(self):
        while True:
            self.handle_events()
            self.update()
            if self.game_over and pygame.key.get_pressed()[pygame.K_r]:
                # Update high score
                if self.score > self.high_score:
                    self.high_score = self.score
                self.reset()
            self.render()
            self.clock.tick(int(self.fps))


# -------------------- Entry Point --------------------
if __name__ == "__main__":
    game = SnakeGame()
    game.run()
