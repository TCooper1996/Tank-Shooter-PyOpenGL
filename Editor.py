import json
from copy import deepcopy
from os import listdir

from cyglfw3 import *

from GameConstants import *
from Interface import Interface, check_overlap
from Polygon import Polygon, EntityType


class Editor(Interface):

    def __init__(self, width, height):
        super().__init__(width, height)
        turret = Polygon(EntityType.Turret, (25, 25))
        barrier = Polygon(EntityType.Barrier, (25, 25), [400, 100])
        sniper = Polygon(EntityType.Sniper, (35, 35))
        macguffin = Polygon(EntityType.MacGuffin, (25, 25))
        self.polygons = [turret, barrier, macguffin, sniper]
        self.selection_index = 0
        self.selected_polygon = deepcopy(self.polygons[self.selection_index])
        self.placed_polygons = []
        # hover_polygon is the polygon that the mouse is hovering over
        self.hover_polygon = None
        self.mouse_position = (-1, -1)
        # If show_selected is False, then the selected object will not be drawn
        self.show_selected = True
        # control_locked is used to prevent multi-pressing the control key. Similar to key_locked
        self.control_locked = False
        self.enter_locked = False
        self.current_level_index = 0
        self.load_level(0)

    def process_input(self, dt):

        if self.Keys[KEY_SPACE] and not self.key_locked:
            pass
        else:
            pass

        # Select next entity
        if self.Keys[KEY_E] and not self.key_locked:
            if self.selection_index == len(self.polygons) - 1:
                self.selection_index = 0
            else:
                self.selection_index += 1
            self.key_locked = True
            del self.selected_polygon
            self.selected_polygon = deepcopy(self.polygons[self.selection_index])
        # Select previous entity
        elif self.Keys[KEY_Q] and not self.key_locked:
            if self.selection_index == 0:
                self.selection_index = len(self.polygons) - 1
            else:
                self.selection_index -= 1
            self.key_locked = True
            del self.selected_polygon
            self.selected_polygon = deepcopy(self.polygons[self.selection_index])

        turn_speed = 0.01 if self.Keys[KEY_W] else 0.1
        # Rotate entity
        if self.Keys[KEY_D]:
            self.selected_polygon.add_position(a=turn_speed)
        elif self.Keys[KEY_A]:
            self.selected_polygon.add_position(a=-turn_speed)
        # Snap entity to nearest axis
        if self.Keys[KEY_S]:
            angle = self.selected_polygon.rotation
            right_angles = [np.pi/2*i for i in range(4)]
            # Get the distances from the current angle to the right angles
            angle_distances = [abs(angle - right_angle) for right_angle in right_angles]
            # Grab the index of the closest angle.
            angle_index = angle_distances.index(min(angle_distances))
            self.selected_polygon.rotation = right_angles[angle_index]

        if self.mouse_buttons[MOUSE_BUTTON_LEFT] and not self.mouse_locked:
            self.placed_polygons.append(deepcopy(self.selected_polygon))
            self.mouse_locked = True
        elif not self.mouse_buttons[MOUSE_BUTTON_LEFT]:
            self.mouse_locked = False

        if self.mouse_buttons[MOUSE_BUTTON_RIGHT]:
            if self.hover_polygon:
                self.placed_polygons.remove(self.hover_polygon)

        if self.Keys[KEY_LEFT_CONTROL] and not self.control_locked:
            self.show_selected = not self.show_selected
            self.control_locked = True
        elif not self.Keys[KEY_LEFT_CONTROL]:
            self.control_locked = False

        if self.Keys[KEY_ENTER] and not self.enter_locked:
            self.enter_locked = True
            self.serialize_level()
        elif not self.Keys[KEY_ENTER]:
            self.enter_locked = False

        if self.Keys[KEY_RIGHT] and not self.key_locked:
            self.load_next_level()
            self.key_locked = True

        if self.Keys[KEY_LEFT] and not self.key_locked:
            self.load_prev_level()
            self.key_locked = True

        if self.Keys[KEY_UP] and not self.key_locked:
            self.create_new_level()

        if not any(self.Keys):
            self.key_locked = False

    def update(self, mouse_position, dt, _time):
        self.hover_polygon = None
        self.mouse_position = (mouse_position[0], self.height - mouse_position[1])
        for p in self.placed_polygons:
            if check_overlap(self.mouse_as_polygon(), p.get_collision_vertices()):
                p.set_color("RED")
                self.hover_polygon = p
            else:
                p.set_color("BLACK")

        # Snap the selected polygon onto the grid, but keep it centered at the mouse position
        selected_x = (self.mouse_position[0] // EDITOR_TILE) * EDITOR_TILE + EDITOR_TILE/2
        selected_y = (self.mouse_position[1] // EDITOR_TILE) * EDITOR_TILE + EDITOR_TILE/2
        self.selected_polygon.set_position(0, selected_x)
        self.selected_polygon.set_position(1, selected_y)

    def render(self):
        self.renderer.draw_grid()
        self.renderer.draw_editor_controls()
        self.polygons[self.selection_index].draw(self.renderer)
        if self.show_selected:
            self.selected_polygon.draw(self.renderer)
        for p in self.placed_polygons:
            p.draw(self.renderer)

    def check_mouse_overlap(self, vertices):
        m_x, m_y = self.mouse_position
        xs = [vertices[i] for i in range(len(vertices)) if i % 2 == 0]
        ys = [vertices[i] for i in range(len(vertices)) if i % 2 == 1]
        min_x = min(xs)
        max_x = max(xs)
        min_y = min(ys)
        max_y = max(ys)

        if min_x <= m_x <= max_x and min_y <= m_y <= max_y:
            print("collision")

    def serialize_level(self):
        data = {}
        if 0 <= self.current_level_index < len(listdir("levels")):
            name = listdir("levels")[self.current_level_index][6:-5]
        else:
            name = input("Enter a name for the level")
        if name == "":
            name = len(listdir("levels"))
        data["name"] = name
        data["enabled"] = True
        data["macguffin"] = False

        entities = []
        for entity in self.placed_polygons:
            if entity.entity_type == EntityType.Turret:
                entities.append([entity.entity_type.name, list(entity.pos)])
            elif entity.entity_type == EntityType.Barrier:
                entities.append([entity.entity_type.name, list(entity.pos), entity.dimensions, entity.rotation])
            elif entity.entity_type == EntityType.MacGuffin:
                entities.append([entity.entity_type.name, list(entity.pos)])
                data["macguffin"] = True
            elif entity.entity_type == EntityType.Sniper:
                entities.append([entity.entity_type.name, list(entity.pos)])
            else:
                raise NotImplemented("Editor.serialize_level given unknown EntityType: ", entity.EntityType)
        data["entities"] = entities
        filename = "levels/Level-%s.json" % name
        with open(filename, "w") as file:
            json.dump(data, file, indent=4)
        print("Level %s has been written" % filename)

    def load_level(self, index):
        del self.placed_polygons[:]

        level = listdir("levels")[index]
        with open("levels/%s" % level, "r") as file:
            data = json.load(file)
        for entity in data["entities"]:
            if entity[0] == EntityType.Turret.name:
                polygon = Polygon(EntityType.Turret, entity[1])
            elif entity[0] == EntityType.Barrier.name:
                polygon = Polygon(EntityType.Barrier, entity[1], entity[2], entity[3])
            elif entity[0] == EntityType.MacGuffin.name:
                polygon = Polygon(EntityType.MacGuffin, entity[1])
            elif entity[0] == EntityType.Sniper.name:
                polygon = Polygon(EntityType.Sniper, entity[1])
            else:
                raise KeyError("Unknown EntityType: %s" % entity[0])
            self.placed_polygons.append(polygon)

        print("Level %d/%d loaded" % (index + 1, len(listdir("levels"))))

    def load_next_level(self):
        if self.current_level_index + 1 == len(listdir("levels")):
            self.current_level_index = 0
        else:
            self.current_level_index += 1
        self.load_level(self.current_level_index)

    def load_prev_level(self):
        if self.current_level_index - 1 == -1:
            self.current_level_index = len(listdir("levels")) - 1
        else:
            self.current_level_index -= 1
        self.load_level(self.current_level_index)

    def create_new_level(self):
        self.current_level_index = len(listdir("levels"))
        del self.placed_polygons[:]

    # returns the position of the mouse a square to interface with check_overlaps()
    def mouse_as_polygon(self):
        v = self.mouse_position
        return [v[0]-1, v[1]-1, v[0]+1, v[1]+1]

