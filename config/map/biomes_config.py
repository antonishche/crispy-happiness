import settings.game_settings as game_settings
from helpers.utils.file_loader import load_json
from helpers.utils.path_constructor import create_path
import helpers.paths.paths as paths


biomes = load_json(paths.BIOMES_JSON)
biome_objects = load_json(paths.BIOME_OBJECTS_JSON)

# Порядок важен: используется для layer и fallback.
# Распределение биомов считается в map_generator через BIOME_CLIMATE,
# здесь оставляем только слои для отрисовки.
BIOME_LAYER = {
    "water": 0,
    "desert": 1,
    "grass": 2,
    "forest": 3,
}

# Оставлено для обратной совместимости с местами, которые ещё импортируют
# BIOMES_DISTRIBUTION. map_generator его больше не использует.
BIOMES_DISTRIBUTION = [
    (-0.2, "water"),
    (0.0, "desert"),
    (0.3, "grass"),
    (0.6, "forest")
]


def _parse_autotile(raw):
    if not raw:
        return None
    return {
        "out": create_path(paths.BIOMES_SPRITES_PATH, raw["out"]),
        "in": create_path(paths.BIOMES_SPRITES_PATH, raw["in"]),
    }


BIOME_CONFIG = {
    biom_name: {
        "blocked": data.get("blocked", True),
        "objects_chance": {
            obj_name: chance
            for obj_name, chance in data.get("objects_chance", {}).items()
            if obj_name in biome_objects
        },
        "color": tuple(data.get("color", [255, 255, 255])),
        "sprite_path": create_path(paths.BIOMES_SPRITES_PATH, data["sprite_path"]) if data.get("sprite_path") else None,
        "autotile": _parse_autotile(data.get("autotile")),
        "layer": BIOME_LAYER[biom_name],
    }
    for biom_name, data in biomes.items()
}