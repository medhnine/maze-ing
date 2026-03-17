from sys import argv, exit


def get_data() -> list:
    """Read lines from the config file given as argv[1].

    Returns:
        List of lines from the file.
    """
    try:
        with open(f"{argv[1]}", "r") as file:
            lines = file.readlines()
        return lines
    except FileNotFoundError:
        print(f"Error: config file '{argv[1]}' not found.")
        exit(2)
    except Exception as e:
        print(f"Error reading config file: {e}")
        exit(2)


def chuck_data(data: list) -> dict:
    """Parse KEY=VALUE lines from config data.

    Args:
        data: List of raw lines from the config file.

    Returns:
        Dictionary of key-value pairs.
    """
    store = {}
    try:
        for line in data:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                print(f"Error: invalid line in config (missing '='): '{line}'")
                exit(2)
            key, value = line.split("=", 1)
            store[key.strip()] = value.strip()
    except Exception as e:
        print(f"Error parsing config file: {e}")
        exit(2)
    return store


def insert_values(data: dict) -> tuple:
    """Extract and validate all values from parsed config dict.

    Args:
        data: Dictionary of key-value pairs from config file.

    Returns:
        Tuple of (width, height, entry_x, entry_y, exit_x, exit_y, perfect, seed).
    """
    required_keys = ["width", "height", "entry", "exit", "output_file", "perfect"]
    data_lower = {k.lower(): v for k, v in data.items()}

    # Check all required keys are present
    for key in required_keys:
        if key not in data_lower:
            print(f"Error: missing required key '{key.upper()}' in config file.")
            exit(2)

    # Parse WIDTH
    try:
        width = int(data_lower["width"])
    except ValueError:
        print(f"Error: WIDTH must be an integer, got '{data_lower['width']}'")
        exit(2)

    # Parse HEIGHT
    try:
        height = int(data_lower["height"])
    except ValueError:
        print(f"Error: HEIGHT must be an integer, got '{data_lower['height']}'")
        exit(2)

    # Parse ENTRY
    try:
        x1, y1 = data_lower["entry"].split(",")
        entry_x1, entry_y1 = int(x1), int(y1)
    except ValueError:
        print(f"Error: ENTRY must be in format 'row,col', got '{data_lower['entry']}'")
        exit(2)

    # Parse EXIT
    try:
        x2, y2 = data_lower["exit"].split(",")
        exit_x2, exit_y2 = int(x2), int(y2)
    except ValueError:
        print(f"Error: EXIT must be in format 'row,col', got '{data_lower['exit']}'")
        exit(2)

    # Parse PERFECT
    if data_lower["perfect"].lower() not in ["true", "false"]:
        print(f"Error: PERFECT must be 'True' or 'False', got '{data_lower['perfect']}'")
        exit(2)
    flag = data_lower["perfect"].lower() == "true"

    # Parse OUTPUT_FILE
    output_file = data_lower["output_file"]
    if not output_file.endswith(".txt"):
        print(f"Error: OUTPUT_FILE must end with '.txt', got '{output_file}'")
        exit(2)

    # Parse optional SEED
    v_seed = None
    if "seed" in data_lower:
        try:
            v_seed = int(data_lower["seed"])
        except ValueError:
            print(f"Error: seed must be an integer, got '{data_lower['seed']}'")
            exit(2)

    return (width, height, entry_x1, entry_y1, exit_x2, exit_y2, flag, v_seed, output_file)


def validate_input(width: int, height: int, entry_cell: tuple, exit_cell: tuple) -> None:
    """Validate maze dimensions and entry/exit positions.

    Args:
        width: Maze width.
        height: Maze height.
        entry_cell: Entry as (row, col).
        exit_cell: Exit as (row, col).
    """
    if width <= 0 or height <= 0:
        print(f"Error: WIDTH and HEIGHT must be positive, got {width}x{height}.")
        exit(2)

    ex1, ey1 = entry_cell
    ex2, ey2 = exit_cell

    if not (0 <= ex1 < height and 0 <= ey1 < width):
        print(f"Error: ENTRY ({ex1},{ey1}) is out of maze bounds ({height}x{width}).")
        exit(2)

    if not (0 <= ex2 < height and 0 <= ey2 < width):
        print(f"Error: EXIT ({ex2},{ey2}) is out of maze bounds ({height}x{width}).")
        exit(2)

    if entry_cell == exit_cell:
        print(f"Error: ENTRY and EXIT cannot be the same cell: {entry_cell}.")
        exit(2)