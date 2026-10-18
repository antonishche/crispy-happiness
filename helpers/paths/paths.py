from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _path(*parts: str) -> str:
    return str(PROJECT_ROOT.joinpath(*parts))


# Directories
SETTINGS_PATH = _path("settings")
DATA_PATH = _path("data")
CONFIG_PATH = _path("config")
ASSETS_PATH = _path("assets")
MAP_PATH = "map"
BIOMES_PATH = "biomes"
ITEMS_PATH = "items"
BIOME_OBJECTS_PATH = "biome_objects"
PLAYER_PATH = "player"
ENEMIES_PATH = "enemies"
GREEN_PETYX_PATH = "green_petyx"

# JSON data
BIOMES_JSON = _path("data", MAP_PATH, BIOMES_PATH, "biomes.json")
BIOME_OBJECTS_JSON = _path("data", MAP_PATH, BIOME_OBJECTS_PATH, "biome_objects.json")
PLAYER_SPRITES_JSON = _path("data", PLAYER_PATH, "player_sprites.json")
PLAYER_SETTINGS_JSON = _path("data", PLAYER_PATH, "player_settings.json")
ENEMIES_DATA_PATH = _path("data", ENEMIES_PATH)
ENEMIES_SPRITES_PATH = _path("assets", ENEMIES_PATH)

# Sprite directories
BIOMES_SPRITES_PATH = _path("assets", MAP_PATH, BIOMES_PATH)
BIOME_OBJECTS_SPRITES_PATH = _path("assets", MAP_PATH, BIOME_OBJECTS_PATH)
PLAYER_SPRITES_PATH = _path("assets", PLAYER_PATH)

# Items
ITEMS_WEAPONS_CSV = _path("data", ITEMS_PATH, "weapons.csv")
ITEMS_ARMOR_CSV = _path("data", ITEMS_PATH, "armor.csv")
ITEMS_FOOD_CSV = _path("data", ITEMS_PATH, "food.csv")
ITEMS_RESOURCES_CSV = _path("data", ITEMS_PATH, "resources.csv")
ITEMS_BAGS_CSV = _path("data", ITEMS_PATH, "bags.csv")
