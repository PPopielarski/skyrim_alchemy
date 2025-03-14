import json
import os

class DataHandler:
    _instance = None
    _data_folder_path = "data"

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_data()
        return cls._instance

    def _init_data(self):
        file_path = f"{DataHandler._data_folder_path}/alchemy_effects.json"
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File {file_path} not found.")

        with open(file_path, "r", encoding="utf-8") as f:
            alchemy_effects_list = json.load(f)
            self.alchemy_effects_to_ingredients_dict = {
                item['name']: item['ingredients'] for item in alchemy_effects_list
            }
            self.alchemy_effects_to_effect_type_dict = {
                item['name']: item['type'] for item in alchemy_effects_list
            }

            self.ingredients_set = {ingredient for ingredients in self.alchemy_effects_to_ingredients_dict.values()
                                    for ingredient in ingredients}

        self.ingredients_to_alchemy_effects_dict = {}
        for effect, ingredients in self.alchemy_effects_to_ingredients_dict.items():
            for ingredient in ingredients:
                self.ingredients_to_alchemy_effects_dict.setdefault(ingredient, set()).add(effect)

if __name__ == '__main__':
    dh = DataHandler()
    print(dh.ingredients_to_alchemy_effects_dict)