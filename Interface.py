import numpy as np
import pyrr

import GameConstants
from Renderer import Renderer
from ResourceManager import *


# This class defines the common functionality for any GUI in the app, namely, the actual game,
# and the level editor.


class Interface:
    def __init__(self, width, height):
        self.active = True
        self.Keys = [False] * 1024
        self.mouse_buttons = [False] * 3
        self.width = width
        self.height = height
        self.key_locked = False
        self.mouse_locked = False
        self.renderer = None
        self.mouse_position = (None, None)

    def load_resources(self):
        ResourceManager.load_shader("vertex.glsl", "fragment.glsl", "sprite")
        projection = pyrr.matrix44.create_orthogonal_projection(float(0), float(self.width), float(0),
                                                                float(self.height), float(-1), float(1))
        ResourceManager.get_shader("sprite").use().set_integer("sprite", 0)
        ResourceManager.get_shader("sprite").set_matrix("projection", projection)
        self.renderer = Renderer(ResourceManager.get_shader("sprite"))

    def process_input(self, dt):
        raise NotImplementedError("Illegal call to Interface.process_input(). This method must be overridden.")

    def render(self):
        raise NotImplementedError("Illegal call to Interface.render(). This method must be overridden.")

    def get_mouse(self):
        return self.mouse_position


# Returns bool defined by collision
def check_overlap(vertices1, vertices2):
    # Closure returns list of normalized np vectors
    def obtain_axes(vertices):
        vert_size = len(vertices)
        axes = []
        #  Compare every pair of vertices
        for k in range(0, vert_size, 2):
            # Get first vector using slice, + 2 due to exclusive upper bound
            vec1 = np.array(vertices[k:k + 2])
            # Slicing is avoided here due to cases like vertices[6:0]
            vec2 = np.array([vertices[(k + 2) % vert_size], vertices[(k + 3) % vert_size]])
            # Subtract vectors to get their edge
            edge = vec1 - vec2
            # Get orthogonal vector
            edge = np.array([edge[1], -edge[0]])
            # Normalize
            edge = edge / np.linalg.norm(edge)
            axes.append(edge)
        return axes

    # Closure returns a tuple of the min and max values projected on the axis
    def project_vertices(axis_, vertices):
        min_ = np.dot(axis_, vertices[:2])
        max_ = min_
        for j in range(0, len(vertices), 2):
            product = np.dot(axis_, vertices[j:j + 2])
            if product < min_:
                min_ = product
            elif product > max_:
                max_ = product
        return min_, max_

    # This is the main code for checkOverlap
    # First check if collision with wall
    for i in range(0, len(vertices1), 2):
        if not 0 <= vertices1[i] <= GameConstants.SCREEN_WIDTH:
            return True
        if not 0 <= vertices1[i + 1] <= GameConstants.SCREEN_HEIGHT:
            return True

    axes1 = obtain_axes(vertices1)
    axes2 = obtain_axes(vertices2)
    for axis in axes1 + axes2:
        min1, max1 = project_vertices(axis, vertices1)
        min2, max2 = project_vertices(axis, vertices2)

        if not (min2 <= min1 <= max2 or min2 <= max1 <= max2
                or min1 <= min2 <= max1 or min1 <= max2 <= max1):
            return False
    return True
