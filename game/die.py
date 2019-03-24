__all__ = ["Die"]

from random import randint


sequences = [
    (2, 3, 5, 4),
    (1, 4, 6, 3),
    (1, 2, 6, 5),
    (1, 5, 6, 2),
    (1, 3, 6, 4),
    (2, 4, 5, 3),
]


class Die(object):
    def __init__(self):
        self.top_number = 1
        self.east_number = 2
        self.north_number = 3

    def rotate_to(self, top_number, twist=0):
        assert top_number >= 1 and top_number <= 6
        self.top_number = top_number
        seq = sequences[top_number - 1]
        self.east_number = seq[twist % 4]
        self.north_number = seq[(twist + 1) % 4]

    def throw(self):
        num = randint(1, 6)
        rot = randint(0, 4)
        self.rotate_to(num, rot)

    @property
    def south_number(self):
        return 7 - self.north_number

    @property
    def west_number(self):
        return 7 - self.east_number

    @property
    def bottom_number(self):
        return 7 - self.top_number

    def rotate_north(self):
        self.top_number, self.north_number = \
            self.south_number, self.top_number

    def rotate_east(self):
        self.top_number, self.east_number = \
            self.west_number, self.top_number

    def rotate_south(self):
        self.top_number, self.north_number = \
            self.north_number, self.bottom_number

    def rotate_west(self):
        self.top_number, self.east_number = \
            self.east_number, self.bottom_number
