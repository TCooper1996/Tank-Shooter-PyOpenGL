from Entity import Entity


class Tank(Entity):
    def __init__(self, role, sides, radius, pos, max_health, max_damage, max_velocity):
        super().__init__(role=role, sides=sides, radius=radius, pos=pos)
        self.max_health = max_health
        self.max_damage = max_damage
        self.max_velocity = max_velocity

