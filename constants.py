from enum import Enum
import pygame

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
TILE_SIZE = 64

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GRAY = (128, 128, 128)

KEY_BINDINGS = {
    'MOVE_LEFT': [pygame.K_LEFT, pygame.K_a],
    'MOVE_RIGHT': [pygame.K_RIGHT, pygame.K_d],
    'JUMP': [pygame.K_SPACE],
    'INTERACT': [pygame.K_e],
    'PAUSE': [pygame.K_ESCAPE]
}

GRAVITY = 0.9
JUMP_FORCE = -18
MOVEMENT_SPEED = 5
FRICTION = 0.9

class TileType(Enum):
    GROUND = 1
    WALL = 2
    PLATFORM = 3
    SPIKE = 4
    LADDER = 5

class GameState(Enum):
    MAIN_MENU = 1
    RUNNING = 2
    PAUSED = 3
    GAME_OVER = 4
    INVENTORY = 5

class Direction(Enum):
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4