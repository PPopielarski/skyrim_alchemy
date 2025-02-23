from DataHandler import DataHandler
import itertools


def get_common_effects(ingredient1, ingredient2):
    """Returns set of effects created by combination of two ingredients"""
    effects_ing1 = set()
    effects_ing2 = set()
    data_handler = DataHandler()
    for effect in data_handler.alchemy_effects_to_ingredients_dict:
        if ingredient1 in data_handler.alchemy_effects_to_ingredients_dict[effect]:
            effects_ing1.add(effect)
        if ingredient2 in data_handler.alchemy_effects_to_ingredients_dict[effect]:
            effects_ing2.add(effect)
    return effects_ing1.intersection(effects_ing2)


def get_possible_effects_combinations(selected_ingredients_set):
    """Returns dict effect -> set of pairs of ingredients (tuples)"""
    effects_to_ingredients = dict()
    for pair in itertools.combinations(selected_ingredients_set, 2):
        effects_list = get_common_effects(pair[0], pair[1])
        for effect in effects_list:
            if effect in effects_to_ingredients.keys():
                effects_to_ingredients[effect].add(pair)
            else:
                effects_to_ingredients[effect] = {pair, }
    return effects_to_ingredients
