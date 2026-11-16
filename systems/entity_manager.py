import random

import settings.game_settings as game_settings
from settings.options import DIFFICULTY_MULTIPLIERS
from entities.enemies.green_petyx.green_petyx import GreenPetyx
from entities.enemies.red_petyx.red_petyx import RedPetyx
from entities.enemies.mashroom.mashroom import Mashroom

ENEMY_CLASSES = [GreenPetyx, RedPetyx, Mashroom]


class EntityManager:
    def __init__(self, resource_manager, enemies_settings, enemies_sprites, difficulty="Средний"):
        self.resource_manager = resource_manager
        self.enemies_settings = enemies_settings
        self.enemies_sprites = enemies_sprites
        self.enemies = []
        self.management_timer = 0.0
        self.management_interval = 1.0
        self.difficulty = difficulty
        self.damage_multiplier = 1.0
        self.hp_multiplier = 1.0
        self.set_difficulty(difficulty)

        half_w = game_settings.SCREEN_WIDTH // 2
        half_h = game_settings.SCREEN_HEIGHT // 2
        self.spawn_blind_zone = (half_w + half_h) * 1.2

    def set_difficulty(self, difficulty):
        self.difficulty = difficulty if difficulty in DIFFICULTY_MULTIPLIERS else "Средний"
        multiplier = DIFFICULTY_MULTIPLIERS[self.difficulty]
        self.damage_multiplier = multiplier
        self.hp_multiplier = multiplier

    def _apply_difficulty(self, enemy):
        # Каждый новый экземпляр создаётся с базовыми характеристиками,
        # поэтому коэффициент применяется ровно один раз.
        if hasattr(enemy, "damage"):
            enemy.damage = max(1, round(enemy.damage * self.damage_multiplier))

        if hasattr(enemy, "max_hp"):
            base_max_hp = enemy.max_hp
            enemy.max_hp = max(1, round(base_max_hp * self.hp_multiplier))
            if hasattr(enemy, "hp"):
                enemy.hp = enemy.max_hp
        elif hasattr(enemy, "hp"):
            enemy.hp = max(1, round(enemy.hp * self.hp_multiplier))

    def update(self, chunk_system, player, dt):
        for enemy in self.enemies:
            enemy.update(chunk_system, player, dt)

        self.management_timer += dt
        if self.management_timer >= self.management_interval:
            self.management_timer = 0.0
            self._despawn_distant_enemies(chunk_system)
            self._try_spawn_enemy(chunk_system, player)

    def _despawn_distant_enemies(self, chunk_system):
        active_enemies = []
        for enemy in self.enemies:
            cx, cy = chunk_system.world_to_chunk(enemy.x, enemy.y)
            if (cx, cy) in chunk_system.loaded_chunks:
                if enemy.state == "dead" and enemy.frame_index >= len(
                    enemy.resource_manager.get_animation(f"{enemy.type}_dead_{enemy.direction}") or []
                ) - 1:
                    continue
                active_enemies.append(enemy)
        self.enemies = active_enemies

    def _try_spawn_enemy(self, chunk_system, player, attempts=15):
        for _ in range(attempts):
            if self._spawn_once(chunk_system, player):
                return True
        return False

    def _spawn_once(self, chunk_system, player):
        if not chunk_system.loaded_chunks:
            return False

        chosen_chunk_coords = random.choice(list(chunk_system.loaded_chunks.keys()))
        cx, cy = chosen_chunk_coords

        count_in_chunk = sum(
            1 for enemy in self.enemies
            if chunk_system.world_to_chunk(enemy.x, enemy.y) == chosen_chunk_coords
        )
        if count_in_chunk >= 2:
            return False

        local_tile_x = random.randint(0, game_settings.CHUNK_SIZE - 1)
        local_tile_y = random.randint(0, game_settings.CHUNK_SIZE - 1)
        world_tile_x = cx * game_settings.CHUNK_SIZE + local_tile_x
        world_tile_y = cy * game_settings.CHUNK_SIZE + local_tile_y

        sub_base_x = world_tile_x * game_settings.SUB_DIVISIONS
        sub_base_y = world_tile_y * game_settings.SUB_DIVISIONS
        target_sub_x = sub_base_x + random.randint(0, game_settings.SUB_DIVISIONS - 1)
        target_sub_y = sub_base_y + random.randint(0, game_settings.SUB_DIVISIONS - 1)

        if (target_sub_x, target_sub_y) in chunk_system.all_blocked_subtiles:
            return False

        pixel_x = target_sub_x * game_settings.SUB_TILE_SIZE + game_settings.SUB_TILE_SIZE // 2
        pixel_y = target_sub_y * game_settings.SUB_TILE_SIZE + game_settings.SUB_TILE_SIZE // 2

        manhattan_dist = abs(pixel_x - player.x) + abs(pixel_y - player.y)
        if manhattan_dist < self.spawn_blind_zone:
            return False

        enemy_cls = random.choice(ENEMY_CLASSES)
        enemy = enemy_cls(
            pixel_x, pixel_y, self.resource_manager,
            self.enemies_settings, self.enemies_sprites
        )
        self._apply_difficulty(enemy)
        self.enemies.append(enemy)
        return True
