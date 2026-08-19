import imagesize
import settings as settings
from utils.path_constructor import create_path
import paths.paths as paths
from config.map.biomes.biomes_config import biome_objects  # type: dict


BIOME_OBJECTS_CONFIG = {
    object_name: {
        "name": object_name,
        "color": tuple(data.get("color", [0, 0, 0])),
        "hit_box": (
            tuple(data["hit_box"])
            if (data.get("hit_box") and any(data["hit_box"]))
            else None
        ),
        "sprite_path": create_path(paths.BIOME_OBJECTS_SPRITES, data["sprite_path"])
        if data.get("sprite_path")
        else None,
    }
    for object_name, data in biome_objects.items()
}

half_tile_size = settings.TILE_SIZE // 2

OBJECT_SPRITES_INFO = {}
OBJECT_PADDINGS = {}
OBJECT_SPRITES_POSITIONS = {}

for object_name, config in BIOME_OBJECTS_CONFIG.items():
    sprite_path = config.get("sprite_path")

    if sprite_path:
        w, h = imagesize.get(sprite_path)
        OBJECT_SPRITES_INFO[object_name] = {
            "half_width": w // 2,
            "height": h
        }

    hit_box = config.get("hit_box")
    if hit_box:
        pad_y = (settings.TILE_SIZE - hit_box[1]) // 2
        OBJECT_PADDINGS[object_name] = {
            "padding_x": (settings.TILE_SIZE - hit_box[0]) // 2,
            "padding_y": pad_y,
            "bottom_margin": settings.TILE_SIZE - pad_y
        }

    if sprite_path and hit_box:
        OBJECT_SPRITES_POSITIONS[object_name] = {
            "x": half_tile_size - OBJECT_SPRITES_INFO[object_name]["half_width"],
            "y": OBJECT_PADDINGS[object_name]["bottom_margin"] - OBJECT_SPRITES_INFO[object_name]["height"]
        }
    elif sprite_path:
        OBJECT_SPRITES_POSITIONS[object_name] = {
            "x": half_tile_size - OBJECT_SPRITES_INFO[object_name]["half_width"],
            "y": settings.TILE_SIZE - OBJECT_SPRITES_INFO[object_name]["height"]
        }
