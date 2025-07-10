import os
import subprocess
import sys


def find_files(directory: str, extensions: list[str]) -> list[str]:
    """Рекурсивно ищет файлы с заданными расширениями в указанной директории."""
    if not os.path.isdir(directory):
        # Возвращаем пустой список, если директория не существует.
        # Обработка ошибки будет в UI.
        return []

    found_files = []

    # Используем `_` для неиспользуемой переменной `dirs`
    for root, _, files in os.walk(directory):
        for file in files:
            if any(file.endswith(ext) for ext in extensions):
                full_path = os.path.normpath(os.path.join(root, file))
                found_files.append(full_path)

    return found_files


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
    if not os.path.isfile(filepath):
        raise FileNotFoundError(f"Файл не найден: {filepath}")

    try:
        if sys.platform == "win32":
            # /select,filepath - синтаксис для Проводника Windows.
            # check=True здесь не используется, т.к. explorer.exe может возвращать
            # ненулевой код завершения (например, 1) даже при успешном выполнении.
            subprocess.run(["explorer", "/select,", filepath])
        elif sys.platform == "darwin":  # macOS
            # -R флаг для Finder
            subprocess.run(["open", "-R", filepath], check=True)
        else:  # linux variants
            # Большинство файловых менеджеров откроют директорию.
            # Выделение файла не является стандартизированной функцией.
            directory = os.path.dirname(filepath)
            subprocess.run(["xdg-open", directory], check=True)
    except (OSError, subprocess.CalledProcessError) as e:
        raise IOError(f"Не удалось открыть расположение файла: {filepath}") from e
