from functools import reduce
import operator
import re
import sys
from z3 import Int, Solver, sat
from itertools import combinations_with_replacement, starmap

FILENAME = sys.argv[1] if len(sys.argv) > 1 else "example"
LIGHTS_KEY = 'indicator_lights_diagram'
BUTTONS_KEY = 'button_schematics'
JOLTAGE_KEY = 'joltage_requirements'

def read_input():
    """
    Reads the input and creates a dictionary for each machine containing the light diagram, the button schematics and the joltage requirements.
    """
    factory = list()
    with open(FILENAME, 'r') as f:
        for line in f:
            machine = dict()
            match = re.search(r'\[(.+)\] (.+) \{(.+)\}', line)
            schematics = match.group(2).replace('(','').replace(')','').split(' ')
            machine[LIGHTS_KEY] = list(map(lambda light : light == '#', match.group(1)))
            machine[BUTTONS_KEY] = list(map(lambda seq : list(map(int, seq.split(','))), schematics))
            machine[JOLTAGE_KEY] = list(map(int, match.group(3).split(',')))
            factory.append(machine)
    return factory

def configure_lights(machine):
    """
    Tests all combinations of buttons by gradually increasing the number of presses and returns the number
    of presses corresponding to the first combination that sets the light in the desired state.
    """
    number_of_presses = 0
    while True:
        number_of_presses += 1
        button_presses_combinations = list(combinations_with_replacement(machine[BUTTONS_KEY], number_of_presses))
        for button_presses in button_presses_combinations:
            lights_resulting_state = [ False ] * len(machine[LIGHTS_KEY])
            for button in button_presses:
                for light_idx in button:
                    lights_resulting_state[light_idx] = bool(1 - lights_resulting_state[light_idx])
            if lights_resulting_state == machine[LIGHTS_KEY]:
                return number_of_presses

def configure_joltage(machine):
    """
    Finds the minimum number of button presses to configure the joltage requirements of a machine.
    """
    buttons_names = list(starmap(lambda i, b : 'B' + str(i), enumerate(machine[BUTTONS_KEY])))
    button_presses_variables = list(map(Int, buttons_names))
    s = Solver()

    # constrain the number of presses of each button to be positive
    for unknown_var in button_presses_variables:
        s.add(unknown_var >= 0)

    # build a constraint that ties the joltage requirements with their respective buttons
    # Example : if buttons B1 and B4 are the only buttons affecting the first joltage requirement
    # and that requirement needs to be set at 12, then a constraint 'B1 + B4 == 12' will be added
    for req_idx, jolt_req in enumerate(machine[JOLTAGE_KEY]):
        constraint = 0
        for btn_idx, button in enumerate(machine[BUTTONS_KEY]):
            if req_idx in button:
                constraint += button_presses_variables[btn_idx]
        s.add(constraint == jolt_req)
    
    number_of_presses = 1
    while True:
        # add a constraint to set the total number of button presses
        temp_constraint = reduce(operator.add, button_presses_variables)
        s.push()
        s.add(temp_constraint == number_of_presses)

        # if satisfactory, we found the minimum number of button presses that solves the joltage requirements
        if s.check() == sat:
            return number_of_presses
        
        # remove the previous constraint if there is no solution
        s.pop()
        number_of_presses += 1

# list of machines
factory = read_input()

# configuring lights
lights_presses_counts = list(map(lambda machine : configure_lights(machine), factory))

# configuring joltage requirements
joltage_presses_counts = list(map(lambda machine : configure_joltage(machine), factory))

print(f"Part 1 : {sum(lights_presses_counts)}")
print(f"Part 2 : {sum(joltage_presses_counts)}")
