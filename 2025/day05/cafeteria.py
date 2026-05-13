import sys
import functools

FILENAME = sys.argv[1] if len(sys.argv) > 1 else "example"

def get_fresh_ingredients(id_ranges, ingredients_ids):
    """
    Returns the fresh ingredients ids - the ones contained in id_ranges.
    """
    fresh_ingredients = set()
    for ingredient in ingredients_ids:
        for fresh_range in id_ranges:
            if fresh_range[0] <= ingredient <= fresh_range[1]:
                fresh_ingredients.add(ingredient)
    return fresh_ingredients

def merge_ranges(reduced_ranges, single_range):
    """
    Merges the ranges until there is no overlap between them.

    This function is to be used in a functools.reduce(...) statement, thus the same format is expected for both parameters :
    reduced_ranges = [ (3-5), (10-14) ]   single_range = [ (8-12) ]
    In this case, the end result will be : [ (3-5), (8-14) ].
    """
    single_lower, single_upper = single_range[0]

    for idx, (merged_lower, merged_upper) in enumerate(reduced_ranges):
        if merged_lower <= single_lower <= merged_upper \
            or merged_lower <= single_upper <= merged_upper \
            or ( single_lower <= merged_lower and merged_upper <= single_upper):
            
            # remove the range that gets merged into the single one
            reduced_ranges_without = reduced_ranges[:idx] + reduced_ranges[idx + 1:]
            modified_range = [ (min(merged_lower, single_lower), max(merged_upper, single_upper)) ]

            # merge recursively to check if the new modified range collides with yet another range
            return merge_ranges(reduced_ranges_without, modified_range)
    
    # no overlap between ranges has been found
    return [ *reduced_ranges, *single_range ]

# [ '3-5', '10-14', ..., '1', '5', ... ]
database = list(map(lambda line : line.strip(), open(FILENAME, 'r')))
split_index = database.index('')

# [ (3,5), (10,14), ... ]
id_ranges = list(map(lambda line : tuple(map(int, line.split('-'))), database[:split_index]))

# [ 1, 5, ... ]
ingredients_ids = list(map(int, database[split_index + 1:]))

# { 5, ... }
fresh_ingredients = get_fresh_ingredients(id_ranges, ingredients_ids)

# [ [(3,5)], [(10,14)], [(16,20)], [(12-18)] ]
wrapped_ranges = list(map(lambda r : [ r ], id_ranges))

# [ [(3,5), (10,20)] ]
merged_ranges = functools.reduce(merge_ranges, wrapped_ranges)

# 3 + 11 = 14
fresh_ids_count = sum(map(lambda r : r[1] - r[0] + 1, merged_ranges))

print(f"Part 1 : {len(fresh_ingredients)}")
print(f"Part 2 : {fresh_ids_count}")
