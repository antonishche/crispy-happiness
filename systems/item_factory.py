import copy
from helpers.utils.file_loader import load_csv
from helpers.paths.paths import (
    ITEMS_WEAPONS_CSV,
    ITEMS_ARMOR_CSV,
    ITEMS_FOOD_CSV,
    ITEMS_RESOURCES_CSV,
    ITEMS_BAGS_CSV
)


class Item:

    def __init__(self, item_type: str, data: dict):
        self.type = item_type

        if "max_stack" not in data:
            self.max_stack = 1

        for key, value in data.items():
            try:
                if '.' in value:
                    value = float(value)
                else:
                    value = int(value)
            except ValueError:
                pass

            setattr(self, key, value)
        
    def __repr__(self):
        item_id = getattr(self, "id", "unknown")
        item_name = getattr(self, "name", "unknown")
        return f"Item({item_id}, {item_name}, type={self.type})"


class ItemFactory:

    def __init__(self):
        self.items = {}

    def load_all(self):
        categories = [
            (ITEMS_WEAPONS_CSV, "weapon"),
            (ITEMS_ARMOR_CSV, "armor"),
            (ITEMS_FOOD_CSV, "food"),
            (ITEMS_RESOURCES_CSV, "resource"),
            (ITEMS_BAGS_CSV, "bag")
        ]

        for file_path, item_type in categories:
            rows = load_csv(file_path)
            for row in rows:
                if not row or not (item_id := row.get("id")):
                    continue
                item = Item(item_type=item_type, data=row)
                self.items[item_id] = item

    def get(self, item_id):
        original = self.items.get(item_id)
        if original is None:
            return None
        return copy.copy(original)

    def get_all(self):
        return self.items

