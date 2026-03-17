"""Interactive terminal display for A-Maze-ing using curses."""

import curses
from typing import List, Set, Tuple

from maze import Maze
from solver import MazeSolver

# ---------------------------------------------------------------------------
# Color pair IDs (must be > 0)
# ---------------------------------------------------------------------------
CP_WALL: int = 1
CP_PATH: int = 2
CP_ENTRY: int = 3
CP_EXIT: int = 4
CP_42: int = 5
CP_MENU: int = 6

# Wall colors cycled by the '3' key
WALL_COLORS: List[int] = [
    curses.COLOR_BLUE,
    curses.COLOR_WHITE,
    curses.COLOR_CYAN,
    curses.COLOR_MAGENTA,
    curses.COLOR_RED,
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _init_colors(wall_color_idx: int) -> None:
    """Initialize all curses color pairs.

    Args:
        wall_color_idx: Index into WALL_COLORS for the wall color.
    """
    w = WALL_COLORS[wall_color_idx % len(WALL_COLORS)]
    curses.init_pair(CP_WALL,  w,                    curses.COLOR_BLACK)
    curses.init_pair(CP_PATH,  curses.COLOR_CYAN,    curses.COLOR_GREEN)
    curses.init_pair(CP_ENTRY, curses.COLOR_BLACK,   curses.COLOR_GREEN)
    curses.init_pair(CP_EXIT,  curses.COLOR_BLACK,     curses.COLOR_RED)
    curses.init_pair(CP_42,    curses.COLOR_YELLOW,  curses.COLOR_BLACK)
    curses.init_pair(CP_MENU,  curses.COLOR_BLACK,   curses.COLOR_WHITE)


def _safe_addch(
    win: curses.window,
    y: int,
    x: int,
    ch: str,
    attr: int,
) -> None:
    """Write a single character, ignoring out-of-bounds errors.

    Args:
        win: Curses window.
        y: Row.
        x: Column.
        ch: Single character string.
        attr: Curses attribute / color pair.
    """
    try:
        win.addch(y, x, ch, attr)
    except curses.error:
        pass


def _safe_addstr(
    win: curses.window,
    y: int,
    x: int,
    s: str,
    attr: int,
) -> None:
    """Write a string, ignoring out-of-bounds errors.

    Args:
        win: Curses window.
        y: Row.
        x: Column.
        s: String to write.
        attr: Curses attribute / color pair.
    """
    try:
        win.addstr(y, x, s, attr)
    except curses.error:
        pass


# ---------------------------------------------------------------------------
# Drawing
# ---------------------------------------------------------------------------

def _draw_maze(
    win: curses.window,
    maze: Maze,
    entry: Tuple[int, int],
    exit_: Tuple[int, int],
    path_set: Set[Tuple[int, int]],
    show_path: bool,
) -> None:
    """Render the full maze grid onto *win* starting at row/col 0.

    Cell (row, col) occupies screen columns [4*col .. 4*col+4] and
    screen rows [2*row+1 .. 2*row+2].  Corners/walls are drawn at the
    shared boundaries.

    Args:
        win: Curses window to draw on.
        maze: The Maze object to render.
        entry: Entry cell as (row, col).
        exit_: Exit cell as (row, col).
        path_set: Set of cells belonging to the solution path.
        show_path: Whether to highlight the solution path.
    """
    pattern_cells: Set[Tuple[int, int]] = maze.get_42_cells()
    wall_a = curses.color_pair(CP_WALL)

    # ---- top border ----
    _safe_addch(win, 0, 0, '█', wall_a)
    for col in range(maze.width):
        seg = '██████' if maze.has_wall(0, col, 'N') else '   '
        _safe_addstr(win, 0, 6 * col + 1, seg, wall_a)
        # _safe_addstr(win, 0, 6 * col + 4, '███', wall_a)

    for row in range(maze.height):  
        sy = 2 * row + 1

        # left border of row
        lw = '█' if maze.has_wall(row, 0, 'W') else ' '
        _safe_addch(win, sy, 0, lw, wall_a)

        for col in range(maze.width):
            sx = 6 * col + 1
            cell: Tuple[int, int] = (row, col)

            # ---- pick content & color ----
            if cell == entry:
                content, cp = ' E ', CP_ENTRY
            elif cell == exit_:
                content, cp = ' X ', CP_EXIT
            elif show_path and cell in path_set:
                content, cp = '   ', CP_PATH
            elif cell in pattern_cells:
                content, cp = '███', CP_42
            else:
                content, cp = '   ', CP_WALL

            _safe_addstr(win, sy, sx, content, curses.color_pair(cp))

            # east wall
            ew = '███' if maze.has_wall(row, col, 'E') else '   '
            _safe_addstr(win, sy, 6 * col + 4, ew, wall_a)

        # ---- bottom border of row ----
        by = 2 * row + 2
        _safe_addch(win, by, 0, '█', wall_a)
        for col in range(maze.width):
            seg = '███' if maze.has_wall(row, col, 'S') else '   '
            _safe_addstr(win, by, 6 * col + 1, seg + '███', wall_a)
        
        # ── path connectors ──────────────────────────────────────────
        if show_path:
            for col in range(maze.width):
                sy = 2 * row + 1
                by = 2 * row + 2
                cell = (row, col)
                if cell not in path_set:
                    continue
                # east connector
                if (col < maze.width - 1
                        and (row, col + 1) in path_set
                        and not maze.has_wall(row, col, 'E')):
                    _safe_addstr(win, sy, 6 * col + 4, '   ',
                                curses.color_pair(CP_PATH))
                # south connector
                if (row < maze.height - 1
                        and (row + 1, col) in path_set
                        and not maze.has_wall(row, col, 'S')):
                    _safe_addstr(win, by, 6 * col + 1, '   ',
                                 curses.color_pair(CP_PATH))


def _draw_menu(
    win: curses.window,
    show_path: bool,
    max_y: int,
    max_x: int,
) -> None:
    """Render the key-binding bar on the last terminal row.

    Args:
        win: Curses window.
        show_path: Current path-visibility state (toggles label).
        max_y: Terminal height in rows.
        max_x: Terminal width in columns.
    """
    path_label = 'Hide path' if show_path else 'Show path'
    menu = (
        f"  1/r: Re-generate   "
        f"2/p: {path_label}   "
        f"3/c: Change color   "
        f"4 / q: Quit      "
    )
    attr = curses.color_pair(CP_MENU) | curses.A_BOLD
    _safe_addstr(win, max_y - 1, 0, menu[:max_x - 1], attr)


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def run_display(
    maze: Maze,
    entry: Tuple[int, int],
    exit_: Tuple[int, int],
    seed: int,
    width: int,
    height: int,
    perfect: bool,
    show_42: bool = True,
) -> None:
    """Launch the interactive curses display for the maze.

    Key bindings:
        1 / r  – Re-generate a new maze (increments seed).
        2 / p  – Toggle solution path visibility.
        3 / c  – Cycle wall color.
        4 / q  – Quit.

    Args:
        maze: Initial generated Maze object.
        entry: Entry cell as (row, col).
        exit_: Exit cell as (row, col).
        seed: Current random seed; incremented on each re-generation.
        width: Maze width in cells.
        height: Maze height in cells.
        perfect: If True, re-generated mazes will be perfect (no cycles).
    """
    def _main(win: curses.window) -> None:
        """Inner curses main loop (passed to curses.wrapper).

        Args:
            win: Standard screen window provided by curses.wrapper.
        """
        curses.curs_set(0)
        curses.start_color()
        curses.use_default_colors()
        win.keypad(True)

        color_idx: int = 0
        _init_colors(color_idx)

        current_maze: Maze = maze
        current_seed: int = seed
        show_path: bool = False

        solver = MazeSolver(current_maze)
        path: List[Tuple[int, int]] = solver.solve_bfs(
            entry[0], entry[1], exit_[0], exit_[1]
        )
        path_set: Set[Tuple[int, int]] = set(path)

        while True:
            win.erase()
            max_y, max_x = win.getmaxyx()

            _draw_maze(win, current_maze, entry, exit_, path_set, show_path)
            _draw_menu(win, show_path, max_y, max_x)
            win.refresh()

            key = win.getch()

            if key in (ord('4'), ord('q'), ord('Q'), 27):  # 27 = ESC
                break

            elif key in (ord('1'), ord('r'), ord('R')):
                current_seed = seed
                current_maze = Maze(width, height, current_seed, show_42)
                current_maze.generate_dfs()
                if not perfect:
                    current_maze.add_random_cycles()
                solver = MazeSolver(current_maze)
                path = solver.solve_bfs(
                    entry[0], entry[1], exit_[0], exit_[1]
                )
                path_set = set(path)
                show_path = False

            elif key in (ord('2'), ord('p'), ord('P')):
                show_path = not show_path

            elif key in (ord('3'), ord('c'), ord('C')):
                color_idx = (color_idx + 1) % len(WALL_COLORS)
                _init_colors(color_idx)

    curses.wrapper(_main)