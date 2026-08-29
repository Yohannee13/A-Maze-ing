"""Reusable maze generation module.

This module exposes a single class, :class:`MazeGenerator`, that can
be imported and reused independently of the command-line tool. See
the package docstring in ``mazegen/__init__.py`` for a quick-start
example.

Algorithm
---------
The maze is built with a randomized,  version of the
"recursive backtracker" algorithm (a depth-first search over the
grid). Because it produces a spanning tree of the grid, the result is
always a *perfect* maze (exactly one path between any two cells).

If ``perfect`` is False, a limited number of extra passages (loops)
are added afterwards. Every candidate extra passage is rejected if it
would create a fully open 3x3 area, so the "no corridor wider than 2
cells" rule from the subject is always respected.
"""

import random

from typing import Dict, List, Optional, Tuple

from .cell import DIRECTIONS, OFFSET, Cell

try:
    from .pattern42 import pattern_cells, MIN_WIDTH, MIN_HEIGHT

    PATTERN_AVAILABLE = True
except ImportError:
    PATTERN_AVAILABLE = False

    MIN_WIDTH = 0
    MIN_HEIGHT = 0

    def pattern_cells(
        width: int, height: int, entry: Tuple[int, int], exit_: Tuple[int, int]
    ) -> List[Tuple[int, int]]:
        return []


Coordinates = Tuple[int, int]


class MazeError(Exception):
    """Raised when the maze configuration is invalid."""

    pass


class MazeGenerator:
    """Generate, hold, and query a maze.

    Example:
        >>> maze = MazeGenerator(
        ...     width=20, height=15, entry=(0, 0), exit=(19, 14), seed=42,
        ... )
        >>> maze.generate()
        >>> path = maze.shortest_path()
        >>> len(path) > 0
        True

    Args:
        width: Maze width, in cells (must be >= 1).
        height: Maze height, in cells (must be >= 1).
        entry: (x, y) coordinates of the entry cell.
        exit: (x, y) coordinates of the exit cell.
        perfect: If True (default), the maze has exactly one path
            between entry and exit. If False, ``extra_passages``
            additional random passages are added, creating loops.
        seed: Optional seed for reproducible generation.
        extra_passages: Number of extra passages to try to add when
            ``perfect`` is False. Ignored when ``perfect`` is True.
        draw_pattern: If True (default), stamp the mandatory "42"
            pattern of fully closed cells on the grid, provided the
            maze is large enough to hold it.
    """

    def __init__(
        self,
        width: int,
        height: int,
        entry: Coordinates,
        exit: Coordinates,
        perfect: bool = True,
        seed: Optional[int] = None,
        extra_passages: int = 0,
        draw_pattern: bool = True,
    ) -> None:
        if width < 1 or height < 1:
            raise MazeError("width and height must be positive integers")
        if not self._in_bounds(entry, width, height):
            raise MazeError(f"entry {entry} is outside the maze bounds")
        if not self._in_bounds(exit, width, height):
            raise MazeError(f"exit {exit} is outside the maze bounds")
        if entry == exit:
            raise MazeError("entry and exit must be different cells")

        self.width: int = width
        self.height: int = height
        self.entry: Coordinates = entry
        self.exit: Coordinates = exit
        self.perfect: bool = perfect
        self.extra_passages: int = max(0, extra_passages)
        self.draw_pattern: bool = draw_pattern
        self.seed: Optional[int] = seed
        self._rng: random.Random = random.Random(seed)
        self.grid: List[List[Cell]] = [
            [Cell(x, y) for x in range(width)] for y in range(height)
        ]
        self.pattern_applied: bool = False
        self._link_neighbors()

    @staticmethod
    def _in_bounds(point: Coordinates, width: int, height: int) -> bool:
        x, y = point
        return 0 <= x < width and 0 <= y < height

    def get_cell(self, x: int, y: int) -> Cell:
        """Return the cell at (x, y).

        Raises:
            MazeError: If the coordinates are outside the grid.
        """
        if not self._in_bounds((x, y), self.width, self.height):
            raise MazeError(f"({x}, {y}) is outside the maze bounds")
        return self.grid[y][x]

    def _link_neighbors(self) -> None:
        """Attach each cell to its existing grid neighbors."""
        for y in range(self.height):
            for x in range(self.width):
                cell: Cell = self.grid[y][x]
                for direction in DIRECTIONS:
                    dx, dy = OFFSET[direction]
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < self.width and 0 <= ny < self.height:
                        cell.neighbors[direction] = self.grid[ny][nx]

    def _apply_pattern(self) -> None:
        """Mark the cells of the "42" pattern as obstacles."""
        if not PATTERN_AVAILABLE:
            print("warning: pattern42 module not available, skipping pattern")
            return

        cells: List[Coordinates] = pattern_cells(
            self.width, self.height, self.entry, self.exit
        )
        if not cells:
            print(
                "warning: maze is too small to draw the '42' pattern "
                f"(minimum size: {self._min_pattern_size()})"
            )
            return
        for x, y in cells:
            if (x, y) in (self.entry, self.exit):
                continue
            self.grid[y][x].blocked = True
        self.pattern_applied = True

    @staticmethod
    def _min_pattern_size() -> Tuple[int, int]:
        if PATTERN_AVAILABLE:
            return MIN_WIDTH, MIN_HEIGHT
        return (0, 0)

    def generate(self) -> None:
        """Run the full generation pipeline.

        Stamps the "42" pattern (if requested and if the maze is
        large enough), carves a perfect maze with an iterative
        backtracker, then adds extra passages if ``perfect`` is
        False.
        """
        if self.draw_pattern:
            self._apply_pattern()

        self._carve_perfect_maze()

        if not self.perfect:
            self._add_extra_passages(self.extra_passages)

        self._check_connectivity()

    def _unvisited_neighbors(self, cell: Cell) -> Dict[str, Cell]:
        result: Dict[str, Cell] = {}
        for direction, neighbor in cell.neighbors.items():
            if neighbor is not None and not neighbor.visited and not neighbor.blocked:
                result[direction] = neighbor
        return result

    def _carve_perfect_maze(self) -> None:
        """Iterative randomized depth-first search (backtracker)."""
        start: Optional[Cell] = self._first_unblocked_cell()
        if start is None:
            raise MazeError("maze has no free cell to start generation")

        stack: List[Cell] = [start]
        start.visited = True

        while stack:
            current: Cell = stack[-1]
            neighbors: Dict[str, Cell] = self._unvisited_neighbors(current)
            if not neighbors:
                stack.pop()
                continue
            direction: str = self._rng.choice(list(neighbors.keys()))
            neighbor: Cell = neighbors[direction]
            current.link(neighbor, direction)
            neighbor.visited = True
            stack.append(neighbor)

    def _first_unblocked_cell(self) -> Optional[Cell]:
        entry_cell: Cell = self.grid[self.entry[1]][self.entry[0]]
        if not entry_cell.blocked:
            return entry_cell
        for row in self.grid:
            for cell in row:
                if not cell.blocked:
                    return cell
        return None

    def _add_extra_passages(self, count: int) -> None:
        """Randomly open `count` extra walls, avoiding wide open areas."""
        candidates: List[Tuple[int, int, str]] = [
            (x, y, direction)
            for y in range(self.height)
            for x in range(self.width)
            for direction in ("E", "S")
            if self.grid[y][x].neighbors[direction] is not None
        ]
        self._rng.shuffle(candidates)

        added: int = 0
        for x, y, direction in candidates:
            if added >= count:
                break
            cell: Cell = self.grid[y][x]
            neighbor: Optional[Cell] = cell.neighbors[direction]
            if neighbor is None or cell.blocked or neighbor.blocked:
                continue
            if cell.is_open(direction):
                continue
            cell.link(neighbor, direction)
            if self._creates_wide_opening(x, y):
                cell.walls[direction] = True
                from .cell import OPPOSITE

                neighbor.walls[OPPOSITE[direction]] = True
                continue
            added += 1

    def _creates_wide_opening(self, x: int, y: int) -> bool:
        """Check whether any 3x3 window around (x, y) is fully open."""
        if self.width < 3 or self.height < 3:
            return False
        lo_y: int = max(0, y - 2)
        hi_y: int = min(y, self.height - 3)
        lo_x: int = max(0, x - 2)
        hi_x: int = min(x, self.width - 3)
        for top_y in range(lo_y, hi_y + 1):
            for top_x in range(lo_x, hi_x + 1):
                if self._is_block_fully_open(top_x, top_y):
                    return True
        return False

    def _is_block_fully_open(self, top_x: int, top_y: int) -> bool:
        """Return True if the 3x3 block starting at (top_x, top_y) has
        every internal wall open."""
        for row in range(3):
            for col in range(3):
                cell: Cell = self.grid[top_y + row][top_x + col]
                if col < 2 and cell.walls["E"]:
                    return False
                if row < 2 and cell.walls["S"]:
                    return False
        return True

    def _check_connectivity(self) -> None:
        """Ensure entry and exit are connected (sanity check)."""
        if self.shortest_path() is None:
            raise MazeError("generated maze is invalid: no path between entry and exit")

    def shortest_path(self) -> Optional[List[str]]:
        """Compute the shortest path from entry to exit.

        Returns:
            A list of direction letters ("N", "E", "S", "W"), one per
            step, or None if entry and exit are not connected.
        """
        start: Cell = self.grid[self.entry[1]][self.entry[0]]
        goal: Cell = self.grid[self.exit[1]][self.exit[0]]

        visited: Dict[Cell, Optional[Tuple[Cell, str]]] = {start: None}
        queue: List[Cell] = [start]
        head: int = 0
        while head < len(queue):
            current: Cell = queue[head]
            head += 1
            if current is goal:
                return self._rebuild_path(visited, goal)
            for direction, neighbor in current.open_neighbors().items():
                if neighbor not in visited:
                    visited[neighbor] = (current, direction)
                    queue.append(neighbor)
        return None

    @staticmethod
    def _rebuild_path(
        visited: Dict[Cell, Optional[Tuple[Cell, str]]], goal: Cell
    ) -> List[str]:
        steps: List[str] = []
        node: Cell = goal
        while visited[node] is not None:
            previous: Cell
            direction: str
            previous, direction = visited[node]  # type: ignore[misc]
            steps.append(direction)
            node = previous
        steps.reverse()
        return steps

    def to_hex_rows(self) -> List[str]:
        """Return the maze as a list of hexadecimal-encoded rows."""
        return ["".join(cell.hex_digit() for cell in row) for row in self.grid]
