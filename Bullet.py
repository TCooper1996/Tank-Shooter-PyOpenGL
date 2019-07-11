from Entity import Entity, Role
import numpy as np

super_params = {
    "role": Role.PROJECTILE,
    "sides": 8,
    "radius": 8,
    "pos": [],
}


class Bullet(Entity):
    def __init__(self, pos, angle):
        super_params["pos"] = pos
        super().__init__(**super_params)
        self.angle = angle
        self.velocity = 500

    def draw(self, renderer):
        renderer.draw_polygon(self)

    def update(self, dt):
        next_x = np.cos(self.angle) * self.velocity * dt
        next_y = np.sin(self.angle) * self.velocity * dt

        new_verticies = self.calc_final_vertices(next_x, next_y)
        self.set_vertices(new_verticies)
        self.add_position(next_x, next_y)

