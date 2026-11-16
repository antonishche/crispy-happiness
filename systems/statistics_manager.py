"""Статистика текущего прохождения.

StatisticsManager собирает данные одного прохождения:
- название мира;
- выбранную сложность;
- количество подтверждённых убийств.

Когда игрок погибает, вызывающий код должен передать менеджеру систему
сохранения через finish_run(storage). Менеджер передаст ей итоговую запись.

Ожидаемый интерфейс системы сохранения:
    storage.save_result(result: dict)

Этот файл пока не подключается к игровому циклу.
"""


class StatisticsManager:
    """Собирает и завершает статистику одного прохождения."""

    def __init__(self, difficulty, world_name="Мир"):
        self.difficulty = difficulty
        self.world_name = world_name
        self.kills = 0
        self.finished = False

    def register_kill(self):
        """Засчитывает одно подтверждённое убийство."""
        if self.finished:
            return

        self.kills += 1

    def get_result(self):
        """Возвращает текущие данные прохождения в виде словаря."""
        return {
            "world_name": self.world_name,
            "kills": self.kills,
            "difficulty": self.difficulty,
        }

    def finish_run(self, storage):
        """Завершает прохождение и передаёт результат в систему сохранения.

        Этот метод нужно вызывать при смерти игрока.
        Повторный вызов не создаст вторую запись.
        """
        if self.finished:
            return None

        result = self.get_result()
        storage.save_result(result)
        self.finished = True
        return result
