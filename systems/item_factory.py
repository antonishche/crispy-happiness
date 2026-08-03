from utils.file_loader import load_csv
import settings


class Item:

    def __init__(
            self, id, name, type, weight,
            max_stack=1,
            damage=None,
            armor=None,
            slots_bonus=None,
            weight_bonus=None,
            health_restore=None):
        self.id = id
        self.name = name
        self.type = type
        self.weight = weight
        self.max_stack = max_stack
        self.damage = damage
        self.armor = armor
        self.slots_bonus = slots_bonus
        self.weight_bonus = weight_bonus
        self.health_restore = health_restore

    def __repr__(self):
        return f"Item({self.id}, {self.name}, type={self.type})"


class ItemFactory:

    def __init__(self):
        self.items = {}

    def load_all(self):
        self._load_weapons()
        self._load_armor()
        self._load_food()
        self._load_resources()
        self._load_bags()

    def _load_weapons(self):
        data = load_csv(settings.ITEMS_WEAPONS_CSV)
        for row in data:
            item_id = row[0]
            name = row[1]
            weight = float(row[2])
            damage = int(row[3])

            item = Item(
                id=item_id,
                name=name,
                type="weapon",
                weight=weight,
                max_stack=1,
                damage=damage
            )
            self.items[item_id] = item

    def _load_armor(self):
        data = load_csv(settings.ITEMS_ARMOR_CSV)
        for row in data:
            item_id = row[0]
            name = row[1]
            weight = float(row[2])
            armor = int(row[3])
        
            item = Item(
                id=item_id,
                name=name,
                type="armor",
                weight=weight,
                max_stack=1,
                armor=armor
            )
            self.items[item_id] = item

    def _load_food(self):
        data = load_csv(settings.ITEMS_FOOD_CSV)
        for row in data:
            item_id = row[0]
            name = row[1]
            weight = float(row[2])
            health_restore = int(row[3])
        
            item = Item(
                id=item_id,
                name=name,
                type="food",
                weight=weight,
                max_stack=20,
                health_restore=health_restore
            )
            self.items[item_id] = item

    def _load_resources(self):
        data = load_csv(settings.ITEMS_RESOURCES_CSV)
        for row in data:
            item_id = row[0]
            name = row[1]
            weight = float(row[2])
            max_stack = int(row[3])
        
            item = Item(
                id=item_id,
                name=name,
                type="resource",
                weight=weight,
                max_stack=max_stack
            )
            self.items[item_id] = item

    def _load_bags(self):
        data = load_csv(settings.ITEMS_BAGS_CSV)
        for row in data:
            item_id = row[0]
            name = row[1]
            weight = float(row[2])
            slots_bonus = int(row[3])
            weight_bonus = float(row[4])
        
            item = Item(
                id=item_id,
                name=name,
                type="bags",
                weight=weight,
                slots_bonus=slots_bonus,
                weight_bonus=weight_bonus
            )
            self.items[item_id] = item

    def get(self, item_id):
        original = self.items.get(item_id)
        return Item(**original.__dict__)

    def get_all(self):
        return self.items

