from game.die import Die
import pytest


@pytest.mark.parametrize("value", range(1, 7))
@pytest.mark.parametrize("twist", range(0, 4))
def test_die(value, twist):
    die = Die()
    die.rotate_to(value, twist)

    assert die.top_number == value
    assert die.bottom_number == 7 - value

    assert die.north_number != value
    assert die.east_number != value
    assert die.south_number != value
    assert die.west_number != value

    assert die.north_number != 7 - value
    assert die.east_number != 7 - value
    assert die.south_number != 7 - value
    assert die.west_number != 7 - value

    assert die.east_number != die.south_number
    assert die.east_number != die.north_number
    assert die.west_number != die.south_number
    assert die.west_number != die.north_number

    orig_north = die.north_number
    orig_east = die.east_number
    orig_south = die.south_number
    orig_west = die.west_number

    # Rotating 2 in any direction should end up at same config
    for spin in [die.rotate_north, die.rotate_east,
                 die.rotate_south, die.rotate_west]:
        spin()
        spin()
        assert die.top_number == 7 - value
        assert die.bottom_number == value
        assert die.north_number != value
        assert die.east_number != value
        assert die.south_number != value
        assert die.west_number != value
        spin()
        spin()
        assert die.top_number == value
        assert die.bottom_number == 7 - value
        assert die.north_number != value
        assert die.east_number != value
        assert die.south_number != value
        assert die.west_number != value


def test_die_throw():
    die = Die()
    die.throw()

    assert die.top_number >= 1 and die.top_number <= 6
    assert die.bottom_number == 7 - die.top_number

    assert die.north_number != die.top_number
    assert die.east_number != die.top_number
    assert die.south_number != die.top_number
    assert die.west_number != die.top_number

    assert die.north_number != die.bottom_number
    assert die.east_number != die.bottom_number
    assert die.south_number != die.bottom_number
    assert die.west_number != die.bottom_number

    assert die.east_number != die.north_number
    assert die.east_number != die.south_number
    assert die.west_number != die.south_number
    assert die.west_number != die.north_number
