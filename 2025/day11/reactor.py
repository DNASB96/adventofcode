import re
import sys
from collections import defaultdict

FILENAME = sys.argv[1] if len(sys.argv) > 1 else "example"

def read_input(filename):
    """
    Returns a dict that contains for each device, the list of other devices connected to its output.
    """
    devices_connections = dict()
    with open(filename, 'r') as f:
        for line in f:
            match = re.search(r'(.{3}): (.+)$', line)
            devices_connections[match.group(1)] = match.group(2).split(' ')
    return devices_connections

def dfs_visit(node, devices_connections):
    """
    Returns all paths from the input node to the node labeled 'out'.
    """
    if node == 'out':
        return [ [ node ] ]

    paths = []
    for child_node in devices_connections[node]:
        for path in dfs_visit(child_node, devices_connections):
            paths.append( [ node, *path ] )
    return paths

def bfs_visit(devices_connections):
    """
    Builds a dictionary containing for each node a nested dictionary that tracks the number of paths to that node.
    The number of paths is given in 4 differents entries depending on which nodes among fft and dac have been traversed.

    Example :
    {
        'aaa' : {'': 1, 'fft': 0, 'dac': 0, 'fftdac': 0}),
        'dac' : {'': 0, 'fft': 0, 'dac': 2, 'fftdac': 0}),
        ...,
        'xyz' : {'': 0, 'fft': 1, 'dac': 2, 'fftdac': 3}),
    }

    This means there are :
    - 0 paths going to xyz that went through none of fft and dac
    - 1 paths going to xyz that only went through fft
    - 2 paths going to xyz that only went through dac
    - 3 paths going to xyz that went through both fft and dac
    """
    nodes_to_visit = { 'svr' }
    dict_keys = ['', 'fft', 'dac', 'fftdac']
    paths_counts = defaultdict(lambda : defaultdict(int))
    paths_counts['svr'][''] = 1
    while len(nodes_to_visit):
        # use a set in case to prevent visiting a node twice in a single iteration
        next_visits = set()
        for parent_node in nodes_to_visit:
            if parent_node != 'out':
                for child_node in devices_connections[parent_node]:
                    match child_node:
                        case 'fft':
                            paths_counts['fft']['fft'] += paths_counts[parent_node]['']
                            paths_counts['fft']['fftdac'] += paths_counts[parent_node]['dac']
                        case 'dac':
                            paths_counts['dac']['dac'] += paths_counts[parent_node]['']
                            paths_counts['dac']['fftdac'] += paths_counts[parent_node]['fft']
                        case _:
                            for key in dict_keys:
                                paths_counts[child_node][key] += paths_counts[parent_node][key]
                    next_visits.add(child_node)
                
                # reset the parent_node in case it gets revisited in the future
                for key in dict_keys:
                    paths_counts[parent_node][key] = 0
        nodes_to_visit = next_visits
    return paths_counts

# dict holding the links between devices
devices_connections = read_input(FILENAME)

# the given example for part 2 differs from the one in part 1
devices_connections_p2 = read_input("example_2") if FILENAME == "example" else devices_connections

# [ ['you', 'qsz', ..., 'wkq', 'out'], ... ]
paths_from_you_to_out = dfs_visit('you', devices_connections)

# { 'svr': {'':1, 'fft':0, 'dac':0, 'fftdac':0}, ...}
paths_counts = bfs_visit(devices_connections_p2)

print(f"Part 1 : {len(paths_from_you_to_out)}")
print(f"Part 2 : {paths_counts['out']['fftdac']}")
