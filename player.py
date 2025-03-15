import pygame
from constants import Direction, GRAVITY, JUMP_FORCE, MOVEMENT_SPEED, FRICTION, TILE_SIZE, TileType
from physics import PhysicsHandler

class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, TILE_SIZE//2, TILE_SIZE)
        self.physics = PhysicsHandler()
        self.velocity_x = 0
        self.velocity_y = 0
        self.direction = Direction.RIGHT
        self.on_ground = False
        self.on_ladder = False
        self.cooldowns = {'dig': 0}
        self.power_ups = []
        self.animation_state = 'idle'
        self.current_frame = 0
        self.animation_frames = {}
        self.last_animation_update = 0
        self.movement_speed = MOVEMENT_SPEED
        self.jump_force = JUMP_FORCE

    def move(self, left_pressed, right_pressed):
        if left_pressed:
            self.velocity_x = -self.movement_speed
            self.direction = Direction.LEFT
        elif right_pressed:
            self.velocity_x = self.movement_speed
            self.direction = Direction.RIGHT
        else:
            self.velocity_x *= FRICTION

    def jump(self):
        if self.on_ground or self.on_ladder:
            self.velocity_y = self.jump_force
            self.on_ground = False

    def dig(self, tiles):
        if self.cooldowns['dig'] > 0:
            return False
        
        check_x = self.rect.x + TILE_SIZE if self.direction == Direction.RIGHT else self.rect.x - TILE_SIZE
        check_y = self.rect.centery
        
        for tile in tiles:
            if tile.position.collidepoint(check_x, check_y) and tile.diggable:
                tile.break_tile()
                self.cooldowns['dig'] = 0.5
                self.animation_state = 'digging'
                return True
        return False

    def update_cooldowns(self, dt):
        for key in self.cooldowns:
            if self.cooldowns[key] > 0:
                self.cooldowns[key] = max(0, self.cooldowns[key] - dt)

    def apply_power_up(self, power_up):
        self.power_ups.append(power_up)
        if power_up['type'] == 'speed_boost':
            self.movement_speed *= 1.5
        elif power_up['type'] == 'jump_boost':
            self.jump_force *= 1.2

    def reset_attributes(self):
        self.movement_speed = MOVEMENT_SPEED
        self.jump_force = JUMP_FORCE

    def update_power_ups(self, dt):
        for power_up in self.power_ups:
            power_up['duration'] -= dt
        self.power_ups = [p for p in self.power_ups if p['duration'] > 0]
        self.reset_attributes()
        for p in self.power_ups:
            self.apply_power_up(p)

    def update_animation(self, dt):
        if self.animation_state == 'digging':
            self.current_frame = (self.current_frame + 1) % 3
        elif not self.on_ground:
            self.animation_state = 'jumping'
        elif abs(self.velocity_x) > 0.5:
            self.animation_state = 'running'
        else:
            self.animation_state = 'idle'

    def update(self, dt, tiles):
        self.update_cooldowns(dt)
        self.update_power_ups(dt)
        self.physics.resolve_collisions(self, tiles)
        self.update_animation(dt)

def main():
    import pygame
    pygame.init()

    player = Player(0, 0)
    assert player.rect.x == 0 and player.rect.y == 0
    assert player.direction == Direction.RIGHT

    player.move(True, False)
    assert player.velocity_x == -MOVEMENT_SPEED
    assert player.direction == Direction.LEFT

    player.move(False, False)
    assert player.velocity_x == -MOVEMENT_SPEED * FRICTION

    player.on_ground = True
    player.jump()
    assert player.velocity_y == JUMP_FORCE
    assert not player.on_ground

    class MockTile:
        def __init__(self, pos, diggable):
            self.position = pygame.Rect(pos[0], pos[1], TILE_SIZE, TILE_SIZE)
            self.diggable = diggable
            self.is_breaking = False
        def break_tile(self):
            self.is_breaking = True

    tile_right = MockTile((TILE_SIZE, 0), True)
    player.direction = Direction.RIGHT
    player.dig([tile_right])
    assert tile_right.is_breaking
    assert player.cooldowns['dig'] == 0.5

    player.apply_power_up({'type': 'speed_boost', 'duration': 5})
    assert player.movement_speed == MOVEMENT_SPEED * 1.5

    player.update_power_ups(3)
    assert any(p['duration'] == 2 for p in player.power_ups)
    player.update_power_ups(2)
    assert len(player.power_ups) == 0
    assert player.movement_speed == MOVEMENT_SPEED

    player.velocity_x = 1
    player.on_ground = True
    player.update_animation(0)
    assert player.animation_state == 'running'

    player.velocity_x = 0
    player.update_animation(0)
    assert player.animation_state == 'idle'

    player.on_ground = False
    player.update_animation(0)
    assert player.animation_state == 'jumping'

    pygame.quit()
    print("All tests passed.")

if __name__ == "__main__":
    main()