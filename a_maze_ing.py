#!/usr/bin/env python3
"""A-Maze-ing: generate, save, and display a maze from a config file.

Usage:
    python3 a_maze_ing.py config.txt [--display ascii|mlx]

The program reads a configuration file (see ``config.txt`` for an
example), generates a maze accordingly, writes it to the configured
output file using the hexadecimal wall format, and finally displays
it (ASCII by default, or MLX graphics if requested and available).
"""

import sys
from typing import Optional, Callable, Any

from cli.config_parser import ConfigError, MazeConfig, load_config
from cli.output_writer import write_output
from mazegen import MazeError, MazeGenerator
from dataclasses import dataclass

# Type aliases pour améliorer la lisibilité
MazeFactory = Callable[[Optional[int]], MazeGenerator]

@dataclass
class CliArgs:
    config: str
    display: str
    
def parse_args(argv: list[str]) -> CliArgs:
    """Parse command-line arguments manually (replaces argparse)."""
    config: Optional[str] = None
    display: str = "ascii"

    i: int = 0
    while i < len(argv):
        arg: str = argv[i]

        if arg == "--display":
            if i + 1 >= len(argv):
                raise SystemExit("error: --display requires an argument (ascii or mlx)")
            value: str = argv[i + 1]
            if value not in ("ascii", "mlx"):
                raise SystemExit(f"error: invalid choice '{value}' for --display")
            display = value
            i += 2

        elif arg.startswith("--"):
            raise SystemExit(f"error: unknown option {arg}")

        else:  # positional argument
            if config is not None:
                raise SystemExit(f"error: unexpected extra argument '{arg}'")
            config = arg
            i += 1

    if config is None:
        raise SystemExit("error: missing required argument 'config'")


    return CliArgs(config=config, display=display)


def build_maze_factory(config: MazeConfig) -> MazeFactory:
    """Return a callable that builds a fresh generated maze.

    The returned callable takes an optional seed: pass the config's
    seed for reproducibility, or ``None`` to get a brand-new random
    maze (used by the "regenerate" interactive command).
    """

    def factory(seed: Optional[int]) -> MazeGenerator:
        maze: MazeGenerator = MazeGenerator(
            width=config.width,
            height=config.height,
            entry=config.entry,
            exit=config.exit,
            perfect=config.perfect,
            seed=seed,
            extra_passages=config.extra_passages,
        )
        maze.generate()
        return maze

    return factory


def fail(message: str) -> None:
    """Print a clear error message and exit with a non-zero status."""
    print(f"error: {message}", file=sys.stderr)
    sys.exit(1)


def main(argv: Optional[list[str]] = None) -> None:
    """Program entry point."""
    args: Any = parse_args(argv if argv is not None else sys.argv[1:])

    try:
        config: MazeConfig = load_config(args.config)
    except ConfigError as exc:
        fail(str(exc))

    build_maze: MazeFactory = build_maze_factory(config)

    try:
        maze: MazeGenerator = build_maze(config.seed)
    except MazeError as exc:
        fail(f"could not generate maze: {exc}")

    try:
        write_output(maze, config.output_file)
    except OSError as exc:
        fail(f"could not write output file '{config.output_file}': {exc}")

    print(f"Maze written to '{config.output_file}'.")

    if args.display == "mlx":
        print("Sorry, Mlx not implemented , falling back to ASCII  ")
    from cli.ascii_render import run_interactive as run_ascii

    run_ascii(build_maze, config.seed, config, initial_maze=maze)


if __name__ == "__main__":
    main()
