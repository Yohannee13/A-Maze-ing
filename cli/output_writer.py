"""Writer for the maze output file, following the subject's format.

Format::

    <hex row 0>
    <hex row 1>
    ...
    <hex row N-1>

    <entry_x>,<entry_y>
    <exit_x>,<exit_y>
    <shortest path as N/E/S/W letters>
"""

from typing import List

from mazegen import MazeGenerator


def write_output(maze: MazeGenerator, output_file: str) -> None:
    """Write the maze to ``output_file`` using the hexadecimal format.

    Args:
        maze: A generated :class:`MazeGenerator`.
        output_file: Path of the file to (over)write.

    Raises:
        OSError: If the file cannot be written.
    """
    rows: List[str] = maze.to_hex_rows()
    path = maze.shortest_path()
    path_letters = "".join(path) if path is not None else ""

    entry_x, entry_y = maze.entry
    exit_x, exit_y = maze.exit

    lines = rows + [
        "",
        f"{entry_x},{entry_y}",
        f"{exit_x},{exit_y}",
        path_letters,
    ]

    with open(output_file, "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines) + "\n")
