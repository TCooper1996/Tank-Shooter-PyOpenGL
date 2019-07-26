from random import uniform

import numpy as np

import GameConstants
from Polygon import Polygon, EntityType


class Entity(Polygon):
    game = None

    def __init__(self, entity_type, pos, dimensions=None, rotation=0):
        super().__init__(entity_type, pos, dimensions=dimensions, rotation=rotation)
        self.collision_checked = False
        self.collisions = []
        self.active = True

    def draw(self, renderer):
        raise NotImplementedError

    def update(self, dt):
        raise NotImplementedError


class Combatant(Entity):
    def __init__(self, entity_type, pos, rotation, max_damage, max_health):
        super(Combatant, self).__init__(entity_type, pos, None, rotation)
        self.bullets = []
        self.cannon_angle = None
        self.max_health = max_health
        self.health = self.max_health
        self.max_damage = max_damage
        self.damage = self.max_damage
        self.max_velocity = None
        self.is_friendly = None

    def draw(self, renderer):
        for bullet in self.bullets:
            bullet.draw(renderer)
        if self.health > 0:
            renderer.draw_polygon(self)
        if self.cannon_angle is None:
            pass  # raise ValueError("Cannon angle has no been set.")
        else:
            renderer.draw_cannon(self.pos, self.cannon_angle)

    def update(self, dt):
        self.update_bullets(dt)
        self.handle_collisions()
        self.check_status()

    def update_bullets(self, dt):
        for bullet in self.bullets:
            if bullet.active:
                bullet.update(dt)
            else:
                self.bullets.remove(bullet)
                del bullet

    def handle_collisions(self):
        for bullet in self.collisions:
            if bullet.active:
                self.health -= bullet.damage
                bullet.active = False
                self.collisions.remove(bullet)

    def check_status(self):
        if self.health <= 0:
            self.active = False


class Tank(Combatant):
    def __init__(self, pos, max_health, max_damage, max_velocity, rotation=0):
        super().__init__(EntityType.Tank, pos=pos, rotation=rotation, max_health=max_health, max_damage=max_damage)
        self.has_center_vertex = True
        self.max_health = max_health
        self.health = self.max_health
        self.max_damage = max_damage
        self.damage = max_damage
        self.max_velocity = max_velocity
        self.is_friendly = True

    def draw(self, renderer):
        super().draw(renderer)

    def update(self, dt):
        super().update(dt)
        mouse_x, mouse_y = Entity.game.mouse_position
        x_distance = mouse_x - self.pos[0]
        y_distance = mouse_y - self.pos[1]
        self.cannon_angle = np.arctan2(y_distance, x_distance)

    def on_click(self):
        self.bullets.append(Bullet(self.pos, self.cannon_angle, True, self.damage))


class Turret(Combatant):
    def __init__(self, pos):
        super().__init__(EntityType.Turret, pos=pos, max_health=100, max_damage=10, rotation=0)
        self.has_center_vertex = True
        self.max_health = 100
        self.health = self.max_health
        self.max_damage = 10
        self.is_friendly = False
        self.time_since_attack = 0

    def draw(self, renderer):
        if self.health > 0:
            super().draw(renderer)

    def update(self, dt):
        # Super().update() regardless of health to allow bullets to finish life cycle before destroying turret
        super().update(dt)
        if self.health > 0:
            self.time_since_attack += dt
            # Set cannon angle
            player_pos = self.game.get_player().pos
            x_distance = player_pos[0] - self.pos[0]
            y_distance = player_pos[1] - self.pos[1]
            self.cannon_angle = np.arctan2(y_distance, x_distance)
            # Attack
            self.attack()

    def attack(self):
        if self.time_since_attack >= 5:
            self.time_since_attack = 0
            for i in range(5):
                bullet_direction = self.cannon_angle + uniform(-np.pi/8, np.pi/8)
                self.bullets.append(Bullet(self.pos, bullet_direction, False, self.damage))


class Bullet(Entity):
    def __init__(self, pos, angle, is_friendly, damage):
        super().__init__(EntityType.Bullet, pos=pos, dimensions=None)
        self.has_center_vertex = True
        self.angle = angle
        self.is_friendly = is_friendly
        self.velocity = 700
        self.damage = damage

    def draw(self, renderer):
        renderer.draw_polygon(self)

    def update(self, dt):
        # Update movement
        next_x = np.cos(self.angle) * self.velocity * dt
        next_y = np.sin(self.angle) * self.velocity * dt
        new_vertices = self.calc_final_vertices(next_x, next_y)
        self.set_vertices(new_vertices)
        self.add_position(next_x, next_y)
        self.active = 0 < self.pos[0] < GameConstants.SCREEN_WIDTH and 0 < self.pos[1] < GameConstants.SCREEN_HEIGHT


class Barrier(Entity):
    def __init__(self, pos, dimensions, rotation):
        self.has_center_vertex = False
        self.width = dimensions[0]
        self.height = dimensions[1]
        super().__init__(EntityType.Barrier, pos, dimensions, rotation)
        self.rotation = rotation
        self.init_buffer_data()
        self._vertex_value_array = self.calc_final_vertices()

    def draw(self, renderer):
        renderer.draw_polygon(self)

    def update(self, dt):
        for entity in self.collisions:
            if isinstance(entity, Bullet):
                entity.active = False
                self.collisions.remove(entity)

    def get_indices(self):
        return np.array([0, 1, 1, 2, 2, 3, 3, 0], dtype=np.uint32)

    def get_collision_vertices(self):
        return np.copy(self._vertex_value_array)


class MacGuffin(Entity):
    def __init__(self, pos):
        super().__init__(EntityType.MacGuffin, pos)
        self.pos = pos

    def update(self, dt):
        pass

    def draw(self, renderer):
        renderer.draw_polygon(self)