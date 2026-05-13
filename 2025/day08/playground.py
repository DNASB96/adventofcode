import functools
import operator
import math
import sys
from itertools import combinations, starmap

FILENAME = sys.argv[1] if len(sys.argv) > 1 else "example"

def calculate_distances(boxes_positions):
    """
    Calculate distances between all combinations of any 2 junction boxes.
    """
    segments = list(combinations(boxes_positions, 2))
    distances = starmap(math.dist, segments)
    return list(zip(distances, segments))

def connect_boxes(box_to_circuit_dict, circuit_to_box_dict, sorted_distances):
    """
    Connects the two junction boxes that are closest together if they are not already in the same circuit.
    """
    _, boxes = sorted_distances[0]
    new_circuit_name = max(circuit_to_box_dict.keys(), default=0) + 1
    connected_boxes = list(filter(lambda b : b in box_to_circuit_dict, boxes))
    unconnected_boxes = list(filter(lambda b : b not in box_to_circuit_dict, boxes)) 

    if len(connected_boxes) == 2:
        # connect the two existing circuits
        if box_to_circuit_dict[boxes[0]] != box_to_circuit_dict[boxes[1]]:
            kept_circuit = box_to_circuit_dict[boxes[0]]
            deleted_circuit = box_to_circuit_dict[boxes[1]]
            relocated_boxes = circuit_to_box_dict[deleted_circuit]
            
            circuit_to_box_dict.pop(deleted_circuit)
            for box in relocated_boxes:
                box_to_circuit_dict[box] = kept_circuit
                circuit_to_box_dict[kept_circuit].append(box)

    # add the unconnected box to the existing circuit
    if len(connected_boxes) == 1:
        circuit_name = box_to_circuit_dict[connected_boxes[0]]
        box_to_circuit_dict[unconnected_boxes[0]] = circuit_name
        circuit_to_box_dict[circuit_name].append(unconnected_boxes[0])

    # create a new circuit containing both boxes
    if len(connected_boxes) == 0:
        circuit_to_box_dict[new_circuit_name] = [ *boxes ]
        for box in unconnected_boxes:
            box_to_circuit_dict[box] = new_circuit_name
    return sorted_distances.pop(0)

def start_connecting(boxes_distances, connection_count):
    """
    Applies a set number of connections between junction boxes depending on their distance from each another.

    Holds two different dictionaries to track the circuits made between junction boxes :
    box_to_circuit_dict : key is a box coordinates (X,Y,Z) and returns the corresponding circuit name
    circuit_to_box_dict : key is the circuit name and returns a list of coordinates of the boxes in that circuit

    Circuits names starts from 1 and are incremented at each addition.
    """
    sorted_distances = sorted(boxes_distances, key=lambda distance : distance[0])
    box_to_circuit_dict, circuit_to_box_dict = dict(), dict()

    for _ in range(connection_count):
        connect_boxes(box_to_circuit_dict, circuit_to_box_dict, sorted_distances)
    
    return box_to_circuit_dict, circuit_to_box_dict, sorted_distances

def resume_connecting(box_to_circuit_dict, circuit_to_box_dict, sorted_distances, boxes_count):
    """
    Keep connecting until all junction boxes are in the same circuit.
    """
    while len(circuit_to_box_dict) != 1 or sum(list(map(len, circuit_to_box_dict.values()))) != boxes_count:
        last_connection_made = connect_boxes(box_to_circuit_dict, circuit_to_box_dict, sorted_distances)
    return last_connection_made

# [ (162, 817, 812), (57, 618, 57), (906, 360, 560), ... ]
junction_boxes = list(map(lambda line : tuple(map(int, line.strip().split(','))), open(FILENAME, 'r')))

connection_count = 1000 if FILENAME == 'input' else 10
boxes_distances = calculate_distances(junction_boxes)
box_to_circuit_dict, circuit_to_box_dict, sorted_distances = start_connecting(boxes_distances, connection_count)
top_three_circuits_sizes = list(sorted(map(len, circuit_to_box_dict.values()), reverse=True))[:3]

# retrieve the last 2 junction boxes that have been connected
_, (box_1, box_2) = resume_connecting(box_to_circuit_dict, circuit_to_box_dict, sorted_distances, len(junction_boxes))

print(f"Part 1 : {functools.reduce(operator.mul, top_three_circuits_sizes)}")
print(f"Part 2 : {box_1[0] * box_2[0]}")
