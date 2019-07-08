from cyglfw3 import *
import pyrr
import numpy as np
from ResourceManager import *
from Renderer import Renderer
from Tank import Tank


class Game:

    def __init__(self, width, height):
        self.Keys = [False] * 1024
        self.Width = width
        self.Height = height
        self.PLAYER_VELOCITY = 500
        self.player = Tank(100, 100, 5)
        self.entities = [self.player]
        self.keyLocked = False
        self.renderer = None

    def Init(self):
        ResourceManager.load_shader("vertex.glsl", "fragment.glsl", "sprite")
        projection = pyrr.matrix44.create_orthogonal_projection(float(0), float(self.Width), float(0),
                                                                float(self.Height), float(-1), float(1))
        ResourceManager.get_shader("sprite").use().set_integer("sprite", 0)
        ResourceManager.get_shader("sprite").set_matrix("projection", projection)
        self.renderer = Renderer(ResourceManager.get_shader("sprite"))

    def ProcessInput(self, dt):
        velocity = self.PLAYER_VELOCITY * dt
        next_x, next_y = 0, 0
        walk = self.Keys[KEY_W] != self.Keys[KEY_S]
        turn = self.Keys[KEY_A] != self.Keys[KEY_D]
        if walk or turn:
            turn_angle = float(0.1) if turn else 0
            if self.Keys[KEY_D]: turn_angle *= -1
            if self.Keys[KEY_S]: velocity *= -1
            if walk:
                next_x = np.cos(self.player.Rotation) * velocity
                next_y = np.sin(self.player.Rotation) * velocity

            new_vertices = self.player.calc_final_vertices(x_offset=next_x, y_offset=next_y, r_offset=turn_angle)
            collisions = [self.checkOverlap(new_vertices, other.get_vertices())
                          for other in self.entities if self.player != other]
            if not any(collisions):
                self.player.set_vertices(new_vertices)
                self.player.add_position(next_x, next_y, turn_angle)

        if self.Keys[KEY_SPACE] and not self.keyLocked:
            self.player.set_color("RED")
            self.keyLocked = True
        if not self.Keys[KEY_SPACE]:
            self.keyLocked = False

    def update(self, dt):
        self.DoCollisionsSAT()

    def render(self):
        for g in self.entities:
            g.draw(self.renderer)

    # Returns bool defined by collision
    def checkOverlap(self, vertices1, vertices2):
        # Closure returns list of normalized np vectors
        def obtainAxes(vertices):
            vertSize = len(vertices)
            axes = []
            #  Compare every pair of vertices
            for i in range(0, vertSize, 2):
                # Get first vector using slice, + 2 due to exclusive upper bound
                vec1 = np.array(vertices[i:i+2])
                # Slicing is avoided here due to cases like vertices[6:0]
                vec2 = np.array([vertices[(i + 2) % vertSize], vertices[(i + 3) % vertSize]])
                # Subtract vectors to get their edge
                edge = vec1 - vec2
                # Get orthogonal vector
                edge = [edge[1], -edge[0]]
                # Normalize
                edge = edge / np.linalg.norm(edge)
                axes.append(edge)
            return axes

        # Closure returns a tuple of the min and max values projected on the axis
        def projectVertices(axis, vertices):
            min_ = np.dot(axis, vertices[:2])
            max_ = min_
            for i in range(0, len(vertices), 2):
                product = np.dot(axis, vertices[i:i + 2])
                if product < min_:
                    min_ = product
                elif product > max_:
                    max_ = product
            return min_, max_
        #  This is the main code for checkOverlap
        #  The final (origin) vertex must be removed
        # TODO: make sure this does not mutate original list
        vertices1 = vertices1[:-2]
        vertices2 = vertices2[:-2]
        axes1 = obtainAxes(vertices1)
        axes2 = obtainAxes(vertices2)
        for axis in axes1 + axes2:
            min1, max1 = projectVertices(axis, vertices1)
            min2, max2 = projectVertices(axis, vertices2)

            if not (min2 <= min1 <= max2 or min2 <= max1 <= max2
                    or min1 <= min2 <= max1 or min1 <= max2 <= max1):
                return False
        return True

    def DoCollisionsSAT(self):
        for polygon in self.entities:
            if polygon != self.player:
                polygon.set_color("BLACK")
            else:
                polygon.set_color("RED")
        for i in range(len(self.entities)):
            polygon1 = self.entities[i]
            polygon2 = self.entities[(i + 1) % len(self.entities)]
            if polygon1 != polygon2 and self.checkOverlap(polygon1.get_vertices(), polygon2.get_vertices()):
                polygon1.set_color("GREEN")
                polygon2.set_color("GREEN")
