import pygame


class MainMenu:
    """Полноэкранное главное меню в стилистике деревянного игрового интерфейса."""

    def __init__(self):
        self.items = [
            ("НОВАЯ ИГРА", "new_game"),
            ("СТАТИСТИКА", "statistics"),
            ("НАСТРОЙКИ", "settings"),
            ("ВЫХОД", "quit"),
        ]
        self.selected = 0
        self.button_rects = []
        self.title_font = pygame.font.SysFont("georgia", 64, bold=True)
        self.subtitle_font = pygame.font.SysFont("georgia", 22)
        self.button_font = pygame.font.SysFont("couriernew", 27, bold=True)
        self.hint_font = pygame.font.SysFont("couriernew", 15)

    @staticmethod
    def _draw_background(surface):
        w, h = surface.get_size()
        surface.fill((22, 30, 22))
        # Спокойный фон с затемнёнными вертикальными полосами.
        for x in range(0, w, 48):
            shade = 2 if (x // 48) % 2 else 0
            pygame.draw.rect(surface, (25 + shade, 37 + shade, 26 + shade), (x, 0, 48, h))
        pygame.draw.rect(surface, (14, 21, 16), (0, 0, w, h), 12)
        pygame.draw.line(surface, (75, 103, 57), (0, 18), (w, 18), 3)
        pygame.draw.line(surface, (75, 103, 57), (0, h - 18), (w, h - 18), 3)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w):
                self.selected = (self.selected - 1) % len(self.items)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.selected = (self.selected + 1) % len(self.items)
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                return self.items[self.selected][1]

        elif event.type == pygame.MOUSEMOTION:
            for i, rect in enumerate(self.button_rects):
                if rect.collidepoint(event.pos):
                    self.selected = i
                    break

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i, rect in enumerate(self.button_rects):
                if rect.collidepoint(event.pos):
                    self.selected = i
                    return self.items[i][1]
        return None

    def draw(self, surface):
        w, h = surface.get_size()
        self._draw_background(surface)

        # Панель растёт вместе с окном и не занимает весь экран на больших разрешениях.
        panel_w = min(int(w * 0.78), 760)
        panel_h = min(int(h * 0.88), 690)
        panel = pygame.Rect(0, 0, panel_w, panel_h)
        panel.center = (w // 2, h // 2)

        pygame.draw.rect(surface, (12, 18, 13), panel.move(9, 10), border_radius=16)
        pygame.draw.rect(surface, (49, 42, 29), panel, border_radius=16)
        inner = panel.inflate(-12, -12)
        pygame.draw.rect(surface, (105, 72, 43), inner, border_radius=12)
        body = inner.inflate(-8, -8)
        pygame.draw.rect(surface, (69, 83, 48), body, border_radius=9)
        pygame.draw.rect(surface, (192, 151, 91), panel, 3, border_radius=16)
        pygame.draw.rect(surface, (42, 54, 34), body, 2, border_radius=8)

        title = self.title_font.render("MY WORLD", True, (255, 232, 180))
        surface.blit(title, title.get_rect(center=(panel.centerx, panel.top + int(panel_h * 0.20))))
        subtitle = self.subtitle_font.render("ТВОЁ ПРИКЛЮЧЕНИЕ НАЧИНАЕТСЯ ЗДЕСЬ", True, (207, 195, 151))
        surface.blit(subtitle, subtitle.get_rect(center=(panel.centerx, panel.top + int(panel_h * 0.29))))

        ornament_y = panel.top + int(panel_h * 0.36)
        pygame.draw.line(surface, (184, 145, 82), (panel.centerx - 100, ornament_y),
                         (panel.centerx + 100, ornament_y), 2)
        pygame.draw.circle(surface, (221, 188, 119), (panel.centerx, ornament_y), 5)

        button_w = min(420, panel_w - 70)
        button_h = max(48, min(62, int(panel_h * 0.095)))
        gap = max(10, int(button_h * 0.25))
        total_h = len(self.items) * button_h + (len(self.items) - 1) * gap
        start_y = panel.top + int(panel_h * 0.43)
        self.button_rects = []

        for i, (label, _) in enumerate(self.items):
            rect = pygame.Rect(0, 0, button_w, button_h)
            rect.centerx = panel.centerx
            rect.y = start_y + i * (button_h + gap)
            self.button_rects.append(rect)

            active = i == self.selected
            outer = (205, 194, 112) if active else (88, 61, 39)
            fill = (83, 119, 57) if active else (105, 72, 45)
            text_color = (255, 247, 211) if active else (239, 218, 181)
            pygame.draw.rect(surface, (35, 29, 21), rect.move(0, 5), border_radius=7)
            pygame.draw.rect(surface, outer, rect, border_radius=7)
            pygame.draw.rect(surface, fill, rect.inflate(-5, -5), border_radius=5)
            pygame.draw.line(surface, (153, 178, 100) if active else (157, 111, 67),
                             (rect.left + 12, rect.top + 5), (rect.right - 12, rect.top + 5), 2)
            text = self.button_font.render(label, True, text_color)
            surface.blit(text, text.get_rect(center=rect.center))

        hint = self.hint_font.render("W / S ИЛИ СТРЕЛКИ — ВЫБОР     ENTER — ПОДТВЕРДИТЬ",
                                     True, (194, 180, 142))
        surface.blit(hint, hint.get_rect(center=(panel.centerx, panel.bottom - 28)))
