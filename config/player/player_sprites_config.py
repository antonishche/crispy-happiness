import helpers.paths.paths as paths
from helpers.utils.entity_sprites_loader import load_entity_sprites_config
from helpers.utils.settings_parser import parse_settings
from helpers.paths.paths import PLAYER_SETTINGS_JSON


PLAYER_SETTINGS = parse_settings(PLAYER_SETTINGS_JSON)

PLAYER_SPRITES = load_entity_sprites_config(
    json_path=paths.PLAYER_SPRITES_JSON,
    main_path=paths.PLAYER_SPRITES_PATH,
    target_height=PLAYER_SETTINGS["target_sprite_height"]
)
