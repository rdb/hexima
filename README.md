hexima
======

This is an entry in [PyWeek 27](https://pyweek.org/27/), with the theme "6".

[Click here to go to the PyWeek entry page.](https://pyweek.org/e/superleuk27/)

![Screenshot](https://pyweek.org/media/dl/27/superleuk27/screenshot-Sun-Mar-31-01-20-02-2019-1489.jpg)

Playing the game
----------------

You can download binary builds from the [PyWeek entry page](https://pyweek.org/e/superleuk27/).

The game can be controlled using the arrow, enter and escape keys alone.  The mouse can additionally be used to rotate the camera, and R resets the level.

The gameplay should be fairly straightforward; navigate the die to the green tile to advance to the next level.  Certain tiles are marked with a die symbol; you can only land on them if your bottom face has the matching number.  If you get stuck, press escape to go to the menu, and select "reset level" or "skip level", or go to the main menu and choose "select level".

If you complete a level within a certain preset number of moves, you can "star" the level, as indicated on the level select screen.  Whether you have exceeded the number of moves to star a level is indicated by the star icon in the top right turning from solid to outlined.

It is also possible to use a game controller with a directional pad.  The thumbsticks are ignored at this time.

Running from source
-------------------

This game requires Python 3 and Panda3D 1.10.  I recommend installing the dependency via pip, using the command:

```
pip install -r requirements.txt
```

To run, open a terminal window, "cd" to the game directory and run:

```
python run_game.py
```

Modifying levels
----------------

If you want to play with creating your own puzzles, you can modify the levels in the `levels` folder as desired.  The levels are laid out in a grid, with the format being a kind of ASCII art.  The meaning of the symbols is as follows:

```
   No tile
.  Plain tile
b  Begin tile (must be one)
e  End tile (may be multiple)
6  Tile with die number (can be 1-6)
x  Cracked tile
s  Ice tile - be careful not to let the player slide out of the level!
t  Transporter, there must be two of these
o  Button (toggles state of / and \ tiles)
/  Tile that is active by default, as switched by button
\  Tile that is inactive by default, as switched by button
```

The first line is prefixed with `#` and should indicate the minimum number of moves needed to complete the level (in other words, the maximum moves you can make to "star" the level).

Sorry about the confusing level naming; the numbering is out of order.  See `game/packs.py` to see how they are ordered into the various packs.

Acknowledgements
----------------
Coding by rdb, level design by xidram

Music is made by [hendrik-jan](https://hendrik-jan.bandcamp.com/) for this game.

This game took inspiration from a puzzle game called Cuboid.

Skybox is by Spiney, licensed under CC-BY 3.0

Sound effects are from CC0 sources on OpenGameArt

Fonts are downloaded from publicly available font sources; the main font is [Quicksand](https://www.fontsquirrel.com/fonts/quicksand), under the SIL Open Font License, and various displayed symbols are from the fonts DejaVu Sans, Font Awesome 5, and Free Serif.

Some GLSL shader code for the blur shader was adapted from [this repository](https://github.com/Jam3/glsl-fast-gaussian-blur); it is licensed under the MIT license.
