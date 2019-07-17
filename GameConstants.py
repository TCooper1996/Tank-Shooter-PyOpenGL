import numpy as np

SCREEN_WIDTH = 1600
SCREEN_HEIGHT = 1000

SCREEN_MARGIN_UP = 950
SCREEN_MARGIN_RIGHT = 1550
SCREEN_MARGIN_DOWN = 50
SCREEN_MARGIN_LEFT = 50

SCREEN_SPAWN_UP = 850
SCREEN_SPAWN_RIGHT = 1450
SCREEN_SPAWN_DOWN = 150
SCREEN_SPAWN_LEFT = 150

COLORS = {"RED": np.array([1, 0, 0], dtype=np.float32),
          "BLACK": np.array([0, 0, 0], dtype=np.float32),
          "GREEN": np.array([0, 1, 0], dtype=np.float32),
          "BLUE": np.array([0, 0, 1], dtype=np.float32),
         }

HEALTH_BAR_COORDINATES = [0, -25, 0, -35, 60, -35, 60, -25]

