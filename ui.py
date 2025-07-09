import customtkinter as ctk
from customtkinter import filedialog
import os
import random
import re

# Импортируем наши новые модули
from config import load_or_create_config, save_config, CONFIG_FILE
from file_utils import find_files, open_file


class App(ctk.CTk):
    """Основной класс приложения, который инкапсулирует всю логику и UI."""

    def __init__(self):
        super().__init__()

        # --- 1. Настройка окна ---
        self.title("Random File Opener v1.3")
        self.geometry("600x250")  # Увеличим высоту для нового виджета
        # Настраиваем сетку: 3 колонки, третья (с полем ввода) растягивается
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=0)
        self.grid_columnconfigure(2, weight=1)

        # --- 2. Загрузка конфигурации и инициализация состояния ---
        self.directory_to_scan, self.file_extensions = load_or_create_config(
            CONFIG_FILE
        )
        self.file_list = []
        # Сохраняем цвет текста по умолчанию для восстановления после ошибки
        self._default_text_color = ctk.ThemeManager.theme["CTkLabel"]["text_color"]

        # --- 3. Создание виджетов ---
        # Кнопка выбора директории
        self.select_dir_button = ctk.CTkButton(
            self, text="Выбор папки", command=self.select_directory
        )
        self.select_dir_button.grid(row=0, column=0, padx=(20, 10), pady=(20, 10))

        # Надпись "Расширения" для наглядности
        self.extensions_label = ctk.CTkLabel(self, text="Расширения:")
        self.extensions_label.grid(row=0, column=1, padx=0, pady=(20, 10), sticky="w")

        # Поле для редактирования расширений
        self.extensions_entry = ctk.CTkEntry(
            self, placeholder_text="Расширения через запятую (напр. mp4, mkv)"
        )
        # Заполняем поле текущими расширениями, убрав точки
        extensions_for_display = ", ".join(
            [ext.lstrip(".") for ext in self.file_extensions]
        )
        self.extensions_entry.insert(0, extensions_for_display)
        self.extensions_entry.grid(
            row=0, column=2, padx=(5, 20), pady=(20, 10), sticky="ew"
        )
        # Привязываем обработчик к нажатию Enter для сохранения изменений
        self.extensions_entry.bind("<Return>", self.update_extensions_and_refresh)
        # Привязываем тот же обработчик к потере фокуса
        self.extensions_entry.bind("<FocusOut>", self.update_extensions_and_refresh)

        # Информационная надпись
        self.label = ctk.CTkLabel(self, text="Инициализация...")
        self.label.grid(row=1, column=0, columnspan=3, padx=20, pady=10, sticky="ew")

        # Основная кнопка действия
        self.open_button = ctk.CTkButton(
            self,
            text="Открыть случайный файл",
            command=self.on_button_click,
        )
        self.open_button.grid(row=2, column=0, columnspan=3, padx=20, pady=(10, 20))

        # --- 4. Первоначальное сканирование файлов ---
        self.refresh_file_list()

        # --- 5. Дополнительные привязки событий ---
        # Привязываем событие клика к самому окну.
        # Если кликнуть на пустое место, фокус уйдет с поля ввода,
        # что вызовет событие <FocusOut> и сохранит изменения.
        self.bind("<Button-1>", self.clear_focus_on_window_click)

    def clear_focus_on_window_click(self, event):
        """Снимает фокус с активного виджета при клике на пустое место окна."""
        if event.widget == self:
            self.focus()

    def update_extensions_and_refresh(self, event=None):
        """
        Обрабатывает, сохраняет и обновляет список расширений.
        Вызывается по нажатию Enter или потере фокуса полем ввода.
        """
        extensions_str = self.extensions_entry.get()

        # 1. Разделяем строку по запятым или пробелам, используя регулярное выражение
        raw_parts = re.split(r"[\s,]+", extensions_str)

        # 2. Очищаем список:
        #    - убираем лишние пробелы и точки в начале
        #    - отфильтровываем пустые строки
        #    - удаляем дубликаты, сохраняя порядок ввода
        cleaned_extensions = []
        for part in raw_parts:
            # Убираем пробелы по краям и возможную точку от пользователя
            clean_part = part.strip().lstrip(".")
            if clean_part and clean_part not in cleaned_extensions:
                cleaned_extensions.append(clean_part)

        # 3. Обновляем поле ввода, чтобы пользователь видел "очищенный" результат
        cleaned_display_str = ", ".join(cleaned_extensions)
        # Проверяем, отличается ли текст, чтобы избежать лишних действий
        if self.extensions_entry.get() != cleaned_display_str:
            self.extensions_entry.delete(0, "end")
            self.extensions_entry.insert(0, cleaned_display_str)

        # 4. Формируем итоговый список для использования в программе (с точками)
        new_extensions_with_dots = [f".{ext}" for ext in cleaned_extensions]

        # 5. Обновляем конфигурацию, только если список расширений действительно изменился
        if set(new_extensions_with_dots) != set(self.file_extensions):
            self.file_extensions = new_extensions_with_dots
            save_config(self.directory_to_scan, self.file_extensions, CONFIG_FILE)
            self.refresh_file_list()

        # 6. Убираем фокус с поля ввода после нажатия Enter для удобства
        if event and hasattr(event, "keysym") and event.keysym == "Return":
            self.focus()

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

    def select_directory(self):
        """Открывает диалог выбора директории и обновляет конфигурацию."""
        new_directory = filedialog.askdirectory(
            initialdir=self.directory_to_scan, title="Выберите папку для сканирования"
        )

        if new_directory:  # Пользователь выбрал папку, а не нажал "Отмена"
            self.directory_to_scan = new_directory
            # Сохраняем новую директорию в конфиг
            save_config(self.directory_to_scan, self.file_extensions, CONFIG_FILE)
            # Обновляем список файлов и UI
            self.refresh_file_list()
