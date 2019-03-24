
tile_models = {
    '.': None,
    '+': 'box',
}


class Level:
    def __init__(self):
        self.rows = []

    def read(self, fn):
        self.rows.clear()

        for line in open(fn, 'r').readlines():
            self.rows.append(line.rstrip())

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

    def get_tile(self, row, col):
        tile = self.rows[row][col]
        if tile.isspace():
            return
        return tile_models.get(tile)
