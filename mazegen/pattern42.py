"""The mandatory "42" pattern.

The subject requires the generated maze to visually contain a "42"
drawn by several fully closed (obstacle) cells. The pattern is
described as a small dot-matrix bitmap that is stamped, centered, on
the maze grid before the generation algorithm runs. Cells that belong
to the pattern are marked as ``blocked`` and are therefore never
linked to any neighbor: they stay fully enclosed (hexadecimal ``F``).
"""

from typing import List
import sys

_DIGIT_4 = [
    "X.X",
    "X.X",
    "XXX",
    "..X",
    "..X",
]

_DIGIT_2 = [
    "XXX",
    "..X",
    "XXX",
    "X..",
    "XXX",
]


MIN_WIDTH = len(_DIGIT_4[0]) + 1 + len(_DIGIT_2[0]) + 2
MIN_HEIGHT = len(_DIGIT_4) + 2


def pattern_cells(
    width: int,
    height: int,
    entry: tuple[int, int],
    exit_: tuple[int, int],
) -> List[tuple[int, int]]:
    """Return the (x, y) coordinates of the cells forming "42".

    The pattern is centered on the grid. If the grid is too small to
    hold it (with a one-cell margin), an empty list is returned; the
    caller is responsible for warning the user in that case, as
    requested by the subject.

    If ``entry`` or ``exit_`` happen to fall inside the pattern, they
    are excluded from the returned cells so the maze always stays
    solvable: entry/exit points must never be fully enclosed.

    Args:
        width: Maze width, in cells.
        height: Maze height, in cells.
        entry: (x, y) coordinates of the maze entry point.
        exit_: (x, y) coordinates of the maze exit point.

    Returns:
        A list of (x, y) coordinates that must be marked as obstacles.
    """
    if width < MIN_WIDTH or height < MIN_HEIGHT:
        return []

    pattern = [row4 + "." + row2 for row4, row2 in zip(_DIGIT_4, _DIGIT_2)]
    pattern_h = len(pattern)
    pattern_w = len(pattern[0])

    offset_x = (width - pattern_w) // 2
    offset_y = (height - pattern_h) // 2

    cells = []
    for row_index, row in enumerate(pattern):
        for col_index, char in enumerate(row):
            if char == "X":
                cell = (offset_x + col_index, offset_y + row_index)
                if cell == entry or cell == exit_:
                    raise MazeError("Error: entry/exit in pattern 42, please check it")
                cells.append(cell)
    return cells
