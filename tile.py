import pygame
from constants import TileType
import constants

class Tile:
    def __init__(self, tile_type, position):
        self.tile_type = tile_type
        self.position = pygame.Rect(position[0], position[1], constants.TILE_SIZE, constants.TILE_SIZE)
        self.collision = self._determine_collision()
        self.diggable = self._determine_diggable()
        self.texture = self._load_texture()
        self.animation_frames = []
        self.current_frame = 0
        self.animation_speed = 200
        self.last_update = pygame.time.get_ticks()
        self.is_breaking = False

    def _determine_collision(self):
        return self.tile_type in [TileType.GROUND, TileType.WALL, TileType.SPIKE]

    def _determine_diggable(self):
        return self.tile_type == TileType.GROUND

    def _load_texture(self):
        colors = {
            TileType.GROUND: constants.GRAY,
            TileType.WALL: constants.BLUE,
            TileType.PLATFORM: constants.GREEN,
            TileType.SPIKE: constants.RED,
            TileType.LADDER: constants.WHITE,
        }
        surface = pygame.Surface((constants.TILE_SIZE, constants.TILE_SIZE))
        surface.fill(colors.get(self.tile_type, constants.WHITE))
        return surface

    def update(self):
        if self.is_breaking:
            now = pygame.time.get_ticks()
            if now - self.last_update > self.animation_speed:
                self.last_update = now
                self.current_frame += 1
                if self.current_frame >= len(self.animation_frames):
                    self.is_breaking = False
                    return True
                self.texture = self.animation_frames[self.current_frame]
        return False

    def render(self, screen):
        screen.blit(self.texture, self.position)

    def break_tile(self):
        if self.diggable and not self.is_breaking:
            self.is_breaking = True
            self.animation_frames = [
                self._create_frame(constants.RED),
                self._create_frame(constants.GRAY),
                self._create_frame(constants.BLACK)
            ]
            self.current_frame = 0

    def _create_frame(self, color):
        surface = pygame.Surface((constants.TILE_SIZE, constants.TILE_SIZE))
        surface.fill(color)
        return surface

def main():
    pygame.init()
    screen = pygame.display.set_mode((constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT))
    clock = pygame.time.Clock()

    # Test initialization
    ground_tile = Tile(TileType.GROUND, (100, 100))
    assert ground_tile.collision == True
    assert ground_tile.diggable == True

    wall_tile = Tile(TileType.WALL, (200, 200))
    assert wall_tile.collision == True
    assert wall_tile.diggable == False

    platform_tile = Tile(TileType.PLATFORM, (300, 300))
    assert platform_tile.collision == False
    assert platform_tile.diggable == False

    # Test breaking functionality
    ground_tile.break_tile()
    assert ground_tile.is_breaking == True
    assert len(ground_tile.animation_frames) == 3

    wall_tile.break_tile()
    assert wall_tile.is_breaking == False

    # Test animation progression
    ground_tile.last_update = pygame.time.get_ticks() - 500
    ground_tile.current_frame = 0
    result = ground_tile.update()
    assert ground_tile.current_frame == 1
    assert result == False

    ground_tile.last_update = pygame.time.get_ticks() - 500
    result = ground_tile.update()
    assert ground_tile.current_frame == 2
    assert result == False

    ground_tile.last_update = pygame.time.get_ticks() - 500
    result = ground_tile.update()
    assert result == True
    assert ground_tile.is_breaking == False

    print("All tests passed. Starting visual demo...")

    # Demo setup
    ground = Tile(TileType.GROUND, (100, 100))
    wall = Tile(TileType.WALL, (200, 200))
    platform = Tile(TileType.PLATFORM, (300, 300))
    running = True
    break_timer = pygame.time.get_ticks()

    while running:
        screen.fill(constants.BLACK)
        current_time = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Auto-break ground tile after 2 seconds
        if current_time - break_timer > 2000:
            ground.break_tile()
            break_timer = current_time

        ground.update()
        wall.update()
        platform.update()

        ground.render(screen)
        wall.render(screen)
        platform.render(screen)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()