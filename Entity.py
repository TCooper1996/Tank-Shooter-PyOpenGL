from abc import ABC, abstractmethod
from collections import namedtuple
import GameConstants
import pyrr
import numpy as np
import enum


class Role(enum.Enum):
    PROJECTILE = 0,
    ACTOR = 1,
    BARRIER = 2,


bufferData = namedtuple("bufferData", "vertexBuffer indexBuffer")


class Entity(ABC):
    basis_arrays = {}
    game_state ={"player_position": None,
                 "mouse_position": None,
                 "entities": []}

    def __init__(self, role, sides, radius, pos):
        self.role = role
        self.sides = sides
        self.radius = radius
        self.pos = pos
        self.color = GameConstants.COLORS["BLACK"]
        self.Rotation = 0
        if role == Role.ACTOR:
            self.bullets = []
            self.cannon_angle = None
            self.max_health = None
            self.max_damage = None
            self.max_velocity = None
        if sides not in Entity.basis_arrays:
            self.init_buffer_data()
        self.__vertex_value_array = self.calc_final_vertices()
        super().__init__()

    @abstractmethod
    def draw(self, renderer):
        raise NotImplementedError

    @abstractmethod
    def update(self, dt):
        raise NotImplementedError

    def set_color(self, color):
        self.color = GameConstants.COLORS[color]

    def init_buffer_data(self):
        # Define size of vertex and index array
        # VertexArraySize is initially self.sides * 2 + 2 and filled with 2 coordinates.
        # The final result is a flat list of x y values
        num_of_vertex_values = self.sides * 2 + 2
        num_of_indices = self.sides * 2 + 2
        # Create vertex array
        funcs = {0: np.cos, 1: np.sin}
        vertices = [self.radius * funcs[i % 2](2 * np.pi * (i // 2) / self.sides)
                    for i in range(num_of_vertex_values)]
        vertices[-2], vertices[-1] = 0, 0  # Set last vertex as origin
        # Create index array
        indices = np.array([(i + 1) // 2 for i in range(num_of_indices)], dtype=np.uint32)
        # Connect last vertex to origin, then connect last vertex to first real vertex
        indices[-4], indices[-3], indices[-2], indices[-1] = (num_of_indices // 2 - 2), 0, 0, (num_of_indices // 2) - 1
        Entity.basis_arrays[self.sides] = bufferData(vertices, indices)

    # This method takes the basis vertices, adds the z dimension (necessary for transformation math), performs the trans
    # /formation, and then removes the z dimension.
    def calc_final_vertices(self, x_offset=0, y_offset=0, r_offset=0):
        model_tran = pyrr.matrix44.create_from_translation(np.array([self.pos[0] + x_offset, self.pos[1] + y_offset, 0],
                                                                    dtype=np.float32))
        model_rot = pyrr.matrix44.create_from_axis_rotation(np.array([0, 0, 1], dtype=np.float32),
                                                            self.Rotation + r_offset)
        model_final = pyrr.matrix44.multiply(model_rot, model_tran)

        #  Copy basis arrays (which are actually lists) to local var to avoid mutation.
        vertex_value_list = Entity.basis_arrays[self.sides].vertexBuffer.copy()
        #  Add 0 to every third position to add a z axis
        for i in range(len(vertex_value_list) // 2):  # VertexArraySize // 2 because that is our number of vertices
            vertex_value_list.insert(i * 3 + 2, 0)
        vertex_value_array = np.array(vertex_value_list, dtype=np.float32)
        #  Resize array so that each item in vertex_value_array is a vec3
        vertex_value_array = np.resize(vertex_value_array, (len(vertex_value_array) // 3, 3))
        #  Apply transformation matrix on each vector
        vertex_value_array = [pyrr.matrix44.apply_to_vector(model_final, vertex_value_array[i])
                              for i in range(self.sides + 1)]
        #  Remove the dummy z values
        vertex_value_array = [vector[0:2] for vector in vertex_value_array]
        #  Flatten list of arrays and return
        return np.array(vertex_value_array).flatten()

    def get_vertices(self):
        return self.__vertex_value_array

    def set_vertices(self, vertices):
        self.__vertex_value_array = vertices

    def add_position(self, x, y, a=0):
        self.pos = (self.pos[0] + x, self.pos[1] + y)
        self.Rotation += a

    def update_bullets(self, dt):
        for bullet in self.bullets:
            if 0 < bullet.pos[0] < GameConstants.SCREEN_WIDTH and 0 < bullet.pos[1] < GameConstants.SCREEN_HEIGHT:
                bullet.update(dt)
            else:
                self.bullets.remove(bullet)
                del bullet
