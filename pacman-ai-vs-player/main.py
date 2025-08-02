import pygame
import random
import sys
from math import sqrt


# Initialize Pygame
pygame.init()

# Screen settings
WIDTH, HEIGHT = 600, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pac-Man Game")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Game settings
GRID_SIZE = 20
SPEED = 5
SAFE_ZONE_RADIUS = 60  # Pac-Man's safe zone radius around the spawn point

# Pac-Man class
class PacMan:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.score = 0
        self.direction = (0, 0)  # (dx, dy)

    def move(self):
        self.x += self.direction[0] * SPEED
        self.y += self.direction[1] * SPEED
        # Keep Pac-Man in bounds
        self.x = max(0, min(WIDTH - GRID_SIZE, self.x))
        self.y = max(0, min(HEIGHT - GRID_SIZE, self.y))

    def draw(self):
        pygame.draw.circle(screen, YELLOW, (self.x + GRID_SIZE // 2, self.y + GRID_SIZE // 2), GRID_SIZE // 2)

    def collect_pellet(self, pellets):
        for pellet in pellets:
            if pygame.Rect(self.x, self.y, GRID_SIZE, GRID_SIZE).colliderect(
                pygame.Rect(pellet[0], pellet[1], GRID_SIZE, GRID_SIZE)
            ):
                pellets.remove(pellet)
                self.score += 10
                return True
        return False

# Ghost class
class Ghost:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.direction = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])  # Random initial direction

    def move(self):
        self.x += self.direction[0] * SPEED
        self.y += self.direction[1] * SPEED
        # Reverse direction if hitting wall
        if self.x <= 0 or self.x >= WIDTH - GRID_SIZE:
            self.direction = (-self.direction[0], self.direction[1])
        if self.y <= 0 or self.y >= HEIGHT - GRID_SIZE:
            self.direction = (self.direction[0], -self.direction[1])

    def draw(self):
        pygame.draw.rect(screen, RED, (self.x, self.y, GRID_SIZE, GRID_SIZE))

# Utility-based AI agent for Pac-Man
class PacManAI(PacMan):
    def decide(self, pellets, ghosts):
        # Possible moves: stay still or move in one of four directions
        possible_moves = [(0, -1), (0, 1), (-1, 0), (1, 0), (0, 0)]

        def calculate_utility(x, y, ghosts, pellets):
            """
            Calculate utility for a given position:
            - High penalty for being close to ghosts
            - Reward for being close to pellets
            """
            ghost_penalty = sum(
                max(0, SAFE_ZONE_RADIUS - sqrt((x - ghost.x)**2 + (y - ghost.y)**2))
                for ghost in ghosts
            )

            if not pellets:
                return -ghost_penalty  # No pellets, just avoid ghosts
            
            pellet_utility = -min(
                sqrt((x - pellet[0])**2 + (y - pellet[1])**2) for pellet in pellets
            )
            
            return pellet_utility - ghost_penalty
         
        #Predict future positions of ghosts based on their current direction. 
        def predict_ghost_positions(ghosts):
          
            predicted_positions = []
            for ghost in ghosts:
                future_x = ghost.x + ghost.direction[0] * SPEED
                future_y = ghost.y + ghost.direction[1] * SPEED
                predicted_positions.append((future_x, future_y))
            return predicted_positions

        # Predict future ghost positions
        predicted_ghosts = [
            Ghost(px, py) for px, py in predict_ghost_positions(ghosts)
        ]

        # Evaluate all possible moves
        utilities = {}
        for move in possible_moves:
            new_x = self.x + move[0] * SPEED
            new_y = self.y + move[1] * SPEED

            # Stay within bounds
            new_x = max(0, min(WIDTH - GRID_SIZE, new_x))
            new_y = max(0, min(HEIGHT - GRID_SIZE, new_y))

            utilities[move] = calculate_utility(new_x, new_y, predicted_ghosts, pellets)

        # Choose the move with the highest utility
        best_move = max(utilities, key=utilities.get)
        self.direction = best_move

        
# Game loop
def main(player_type):
    clock = pygame.time.Clock()

    # Create Pac-Man
    if player_type == "user":
        pacman = PacMan(WIDTH // 2, HEIGHT // 2)
    else:
        pacman = PacManAI(WIDTH // 2, HEIGHT // 2)

    # Generate ghosts, avoiding Pac-Man's spawn area
    ghosts = []
    while len(ghosts) < 3:
        x = random.randint(0, WIDTH - GRID_SIZE)
        y = random.randint(0, HEIGHT - GRID_SIZE)
        if (abs(x - pacman.x) > SAFE_ZONE_RADIUS or abs(y - pacman.y) > SAFE_ZONE_RADIUS):
            ghosts.append(Ghost(x, y))

    # Generate pellets
    pellets = [[random.randint(0, WIDTH // GRID_SIZE - 1) * GRID_SIZE, random.randint(0, HEIGHT // GRID_SIZE - 1) * GRID_SIZE]
               for _ in range(10)]

    running = True
    while running:
        screen.fill(BLACK)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Handle user input
        if player_type == "user":
            keys = pygame.key.get_pressed()
            if keys[pygame.K_UP]:
                pacman.direction = (0, -1)
            if keys[pygame.K_DOWN]:
                pacman.direction = (0, 1)
            if keys[pygame.K_LEFT]:
                pacman.direction = (-1, 0)
            if keys[pygame.K_RIGHT]:
                pacman.direction = (1, 0)

        # AI decision-making
        elif player_type == "ai":
            pacman.decide(pellets, ghosts)

        # Move Pac-Man and ghosts
        pacman.move()
        for ghost in ghosts:
            ghost.move()

        # Check for pellet collection
        pacman.collect_pellet(pellets)

        # Check if all pellets are collected
        if len(pellets) == 0:
            print(f"You Win! Final Score: {pacman.score}")
            running = False

        # Check for collisions with ghosts
        for ghost in ghosts:
            if pygame.Rect(pacman.x, pacman.y, GRID_SIZE, GRID_SIZE).colliderect(
                pygame.Rect(ghost.x, ghost.y, GRID_SIZE, GRID_SIZE)
            ):
                print(f"Game Over! Final Score: {pacman.score}")
                running = False

        # Draw pellets
        for pellet in pellets:
            pygame.draw.circle(screen, BLUE, (pellet[0] + GRID_SIZE // 2, pellet[1] + GRID_SIZE // 2), GRID_SIZE // 4)

        # Draw Pac-Man and ghosts
        pacman.draw()
        for ghost in ghosts:
            ghost.draw()

        # Update the display
        pygame.display.flip()
        clock.tick(30)

    pygame.quit()
    sys.exit()

# Run the game
if __name__ == "__main__":
    print("Choose Player Type: [1] User-Controlled Pac-Man, [2] AI-Controlled Pac-Man")
    choice = input("Enter 1 or 2: ")
    if choice == "1":
        main(player_type="user")
    elif choice == "2":
        main(player_type="ai")
