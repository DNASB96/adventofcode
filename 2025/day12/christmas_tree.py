import operator
import re
import sys
from functools import reduce
from itertools import chain, starmap

def read_input():
    """
    Reads the input and returns a list of presents shapes and a list of regions informations.

    The present shape is represented as a list of strings.
    The list of regions informations contains for each one of them :
    - a tuple representing its size
    - a list of the number of presents to place in that region
    """
    filename = sys.argv[1] if len(sys.argv) > 1 else "example"
    presents_shapes, regions_infos = list(), list()
    patterns = {
        'shape_index': r'^([0-9]):$',
        'shape_pattern': r'^([\#\.]+)$',
        'region': r'^([0-9]+)x([0-9]+): (.+)$',
    }
    with open(filename, 'r') as f:
        for line in f:
            for match_case, regex_pattern in patterns.items():
                regex_match = re.match(regex_pattern, line)
                if regex_match:
                    match match_case:
                        case 'shape_index':
                            presents_shapes.append([])
                        case 'shape_pattern':
                            presents_shapes[-1].append(regex_match.group(1))
                        case 'region':
                            region_shape = int(regex_match.group(1)), int(regex_match.group(2))
                            presents_to_fit = list(map(int, regex_match.group(3).split(' ')))
                            regions_infos.append((region_shape, presents_to_fit))
    return presents_shapes, regions_infos

def get_shape_min_size(shapes):
    """
    Returns the number of # in a present shape.
    """
    return len(list(filter(lambda c : c == '#', chain.from_iterable(shapes))))

def can_fit(presents_shapes, region_info):
    """
    Returns True if the region can fit all its presents, False otherwise.

    Looks at the maximum available space in the region and check the minimum space required to place all presents.
    (Assuming the presents would fit perfectly together)

    Looking at these informations reveals regions' presents either take:
    - more than 100% of the region maximum capacity
    - less than 75% of the region maximum capacity
    
    Counting the number of region with less than 75% occupied capacity solves the puzzle.
    """
    region_sizes, presents_counts = region_info
    region_capacity = reduce(operator.mul, region_sizes)
    presents_min_required_capacity = list(map(get_shape_min_size, presents_shapes))
    required_capacity = sum(starmap(operator.mul, zip(presents_counts, presents_min_required_capacity)))

    # get the percentage of the region filled by presents (2 decimals for readability)
    fill_ratio = int(10000 * required_capacity / region_capacity) / 100
    print(f"(max capacity) {region_capacity} >? {required_capacity} (req capacity) ──► {fill_ratio=}")
    if fill_ratio > 100:
        return False
    else:
        return True

# presents_shapes : [ ['###', '##.', '##.'], ... ]
# regions : [ ((4, 4), [0, 0, 0, 0, 2, 0]), ... ]
presents_shapes, regions_infos = read_input()

# [ True, True, False, ... ]
fits = list(map(lambda reg : can_fit(presents_shapes, reg), regions_infos))

print(f"Part 1 : {sum(fits)}")
print(f"Part 2 : {None}")
