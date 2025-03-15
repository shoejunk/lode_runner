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
        self.animation_speed = 200  # milliseconds per frame
        self.last_update = pygame.time.get_ticks()
        self.is_breaking = False

    def _determine_collision(self):
        if self.tile_type in [TileType.GROUND, TileType.WALL, TileType.SPIKE]:
            return True
        elif self.tile_type in [TileType.PLATFORM, TileType.LADDER]:
            return False
        return False

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
                else:
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
    import pygame
    from constants import TileType

    pygame.init()
    screen = pygame.display.set_mode((constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT))
    clock = pygame.time.Clock()

    ground_tile = Tile(TileType.GROUND, (100, 100))
    assert ground_tile.collision == True
    assert ground_tile.diggable == True

    wall_tile = Tile(TileType.WALL, (200, 200))
    assert wall_tile.collision == True
    assert wall_tile.diggable == False

    platform_tile = Tile(TileType.PLATFORM, (300, 300))
    assert platform_tile.collision == False
    assert platform_tile.diggable == False

    ground_tile.break_tile()
    assert ground_tile.is_breaking == True
    assert len(ground_tile.animation_frames) == 3

    wall_tile.break_tile()
    assert wall_tile.is_breaking == False

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

    ground_tile.render(screen)
    pygame.display.flip()
    pygame.time.wait(500)

    print("All tests passed.")
    print("Press any key to exit...")
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                waiting = False

    pygame.quit()

if __name__ == "__main__":
    main()