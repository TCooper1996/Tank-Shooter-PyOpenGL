import json
from math import log10
from os import listdir
from random import random, randint

from GameConstants import *


class Room:
    def __init__(self, design, depth):
        self.design = design
        self.depth = depth
        self.exit_list = [False] * 4

    def enable_right(self):
        self.exit_list[0] = True

    def enable_up(self):
        self.exit_list[1] = True

    def enable_left(self):
        self.exit_list[2] = True

    def enable_down(self):
        self.exit_list[3] = True

    def get_right(self):
        return self.exit_list[0]

    def get_up(self):
        return self.exit_list[1]

    def get_left(self):
        return self.exit_list[2]

    def get_down(self):
        return self.exit_list[3]

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
        room_created = False
        if self.max_rooms > 0 and -MAX_MAP_WIDTH <= root[0] <= MAX_MAP_WIDTH \
                and -MAX_MAP_HEIGHT <= root[1] <= MAX_MAP_HEIGHT:
            directions = [random() < 0.7 - log10(depth) / 4 for _ in range(4)]
            if directions[0] and not self.room_right(root):
                room_created = True
                if root not in dict.keys(self):
                    self[root] = Room(self.level_names[randint(0, len(self.level_names) - 1)], depth)
                self.max_rooms -= 1
                next_room = (root[0] + 1, root[1])
                if self.generate_level(next_room, depth + 1):
                    self[root].enable_right()
                    self[next_room].enable_left()

            if directions[1] and not self.room_up(root):
                room_created = True
                if root not in dict.keys(self):
                    self[root] = Room(self.level_names[randint(0, len(self.level_names) - 1)], depth)
                self.max_rooms -= 1
                next_room = (root[0], root[1] + 1)
                if self.generate_level(next_room, depth + 1):
                    self[root].enable_up()
                    self[next_room].enable_down()
            if directions[2] and not self.room_down(root):
                room_created = True
                if root not in dict.keys(self):
                    self[root] = Room(self.level_names[randint(0, len(self.level_names) - 1)], depth)
                self.max_rooms -= 1
                next_room = (root[0] - 1, root[1])
                if self.generate_level(next_room, depth + 1):
                    self[root].enable_left()
                    self[next_room].enable_right()
            if directions[3] and not self.room_down(root):
                room_created = True
                if root not in dict.keys(self):
                    self[root] = Room(self.level_names[randint(0, len(self.level_names) - 1)], depth)
                self.max_rooms -= 1
                next_room = (root[0], root[1] - 1)
                if self.generate_level(next_room, depth + 1):
                    self[root].enable_down()
                    self[next_room].enable_up()
            return room_created

    # Returns true if a room exists to the right of given room
    def room_right(self, root: (int, int)) -> bool:
        return (root[0] + 1, root[1]) in dict.keys(self)

    def room_up(self, root: (int, int)) -> bool:
        return (root[0], root[1] + 1) in dict.keys(self)

    def room_left(self, root: (int, int)) -> bool:
        return (root[0] - 1, root[1]) in dict.keys(self)

    def room_down(self, root: (int, int)) -> bool:
        return (root[0], root[1] - 1) in dict.keys(self)

    def __getitem__(self, item):
        return dict.__getitem__(self, item)

    def __setitem__(self, key, value):
        dict.__setitem__(self, key, value)
