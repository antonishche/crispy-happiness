import settings.game_settings as game_settings


def parse_size(raw, default_unit="px"):
    if not raw:
        return None

    if isinstance(raw, dict):
        value = raw["value"]
        unit = raw.get("unit", default_unit)
    else:
        value = raw
        unit = default_unit

    k = game_settings.SUB_TILE_SIZE if unit == "sub" else 1
    return (value[0] * k, value[1] * k)