"""Parser for the maze configuration file.

The configuration file uses one ``KEY=VALUE`` pair per line. Lines
starting with ``#`` (after stripping leading spaces) are comments and
are ignored, as are blank lines.
"""

import os
import random
from typing import Dict, Optional, Tuple


class ConfigError(Exception):
    """Raised when the configuration file is missing, malformed, or
    contains invalid values."""


class MazeConfig:
    """Typed, validated configuration for a maze generation run.

    Attributes:
        width: Maze width, in cells.
        height: Maze height, in cells.
        entry: (x, y) coordinates of the entry cell.
        exit: (x, y) coordinates of the exit cell.
        output_file: Path of the file the maze will be written to.
        perfect: Whether the maze must have exactly one solution.
        seed: Optional seed for reproducible generation.
        algorithm: Name of the generation algorithm (informational).
        extra_passages: Number of extra passages when not perfect.
    """

    def __init__(
        self,
        width: int,
        height: int,
        entry: Tuple[int, int],
        exit: Tuple[int, int],
        output_file: str,
        perfect: bool,
        seed: Optional[int] = None,
        algorithm: str = "backtracker",
        extra_passages: int = 0,
    ) -> None:
        self.width = width
        self.height = height
        self.entry = entry
        self.exit = exit
        self.output_file = output_file
        self.perfect = perfect
        self.seed = seed
        self.algorithm = algorithm
        self.extra_passages = extra_passages


_MANDATORY_KEYS = (
    "WIDTH",
    "HEIGHT",
    "ENTRY",
    "EXIT",
    "OUTPUT_FILE",
    "PERFECT",
)


def _read_raw_pairs(path: str) -> Dict[str, str]:
    """Read `KEY=VALUE` pairs from the configuration file."""
    pairs: Dict[str, str] = {}
    try:
        with open(path, "r", encoding="utf-8") as handle:
            for line_number, raw_line in enumerate(handle, start=1):
                line = raw_line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" not in line:
                    raise ConfigError(
                        f"{path}:{line_number}: expected KEY=VALUE, "
                        f"got: {raw_line!r}"
                    )
                key, _, value = line.partition("=")
                if "#" in value:
                    value, ignore = value.split("#", 1)
                pairs[key.strip().upper()] = value.strip()
    except OSError as exc:
        raise ConfigError(f"cannot read config file '{path}': {exc}") from exc
    return pairs


def _parse_int(pairs: Dict[str, str], key: str) -> int:
    try:
        return int(pairs[key])
    except ValueError as exc:
        raise ConfigError(f"{key} must be an integer, got: {pairs[key]!r}") \
            from exc


def _parse_coordinates(pairs: Dict[str, str], key: str) -> Tuple[int, int]:
    raw = pairs[key]
    parts = raw.split(",")
    if len(parts) != 2:
        raise ConfigError(f"{key} must be formatted as 'x,y', got: {raw!r}")
    try:
        return int(parts[0].strip()), int(parts[1].strip())
    except ValueError as exc:
        raise ConfigError(f"{key} coordinates must be integers: {raw!r}") \
            from exc


def _parse_bool(pairs: Dict[str, str], key: str) -> bool:
    value = pairs[key].strip().lower()
    if value in ("true", "1", "yes"):
        return True
    if value in ("false", "0", "no"):
        return False
    raise ConfigError(
        f"{key} must be a boolean (True/False), got:"
        f" {pairs[key].strip()!r}"
    )


def load_config(path: str) -> MazeConfig:
    """Load, parse, and validate the maze configuration file.

    Args:
        path: Path to the configuration file.

    Returns:
        A validated :class:`MazeConfig`.

    Raises:
        ConfigError: If the file is missing, malformed, or contains
            invalid or missing mandatory values.
    """
    if not os.path.isfile(path):
        raise ConfigError(f"config file not found: '{path}'")

    pairs = _read_raw_pairs(path)

    missing = [key for key in _MANDATORY_KEYS if key not in pairs]
    if missing:
        raise ConfigError(
            "missing mandatory key(s) in config file: " + ", ".join(missing)
        )

    width = _parse_int(pairs, "WIDTH")
    height = _parse_int(pairs, "HEIGHT")
    if width <= 0 or height <= 0:
        raise ConfigError("WIDTH and HEIGHT must be positive integers")

    if width < 3 or height < 3:
        raise ConfigError("WIDTH and HEIGHT must be more than or equal 3")

    if width > 30 or height > 30:
        raise ConfigError("WIDTH and HEIGHT must be less than or equal 30")

    entry = _parse_coordinates(pairs, "ENTRY")
    exit_ = _parse_coordinates(pairs, "EXIT")
    perfect = _parse_bool(pairs, "PERFECT")
    output_file = pairs["OUTPUT_FILE"]
    if not output_file:
        raise ConfigError("OUTPUT_FILE must not be empty")

    seed = _parse_int(pairs["SEED"]) if "SEED" in pairs and pairs["SEED"] else None
    algorithm = pairs.get("ALGORITHM", "backtracker")
    if "EXTRA_PASSAGES" in pairs:
        extra_passages = _parse_int(pairs, "EXTRA_PASSAGES")
    else:
        extra_passages = random.Random(seed).randrange(2, 32, 5)

    for name, point in (("ENTRY", entry), ("EXIT", exit_)):
        x, y = point
        if not (0 <= x < width and 0 <= y < height):
            raise ConfigError(
                f"{name}={x},{y} is outside the maze bounds "
                f"(0..{width - 1}, 0..{height - 1})"
            )
    if entry == exit_:
        raise ConfigError("ENTRY and EXIT must be different cells")

    return MazeConfig(
        width=width,
        height=height,
        entry=entry,
        exit=exit_,
        output_file=output_file,
        perfect=perfect,
        seed=seed,
        algorithm=algorithm,
        extra_passages=extra_passages,
    )
