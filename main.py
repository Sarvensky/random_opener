import customtkinter as ctk
import configparser
import os
import random
import subprocess
import sys
from pathlib import Path

# --- КОНСТАНТЫ ---
CONFIG_FILE = "settings.ini"
CONFIG_SECTION = "Settings"
DEFAULT_EXTENSIONS = ".mp4, .mkv, .avi"
# Путь к папке "Видео" пользователя для использования по умолчанию.
DEFAULT_SCAN_PATH = str(Path.home() / "Videos")


# --- УТИЛИТАРНЫЕ ФУНКЦИИ ---


def load_or_create_config(config_file: str) -> tuple[str, list[str]]:
    """Загружает конфигурацию из .ini файла или создает его с настройками по умолчанию."""
    config = configparser.ConfigParser()

    if not os.path.exists(config_file):
        # Создаем конфиг по умолчанию, если файл не найден
        config[CONFIG_SECTION] = {
            "directory": DEFAULT_SCAN_PATH,
            "extensions": DEFAULT_EXTENSIONS,
        }
        with open(config_file, "w", encoding="utf-8") as f:
            config.write(f)

    config.read(config_file, encoding="utf-8")

    directory = config.get(CONFIG_SECTION, "directory", fallback=DEFAULT_SCAN_PATH)
    extensions_str = config.get(
        CONFIG_SECTION, "extensions", fallback=DEFAULT_EXTENSIONS
    )
    extensions = [ext.strip() for ext in extensions_str.split(",")]
    return directory, extensions


def find_files(directory: str, extensions: list[str]) -> list[str]:
    """Рекурсивно ищет файлы с заданными расширениями в указанной директории."""
    if not os.path.isdir(directory):
        # Возвращаем пустой список, если директория не существует.
        # Обработка ошибки будет в UI.
        return []

    found_files = []

    for root, dirs, files in os.walk(directory):
        for file in files:
            if any(file.endswith(ext) for ext in extensions):
                full_path = os.path.join(root, file)
                found_files.append(full_path)

    return found_files


# --- КЛАСС ПРИЛОЖЕНИЯ ---


class App(ctk.CTk):
    """Основной класс приложения, который инкапсулирует всю логику и UI."""

    def __init__(self):
        super().__init__()

        # --- 1. Настройка окна ---
        self.title("Random File Opener v1.1")
        self.geometry("600x200")
        # Центрируем виджеты по горизонтали
        self.grid_columnconfigure(0, weight=1)

        # --- 2. Загрузка конфигурации и инициализация состояния ---
        self.directory_to_scan, self.file_extensions = load_or_create_config(
            CONFIG_FILE
        )
        self.file_list = []

        # --- 3. Создание виджетов ---
        self.label = ctk.CTkLabel(self, text="Инициализация...")
        self.label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.button = ctk.CTkButton(
            self, text="Выбрать случайный файл", command=self.on_button_click
        )
        self.button.grid(row=1, column=0, padx=20, pady=(10, 20))

        # --- 4. Первоначальное сканирование файлов ---
        self.refresh_file_list()

    def refresh_file_list(self):
        """Сканирует директорию, обновляет список файлов и UI."""
        self.file_list = find_files(self.directory_to_scan, self.file_extensions)

        if not os.path.isdir(self.directory_to_scan):
            self.label.configure(
                text=f"Ошибка: Папка не найдена!\n{self.directory_to_scan}",
                text_color="red",
            )
        else:
            self.label.configure(
                text=f"Найдено файлов: {len(self.file_list)}",
                text_color=self.label.cget("text_color"),
            )

    def open_random_file(self):
        """Выбирает и открывает случайный файл из списка."""
        if not self.file_list:
            self.label.configure(text="Файлы с указанными расширениями не найдены.")
            return

        random_file = random.choice(self.file_list)
        filename = os.path.basename(random_file)
        self.label.configure(text=f"Выбрано: {filename}")

        # Открываем файл с помощью приложения по умолчанию
        try:
            if sys.platform == "win32":
                os.startfile(random_file)
            elif sys.platform == "darwin":  # macOS
                subprocess.call(["open", random_file])
            else:  # linux variants
                subprocess.call(["xdg-open", random_file])
        except Exception as e:
            error_message = f"Ошибка открытия файла: {e}"
            self.label.configure(text=error_message)
            print(f"Не удалось открыть файл {random_file}: {e}")

    def on_button_click(self):
        """Обработчик нажатия на основную кнопку."""
        self.open_random_file()


# --- ТОЧКА ВХОДА В ПРОГРАММУ ---

if __name__ == "__main__":
    app = App()
    app.mainloop()
