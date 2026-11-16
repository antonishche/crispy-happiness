import pygame

from entities.base.creature import Creature
from config.player.player_sprites_config import PLAYER_SETTINGS
from core.chunk_system import ChunkSystem


class Player(Creature):
    MAX_STAMINA = 100.0
    ATTACK_STAMINA_COST = 20.0
    STAMINA_REGEN_PER_SECOND = 12.0

    HEALTH_REGEN_PER_SECOND = 2.0
    HEALTH_REGEN_DELAY = 10.0

    def __init__(self, x, y, resource_manager, player_sprites):
        super().__init__(x, y, resource_manager, PLAYER_SETTINGS, player_sprites)
        self.target_enemy = None
        self.max_stamina = self.MAX_STAMINA
        self.stamina = self.max_stamina
        self.attack_active = False
        self.time_since_combat = 0.0
        self._last_hp = self.hp
        self._l_key_was_down = False

    def notify_damage(self):
        self.time_since_combat = 0.0

    def take_damage(self, amount):
        self.hp = max(0, self.hp - amount)
        self.notify_damage()
        if self.hp <= 0:
            self.state = "dead"
            self.frame_index = 0

    def update(self, keys, chunk_system: ChunkSystem, entity_manager, dt=1.0):
        if self.state == "dead":
            self.momentum_x = 0.0
            self.momentum_y = 0.0
            self.attack_active = False
            self._last_hp = self.hp
            self._animate(dt)
            return

        dt = max(0.0, dt)
        self.attack_cooldown_timer = max(0.0, self.attack_cooldown_timer - dt)

        if self.hp < self._last_hp:
            self.time_since_combat = 0.0
        self._last_hp = self.hp

        self._handle_lie_input(keys)

        move_left = keys[pygame.K_LEFT] or keys[pygame.K_a]
        move_right = keys[pygame.K_RIGHT] or keys[pygame.K_d]
        move_up = keys[pygame.K_UP] or keys[pygame.K_w]
        move_down = keys[pygame.K_DOWN] or keys[pygame.K_s]
        any_movement = move_left or move_right or move_up or move_down
        want_attack = keys[pygame.K_SPACE]

        if self.state == "sleep":
            if any_movement or want_attack:
                self._wake_up()
            else:
                self.dir_x = 0
                self.dir_y = 0
                self.momentum_x *= self.friction
                self.momentum_y *= self.friction
                self.attack_active = False
                self._move(chunk_system)
                self._animate(dt)
                self._update_health_regen(dt)
                return

        moving = any_movement

        if moving:
            self._handle_manual_movement(move_left, move_right, move_up, move_down)
            self.afk_timer = 0.0
        else:
            self._handle_idle_movement()

        if want_attack and not self.attack_active:
            self._try_start_attack(entity_manager)

        self._move(chunk_system)

        if not moving and self.ai_state == "idle" and not self.attack_active:
            self._update_afk_timer(dt)

        animation_finished = self._animate(
            dt, state_override="hit" if self.attack_active else None
        )
        if self.attack_active and animation_finished:
            self._finish_attack()

        if not self.attack_active:
            self.stamina = min(
                self.max_stamina,
                self.stamina + self.STAMINA_REGEN_PER_SECOND * dt
            )

        self._update_health_regen(dt)

    def _handle_lie_input(self, keys):
        l_down = bool(keys[pygame.K_l])
        if l_down and not self._l_key_was_down:
            if self.state != "sleep" and not self.attack_active:
                self.state = "sleep"
                self.ai_state = "idle"
                self.target_enemy = None
                self.dir_x = 0
                self.dir_y = 0
                self.momentum_x = 0.0
                self.momentum_y = 0.0
                self.frame_index = 0
        self._l_key_was_down = l_down

    def _update_health_regen(self, dt):
        if self.state == "sleep":
            if self.hp < self.max_hp:
                self.hp = min(
                    self.max_hp,
                    self.hp + self.HEALTH_REGEN_PER_SECOND * dt
                )
            return

        in_combat = (
            self.attack_active
            or self.attack_cooldown_timer > 0
            or (self.ai_state == "chase" and self.target_enemy and self.target_enemy.state != "dead")
        )

        if in_combat:
            self.time_since_combat = 0.0
            return

        self.time_since_combat += dt

        if self.time_since_combat < self.HEALTH_REGEN_DELAY:
            return

        if self.hp < self.max_hp:
            self.hp = min(
                self.max_hp,
                self.hp + self.HEALTH_REGEN_PER_SECOND * dt
            )

    def _wake_up(self):
        if self.state == "sleep":
            self.state = "idle"
            self.afk_timer = 0.0

    def _handle_manual_movement(self, left, right, up, down):
        self._wake_up()
        self.ai_state = "idle"
        if not self.attack_active:
            self.target_enemy = None
        self.dir_x = int(right) - int(left)
        self.dir_y = int(down) - int(up)

        if self.dir_x == 0:
            self.momentum_x *= self.friction
        else:
            self.momentum_x += self.dir_x * self.acceleration
            self.momentum_x = max(-self.speed, min(self.speed, self.momentum_x))

        if self.dir_y == 0:
            self.momentum_y *= self.friction
        else:
            self.momentum_y += self.dir_y * self.acceleration
            self.momentum_y = max(-self.speed, min(self.speed, self.momentum_y))

    def _handle_idle_movement(self):
        if self.ai_state == "chase" and self.target_enemy:
            if self.target_enemy.state == "dead":
                self.target_enemy = None
                self.ai_state = "idle"
            else:
                distance = abs(self.x - self.target_enemy.x) + abs(self.y - self.target_enemy.y)
                if distance <= self.action_range:
                    self.dir_x = self.dir_y = 0
                    self.momentum_x *= self.friction
                    self.momentum_y *= self.friction
                    if not self.attack_active and self.attack_cooldown_timer <= 0:
                        self._begin_attack(self.target_enemy)
                else:
                    self._move_to(self.target_enemy.x, self.target_enemy.y)
            return

        self.dir_x = self.dir_y = 0
        self.momentum_x *= self.friction
        self.momentum_y *= self.friction

    def _try_start_attack(self, entity_manager):
        if self.attack_active or self.attack_cooldown_timer > 0:
            return
        if self.stamina < self.ATTACK_STAMINA_COST:
            return

        self._wake_up()

        closest_enemy = None
        min_dist = float("inf")
        for enemy in entity_manager.enemies:
            if enemy.state == "dead":
                continue
            distance = abs(self.x - enemy.x) + abs(self.y - enemy.y)
            if distance < min_dist:
                min_dist = distance
                closest_enemy = enemy

        if closest_enemy and min_dist <= self.action_range:
            self._begin_attack(closest_enemy)
        elif closest_enemy and min_dist <= self.reaction_range:
            self.target_enemy = closest_enemy
            self.ai_state = "chase"
        else:
            self._begin_attack(None)

    def _begin_attack(self, target):
        if self.attack_active or self.stamina < self.ATTACK_STAMINA_COST:
            return
        self._wake_up()
        self.attack_active = True
        self.target_enemy = target
        self.stamina = max(0.0, self.stamina - self.ATTACK_STAMINA_COST)
        self.frame_index = 0
        self.frame_timer = 0.0
        self.last_full_key = ""
        self.time_since_combat = 0.0

    def _finish_attack(self):
        if self.target_enemy and self.target_enemy.state != "dead":
            self.target_enemy.hp -= self.damage
            if self.target_enemy.hp <= 0:
                self.target_enemy.hp = 0
                self.target_enemy.state = "dead"
                self.target_enemy.frame_index = 0

        self.attack_active = False
        self.attack_cooldown_timer = self.attack_cooldown
        self.target_enemy = None
        self.ai_state = "idle"
        self.frame_index = 0
        self.frame_timer = 0.0
        self.last_full_key = ""
        self.afk_timer = 0.0
        self.time_since_combat = 0.0

    def _update_afk_timer(self, dt):
        if self.state == "idle":
            self.afk_timer += dt
            if self.afk_timer >= 5.0:
                self.state = "sleep"
                self.frame_index = 0
                self.afk_timer = 0.0
        else:
            self.afk_timer = 0.0

    def _move(self, chunk_system):
        original_mx, original_my = self.momentum_x, self.momentum_y
        if int(self.momentum_x) != 0 and int(self.momentum_y) != 0:
            self.momentum_x *= 0.75
            self.momentum_y *= 0.75
        super()._move(chunk_system)
        self.momentum_x, self.momentum_y = original_mx, original_my