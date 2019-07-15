import numpy as np

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 800

COLORS = {"RED": np.array([1, 0, 0], dtype=np.float32),
          "BLACK": np.array([0, 0, 0], dtype=np.float32),
          "GREEN": np.array([0, 1, 0], dtype=np.float32),
          "BLUE": np.array([0, 0, 1], dtype=np.float32),
         }

HEALTH_BAR_COORDINATES = [0, -25, 0, -35, 60, -35, 60, -25]
