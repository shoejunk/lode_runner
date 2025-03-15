import pygame
from constants import TileType, GRAVITY, JUMP_FORCE, TILE_SIZE
from tile import Tile

class PhysicsHandler:
    def resolve_collisions(self, entity, tiles):
        # Horizontal collision
        entity.rect.x += round(entity.velocity_x)
        for tile in tiles:
            if tile.collision and entity.rect.colliderect(tile.position):
                if entity.velocity_x > 0:
                    entity.rect.right = tile.position.left
                elif entity.velocity_x < 0:
                    entity.rect.left = tile.position.right
                entity.velocity_x = 0
                break

        # Vertical collision
        entity.velocity_y += GRAVITY
        entity.rect.y += round(entity.velocity_y)
        entity.on_ground = False
        for tile in tiles:
            if tile.collision and entity.rect.colliderect(tile.position):
                if entity.velocity_y > 0:
                    entity.rect.bottom = tile.position.top
                    entity.on_ground = True
                elif entity.velocity_y < 0:
                    entity.rect.top = tile.position.bottom
                entity.velocity_y = 0
                break

        # Ladder detection
        entity.on_ladder = any(tile.tile_type == TileType.LADDER and entity.rect.colliderect(tile.position) for tile in tiles)

    def check_move_valid(self, entity, new_pos, tiles):
        temp_rect = entity.rect.copy()
        temp_rect.topleft = new_pos
        return not any(tile.collision and temp_rect.colliderect(tile.position) for tile in tiles)

def main():
    pygame.init()
    
    class TestEntity:
        def __init__(self, x, y):
            self.rect = pygame.Rect(x, y, TILE_SIZE//2, TILE_SIZE)
            self.velocity_x = 0
            self.velocity_y = 0
            self.on_ground = False
            self.on_ladder = False

    physics = PhysicsHandler()

    # Test horizontal collision
    e = TestEntity(0, 0)
    wall = Tile(TileType.WALL, (TILE_SIZE, 0))
    e.velocity_x = TILE_SIZE
    physics.resolve_collisions(e, [wall])
    assert e.rect.right == wall.position.left and e.velocity_x == 0

    # Test vertical collision
    e = TestEntity(0, TILE_SIZE*2)
    ground = Tile(TileType.GROUND, (0, TILE_SIZE*3))
    e.velocity_y = TILE_SIZE
    physics.resolve_collisions(e, [ground])
    assert e.rect.bottom == ground.position.top and e.on_ground

    # Test ladder detection
    e = TestEntity(0, 0)
    ladder = Tile(TileType.LADDER, (0, 0))
    physics.resolve_collisions(e, [ladder])
    assert e.on_ladder

    # Test move validation
    e = TestEntity(0, 0)
    wall = Tile(TileType.WALL, (TILE_SIZE, 0))
    assert not physics.check_move_valid(e, (TILE_SIZE, 0), [wall])
    assert physics.check_move_valid(e, (TILE_SIZE//2, 0), [])

    # Test terrain modification
    e = TestEntity(0, 0)
    ground = Tile(TileType.GROUND, (0, TILE_SIZE))
    physics.resolve_collisions(e, [ground])
    ground.break_tile()
    physics.resolve_collisions(e, [])
    assert e.rect.y > 0

    pygame.quit()
    print("All tests passed.")

if __name__ == "__main__":
    main()