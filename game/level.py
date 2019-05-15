__all__ = ["Level", "TileType"]

from .die import Die

from enum import Enum
from copy import copy


class TileType(Enum):
    # Order matters!  Add only to the end!
    entrance = 'b'
    exit = 'e'
    gate1 = '1'
    gate2 = '2'
    gate3 = '3'
    gate4 = '4'
    gate5 = '5'
    gate6 = '6'
    blank = '.'
    cracked = 'x'
    ice = 's'
    teleporter = 't'
    button = 'o'
    active = '/'
    inactive = '\\'

    void = None

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
            return (0.5, 0.3, 0.9, 1)
        elif self.value == 's':
            return (0.7, 0.95, 1.3, 0.7)
        elif self.value == 'o':
            return (1, 0.2, 0.2, 1.0)
        else:
            return (1, 1, 1, 1)

    def get_model(self):
        if self.value == 'x':
            return "gfx/tile-cracked.bam"
        elif self.value == 'o':
            return "gfx/tile-button.bam"
        else:
            return "gfx/tile.bam"


class Cell:
    """ Abstract class for calculating solutions and level codes. """

    def __init__(self, type):
        self.type = type
        self.neighbors = (None, None, None, None) # NESW

    def solve(self, die):
        solutions = []
        self.r_solve(die, '', solutions, cracked=frozenset(), toggle_state=False, tested_states={})
        return solutions

    def r_solve(self, die, path, solutions, cracked, toggle_state, tested_states):
        # Have we visited this cell before?
        state = (self, die.top_number, die.east_number, die.north_number, toggle_state)
        shortest_path = tested_states.get(state)
        if shortest_path:
            # We already went here in this state.
            if len(shortest_path) < len(path):
                # And last time we got here, we took a shorter path.
                return

        if solutions and len(path) > len(solutions[0]):
            # Our current path is longer than a found solution, so forget it.
            return

        tested_states[state] = path

        if self.type == TileType.cracked:
            if self in cracked:
                return
            cracked = cracked | frozenset((self, ))

        if not self.type.is_passable(die.bottom_number, toggle_state):
            #print("%s: cannot move onto %s with number %d" % (path, self.type.name, die.bottom_number))
            return

        if self.type == TileType.exit:
            if solutions:
                if len(solutions[0]) > len(path):
                    solutions.clear()
            solutions.append(path)

        if self.type == TileType.button:
            toggle_state = not toggle_state

        if self.neighbors[0]:
            die_n = copy(die)
            die_n.rotate_north()
            self.neighbors[0].r_solve(die_n, path + '⇧', solutions=solutions, cracked=cracked, toggle_state=toggle_state, tested_states=tested_states)

        if self.neighbors[1]:
            die_e = copy(die)
            die_e.rotate_east()
            self.neighbors[1].r_solve(die_e, path + '⇨', solutions=solutions, cracked=cracked, toggle_state=toggle_state, tested_states=tested_states)

        if self.neighbors[2]:
            die_s = copy(die)
            die_s.rotate_south()
            self.neighbors[2].r_solve(die_s, path + '⇩', solutions=solutions, cracked=cracked, toggle_state=toggle_state, tested_states=tested_states)

        if self.neighbors[3]:
            die_w = copy(die)
            die_w.rotate_west()
            self.neighbors[3].r_solve(die_w, path + '⇦', solutions=solutions, cracked=cracked, toggle_state=toggle_state, tested_states=tested_states)


class Level:
    def __init__(self):
        self.rows = []
        self.entrance = (0, 0)
        self.teleporters = []
        self.par = None
        self.key = None
        self.begin_cell = None

    def read(self, fn):
        self.rows.clear()
        self.teleporters.clear()

        for line in open(fn, 'r').readlines():
            line = line.rstrip()

            if line.startswith('#'):
                line = line.lstrip('# ')
                self.par = int(line)
                continue

            # Ignore empty lines at the beginning.
            if not self.rows and not line.strip():
                continue

            for i, c in enumerate(line):
                if c == 'b':
                    self.entrance = i, len(self.rows)
                if c == 't':
                    self.teleporters.append((i, len(self.rows)))
            self.rows.append(line)

        # Build graph, starting from beginning.
        self.cells = {}
        self.begin_cell = self.__get_cell(self.cells, *self.entrance)

    def solve(self):
        # Find best solutions.
        die = Die()
        return self.begin_cell.solve(die)

    def __get_cell(self, cells, x, y):
        cell = cells.get((x, y))
        if cell:
            return cell

        type = self.get_tile(x, y)
        if type == TileType.void:
            return None

        cell = Cell(type)
        cells[(x, y)] = cell

        # Neighbors: NESW
        neighbors = []
        for xo, yo in (0, 1), (1, 0), (0, -1), (-1, 0):
            nx = x + xo
            ny = y + yo
            ncell = self.__get_cell(cells, nx, ny)

            while ncell and ncell.type == TileType.ice:
                nx += xo
                ny += yo
                ncell = self.__get_cell(cells, nx, ny)

            if ncell and ncell.type == TileType.teleporter and len(self.teleporters) >= 2:
                i = self.teleporters.index((nx, ny))
                nx, ny = self.teleporters[(i + 1) % len(self.teleporters)]
                ncell = self.__get_cell(cells, nx, ny)

            neighbors.append(ncell)

        cell.neighbors = tuple(neighbors)
        return cell

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
