from game.level import Level

from glob import glob
import pytest
import os


@pytest.mark.parametrize("fn", glob(os.path.join(os.path.dirname(__file__), '..', 'levels', '*.lvl')))
def test_level(fn):
    level = Level()
    level.read(fn)

    solutions = level.solve()
    assert len(solutions) > 0
    assert level.par == len(solutions[0])
