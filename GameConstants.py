import numpy as np

SCREEN_WIDTH = 1600
SCREEN_HEIGHT = 1000

# Below are the maximum x and y distances from the center of the screen in which a level transition will not trigger

MIN_X = 50
MIN_Y = 50
MAX_X = SCREEN_WIDTH - 50
MAX_Y = SCREEN_HEIGHT - 50

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