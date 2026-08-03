DEFAULT_TILE_STATE = {
    "blocked": False,
    "has_tree": False,
    "has_stone": False
    # ...
}

BIOMES_DISTRIBUTION = [
    (0.0, "grass"),
    (0.3, "forest"),
    (0.5, "desert"),
    (1.0, "mountain")
]

BIOME_CONFIGS = {
    "grass": {
        "blocked": False,
        "objects_chance": [("has_tree", 0.05), ("has_stone", 0.02)]
    },
    "forest": {
        "blocked": False,
        "objects_chance": [("has_tree", 0.40), ("has_stone", 0.05)]
    },
    "desert": {
        "blocked": False,
        "objects_chance": [("has_tree", 0.0), ("has_stone", 0.08)]
    },
    "mountain": {
        "blocked": True,
        "objects_chance": [("has_tree", 0.0), ("has_stone", 0.40)]
    }
}

# Цвета-заглушки для биомов
BIOME_COLORS = {
    "grass": (34, 139, 34),       # Зеленый
    "forest": (0, 100, 0),        # Темно-зеленый
    "desert": (237, 201, 175),    # Песочный
    "mountain": (128, 128, 128)   # Серый
}

OBJECT_COLORS = {
    "has_tree": (139, 69, 19),    # Коричневый
    "has_stone": (169, 169, 169)  # Светло-серый
}

OBJECT_HITBOXES = {
    "has_tree": (16, 16),
    "has_stone": (24, 24)
}
