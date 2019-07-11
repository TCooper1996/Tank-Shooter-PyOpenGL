from Entity import Entity, Role
from Bullet import Bullet
import numpy as np


class Tank(Entity):
    def __init__(self, radius, pos, max_health, max_damage, max_velocity):
        super().__init__(role=Role.ACTOR, sides=3, radius=radius, pos=pos)
        self.max_health = max_health
        self.max_damage = max_damage
        self.max_velocity = max_velocity

    def draw(self, renderer):
        renderer.draw_polygon(self)
        renderer.draw_cannon(self.pos, self.cannon_angle)
        for bullet in self.bullets:
            bullet.draw(renderer)

    def update(self, dt):
        mouse_x, mouse_y = Entity.game_state["mouse_position"]
        x_distance = mouse_x - self.pos[0]
        y_distance = mouse_y - self.pos[1]
        self.cannon_angle = np.arctan2(y_distance, x_distance)
        self.update_bullets(dt)

    def on_click(self):
        self.bullets.append(Bullet(self.pos, self.cannon_angle))
