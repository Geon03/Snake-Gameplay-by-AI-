import pygame
import random
import sys
from collections import deque
import heapq

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
GRID_SIZE = 20
GRID_WIDTH = WINDOW_WIDTH // GRID_SIZE
GRID_HEIGHT = WINDOW_HEIGHT // GRID_SIZE

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
DARK_GREEN = (0, 128, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Directions
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)
DIRECTIONS = [UP, DOWN, LEFT, RIGHT]

class Node:
    """Node class for A* pathfinding algorithm"""
    def __init__(self, x, y, g=0, h=0, parent=None):
        self.x = x
        self.y = y
        self.g = g  # Distance from start
        self.h = h  # Heuristic distance to goal
        self.f = g + h  # Total cost
        self.parent = parent
    
    def __lt__(self, other):
        return self.f < other.f
    
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

class AISnakeGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("AI Snake Game - Pygame")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        
        # Game state
        self.reset_game()
        self.running = True
        self.ai_running = False
        self.game_speed = 10  # FPS
        
    def reset_game(self):
        """Reset the game to initial state"""
        self.snake = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = RIGHT
        self.food = self.generate_food()
        self.score = 0
        self.food_eaten = 0
        self.current_path = []
        self.path_index = 0
        
    def generate_food(self):
        """Generate food at a random position not occupied by snake"""
        while True:
            food_pos = (random.randint(0, GRID_WIDTH - 1), 
                       random.randint(0, GRID_HEIGHT - 1))
            if food_pos not in self.snake:
                return food_pos
    
    def heuristic(self, a, b):
        """Manhattan distance heuristic for A* algorithm"""
        return abs(a[0] - b[0]) + abs(a[1] - b[1])
    
    def get_neighbors(self, pos):
        """Get valid neighboring positions"""
        neighbors = []
        x, y = pos
        
        for dx, dy in DIRECTIONS:
            new_x, new_y = x + dx, y + dy
            
            # Check boundaries
            if 0 <= new_x < GRID_WIDTH and 0 <= new_y < GRID_HEIGHT:
                # Check if position is not occupied by snake body (except tail)
                if (new_x, new_y) not in self.snake[:-1]:  # Exclude tail as it will move
                    neighbors.append((new_x, new_y))
        
        return neighbors
    
    def find_path_astar(self, start, goal):
        """A* pathfinding algorithm"""
        open_set = []
        closed_set = set()
        
        start_node = Node(start[0], start[1], 0, self.heuristic(start, goal))
        heapq.heappush(open_set, start_node)
        
        while open_set:
            current = heapq.heappop(open_set)
            
            if (current.x, current.y) == goal:
                # Reconstruct path
                path = []
                temp = current
                while temp.parent:
                    path.append((temp.x, temp.y))
                    temp = temp.parent
                return path[::-1]  # Reverse to get path from start to goal
            
            closed_set.add((current.x, current.y))
            
            # Check neighbors
            for neighbor_pos in self.get_neighbors((current.x, current.y)):
                if neighbor_pos in closed_set:
                    continue
                
                tentative_g = current.g + 1
                neighbor = Node(neighbor_pos[0], neighbor_pos[1], 
                              tentative_g, self.heuristic(neighbor_pos, goal), current)
                
                # Check if this path to neighbor is better
                existing = None
                for node in open_set:
                    if node.x == neighbor.x and node.y == neighbor.y:
                        existing = node
                        break
                
                if existing is None:
                    heapq.heappush(open_set, neighbor)
                elif tentative_g < existing.g:
                    existing.g = tentative_g
                    existing.f = existing.g + existing.h
                    existing.parent = current
        
        return []  # No path found
    
    def get_safe_direction(self):
        """Get a safe direction when no path to food exists"""
        head = self.snake[0]
        safe_directions = []
        
        for direction in DIRECTIONS:
            new_x = head[0] + direction[0]
            new_y = head[1] + direction[1]
            
            # Check boundaries and collision
            if (0 <= new_x < GRID_WIDTH and 
                0 <= new_y < GRID_HEIGHT and 
                (new_x, new_y) not in self.snake):
                safe_directions.append(direction)
        
        # Return a random safe direction, or current direction if none
        return random.choice(safe_directions) if safe_directions else self.direction
    
    def update_ai(self):
        """Update AI decision making"""
        head = self.snake[0]
        
        # Find path to food using A*
        self.current_path = self.find_path_astar(head, self.food)
        self.path_index = 0
        
        if not self.current_path:
            # No path found, move in a safe direction
            self.direction = self.get_safe_direction()
            return
        
        # Follow the path
        if self.path_index < len(self.current_path):
            next_pos = self.current_path[self.path_index]
            dx = next_pos[0] - head[0]
            dy = next_pos[1] - head[1]
            self.direction = (dx, dy)
            self.path_index += 1
    
    def update_game(self):
        """Update game state"""
        if not self.ai_running:
            return
        
        # Update AI
        self.update_ai()
        
        # Move snake
        head = self.snake[0]
        new_head = (head[0] + self.direction[0], head[1] + self.direction[1])
        
        # Check collisions
        if (new_head[0] < 0 or new_head[0] >= GRID_WIDTH or
            new_head[1] < 0 or new_head[1] >= GRID_HEIGHT or
            new_head in self.snake):
            self.game_over()
            return
        
        self.snake.insert(0, new_head)
        
        # Check food collision
        if new_head == self.food:
            self.score += 10
            self.food_eaten += 1
            self.food = self.generate_food()
        else:
            self.snake.pop()
    
    def game_over(self):
        """Handle game over"""
        self.ai_running = False
        print(f"Game Over! Score: {self.score}, Food Eaten: {self.food_eaten}, Length: {len(self.snake)}")
    
    def draw_snake(self):
        """Draw the snake"""
        for i, segment in enumerate(self.snake):
            x, y = segment[0] * GRID_SIZE, segment[1] * GRID_SIZE
            color = GREEN if i == 0 else DARK_GREEN  # Head is brighter
            pygame.draw.rect(self.screen, color, (x, y, GRID_SIZE, GRID_SIZE))
    
    def draw_food(self):
        """Draw the food"""
        x, y = self.food[0] * GRID_SIZE, self.food[1] * GRID_SIZE
        pygame.draw.rect(self.screen, RED, (x, y, GRID_SIZE, GRID_SIZE))
    
    def draw_ui(self):
        """Draw user interface elements"""
        # Score and stats
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        length_text = self.font.render(f"Length: {len(self.snake)}", True, WHITE)
        food_text = self.font.render(f"Food Eaten: {self.food_eaten}", True, WHITE)
        
        # AI status
        status = "Running" if self.ai_running else "Stopped"
        status_text = self.font.render(f"AI Status: {status}", True, WHITE)
        
        # Instructions
        if not self.ai_running:
            instruction_text = self.font.render("Press SPACE to start AI, R to reset, Q to quit", True, WHITE)
            self.screen.blit(instruction_text, (10, WINDOW_HEIGHT - 30))
        else:
            instruction_text = self.font.render("Press SPACE to stop AI, R to reset, Q to quit", True, WHITE)
            self.screen.blit(instruction_text, (10, WINDOW_HEIGHT - 30))
        
        # Position stats on screen
        self.screen.blit(score_text, (10, 10))
        self.screen.blit(length_text, (10, 50))
        self.screen.blit(food_text, (10, 90))
        self.screen.blit(status_text, (10, 130))
    
    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.ai_running = not self.ai_running
                elif event.key == pygame.K_r:
                    self.reset_game()
                    self.ai_running = False
                elif event.key == pygame.K_q:
                    self.running = False
                elif event.key == pygame.K_UP:
                    self.game_speed = min(20, self.game_speed + 1)
                elif event.key == pygame.K_DOWN:
                    self.game_speed = max(1, self.game_speed - 1)
    
    def run(self):
        """Main game loop"""
        print("AI Snake Game Controls:")
        print("SPACE - Start/Stop AI")
        print("R - Reset Game")
        print("Q - Quit")
        print("UP/DOWN Arrow - Adjust Speed")
        print()
        
        while self.running:
            self.handle_events()
            self.update_game()
            
            # Draw everything
            self.screen.fill(BLACK)
            self.draw_snake()
            self.draw_food()
            self.draw_ui()
            
            pygame.display.flip()
            self.clock.tick(self.game_speed)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = AISnakeGame()
    game.run()
