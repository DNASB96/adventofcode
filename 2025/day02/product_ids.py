import sys
import itertools

def inclusive_range(start, stop):
    return range(start, stop + 1)

def is_invalid(product_id):
    """
    Checks whether slicing a product id in the middle produces two identical patterns.
    """
    middle_slice_idx = len(product_id) // 2
    return product_id[:middle_slice_idx] == product_id[middle_slice_idx:]

def is_invalid_2(product_id):
    """
    Checks whether a product id consists in a pattern repetition.
    """
    # Pattern can be up to half of the ID to be a case for repetition.
    for pattern_size in range(1, 1 + len(product_id) // 2):
        if len(product_id) % pattern_size == 0:
            # Check whether each of the ID digit matches the current pattern.
            pattern_it = itertools.cycle(product_id[:pattern_size])
            non_matching_chars = list(itertools.dropwhile(lambda id_digit : id_digit == next(pattern_it), product_id))
            if not len(non_matching_chars):
                return True
    return False

def check_product_ids(id_ranges):
    """
    Checks all product ranges for invalid ids.
    """
    invalid_products, all_invalid_products = [], []
    for id_range in id_ranges:
        for product_id in id_range:
            if is_invalid(str(product_id)):
                invalid_products.append(product_id)
            if is_invalid_2(str(product_id)):
                all_invalid_products.append(product_id)
    return invalid_products, all_invalid_products

filename = "input" if "input" in sys.argv else "example"

# ['10-12', ...]
data = list(map(lambda line : line.split(','), open(filename, 'r')))[0] # input is a single line

# [range(10,13), ...]
id_ranges = list(map(lambda id_range : inclusive_range(*map(int, id_range.split('-'))), data))

# [11, ...]
invalid_ids, all_invalid_ids = check_product_ids(id_ranges)

print(f"Part 1 : {sum(invalid_ids)}")
print(f"Part 2 : {sum(all_invalid_ids)}")

"""
# Using map/compress instead of the check_product_ids function.

# [[False, True, False], ...]
validities = list(map(lambda id_range : list(map(is_invalid, id_range)), id_ranges))

# [[11], ...]
invalid_ids = list(map(lambda z : itertools.compress(*z), zip(id_ranges, validities)))
total = sum(map(sum, invalid_ids))
"""
