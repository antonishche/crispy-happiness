import glob
import imagesize
import settings.game_settings as game_settings
from helpers.utils.path_constructor import create_path, path_exists
import helpers.paths.paths as paths
from config.map.biomes_config import biome_objects  # type: dict


BIOME_OBJECTS_CONFIG = {}
OBJECT_PADDINGS = {}
OBJECT_SPRITES_GEOMETRY = {}

half_tile_size = game_settings.TILE_SIZE // 2
SUB_DIVISIONS = game_settings.SUB_DIVISIONS
SUB_TILE_SIZE = game_settings.SUB_TILE_SIZE

for object_name, data in biome_objects.items():
    hit_box = (
        tuple(data["hit_box"])
        if (data.get("hit_box") and any(data["hit_box"]))
        else None
    )

    sprite_paths = []
    search_dir = None

    if data.get("category") and data.get("folder"):
        search_dir = create_path(paths.BIOME_OBJECTS_SPRITES_PATH, data["category"], data["folder"])
    elif data.get("folder"):
        search_dir = create_path(paths.BIOME_OBJECTS_SPRITES_PATH, data["folder"])
    elif data.get("category"):
        search_dir = create_path(paths.BIOME_OBJECTS_SPRITES_PATH, data["category"])

    if search_dir and path_exists(search_dir):
        search_pattern = create_path(search_dir, "*.png")
        sprite_paths = sorted(glob.glob(search_pattern))

    object_subtiles = set()
    if hit_box:
        pad_x = (game_settings.TILE_SIZE - hit_box[0]) // 2
        pad_y = (game_settings.TILE_SIZE - hit_box[1]) // 2

        left = pad_x
        right = pad_x + hit_box[0]
        top = pad_y
        bottom = pad_y + hit_box[1]

        for sy in range(SUB_DIVISIONS):
            for sx in range(SUB_DIVISIONS):
                st_left = sx * SUB_TILE_SIZE
                st_right = st_left + SUB_TILE_SIZE
                st_top = sy * SUB_TILE_SIZE
                st_bottom = st_top + SUB_TILE_SIZE

                if not (st_right <= left or st_left >= right or st_bottom <= top or st_top >= bottom):
                    object_subtiles.add((sx, sy))

    BIOME_OBJECTS_CONFIG[object_name] = {
        "name": object_name,
        "color": tuple(data.get("color", [0, 0, 0])),
        "hit_box": hit_box,
        "sprite_paths": sprite_paths if sprite_paths else None,
        "subtiles": object_subtiles
    }

    if hit_box:
        pad_y = (game_settings.TILE_SIZE - hit_box[1]) // 2
        OBJECT_PADDINGS[object_name] = {
            "padding_x": (game_settings.TILE_SIZE - hit_box[0]) // 2,
            "padding_y": pad_y,
            "bottom_margin": game_settings.TILE_SIZE - pad_y
        }

    OBJECT_SPRITES_GEOMETRY[object_name] = []

    if sprite_paths:
        for path in sprite_paths:
            w, h = imagesize.get(path)
            half_width = w // 2
            sprite_bottom_margin = data.get("sprite_bottom_margin", 0)
            sprite_left_margin = data.get("sprite_left_margin", 0)

            if hit_box:
                sprite_x = half_tile_size - half_width - sprite_left_margin
                sprite_y = OBJECT_PADDINGS[object_name]["bottom_margin"] - h + sprite_bottom_margin
            else:
                sprite_x = half_tile_size - half_width - sprite_left_margin
                sprite_y = half_tile_size - h + sprite_bottom_margin

            OBJECT_SPRITES_GEOMETRY[object_name].append({
                "path": path,
                "half_width": half_width,
                "height": h,
                "sprite_x": sprite_x,
                "sprite_y": sprite_y
            })
