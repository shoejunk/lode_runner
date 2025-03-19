#!/usr/bin/env python3
import os
import sys
import json
import pygame
from constants import TILE_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT, TileType, BLACK
from tile import Tile
from level_loader import load_level

class EditorTools:
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.grid = []
        for row in range(rows):
            row_tiles = []
            for col in range(cols):
                position = (col * TILE_SIZE, row * TILE_SIZE)
                row_tiles.append(Tile(TileType.GROUND, position))
            self.grid.append(row_tiles)
        self.selected_tile_type = TileType.GROUND

    def select_tile_type(self, tile_type):
        self.selected_tile_type = tile_type

    def place_tile(self, row, col):
        if 0 <= row < self.rows and 0 <= col < self.cols and self.selected_tile_type is not None:
            position = (col * TILE_SIZE, row * TILE_SIZE)
            self.grid[row][col] = Tile(self.selected_tile_type, position)

    def remove_tile(self, row, col):
        if 0 <= row < self.rows and 0 <= col < self.cols:
            position = (col * TILE_SIZE, row * TILE_SIZE)
            self.grid[row][col] = Tile(TileType.GROUND, position)

    def save_level(self, filepath, spawn=(0, 0), enemies=[], treasures=[]):
        level_data = {}
        level_data["tiles"] = [[tile.tile_type.name for tile in row] for row in self.grid]
        level_data["spawn"] = list(spawn)
        level_data["enemies"] = [list(pos) for pos in enemies]
        level_data["treasures"] = [list(pos) for pos in treasures]
        with open(filepath, "w") as f:
            json.dump(level_data, f, indent=4)
        return True

    def load_level(self, filepath):
        level = load_level(filepath)
        self.grid = level["tiles"]
        self.rows = len(self.grid)
        self.cols = len(self.grid[0]) if self.rows > 0 else 0
        return level["spawn"], level["enemies"], level["treasures"]

    def render(self, screen):
        for row in self.grid:
            for tile in row:
                tile.render(screen)

class PreviewSystem:
    def __init__(self, level_data):
        self.level_data = level_data

    def run_preview(self, duration=2000):
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        clock = pygame.time.Clock()
        start_time = pygame.time.get_ticks()
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            screen.fill(BLACK)
            for row in self.level_data["tiles"]:
                for tile in row:
                    tile.render(screen)
            pygame.display.flip()
            if pygame.time.get_ticks() - start_time > duration:
                running = False
            clock.tick(60)

    def get_level_info(self):
        rows = len(self.level_data["tiles"])
        cols = len(self.level_data["tiles"][0]) if rows > 0 else 0
        enemy_count = len(self.level_data["enemies"])
        treasure_count = len(self.level_data["treasures"])
        return {"rows": rows, "cols": cols, "enemies": enemy_count, "treasures": treasure_count}

def run_tests():
    pygame.init()
    # Test EditorTools default grid initialization and tile placement/removal
    rows, cols = 5, 5
    editor = EditorTools(rows, cols)
    for row in editor.grid:
        for tile in row:
            assert tile.tile_type == TileType.GROUND, "Default tile should be GROUND"
    editor.select_tile_type(TileType.WALL)
    editor.place_tile(2, 2)
    assert editor.grid[2][2].tile_type == TileType.WALL, "Tile at (2,2) should be WALL after placement"
    editor.remove_tile(2, 2)
    assert editor.grid[2][2].tile_type == TileType.GROUND, "Tile at (2,2) should be reset to GROUND after removal"

    # Test save and load level functionality.
    temp_filename = "temp_level.json"
    spawn_point = (64, 64)
    enemies = [(128, 128), (192, 192)]
    treasures = [(256, 256)]
    save_status = editor.save_level(temp_filename, spawn=spawn_point, enemies=enemies, treasures=treasures)
    assert save_status == True, "save_level should return True on success"
    assert os.path.exists(temp_filename), "Level file should exist after saving"
    editor.select_tile_type(TileType.SPIKE)
    editor.place_tile(0, 0)
    assert editor.grid[0][0].tile_type == TileType.SPIKE, "Tile at (0,0) should be SPIKE after placement"
    spawn_loaded, enemies_loaded, treasures_loaded = editor.load_level(temp_filename)
    assert editor.grid[0][0].tile_type == TileType.GROUND, "Tile at (0,0) should be GROUND after loading saved level"
    assert tuple(spawn_loaded) == spawn_point, "Loaded spawn point does not match saved spawn point"
    assert [tuple(pos) for pos in enemies_loaded] == enemies, "Loaded enemies do not match saved enemies"
    assert [tuple(pos) for pos in treasures_loaded] == treasures, "Loaded treasures do not match saved treasures"
    os.remove(temp_filename)

    # Test PreviewSystem functionality.
    level_data = {
        "tiles": editor.grid,
        "spawn": spawn_point,
        "enemies": enemies,
        "treasures": treasures
    }
    preview = PreviewSystem(level_data)
    info = preview.get_level_info()
    assert info["rows"] == rows, "Preview level info rows count mismatch"
    assert info["cols"] == cols, "Preview level info columns count mismatch"
    assert info["enemies"] == len(enemies), "Preview enemy count mismatch"
    assert info["treasures"] == len(treasures), "Preview treasure count mismatch"
    # Run preview briefly (not interactive test)
    preview.run_preview(duration=500)

    print("All EditorTools and PreviewSystem tests passed successfully.")
    pygame.quit()

def run_editor():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Level Editor - Press 1-5 to change tile type, LMB to place, RMB to remove, S to save, L to load, P to preview, Q to quit")
    clock = pygame.time.Clock()
    
    rows = SCREEN_HEIGHT // TILE_SIZE
    cols = SCREEN_WIDTH // TILE_SIZE
    editor = EditorTools(rows, cols)
    
    current_spawn = (0, 0)
    current_enemies = []
    current_treasures = []
    save_filepath = "custom_level.json"
    
    font = pygame.font.SysFont(None, 24)
    
    instructions = [
        "Level Editor Controls:",
        "1: GROUND, 2: WALL, 3: PLATFORM, 4: SPIKE, 5: LADDER",
        "Left Click: Place tile | Right Click: Remove tile",
        "S: Save level | L: Load level | P: Preview level | Q: Quit"
    ]
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                # Change selected tile type with number keys
                if event.key == pygame.K_1:
                    editor.select_tile_type(TileType.GROUND)
                elif event.key == pygame.K_2:
                    editor.select_tile_type(TileType.WALL)
                elif event.key == pygame.K_3:
                    editor.select_tile_type(TileType.PLATFORM)
                elif event.key == pygame.K_4:
                    editor.select_tile_type(TileType.SPIKE)
                elif event.key == pygame.K_5:
                    editor.select_tile_type(TileType.LADDER)
                elif event.key == pygame.K_s:
                    # Save level with current grid; spawn point set to (0,0) for simplicity
                    editor.save_level(save_filepath, spawn=current_spawn, enemies=current_enemies, treasures=current_treasures)
                    print(f"Level saved to {save_filepath}")
                elif event.key == pygame.K_l:
                    try:
                        spawn_loaded, enemies_loaded, treasures_loaded = editor.load_level(save_filepath)
                        current_spawn = tuple(spawn_loaded)
                        current_enemies = enemies_loaded
                        current_treasures = treasures_loaded
                        print(f"Level loaded from {save_filepath}")
                    except Exception as e:
                        print(f"Error loading level: {e}")
                elif event.key == pygame.K_p:
                    # Preview the current level using PreviewSystem
                    level_data = {
                        "tiles": editor.grid,
                        "spawn": current_spawn,
                        "enemies": current_enemies,
                        "treasures": current_treasures
                    }
                    preview = PreviewSystem(level_data)
                    preview.run_preview(duration=1000)
                elif event.key == pygame.K_q:
                    running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                row = y // TILE_SIZE
                col = x // TILE_SIZE
                if event.button == 1:
                    editor.place_tile(row, col)
                elif event.button == 3:
                    editor.remove_tile(row, col)

        screen.fill(BLACK)
        editor.render(screen)
        # Render instructions overlay
        y_offset = 5
        for line in instructions:
            text = font.render(line, True, (255,255,255))
            screen.blit(text, (5, y_offset))
            y_offset += 20
        # Show current selected tile type
        current_tile_text = font.render(f"Current Tile: {editor.selected_tile_type.name}", True, (255,255,0))
        screen.blit(current_tile_text, (5, y_offset))
        pygame.display.flip()
        clock.tick(60)
    pygame.quit()

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        run_tests()
    else:
        run_editor()

if __name__ == "__main__":
    main()