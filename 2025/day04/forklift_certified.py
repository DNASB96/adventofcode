import sys
import itertools

FILENAME = sys.argv[1] if len(sys.argv) > 1 else "example"

def get_adjacent_spots(grid, x, y):
    """
    Returns the adjacent positions of (x, y) as a slice of the grid.

    Examples :
    ┌────► y
    │ ┌─────┐
    │ │..@@.│           ┌──┐           ┌───┐
    │ │.@.@.│           │.@│           │.@@│           ┌──┐
    │ │.@..@│ x=2 y=0 ─►│.@│ x=1 y=2 ─►│@.@│ x=4 y=4 ─►│..│
    │ │@.@..│           │@.│           │@..│           │@@│
    ▼ │..@@@│           └──┘           └───┘           └──┘
    x └─────┘
    """
    sliced_lines = grid[ max(0, x - 1) : min(len(grid), x + 2) ]
    return list(map(lambda line : line[ max(0, y - 1) : min(len(grid[0]), y + 2) ], sliced_lines))

def scan_department(grid):
    """
    Scan each position of the grid and marks with an X paper rolls that can be retrieved by forklifts.
    """
    for x, line in enumerate(grid):
        for y, spot in enumerate(line):
            if spot == '@':
                adjacent_spots = get_adjacent_spots(grid, x, y)

                # Substract the paper roll in the center, we only count the adjacent ones.
                adjacent_paper_rolls_count = sum(list(map(lambda line : len(line.replace('.','')), adjacent_spots))) - 1

                # Mark the paper roll for removal
                if adjacent_paper_rolls_count < 4:
                    grid[x]= grid[x][:y] + 'X' + grid[x][y + 1:]

def count_rolls_marked_for_removal(grid):
    """
    Returns the number of paper rolls marked for removal.
    """
    return sum(map(lambda line : len(line.replace('@','').replace('.','')), grid))

def remove_paper_roll(grid):
    """
    Proceeds to the removal of marked paper rolls using forklifts.
    """
    for i in range(len(grid)):
        grid[i] = grid[i].replace('X','.')

def clean_department(grid):
    """
    Removes paper rolls until there are only inaccessible rolls left.
    """
    if 'X' not in itertools.chain(grid): # Make sur the department has been scanned at least once
        scan_department(grid)
    
    removed_rolls_count = 0
    while count_rolls_marked_for_removal(grid):
        removed_rolls_count += count_rolls_marked_for_removal(grid)
        remove_paper_roll(grid)
        scan_department(grid)

    return removed_rolls_count

# [ '..@@.', '@.@.@' ... ]
department_grid = list(map(lambda line : line.strip(), open(FILENAME, 'r')))

scan_department(department_grid)

print(f"Part 1 : {count_rolls_marked_for_removal(department_grid)}")
print(f"Part 2 : {clean_department(department_grid)}")
