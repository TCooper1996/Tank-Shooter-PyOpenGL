import numpy as np

SCREEN_WIDTH = 1600
SCREEN_HEIGHT = 1000
SCREEN_MARGIN = 150
EDITOR_TILE = 50
MINI_TILE = 20

MAX_ROOMS = 30

# Below are the maximum x and y distances from the center of the screen in which a level transition will not trigger

MIN_X = 50
MIN_Y = 50
MAXS = [
    (SCREEN_WIDTH - 120)/2,
    (SCREEN_HEIGHT - 120)/2
]

MAX_MAP_WIDTH = 5
MAX_MAP_HEIGHT = 5

# X or Y Distance from the origin that the player will be spawned in order of LEFT, DOWN, RIGHT, UP
SPAWN_LIST = [
    150,
    150,
    1450,
    850,
    ]

COLORS = {"RED": np.array([1, 0, 0], dtype=np.float32),
          "BLACK": np.array([0, 0, 0], dtype=np.float32),
          "GREEN": np.array([0, 1, 0], dtype=np.float32),
          "BLUE": np.array([0, 0, 1], dtype=np.float32),
          }

HEALTH_BAR_COORDINATES = [0, -25, 0, -35, 60, -35, 60, -25]

TILE_WIDTH = 50
TILE_HEIGHT = 50