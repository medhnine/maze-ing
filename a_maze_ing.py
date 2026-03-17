

# 28/02/2026

from maze import Maze
from solver import MazeSolver
from parser import *
from display import run_display
from sys import argv
import random
        




def main():
    if len(argv) != 2:
        return
    
    data = get_data()
    result = chuck_data(data)
    # print(insert_values(result))

    
    width ,height,entry_x1, entry_y1, exit_x2, exit_y2 ,flag,seed, outputfile = insert_values(result)
    # exit_cell = (height -1, width - 1)

    random.seed(seed)

    validate_input(width,height,(entry_x1,entry_y1),(exit_x2,exit_y2))

    # Minimum size check for 42 pattern (same as mazegen.py)
    show_42 = True
    if width < 8 or height < 6:
        print("Maze is too small to display the '42' pattern (need at least 6x8)")
        show_42 = False

    # Validate entry/exit are not inside the 42 zone
    if show_42 and Maze.check_42(height, width, entry_x1, entry_y1):
        print(f"ENTRY ({entry_x1},{entry_y1}) is inside the 42 zone")
        exit(2)

    if show_42 and Maze.check_42(height, width, exit_x2, exit_y2):
        print(f"EXIT ({exit_x2},{exit_y2}) is inside the 42 zone")
        exit(2)

    maze = Maze(width, height, seed, show_42)
    maze.generate_dfs()
    if not flag:
        maze.add_random_cycles()
    solver = MazeSolver(maze)
    path = solver.solve_bfs(entry_x1, entry_y1, exit_x2, exit_y2)
    directions = solver.path_into_dir(path)

    output = maze.to_hex_string()
    output += f"\n{entry_x1},{entry_y1}\n"
    output += f"\n{exit_x2},{exit_y2}\n"
    output += directions +"\n"
    print(outputfile)
    with open(outputfile,"w") as file:
            file.write(output)
    # print(maze.get_42_cells())
    run_display(
        maze=maze,
        entry=(entry_x1, entry_y1),
        exit_=(exit_x2, exit_y2),
        seed=seed,
        width=width,
        height=height,
        perfect=flag,
        show_42=show_42,
    )
    # hex_string = maze.to_hex_file((entry_x1, entry_y1),(exit_x2, exit_y2))
    
    

if __name__ == "__main__":
    main()
    # if prfect = false open max 3*3 wals