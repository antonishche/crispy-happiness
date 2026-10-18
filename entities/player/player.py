import pygame
import math
from entities.base.creature import Creature
from settings.player_settings import PLAYER_SETTINGS
from core.chunk_system import ChunkSystem


class Player(Creature):

    def __init__(self, x, y, resource_manager, player_sprites):
        super().__init__(x, y, resource_manager, PLAYER_SETTINGS, player_sprites)
        self.target_enemy = None

    def update(self, keys, chunk_system: ChunkSystem, entity_manager, dt=1.0):
        if self.state == "dead":
            self.momentum_x = 0.0
            self.momentum_y = 0.0
            self._animate(dt)
            return

        move_left = keys[pygame.K_LEFT] or keys[pygame.K_a]
        move_right = keys[pygame.K_RIGHT] or keys[pygame.K_d]
        move_up = keys[pygame.K_UP] or keys[pygame.K_w]
        move_down = keys[pygame.K_DOWN] or keys[pygame.K_s]
        is_moving_manually = move_left or move_right or move_up or move_down

        if is_moving_manually:
            self._handle_manual_movement(move_left, move_right, move_up, move_down)
        else:
            self._handle_combat_logic(keys, entity_manager, dt)

        self._move(chunk_system)
        
        if self.ai_state == "idle" and not is_moving_manually:
            self._update_afk_timer(dt)
            
        animation_finished = self._animate(dt)
        if self.state == "hit" and animation_finished:
            if self.target_enemy and self.target_enemy.state != "dead":
                self.target_enemy.hp -= self.damage
                if self.target_enemy.hp <= 0:
                    self.target_enemy.state = "dead"
                    self.target_enemy.frame_index = 0

            self.attack_cooldown_timer = self.attack_cooldown
            self.state = "idle"
            self.ai_state = "idle"
            self.target_enemy = None

    def _handle_manual_movement(self, move_left, move_right, move_up, move_down):
        self.state = "walk"
        self.ai_state = "idle"
        self.target_enemy = None

        self.dir_x = int(move_right) - int(move_left)
        if self.dir_x == 0:
            self.momentum_x *= self.friction
        else:
            self.momentum_x += self.dir_x * self.acceleration
            if abs(self.momentum_x) > self.speed: 
                self.momentum_x = self.dir_x * self.speed
                
        self.dir_y = int(move_down) - int(move_up)
        if self.dir_y == 0:
            self.momentum_y *= self.friction
        else:
            self.momentum_y += self.dir_y * self.acceleration
            if abs(self.momentum_y) > self.speed: 
                self.momentum_y = self.dir_y * self.speed

    def _handle_combat_logic(self, keys, entity_manager, dt):
        if self.attack_cooldown_timer > 0:
            self.attack_cooldown_timer -= dt

        if keys[pygame.K_SPACE] and self.state != "hit" and self.ai_state == "idle" and self.attack_cooldown_timer <= 0:
            self.frame_index = 0
            
            closest_enemy = None
            min_dist = float('inf')
            for enemy in entity_manager.enemies:
                if enemy.state == "dead":
                    continue
                d = abs(self.x - enemy.x) + abs(self.y - enemy.y)
                if d < min_dist:
                    min_dist = d
                    closest_enemy = enemy
            
            if closest_enemy and min_dist <= self.reaction_range:
                self.ai_state = "chase"
                self.target_enemy = closest_enemy
            else:
                self.state = "hit"
                self.ai_state = "idle"
                self.momentum_x = 0.0
                self.momentum_y = 0.0

        if self.state == "hit":
            self.dir_x = 0
            self.dir_y = 0
            self.momentum_x *= self.friction
            self.momentum_y *= self.friction

        elif self.ai_state == "chase" and self.target_enemy:
            dx = self.target_enemy.x - self.x
            dy = self.target_enemy.y - self.y
            dist = abs(dx) + abs(dy)
            
            if dist <= self.action_range:
                if self.attack_cooldown_timer <= 0:
                    self.state = "hit"
                    self.momentum_x = 0.0
                    self.momentum_y = 0.0
                else:
                    self.state = "idle"
            else:
                self.state = "walk"
                self._move_to(self.target_enemy.x, self.target_enemy.y)
        else:
            self.dir_x = 0
            self.dir_y = 0
            self.momentum_x *= self.friction
            self.momentum_y *= self.friction

    def _update_afk_timer(self, dt):
        if self.state in {"idle", "sleep", "dead"}:
            if self.state == "idle":
                self.afk_timer += dt

                if self.afk_timer >= 5.0:
                    self.state = "sleep"
                    self.frame_index = 0
                    self.afk_timer = 0.0
        else:
            self.afk_timer = 0.0

    def _move(self, chunk_system):
        orig_mx = self.momentum_x
        orig_my = self.momentum_y

        if int(self.momentum_x) != 0 and int(self.momentum_y) != 0:
            self.momentum_x *= 0.75
            self.momentum_y *= 0.75

        super()._move(chunk_system)

        self.momentum_x = orig_mx
        self.momentum_y = orig_my