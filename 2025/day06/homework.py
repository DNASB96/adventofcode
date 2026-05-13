import functools
import operator
import re
import sys
from itertools import chain
from more_itertools import split_into

FILENAME = sys.argv[1] if len(sys.argv) > 1 else "example"

# Useage : OPERATORS['+']( [1, 9, 56, ... 8] )
# Compute the sum/multiplication of all numbers in the parameter list
OPERATORS = {
    '+' : lambda numbers : functools.reduce(operator.add, numbers),
    '*' : lambda numbers : functools.reduce(operator.mul, numbers)
}

def convert(line):
    """
    Converts a line depending on its type :
    123 38 1 64 ───► [ 123, 38, 1, 64 ]
    *   +  * +  ───► [ '*', '+', '*', '+' ]
    """
    return list(map(lambda item : int(item) if item.isdigit() else item, re.split(r'[\s]+', line.strip())))

def solve(homework):
    """
    Computes each math problem like a human would read the homework and returns a list containing all results.
    """
    return list(map(lambda column : OPERATORS[column[-1]](column[:-1]), zip(*homework)))

def read_and_solve_cephalopodically(homework):
    """
    Reads numbers vertically and solves each math problem like a proper cephalopod.

    The comments following assume this input :
    ┌────────────┐
    │123 38 1 64 │
    │ 45 4  7 23 │
    │  6 8  5 314│
    │*   +  * +  │
    └────────────┘
    """
    
    # Counting spaces after each operator gives us the count of numbers used for that problem
    # [ '   ', '  ', ' ', '   ' ]
    spaces_after_each_op = re.split(r'[\*\+]', homework[-1])[1:]

    # The last problem is an exception though as it lacks a space to match its numbers count
    spaces_after_each_op[-1] += ' '

    # [ 3, 2, 1, 3 ] - first problem contains 3 numbers (1, 24, 356), second one contains 2, etc.
    op_lengths = list(map(len, spaces_after_each_op))

    # [ '*', '+', '*', '+' ]
    operators = convert(homework[-1])

    # [ '123 38 1 64 ', ' 45 4  7 23 ', '  6 8  5 314' ]
    numbers_lines = homework[:-1]

    # [ '1  ', '24 ', '356', '   ', '348', '8  ', '   ', '175', '   ', '623', '431', '  4' ]
    numbers_read_by_column = list(map(lambda number_column : ''.join(number_column), zip(*numbers_lines)))

    # [ 1, 24, 356, 348, 8, 175, 623, 431, 4 ]
    numbers = list(map(int, filter(lambda item : item.strip().isdigit(), numbers_read_by_column)))
    
    # [ [1, 24, 356], [348, 8], [175], [623, 431, 4] ]
    numbers_batches = list(split_into(numbers, op_lengths))

    # [ 8544, 356, 175, 1058 ]
    return list(map(lambda zipped : OPERATORS[zipped[1]](zipped[0]), zip(numbers_batches, operators)))

# [ [123, 38, 1, 64], [45, 4, 7, 23], [6, 8, 5, 314], ['*', '+', '*', '+'] ]
homework_sheet = list(map(convert, open(FILENAME, 'r')))

# [ '123 38 1 64 ', ' 45 4  7 23 ', '  6 8  5 314', '*   +  * +  ' ]
homework_lines = list(chain.from_iterable(map(lambda line : line.splitlines(), open(FILENAME, 'r'))))

print(f"Part 1 : {sum(solve(homework_sheet))}")
print(f"Part 2 : {sum(read_and_solve_cephalopodically(homework_lines))}")
