import os
import subprocess
import sys
from pathlib import Path


def find_files(directory: str, extensions: list[str]) -> list[str]:
    """Рекурсивно ищет файлы с заданными расширениями в указанной директории."""
    p = Path(directory)
    if not p.is_dir():
        # Возвращаем пустой список, если директория не существует.
        # Обработка ошибки будет в UI.
        return []

    found_files = []
    for ext in extensions:
        # rglob выполняет рекурсивный поиск. Паттерн должен быть вида '*.ext'.
        pattern = f"*{ext}"
        found_files.extend(p.rglob(pattern))

    # Возвращаем список строк с абсолютными путями
    return [str(f.resolve()) for f in found_files]


def open_file(filepath: str):
    """
    Открывает файл с помощью приложения по умолчанию в зависимости от ОС.
    Вызывает IOError при ошибке.
    """
    try:
        if sys.platform == "win32":
            os.startfile(filepath)
        elif sys.platform == "darwin":  # macOS
            # check=True вызовет CalledProcessError, если команда завершится с ошибкой
            subprocess.run(["open", filepath], check=True)
        else:  # linux variants
            subprocess.run(["xdg-open", filepath], check=True)
    except (OSError, subprocess.CalledProcessError) as e:
        # Оборачиваем специфичные для платформы ошибки в общее исключение,
        # чтобы UI-слою не нужно было знать детали реализации.
        raise IOError(f"Не удалось запустить приложение для файла: {filepath}") from e


def show_file_in_explorer(filepath: str):
    """
    Открывает файловый менеджер и показывает указанный файл.
    Вызывает IOError при ошибке.
    """
    p = Path(filepath)
    if not p.is_file():
        raise FileNotFoundError(f"Файл не найден: {filepath}")

    try:
        if sys.platform == "win32":
            # /select,filepath - синтаксис для Проводника Windows.
            # check=True здесь не используется, т.к. explorer.exe может возвращать
            # ненулевой код завершения (например, 1) даже при успешном выполнении.
            subprocess.run(["explorer", "/select,", str(p)])
        elif sys.platform == "darwin":  # macOS
            # -R флаг для Finder
            subprocess.run(["open", "-R", str(p)], check=True)
        else:  # linux variants
            # Большинство файловых менеджеров откроют директорию.
            # Выделение файла не является стандартизированной функцией.
            directory = str(p.parent)
            subprocess.run(["xdg-open", directory], check=True)
    except (OSError, subprocess.CalledProcessError) as e:
        raise IOError(f"Не удалось открыть расположение файла: {filepath}") from e
