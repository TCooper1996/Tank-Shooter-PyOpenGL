import json

from cyglfw3 import *

import Interface
import WorldMap
from Entity import *
from GameConstants import *


class Game(Interface.Interface):
    game_state = {"entities": [], "exits": {}, "paused": False, "level": (0, 0), "world": WorldMap.World}

    def __init__(self, width, height):
        super().__init__(width, height)
        self.player = Tank(pos=[300, 300], max_health=100, max_damage=50, max_velocity=800)
        Game.game_state["entities"].append(self.player)
        Entity.game = self

    def load_resources(self):
        super().load_resources()
        Game.game_state["world"] = generate_world(GameConstants.MAX_ROOMS)
        load_level(-1)

    def process_input(self, dt):
        world = Game.game_state["world"]
        level = world[Game.game_state["level"]]
        funcs = (np.cos, np.sin)

        for dir in range(4):
            dist = (np.array(self.player.get_position()) - np.array([SCREEN_WIDTH/2, SCREEN_HEIGHT/2]))[dir % 2]
            if dist * funcs[dir % 2](dir*np.pi/2) > MAXS[dir % 2] and level.get_exit(dir):
                load_level(dir)
                self.player.set_position(dir % 2, SPAWN_LIST[dir])
                break


        velocity = self.player.max_velocity * dt
        next_x, next_y = 0, 0
        walk = self.Keys[KEY_W] != self.Keys[KEY_S]
        turn = self.Keys[KEY_A] != self.Keys[KEY_D]
        if walk or turn:
            turn_angle = float(3) * dt if turn else 0
            if self.Keys[KEY_D]:
                turn_angle *= -1
            if self.Keys[KEY_S]:
                velocity *= -1
            if walk:
                next_x = np.cos(self.player.rotation) * velocity
                next_y = np.sin(self.player.rotation) * velocity

            new_vertices = self.player.calc_final_vertices(x_offset=next_x, y_offset=next_y, r_offset=turn_angle)
            collisions = [Interface.check_overlap(new_vertices, other.get_collision_vertices())
                          for other in Game.game_state["entities"] if self.player != other]
            wall_collision = False
            for f in range(0, len(new_vertices), 2):
                if not 0 <= new_vertices[f] <= GameConstants.SCREEN_WIDTH or \
                        not 0 <= new_vertices[f + 1] <= GameConstants.SCREEN_HEIGHT:
                    wall_collision = True
            if not any(collisions) and not wall_collision:
                self.player.set_vertices(new_vertices)
                self.player.add_position(next_x, next_y, turn_angle)

        if self.Keys[KEY_SPACE] and not self.key_locked:
            self.game_state["paused"] = not self.game_state["paused"]
            self.key_locked = True
        if not self.Keys[KEY_SPACE]:
            self.key_locked = False

        if self.mouse_buttons[MOUSE_BUTTON_LEFT] and not self.mouse_locked:
            self.mouse_locked = True
            self.player.on_click()
        if not self.mouse_buttons[MOUSE_BUTTON_LEFT]:
            self.mouse_locked = False

    def update(self, mouse_position, dt):
        # Only update if game is not paused
        if not Game.game_state["paused"]:
            # Check player status
            if not self.player.active:
                self.active = False
            # Get correct mouse position
            self.mouse_position = (mouse_position[0], self.height - mouse_position[1])
            Game.game_state["player_position"] = self.player.pos
            handle_collisions()
            for entity in Game.game_state["entities"]:
                if entity.active:
                    entity.update(dt)
                else:
                    Game.game_state["entities"].remove(entity)
                    del entity

    def render(self):
        if Game.game_state["paused"]:
            self.renderer.draw_map(Game.game_state["world"], Game.game_state["level"])
        else:
            self.renderer.draw_map(Game.game_state["world"], Game.game_state["level"], True)
            for g in Game.game_state["entities"]:
                g.draw(self.renderer)

    def get_player(self):
        return self.player


def generate_world(max_rooms):
    world = WorldMap.World(max_rooms, "levels")
    return world


# Direction param determines which level to load, the one of the right, top, left, or bottom.
def load_level(direction):
    # Make sure the player is the first object created
    # Remove all current entities excepted player
    for entity in Game.game_state["entities"][1:]:
        entity.active = False

    # Clear player bullets as well
    for bullet in Game.game_state["entities"][0].bullets:
        bullet.active = False
        del bullet

    level_list = list(Game.game_state["level"])
    if direction == 0:
        level_list[0] += 1
    elif direction == 1:
        level_list[1] += 1
    elif direction == 2:
        level_list[0] -= 1
    elif direction == 3:
        level_list[1] -= 1
    elif direction == -1:
        level_list = [0, 0]

    Game.game_state["level"] = tuple(level_list)
    room = Game.game_state["world"][tuple(level_list)]
    with open("levels/" + room.get_design()) as level:
        level = json.load(level)
        Game.game_state["exits"] = room.get_exits()
        entities = level["entities"]
        for entity in entities:
            class_name = entity[0]
            if class_name == "Turret":
                entity_object = Turret(*entity[1:])
            elif class_name == "Barrier":
                entity_object = Barrier(*entity[1:])
            elif class_name == "MacGuffin":
                entity_object = MacGuffin(*entity[1:])
            else:
                raise ValueError("Unknown class: {0}".format(class_name))
            Game.game_state["entities"].append(entity_object)


# TODO: Optimize handle_collisions; this looks ugly
def handle_collisions():
    for actor in Game.game_state["entities"]:
        if isinstance(actor, (Combatant, Barrier)):
            # Grab all projectiles in game. all_projectiles will be a list of lists
            all_bullets = [entity.bullets for entity in Game.game_state["entities"] if isinstance(entity, Combatant)]
            # Filter out all bullets friendly to the current actor and flatten list.
            if isinstance(actor, Combatant):
                hostile_bullets = [b for bs in all_bullets for b in bs if b.is_friendly != actor.is_friendly]
            # If the object is not a combatant, then all bullets will be tested against it.
            else:
                hostile_bullets = [b for bs in all_bullets for b in bs]
            for projectile in hostile_bullets:
                if Interface.check_overlap(actor.get_collision_vertices(), projectile.get_collision_vertices()):
                    actor.collisions.append(projectile)
