from cyglfw3 import *

from Entity import *
from Renderer import Renderer
from ResourceManager import *


class Game:
    game_state = {}

    def __init__(self, width, height):
        self.player_values = {
            "radius": 25,
            "pos": [300, 300],
            "max_health": 100,
            "max_damage": 100,
            "max_velocity": 300
        }
        self.Keys = [False] * 1024
        self.mouse_buttons = [False] * 3
        self.Width = width
        self.Height = height
        self.player = Tank(**self.player_values)
        self.enemy = Turret(25, [600, 500], 100, 100, 300)
        Game.game_state["entities"] = [self.player, self.enemy]
        self.keyLocked = False
        self.mouse_locked = False
        self.renderer = None
        self.mouse_position = (None, None)
        Entity.game = self

    def load_resources(self):
        ResourceManager.load_shader("vertex.glsl", "fragment.glsl", "sprite")
        projection = pyrr.matrix44.create_orthogonal_projection(float(0), float(self.Width), float(0),
                                                                float(self.Height), float(-1), float(1))
        ResourceManager.get_shader("sprite").use().set_integer("sprite", 0)
        ResourceManager.get_shader("sprite").set_matrix("projection", projection)
        self.renderer = Renderer(ResourceManager.get_shader("sprite"))

    def process_input(self, dt):
        velocity = self.player_values["max_velocity"] * dt
        next_x, next_y = 0, 0
        walk = self.Keys[KEY_W] != self.Keys[KEY_S]
        turn = self.Keys[KEY_A] != self.Keys[KEY_D]
        if walk or turn:
            turn_angle = float(0.1) if turn else 0
            if self.Keys[KEY_D]:
                turn_angle *= -1
            if self.Keys[KEY_S]:
                velocity *= -1
            if walk:
                next_x = np.cos(self.player.Rotation) * velocity
                next_y = np.sin(self.player.Rotation) * velocity

            new_vertices = self.player.calc_final_vertices(x_offset=next_x, y_offset=next_y, r_offset=turn_angle)
            collisions = [check_overlap(new_vertices, other.get_vertices())
                          for other in Game.game_state["entities"] if self.player != other]
            if not any(collisions):
                self.player.set_vertices(new_vertices)
                self.player.add_position(next_x, next_y, turn_angle)

        if self.Keys[KEY_SPACE] and not self.keyLocked:
            self.player.set_color("RED")
            print(self.renderer.mouse_position)
            self.keyLocked = True
        if not self.Keys[KEY_SPACE]:
            self.keyLocked = False

        if self.mouse_buttons[MOUSE_BUTTON_LEFT] and not self.mouse_locked:
            self.mouse_locked = True
            self.player.on_click()
        if not self.mouse_buttons[MOUSE_BUTTON_LEFT]:
            self.mouse_locked = False

    def update(self, dt, mouse_position):
        # Get correct mouse position
        self.mouse_position = (mouse_position[0], self.Height - mouse_position[1])
        Game.game_state["player_position"] = self.player.pos
        handle_collisions()
        for entity in Game.game_state["entities"]:
            if entity.active:
                entity.update(dt)
            else:
                Game.game_state["entities"].remove(entity)

    def render(self):
        for g in Game.game_state["entities"]:
            g.draw(self.renderer)

    def get_mouse(self):
        return self.mouse_position


# TODO: Optimize handle_collisions; this looks ugly
def handle_collisions():
    for actor in Game.game_state["entities"]:
        # Grab all projectiles in game. all_projectiles will be a list of lists
        all_bullets = [entity.bullets for entity in Game.game_state["entities"] if entity.role is Role.ACTOR]
        # Filter out all bullets friendly to the current actor and flatten list.
        hostile_bullets = [bullet for bullets in all_bullets for bullet in bullets if bullet.is_friendly != actor.is_friendly]
        for projectile in hostile_bullets:
            if check_overlap(actor.get_vertices(), projectile.get_vertices()):
                actor.collisions.append(projectile)


# Returns bool defined by collision
def check_overlap(vertices1, vertices2):
    # Closure returns list of normalized np vectors
    def obtain_axes(vertices):
        vert_size = len(vertices)
        axes = []
        #  Compare every pair of vertices
        for i in range(0, vert_size, 2):
            # Get first vector using slice, + 2 due to exclusive upper bound
            vec1 = np.array(vertices[i:i + 2])
            # Slicing is avoided here due to cases like vertices[6:0]
            vec2 = np.array([vertices[(i + 2) % vert_size], vertices[(i + 3) % vert_size]])
            # Subtract vectors to get their edge
            edge = vec1 - vec2
            # Get orthogonal vector
            edge = [edge[1], -edge[0]]
            # Normalize
            edge = edge / np.linalg.norm(edge)
            axes.append(edge)
        return axes

    # Closure returns a tuple of the min and max values projected on the axis
    def project_vertices(axis_, vertices):
        min_ = np.dot(axis_, vertices[:2])
        max_ = min_
        for i in range(0, len(vertices), 2):
            product = np.dot(axis_, vertices[i:i + 2])
            if product < min_:
                min_ = product
            elif product > max_:
                max_ = product
        return min_, max_

    #  This is the main code for checkOverlap
    #  The final (origin) vertex must be removed
    vertices1 = vertices1[:-2]
    vertices2 = vertices2[:-2]
    axes1 = obtain_axes(vertices1)
    axes2 = obtain_axes(vertices2)
    for axis in axes1 + axes2:
        min1, max1 = project_vertices(axis, vertices1)
        min2, max2 = project_vertices(axis, vertices2)

        if not (min2 <= min1 <= max2 or min2 <= max1 <= max2
                or min1 <= min2 <= max1 or min1 <= max2 <= max1):
            return False
    return True
