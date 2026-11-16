"""Настройки игры и их сохранение."""

import json
from pathlib import Path

_OPTIONS_FILE = Path(__file__).resolve().parent / "options.json"

DIFFICULTY_MULTIPLIERS = {
    "Лёгкий": 0.75,
    "Средний": 1.0,
    "Сложный": 1.5,
}

DEFAULT_OPTIONS = {
    "difficulty": "Средний",
    "controls": {
        "move_up": ["w", "up"],
        "move_down": ["s", "down"],
        "move_left": ["a", "left"],
        "move_right": ["d", "right"],
        "attack": ["space"],
    },
}


def _validate_options(data):
    if not isinstance(data, dict):
        data = {}

    difficulty = data.get("difficulty", DEFAULT_OPTIONS["difficulty"])
    if difficulty not in DIFFICULTY_MULTIPLIERS:
        difficulty = DEFAULT_OPTIONS["difficulty"]

    controls_data = data.get("controls", {})
    if not isinstance(controls_data, dict):
        controls_data = {}

    controls = {}
    for action, default_keys in DEFAULT_OPTIONS["controls"].items():
        keys = controls_data.get(action, default_keys)
        if isinstance(keys, list) and keys and all(isinstance(k, str) for k in keys):
            controls[action] = keys
        else:
            controls[action] = default_keys.copy()

    return {"difficulty": difficulty, "controls": controls}


def load_options():
    try:
        with _OPTIONS_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except (OSError, json.JSONDecodeError):
        data = {}

    options = _validate_options(data)
    save_options(options)
    return options


def save_options(options):
    validated = _validate_options(options)
    try:
        _OPTIONS_FILE.parent.mkdir(parents=True, exist_ok=True)
        with _OPTIONS_FILE.open("w", encoding="utf-8") as file:
            json.dump(validated, file, ensure_ascii=False, indent=4)
    except OSError as error:
        print(f"Не удалось сохранить настройки: {error}")


def get_enemy_damage_multiplier(options):
    difficulty = options.get("difficulty", DEFAULT_OPTIONS["difficulty"])
    return DIFFICULTY_MULTIPLIERS.get(difficulty, 1.0)


def get_enemy_hp_multiplier(options):
    """На выбранной сложности одинаково масштабируются урон и здоровье врагов."""
    return get_enemy_damage_multiplier(options)
