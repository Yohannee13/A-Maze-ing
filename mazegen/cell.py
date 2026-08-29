"""Cell representation used by the maze grid.

A cell stores the state of its four walls (North, East, South, West)
and a reference to its direct neighbors on the grid. Walls are closed
by default; the generation algorithm opens them by "linking" two
adjacent cells together.
"""

from typing import Dict, Optional

DIRECTIONS: tuple[str, ...] = ("N", "E", "S", "W")

OPPOSITE: Dict[str, str] = {"N": "S", "S": "N", "E": "W", "W": "E"}

OFFSET: Dict[str, tuple[int, int]] = {
    "N": (0, -1),
    "E": (1, 0),
    "S": (0, 1),
    "W": (-1, 0),
}

WALL_BIT: Dict[str, int] = {"N": 1, "E": 2, "S": 4, "W": 8}


class Cell:
    """A single cell of the maze grid.

    Attributes:
        x: Column index of the cell (0-indexed).
        y: Row index of the cell (0-indexed).
        walls: Mapping of direction to a boolean, True meaning the
            wall is closed.
        blocked: True if the cell is an obstacle (for example part of
            the mandatory "42" pattern) and must never be linked to
            any neighbor.
        visited: Helper flag used by generation algorithms.
        neighbors: Mapping of direction to the neighboring Cell (or
            None if the cell is on the border of the grid).
    """

    def __init__(self, x: int, y: int) -> None:
        """Initialize a cell with all four walls closed.

        Args:
            x: Column index of the cell.
            y: Row index of the cell.
        """
        self.x = x
        self.y = y
        self.walls: Dict[str, bool] = {d: True for d in DIRECTIONS}
        self.blocked: bool = False
        self.visited: bool = False
        self.neighbors: Dict[str, Optional["Cell"]] = {
            d: None for d in DIRECTIONS
        }

    def link(self, other: "Cell", direction: str) -> None:
        """Open the wall between this cell and ``other``.

        Blocked cells (obstacles) are never linked, so they always
        keep their four walls closed.

        Args:
            other: The neighboring cell to link to.
            direction: Direction from ``self`` to ``other``.
        """
        if self.blocked or other.blocked:
            return
        self.walls[direction] = False
        other.walls[OPPOSITE[direction]] = False

    def is_open(self, direction: str) -> bool:
        """Return True if the wall in ``direction`` is open."""
        return not self.walls[direction]

    def open_neighbors(self) -> Dict[str, "Cell"]:
        """Return the neighboring cells reachable through an open wall."""
        result: Dict[str, "Cell"] = {}
        for direction, neighbor in self.neighbors.items():
            if neighbor is not None and self.is_open(direction):
                result[direction] = neighbor
        return result

    def hex_digit(self) -> str:
        """Encode the closed walls of the cell as one hexadecimal digit."""
        value = 0
        for direction, bit in WALL_BIT.items():
            if self.walls[direction]:
                value |= bit
        return format(value, "X")

    def __repr__(self) -> str:
        return f"Cell(x={self.x}, y={self.y}, walls={self.walls})"
