import pygame
import threading

import settings.game_settings as game_settings
from settings.options import load_options, save_options
from core.camera import Camera
from core.chunk_system import ChunkSystem
from systems.map_generator import MapGenerator
from entities.player.player import Player
from core.resource_manager import ResourceManager
from systems.entity_manager import EntityManager
from ui.hud import HUD
from core.game_state import GameState
from ui.pause_menu import PauseMenu
from ui.difficulty_menu import DifficultyMenu
from helpers.functions.save_spot_finder import find_save_spot
from config.player.player_sprites_config import PLAYER_SPRITES
from helpers.functions.enemy_loader import load_all_enemies
from systems.statistics_manager import StatisticsManager
from systems.statistics_storage import StatisticsStorage
from ui.statistics_menu import StatisticsMenu
from ui.main_menu import MainMenu


class Game:
    def __init__(self):
        # pygame
        pygame.init()
        self.screen = pygame.display.set_mode(
            (game_settings.SCREEN_WIDTH, game_settings.SCREEN_HEIGHT)
        )
        self.clock = pygame.time.Clock()
        pygame.display.set_caption("My World")
        self.running = True
        # systems
        self.camera = Camera(game_settings.SCREEN_WIDTH, game_settings.SCREEN_HEIGHT)
        self.chunk_system = ChunkSystem()
        self.resource_manager = ResourceManager()
        self.generator = MapGenerator(self.resource_manager, seed=game_settings.SEED)
        self.hud = HUD(username="Antony")
        self.state = GameState.PLAYING
        # ui
        self.options = load_options()
        self.main_menu = MainMenu()
        self.difficulty_menu = DifficultyMenu()
        self.main_menu_open = True
        self.difficulty_open = False
        self.main_menu_settings_open = False
        self.pause_menu = PauseMenu()
        # statistics
        self.statistics_storage = StatisticsStorage()
        self.statistics_menu = StatisticsMenu(self.statistics_storage)
        self.statistics_open = False
        # run state
        self.statistics_manager = StatisticsManager(self.options["difficulty"])
        self.run_finished = False
        self.finish_reason = "ПРОХОЖДЕНИЕ ЗАВЕРШЕНО"
        self.finish_buttons = []
        self.finish_selected = 0
        # entities
        self.player = None
        self.enemies_settings, self.enemies_sprites = load_all_enemies()
        self.entity_manager = EntityManager(
            self.resource_manager,
            self.enemies_settings,
            self.enemies_sprites,
            difficulty=self.options["difficulty"],
        )
        # background
        self.bg_thread = threading.Thread(
            target=self.chunk_system._bg_generation_worker,
            args=(self.generator.generate_chunk_math,),
            daemon=True,
        )
        self.bg_thread.start()
        # other
        self.chunk_pixel_size = game_settings.CHUNK_SIZE * game_settings.TILE_SIZE
        self.tile_size = game_settings.TILE_SIZE
        self.base_seed = game_settings.SEED

    def start_new_game(self):
        self.chunk_system.loaded_chunks.clear()
        if hasattr(self.chunk_system, "cached_chunks"):
            self.chunk_system.cached_chunks.clear()
        if hasattr(self.chunk_system, "all_blocked_subtiles"):
            self.chunk_system.all_blocked_subtiles.clear()
        self.entity_manager.enemies.clear()
        self.entity_manager.management_timer = 0.0
        self.entity_manager.set_difficulty(self.options["difficulty"])

        self.statistics_manager = StatisticsManager(self.options["difficulty"])
        self.run_finished = False
        self.statistics_open = False
        self.state = GameState.PLAYING

        raw_start_chunk = self.generator.generate_chunk_math(0, 0)
        center_chunk = self.generator.generate_chunk_visual(raw_start_chunk)
        self.chunk_system.loaded_chunks[(0, 0)] = center_chunk
        self.chunk_system.all_blocked_subtiles |= center_chunk["blocked_subtiles"]

        spawn_x, spawn_y = find_save_spot(center_chunk)
        self.player = Player(spawn_x, spawn_y, self.resource_manager, PLAYER_SPRITES)
        self.camera.snap_to(self.player)

        self.chunk_system.update(
            player_world_x=self.player.x,
            player_world_y=self.player.y,
            math_generator_func=self.generator.generate_chunk_math,
            visual_generator_func=self.generator.generate_chunk_visual,
        )

    def _finish_run(self, reason):
        if self.run_finished:
            return
        self.statistics_manager.finish_run(self.statistics_storage)
        self.run_finished = True
        self.finish_reason = reason
        self.finish_selected = 0
        self.state = GameState.PAUSED

    def _return_to_main_menu(self):
        self.main_menu_open = True
        self.difficulty_open = False
        self.run_finished = False
        self.statistics_open = False
        self.player = None
        self.entity_manager.enemies.clear()
        self.main_menu.selected = 0
        self.pause_menu.screen = "main"
        self.pause_menu.selected = 0

    def run(self):
        while self.running:
            pygame.display.set_caption(f"My World — {self.clock.get_fps():.0f} FPS")
            dt = self.clock.tick(game_settings.FPS) / 1000
            self._handle_events()
            self._update(dt)
            self._draw()

        try:
            self.chunk_system.generation_queue.put((None, None))
        except Exception:
            pass
        pygame.quit()

    def _handle_finish_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w, pygame.K_DOWN, pygame.K_s):
                self.finish_selected = 1 - self.finish_selected
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                if self.finish_selected == 0:
                    self._return_to_main_menu()
                else:
                    self.running = False
            elif event.key == pygame.K_ESCAPE:
                self._return_to_main_menu()
        elif event.type == pygame.MOUSEMOTION:
            for i, rect in enumerate(self.finish_buttons):
                if rect.collidepoint(event.pos):
                    self.finish_selected = i
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i, rect in enumerate(self.finish_buttons):
                if rect.collidepoint(event.pos):
                    self.finish_selected = i
                    if i == 0:
                        self._return_to_main_menu()
                    else:
                        self.running = False

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if not self.main_menu_open and not self.run_finished and self.player is not None:
                    self._finish_run("ЗАБЕГ ПОКИНУТ")
                else:
                    self.running = False
                continue

            if self.run_finished:
                self._handle_finish_event(event)
                continue

            if self.main_menu_open:
                if self.statistics_open:
                    action = self.statistics_menu.handle_event(event)
                    if action == "back":
                        self.statistics_open = False
                    continue

                if self.difficulty_open:
                    choice = self.difficulty_menu.handle_event(event)
                    if choice == "back":
                        self.difficulty_open = False
                    elif choice:
                        self.options["difficulty"] = choice
                        save_options(self.options)
                        self.difficulty_open = False
                        self.main_menu_open = False
                        self.start_new_game()
                    continue

                if self.main_menu_settings_open:
                    self.pause_menu.handle_event(event)
                    self.options["difficulty"] = self.pause_menu.options["difficulty"]
                    self.entity_manager.set_difficulty(self.options["difficulty"])
                    if self.pause_menu.screen == "main":
                        self.main_menu_settings_open = False
                    continue

                action = self.main_menu.handle_event(event)
                if action == "new_game":
                    self.difficulty_open = True
                elif action == "statistics":
                    self.statistics_menu.refresh()
                    self.statistics_open = True
                elif action == "settings":
                    self.pause_menu.screen = "settings"
                    self.pause_menu.selected = 0
                    self.main_menu_settings_open = True
                elif action == "quit":
                    self.running = False
                continue

            if self.state == GameState.PAUSED and self.statistics_open:
                action = self.statistics_menu.handle_event(event)
                if action == "back":
                    self.statistics_open = False
                    self.pause_menu.selected = 2
                continue

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                if self.state == GameState.PLAYING:
                    self.state = GameState.PAUSED
                    self.pause_menu.screen = "main"
                    self.pause_menu.selected = 0
                elif self.state == GameState.PAUSED:
                    self.state = GameState.PLAYING
                continue

            if self.state == GameState.PAUSED:
                action = self.pause_menu.handle_event(event)
                self.options["difficulty"] = self.pause_menu.options["difficulty"]
                self.entity_manager.set_difficulty(self.options["difficulty"])
                if action == "resume":
                    self.state = GameState.PLAYING
                elif action == "statistics":
                    self.statistics_menu.refresh()
                    self.statistics_open = True
                elif action == "quit_confirmed":
                    self._finish_run("ЗАБЕГ ПОКИНУТ")
                elif action == "cancel_quit":
                    pass

    def _update(self, dt):
        if (
            self.main_menu_open or self.difficulty_open or self.run_finished
            or self.player is None or self.state != GameState.PLAYING
        ):
            return

        keys = pygame.key.get_pressed()
        alive_enemies = {
            id(enemy) for enemy in self.entity_manager.enemies
            if enemy.state != "dead"
        }
        self.player.update(keys, self.chunk_system, self.entity_manager, dt)

        for enemy in self.entity_manager.enemies:
            if id(enemy) in alive_enemies and enemy.state == "dead":
                if not getattr(enemy, "_statistics_kill_counted", False):
                    enemy._statistics_kill_counted = True
                    self.statistics_manager.register_kill()

        self.camera.update(self.player, dt)
        self.chunk_system.update(
            self.player.x, self.player.y,
            self.generator.generate_chunk_math,
            self.generator.generate_chunk_visual,
        )
        self.entity_manager.update(self.chunk_system, self.player, dt)

        if self.player.state == "dead":
            self._finish_run("ВЫ ПОГИБЛИ")

    def _draw_finish_screen(self):
        w, h = self.screen.get_size()
        dim = pygame.Surface((w, h), pygame.SRCALPHA)
        dim.fill((10, 15, 11, 205))
        self.screen.blit(dim, (0, 0))

        panel = pygame.Rect(0, 0, min(540, w - 36), min(390, h - 30))
        panel.center = (w // 2, h // 2)
        pygame.draw.rect(self.screen, (35, 29, 21), panel, border_radius=12)
        pygame.draw.rect(self.screen, (153, 112, 66), panel, 4, border_radius=12)

        title_font = pygame.font.SysFont("georgia", 38, bold=True)
        text_font = pygame.font.SysFont("couriernew", 19, bold=True)
        small_font = pygame.font.SysFont("couriernew", 15)
        title = title_font.render(self.finish_reason, True, (255, 226, 180))
        self.screen.blit(title, title.get_rect(center=(panel.centerx, panel.top + 62)))

        stats = [
            f"УБИЙСТВА: {self.statistics_manager.kills}",
            f"СЛОЖНОСТЬ: {self.statistics_manager.difficulty}",
        ]
        for i, line in enumerate(stats):
            rendered = text_font.render(line, True, (240, 222, 188))
            self.screen.blit(rendered, rendered.get_rect(center=(panel.centerx, panel.top + 135 + i * 34)))

        labels = ["В ГЛАВНОЕ МЕНЮ", "ВЫЙТИ ИЗ ИГРЫ"]
        self.finish_buttons = []
        button_w = min(340, panel.width - 50)
        for i, label in enumerate(labels):
            rect = pygame.Rect(0, 0, button_w, 46)
            rect.center = (panel.centerx, panel.top + 235 + i * 58)
            self.finish_buttons.append(rect)
            active = i == self.finish_selected
            pygame.draw.rect(self.screen, (190, 184, 104) if active else (88, 61, 39), rect, border_radius=6)
            pygame.draw.rect(self.screen, (83, 119, 57) if active else (105, 72, 45),
                             rect.inflate(-5, -5), border_radius=5)
            label_s = text_font.render(label, True, (255, 245, 210))
            self.screen.blit(label_s, label_s.get_rect(center=rect.center))

        hint = small_font.render("W / S — ВЫБОР     ENTER — ПОДТВЕРДИТЬ", True, (205, 185, 145))
        self.screen.blit(hint, hint.get_rect(center=(panel.centerx, panel.bottom - 17)))

    def _draw(self):
        if self.main_menu_open:
            if self.statistics_open:
                self.main_menu.draw(self.screen)
                self.statistics_menu.draw(self.screen)
            elif self.difficulty_open:
                self.difficulty_menu.draw(self.screen)
            elif self.main_menu_settings_open:
                self.main_menu.draw(self.screen)
                self.pause_menu.draw(self.screen)
            else:
                self.main_menu.draw(self.screen)
            pygame.display.flip()
            return

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

        if self.run_finished:
            self._draw_finish_screen()
        elif self.state == GameState.PAUSED:
            if self.statistics_open:
                self.statistics_menu.draw(self.screen)
            else:
                self.pause_menu.draw(self.screen)
        pygame.display.flip()

    def _collect_objects(self):
        queue = [{"sort_y": self.player.y if self.player else 0, "type": "player"}]

        for enemy in self.entity_manager.enemies:
            queue.append({"sort_y": enemy.y, "type": "enemy", "obj": enemy})

        for chunk in self.chunk_system.loaded_chunks.values():
            screen_x, screen_y = self.camera.apply_point(chunk["world_x"], chunk["world_y"])
            if (
                screen_x + self.chunk_pixel_size < -100
                or screen_x > self.screen.get_width() + 100
                or screen_y + self.chunk_pixel_size < -100
                or self.screen.get_height() + 100 < screen_y
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
                    "y": obj_draw_y,
                })
        return queue

    def _draw_world_tiles(self):
        for chunk in self.chunk_system.loaded_chunks.values():
            screen_x, screen_y = self.camera.apply_point(chunk["world_x"], chunk["world_y"])
            if (
                screen_x + self.chunk_pixel_size < 0
                or screen_x > self.screen.get_width()
                or screen_y + self.chunk_pixel_size < 0
                or screen_y > self.screen.get_height()
            ):
                continue
            self.screen.blit(chunk["visual_surface"], (screen_x, screen_y))
