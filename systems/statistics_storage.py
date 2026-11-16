"""Хранилище результатов завершённых прохождений.

История хранится в data/statistics.json относительно корня проекта.
Каждый вызов save_result добавляет новую запись, не заменяя предыдущие.
"""

import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4


class StatisticsStorage:
    """Загружает и сохраняет историю завершённых прохождений."""

    def __init__(self, file_path=None):
        # По умолчанию: <корень проекта>/data/statistics.json
        project_root = Path(__file__).resolve().parent.parent
        self.file_path = Path(file_path) if file_path else (
            project_root / "data" / "statistics.json"
        )

    def load_results(self):
        """Возвращает список сохранённых результатов.

        Если файла ещё нет, возвращает пустой список.
        Если JSON повреждён или имеет неверную структуру, сообщает об ошибке,
        не затирая существующий файл.
        """
        if not self.file_path.exists():
            return []

        try:
            with self.file_path.open("r", encoding="utf-8") as file:
                data = json.load(file)
        except json.JSONDecodeError as error:
            raise ValueError(
                f"Файл статистики повреждён: {self.file_path}"
            ) from error

        if not isinstance(data, list):
            raise ValueError(
                f"Неверный формат файла статистики: ожидался список записей "
                f"в {self.file_path}"
            )

        return data

    def save_result(self, result):
        """Добавляет результат прохождения в историю и возвращает запись."""
        if not isinstance(result, dict):
            raise TypeError("Результат прохождения должен быть словарём.")

        required_fields = ("world_name", "kills", "difficulty")
        missing_fields = [
            field for field in required_fields if field not in result
        ]

        if missing_fields:
            raise ValueError(
                "В результате отсутствуют обязательные поля: "
                + ", ".join(missing_fields)
            )

        kills = result["kills"]

        if isinstance(kills, bool) or not isinstance(kills, int) or kills < 0:
            raise ValueError(
                "Количество убийств должно быть целым числом >= 0."
            )

        record = {
            "id": str(uuid4()),
            "world_name": str(result["world_name"]),
            "kills": kills,
            "difficulty": str(result["difficulty"]),
            "finished_at": datetime.now(timezone.utc).isoformat(
                timespec="seconds"
            ),
        }

        results = self.load_results()
        results.append(record)
        self._write_results(results)

        return record

    def delete_result(self, result_id):
        """Удаляет одну запись по её уникальному ID.

        Возвращает True, если запись найдена и удалена, иначе False.
        """
        results = self.load_results()

        remaining = [
            item for item in results
            if item.get("id") != result_id
        ]

        if len(remaining) == len(results):
            return False

        self._write_results(remaining)
        return True

    def _write_results(self, results):
        """Атомарно записывает всю историю, чтобы снизить риск потери данных."""
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

        temp_path = None

        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=self.file_path.parent,
                prefix=self.file_path.name + ".",
                suffix=".tmp",
                delete=False,
            ) as temp_file:

                temp_path = Path(temp_file.name)

                json.dump(
                    results,
                    temp_file,
                    ensure_ascii=False,
                    indent=4
                )

                temp_file.write("\n")

            os.replace(temp_path, self.file_path)

        finally:
            if temp_path is not None and temp_path.exists():
                temp_path.unlink()