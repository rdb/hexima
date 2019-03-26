
tile_models = {
    #TODO?: Randomly select from tile types (e.g. grass tiles, sand tiles)
    '.': 'gfx/tiles/tile-grass-blank',
    ',': 'gfx/tiles/tile-sand-blank',
    '+': 'gfx/tiles/tile-wall-1',
    '1': 'gfx/tiles/tile-d6-1',
    '2': 'gfx/tiles/tile-d6-2',
    '3': 'gfx/tiles/tile-d6-3',
    '4': 'gfx/tiles/tile-d6-4',
    '5': 'gfx/tiles/tile-d6-5',
    '6': 'gfx/tiles/tile-d6-6',
    'b': 'gfx/tiles/tile-d6-blank',
    'e': 'gfx/tiles/tile-d6-blank'
}

passable = '.,be'


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
                    model = tile_models.get(tile)
                    if model:
                        yield (x, y, model)

    def get_tile(self, x, y):
        tile = self.rows[y][x]
        if tile.isspace():
            return
        return tile_models.get(tile)

    def check_obstacle(self, x, y, dieval):
        if x < 0 or y < 0:
            return True
        try:
            tile = self.rows[y][x]
        except IndexError:
            return True
        if tile == str(dieval):
            return False
        return tile not in passable
