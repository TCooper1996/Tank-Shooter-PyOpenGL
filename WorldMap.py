import json
from math import log10, cos, sin, pi
from os import listdir
from random import random, randint

from GameConstants import *


class Room:
    def __init__(self, design, depth):
        self.design = design
        self.depth = depth
        self.exit_list = [False] * 4

    def connect(self, dir: int):
        self.exit_list[dir] = True

    def get_exit(self, dir):
        return self.exit_list[dir]

    def get_design(self):
        return self.design

    def get_exits(self):
        return self.exit_list

# Module named WorldMap instead of World because for some reason Pycharm refuses to
# recognize World.py as a python file.


class World(dict):
    def __init__(self, max_rooms, level_directory):
        dict.__init__(self)
        self.max_rooms = max_rooms
        self.level_names = []
        self.macguffin_level_names = []
        for file in listdir(level_directory):
            with open("levels/" + file, "r") as level:
                data = json.load(level)
                if data["enabled"] and not data["macguffin"]:
                    self.level_names.append(file)
                elif data["macguffin"]:
                    self.macguffin_level_names.append(file)
        self.generate_level((0, 0), 1)
        self.deepest_room = self[(0, 0)]
        for room in list(dict.values(self)):
            if room.depth > self.deepest_room.depth:
                self.deepest_room = room
        self.deepest_room.design = self.macguffin_level_names[randint(0, len(self.macguffin_level_names)-1)]

    def generate_level(self, root: (int, int), depth: int):
        if self.max_rooms > 0 and -MAX_MAP_WIDTH <= root[0] <= MAX_MAP_WIDTH \
                and -MAX_MAP_HEIGHT <= root[1] <= MAX_MAP_HEIGHT:
            directions = [random() < 0.9 - log10(depth) / 2 for _ in range(4)]
            self[root] = Room(self.level_names[randint(0, len(self.level_names) - 1)], depth)
            self.max_rooms -= 1
            # i represents the 4 directions
            for i in range(3):
                # dirs is the direction as a binary string where right = 0b00, up = 0b01, left = 0b10, down = 0b11
                if directions[i] and not self.room_exists(root, i):
                    next_room = (root[0] + int(cos(i * pi/2)), root[1] + int(sin(i * pi/2)))
                    if self.generate_level(next_room, depth+1):
                        self[root].connect(i)
                        self[next_room].connect((i + 2) % 4)
            return True
        else:
            return False

    # Returns true if a room exists to the right of given room
    def room_exists(self, root: (int, int), direction) -> bool:
        return (root[0] + int(cos(direction * pi/2)), root[1] + int(sin(direction * pi/2))) in dict.keys(self)

    def __getitem__(self, item):
        return dict.__getitem__(self, item)

    def __setitem__(self, key, value):
        dict.__setitem__(self, key, value)
