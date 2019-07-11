from Entity import Entity
from Bullet import Bullet
import GameConstants


class Tank(Entity):
    def __init__(self, role, sides, radius, pos, max_health, max_damage, max_velocity):
        super().__init__(role=role, sides=sides, radius=radius, pos=pos)
        self.max_health = max_health
        self.max_damage = max_damage
        self.max_velocity = max_velocity
        self.bullets = []
        self.cannon_angle = (-1, -1)

    def draw(self, renderer):
        renderer.draw_polygon(self)
        renderer.draw_cannon(self.pos, self.cannon_angle)
        for bullet in self.bullets:
            bullet.draw(renderer)

    def update(self, dt):
        for bullet in self.bullets:
            if 0 < bullet.pos[0] < GameConstants.SCREEN_WIDTH and 0 < bullet.pos[1] < GameConstants.SCREEN_HEIGHT:
                bullet.update(dt)
            else:
                self.bullets.remove(bullet)
                del bullet

    def on_click(self):
        self.bullets.append(Bullet(self.pos, self.cannon_angle))
