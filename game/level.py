__all__ = ["Level", "TileType"]

from enum import Enum


class TileType(Enum):
    entrance = 'b'
    exit = 'e'
    gate1 = '1'
    gate2 = '2'
    gate3 = '3'
    gate4 = '4'
    gate5 = '5'
    gate6 = '6'
    blank = '.'
    blank2 = ','

    def is_passable(self, dieval):
        if self.value in '123456':
            return int(self.value) == int(dieval)
        else:
            return True


class Level:
    def __init__(self):
        self.rows = []
        self.entrance = (0, 0)

    def read(self, fn):
        self.rows.clear()

        for line in open(fn, 'r').readlines():
            line = line.rstrip()
            if 'b' in line:
                self.entrance = line.index('b'), len(self.rows)
            self.rows.append(line)

    def find_tile(self, type):
        "Returns the coordinates of the first tile with the given type."

        for x, y, tile_type in self.get_tiles():
            if tile_type == type:
                return (x, y)

    def get_tiles(self):
        for y, row in enumerate(self.rows):
            for x, tile in enumerate(row):
                if not tile.isspace():
                    model = TileType(tile)
                    if model:
                        yield (x, y, model)

    def get_tile(self, x, y):
        tile = self.rows[y][x]
        if tile.isspace():
            return
        return TileType(tile)

    def check_obstacle(self, x, y, dieval=None):
        if x < 0 or y < 0:
            return True
        try:
            v = self.rows[y][x]
        except IndexError:
            return True

        if v.isspace():
            return True

        tile = TileType(v)
        return not tile.is_passable(dieval)
