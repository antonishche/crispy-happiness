import settings as settings
from utils.file_loader import load_json
from utils.path_constructor import create_path
import paths.paths as paths


biomes = load_json(paths.BIOMES_JSON)
biome_objects = load_json(paths.BIOME_OBJECTS_JSON)

BIOME_CONFIG = {
    biom_name: {
        "blocked": data.get("blocked", True),
        "objects_chance": {
            obj_name: chance
            for obj_name, chance in data.get("objects_chance", {}).items()
            if obj_name in biome_objects
        },
        "color": tuple(data.get("color", [255, 255, 255])),
        "sprite_path": create_path(paths.BIOMES_SPRITES, data["sprite_path"]) if data.get("sprite_path") else None
    }
    for biom_name, data in biomes.items()
}

BIOMES_DISTRIBUTION = [
    (-0.5, "ocean"),
    (-0.2, "water"),
    (0.0, "desert"),
    (0.3, "grass"),
    (0.6, "forest"),
    (1.0, "mountain")
]
