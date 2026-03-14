import os
import subprocess
import sys
from pathlib import Path


def find_files(
    directory: str, 
    extensions: list[str], 
    recursive: bool,
    prefixes: list[str] | None = None,
    postfixes: list[str] | None = None,
    not_prefix: bool = False,
    not_postfix: bool = False,
) -> list[str]:
    """
    Рекурсивно ищет файлы с заданными расширениями в указанной директории.
    Применяет фильтрацию по префиксам и постфиксам имени файла (без расширения).
    
    Args:
        directory: Путь к директории для поиска
        extensions: Список расширений для поиска (например, ['.mp4', '.mkv'])
        recursive: Рекурсивный поиск во вложенных директориях
        prefixes: Список префиксов для фильтрации имён файлов
        postfixes: Список постфиксов для фильтрации имён файлов
        not_prefix: Если True, исключать файлы с указанными префиксами
        not_postfix: Если True, исключать файлы с указанными постфиксами
    """
    p = Path(directory)
    if not p.is_dir():
        # Возвращаем пустой список, если директория не существует.
        # Обработка ошибки будет в UI.
        return []

    glob_method = p.rglob if recursive else p.glob

    found_files = []
    for ext in extensions:
        # glob/rglob выполняет поиск. Паттерн должен быть вида '*.ext'.
        pattern = f"*{ext}"
        found_files.extend(glob_method(pattern))

    # Применяем фильтрацию по префиксам и постфиксам
    filtered_files = []
    for file_path in found_files:
        # Получаем имя файла без расширения
        file_name_without_ext = file_path.stem
        
        # Проверяем префиксы
        prefix_match = False
        if prefixes:
            prefix_match = any(
                file_name_without_ext.startswith(prefix) 
                for prefix in prefixes
            )
        else:
            prefix_match = True  # Если префиксы не заданы, считаем что совпадает
        
        # Проверяем постфиксы
        postfix_match = False
        if postfixes:
            postfix_match = any(
                file_name_without_ext.endswith(postfix) 
                for postfix in postfixes
            )
        else:
            postfix_match = True  # Если постфиксы не заданы, считаем что совпадает
        
        # Применяем инверсию если нужно
        if not_prefix:
            prefix_match = not prefix_match
        if not_postfix:
            postfix_match = not postfix_match
        
        # Файл подходит если совпадает и по префиксу и по постфиксу
        if prefix_match and postfix_match:
            filtered_files.append(file_path)

    # Возвращаем список строк с абсолютными путями
    return [str(f.resolve()) for f in filtered_files]


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
