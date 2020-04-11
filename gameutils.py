import json
import random

class AbaloneUtils:

    def __init__(self):
        pass

    @staticmethod
    def _safe_json_pick(target, filename, default, random_pick):
        with open(filename, 'r') as f:
            options = json.load(f)
        if random_pick:
            return random.choice(list(options.values()))
        if target in options:
            return options[target]
        return options[default]

    @staticmethod
    def get_theme(theme_name='default', random_pick=False):
        return AbaloneUtils._safe_json_pick(theme_name, 'assets/themes.json', 'default', random_pick)
    
    @staticmethod
    def get_variants(variant_name='classical', random_pick=False):
        return AbaloneUtils._safe_json_pick(variant_name, 'assets/variants.json', 'classical', random_pick)