import sys
import itertools

FILENAME = sys.argv[1] if len(sys.argv) > 1 else "example"

def get_two_battery_joltage(power_bank):
    """
    Get the maximum joltage of a bank when turning on 2 batteries.
    """
    first_battery = max(power_bank[:-1])
    second_battery = max(power_bank[power_bank.index(first_battery) + 1:])
    return int(first_battery + second_battery)

def get_bank_repr(power_bank, activations):
    """
    Returns a visual representation of the activated state of a battery bank.
    
    │234234234234278│ battery bank
    │xxx    x   x xx│ activated batteries
    '234    3   4 78' returned string
    """
    return ''.join(list(itertools.starmap(lambda bat, act : bat if act else ' ', zip(power_bank, activations))))

def get_bank_joltage(power_bank, activations):
    """
    Returns the joltage of a power bank given the configuration of activated batteries.
    
    │234234234234278│ battery bank
    │xxx    x   x xx│ activated batteries ─► returns 2343478
    """
    return int(get_bank_repr(power_bank, activations).replace(' ', ''))

def get_n_batteries_joltage(power_bank, activation_count = 12):
    """
    Get the maximum joltage of a bank when turning on a set amount of batteries.

    The idea is to shift the activated batteries from left to right.
    To do so, we check each battery one by one, and for each we ask ourselves :
    "Would turning off batteries that are on its left increase the joltage?"

    Here is how one iteration works :
    target_idx ─┐ ┌─ bat_idx
                ▼ ▼
            │818117111111111│ battery bank (20)
            │8 811711       │ currently active batteries BEFORE iteration (7)
            │8_8            │ (A) unchanged batteries (2 ON │ 1 OFF)
            │   __          │ (B) turn off batteries from (target_idx) to (bat_idx - 1)
            │     71111     │ (C) activate batteries from bat_idx until enough are ON (7 (total) - 2 (A) => 5 needed)
            │          _____│ (D) make sure the remaining batteries are all OFF
            │8 8  71111     │ resulting active batteries
    """

    # Start with turning the first N batteries of the battery bank - 1 is ON │ 0 is OFF
    # [ 1, 1, 1, ... 1, 1, 0, 0, 0, ... 0 ]
    activations = [ 1 ] * activation_count + [ 0 ] * (len(power_bank) - activation_count)

    for bat_idx, battery in enumerate(power_bank):
        changed = False
        for target_idx, is_activated in enumerate(activations[:bat_idx]):
            if not changed and is_activated:
                # count A-ON
                unchanged_active_batteries_count =  sum(activations[:target_idx])
                # count B
                off_batteries_count = bat_idx - target_idx
                # count C
                shifted_batteries_count = activation_count - unchanged_active_batteries_count
                # count D
                remaining_off_batteries_count = len(power_bank) - (target_idx + off_batteries_count + shifted_batteries_count)

                # Compute B
                modified_activations = activations[:target_idx] + [ 0 ] * off_batteries_count + activations[bat_idx:]
                # Compute C
                newly_activated_batteries = [ 1 ] * (activation_count - sum(modified_activations[:bat_idx]))
                # Compute D
                remaining_batteries = [ 0 ] * (len(power_bank) - len(modified_activations[:bat_idx]) - len(newly_activated_batteries))
                # A+B+C+D
                modified_activations = modified_activations[:bat_idx] + newly_activated_batteries + remaining_batteries

                """
                We compare both total and battery joltage : total is obvious, we need to increase the joltage as much as possible ;
                
                Updating the activations only when the battery joltage STRICTLY increases lets us avoid cases such as :
                target_idx ─┐ ┌─ bat_idx
                            ▼ ▼
                           │818711  │ ─► 818711 vs 871111 ─► would update as |  871111|
                This way, we select the leftmost battery with maximum individual joltage.

                target_idx >= unchanged_active_batteries_count : this means "having enough place on the left side for (A)"
                remaining_off_batteries_count >= 0             : this means "having enough place on the right side for (D)"
                """
                if battery > power_bank[target_idx] \
                    and get_bank_joltage(power_bank, modified_activations) > get_bank_joltage(power_bank, activations) \
                    and target_idx >= unchanged_active_batteries_count \
                    and remaining_off_batteries_count >= 0:

                    activations = modified_activations
                    changed = True

        """bat_idx
              ▼
        │11211311911│ If all batteries on the right of the one we are currently checking are ON,
        │     311911│ then we cannot shift further => stop searching and return instead."""
        if sum(activations[bat_idx:]) == len(activations[bat_idx:]):
            return get_bank_joltage(power_bank, activations)

    return get_bank_joltage(power_bank, activations)

def get_n_batteries_joltage_alternative(power_bank, activation_count = 12):
    """
    This is the same function as the precedent one, I just thought of another way to implement it while commenting the code.
    This is both way more simpler and efficient than the previous version, I wish i had thought of that earlier. -_-

    Here is an example with activation_count=7 :
    │   power bank  │ battery       ┌─────────────────────┐
    │818181911112111│               │   search interval   │
    │8--------      │ 0             │  ┌───────────────┐  │
    │ -8-------     │ 1             │  ▼               ▼  │
    │   -8------    │ 2             │  --------6--------  │
    │     -9-----   │ 3             │  ▲       ▲        ▲ │
    │       ----2-  │ 4             │start     │       end│
    │            1- │ 5             │          │          │
    │             1-│ 6             │  activated battery  │
                                    └─────────────────────┘

    │8 8 8 9    211 │ resulting activations
    """
    activated_batteries_joltages = []
    start, end = 0, len(power_bank) - activation_count + 1

    for _ in range(activation_count):
        search_interval = power_bank[start:end]
        activated_batteries_joltages.append(max(search_interval))

        start += 1 + power_bank[start:].index(activated_batteries_joltages[-1])
        end += 1

    return int(''.join(activated_batteries_joltages))

# ['234234234234278', ...]
data = list(map(lambda line : line.strip(), open(FILENAME, 'r')))

# [78, ...]
simple_joltages = list(map(get_two_battery_joltage, data))

# [434234234278, ...]
hyper_joltage = list(map(get_n_batteries_joltage, data))

# [434234234278, ...]
omega_joltage = list(map(get_n_batteries_joltage_alternative, data))

print(f"Part 1 : {sum(simple_joltages)}")
print(f"Part 2 : {sum(hyper_joltage)}")
print(f"Part 2 : {sum(omega_joltage)} (alternative)")

"""
Notes for Part 2 :
I initially thought getting the maximum of itertools.combinations(power_bank, 12) would be super straightforward
but it takes way too long to compute (100 digits per bank in the real input ─► 1 050 421 051 106 700 combinations).

⣿⣿⡙⠿⠿⠶⢒⣤⣶⣿⣿⢻⣿⣿⣿⣷⣮⡻⣷⣬⠰⣶⣭⡛⢿⣿⣿
⣿⣿⣷⣬⡟⣩⣿⣿⣿⣿⢏⣿⣿⡿⢿⣿⣿⣿⣎⢿⣷⡹⣿⣿⣮⡻⣿
⣿⣿⣿⡿⣸⣿⣿⣿⣿⡿⢸⣿⣿⣿⢸⣿⣿⣿⣿⣦⢻⣷⡹⣿⣿⣿⡙
⣿⣿⠟⣱⣿⣿⡿⢸⡿⣣⣥⢉⣿⡟⣘⡻⣿⣿⢿⣿⣧⡹⣧⠻⣿⣿⣷
⡟⠫⠾⢡⣿⣹⢇⡿⢣⡆⡇⣿⣿⣧⠩⣥⣿⣿⢸⣿⣿⣷⢹⣆⣿⣿⣿
⣿⣿⡇⢸⡏⡟⠘⠱⣿⣷⠀⢻⣿⡏⣶⠱⢹⠏⣸⣿⢻⣿⠈⣿⢹⡻⣿
⣿⣿⢡⡌⣇⢠⣷⣦⠈⢻⣷⣥⡻⠏⣿⠷⠀⠘⠃⠻⢸⣿⠀⣿⢻⣷⡘
⣿⡟⠸⣷⡙⡞⢉⣠⣴⣾⣿⣿⣿⣿⣧⡀⠲⢿⣿⡇⣿⡿⣰⡟⣘⢿⣷
⣿⢠⡆⡹⠐⡝⣿⣿⡿⡿⡿⢿⡿⢿⣿⣿⣶⣄⡈⢸⠟⣱⣿⠇⣯⡀⠙
⡏⡘⡇⣷⠸⣿⣿⣿⡇⠀⠀⠀⠀⠀⠀⠈⢻⣿⣟⡝⣲⡇⣿⣿⠀⡿⠿⠋
⣷⣕⠇⣿⣧⠈⠻⣿⢠⣴⣶⣶⣶⣶⣦⡄⣿⣿⣿⠿⡃⣿⣿⠀⣵⣷⡄
⣿⡇⡇⢿⣿⢸⢸⡖⣴⣌⠙⠛⠛⠛⠛⣃⣩⣭⣶⣾⡇⣿⡿⠠⣫⡵⠀ 
"""
