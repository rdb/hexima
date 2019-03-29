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
    void = None
    cracked = 'x'
    ice = 's'
    teleporter = 't'
    button = 'o'
    active = '/'
    inactive = '\\'

    def is_passable(self, dieval, toggle_state=False):
        if self.value is None:
            return False
        if self.value in '123456':
            return int(self.value) == int(dieval)
        elif self.value == '/':
            return not toggle_state
        elif self.value == '\\':
            return toggle_state
        else:
            return True

    def get_symbol(self):
        if self.value in '123456':
            return chr(0x2680 + ord(self.value) - ord('1'))
        else:
            return ''

    def get_color(self):
        if self.value == 'e':
            return (0.5, 1, 0.5, 1.0)
        elif self.value == 't':
            return (0.9, 0.3, 0.6, 1)
        elif self.value == 's':
            return (0.7, 0.95, 1.3, 0.7)
        elif self.value == 'o':
            return (1, 0.2, 0.2, 1.0)
        else:
            return (1, 1, 1, 1)

    def get_model(self):
        if self.value == 'x':
            return "gfx/tile-cracked.bam"
        else:
            return "gfx/tile.bam"


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
        if x < 0 or y < 0:
            return TileType.void
        try:
            v = self.rows[y][x]
        except IndexError:
            return TileType.void

        tile = self.rows[y][x]
        if tile.isspace():
            return TileType.void
        return TileType(tile)

    def remove_tile(self, x, y):
        self.rows[y] = self.rows[y][:x] + ' ' + self.rows[y][x + 1:]

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
