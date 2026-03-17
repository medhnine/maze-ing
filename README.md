*This project has been created as part of the 42 curriculum by mohhnine, bahriz.*

# A-Maze-ing

## Description

A-Maze-ing is a maze generator and solver written in Python. The program takes a configuration file as input, generates a random maze, solves it using BFS (shortest path), and outputs the result to a file in hexadecimal format. The maze always contains a visible "42" pattern made of fully closed cells — a nod to the 42 School. The generation logic is packaged as a reusable Python module that can be installed via pip.

## Instructions

### Requirements

- Python 3.10 or later
- pip

### Installation

```bash
# Install dependencies (flake8, mypy)
make install
```

### Run

```bash
make run
# or directly:
python3 a_maze_ing.py config.txt
```

### Debug

```bash
make debug
```

### Lint

```bash
make lint
```

### Clean

```bash
make clean
```

---

## Configuration file format

The configuration file uses `KEY=VALUE` pairs, one per line. Lines starting with `#` are comments and are ignored.

| Key | Description | Required | Example |
|-----|-------------|----------|---------|
| `WIDTH` | Number of columns in the maze | Yes | `WIDTH=20` |
| `HEIGHT` | Number of rows in the maze | Yes | `HEIGHT=15` |
| `ENTRY` | Entry cell coordinates (row,col) | Yes | `ENTRY=0,0` |
| `EXIT` | Exit cell coordinates (row,col) | Yes | `EXIT=19,14` |
| `OUTPUT_FILE` | Output filename (must end in .txt) | Yes | `OUTPUT_FILE=maze.txt` |
| `PERFECT` | If True, only one path exists between entry and exit | Yes | `PERFECT=True` |
| `seed` | Integer seed for reproducibility | No | `seed=42` |
| `algorithm` | `prim` or `recursive backtracking` | No | `algorithm=prim` |

### Example config file

```
# A-Maze-ing configuration
WIDTH=20
HEIGHT=15
ENTRY=0,0
EXIT=14,19
OUTPUT_FILE=maze.txt
PERFECT=True
seed=42
algorithm=recursive backtracking
```

---

## Maze generation algorithm

We implemented two algorithms:

**Recursive Backtracking (DFS)** — used as the default in `maze.py` and available in `mazegen.py`. It starts from a random cell, carves passages by visiting unvisited neighbors recursively, and backtracks when stuck. It produces mazes with long winding corridors and a single solution when PERFECT is enabled.

**Prim's algorithm** — available in `mazegen.py`. It starts from the entry cell, maintains a frontier of reachable unvisited cells, and randomly picks one to connect at each step. It produces mazes with more branching and a more uniform feel.

### Why we chose these algorithms

Recursive Backtracking was our primary choice because it is simple to implement, easy to understand, and naturally produces perfect mazes (spanning trees). It also integrates cleanly with the "42" pattern constraint — we simply mark those cells as already visited so DFS never enters them. Prim's algorithm was added as a bonus to support multiple generation strategies as suggested in the subject.

---

## Reusable module

The maze generation logic is packaged as a pip-installable module called `mazegen`.

### Installation

```bash
pip install mazegen-1.0.0-py3-none-any.whl
```

### Basic example

```python
from mazegen.mazegen import MazeGenerator
import sys

sys.argv = ["mazegen.py", "config.txt"]
maze = MazeGenerator()

# Access the grid (list of lists of ints)
grid = maze.get_grid()

# Access entry and exit
entry = maze.get_entry()   # e.g. [0, 0]
exit  = maze.get_exit()    # e.g. [14, 19]

# Access the solution path
path = maze.get_path()           # list of [row, col] cells
directions = maze.strin_path     # e.g. "SSSEEENEE..."
```

### Custom parameters

All parameters are passed via the config file. You can change the seed, dimensions, algorithm, and perfect flag there. The `mazegen` module reads the config file path from `sys.argv[1]`.

### Rebuild the package from source

```bash
pip install build
python3 -m build
# outputs dist/mazegen-1.0.0-py3-none-any.whl and dist/mazegen-1.0.0.tar.gz
```

---


---

## Visual display

The maze is displayed interactively in the terminal using Python's built-in `curses` library. The display is handled by `display.py` and launched automatically after the maze is generated.

### What is shown

- **Walls** — drawn using block characters, colored based on current wall color
- **Entry cell** — marked with `E` in green
- **Exit cell** — marked with `X` in red
- **42 pattern** — cells fully closed, highlighted in yellow
- **Solution path** — highlighted in cyan/green when toggled on

### Key bindings

| Key | Action |
|-----|--------|
| `1` or `r` | Re-generate a new maze |
| `2` or `p` | Show / hide the shortest path |
| `3` or `c` | Cycle through wall colors |
| `4` or `q` | Quit |

### Wall colors

The wall color cycles through: **blue, white, cyan, magenta, red**. Green and yellow are excluded — green clashes with the solution path background, yellow clashes with the 42 pattern color.

### Re-generation behavior

- If `seed` is set in the config → re-generation increments the seed each time, producing different but reproducible mazes
- If `seed` is not set → re-generation picks a new random seed each time, producing a completely random maze

## Team and project management

### Roles

- **mohhnine** — maze generation logic (`maze.py`, `mazegen.py`), DFS and Prim algorithms, "42" pattern implementation, hex output format
- **bahriz** — solver (`solver.py`), BFS pathfinding, parser (`parser.py`), config validation, main entry point (`a_maze_ing.py`)

### Planning

We started by reading the subject carefully and splitting the work into four parts: parsing, generation, solving, and output. Our initial plan was to finish generation first, then solving, then packaging. In practice, the "42" pattern constraint took more time than expected — making sure DFS never enters those cells and that entry/exit are never placed inside the pattern required careful handling. The packaging part (pyproject.toml, building the .whl) was done last.

### What worked well and what could be improved

What worked well: splitting the code into clean separate modules made it easy to work in parallel and test each part independently. The BFS solver was straightforward once the maze structure was solid.

What could be improved: our `a_maze_ing.py` and `mazegen.py` are somewhat separate codebases that duplicate some logic. With more time we would refactor `a_maze_ing.py` to fully use the `MazeGenerator` class from `mazegen.py` instead of having two parallel implementations.

### Tools used

- **Claude (Anthropic)** — used to help understand Python packaging (pyproject.toml, building .whl files), generate the Makefile structure, and review README requirements. All generated code was reviewed, tested and understood before use.
- **Git** — version control and collaboration
- **mypy / flake8** — static type checking and linting
- **pytest** — local unit testing (not submitted)

---

## Resources

- [Maze generation algorithms — Wikipedia](https://en.wikipedia.org/wiki/Maze_generation_algorithm)
- [Recursive backtracker explained — Jamis Buck](https://weblog.jamisbuck.org/2010/12/27/maze-generation-recursive-backtracker)
- [Prim's algorithm for mazes](https://weblog.jamisbuck.org/2011/1/10/maze-generation-prim-s-algorithm)
- [Python packaging guide — pypa.io](https://packaging.python.org/en/latest/tutorials/packaging-projects/)
- [BFS pathfinding — GeeksForGeeks](https://www.geeksforgeeks.org/breadth-first-search-or-bfs-for-a-graph/)
- [mypy documentation](https://mypy.readthedocs.io/en/stable/)
- [flake8 documentation](https://flake8.pycqa.org/en/latest/)

### AI usage

We used Claude (Anthropic) during this project for the following tasks:
- Understanding Python packaging concepts (pyproject.toml, .whl, src layout)
- Generating the Makefile with the correct mypy and flake8 flags from the subject
- Drafting this README structure

All AI-generated content was carefully reviewed, tested, and adapted. We made sure to fully understand every line before including it in the project.
