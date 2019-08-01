from enum import Enum

import numpy as np
import pyrr

import GameConstants


class EntityType(Enum):
    Turret = 0,
    Barrier = 1,
    Tank = 2,
    Bullet = 3,
    MacGuffin = 4,
    Sniper = 5


# Polygon class defines all functionality for an object to be drawn. Entity will inherit from this class to draw
# its objects. Polygon objects will be directly initialized when an object must be rendered, but does not need to
# respond to the environment, namely, when designing levels in the Editor.
class Polygon:
    def __init__(self, entity_type, pos, dimensions=None, rotation=0):
        self.entity_type = entity_type
        self.dimensions = dimensions
        self.pos = pos
        self.rotation = rotation
        if entity_type == EntityType.Turret:
            self.sides = 10
            self.radius = 25
        elif entity_type == EntityType.Barrier:
            self.sides = 4
            self.radius = None
        elif entity_type == EntityType.Tank:
            self.sides = 3
            self.radius = 25
        elif entity_type == EntityType.Bullet:
            self.sides = 8
            self.radius = 8
        elif entity_type == EntityType.MacGuffin:
            self.sides = 5
            self.radius = 25
        elif entity_type == EntityType.Sniper:
            self.sides = 6
            self.radius = 35
        else:
            ValueError("Unknown entity_type:%s" % entity_type)
        self.color = GameConstants.COLORS["BLACK"]
        self.basis_array = []
        self._index_array = []
        self.init_buffer_data()
        self._vertex_value_array = self.calc_final_vertices()

    def draw(self, renderer):
        renderer.draw_polygon(self)

    def set_color(self, color):
        self.color = GameConstants.COLORS[color]

    def init_buffer_data(self):
        if self.dimensions:
            vertices = [0, 0,
                        self.dimensions[0], 0,
                        self.dimensions[0], self.dimensions[1],
                        0, self.dimensions[1]
                        ]
            indices = [0, 1, 1, 2, 2, 3, 3, 0]

        else:
            # Define size of vertex and index array
            # VertexArraySize is initially self.sides * 2 + 2 and filled with 2 coordinates.
            # The final result is a flat list of x y values
            num_of_vertex_values = self.sides * 2
            # After draw_polygon is revamped, assure that indices are necessary for this class
            num_of_indices = self.sides * 2 + 2
            # Create vertex array
            funcs = {0: np.cos, 1: np.sin}
            vertices = [self.radius * funcs[i % 2](2 * np.pi * (i // 2) / self.sides)
                        for i in range(num_of_vertex_values)]
            # Create index array
            indices = [(i + 1) // 2 for i in range(num_of_indices)]
            # Connect last vertex to origin, then connect last vertex to first real vertex
            indices[-4], indices[-3], indices[-2], indices[-1] = \
                (num_of_indices // 2 - 2), 0, 0, (num_of_indices // 2) - 1
        self.basis_array = vertices
        self._index_array = np.array(indices, dtype=np.uint32)

    # This method takes the basis vertices, adds the z dimension (necessary for transformation math), performs the trans
    # /formation, and then removes the z dimension.
    def calc_final_vertices(self, x_offset=0, y_offset=0, r_offset=0):
        # If the object is a combatant, it will have a center vertex, which means the number of vertices it has will
        # be sides + 1. The condition below assures that only combatants and bullets have the extra vertex.

        model_tran = pyrr.matrix44.create_from_translation(np.array([self.pos[0] + x_offset, self.pos[1] + y_offset, 0],
                                                                    dtype=np.float32))
        model_rot = pyrr.matrix44.create_from_axis_rotation(np.array([0, 0, 1], dtype=np.float32),
                                                            self.rotation + r_offset)
        model_final = pyrr.matrix44.multiply(model_rot, model_tran)

        #  Copy basis arrays (which are actually lists) to local var to avoid mutation.
        vertex_value_list = self.basis_array.copy()
        #  Add 0 to every third position to add a z axis
        for i in range(len(vertex_value_list) // 2):  # VertexArraySize // 2 because that is our number of vertices
            vertex_value_list.insert(i * 3 + 2, 0)
        vertex_value_array = np.array(vertex_value_list, dtype=np.float32)
        #  Resize array so that each item in vertex_value_array is a vec3
        vertex_value_array = np.resize(vertex_value_array, (len(vertex_value_array) // 3, 3))
        #  Apply transformation matrix on each vector
        vertex_value_array = [pyrr.matrix44.apply_to_vector(model_final, vertex_value_array[i])
                              for i in range(self.sides)]
        #  Remove the dummy z values
        vertex_value_array = [vector[0:2] for vector in vertex_value_array]
        #  Flatten list of arrays and return
        return np.array(vertex_value_array).flatten()

    # Include all vertices. Do not exclude center vertex
    def get_render_vertices(self):
        return np.copy(self._vertex_value_array)

    # Exclude center vertex
    def get_collision_vertices(self):
        vertices = np.copy(self._vertex_value_array)
        return vertices

    def set_vertices(self, vertices):
        self._vertex_value_array = np.copy(vertices)

    def get_indices(self):
        return np.copy(self._index_array)

    def add_position(self, x=0, y=0, a=0):
        self.pos = (self.pos[0] + x, self.pos[1] + y)
        self.rotation += a
        self.rotation %= np.pi*2
        self._vertex_value_array = self.calc_final_vertices()

    def set_position(self, axis, val):
        x, y = self.pos
        if axis == 1:
            y = val
        elif axis == 0:
            x = val
        self.pos = (x, y)
        self._vertex_value_array = self.calc_final_vertices()

    def get_position(self):
        return np.array(self.pos)


