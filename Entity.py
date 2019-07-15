import enum
from abc import ABC, abstractmethod
from random import uniform

import numpy as np
import pyrr

import GameConstants


class Role(enum.Enum):
    PROJECTILE = 0,
    ACTOR = 1,
    BARRIER = 2,


class Entity(ABC):
    game = None

    def __init__(self, role, sides, radius, pos):
        self.role = role
        self.sides = sides
        self.radius = radius
        self.pos = pos
        self.color = GameConstants.COLORS["BLACK"]
        self.Rotation = 0
        self.collision_checked = False
        self.collisions = []
        self.active = True
        self.basis_array = []
        self.__index_array = []
        self.init_buffer_data()
        self.__vertex_value_array = self.calc_final_vertices()
        super().__init__()

    @abstractmethod
    def draw(self, renderer):
        raise NotImplementedError

    @abstractmethod
    def update(self):
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
        self.basis_array = vertices
        self.__index_array = indices

    # This method takes the basis vertices, adds the z dimension (necessary for transformation math), performs the trans
    # /formation, and then removes the z dimension.
    def calc_final_vertices(self, x_offset=0, y_offset=0, r_offset=0):
        model_tran = pyrr.matrix44.create_from_translation(np.array([self.pos[0] + x_offset, self.pos[1] + y_offset, 0],
                                                                    dtype=np.float32))
        model_rot = pyrr.matrix44.create_from_axis_rotation(np.array([0, 0, 1], dtype=np.float32),
                                                            self.Rotation + r_offset)
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
                              for i in range(self.sides + 1)]
        #  Remove the dummy z values
        vertex_value_array = [vector[0:2] for vector in vertex_value_array]
        #  Flatten list of arrays and return
        return np.array(vertex_value_array).flatten()

    def get_vertices(self):
        return np.copy(self.__vertex_value_array)

    def set_vertices(self, vertices):
        self.__vertex_value_array = np.copy(vertices)

    def get_indices(self):
        return np.copy(self.__index_array)

    def add_position(self, x, y, a=0):
        self.pos = (self.pos[0] + x, self.pos[1] + y)
        self.Rotation += a


class Combatant(Entity):
    def __init__(self, role, sides, radius, pos):
        super(Combatant, self).__init__(role, sides, radius, pos)
        self.bullets = []
        self.cannon_angle = None
        self.max_health = None
        self.health = self.max_health
        self.max_damage = None
        self.damage = self.max_damage
        self.max_velocity = None

    def draw(self, renderer):
        renderer.draw_polygon(self)
        renderer.draw_cannon(self.pos, self.cannon_angle)
        for bullet in self.bullets:
            bullet.draw(renderer)

    def update(self):
        self.update_bullets()
        self.handle_collisions()
        self.check_status()

    def update_bullets(self):
        for bullet in self.bullets:
            if 0 < bullet.pos[0] < GameConstants.SCREEN_WIDTH and 0 < bullet.pos[1] < GameConstants.SCREEN_HEIGHT and bullet.active:
                bullet.update()
            else:
                self.bullets.remove(bullet)
                del bullet

    def handle_collisions(self):
        for bullet in self.collisions:
            if bullet.active:
                self.health -= 10
                bullet.active = False
                self.collisions.remove(bullet)

    def check_status(self):
        if self.health <= 0:
            self.active = False


class Tank(Combatant):
    def __init__(self, radius, pos, max_health, max_damage, max_velocity):
        super().__init__(role=Role.ACTOR, sides=3, radius=radius, pos=pos)
        self.max_health = max_health
        self.health = self.max_health
        self.max_damage = max_damage
        self.max_velocity = max_velocity
        self.is_friendly = True

    def draw(self, renderer):
        super().draw(renderer)

    def update(self):
        super().update()
        mouse_x, mouse_y = Entity.game.mouse_position
        x_distance = mouse_x - self.pos[0]
        y_distance = mouse_y - self.pos[1]
        self.cannon_angle = np.arctan2(y_distance, x_distance)

    def on_click(self):
        self.bullets.append(Bullet(self.pos, self.cannon_angle, True))


class Turret(Combatant):
    def __init__(self, radius, pos, max_health, max_damage, max_velocity):
        super().__init__(role=Role.ACTOR, sides=10, radius=radius, pos=pos)
        self.max_health = max_health
        self.health = self.max_health
        self.max_damage = max_damage
        self.max_velocity = max_velocity
        self.is_friendly = False
        self.ticks_since_attack = 0

    def draw(self, renderer):
        super().draw(renderer)

    def update(self):
        super().update()
        self.ticks_since_attack += 1
        # Set cannon angle
        player_pos = self.game.game_state["player_position"]
        x_distance = player_pos[0] - self.pos[0]
        y_distance = player_pos[1] - self.pos[1]
        self.cannon_angle = np.arctan2(y_distance, x_distance)
        # Attack
        self.attack()

    def attack(self):
        if self.ticks_since_attack >= 200:
            self.ticks_since_attack = 0
            for i in range(5):
                bullet_direction = self.cannon_angle + uniform(-np.pi/8, np.pi/8)
                self.bullets.append(Bullet(self.pos, bullet_direction, False))


class Bullet(Entity):
    def __init__(self, pos, angle, is_friendly):
        super().__init__(role=Role.PROJECTILE, sides=8, radius=8, pos=pos)
        self.angle = angle
        self.is_friendly = is_friendly
        self.velocity = 10

    def draw(self, renderer):
        renderer.draw_polygon(self)

    def update(self):
        # Update movement
        next_x = np.cos(self.angle) * self.velocity
        next_y = np.sin(self.angle) * self.velocity
        new_vertices = self.calc_final_vertices(next_x, next_y)
        self.set_vertices(new_vertices)
        self.add_position(next_x, next_y)
