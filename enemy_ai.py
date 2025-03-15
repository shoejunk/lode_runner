import pygame
from pygame.math import Vector2
from constants import TILE_SIZE
from pathfinding import Pathfinder
from physics import PhysicsHandler

class BehaviorTree:
    def __init__(self, enemy):
        self.enemy = enemy

    def decide_state(self, player_pos):
        if self.enemy.health < self.enemy.retreat_threshold:
            return "retreat"
        player_distance = Vector2(player_pos).distance_to(self.enemy.position)
        if self.enemy.state == "chase":
            if player_distance <= self.enemy.detection_radius:
                return "chase"
            else:
                return "patrol"
        else:
            if player_distance <= self.enemy.detection_radius or self.enemy.alerted:
                return "chase"
            return "patrol"

class EnemyAI:
    def __init__(self, position, patrol_points, pathfinder, physics_handler):
        self.position = Vector2(position)
        self.patrol_points = [Vector2(point) for point in patrol_points]
        self.current_patrol_index = 0
        self.pathfinder = pathfinder
        self.physics = physics_handler
        self.path = []
        self.state = "patrol"
        self.health = 100
        self.alerted = False
        self.speed = 2
        self.detection_radius = 200
        self.retreat_threshold = 30
        self.behavior_tree = BehaviorTree(self)
        self.group = []

    def update(self, player_pos, tiles):
        prev_state = self.state
        new_state = self.behavior_tree.decide_state(player_pos)
        if self.state == "chase" and new_state != "chase":
            self.alerted = False
        self.state = new_state

        if prev_state != "chase" and self.state == "chase":
            self._alert_group()
        
        if self.state == "patrol":
            self._patrol(tiles)
        elif self.state == "chase":
            self._chase(player_pos, tiles)
        elif self.state == "retreat":
            self._retreat(tiles)

    def _patrol(self, tiles):
        if not self.path:
            target = self.patrol_points[self.current_patrol_index]
            self.path = self.pathfinder.get_path(self.position, target)
            if self.path:
                self.current_patrol_index = (self.current_patrol_index + 1) % len(self.patrol_points)
        self._follow_path()

    def _chase(self, player_pos, tiles):
        self.path = self.pathfinder.get_path(self.position, player_pos)
        self._follow_path()

    def _retreat(self, tiles):
        self.path = self.pathfinder.get_path(self.position, self.patrol_points[0])
        self._follow_path()

    def _follow_path(self):
        if self.path:
            target = Vector2(self.path[0])
            direction = target - self.position
            if direction.length() >= self.speed:
                direction.scale_to_length(self.speed)
                self.position += direction
            else:
                self.position = target
                self.path.pop(0)

    def _alert_group(self):
        for enemy in self.group:
            if enemy != self:
                enemy.alerted = True
        self.alerted = True

    def take_damage(self, damage):
        self.health -= damage

def main():
    class MockPathfinder:
        def get_path(self, start, end):
            return [Vector2(end)]
    class MockPhysics: pass

    patrol_points = [(100, 100), (300, 100)]
    pathfinder = MockPathfinder()
    physics = MockPhysics()
    enemy = EnemyAI((200, 100), patrol_points, pathfinder, physics)
    enemy.group = []

    assert enemy.state == "patrol", "Test 1 failed"

    enemy.update((200, 150), [])
    assert enemy.state == "chase", "Test 2 failed"

    enemy.update((500, 500), [])
    assert enemy.state == "patrol", "Test 3 failed"

    enemy.health = 20
    enemy.update((200, 150), [])
    assert enemy.state == "retreat", "Test 4 failed"

    enemy2 = EnemyAI((200, 200), patrol_points, pathfinder, physics)
    enemy.group = [enemy2]
    enemy.alerted = False
    enemy.update((200, 150), [])
    assert enemy2.alerted, "Test 5 failed"

    enemy.state = "patrol"
    enemy.path = [Vector2(300, 100)]
    enemy.position = Vector2(290, 100)
    enemy._follow_path()
    assert enemy.position == Vector2(300, 100) and not enemy.path, "Test 6 failed"

    print("All tests passed.")

if __name__ == "__main__":
    main()