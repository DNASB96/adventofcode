import sys
from itertools import combinations, starmap, pairwise

FILENAME = sys.argv[1] if len(sys.argv) > 1 else "example"

# Returns the left direction depending of the current direction taken : { '►':'▲', '▲':'◄', ... }
LEFT = dict(pairwise(['►', '▲', '◄', '▼', '►']))
# Same for the right direction : { '►':'▼', '▼':'◄', ... }
RIGHT = dict(pairwise(['►', '▼', '◄', '▲', '►']))

# Translates directions into vectors and vice versa
MOVE_DIR = { '►' : (1,0), '◄' : (-1,0), '▲' : (0,-1), '▼' : (0,1),
            (1,0) : '►', (-1,0) : '◄', (0,-1) : '▲', (0,1) : '▼' }

# Used to compute on which 'side' of the contour the red and green tiles are
TURN_DIR = { 1:'R', -1:'L' }

# Used to determine before_dirs in compute_tile_info
BEFORE = { 'R' : LEFT, 'L' : RIGHT }

def sign(x):
    """
    Returns 1 if x is positive, -1 if negative and 0 otherwise.
    """
    return (x > 0) - (x < 0)

def shift(subscriptable_collection, shift_dir):
    """
    Shift a collection by one offset either to the right or to the left.
    shift_dir='right' ['A','B','C','D'] ──► ['D','A','B','C']
    shift_dir='left'  ['A','B','C','D'] ──► ['B','C','D','A']
    """
    if shift_dir == 'right':
        return [ subscriptable_collection[-1] ] + subscriptable_collection[:-1]
    if shift_dir == 'left':
        return subscriptable_collection[1:] + [ subscriptable_collection[0] ]

def cycled_window(subscriptable_collection):
    """
    Returns all adjacent pairs of an iterable as if it were a cycled collection.
    The pair (X[-1],X[0]) is also returned in addition to all conventional pairs (X is the collection).
    This is useful to translate the collection of tiles into a collection of segments (a succession of 2 tiles forms a segment).
    """
    return list(pairwise(subscriptable_collection + [ subscriptable_collection[0] ]))

def corner_dir(dir_before, dir_after):
    """
    Returns a turn direction, either 1 (Right) or -1 (Left), for a sequel of directions represented by one of ► ▼ ◄ ▲.
    """
    return (dir_after == RIGHT[dir_before]) - (dir_after == LEFT[dir_before])

def calculate_segment_dir(start, end):
    """
    Returns the direction that translates the movement from tile_a to tile_b.
    For instance : start = (1,10) end = (5,5) will produce (1,-1).
    """
    return ( sign(end[0] - start[0]), sign(end[1] - start[1]) )

def compute_tile_info(red_tiles):
    """
    Computes the global direction towards which the red and green tiles are present when going through each segment of the contour formed by red tiles.
    Returns as well a dictionary that contains for each tile (key) :
    - the direction from the previous tile (one of ► ▼ ◄ ▲)
    - the direction to the next tile (one of ► ▼ ◄ ▲)
    - the turn made by the contour in this tile (either 'R' or 'L')
    - the position of the next tile (represented by (X,Y))

    Example :                               ┌─►X
    ..............      ......┌◄......      ▼
    .......Axxxx..      ......▼LxxxL..      Y
    .......xxxxx..      .......xxxxx..
    ..xxxxxBxxxx..  ──► ..LxxxxR▼xxx..  ──► dict[(X_A, Y_A)] = ('◄', '▼', 'L', (X_B, Y_B))
    ..xxxxxxxxxx..      ..xxxxx◄┘xxx..      dict[(X_B, Y_B)] = ('▼', '◄', 'R', (X_C, Y_C))
    ..xxxxxxxxxx..      ..LxxxxxxxxL..      inner_dir = 'L' (5L + 1R)
    ..............      ..............      the sum of turns will always be either 4R or 4L
    """
    all_segments = cycled_window(red_tiles)
    segment_ends = shift(red_tiles, 'left')
    after_dirs = list(map(lambda vect : MOVE_DIR[vect], starmap(calculate_segment_dir, all_segments)))
    turns = list(starmap(corner_dir, cycled_window(shift(after_dirs, 'right'))))
    turn_dirs = list(map(lambda t : TURN_DIR[t], turns))
    before_dirs = list(starmap(lambda td, ad: BEFORE[td][ad], zip(turn_dirs, after_dirs)))
    inner_dir = TURN_DIR[sum(turns) // 4]
    return inner_dir, dict(zip(red_tiles, zip(before_dirs, after_dirs, turn_dirs, segment_ends)))

def rectangle_fits_tiles(before_dir, after_dir, rect_dir):
    """
    Checks that the rectangle fits the tiles properties.
    This check lets us avoid trying to form a rectangles using AB in configurations similar to :
    xxx......       xxxxx....       .........
    xxx......       x#xxA....       xxA......
    xxA......       xx.......       xxx......
    .....Bxxx       xx.......       xx#xxxB..
    .....xxxx       x#xxxxB..       xxxxxxx..
    .....xxxx       xxxxxxx..       xxxxxxx..
    """
    before_vect, after_vect = MOVE_DIR[before_dir], MOVE_DIR[after_dir]
    return ((-1 * before_vect[0] + after_vect[0]) == rect_dir[0]) \
        and ((-1 * before_vect[1] + after_vect[1]) == rect_dir[1])

def filter_combination(tile_combination, inner_dir, segments):
    """
    Checks that a combination of two tiles produces a rectangle which only uses red and green tiles.
    """
    (start_tile_X, start_tile_Y), (end_tile_X, end_tile_Y) = tile_combination

    # compute the rectangle coordinates
    X_min, Y_min = min(start_tile_X, end_tile_X), min(start_tile_Y, end_tile_Y)
    X_max, Y_max = max(start_tile_X, end_tile_X), max(start_tile_Y, end_tile_Y)

    # eventhough a rectangle consisting of a single line is valid, it's very unlikely to be the answer
    if X_min == X_max or Y_min == Y_max:
        return False

    # both tiles should be well positioned to form a rectangle
    for tile, other_tile in zip(tile_combination, tile_combination[::-1]):
        before_dir, after_dir, seg_turn, _ = segments[tile]
        is_perfect_turn = rectangle_fits_tiles(before_dir, after_dir, calculate_segment_dir(tile, other_tile))
        if seg_turn == inner_dir:
            if not is_perfect_turn:
                return False
        else:
            if is_perfect_turn:
                return False

    for seg_start, (_, _, seg_turn, seg_end) in segments.items():
        seg_start_X, seg_start_Y = seg_start
        seg_end_X, seg_end_Y = seg_end
        # there should be no tiles inside the rectangle (excluding the sides)
        if X_min < seg_start_X < X_max and Y_min < seg_start_Y < Y_max:
            return False
        
        # there should be no tiles on the side of the rectangle producing an inner turn (*)
        if (seg_start_X in [X_min, X_max]) and Y_min < seg_start_Y < Y_max and seg_turn == inner_dir:
            return False
        if (seg_start_Y in [Y_min, Y_max]) and X_min < seg_start_X < X_max and seg_turn == inner_dir:
            return False
        
        # there should be no segment going through the rectangle (**)
        if seg_start_X < X_min and X_max < seg_end_X and Y_min < seg_start_Y < Y_max:
            return False
        if seg_end_X < X_min and X_max < seg_start_X and Y_min < seg_start_Y < Y_max:
            return False
        if X_min < seg_start_X < X_max and seg_start_Y < Y_min and Y_max < seg_end_Y:
            return False
        if X_min < seg_start_X < X_max and seg_end_Y < Y_min and Y_max < seg_start_Y:
            return False
    
    """
    (*) : assuming the following scenario, if the tile A produces an inner turn, the rectangle will be "eaten" a bit.
    The only solution is for the tile A to produce an outer turn.
    .........       .........       .........
    ..#xxxx..       ..#xxxx..       ...#xxxx.
    ..xxxxx..       ..xxxxx..       ...xxxxx.
    ..xxxxx..       .....xx..       .xxxxxxx.
    ..Axxxx..       ..Axxxx..       .xxAxxxx.
    ..xxxx#..       ..xxxx#..       ...xxxx#.
    .........       .........       .........
    scenario        inner turn      outer turn

    (**) : there is an edge case that would still count as a valid rectangle eventhough it's crossed by segments.
    xxx......
    xxAxxxxB.       Here trying to form a rectangle using A and F would technically be legal.
    xDxxxxxC.       But this same rectangle is crossed by the CD segment.
    xExxxF...
    xxxxxx...
    xxxxxx...
    The input does not contain such cases fortunately though.
    (All tiles are separated by at least one space in between them which prevents this scenario.)
    """
    return True

def calculate_rectange_size(tile_a, tile_b):
    """
    Returns the size of the rectangle made using two tiles as opposite corners.
    """
    return (abs(tile_a[0] - tile_b[0]) + 1) * (abs(tile_a[1] - tile_b[1]) + 1)

# [ (7,1), (11,1), ... ]
red_tiles = list(map(lambda line : tuple(map(int, line.strip().split(','))), open(FILENAME, 'r')))

# [ ((7,1), (11,1)), ((7,1), (11,7)), ... ]
all_tiles_combinations = list(combinations(red_tiles, 2))

# [ 5, 35, ... ]
rect_sizes = starmap(calculate_rectange_size, all_tiles_combinations)

# compute tile informations by 'going along the whole contour' 
inner_dir, tiles_info = compute_tile_info(red_tiles)

# filter combinations to keep rectangles that would only use green and red tiles
valid_tiles_combinations = list(filter(lambda comb : filter_combination(comb, inner_dir, tiles_info), all_tiles_combinations))
valid_rect_sizes = list(starmap(calculate_rectange_size, valid_tiles_combinations))

print(f"Part 1 : {max(rect_sizes)}")
print(f"Part 2 : {max(valid_rect_sizes)}")
