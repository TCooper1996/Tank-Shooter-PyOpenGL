from Entity import Entity


class Tank(Entity):
    def __init__(self, max_health, max_damage, max_velocity):
        super().__init__(3, 50, [300, 30])
        self.max_health = max_health
        self.max_damage = max_damage
        self.max_velocity = max_velocity

    def draw(self, renderer):
        super().draw(renderer)
