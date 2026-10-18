from helpers.utils.file_loader import load_json
import random


def parse_settings(path):
    s = load_json(path)

    hit_box = tuple(s.get("hit_box", [0, 0]))
    if not s.get("start_direction"):
        if random.random() >= 0.5:
            start_direction = "left"
        else:
            start_direction = "right"
    else:
        start_direction = s["start_direction"]

    max_hp = s.get("max_hp", 1)
    action_range = s.get("action_range", 35)

    return {
        # speed
        "speed": s.get("speed", 1),
        "acceleration": s.get("acceleration", 1),
        "friction": s.get("friction", 1),
        "momentum_x": 0.0,
        "momentum_y": 0.0,
        # hit_box
        "width": hit_box[0],
        "height": hit_box[1],
        # animation
        "state": s.get("start_state", "idle"),
        "type": s.get("type", "default"),
        "direction": start_direction,
        "target_sprite_height": s.get("target_sprite_height", 64),
        "loaded_sprite_direction": s.get("loaded_sprite_direction", None),
        "target_animations": s.get("target_animations"),
        # ai
        "reaction_range": s.get("reaction_range", 200),
        "action_range": action_range,
        "advanced_range": int(s.get("advanced_range", 1.5 * action_range)),
        "forget_range": s.get("forget_range", 300),
        "ai_state": s.get("ai_state", "idle"),
        # hp
        "damage": s.get("damage", 1),
        "max_hp": max_hp,
        "hp": s.get("hp", max_hp),
        "attack_cooldown": s.get("attack_cooldown", 1.0),
        # default
        "frame_duration": 0.15,
        "frame_index": 0,
        "frame_timer": 0.0,
        "afk_timer": 0.0,
        "current_frame": None,
        "last_full_key": "",
        "cached_frames": None,
        "dir_x": 0,
        "dir_y": 0,
        "attack_cooldown_timer": 0.0
    }