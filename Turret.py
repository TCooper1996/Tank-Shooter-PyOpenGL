from Entity import Entity, Role
import numpy as np


class Turret(Entity):
    def __init__(self, radius, pos, max_health, max_damage, max_velocity):
        super().__init__(role=Role.ACTOR, sides=10, radius=radius, pos=pos)
        self.max_health = max_health
        self.max_damage = max_damage
        self.max_velocity = max_velocity

    def draw(self, renderer):
        renderer.draw_polygon(self)
        renderer.draw_cannon(self.pos, self.cannon_angle)

    def update(self, dt):
        # Set cannon angle
        player_pos = Entity.game_state["player_position"]
        x_distance = player_pos[0] - self.pos[0]
        y_distance = player_pos[1] - self.pos[1]
        self.cannon_angle = np.arctan2(y_distance, x_distance)
        # Update bullets
        self.update_bullets(dt)
