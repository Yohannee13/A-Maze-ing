*This project has been created as part of the 42 curriculum by fralaiav, yoandria*

# A-Maze-ing

## Description

**A-Maze-ing** is a command-line maze generator written in Python. Given a
simple text configuration file, the program:

1. **generates** a maze of the requested size, with a chosen entry and exit
   cell,
2. **stamps** the mandatory "42" pattern on the grid (a block of cells that
   stay fully enclosed, drawn as a small dot-matrix bitmap of the digits
   "4" and "2"),
3. **writes** the resulting maze to an output file using a compact
   hexadecimal wall-encoding format,
4. **displays** the maze interactively in the terminal (ASCII/block
   rendering).

The goal of the project is to practice procedural generation, graph/grid
algorithms (back-tracking generation, shortest-path search), clean
separation between a reusable core library and a CLI front-end, and basic
interactive terminal programming.

## Instructions

### Requirements

- Python 3.10+ (the code uses modern type-hint syntax such as
  `tuple[int, int]`)
- (optional, for `make lint`) `flake8`, `mypy`


### Installation

```bash
make install
```

This upgrades `pip` and installs the development dependencies
(`flake8`, `mypy`, `build`) used for linting and packaging.

### Running the program

```bash
make run                       # uses the default CONFIG=config.txt
```

which is equivalent to:

```bash
python3 a_maze_ing.py config.txt #IT should be preceeded by'(venv)cl?r?s?% in a virtual environement
```

- `config.txt` (positional, required): path to the configuration file.

Once running, the maze is shown and an interactive prompt lets you:

| Key | Action                              |
|-----|--------------------------------------|
| `r` | regenerate a brand-new random maze   |
| `p` | show / hide the shortest solving path |
| `c` | cycle through the wall colours        |
| `f` | Changes the patterns colors           |
| `q` | quit                                  |

### Other Makefile targets

```bash
make debug          # run the program under pdb
make lint           # flake8 + mypy (permissive mode)
make lint-strict    # flake8 + mypy --strict
make package        # build a distributable package
make clean          # remove caches / build artifacts
```

## Configuration file format

The configuration file is a plain text file, one `KEY=VALUE` pair per line.
Blank lines and lines starting with `#` are ignored, and inline comments
(`KEY=VALUE # comment`) are stripped as well.

| Key              | Mandatory | Type            | Description                                                               |
|-------------------|-----------|-----------------|----------------------------------------------------------------------------|
| `WIDTH`           | yes       | integer, 3–30   | Maze width, in cells                                                       |
| `HEIGHT`          | yes       | integer, 3–30   | Maze height, in cells                                                      |
| `ENTRY`           | yes       | `x,y`           | Coordinates of the entry cell (must be inside the grid)                    |
| `EXIT`            | yes       | `x,y`           | Coordinates of the exit cell (must be inside the grid, different from ENTRY) |
| `OUTPUT_FILE`     | yes       | string          | Path of the file the maze is written to                                    |
| `PERFECT`         | yes       | boolean         | `True`/`False`, `1`/`0`, `yes`/`no` — whether the maze has exactly one solution |
| `SEED`            | no        | integer         | Seed for reproducible generation |
| `EXTRA_PASSAGES`  | no        | integer         | Number of extra passages (loops) to try to add when `PERFECT=False`        |

Example:

```
WIDTH=20
HEIGHT=15
ENTRY=0,0
EXIT=19,14
OUTPUT_FILE=maze.hex
PERFECT=True
SEED=42
# EXTRA_PASSAGES=5
```

The generated maze is written to `OUTPUT_FILE` as one line per row: each
cell is encoded as a single hexadecimal digit whose bits represent its
closed walls (`N=1`, `E=2`, `S=4`, `W=8`), so a fully closed cell is `F`.

## Maze generation algorithm

The maze is carved with an **iterative randomized backtracker**
(a depth-first search over the grid, implemented with an explicit stack
rather than recursion):

1. Start from an unvisited, unblocked cell.
2. Push it on the stack and mark it visited.
3. While the stack is not empty, look at the top cell's unvisited,
   unblocked neighbours. If there is at least one, pick one at random,
   knock down the wall between the two cells, mark the neighbour visited,
   and push it. If there is none, pop the stack (backtrack).

Because this produces a spanning tree of the grid, the result is always a
*perfect* maze: there is exactly one path between any two cells.

If `PERFECT=False`, a limited number of extra passages are then added on
top of the spanning tree to create loops or if `EXTRA_PASSAGES` unspecified , that carving will be done randomly. Each candidate extra passage is
rejected if it would open up a fully-connected 3x3 area, so that no
corridor ever becomes wider than two cells.

The mandatory "42" pattern is stamped **before** carving the maze: the
cells that form the digits "4" and "2" are marked as obstacles and are
therefore never linked to any neighbour, so they stay fully enclosed
(hex digit `F`) regardless of the rest of the generation.

### Why this algorithm

- It is simple to implement correctly and to reason about (a graph
  spanning-tree walk), while still producing long, winding corridors with
  few short dead ends — visually satisfying mazes rather than a grid of
  short branches.
- Being iterative (stack-based) instead of recursive avoids Python's
  recursion-depth limit on large mazes.
- It naturally guarantees a perfect maze (single solution) by
  construction, which matches the subject's default requirement, while
  still allowing loops to be layered on top for the non-perfect mode.
- It composes cleanly with the "blocked cell" mechanism used for the "42"
  pattern: blocked cells are simply excluded from the walk and never
  linked, with no special-casing needed elsewhere in the algorithm.

## Reusable code

The project is split into a **reusable core library** and a **CLI
front-end**, so the maze engine can be imported and used independently of
the command line tool:

- `mazegen/` — the reusable package:
  - `cell.py`: the `Cell` class (walls, neighbours, hexadecimal
    encoding) and the shared direction constants.
  - `generator.py`: the `MazeGenerator` class, which builds the grid,
    carves the maze, adds extra passages, checks connectivity, and
    computes the shortest path (BFS) between entry and exit. It has no
    dependency on the CLI, the config file format, or any display code.
  - `pattern42.py`: computes the coordinates of the mandatory "42"
    pattern for a given grid size.

  Any of these can be reused as-is in another project, for example:

  ```python
  from mazegen import MazeGenerator

  maze = MazeGenerator(width=20, height=15, entry=(0, 0), exit=(19, 14), seed=42)
  maze.generate()
  path = maze.shortest_path()
  rows = maze.to_hex_rows()
  ```

- `cli/` — everything specific to this command-line tool and not meant to
  be reused elsewhere: `config_parser.py` (reads and validates the
  configuration file), `output_writer.py` (writes the hex-encoded output
  file), and `ascii_render.py` (block-style terminal rendering and
  interactive session).
- `a_maze_ing.py`: the entry point, which wires the config parser, the
  generator, the output writer, and the renderer together.

## Team and project management

- **Team members and roles**:
    - **fralaiav** — CLI front-end: `config_parser.py` and
      `output_writer.py`, the `ascii_render.py` terminal renderer and
      interactive session, plus the `Makefile` and packaging setup.
    - **yoandria** — `mazegen` core library: `Cell`/`MazeGenerator`
      design, the iterative backtracker and shortest-path
      implementation, the "42" pattern stamping, and the `mypy --strict`
      type-annotation pass.


- **Retrospective**:
    - **What went well**: splitting the project into a reusable
      `mazegen` package and a separate CLI front-end early on made it
      easy to work in parallel without stepping on each other's code;
      the iterative backtracker turned out simple to test in isolation
      once `Cell`/`MazeGenerator` had no CLI dependencies.
    - **What we'd do differently next time (What we will improve)**: write a couple of small
      shared tests for `mazegen` before building the CLI on top of it,
      and settle on config/file formats between teammates before
      writing the parser and writer in parallel(so we will improve conections).
    - **Anticipated planning**: we initially planned to split work by
      feature (generation, then output, then display) but switched early
      to a split by layer (`mazegen` vs `cli`) once we realized it let us
      work fully in parallel without merge conflicts.

- **Tools used**:
    - Git/GitHub for version control
    - `flake8` and `mypy` for linting and static typing
    - `make` to standardize common commands.

## Resources

- [Think Labyrinth! — Maze generation algorithms](https://www.astrolog.org/labyrnth/algrithm.htm)
- [Jamis Buck, *Mazes for Programmers* — blog series on maze algorithms](https://weblog.jamisbuck.org/2011/2/7/maze-generation-algorithm-recap)
- [Wikipedia — Maze generation algorithm](https://en.wikipedia.org/wiki/Maze_generation_algorithm)
- Python `random` and `typing` official documentation

**Use of AI**:

AI assistance (Claude, ChatGpt) was used during this project for:

- **Type-annotation fixes**: resolving `mypy --strict` errors in
  `a_maze_ing.py` (adding return type annotations, casting the loosely-typed
  config dictionary returned by the parser, narrowing `Optional` types)
  without changing the program's runtime behavior.
- **Packaging**: scaffolding the `pyproject.toml` for the `mazegen`
  pip package, and verifying the wheel/sdist build process in a clean
  virtual environment.
