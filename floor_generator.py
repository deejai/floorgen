from random import randint, choice, sample

n_loot = 3
n_mobs = 8
room_size = 5
floor_cols = 5
floor_rows = 5
map = []

def initialize_map():
    global map
    map = []

    for row_n in range(1 + floor_rows * (room_size + 1)):
        row = []
        for col_n in range(1 + floor_cols * (room_size + 1)):
            if ((row_n % (room_size + 1)) == 0) or ((col_n % (room_size + 1)) == 0):
                row.append("X")
            else:
                row.append(" ")
        map.append(row)

def can_open_wall(room_row, room_col, dir):
    if room_row < 0 or room_row > floor_rows:
        raise IndexError(f"Row out of range ({room_row})")

    if room_col < 0 or room_col > floor_cols:
        raise IndexError(f"Row out of range ({room_col})")

    if dir == "n" and room_row == 0:
            return False
    
    if dir == "e" and room_col == floor_cols-1:
            return False
    
    if dir == "s" and room_row == floor_rows-1:
            return False
    
    if dir == "w" and room_col == 0:
            return False

    return True

def build_door(room_row, room_col, dir):
    if room_row < 0 or room_row > floor_rows:
        raise IndexError(f"Row out of range ({room_row})")

    if room_col < 0 or room_col > floor_cols:
        raise IndexError(f"Row out of range ({room_col})")

    if dir == "n" and room_row == 0:
            raise IndexError(f"Can't build n door in top row")
    
    if dir == "e" and room_col == floor_cols-1:
            raise IndexError(f"Can't build e door in rightmost column")
    
    if dir == "s" and room_row == floor_rows-1:
            raise IndexError(f"Can't build s door in bottom row")
    
    if dir == "w" and room_col == 0:
            raise IndexError(f"Can't build w door in leftmost column")

    row_n, col_n = get_door_tile_row_col(room_row, room_col, dir)

    map[row_n][col_n] = "D"

def get_door_tile_row_col(room_row, room_col, dir):
    # nesw doors
    if dir == "n":
        row_n = (room_size + 1) * room_row
        col_n = (room_size + 1)//2 + (room_size + 1) * room_col
    
    if dir == "e":
        row_n = (room_size + 1)//2 + (room_size + 1) * room_row
        col_n = (room_size + 1) * (room_col + 1)
    
    if dir == "s":
        row_n = (room_size + 1) * (room_row + 1)
        col_n = (room_size + 1)//2 + (room_size + 1) * room_col
    
    if dir == "w":
        row_n = (room_size + 1)//2 + (room_size + 1) * room_row
        col_n = (room_size + 1) * room_col

    if dir == "c":
        row_n = (room_size + 1)//2 + (room_size + 1) * room_row
        col_n = (room_size + 1)//2 + (room_size + 1) * room_col

    if dir == "topleft":
        row_n = (room_size + 1) * room_row
        col_n = (room_size + 1) * room_col

    return row_n, col_n

def get_wall_coords(room_row, room_col, dir):
    door_row_n, door_col_n = get_door_tile_row_col(room_row, room_col, dir)

    coords = []

    if dir in "ns":
        for i in range(1 - room_size % 2, room_size + 1 - (room_size % 2)):
            coords.append((door_row_n, door_col_n + i - room_size // 2))

    elif dir in "ew":
        for i in range(1 - room_size % 2, room_size + 1 - (room_size % 2)):
            coords.append((door_row_n + i - room_size // 2, door_col_n))

    else:
        raise KeyError(f"Wall must specify a direction among: n, e, s, w")

    return coords

def opening_exists(room_row, room_col, dir):
    row_n, col_n = get_door_tile_row_col(room_row, room_col, dir)
    return map[row_n][col_n] != "X"

def build_random_doors(num):
    for i in range(num):
        while True:
            try:
                build_door(
                    randint(0, floor_rows-1),
                    randint(0, floor_cols-1),
                    choice("nesw")
                )
                break
            except IndexError:
                pass

def open_room_wall(room_row, room_col, dir):
    if can_open_wall(room_row, room_col, dir) == False:
        raise IndexError(f"Can't open wall: {room_row}, {room_col}, {dir}")

    wall_coords = get_wall_coords(room_row, room_col, dir)

    for coords in wall_coords:
        map[coords[0]][coords[1]] = " "

def initialize_connections():
    for floor_row in range(floor_rows):
        for floor_col in range(floor_cols):
            build_random_connection_in_room(floor_row, floor_col)

def build_random_connection_in_room(floor_row, floor_col):
    index = randint(0, 3)
    iter_jump = choice([1, 5]) # 1 is forward, 5 is reverse
    for i in range(4):
        dir = "nesw"[index]
        if can_open_wall(floor_row, floor_col, dir) and not opening_exists(floor_row, floor_col, dir):
            op = choice(["door", "opening"])
            if op == "door":
                build_door(floor_row, floor_col, dir)
            else:
                open_room_wall(floor_row, floor_col, dir)
            return True

        index = (index + iter_jump) % 4

    return False # room has all doors populated already

def label_room(room_row, room_col, label):
    if len(label) != 1:
        raise TypeError("label must be a 1 character string")

    row_n, col_n = get_door_tile_row_col(room_row, room_col, "c")

    map[row_n][col_n] = label

def print_map():
    for row in map:
        for col in row:
            print(col, end="")
        print()

def floodfill_connected_rooms(current_coords, connected_rooms = None):
    if connected_rooms == None:
        connected_rooms = set()

    if current_coords in connected_rooms:
        return connected_rooms

    connected_rooms.add(current_coords)

    for dir in "nesw":
        if(opening_exists(current_coords[0], current_coords[1], dir)):
            floodfill_connected_rooms((
                current_coords[0] + (1 if dir == "s" else -1 if dir == "n" else 0),
                current_coords[1] + (1 if dir == "e" else -1 if dir == "w" else 0)
            ), connected_rooms)

    return connected_rooms

def randomize_settings(level=0):
    global room_size, floor_cols, floor_rows, n_loot, n_mobs
    room_size = randint(5, 6 + level // 3)
    floor_cols = randint(3 + level // 3, 4 + level // 2)
    floor_rows = randint(3 + level // 4, 4 + level // 3)
    n_loot = randint(2 + level // 4, 2 + (1 if level > 0 else 0) + level // 2)
    n_mobs = randint(5 + level // 2, 6 + level)

def pick_random_distinct_rooms(num):
    chosen_rooms = set()
    for i in range(num):
        while True:
            coords = (randint(0, floor_rows-1), randint(0, floor_cols-1))
            if coords not in chosen_rooms:
                break
        chosen_rooms.add(coords)

    return chosen_rooms

def pick_empty_spot_in_room(room_row, room_col):
    topleft_row_n, topleft_col_n = get_door_tile_row_col(room_row, room_col, "topleft")

    while True:
        coords = (
            topleft_row_n + randint(1, room_size),
            topleft_col_n + randint(1, room_size)
        )

        if map[coords[0]][coords[1]] == " ":
            break

    return coords

def populate_mobs():
    chosen_rooms = pick_random_distinct_rooms(n_mobs)

    for room_row, room_col in chosen_rooms:
        map_coords = pick_empty_spot_in_room(room_row, room_col)
        map[map_coords[0]][map_coords[1]] = "&"

def populate_loot():
    chosen_rooms = pick_random_distinct_rooms(n_loot)

    for room_row, room_col in chosen_rooms:
        map_coords = pick_empty_spot_in_room(room_row, room_col)
        map[map_coords[0]][map_coords[1]] = "*"

def generate_floor():
    randomize_settings()
    initialize_map()
    initialize_connections()

    start_coords = choice([
        (randint(0,1), randint(0,1)),
        (randint(floor_rows-2,floor_rows-2), randint(0,1)),
        (randint(0,1), randint(floor_cols-2,floor_cols-2)),
        (randint(floor_rows-2,floor_rows-2), randint(floor_cols-2,floor_cols-2)),
        ])

    end_coords = (
        (start_coords[0] + floor_rows // 2) % floor_rows,
        (start_coords[1] + floor_cols // 2) % floor_cols
        )

    floodfill_results = floodfill_connected_rooms(start_coords)

    iterations = 1
    while len(floodfill_results) != floor_rows * floor_cols:
        for i in range(5):
            build_random_connection_in_room(randint(0, floor_rows-1), randint(0, floor_cols-1))

        floodfill_results = floodfill_connected_rooms(start_coords)
        iterations += 1

    label_room(start_coords[0], start_coords[1], "S")
    label_room(end_coords[0], end_coords[1], "E")

    populate_mobs()
    populate_loot()

    print_map()

    # print(f"floodfill iterations: {iterations}")

for i in range(10):
    generate_floor()
