import re
import sys
from itertools import pairwise
from more_itertools import transpose
from collections import defaultdict

FILENAME = sys.argv[1] if len(sys.argv) > 1 else "example"

def replace_spot(line_idx, col_idx, subst, manifold):
    """
    Replace the n-th character of a string with subst.
    """
    manifold[line_idx] = manifold[line_idx][:col_idx] + subst + manifold[line_idx][col_idx+1:]

def analyze_splitting(manifold):
    """
    Calculates the beams propagation through the manifold.

    Returns a dictionary containing the number of timelines active for each position (x, y) the tachyon particle ends up in.
    ┌──────► y
    │┌───────┐       ┌───────┐
    ││...S...│       │...S...│
    ││.......│       │...|...│
    ││...^...│       │..|^|..│
    ││.......│ ───►  │..|.|..│
    ││..^....│       │.|^||..│
    ▼│.......│       │.|.||..│
    x└───────┘       └───────┘
    """
    timelines = defaultdict(int)

    # operate two lines at a time, modifications of the manifold are made in the bottom line
    # while the top one is used for checking whether the beam is present
    for top_idx, bot_idx in pairwise(range(len(manifold))):
        for col_idx, _ in enumerate(manifold[bot_idx]):
            if manifold[top_idx][col_idx] == 'S':
                timelines[(top_idx, col_idx)] = 1

            # advance beams further
            if manifold[top_idx][col_idx] in ['S', '|'] and manifold[bot_idx][col_idx] in ['.', '|']:
                replace_spot(bot_idx, col_idx, '|', manifold)
                timelines[(bot_idx, col_idx)] += timelines[(top_idx, col_idx)]
            
            if manifold[top_idx][col_idx] == '|' and manifold[bot_idx][col_idx] == '^':
                if col_idx > 0 and manifold[bot_idx][col_idx-1] in ['.', '|']: # split left
                    replace_spot(bot_idx, col_idx-1, '|', manifold)
                    timelines[(bot_idx, col_idx-1)] += timelines[(top_idx, col_idx)]
                if col_idx < len(manifold[0]) - 1 and manifold[bot_idx][col_idx+1] in ['.', '|']: # split right
                    replace_spot(bot_idx, col_idx+1, '|', manifold)
                    timelines[(bot_idx, col_idx+1)] += timelines[(top_idx, col_idx)]
    return timelines

def count_beam_splitting(manifold):
    """
    Count the number of occurences of beam '|' coming into splitters '^'.
    """
    transposed = map(lambda lst : ''.join(lst), transpose(manifold))
    splits_counts = map(lambda line : len(re.findall(r'\|\^', line)), transposed)
    return sum(splits_counts)

def display(manifold):
    print('\n'.join(manifold))

# [ '..S..', '.....', etc ]
manifold = list(map(lambda line : line.strip(), open(FILENAME, 'r')))
timelines_dict = analyze_splitting(manifold)

# retrieve the number of timelines for each position in the last line
completed_timelines = list(filter(lambda item : item[0][0] == len(manifold)-1, timelines_dict.items()))
timelines_count = sum(map(lambda item : item[1], completed_timelines))

display(manifold)

print(f"Part 1 : {count_beam_splitting(manifold)}")
print(f"Part 2 : {timelines_count}")

