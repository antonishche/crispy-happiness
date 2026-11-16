import glob
import imagesize
import settings.game_settings as game_settings
from helpers.utils.path_constructor import create_path, path_exists
import helpers.paths.paths as paths
from config.map.biomes_config import biome_objects  # type: dict
from helpers.utils.units import parse_size


BIOME_OBJECTS_CONFIG = {}
OBJECT_SPRITES_GEOMETRY = {}

SUB_TILE_SIZE = game_settings.SUB_TILE_SIZE


def _to_sub(px):
    return -(-px // SUB_TILE_SIZE)  # округление вверх


def _validate_unit(data, field_name, obj_name):
    raw = data.get(field_name)
    if raw is None:
        return
    if isinstance(raw, dict):
        unit = raw.get("unit")
        if unit != "sub":
            raise ValueError(
                f"[biome_objects] {obj_name}.{field_name}: unit='{unit}' "
                f"не поддерживается, используй 'sub'"
            )


def _find_sprite_paths(data):
    search_dir = None

    if data.get("category") and data.get("folder"):
        search_dir = create_path(paths.BIOME_OBJECTS_SPRITES_PATH, data["category"], data["folder"])
    elif data.get("folder"):
        search_dir = create_path(paths.BIOME_OBJECTS_SPRITES_PATH, data["folder"])
    elif data.get("category"):
        search_dir = create_path(paths.BIOME_OBJECTS_SPRITES_PATH, data["category"])

    if search_dir and path_exists(search_dir):
        return sorted(glob.glob(create_path(search_dir, "*.png")))
    return []


for object_name, data in biome_objects.items():
    _validate_unit(data, "hit_box", object_name)
    _validate_unit(data, "margin", object_name)

    hit_box = parse_size(data.get("hit_box"))
    if hit_box and not any(hit_box):
        hit_box = None

    margin = parse_size(data.get("margin")) or (0, 0)

    # footprint == (0, 0) для объектов без hit_box — намеренно:
    # map_generator трактует их как декор (кластерный спавн, без коллизии),
    # а при отрисовке использует max(fw, 1) только для объектов с hit_box.
    footprint = (_to_sub(hit_box[0]), _to_sub(hit_box[1])) if hit_box else (0, 0)
    margin_sub = (_to_sub(margin[0]), _to_sub(margin[1]))

    if hit_box:
        foot_w = footprint[0] * SUB_TILE_SIZE
        foot_h = footprint[1] * SUB_TILE_SIZE
        sort_offset = foot_h
    else:
        foot_w = foot_h = SUB_TILE_SIZE
        sort_offset = SUB_TILE_SIZE

    sprite_paths = _find_sprite_paths(data)

    BIOME_OBJECTS_CONFIG[object_name] = {
        "name": object_name,
        "color": tuple(data.get("color", [0, 0, 0])),
        "hit_box": hit_box,
        "footprint": footprint,
        "margin_sub": margin_sub,
        "sort_offset": sort_offset,
        "sprite_paths": sprite_paths if sprite_paths else None,
    }

    sprite_bottom_margin = data.get("sprite_bottom_margin", 0)
    sprite_left_margin = data.get("sprite_left_margin", 0)

    OBJECT_SPRITES_GEOMETRY[object_name] = []

    for path in sprite_paths:
        w, h = imagesize.get(path)
        half_width = w // 2

        if hit_box:
            sprite_x = foot_w // 2 - half_width - sprite_left_margin
            sprite_y = foot_h - h + sprite_bottom_margin
        else:
            # декор: центрируем по субтайлу, "сидим" на его нижнем крае
            sprite_x = SUB_TILE_SIZE // 2 - half_width - sprite_left_margin
            sprite_y = SUB_TILE_SIZE - h + sprite_bottom_margin

        OBJECT_SPRITES_GEOMETRY[object_name].append({
            "path": path,
            "sprite_x": sprite_x,
            "sprite_y": sprite_y
        })


def debug_dump():
    for name, cfg in BIOME_OBJECTS_CONFIG.items():
        sprites = len(cfg["sprite_paths"] or [])
        kind = "solid" if cfg["hit_box"] else "decor"
        print(
            f"{name:10s} [{kind:5s}] footprint={cfg['footprint']} "
            f"margin={cfg['margin_sub']} sort={cfg['sort_offset']} "
            f"sprites={sprites}"
        )