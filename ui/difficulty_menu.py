import pygame


class DifficultyMenu:
    """Выбор сложности. Сложность меняет только HP и урон врагов."""

    DIFFICULTIES = [
        ("Лёгкий", "Враги имеют меньше здоровья и наносят меньше урона.", "Коэффициенты здоровья и урона: ×0.75"),
        ("Средний", "Стандартная сложность с обычными характеристиками.", "Коэффициенты здоровья и урона: ×1.0"),
        ("Сложный", "Враги выносливее и наносят заметно больше урона.", "Коэффициенты здоровья и урона: ×1.5"),
    ]

    def __init__(self):
        self.selected = 1
        self.buttons = []
        self.title_font = pygame.font.SysFont("georgia", 44, bold=True)
        self.name_font = pygame.font.SysFont("couriernew", 25, bold=True)
        self.text_font = pygame.font.SysFont("couriernew", 17)
        self.hint_font = pygame.font.SysFont("couriernew", 15)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w):
                self.selected = (self.selected - 1) % 3
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.selected = (self.selected + 1) % 3
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                return self.DIFFICULTIES[self.selected][0]
            elif event.key == pygame.K_ESCAPE:
                return "back"
        elif event.type == pygame.MOUSEMOTION:
            for i, rect in enumerate(self.buttons):
                if rect.collidepoint(event.pos):
                    self.selected = i
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i, rect in enumerate(self.buttons):
                if rect.collidepoint(event.pos):
                    self.selected = i
                    return self.DIFFICULTIES[i][0]
        return None

    def draw(self, surface):
        w, h = surface.get_size()
        surface.fill((23, 32, 23))
        for x in range(0, w, 52):
            pygame.draw.line(surface, (29, 43, 29), (x, 0), (x, h), 1)

        panel = pygame.Rect(0, 0, min(820, w - 36), min(650, h - 32))
        panel.center = (w // 2, h // 2)
        pygame.draw.rect(surface, (12, 18, 13), panel.move(8, 9), border_radius=14)
        pygame.draw.rect(surface, (53, 43, 29), panel, border_radius=14)
        inner = panel.inflate(-10, -10)
        pygame.draw.rect(surface, (112, 76, 45), inner, border_radius=10)
        pygame.draw.rect(surface, (191, 147, 83), panel, 3, border_radius=14)

        title = self.title_font.render("ВЫБОР СЛОЖНОСТИ", True, (255, 232, 180))
        surface.blit(title, title.get_rect(center=(panel.centerx, panel.top + 60)))

        self.buttons = []
        gap = 13
        card_h = min(125, max(92, (panel.height - 185 - gap * 2) // 3))
        card_w = panel.width - 58
        start_y = panel.top + 112

        for i, (name, description, multiplier) in enumerate(self.DIFFICULTIES):
            rect = pygame.Rect(panel.centerx - card_w // 2, start_y + i * (card_h + gap), card_w, card_h)
            self.buttons.append(rect)
            active = i == self.selected
            pygame.draw.rect(surface, (36, 31, 22), rect.move(0, 4), border_radius=8)
            pygame.draw.rect(surface, (192, 192, 112) if active else (86, 60, 39), rect, border_radius=8)
            pygame.draw.rect(surface, (83, 117, 57) if active else (100, 69, 44),
                             rect.inflate(-5, -5), border_radius=6)

            name_s = self.name_font.render(name.upper(), True, (255, 240, 198))
            desc_s = self.text_font.render(description, True, (240, 224, 190))
            mult_s = self.text_font.render(multiplier, True, (205, 194, 145))
            surface.blit(name_s, (rect.left + 20, rect.top + 13))
            surface.blit(desc_s, (rect.left + 20, rect.top + 49))
            surface.blit(mult_s, (rect.left + 20, rect.top + 74))

        hint = self.hint_font.render("ENTER — НАЧАТЬ     ESC — НАЗАД", True, (210, 190, 150))
        surface.blit(hint, hint.get_rect(center=(panel.centerx, panel.bottom - 25)))
