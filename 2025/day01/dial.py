import re
import sys

# Left means substract, Right means add
TURN_DIRECTION = { 'L':-1, 'R':1 }

def read_input():
    """
    Returns the list of rotations as list(tuple('R'|'L', int)).
    """
    rotations = []
    pattern = r"([RL])([0-9]+)"
    filename = sys.argv[1] if len(sys.argv) > 1 else "example"
    with open(filename, 'r') as file:
        for line in file:
            match = re.search(pattern, line)
            rotations += [ ( match.group(1) , int(match.group(2)) ) ]
    return rotations

def rotate_dial(dial_position, rotation):
    """
    Computes the new dial position between 0 and 99.
    Returns the new position and the number of times the dial passed over 0 without stopping.
    """
    full_rotation_count = rotation[1] // 100
    rotation_remainder = rotation[1] % 100
    new_position = dial_position + TURN_DIRECTION[rotation[0]] * rotation_remainder

    # Only count cases where the rotation does not stop at position 0
    zero_transition_count = int(dial_position != 0 and new_position < 0) \
                            + int(dial_position != 100 and 100 < new_position) \
                            + full_rotation_count

    # Make sure the position is between 0 and 99
    return ( 100 + new_position ) % 100, zero_transition_count

data = read_input()
dial_position = 50
stopped_at_zero_count, zero_transition_total = 0, 0

for rotation in data:
    dial_position, r_zero_transition_count = rotate_dial(dial_position, rotation)
    stopped_at_zero_count += not dial_position
    zero_transition_total += r_zero_transition_count

print(f"Part 1 : actual password = {stopped_at_zero_count}")
print(f"Part 2 : method 0x434C49434B = {zero_transition_total + stopped_at_zero_count}")
