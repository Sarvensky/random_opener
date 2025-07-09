import customtkinter as ctk
import os
import random

# Импортируем наши новые модули
from config import load_or_create_config, CONFIG_FILE
from file_utils import find_files, open_file


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
        # Сохраняем цвет текста по умолчанию для восстановления после ошибки
        self._default_text_color = ctk.ThemeManager.theme["CTkLabel"]["text_color"]

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
                text_color=self._default_text_color,
            )

    def open_random_file(self):
        """Выбирает и открывает случайный файл из списка."""
        if not self.file_list:
            self.label.configure(
                text="Файлы с указанными расширениями не найдены.",
                text_color=self._default_text_color,
            )
            return

        random_file = random.choice(self.file_list)
        filename = os.path.basename(random_file)
        self.label.configure(
            text=f"Выбрано: {filename}", text_color=self._default_text_color
        )

        # Открываем файл с помощью утилитарной функции
        try:
            open_file(random_file)
        except IOError as e:
            # IOError - это исключение, которое мы определили в file_utils
            error_message = f"Ошибка открытия файла:\n{os.path.basename(str(e))}"
            self.label.configure(text=error_message, text_color="red")
            print(f"Не удалось открыть файл {random_file}: {e}")

    def on_button_click(self):
        """Обработчик нажатия на основную кнопку."""
        self.open_random_file()
