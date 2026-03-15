from sys import argv

def get_data():
    try:
        with open(f"{argv[1]}", "r") as file:
            lines = file.readlines()
    except Exception as e:
        print(f"there is an error {e} le")
    return lines
def chuck_data(data):
    store = {}
    try:
        for line in data:
            line = line.strip()
            if not line or "=" not in line:
                continue
            key, value = line.split("=", 1)
            store[key.strip()] = value.strip()
    except Exception as e:
        print(f"there is an error{e}")
    return store
def insert_values(data):
    width = 0
    height = 0
    entry_x1 = 0
    entry_y1 = 0
    exit_x2 = 0
    exit_y2 = 0
    flag = False
    v_seed = None
    try:
        for key, value in data.items():
            key = key.lower()
            if key == "width":
                width = int(value)
            if key == "height":
                height = int(value)
            if key == "entry":
                x1 , y1 = value.split(',')
                entry_x1, entry_y1 = (int(x1), int(y1))
            if key == "exit":
                x2 , y2 = value.split(',')
                exit_x2, exit_y2 = (int(x2), int(y2))
            if key =="perfect":
                if value.lower() == "true":
                    flag = True
            if key == "seed" :
                v_seed =int(value)
    except Exception as e:
        print(e)
    return (width,height,entry_x1, entry_y1, exit_x2, exit_y2,flag, v_seed)

def validate_input(width, height, entry_cell, exit_cell):
    if width <= 0 or height <= 0:
        exit(2)

    ex1, ey1 = entry_cell
    ex2, ey2 = exit_cell

    if not (0 <= ex1 < height and 0 <= ey1 < width):
        exit(2)

    if not (0 <= ex2 < height and 0 <= ey2 < width):
        exit(2)

    if entry_cell == exit_cell:
        exit(2)

        print(x, x2)