import random

class Maze:
    NORTH = 1
    EAST = 2
    SOUTH = 4
    WEST = 8

    def __init__(self, width: int, height: int, seed_value):
        self.width = 1
        self.height = 1
        self.random = random.Random(seed_value)
        self.set_dimension(width, height)
        self.grid = []
        for row in range(self.height):
            current_row = []
            for col in range(self.width):
                current_row.append(
                    self.NORTH | self.EAST | self.SOUTH | self.WEST
                )

            self.grid.append(current_row)
    def set_dimension(self, width, height):
        if 0 < width <= 100 and 0 < height <= 100:
            self.width = width
            self.height = height
        else:
            print("invalid input")
            exit(2)

        

    def has_wall(self, row: int, col: int, direction: str) -> bool:
        if direction == "N":
            return (self.grid[row][col] & self.NORTH) != 0
        if direction == "E":
            return (self.grid[row][col] & self.EAST) != 0
        if direction == "S":
            return (self.grid[row][col] & self.SOUTH) != 0
        if direction == "W":
            return (self.grid[row][col] & self.WEST) != 0
        return False

    def open_wall(self, row: int, col: int, direction: str) -> None:
        if direction == "N" and row > 0:
            self.grid[row][col] &= ~self.NORTH
            self.grid[row - 1][col] &= ~self.SOUTH

        elif direction == "S" and row < self.height - 1:
            self.grid[row][col] &= ~self.SOUTH
            self.grid[row + 1][col] &= ~self.NORTH

        elif direction == "E" and col < self.width - 1:
            self.grid[row][col] &= ~self.EAST
            self.grid[row][col + 1] &= ~self.WEST

        elif direction == "W" and col > 0:
            self.grid[row][col] &= ~self.WEST
            self.grid[row][col - 1] &= ~self.EAST


    def generate_binary_tree(self):
        for row in range(self.height):
            for col in range(self.width):

                can_go_north = row > 0
                can_go_east = col < self.width - 1

                if can_go_north and can_go_east:
                    direction = self.random.choice(["N", "E"])
                    self.open_wall(row, col, direction)

                elif can_go_north:
                    self.open_wall(row, col, "N")

                elif can_go_east:
                    self.open_wall(row, col, "E")

    # -----------------------------
    # ASCII Drawing
    # -----------------------------

    def draw(self):
        top_line = "+"
        for col in range(self.width):
            if self.has_wall(0, col, "N"):
                top_line += "---+"
            else:
                top_line += "   +"
        print(top_line)

        for row in range(self.height):

            line = ""
            for col in range(self.width):

                if col == 0:
                    line += "|" if self.has_wall(row, col, "W") else " "

                if self.check_42(self.height, self.width, row, col):
                    line += " 4 "
                else:
                    line += "   "

                line += "|" if self.has_wall(row, col, "E") else " "

            print(line)

            bottom = "+"
            for col in range(self.width):
                bottom += "---+" if self.has_wall(row, col, "S") else "   +"
            print(bottom)
    @staticmethod
    def check_42(rows, columns, row, column):
        """Check if cell (row, column) is part of the '42' pattern.
        Uses the same centering formula as mazegen.py."""
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

    def get_42_cells(self):
        """Return the set of all cells that belong to the '42' pattern."""
        cells = set()
        for r in range(self.height):
            for c in range(self.width):
                if self.check_42(self.height, self.width, r, c):
                    cells.add((r, c))
        return cells
    

    def generate_dfs(self):
        # Pre-compute 42 pattern cells — treat them as obstacles
        pattern_cells = self.get_42_cells()

        # Choose random starting position (must not be a 42 cell)
        start_row = self.random.randint(0, self.height - 1)
        start_col = self.random.randint(0, self.width - 1)
        while (start_row, start_col) in pattern_cells:
            start_row = self.random.randint(0, self.height - 1)
            start_col = self.random.randint(0, self.width - 1)

        current_row = start_row
        current_col = start_col

        # Mark all 42 cells as already visited so DFS never enters them
        visited = set(pattern_cells)
        visited.add((current_row, current_col))

        stack = []

        while True:
            # Collect unvisited neighbors (42 cells are already in visited)
            neighbors = []

            # Check NORTH
            if current_row > 0 and (current_row - 1, current_col) not in visited:
                neighbors.append(("N", current_row - 1, current_col))

            # Check SOUTH
            if current_row < self.height - 1 and (current_row + 1, current_col) not in visited:
                neighbors.append(("S", current_row + 1, current_col))

            # Check EAST
            if current_col < self.width - 1 and (current_row, current_col + 1) not in visited:
                neighbors.append(("E", current_row, current_col + 1))

            # Check WEST
            if current_col > 0 and (current_row, current_col - 1) not in visited:
                neighbors.append(("W", current_row, current_col - 1))

            if neighbors:
                # Choose random neighbor
                direction, new_row, new_col = self.random.choice(neighbors)

                # Open wall between current and neighbor
                self.open_wall(current_row, current_col, direction)

                # Push current cell to stack
                stack.append((current_row, current_col))

                # Move to neighbor
                current_row = new_row
                current_col = new_col

                # Mark visited
                visited.add((current_row, current_col))

            elif stack:
                # Backtrack
                current_row, current_col = stack.pop()

            else:
                # Finished
                break
    # if perfect is false this method creates more than one path
    def add_random_cycles(self):
        """Open extra walls at dead-end cells to create multiple paths.
        Same approach as mazegen.py: find cells with only 1 passage
        (dead-ends) and open a random extra wall.
        Values: 14 (only N open), 13 (only E open), 11 (only S open), 7 (only W open)."""
        dead_end_values = {14, 13, 11, 7}

        for row in range(self.height):
            for col in range(self.width):
                # Skip 42 pattern cells
                if self.check_42(self.height, self.width, row, col):
                    continue

                if self.grid[row][col] in dead_end_values:
                    # Collect valid non-42 neighbors
                    neighbors = []
                    if row > 0 and not self.check_42(self.height, self.width, row - 1, col):
                        neighbors.append("N")
                    if col < self.width - 1 and not self.check_42(self.height, self.width, row, col + 1):
                        neighbors.append("E")
                    if row < self.height - 1 and not self.check_42(self.height, self.width, row + 1, col):
                        neighbors.append("S")
                    if col > 0 and not self.check_42(self.height, self.width, row, col - 1):
                        neighbors.append("W")

                    if neighbors:
                        # Pick a random neighbor direction and open the wall
                        self.random.shuffle(neighbors)
                        self.open_wall(row, col, neighbors[0])
    # 01/03/2026
    
    
    # def to_hex_file(self, entry, exit):
        
    #     string = ""
    #     for i in self.grid:
    #         for x in i:
    #             string += (f"{x:X}")
    #         string += "\n"
    #     x1, y1 = entry
    #     x2, y2 = exit
    #     path = self.solve_bfs(x1, y1, x2, y2)
    #     dir = self.path_into_dir(path)
    #     string += f"\n{x1},{y1}\n"
    #     string += f"\n{x2},{y2}\n"
    #     string += dir +"\n"
    #     return string

    def to_hex_string(self):
        string = ""

        for row in self.grid:
            for cell in row:
                string += f"{cell:X}"
            string += "\n"

        return string

if __name__ == "__main__":
    pass