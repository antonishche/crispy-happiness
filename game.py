import pygame
import threading
import settings.game_settings as game_settings
from core.camera import Camera
from core.chunk_system import ChunkSystem
from systems.map_generator import MapGenerator
from entities.player.player import Player
from core.resource_manager import ResourceManager
from systems.entity_manager import EntityManager
from ui.hud import HUD
from helpers.functions.save_spot_finder import find_save_spot
from config.player.player_sprites_config import PLAYER_SPRITES
from helpers.functions.enemy_loader import load_all_enemies


class Game:

    def __init__(self):
        # pygame
        pygame.init()
        self.screen = pygame.display.set_mode((game_settings.SCREEN_WIDTH, game_settings.SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        pygame.display.set_caption("")
        self.running = True
        # systems
        self.camera = Camera(game_settings.SCREEN_WIDTH, game_settings.SCREEN_HEIGHT)
        self.chunk_system = ChunkSystem()
        self.resource_manager = ResourceManager()
        self.generator = MapGenerator(self.resource_manager, seed=game_settings.SEED)
        self.hud = HUD(username="Antony")
        # entities
        self.player = None
        self.enemies_settings, self.enemies_sprites = load_all_enemies()
        self.entity_manager = EntityManager(self.resource_manager, self.enemies_settings, self.enemies_sprites)
        # background
        self.bg_thread = threading.Thread(
            target=self.chunk_system._bg_generation_worker,
            args=(self.generator.generate_chunk_math,),
            daemon=True
        )
        self.bg_thread.start()
        # other
        self.chunk_pixel_size = game_settings.CHUNK_SIZE * game_settings.TILE_SIZE
        self.tile_size = game_settings.TILE_SIZE
        # default
        self.start_new_game()

    def start_new_game(self):
        raw_start_chunk = self.generator.generate_chunk_math(0, 0)
        center_chunk = self.generator.generate_chunk_visual(raw_start_chunk)
        self.chunk_system.loaded_chunks[(0, 0)] = center_chunk
        self.chunk_system.all_blocked_subtiles |= center_chunk["blocked_subtiles"]
        
        spawn_x, spawn_y = find_save_spot(center_chunk)
        self.player = Player(spawn_x, spawn_y, self.resource_manager, PLAYER_SPRITES)
        
        self.chunk_system.update(
            player_world_x=self.player.x,
            player_world_y=self.player.y,
            math_generator_func=self.generator.generate_chunk_math,
            visual_generator_func=self.generator.generate_chunk_visual
        )

    def run(self):
        while self.running:
            pygame.display.set_caption(str(self.clock.get_fps()))
            dt = self.clock.tick(game_settings.FPS) / 1000

            self._handle_events()
            self._update(dt)
            self._draw()

        self.chunk_system.generation_queue.put((None, None))
        pygame.quit()

    def _handle_events(self):
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                self.running = False

    def _update(self, dt):
        if self.player is None:
            return
        
        keys = pygame.key.get_pressed()
        self.player.update(keys, self.chunk_system, self.entity_manager, dt)
        self.camera.update(self.player, dt)
        self.chunk_system.update(
            self.player.x, self.player.y,
            self.generator.generate_chunk_math,
            self.generator.generate_chunk_visual
        )
        self.entity_manager.update(self.chunk_system, self.player, dt)

    def _draw(self):
        self.screen.fill((0, 0, 0))
        self._draw_world_tiles()

        for enemy in self.entity_manager.enemies:
            enemy.draw_shadow(self.screen, self.camera)
        if self.player:
            self.player.draw_shadow(self.screen, self.camera)

        render_queue = self._collect_objects()
        render_queue.sort(key=lambda item: item["sort_y"])

        for item in render_queue:
            if item["type"] == "object":
                self.screen.blit(item["sprite"], (item["x"], item["y"]))
            elif item["type"] == "player":
                if self.player:
                    self.player.draw(self.screen, self.camera)
            elif item["type"] == "enemy":
                item["obj"].draw(self.screen, self.camera)

        self.hud.draw(self.screen, self.player, self.entity_manager.enemies)
        pygame.display.flip()

    def _collect_objects(self):
        queue = []

        queue.append({
            "sort_y": self.player.y if self.player else 0,
            "type": "player"
        })

        # ………
        for enemy in self.entity_manager.enemies:
            queue.append({"sort_y": enemy.y, "type": "enemy", "obj": enemy})
        # ………

        for chunk in self.chunk_system.loaded_chunks.values():
            screen_x, screen_y = self.camera.apply_point(chunk["world_x"], chunk["world_y"])
            if (
                screen_x + self.chunk_pixel_size < -100 or 
                screen_x > self.screen.get_width() + 100 or
                screen_y + self.chunk_pixel_size < -100 or 
                self.screen.get_height() + 100 < screen_y
            ):
                continue

            for obj in chunk["objects"]:
                obj_sprite = self.resource_manager.load_image(obj["sprite_path"])

                obj_draw_x = obj["world_draw_x"] - self.camera.x
                obj_draw_y = obj["world_draw_y"] - self.camera.y

                queue.append({
                    "type": "object",
                    "sort_y": obj["world_sort_y"],
                    "sprite": obj_sprite,
                    "x": obj_draw_x,
                    "y": obj_draw_y
                })

        return queue

    def _draw_world_tiles(self):
        for chunk in self.chunk_system.loaded_chunks.values():
            screen_x, screen_y = self.camera.apply_point(chunk["world_x"], chunk["world_y"])

            # Виден ли чанк на экране
            if (
                screen_x + self.chunk_pixel_size < 0 or
                screen_x > self.screen.get_width() or
                screen_y + self.chunk_pixel_size < 0 or
                screen_y > self.screen.get_height()
            ):
                continue

            self.screen.blit(chunk["visual_surface"], (screen_x, screen_y))
