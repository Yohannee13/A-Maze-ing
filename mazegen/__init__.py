"""mazegen -- a small, reusable maze generation library.

``mazegen`` exposes a single class, :class:`MazeGenerator`, that
builds a grid-based maze (optionally perfect, i.e. with exactly one
path between two given cells) and lets you query its structure and
its shortest solution path.

Quick start
-----------
Instantiate the generator with a size, an entry and an exit point,
then call :meth:`MazeGenerator.generate`::

    from mazegen import MazeGenerator

    maze = MazeGenerator(
        width=20,
        height=15,
        entry=(0, 0),
        exit=(19, 14),
        perfect=True,
        seed=12345,
    )
    maze.generate()

Custom parameters
-----------------
* ``perfect`` (bool): when False, extra loops are carved with
  ``extra_passages`` (int) additional open walls.
* ``seed`` (int | None): fixes the random generator for reproducible
  mazes. Two generators created with the same arguments and the same
  seed always produce the same maze.
* ``draw_pattern`` (bool): stamps the mandatory "42" pattern of
  fully-closed cells on the grid (skipped automatically, with a
  warning, if the maze is too small to hold it).

Accessing the generated structure
----------------------------------
* ``maze.get_cell(x, y)`` returns the :class:`~mazegen.cell.Cell` at
  those coordinates. Each cell exposes ``walls`` (a dict of
  direction -> is_closed) and ``hex_digit()`` (the single hexadecimal
  digit used in the output file format).
* ``maze.shortest_path()`` returns the shortest path from entry to
  exit as a list of direction letters (``"N"``, ``"E"``, ``"S"``,
  ``"W"``), or ``None`` if entry and exit are not connected.
* ``maze.to_hex_rows()`` returns the whole maze as a list of strings,
  one hexadecimal digit per cell, one string per row.
"""

from .cell import Cell
from .generator import MazeError, MazeGenerator

__all__ = ["MazeGenerator", "MazeError", "Cell"]
__version__ = "1.0.0"
