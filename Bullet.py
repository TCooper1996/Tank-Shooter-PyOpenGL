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
        super().__init__(role=Role.PROJECTILE, sides=8, radius=8, pos=pos)
        self.angle = angle
        self.velocity = 500

    def draw(self, renderer):
        renderer.draw_polygon(self)

    def update(self, dt):
        # Update movement
        next_x = np.cos(self.angle) * self.velocity * dt
        next_y = np.sin(self.angle) * self.velocity * dt
        new_vertices = self.calc_final_vertices(next_x, next_y)
        self.set_vertices(new_vertices)
        self.add_position(next_x, next_y)
