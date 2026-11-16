"""Пауза, настройки/управление и подтверждение выхода из мира."""

import random
import pygame

from settings.options import load_options


class PauseMenu:
    def __init__(self):
        self.title_font = pygame.font.SysFont("georgia", 38, bold=True)
        self.font = pygame.font.SysFont("couriernew", 21, bold=True)
        self.text_font = pygame.font.SysFont("couriernew", 17)
        self.small_font = pygame.font.SysFont("couriernew", 14)
        self.items = [
            ("ПРОДОЛЖИТЬ", "resume"),
            ("НАСТРОЙКИ", "settings"),
            ("СТАТИСТИКА", "statistics"),
            ("ПОКИНУТЬ МИР", "quit"),
        ]
        self.selected = 0
        self.screen = "main"
        self.rects = []
        self.options = load_options()
        self.back_rect = None
        self.confirm_rects = []

    def handle_event(self, e):
        if self.screen == "main":
            return self._handle_main_event(e)
        if self.screen == "settings":
            return self._handle_settings_event(e)
        if self.screen == "confirm_exit":
            return self._handle_confirm_event(e)
        return None

    def _handle_main_event(self, e):
        if e.type == pygame.KEYDOWN:
            if e.key in (pygame.K_UP, pygame.K_w):
                self.selected = (self.selected - 1) % len(self.items)
            elif e.key in (pygame.K_DOWN, pygame.K_s):
                self.selected = (self.selected + 1) % len(self.items)
            elif e.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                return self._activate(self.items[self.selected][1])
        elif e.type == pygame.MOUSEMOTION:
            for i, rect in enumerate(self.rects):
                if rect.collidepoint(e.pos):
                    self.selected = i
                    break
        elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            for i, rect in enumerate(self.rects):
                if rect.collidepoint(e.pos):
                    self.selected = i
                    return self._activate(self.items[i][1])
        return None

    def _activate(self, action):
        if action == "settings":
            self.screen, self.selected = "settings", 0
        elif action == "quit":
            self.screen, self.selected = "confirm_exit", 1
        else:
            return action
        return None

    def _handle_settings_event(self, e):
        if e.type == pygame.KEYDOWN:
            if e.key in (pygame.K_ESCAPE, pygame.K_BACKSPACE, pygame.K_RETURN,
                         pygame.K_KP_ENTER, pygame.K_SPACE):
                self.screen, self.selected = "main", 1
        elif e.type == pygame.MOUSEMOTION:
            if self.back_rect and self.back_rect.collidepoint(e.pos):
                self.selected = 0
        elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            if self.back_rect and self.back_rect.collidepoint(e.pos):
                self.screen, self.selected = "main", 1
        return None

    def _handle_confirm_event(self, e):
        if e.type == pygame.KEYDOWN:
            if e.key in (pygame.K_LEFT, pygame.K_a, pygame.K_RIGHT, pygame.K_d):
                self.selected = 1 - self.selected
            elif e.key == pygame.K_ESCAPE:
                self.screen, self.selected = "main", 3
                return "cancel_quit"
            elif e.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                if self.selected == 0:
                    return "quit_confirmed"
                self.screen, self.selected = "main", 3
                return "cancel_quit"
        elif e.type == pygame.MOUSEMOTION:
            for i, rect in enumerate(self.confirm_rects):
                if rect.collidepoint(e.pos):
                    self.selected = i
        elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            for i, rect in enumerate(self.confirm_rects):
                if rect.collidepoint(e.pos):
                    self.selected = i
                    if i == 0:
                        return "quit_confirmed"
                    self.screen, self.selected = "main", 3
                    return "cancel_quit"
        return None

    @staticmethod
    def _draw_panel(surface, rect):
        pygame.draw.rect(surface, (12, 18, 13), rect.move(8, 9), border_radius=15)
        pygame.draw.rect(surface, (49, 42, 29), rect, border_radius=15)
        inner = rect.inflate(-10, -10)
        pygame.draw.rect(surface, (105, 72, 43), inner, border_radius=11)
        body = inner.inflate(-7, -7)
        pygame.draw.rect(surface, (69, 83, 48), body, border_radius=8)
        pygame.draw.rect(surface, (192, 151, 91), rect, 3, border_radius=15)
        pygame.draw.rect(surface, (42, 54, 34), body, 2, border_radius=8)
        grain = pygame.Surface(body.size, pygame.SRCALPHA)
        rng = random.Random(12)
        for _ in range(max(8, body.height // 12)):
            y = rng.randrange(4, max(5, body.height - 3))
            x = rng.randrange(5, max(6, body.width // 3))
            pygame.draw.line(grain, (30, 43, 27, 30), (x, y),
                             (min(body.width - 4, x + body.width // 3), y), 1)
        surface.blit(grain, body.topleft)

    @staticmethod
    def _draw_button(surface, rect, label, font, active=False):
        pygame.draw.rect(surface, (35, 29, 21), rect.move(0, 5), border_radius=7)
        pygame.draw.rect(surface, (205, 194, 112) if active else (88, 61, 39),
                         rect, border_radius=7)
        pygame.draw.rect(surface, (83, 119, 57) if active else (105, 72, 45),
                         rect.inflate(-5, -5), border_radius=5)
        color = (255, 247, 211) if active else (239, 218, 181)
        rendered = font.render(label, True, color)
        surface.blit(rendered, rendered.get_rect(center=rect.center))

    def _header(self, surface, panel, title):
        title_surface = self.title_font.render(title, True, (255, 232, 180))
        surface.blit(title_surface, title_surface.get_rect(center=(panel.centerx, panel.top + 55)))
        pygame.draw.line(surface, (184, 145, 82), (panel.centerx - 90, panel.top + 91),
                         (panel.centerx + 90, panel.top + 91), 2)
        pygame.draw.circle(surface, (221, 188, 119), (panel.centerx, panel.top + 91), 4)

    def _draw_main(self, surface, panel):
        self._header(surface, panel, "ПАУЗА")
        button_w = min(390, panel.width - 56)
        button_h = 52
        gap = 13
        total = len(self.items) * button_h + (len(self.items) - 1) * gap
        first_y = panel.centery - total // 2 + 24
        self.rects = []
        for i, (label, _) in enumerate(self.items):
            rect = pygame.Rect(0, first_y + i * (button_h + gap), button_w, button_h)
            rect.centerx = panel.centerx
            self.rects.append(rect)
            self._draw_button(surface, rect, label, self.font, i == self.selected)
        hint = self.small_font.render("W / S ИЛИ СТРЕЛКИ — ВЫБОР     ENTER — ПОДТВЕРДИТЬ",
                                      True, (207, 195, 151))
        surface.blit(hint, hint.get_rect(center=(panel.centerx, panel.bottom - 20)))

    def _draw_settings(self, surface, panel):
        self._header(surface, panel, "НАСТРОЙКИ")

        controls_title = self.text_font.render("УПРАВЛЕНИЕ", True, (255, 232, 180))
        surface.blit(controls_title, controls_title.get_rect(center=(panel.centerx, panel.top + 155)))

        controls = [
            ("W A S D / СТРЕЛКИ", "ПЕРЕМЕЩЕНИЕ"),
            ("ПРОБЕЛ", "АТАКА"),
            ("ESC", "ПАУЗА"),
        ]
        start_y = panel.top + 205
        for i, (key, action) in enumerate(controls):
            y = start_y + i * 48
            key_s = self.text_font.render(key, True, (255, 226, 174))
            action_s = self.text_font.render(action, True, (235, 222, 190))
            surface.blit(key_s, key_s.get_rect(midright=(panel.centerx - 15, y)))
            surface.blit(action_s, action_s.get_rect(midleft=(panel.centerx + 15, y)))

        self.back_rect = pygame.Rect(0, 0, 210, 48)
        self.back_rect.center = (panel.centerx, panel.bottom - 75)
        self._draw_button(surface, self.back_rect, "НАЗАД", self.font, self.selected == 0)
        hint = self.small_font.render("ESC — НАЗАД", True, (207, 195, 151))
        surface.blit(hint, hint.get_rect(center=(panel.centerx, panel.bottom - 24)))

    def _draw_confirm(self, surface, panel):
        self._header(surface, panel, "ПОКИНУТЬ МИР?")
        for i, line in enumerate(("Текущий забег будет завершён.",
                                  "Результат сохранится в статистике.")):
            rendered = self.text_font.render(line, True, (255, 239, 202))
            surface.blit(rendered, rendered.get_rect(center=(panel.centerx, panel.centery - 28 + i * 30)))
        self.confirm_rects = []
        for i, label in enumerate(("ДА, ЗАВЕРШИТЬ", "НЕТ, ВЕРНУТЬСЯ")):
            rect = pygame.Rect(0, 0, min(300, panel.width - 55), 48)
            rect.center = (panel.centerx, panel.centery + 65 + i * 60)
            self.confirm_rects.append(rect)
            self._draw_button(surface, rect, label, self.font, i == self.selected)

    def draw(self, surface):
        w, h = surface.get_size()
        dim = pygame.Surface((w, h), pygame.SRCALPHA)
        dim.fill((12, 20, 13, 150))
        surface.blit(dim, (0, 0))
        panel = pygame.Rect(0, 0, min(590, w - 36), min(510, h - 30))
        panel.center = (w // 2, h // 2)
        self._draw_panel(surface, panel)

        if self.screen == "main":
            self._draw_main(surface, panel)
        elif self.screen == "settings":
            self._draw_settings(surface, panel)
        else:
            self._draw_confirm(surface, panel)
