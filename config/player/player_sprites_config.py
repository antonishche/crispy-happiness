from utils.file_loader import load_json
import paths.paths as paths
from utils.path_constructor import create_path


player_sprites = load_json(paths.PLAYER_SPRITES_JSON)

PLAYER_SPRITES = {
    state_direction: {
        "count": data.get("count", 1),
        "width_count": data.get("width_count", 1),
        "height_count": data.get("height_count", 1),
        "frame_duration": data.get("frame_duration", 0.15),
        "path": create_path(paths.PLAYER_SPRITES, data["path"]) if data.get("path") else None
    }
    for state_direction, data in player_sprites.items()
}
