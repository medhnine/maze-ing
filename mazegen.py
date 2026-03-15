import sys
from random import choice, shuffle, seed
from typing import Dict, List, Any, Tuple, Optional, Union


class MazeGenerator:
    west = 8  # 1000
    south = 4  # 0100
    east = 2  # 0010
    north = 1  # 0001

    def __init__(self) -> None:
        if len(sys.argv) < 2:
            print("Error: No config file provided")
            print("Usage: python mazegen.py <config_file>")
            sys.exit(1)
        self.file_name: str = sys.argv[1]

        self.pars: MazeGenerator.Pars = self.Pars()
        self.values: Dict[str, Any] = self.pars.extract_values(self.file_name)
        self.width: int = self.values["WIDTH"]
        self.height: int = self.values["HEIGHT"]
        self.entry: List[int] = self.values["ENTRY"]
        self.exit: List[int] = self.values["EXIT"]
        self.perfection: bool = self.values["PERFECT"]
        self.seed: int = self.values.get("seed", 0)
        seed(self.seed)

        self.grid: MazeGenerator.Grid = self.Grid(self.height, self.width)

        self.algo: Union[MazeGenerator.Prim,
                         MazeGenerator.Recursive_back_tracking]
        if self.values["algorithm"].lower() == "prim":
            self.algo = self.Prim(self.entry, self.exit)
        else:
            self.algo = self.Recursive_back_tracking(self.entry, self.exit)

        self.algo.algorithme(self.grid)
        if not self.perfection:
            self.imperfction()
        self.path: List[List[int]]
        self.strin_path: str
        self.path, self.strin_path = self.get_the_path()
        self.gen_outfile()

    def get_path(self) -> List[List[int]]:
        return self.path

    def get_entry(self) -> List[int]:
        return self.entry

    def get_exit(self) -> List[int]:
        return self.exit

    def get_grid(self) -> List[List[int]]:
        return self.grid.grid

    def get_values(self) -> Dict[str, Any]:
        return self.values

    def change_maze(self) -> None:
        self.seed += 1
        seed(self.seed)
        print("change")
        self.grid = self.Grid(self.height, self.width)
        print(self.values["algorithm"].lower())
        # self.algo = self.Recursive_back_tracking(self.entry, self.exit)
        if self.values["algorithm"].lower() == "prim":
            print("Prim")
            self.algo = self.Prim(self.entry, self.exit)
        else:
            self.algo = self.Recursive_back_tracking(self.entry, self.exit)
        self.algo.algorithme(self.grid)
        if not self.perfection:
            self.imperfction()
        self.path, self.strin_path = self.get_the_path()
        self.gen_outfile()

    def imperfction(self) -> None:
        """Add imperfections to the maze by opening extra walls.

        Iterates over every cell. If a cell has exactly one wall removed
        (values 14, 13, 11, or 7 each have exactly three walls set, i.e.
        only one passage), a random neighbor's shared wall is opened to
        create an extra passage. This introduces loops / alternative routes,
        making the maze "imperfect" (no longer a perfect maze with a single
        unique solution).

        Cells that satisfy grid.check_42() are skipped (boundary or special
        cells that should not be modified).

        Args:
            grid: The Grid object whose walls will be modified in place.
        """
        x = 0
        for row in self.grid.grid:
            y = 0
            for column in row:
                if not self.grid.check_42(self.grid.rows, self.grid.columns,
                                          x, y):
                    # 14 = 1110 (only north open), 13 = 1101 (only east open),
                    # 11 = 1011 (only south open),  7 = 0111 (only west open).
                    # These cells are near-dead-ends with just one passage.
                    if (column == 14 or column == 13 or column == 11
                            or column == 7):
                        neighbors = self.grid.get_neighbors(x, y)
                        # Filter out None (out-of-bounds neighbors)
                        filtered_neighbors: List[List[int]] = [item for item in neighbors if item is not None]  # noqa
                        # Pick a random neighbor and open the wall between them
                        shuffle(filtered_neighbors)
                        self.grid.open_direction(filtered_neighbors[0], x, y)
                y += 1
            x += 1

    def get_paths(self) -> Dict[Tuple[int, int], int]:
        """BFS flood-fill from 'entry', recording the minimum step count
        to reach each reachable cell.

        Uses a FIFO queue (list) to explore cells level-by-level (breadth-
        first). Because BFS visits cells in order of increasing distance,
        the FIRST time a cell is dequeued is guaranteed to be via the
        shortest route — no need to revisit or compare step counts.

        Args:
            grid:    The Grid object whose .grid attribute is the 2-D
                    bitmask array representing walls.
            entry:   Starting cell as [x, y].
            exit:    Destination cell as [x, y].
            path:    (optional) Pre-existing dict to accumulate results into.
            counter: Unused (kept for signature compatibility with the old DFS)
            visited: Unused (a fresh set is created internally).

        Returns:
            dict mapping (x, y) tuples to the minimum number of steps
            required to reach that cell from 'entry'.
            Example: {(0,0): 0, (0,1): 1, (1,1): 2, ...}
        """
        path: Dict[Tuple[int, int], int] = {}

        # Seed the BFS queue with the starting cell at distance 0.
        # Each element is a tuple: (row, column, steps_from_entry).
        cells: List[Tuple[int, int, int]] = []
        cells.append((self.entry[0], self.entry[1], 0))
        visited: set[Tuple[int, int]] = set()

        while cells:
            # cells.pop(0) removes and returns the element at index 0.
            x, y, steps = cells.pop(0)

            # If this cell was already visited, skip it.
            # BFS guarantees the first visit used the fewest steps.
            if (x, y) in visited:
                continue
            visited.add((x, y))

            # Record the shortest distance to this cell.
            path[(x, y)] = steps

            # If we've reached the exit, record it but don't enqueue its
            # neighbors — we don't need to explore beyond the destination.
            if [x, y] == self.exit:
                break

            # NORTH: if no north wall, enqueue the cell above (x-1, y)
            if not self.grid.grid[x][y] & MazeGenerator.north:
                if (x - 1, y) not in visited:
                    cells.append((x - 1, y, steps + 1))

            # EAST: if no east wall, enqueue the cell to the right (x, y+1)
            if not self.grid.grid[x][y] & MazeGenerator.east:
                if (x, y + 1) not in visited:
                    cells.append((x, y + 1, steps + 1))

            # SOUTH: if no south wall, enqueue the cell below (x+1, y)
            if not self.grid.grid[x][y] & MazeGenerator.south:
                if (x + 1, y) not in visited:
                    cells.append((x + 1, y, steps + 1))

            # WEST: if no west wall, enqueue the cell to the left (x, y-1)
            if not self.grid.grid[x][y] & MazeGenerator.west:
                if (x, y - 1) not in visited:
                    cells.append((x, y - 1, steps + 1))
        return path

    def get_the_path(self) -> Tuple[List[List[int]], str]:
        """Traces back the shortest path from exit to entry using
        the step-count
        dict produced by get_paths. Returns the path as a list of [x, y] coords
        ordered from entry to exit.

        Args:
            grrid: The Grid object containing the maze walls.
            entry: The starting cell [x, y].
            exit: The destination cell [x, y].

        Returns:
            A list of [x, y] coordinates representing the shortest path
            from entry to exit.
        """

        paths = self.get_paths()

        path: List[List[int]] = []
        string_path = ""

        cell: Tuple[int, int] = tuple(self.exit)  # type: ignore[assignment]

        while True:
            path.append(list(cell))
            x, y = cell

            if paths[cell] == 0:
                break

            if (paths.get((x - 1, y)) == (paths[cell]) - 1
                    and not self.grid.grid[x][y] & MazeGenerator.north):
                cell = (x - 1, y)
                string_path = "S" + string_path

            elif (paths.get((x, y + 1)) == paths[cell] - 1
                    and not self.grid.grid[x][y] & MazeGenerator.east):
                cell = (x, y + 1)
                string_path = "W" + string_path

            elif (paths.get((x + 1, y)) == int(paths[cell]) - 1
                    and not self.grid.grid[x][y] & MazeGenerator.south):
                cell = (x + 1, y)
                string_path = "N" + string_path

            elif (paths.get((x, y - 1)) == paths[cell] - 1
                    and not self.grid.grid[x][y] & MazeGenerator.west):
                cell = (x, y - 1)
                string_path = "E" + string_path

        path.reverse()
        return path, string_path

    @staticmethod
    def convert_in_hex(maze: List[List[int]]) -> str:
        """Convert the 2-D maze grid into a hex-encoded string.

        Each cell value (0–15) is written as a single hex digit (0–F).
        Rows are separated by newlines.

        Args:
            maze: 2-D list of integer cell values.

        Returns:
            A string like 'A3F\n72B\n...' representing the maze.
        """
        maze_hex = ""
        for row in maze:
            for column in row:
                maze_hex += format(column, "X")
            maze_hex += "\n"
        return maze_hex

    def gen_outfile(self) -> None:
        with open(self.values["OUTPUT_FILE"], "w") as output_file:
            hex_maze = self.convert_in_hex(self.grid.grid)
            output_file.write(hex_maze)
            x_entry, y_entry = self.entry
            x_exit, y_exit = self.exit
            output_file.writelines(f"\n{x_entry},{y_entry}")
            output_file.writelines(f"\n{x_exit},{y_exit}")
            output_file.writelines(f"\n{self.strin_path}")

    class Grid:
        def __init__(self, rows: int, columns: int) -> None:
            self.rows = rows
            self.columns = columns
            self.grid: List[List[int]] = self.prepare_grid()

        def prepare_grid(self) -> List[List[int]]:
            grid: List[List[int]] = []
            for row in range(self.rows):
                grid.append([])
                for column in range(self.columns):
                    grid[row].append(15)
            return grid

        def get_neighbors(self, row: int, column: int,
                          check: bool = True) -> List[Optional[List[int]]]:
            """Returns a list of 4 neighbors in order [North, East, South,
            West].

            Each element is either [row, col] of a valid neighbor, or None if
            that neighbor is out of bounds or part of the '42' blocked zone.

            Args:
                row: The row index of the current cell.
                column: The column index of the current cell.

            Returns:
                A list of 4 elements: [N, E, S, W], where each is [row, col]
                or None.
            """
            neighbors: List[Optional[List[int]]] = []

            if row - 1 < 0:
                neighbors.append(None)
            else:
                if check and self.check_42(self.rows, self.columns,
                                           row - 1, column):
                    neighbors.append(None)
                else:
                    neighbors.append([row - 1, column])

            if column + 1 > self.columns - 1:
                neighbors.append(None)
            else:
                if check and self.check_42(self.rows, self.columns,
                                           row, column + 1):
                    neighbors.append(None)
                else:
                    neighbors.append([row, column + 1])

            if row + 1 > self.rows - 1:
                neighbors.append(None)
            else:
                if check and self.check_42(self.rows, self.columns,
                                           row + 1, column):
                    neighbors.append(None)
                else:
                    neighbors.append([row + 1, column])

            if column - 1 < 0:
                neighbors.append(None)
            else:
                if check and self.check_42(self.rows, self.columns,
                                           row, column - 1):
                    neighbors.append(None)
                else:
                    neighbors.append([row, column - 1])

            return neighbors

        def open_west(self, row: int, column: int, bidi: bool = True) -> None:
            west_neighbor = self.get_neighbors(row, column)[3]
            if bidi and west_neighbor:
                self.open_east(west_neighbor[0], west_neighbor[1], False)
            if west_neighbor:
                if self.grid[row][column] & MazeGenerator.west:
                    self.grid[row][column] -= MazeGenerator.west
                    # return self.grid[row][column]

        def open_east(self, row: int, column: int, bidi: bool = True) -> None:
            east_neighbor = self.get_neighbors(row, column)[1]
            if bidi and east_neighbor:
                self.open_west(east_neighbor[0], east_neighbor[1], False)
            if east_neighbor:
                if self.grid[row][column] & MazeGenerator.east:
                    self.grid[row][column] -= MazeGenerator.east
                    # return self.grid[row][column]

        def open_north(self, row: int, column: int, bidi: bool = True) -> None:
            north_neighbor = self.get_neighbors(row, column)[0]
            if bidi and north_neighbor:
                self.open_south(north_neighbor[0], north_neighbor[1], False)
            if north_neighbor:
                if self.grid[row][column] & MazeGenerator.north:
                    self.grid[row][column] -= MazeGenerator.north
                    # return self.grid[row][column]

        def open_south(self, row: int, column: int, bidi: bool = True) -> None:
            south_neighbor = self.get_neighbors(row, column)[2]
            if bidi and south_neighbor:
                self.open_north(south_neighbor[0], south_neighbor[1], False)
            if south_neighbor:
                if self.grid[row][column] & MazeGenerator.south:
                    self.grid[row][column] -= MazeGenerator.south
                    # return self.grid[row][column]

        def open_direction(self, direction: List[int],
                           row: int, column: int) -> str:
            directions = self.get_neighbors(row, column, False)
            funcs = [self.open_north, self.open_east, self.open_south, self.open_west] # noqa
            index = directions.index(direction)
            funcs[index](row, column)
            path = ["N", "E", "S", "W"]
            return path[index]

        @staticmethod
        def check_42(rows: int, columns: int, row: int, column: int) -> bool:
            ft_cordonate = [
                [1, 0, 0, 0, 1, 1, 1],
                [1, 0, 0, 0, 0, 0, 1],
                [1, 1, 1, 0, 1, 1, 1],
                [0, 0, 1, 0, 1, 0, 0],
                [0, 0, 1, 0, 1, 1, 1]
            ]

            x, y = [int((rows + 1) / 2) - 3, int((columns + 1) / 2) - 4]
            if row >= x and column >= y:
                try:
                    return bool(ft_cordonate[row - x][column - y])
                except Exception:
                    return False
            return False

    class Prim:
        def __init__(self, entry: List[int], exit: List[int]) -> None:
            self.entry = entry
            self.exit = exit

            self.visited: List[List[int]] = []
            self.frontier: List[List[int]] = []

        def filter_list(self,
                        lst: List[Optional[List[int]]]) -> List[List[int]]:
            return [item for item in lst if item]

        def algorithme(self, grid: "MazeGenerator.Grid") -> List[List[int]]:
            entry_x, entry_y = self.entry

            self.visited.append(self.entry)

            self.frontier.extend(self.filter_list(grid.get_neighbors(entry_x,
                                                                     entry_y)))

            while self.frontier:
                picked_cell = choice(self.frontier)

                px, py = picked_cell

                neighbors = [
                    neighbor for neighbor
                    in grid.get_neighbors(px, py)
                    if neighbor
                ]

                visited_neighbors = [
                    neighbor for neighbor in
                    neighbors
                    if neighbor in self.visited
                ]

                if visited_neighbors:

                    shuffle(visited_neighbors)
                    neighbor_to_connect = visited_neighbors[0]

                    grid.open_direction(neighbor_to_connect, px, py)

                    self.visited.append(picked_cell)

                    invisited_neighbors = [
                        item for item in
                        neighbors
                        if item not in self.visited
                        and item not in self.frontier
                    ]

                    self.frontier.extend(invisited_neighbors)

                self.frontier.remove(picked_cell)

            return self.visited

    class Recursive_back_tracking:
        def __init__(self, entry: List[int], exit: List[int]) -> None:
            self.entry = entry
            self.exit = exit

        def algorithme(self, grid: "MazeGenerator.Grid") -> None:
            stack = []
            stack_visited = []
            x = self.entry[0]
            y = self.entry[1]

            stack_visited.append(self.entry)
            stack.append(self.entry)

            while True:
                neighbors = grid.get_neighbors(x, y)
                neighbors = [item for item in neighbors if item is not None]
                shuffle(neighbors)
                neighbor = None

                try:
                    neighbor = [item for item in neighbors if item not in stack_visited][0] # noqa
                except IndexError:
                    neighbor = None

                if neighbor is None:
                    stack.pop(-1)
                    if len(stack) == 0:
                        break
                    [x, y] = stack[-1]
                    continue

                grid.open_direction(neighbor, x, y)
                stack.append(neighbor)
                stack_visited.append(neighbor)
                [x, y] = neighbor

    class KeyNotFound(Exception):
        pass

    class InvalidFile(Exception):
        pass

    class MissingRequiredKey(Exception):
        pass

    class NotPositiveNumber(Exception):
        pass

    class OutOfMaze(Exception):
        pass

    class EntryExitSame(Exception):
        pass

    class In42(Exception):
        pass

    class InvalidValue(Exception):
        pass

    class Pars:

        required_keys = ["WIDTH", "HEIGHT", "ENTRY", "EXIT", "OUTPUT_FILE",
                         "PERFECT"]
        optional_keys = ["seed", "algorithm"]

        algorithms = ["recursive backtracking", "prim"]

        def __init__(self) -> None:
            self.values: Dict[str, Any] = {}

        @classmethod
        def inRequired(cls, key: str) -> bool:
            return (key in cls.required_keys)

        @classmethod
        def inOptional(cls, key: str) -> bool:
            return (key in cls.optional_keys)

        def all_required_exist(self) -> bool:
            if set(MazeGenerator.Pars.required_keys).issubset(
                    set(self.values)):
                return True
            return False

        def fill_required_values(self, key: str, value: str) -> None:
            if (key == MazeGenerator.Pars.required_keys[0] or key ==
                    MazeGenerator.Pars.required_keys[1]):
                number = int(value)
                if number <= 0:
                    raise MazeGenerator.NotPositiveNumber(
                        f"{key} must be a positive number, got {number}")
                self.values[key] = number
            if (key == MazeGenerator.Pars.required_keys[2] or key ==
                    MazeGenerator.Pars.required_keys[3]):
                x_str, y_str = value.split(",")
                x = int(x_str)
                y = int(y_str)
                if x < 0 or y < 0:
                    raise MazeGenerator.OutOfMaze(
                        f"{key} coordinates must be positive, got ({x},{y})")
                if x >= self.values["HEIGHT"]:
                    raise MazeGenerator.OutOfMaze(
                        f"{key} row {x} is out of bounds "
                        f"(HEIGHT={self.values['HEIGHT']})")
                if y >= self.values["WIDTH"]:
                    raise MazeGenerator.OutOfMaze(
                        f"{key} column {y} is out of bounds"
                        f" (WIDTH={self.values['WIDTH']})")
                if MazeGenerator.Grid.check_42(
                        self.values["HEIGHT"],
                        self.values["WIDTH"], x, y):
                    raise MazeGenerator.In42(
                        f"{key} ({x},{y}) is inside the 42 zone")
                self.values[key] = [x, y]
            if key == MazeGenerator.Pars.required_keys[4]:
                if not value.endswith(".txt"):
                    raise MazeGenerator.InvalidFile(
                        f"OUTPUT_FILE must end with .txt, got '{value}'")
                self.values[key] = value
            if key == MazeGenerator.Pars.required_keys[5]:
                if value.lower() not in ["true", "false"]:
                    raise MazeGenerator.InvalidValue(
                        f"PERFECT must be 'True' or 'False', got '{value}'")
                if value.lower() == "true":
                    self.values[key] = True
                else:
                    self.values[key] = False

        def fill_optional_values(self, key: str, value: str) -> None:
            if key == MazeGenerator.Pars.optional_keys[0]:
                self.values[key] = int(value)
            if key == MazeGenerator.Pars.optional_keys[1]:
                if value.lower() in self.algorithms:
                    self.values[key] = value.lower()
                else:
                    raise MazeGenerator.InvalidValue(
                        f"Unknown algInvalidValueorithm '{value}'. "
                        f"Choose from: {', '.join(self.algorithms)}")

        def extract_values(self, file_name: str) -> Dict[str, Any]:
            try:
                with open(file_name) as file:
                    for line in file.read().split("\n"):
                        line = line.strip()

                        if not line or line.startswith("#"):
                            continue

                        if "=" not in line:
                            raise MazeGenerator.InvalidFile(
                                f"Invalid line in config: '{line}'"
                                " (missing '=')")

                        key, value = line.split("=")
                        if self.inRequired(key):
                            self.fill_required_values(key, value)
                        elif self.inOptional(key):
                            self.fill_optional_values(key, value)
                        else:
                            raise MazeGenerator.KeyNotFound(
                                f"Unknown key '{key}' in config file")
                    if not self.all_required_exist():
                        missing = set(MazeGenerator.Pars.required_keys) - set(self.values) # noqa
                        raise MazeGenerator.MissingRequiredKey(
                            f"Missing required key(s): {', '.join(missing)}")

                    if self.values["ENTRY"] == self.values["EXIT"]:
                        raise MazeGenerator.EntryExitSame(
                            "ENTRY and EXIT cannot be the same cell: "
                            f"{self.values['ENTRY']}")

                    if self.values["WIDTH"] < 8 or self.values["HEIGHT"] < 6:
                        raise MazeGenerator.InvalidValue(
                            "Maze is too small to display"
                            " the '42' pattern (need at least 6x8, got "
                            f"{self.values['HEIGHT']}x{self.values['WIDTH']})")

                return self.values

            except Exception as e:
                print(f"Error: {e}")
                sys.exit(1)
