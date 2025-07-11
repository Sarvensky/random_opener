import random
import re
from pathlib import Path
from send2trash import send2trash

from config import load_or_create_config, save_config, CONFIG_FILE
from file_utils import find_files, open_file, show_file_in_explorer


class AppLogic:
    """
    Класс, инкапсулирующий основную логику приложения,
    не зависящую от пользовательского интерфейса.
    """

    def __init__(self):
        """Инициализирует состояние приложения, загружая конфигурацию."""
        # Загружаем начальную конфигурацию
        (
            self.directory_to_scan,
            self.file_extensions,
            self.recursive_scan,
        ) = load_or_create_config(CONFIG_FILE)
        self.file_list = []
        self.subdirectories = []
        self.selected_subdirectory: str | None = None  # None означает "Искать везде"
        self.last_selected_file: Path | None = None

        # Выполняем первоначальное сканирование
        self.update_subdirectories()
        self.refresh_file_list()

    def get_scan_path(self) -> Path:
        """Определяет корневой путь для сканирования на основе выбранной подпапки."""
        main_path = Path(self.directory_to_scan)
        if self.selected_subdirectory:
            return main_path / self.selected_subdirectory
        return main_path

    def refresh_file_list(self) -> tuple[str, str]:
        """
        Сканирует указанную директорию на наличие файлов с заданными расширениями.
        Возвращает кортеж (сообщение, статус) для UI.
        """
        scan_path = self.get_scan_path()
        if not scan_path.is_dir():
            self.file_list = []
            return (
                f"Ошибка: Папка не найдена!\n{scan_path}",
                "error",
            )

        self.file_list = find_files(
            str(scan_path), self.file_extensions, self.recursive_scan
        )
        return f"Найдено файлов: {len(self.file_list)}", "info"

    def update_subdirectories(self) -> list[str]:
        """Сканирует и обновляет список подпапок первого уровня."""
        self.subdirectories = []
        scan_path = Path(self.directory_to_scan)
        if not scan_path.is_dir():
            return []

        try:
            self.subdirectories = sorted(
                [p.name for p in scan_path.iterdir() if p.is_dir()]
            )
        except OSError as e:
            print(f"Ошибка сканирования подпапок в {scan_path}: {e}")
            self.subdirectories = []

        return self.subdirectories

    def select_new_directory(self, new_directory: str) -> tuple[str, str] | None:
        """
        Обновляет рабочую директорию, сохраняет конфигурацию и обновляет список файлов.
        """
        if new_directory and new_directory != self.directory_to_scan:
            self.directory_to_scan = new_directory
            self.last_selected_file = None
            self.selected_subdirectory = None  # Сбрасываем на "Искать везде"
            self.update_subdirectories()  # Обновляем список подпапок
            save_config(
                self.directory_to_scan,
                self.file_extensions,
                self.recursive_scan,
                CONFIG_FILE,
            )
            return self.refresh_file_list()
        return None  # Нет изменений

    def update_extensions(
        self, extensions_str: str
    ) -> tuple[str, str | None, str | None]:
        """
        Обрабатывает строку с расширениями, обновляет конфигурацию и список файлов.
        Возвращает (очищенная_строка, сообщение_для_ui, статус).
        """
        raw_parts = re.split(r"[\s,]+", extensions_str)
        cleaned_extensions = []
        seen = set()
        for part in raw_parts:
            clean_part = part.strip().lstrip(".")
            if clean_part and clean_part not in seen:
                cleaned_extensions.append(clean_part)
                seen.add(clean_part)

        new_extensions_with_dots = [f".{ext}" for ext in cleaned_extensions]
        cleaned_display_str = ", ".join(cleaned_extensions)

        if set(new_extensions_with_dots) != set(self.file_extensions):
            self.file_extensions = new_extensions_with_dots
            save_config(
                self.directory_to_scan,
                self.file_extensions,
                self.recursive_scan,
                CONFIG_FILE,
            )
            self.last_selected_file = None
            message, status = self.refresh_file_list()
            return cleaned_display_str, message, status

        # Возвращаем очищенную строку для консистентности UI, но без сообщения
        return cleaned_display_str, None, None

    def set_selected_subdirectory(
        self, subdir_name: str | None
    ) -> tuple[str, str] | None:
        """Обновляет выбранную подпапку и обновляет список файлов."""
        if subdir_name != self.selected_subdirectory:
            self.selected_subdirectory = subdir_name
            self.last_selected_file = None
            # Эта настройка не сохраняется в конфиг, это временный фильтр
            return self.refresh_file_list()
        return None

    def set_recursive_scan(self, is_recursive: bool) -> tuple[str, str] | None:
        """
        Обновляет настройку рекурсивного сканирования и список файлов.
        """
        if is_recursive != self.recursive_scan:
            self.recursive_scan = is_recursive
            self.last_selected_file = None
            save_config(
                self.directory_to_scan,
                self.file_extensions,
                self.recursive_scan,
                CONFIG_FILE,
            )
            return self.refresh_file_list()
        return None

    def get_random_file(self) -> tuple[Path | None, str]:
        """
        Выбирает случайный файл из списка.
        Возвращает (путь_к_файлу, сообщение_для_ui).
        """
        if not self.file_list:
            return None, "Файлы с указанными расширениями не найдены."

        random_file_path_str = random.choice(self.file_list)
        self.last_selected_file = Path(random_file_path_str)
        return self.last_selected_file, f"Выбрано: {self.last_selected_file.name}"

    def open_last_file(self) -> str:
        """Открывает последний выбранный файл. Возвращает статус операции."""
        if not self.last_selected_file:
            return "Файл не был выбран."
        try:
            open_file(str(self.last_selected_file))
            return "success"
        except IOError as e:
            # В `e` уже обернуто имя файла из file_utils
            return f"Ошибка открытия файла:\n{Path(str(e)).name}"

    def show_last_file_in_explorer(self) -> str:
        """Показывает последний выбранный файл в проводнике. Возвращает статус."""
        if not self.last_selected_file:
            return "Файл не был выбран."
        try:
            show_file_in_explorer(str(self.last_selected_file))
            return "success"
        except (IOError, FileNotFoundError) as e:
            self.last_selected_file = None  # Файл больше не существует
            return f"Ошибка:\n{e}"

    def delete_last_file(self) -> tuple[str, str]:
        """Перемещает последний выбранный файл в корзину. Возвращает (сообщение, статус)."""
        if not self.last_selected_file:
            return "Еще ничего не выбиралось.", "info"

        file_to_delete = self.last_selected_file
        filename = file_to_delete.name

        if not file_to_delete.exists():
            self.last_selected_file = None
            return f"Файл '{filename}' уже удален или перемещен.", "error"

        try:
            send2trash(str(file_to_delete))
            self.last_selected_file = None
            # Обновляем список файлов после удаления
            self.refresh_file_list()
            return f"Файл '{filename}' перемещен в корзину.", "success"
        except OSError as e:
            print(f"Не удалось удалить файл {file_to_delete}: {e}")
            return f"Ошибка удаления файла:\n{filename}", "error"
