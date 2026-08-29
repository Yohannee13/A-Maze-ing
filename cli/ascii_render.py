"""
Draws the maze in the terminal using solid block characters, marks
the entry, the exit, and (optionally) the shortest path, and offers a
small interactive menu to regenerate the maze, toggle the path, and
change the wall colour, as required by the subject.
"""

from typing import List, Optional, Set, Tuple, Callable
import os
from mazegen import Cell, MazeGenerator
from cli.output_writer import write_output
from cli.config_parser import MazeConfig

_WALL_COLOURS: dict[str, str] = {
    "default": "\033[90m",
    "skyblue": "\033[96m",
    "red": "\033[31m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "blue": "\033[34m",
    "magenta": "\033[35m",
    "cyan": "\033[36m",
}
_RESET: str = "\033[0m"
_PATTERN_COLOURS: dict[str, str] = {
    "default": "\033[95m",
    "skyblue": "\033[96m",
    "red": "\033[31m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "blue": "\033[34m",
    "magenta": "\033[35m",
    "cyan": "\033[36m",
}

_TITLE = [
    "    █████╗           ███╗   ███╗  █████╗ ███████╗███████╗          "
    "██╗███╗   ██╗ ██████╗",
    "   ██╔══██╗          ████╗ ████║ ██╔══██╗╚══███╔╝██╔════╝          "
    "██║████╗  ██║██╔════╝",
    "   ███████║  █████╗  ██╔████╔██║ ███████║  ███╔╝ █████╗    █████╗  "
    "██║██╔██╗ ██║██║  ███╗",
    "   ██╔══██║  ╚════╝  ██║╚██╔╝██║ ██╔══██║ ███╔╝  ██╔══╝    ╚════╝  "
    "██║██║╚██╗██║██║   ██║",
    "   ██║  ██║          ██║ ╚═╝ ██║ ██║  ██║███████╗███████╗          "
    "██║██║ ╚████║╚██████╔╝",
    "   ╚═╝  ╚═╝          ╚═╝     ╚═╝ ╚═╝  ╚═╝╚══════╝╚══════╝          "
    "╚═╝╚═╝  ╚═══╝ ╚═════╝",
    "",
    "",
    "                                ──『 AMAZE_IN [YOANDRIA - FRALAIAV] 』──",
]

_PATH_COLOUR: str = "\033[37m"

_WALL_BLOCK: str = "▓▓"
_WALL_ROW: str = "▓▓"
_PATTERN_ROW: str = "▓▓"
_PATH_SYMBOL: str = "▒▒"


def show_title(color: str) -> None:
    print(color)
    for row in _TITLE:
        print(row)
    print(_RESET)


def _path_cells(maze: MazeGenerator) -> Set[Tuple[int, int]]:
    """Return the (x, y) coordinates visited by the shortest path."""
    path: Optional[List[str]] = maze.shortest_path()
    if not path:
        return set()

    from mazegen.cell import OFFSET

    cells: Set[Tuple[int, int]] = {maze.entry}
    x: int
    y: int
    x, y = maze.entry
    for direction in path:
        dx: int
        dy: int
        dx, dy = OFFSET[direction]
        x, y = x + dx, y + dy
        cells.add((x, y))
    return cells


def render(
    maze: MazeGenerator,
    show_path: bool = False,
    colour: str = "default",
    pattern_color: str = "default",
) -> str:
    """Build the full block-style representation of the maze as a string.

    Walls are drawn as solid ``▓`` blocks. Args:
        maze: A generated maze.
        show_path: If True, highlight the shortest path.
        colour: Key of ``_WALL_COLOURS`` used for the wall blocks
            (sky blue by default).

    Returns:
        The multi-line block rendering of the maze.
    """
    wall_colour: str = _WALL_COLOURS.get(colour, _WALL_COLOURS["default"])
    pattern_colour: str = _PATTERN_COLOURS.get(
        pattern_color, _PATTERN_COLOURS["default"]
    )
    path_cells: Set[Tuple[int, int]] = (
        _path_cells(maze) if show_path else set()
    )

    lines: List[str] = []

    top: str = wall_colour + _WALL_BLOCK
    for _ in range(maze.width):
        top += _WALL_ROW + wall_colour + _WALL_BLOCK
    lines.append(top + _RESET)

    for y in range(maze.height):
        top_line: str = wall_colour + _WALL_BLOCK + _RESET
        bottom_line: str = wall_colour + _WALL_BLOCK + _RESET
        for x in range(maze.width):
            cell: Cell = maze.get_cell(x, y)
            top_line += _cell_symbol(maze, cell, path_cells, pattern_colour)

            east_wall: str = (
                wall_colour + _WALL_BLOCK + _RESET if cell.walls["E"] else "  "
            )
            top_line += east_wall

            south: str = (
                wall_colour + _WALL_ROW + _RESET if cell.walls["S"] else "  "
            )
            bottom_line += south
            bottom_line += wall_colour + _WALL_BLOCK + _RESET
        lines.append(top_line)
        lines.append(bottom_line)

    return "\n".join(lines)


def _cell_symbol(
    maze: MazeGenerator,
    cell: Cell,
    path_cells: Set[Tuple[int, int]],
    pattern_colour: str,
) -> str:
    coords: Tuple[int, int] = (cell.x, cell.y)
    if coords == maze.entry:
        return "\033[97m▓▓\033[0m"
    if coords == maze.exit:
        return "\033[34m▓▓\033[0m"
    if cell.blocked:
        return pattern_colour + _PATTERN_ROW + _RESET
    if coords in path_cells:
        return _PATH_COLOUR + _PATH_SYMBOL + _RESET
    return "  "


def run_interactive(
    build_maze: Callable[[Optional[int]], MazeGenerator],
    initial_seed: Optional[int],
    config: MazeConfig,
    initial_maze: Optional[MazeGenerator] = None,
) -> None:
    """Run the interactive block-style session described by the subject.

    Args:
        build_maze: A callable that (re)builds a maze given a seed
            (or None for a random one) and returns it, already
            generated.
        initial_seed: Seed used for the first maze shown.
        initial_maze: Already-generated maze to display first, to
            avoid generating the maze twice. If None, one is built
            from ``initial_seed``.
    """
    maze: MazeGenerator = (
        initial_maze if initial_maze is not None else build_maze(initial_seed)
    )
    show_path: bool = False
    colour: str = "default"
    colours: List[str] = list(_WALL_COLOURS.keys())
    pattern_colours: List[str] = list(_PATTERN_COLOURS.keys())
    pattern_color: str = "default"
    help_text: str = (
        "\nControls: [r] regenerate  [p] show/hide path  "
        "[c] change colour  [q] quit [f] pattern colour\n"
    )

    while True:
        show_title(_PATTERN_COLOURS[pattern_color])
        print(
            render(
                maze,
                show_path=show_path,
                colour=colour,
                pattern_color=pattern_color
            )
        )
        write_output(maze, config.output_file)
        print(help_text)
        try:
            choice: str = input("> ").strip().lower()
        except EOFError:
            break
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as exc:
            print(f"error reading input: {exc}")
            print("Exiting...")
            break
        os.system("clear")
        print("\n")
        if choice == "r":
            maze = build_maze(None)
        elif choice == "p":
            show_path = not show_path
        elif choice == "c":
            colour = colours[(colours.index(colour) + 1) % len(colours)]
        elif choice == "f":
            len_pat_col = len(pattern_colours)
            idx = (pattern_colours.index(pattern_color) + 1) % len_pat_col
            pattern_color = pattern_colours[idx]
        elif choice == "q":
            break
        else:
            print("unknown command")
