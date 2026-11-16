"""История прохождений в едином стиле игрового меню."""

from datetime import datetime
import pygame


class StatisticsMenu:
    FILTERS = ("Все", "Лёгкий", "Средний", "Сложный")

    def __init__(self, storage):
        self.storage = storage
        self.title_font = pygame.font.SysFont("georgia", 38, bold=True)
        self.font = pygame.font.SysFont("couriernew", 18, bold=True)
        self.small_font = pygame.font.SysFont("couriernew", 13)
        self.filter_index = 0
        self.selected = 0
        self.scroll = 0
        self.results = []
        self.visible_results = []
        self.row_rects = []
        self.filter_rects = []
        self.delete_rect = pygame.Rect(0, 0, 0, 0)
        self.back_rect = pygame.Rect(0, 0, 0, 0)
        self.refresh()

    def refresh(self):
        self.results = self.storage.load_results()
        self._apply_filter()

    def _apply_filter(self):
        difficulty = self.FILTERS[self.filter_index]
        records = self.results if difficulty == "Все" else [
            item for item in self.results if item.get("difficulty") == difficulty
        ]
        self.visible_results = list(reversed(records))
        self.selected = min(self.selected, max(0, len(self.visible_results) - 1))
        self.scroll = min(self.scroll, max(0, len(self.visible_results) - 1))

    @staticmethod
    def _format_date(value):
        if not value:
            return "—"
        try:
            date = datetime.fromisoformat(value.replace("Z", "+00:00"))
            return date.astimezone().strftime("%d.%m.%Y %H:%M")
        except (TypeError, ValueError):
            return str(value)

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

    @staticmethod
    def _button(surface, rect, label, font, active=False):
        pygame.draw.rect(surface, (35, 29, 21), rect.move(0, 4), border_radius=6)
        pygame.draw.rect(surface, (205, 194, 112) if active else (88, 61, 39),
                         rect, border_radius=6)
        pygame.draw.rect(surface, (83, 119, 57) if active else (105, 72, 45),
                         rect.inflate(-5, -5), border_radius=4)
        rendered = font.render(label, True, (255, 247, 211) if active else (239, 218, 181))
        surface.blit(rendered, rendered.get_rect(center=rect.center))

    def _layout(self, surface):
        width, height = surface.get_size()
        panel = pygame.Rect(0, 0, min(1040, width - 30), min(700, height - 30))
        panel.center = (width // 2, height // 2)

        filter_w = min(150, (panel.width - 58) // len(self.FILTERS))
        total_w = filter_w * len(self.FILTERS) + 8 * (len(self.FILTERS) - 1)
        start_x = panel.centerx - total_w // 2
        self.filter_rects = [
            pygame.Rect(start_x + i * (filter_w + 8), panel.top + 105, filter_w, 38)
            for i in range(len(self.FILTERS))
        ]

        list_top = panel.top + 165
        chart_top = panel.bottom - 140
        self.list_rect = pygame.Rect(panel.left + 28, list_top, panel.width - 56,
                                     max(90, chart_top - list_top - 30))
        row_h = 43
        max_rows = max(1, self.list_rect.height // row_h)
        self.scroll = max(0, min(self.scroll, max(0, len(self.visible_results) - max_rows)))
        self.row_rects = []
        for index in range(self.scroll, min(len(self.visible_results), self.scroll + max_rows)):
            rect = pygame.Rect(self.list_rect.left, self.list_rect.top + (index - self.scroll) * row_h,
                               self.list_rect.width, row_h - 4)
            self.row_rects.append((index, rect))

        button_y = panel.bottom - 73
        self.delete_rect = pygame.Rect(panel.centerx - 190, button_y, 180, 45)
        self.back_rect = pygame.Rect(panel.centerx + 10, button_y, 180, 45)
        self.chart_rect = pygame.Rect(panel.left + 30, panel.bottom - 132, panel.width - 60, 42)
        return panel

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_ESCAPE, pygame.K_BACKSPACE):
                return "back"
            if event.key in (pygame.K_LEFT, pygame.K_a):
                self.filter_index = (self.filter_index - 1) % len(self.FILTERS)
                self.selected = self.scroll = 0
                self._apply_filter()
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                self.filter_index = (self.filter_index + 1) % len(self.FILTERS)
                self.selected = self.scroll = 0
                self._apply_filter()
            elif event.key in (pygame.K_UP, pygame.K_w):
                self.selected = max(0, self.selected - 1)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.selected = min(max(0, len(self.visible_results) - 1), self.selected + 1)
            elif event.key == pygame.K_DELETE:
                self.delete_selected()
            self._keep_selection_visible()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i, rect in enumerate(self.filter_rects):
                if rect.collidepoint(event.pos):
                    self.filter_index = i
                    self.selected = self.scroll = 0
                    self._apply_filter()
                    return None
            for index, rect in self.row_rects:
                if rect.collidepoint(event.pos):
                    self.selected = index
                    return None
            if self.delete_rect.collidepoint(event.pos):
                self.delete_selected()
            elif self.back_rect.collidepoint(event.pos):
                return "back"
        return None

    def _keep_selection_visible(self):
        visible_count = max(1, len(self.row_rects))
        if self.selected < self.scroll:
            self.scroll = self.selected
        elif self.selected >= self.scroll + visible_count:
            self.scroll = self.selected - visible_count + 1

    def delete_selected(self):
        if not self.visible_results:
            return
        record = self.visible_results[self.selected]
        record_id = record.get("id")
        if record_id and self.storage.delete_result(record_id):
            self.refresh()

    def draw(self, surface):
        width, height = surface.get_size()
        dim = pygame.Surface((width, height), pygame.SRCALPHA)
        dim.fill((12, 20, 13, 155))
        surface.blit(dim, (0, 0))
        panel = self._layout(surface)
        self._draw_panel(surface, panel)

        title = self.title_font.render("ИСТОРИЯ ПРОХОЖДЕНИЙ", True, (255, 232, 180))
        surface.blit(title, title.get_rect(center=(panel.centerx, panel.top + 55)))
        pygame.draw.line(surface, (184, 145, 82), (panel.centerx - 90, panel.top + 88),
                         (panel.centerx + 90, panel.top + 88), 2)

        for i, rect in enumerate(self.filter_rects):
            self._button(surface, rect, self.FILTERS[i].upper(), self.small_font,
                         i == self.filter_index)

        headers = [
            ("МИР", 0.02), ("УБИЙСТВА", 0.47), ("СЛОЖНОСТЬ", 0.64), ("ДАТА", 0.82)
        ]
        for label, fraction in headers:
            text = self.small_font.render(label, True, (255, 226, 174))
            surface.blit(text, (self.list_rect.left + int(self.list_rect.width * fraction),
                                self.list_rect.top - 19))

        for index, rect in self.row_rects:
            record = self.visible_results[index]
            active = index == self.selected
            pygame.draw.rect(surface, (83, 119, 57) if active else (75, 55, 38),
                             rect, border_radius=4)
            pygame.draw.rect(surface, (192, 151, 91), rect, 1, border_radius=4)
            color = (255, 247, 211) if active else (235, 222, 190)
            values = [
                (str(record.get("world_name", "Мир")), 0.02, 0.42),
                (str(record.get("kills", 0)), 0.47, 0.13),
                (str(record.get("difficulty", "—")), 0.64, 0.16),
                (self._format_date(record.get("finished_at")), 0.82, 0.17),
            ]
            for value, fraction, max_fraction in values:
                rendered = self.small_font.render(value, True, color)
                max_width = int(rect.width * max_fraction)
                if rendered.get_width() > max_width:
                    value = value[:max(1, int(len(value) * max_width / rendered.get_width()) - 1)] + "…"
                    rendered = self.small_font.render(value, True, color)
                surface.blit(rendered, (rect.left + int(rect.width * fraction),
                                        rect.centery - rendered.get_height() // 2))

        if not self.visible_results:
            message = self.font.render("ПОКА НЕТ ЗАВЕРШЁННЫХ ПРОХОЖДЕНИЙ", True,
                                       (255, 226, 174))
            surface.blit(message, message.get_rect(center=self.list_rect.center))

        self._draw_chart(surface)
        self._button(surface, self.delete_rect, "УДАЛИТЬ", self.small_font,
                     bool(self.visible_results))
        self._button(surface, self.back_rect, "НАЗАД", self.small_font, True)

        hint = self.small_font.render(
            "← / → ФИЛЬТР     ↑ / ↓ ВЫБОР     DELETE УДАЛИТЬ     ESC НАЗАД",
            True, (207, 195, 151))
        surface.blit(hint, hint.get_rect(center=(panel.centerx, panel.bottom - 16)))

    def _draw_chart(self, surface):
        chart = self.chart_rect
        pygame.draw.line(surface, (184, 145, 82), chart.bottomleft, chart.bottomright, 2)
        records = list(reversed(self.visible_results[-20:]))
        if not records:
            return
        max_kills = max(1, max(int(item.get("kills", 0)) for item in records))
        slot = max(4, chart.width // len(records))
        bar_width = max(3, min(18, slot - 4))
        for i, record in enumerate(records):
            try:
                kills = max(0, int(record.get("kills", 0)))
            except (TypeError, ValueError):
                kills = 0
            bar_height = int((kills / max_kills) * (chart.height - 4))
            x = chart.left + i * slot + (slot - bar_width) // 2
            pygame.draw.rect(surface, (190, 151, 82),
                             pygame.Rect(x, chart.bottom - bar_height, bar_width, bar_height))
