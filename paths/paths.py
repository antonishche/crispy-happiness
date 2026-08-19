from utils.path_constructor import create_path


DATA_PATH = "data"
CONFIG_PATH = "config"
ASSETS_PATH = "assets"
MAP_PATH = "map"
BIOMES_PATH = "biomes"
BIOME_OBJECTS_PATH = "biome_objects"
PLAYER_PATH = "player"

BIOMES_JSON = create_path(CONFIG_PATH, MAP_PATH, BIOMES_PATH, "biomes.json")
BIOME_OBJECTS_JSON = create_path(CONFIG_PATH, MAP_PATH, BIOME_OBJECTS_PATH, "biome_objects.json")
PLAYER_SPRITES_JSON = create_path(CONFIG_PATH, PLAYER_PATH, "player_sprites.json")

BIOMES_SPRITES = create_path(ASSETS_PATH, MAP_PATH, BIOMES_PATH)
BIOME_OBJECTS_SPRITES = create_path(ASSETS_PATH, MAP_PATH, BIOME_OBJECTS_PATH)
PLAYER_SPRITES = create_path(ASSETS_PATH, PLAYER_PATH)

ITEMS_WEAPONS_CSV = create_path(DATA_PATH, "weapons.csv")
ITEMS_ARMOR_CSV = create_path(DATA_PATH, "armor.csv")
ITEMS_FOOD_CSV = create_path(DATA_PATH, "food.csv")
ITEMS_RESOURCES_CSV = create_path(DATA_PATH, "resources.csv")
ITEMS_BAGS_CSV = create_path(DATA_PATH, "bags.csv")
