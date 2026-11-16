"""Local save slots for worlds. Runtime pygame objects are rebuilt on load."""
import json
import os
import pickle
import time
from pathlib import Path

import pygame


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SAVES_DIR = PROJECT_ROOT / "saves"

# Only plain data is persisted; surfaces, queues, threads and resource caches are rebuilt.
ENTITY_FIELDS = (
    "x", "y", "hp", "max_hp", "stamina", "max_stamina", "state", "direction",
    "ai_state", "momentum_x", "momentum_y", "dir_x", "dir_y", "frame_index",
    "frame_timer", "afk_timer", "ai_timer", "ai_target_time", "attack_cooldown_timer",
    "attack_active", "damage", "last_x", "last_y",
)


class SaveManager:
    def __init__(self, root=SAVES_DIR):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def _slot_path(self, slot_id):
        return self.root / str(slot_id)

    def list_saves(self):
        result = []
        for folder in self.root.iterdir():
            meta_path = folder / "meta.json"
            if not folder.is_dir() or not meta_path.exists():
                continue
            try:
                with meta_path.open("r", encoding="utf-8") as f:
                    meta = json.load(f)
                meta["slot_id"] = folder.name
                meta["preview"] = str(folder / "preview.png") if (folder / "preview.png").exists() else None
                result.append(meta)
            except (OSError, ValueError):
                continue
        result.sort(key=lambda item: item.get("updated_at", 0), reverse=True)
        return result

    @staticmethod
    def _entity_data(entity):
        data = {}
        for field in ENTITY_FIELDS:
            if hasattr(entity, field):
                value = getattr(entity, field)
                if isinstance(value, (str, int, float, bool)) or value is None:
                    data[field] = value
        return data

    def save_game(self, game, name=None, slot_id=None):
        slot_id = slot_id or str(int(time.time() * 1000))
        folder = self._slot_path(slot_id)
        folder.mkdir(parents=True, exist_ok=True)

        # Chunks are deterministic from the seed. Store known coordinates and regenerate
        # their visual surfaces on load instead of trying to pickle pygame.Surface objects.
        known_chunks = set(game.chunk_system.loaded_chunks) | set(game.chunk_system.cached_chunks)
        state = {
            "version": 1,
            "seed": game.generator.seed,
            "player": self._entity_data(game.player),
            "enemies": [
                {"type": enemy.type, **self._entity_data(enemy)}
                for enemy in game.entity_manager.enemies
            ],
            "chunk_coords": [list(coord) for coord in sorted(known_chunks)],
            "destroyed_objects": list(game.generator.destroyed_objects),
            "entity_management_timer": game.entity_manager.management_timer,
            "random_state": __import__("random").getstate(),
        }
        with (folder / "world.pkl").open("wb") as f:
            pickle.dump(state, f, protocol=pickle.HIGHEST_PROTOCOL)

        preview_path = folder / "preview.png"
        try:
            pygame.image.save(game.screen, str(preview_path))
        except pygame.error:
            pass

        old_meta = {}
        if (folder / "meta.json").exists():
            try:
                old_meta = json.loads((folder / "meta.json").read_text(encoding="utf-8"))
            except (OSError, ValueError):
                old_meta = {}
        meta = {
            "name": name or old_meta.get("name") or f"Мир {len(self.list_saves()) + 1}",
            "seed": game.generator.seed,
            "created_at": int(time.time()),
            "updated_at": int(time.time()),
        }
        meta_path = folder / "meta.json"
        if old_meta:
            meta["created_at"] = old_meta.get("created_at", meta["created_at"])
        meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
        return slot_id

    def load_game(self, slot_id):
        with (self._slot_path(slot_id) / "world.pkl").open("rb") as f:
            return pickle.load(f)

    def rename(self, slot_id, new_name):
        path = self._slot_path(slot_id) / "meta.json"
        meta = json.loads(path.read_text(encoding="utf-8"))
        meta["name"] = new_name.strip() or meta.get("name", "Мир")
        meta["updated_at"] = int(time.time())
        path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

    def delete(self, slot_id):
        import shutil
        shutil.rmtree(self._slot_path(slot_id), ignore_errors=True)
