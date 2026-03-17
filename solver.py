from collections import deque
class MazeSolver:
    def __init__(self, maze):
        self.maze = maze
    def solve_bfs(self, start_row: int, start_col: int,
              end_row: int, end_col: int):

        # Create queue and add starting position
        queue: deque = deque()
        queue.append((start_row, start_col))

        # Track visited cells
        visited = set()
        visited.add((start_row, start_col))

        # moves =[]
        # move = ""

        # Store parent of each cell to reconstruct path
        parent: dict = {}
        parent[(start_row, start_col)] = None

        # Start BFS loop
        while queue:

            current_row, current_col = queue.popleft()

            # If we reached the goal, stop
            if (current_row, current_col) == (end_row, end_col):
                break

            # Check all four directions
            directions = ["N", "S", "E", "W"]
            

            for direction in directions:

                # Only move if there is NO wall
                if not self.maze.has_wall(current_row, current_col, direction):

                    # Compute neighbor coordinates
                    if direction == "N":
                        new_row = current_row - 1
                        new_col = current_col
                        # move = "N"

                    elif direction == "S":
                        new_row = current_row + 1
                        new_col = current_col
                        # move = "S"

                    elif direction == "E":
                        new_row = current_row
                        new_col = current_col + 1
                        # move = "E"

                    else:  # "W"
                        new_row = current_row
                        new_col = current_col - 1
                        # move = "W"

                    # If neighbor not visited and within bounds, process it
                    if (0 <= new_row < self.maze.height
                            and 0 <= new_col < self.maze.width
                            and (new_row, new_col) not in visited):

                        visited.add((new_row, new_col))
                        parent[(new_row, new_col)] = (current_row, current_col)
                        queue.append((new_row, new_col))
                        # moves.append(move)
        # Reconstruct shortest path
        path = []
        current = (end_row, end_col)

        while current is not None:
            path.append(current)
            current = parent.get(current)

        path.reverse()

        return path
    
    def path_into_dir(self,path):
        i = 0
        dir = []
        while i < len(path) - 1:
            x ,y = path[i]
            a , b = path[i+1]
            row = a - x
            column = b - y
            if(row == 1):
                dir.append("S")
            elif(row == -1):
                dir.append("N")
            elif(column == 1):
                dir.append("E")
            elif(column == -1 ):
                dir.append("W")

            i += 1
        return "".join(dir)