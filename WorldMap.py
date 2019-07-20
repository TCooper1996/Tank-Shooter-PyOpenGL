from os import listdir
from random import random, randint

from math import log10


class Room:
    def __init__(self, design, exit_list):
        self.design = design
        self.exit_list = exit_list

    def enable_right(self):
        self.exit_list[0] = True

    def enable_up(self):
        self.exit_list[1] = True

    def enable_left(self):
        self.exit_list[2] = True

    def enable_down(self):
        self.exit_list[3] = True

    def get_design(self):
        return self.design

    def get_exits(self):
        return self.exit_list

# Module named WorldMap instead of World because for some reason Pycharm refuses to
# recognize World.py as a python file.


class World(dict):
    def __init__(self, max_rooms, level_directory):
        dict.__init__(self)
        self._rooms = [None]*max_rooms
        self.max_rooms = max_rooms
        self.level_names = listdir(level_directory)
        self.generate_level((0, 0), 1)

    def generate_level(self, root: (int, int), depth: int):
        directions = [random() < 0.7 - log10(depth) / 2 for _ in range(4)]
        if directions[0] and not self.room_right(root) and self.max_rooms > 0:
            self.max_rooms -= 1
            next_room = (root[0] + 1, root[1])
            self.generate_level(next_room, depth + 1)
            self[next_room].enable_right()
        if directions[1] and not self.room_up(root) and self.max_rooms > 0:
            self.max_rooms -= 1
            next_room = (root[0], root[1] + 1)
            self.generate_level(next_room, depth + 1)
            self[next_room].enable_up()
        if directions[2] and not self.room_down(root) and self.max_rooms > 0:
            self.max_rooms -= 1
            next_room = (root[0] - 1, root[1])
            self.generate_level(next_room, depth + 1)
            self[next_room].enable_left()
        if directions[3] and not self.room_down(root) and self.max_rooms > 0:
            self.max_rooms -= 1
            next_room = (root[0], root[1] - 1)
            self.generate_level(next_room, depth + 1)
            self[next_room].enable_down()
        self[root] = Room(self.level_names[randint(0, len(self.level_names) - 1)], directions)

    def room_right(self, root: (int, int)) -> bool:
        return (root[0] + 1, root[1]) in self._rooms

    def room_up(self, root: (int, int)) -> bool:
        return (root[0], root[1] + 1) in self._rooms

    def room_left(self, root: (int, int)) -> bool:
        return (root[0] - 1, root[1]) in self._rooms

    def room_down(self, root: (int, int)) -> bool:
        return (root[0], root[1] - 1) in self._rooms

    def __getitem__(self, item):
        return dict.__getitem__(self, item)

    def __setitem__(self, key, value):
        dict.__setitem__(self, key, value)
