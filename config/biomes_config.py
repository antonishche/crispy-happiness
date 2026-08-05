import settings
from utils.file_loader import load_json
from paths.paths import (
    BIOMES_JSON,
    BIOME_OBJECTS_JSON
)


biomes = load_json(BIOMES_JSON)
biome_objects = load_json(BIOME_OBJECTS_JSON)

BIOME_CONFIG = {
    biom_name: {
        "blocked": data.get("blocked", True),
        "objects_chance": data.get("objects_chance") or dict(),
        "color": tuple(data.get("color", [255, 255, 255])),
        "sprite_path": data.get("sprite_path", None)
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

BIOME_OBJECTS_CONFIG = {
    object_name: {
        "color": tuple(data.get("color", [0, 0, 0])),
        "hit_box": (
            tuple(data["hit_box"])
            if (data.get("hit_box") and any(data["hit_box"]))
            else None
        ),
        "sprite_path": data.get("sprite_path", None),
    }
    for object_name, data in biome_objects.items()
}

OBJECT_PADDINGS = {
    object_name: {
        "padding_x": (settings.TILE_SIZE - config["hit_box"][0]) // 2,
        "padding_y": (settings.TILE_SIZE - config["hit_box"][1]) // 2
    }
    for object_name, config in BIOME_OBJECTS_CONFIG.items()
    if config.get("hit_box")
}
