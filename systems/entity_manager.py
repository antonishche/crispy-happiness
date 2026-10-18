import random
import settings.game_settings as game_settings
from entities.enemies.green_petyx.green_petyx import GreenPetyx
from entities.enemies.red_petyx.red_petyx import RedPetyx

ENEMY_CLASSES = [GreenPetyx, RedPetyx]

class EntityManager:

    def __init__(self, resource_manager, enemies_settings, enemies_sprites):
        self.resource_manager = resource_manager
        self.enemies_settings = enemies_settings
        self.enemies_sprites = enemies_sprites

        self.enemies = []

        self.management_timer = 0.0
        self.management_interval = 1.0

        half_w = game_settings.SCREEN_WIDTH // 2
        half_h = game_settings.SCREEN_HEIGHT // 2
        self.spawn_blind_zone = (half_w + half_h) * 1.2

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
                if enemy.state == "dead" and enemy.frame_index >= len(enemy.resource_manager.get_animation(f"{enemy.type}_dead_{enemy.direction}") or []) - 1:
                    continue
                    
                active_enemies.append(enemy)
                
        self.enemies = active_enemies

    def _try_spawn_enemy(self, chunk_system, player, attempts=15):
        for _ in range(attempts):
            if self._spawn_once(chunk_system, player):
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

        # random subtile
        local_tile_x = random.randint(0, game_settings.CHUNK_SIZE - 1)
        local_tile_y = random.randint(0, game_settings.CHUNK_SIZE - 1)

        world_tile_x = cx * game_settings.CHUNK_SIZE + local_tile_x
        world_tile_y = cy * game_settings.CHUNK_SIZE + local_tile_y

        sub_base_x = world_tile_x * game_settings.SUB_DIVISIONS
        sub_base_y = world_tile_y * game_settings.SUB_DIVISIONS

        rand_sub_x = random.randint(0, game_settings.SUB_DIVISIONS - 1)
        rand_sub_y = random.randint(0, game_settings.SUB_DIVISIONS - 1)

        target_sub_x = sub_base_x + rand_sub_x
        target_sub_y = sub_base_y + rand_sub_y

        if (target_sub_x, target_sub_y) in chunk_system.all_blocked_subtiles:
            return False

        pixel_x = target_sub_x * game_settings.SUB_TILE_SIZE + game_settings.SUB_TILE_SIZE // 2
        pixel_y = target_sub_y * game_settings.SUB_TILE_SIZE + game_settings.SUB_TILE_SIZE // 2

        manhattan_dist = abs(pixel_x - player.x) + abs(pixel_y - player.y)
        if manhattan_dist < self.spawn_blind_zone:
            return False

        enemy_cls = random.choice(ENEMY_CLASSES)
        new_enemy = enemy_cls(
        pixel_x, pixel_y,
        self.resource_manager,
        self.enemies_settings,
        self.enemies_sprites
        )
        self.enemies.append(new_enemy)
        return True
