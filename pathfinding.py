import heapq
import pygame
from constants import TILE_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT

class Pathfinder:
    def __init__(self, tiles):
        self.cols = SCREEN_WIDTH // TILE_SIZE
        self.rows = SCREEN_HEIGHT // TILE_SIZE
        self.grid = [[False for _ in range(self.cols)] for _ in range(self.rows)]
        self.update_grid(tiles)

    def update_grid(self, tiles):
        self.grid = [[False for _ in range(self.cols)] for _ in range(self.rows)]
        for tile in tiles:
            x, y = tile.position.x, tile.position.y
            col = x // TILE_SIZE
            row = y // TILE_SIZE
            if 0 <= row < self.rows and 0 <= col < self.cols:
                self.grid[row][col] = tile.collision

    def get_path(self, start_pos, end_pos):
        start = self.world_to_grid(start_pos)
        end = self.world_to_grid(end_pos)
        
        if not self.is_valid(start) or not self.is_valid(end):
            return []
        
        open_heap = []
        heapq.heappush(open_heap, (0, 0, start))
        came_from = {}
        g_scores = {start: 0}
        f_scores = {start: self.heuristic(start, end)}
        closed_set = set()

        while open_heap:
            current_f, current_g, current = heapq.heappop(open_heap)
            if current in closed_set:
                continue
            closed_set.add(current)

            if current == end:
                path = self.reconstruct_path(came_from, current)
                return [self.grid_to_world(node) for node in path]

            for neighbor in self.get_neighbors(current):
                if neighbor in closed_set:
                    continue
                tentative_g = current_g + 1
                if tentative_g < g_scores.get(neighbor, float('inf')):
                    came_from[neighbor] = current
                    g_scores[neighbor] = tentative_g
                    f = tentative_g + self.heuristic(neighbor, end)
                    heapq.heappush(open_heap, (f, tentative_g, neighbor))
                    f_scores[neighbor] = f

        return []

    def get_neighbors(self, pos):
        row, col = pos
        neighbors = []
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            new_row, new_col = row + dr, col + dc
            if 0 <= new_row < self.rows and 0 <= new_col < self.cols:
                if not self.grid[new_row][new_col]:
                    neighbors.append((new_row, new_col))
        return neighbors

    def heuristic(self, a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def reconstruct_path(self, came_from, current):
        path = [current]
        while current in came_from:
            current = came_from[current]
            path.append(current)
        path.reverse()
        return path

    def world_to_grid(self, pos):
        x, y = pos
        return (y // TILE_SIZE, x // TILE_SIZE)

    def grid_to_world(self, grid_pos):
        row, col = grid_pos
        return (col * TILE_SIZE + TILE_SIZE // 2, row * TILE_SIZE + TILE_SIZE // 2)

    def is_valid(self, pos):
        row, col = pos
        return 0 <= row < self.rows and 0 <= col < self.cols and not self.grid[row][col]

def main():
    from tile import Tile
    from constants import TileType

    TILE_SIZE = 64
    TestTile = type('TestTile', (object,), {'position': None, 'collision': False})

    # Test 1: Straight path
    tiles = []
    for col in range(5):
        tile = TestTile()
        tile.position = pygame.Rect(col * TILE_SIZE, 0, TILE_SIZE, TILE_SIZE)
        tile.collision = False
        tiles.append(tile)
    
    pathfinder = Pathfinder(tiles)
    path = pathfinder.get_path((32, 32), (4*TILE_SIZE + 32, 32))
    assert len(path) == 5, "Test 1 failed"

    # Test 2: Obstacle in path
    wall_tile = TestTile()
    wall_tile.position = pygame.Rect(2 * TILE_SIZE, 0, TILE_SIZE, TILE_SIZE)
    wall_tile.collision = True
    tiles.append(wall_tile)
    pathfinder.update_grid(tiles)
    path = pathfinder.get_path((32, 32), (4*TILE_SIZE + 32, 32))
    assert len(path) > 0 and path[-1] == (4*TILE_SIZE + 32, 32), "Test 2 failed"

    # Test 3: Update grid after destruction
    tiles.remove(wall_tile)
    pathfinder.update_grid(tiles)
    path = pathfinder.get_path((32, 32), (4*TILE_SIZE + 32, 32))
    assert len(path) == 5, "Test 3 failed"

    # Test 4: Blocked endpoints
    blocked_tile = TestTile()
    blocked_tile.position = pygame.Rect(0, 0, TILE_SIZE, TILE_SIZE)
    blocked_tile.collision = True
    pathfinder.update_grid([blocked_tile])
    path = pathfinder.get_path((32, 32), (4*TILE_SIZE + 32, 32))
    assert len(path) == 0, "Test 4 failed"

    print("All tests passed")

if __name__ == "__main__":
    main()