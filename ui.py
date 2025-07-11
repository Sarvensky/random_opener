import customtkinter as ctk
from customtkinter import filedialog

# Импортируем наши новые модули
from app_logic import AppLogic


class App(ctk.CTk):
    """Основной класс приложения, который инкапсулирует UI."""

    def __init__(self):
        super().__init__()

        # --- 1. Настройка окна ---
        self.title("Random File Opener v1.7")
        self.geometry("600x250")  # Высота окна для всех элементов
        # Настраиваем сетку: 3 колонки, третья (с полем ввода) растягивается
        self.grid_columnconfigure(2, weight=1)

        # --- 2. Инициализация логики и состояния UI ---
        self.logic = AppLogic()
        # Сохраняем цвет текста по умолчанию для восстановления после ошибки
        self._default_text_color = ctk.ThemeManager.theme["CTkLabel"]["text_color"]
        self._success_text_color = "green"
        self._error_text_color = "red"

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
            [ext.lstrip(".") for ext in self.logic.file_extensions]
        )
        self.extensions_entry.insert(0, extensions_for_display)
        self.extensions_entry.grid(
            row=0, column=2, padx=(5, 20), pady=(20, 10), sticky="ew"
        )
        # Привязываем обработчик к нажатию Enter для сохранения изменений
        self.extensions_entry.bind("<Return>", self.update_extensions_and_refresh)
        # Привязываем тот же обработчик к потере фокуса
        self.extensions_entry.bind("<FocusOut>", self.update_extensions_and_refresh)

        # --- Чек-бокс для рекурсивного поиска ---
        self.recursive_checkbox = ctk.CTkCheckBox(
            self,
            text="Искать во вложенных папках",
            command=self.toggle_recursive_search,
        )
        self.recursive_checkbox.grid(
            row=1, column=0, columnspan=3, padx=20, pady=(5, 0), sticky="w"
        )
        # Устанавливаем начальное состояние чек-бокса из логики
        if self.logic.recursive_scan:
            self.recursive_checkbox.select()
        else:
            self.recursive_checkbox.deselect()

        # Информационная надпись для основных сообщений
        self.info_label = ctk.CTkLabel(self, text="Инициализация...")
        self.info_label.grid(
            row=2, column=0, columnspan=3, padx=20, pady=10, sticky="ew"
        )

        # Метка для сообщений об ошибках и удалении
        self.error_label = ctk.CTkLabel(
            self, text="", text_color=self._error_text_color
        )
        self.error_label.grid(
            row=5, column=0, columnspan=3, padx=20, pady=(0, 10), sticky="ew"
        )

        # --- Фрейм для кнопок действия ---
        self.action_buttons_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.action_buttons_frame.grid(
            row=3, column=0, columnspan=3, padx=20, pady=(10, 10)
        )

        # Основная кнопка действия
        self.open_button = ctk.CTkButton(
            self.action_buttons_frame,  # Родитель - фрейм
            text="Открыть случайный файл",
            command=self.open_random_file,
        )
        self.open_button.grid(row=0, column=0, padx=(0, 5))

        # Кнопка "Открыть папку"
        self.open_folder_button = ctk.CTkButton(
            self.action_buttons_frame,  # Родитель - фрейм
            text="Открыть папку",
            command=self.open_containing_folder,
            state="disabled",  # Изначально неактивна
        )
        self.open_folder_button.grid(row=0, column=1, padx=(5, 0))
        # Кнопка удаления файла
        self.delete_button = ctk.CTkButton(
            self,
            text="Удалить последний файл",
            command=self.delete_last_file,
            fg_color="firebrick",
            hover_color="darkred",
            state="disabled",  # Изначально неактивна
        )
        self.delete_button.grid(row=4, column=0, columnspan=3, padx=20, pady=(0, 20))

        # --- 4. Первоначальное обновление UI ---
        self.refresh_ui_from_logic()

        # --- 5. Дополнительные привязки событий ---
        # Привязываем событие клика к самому окну.
        # Если кликнуть на пустое место, фокус уйдет с поля ввода,
        # что вызовет событие <FocusOut> и сохранит изменения.
        self.bind("<Button-1>", self.clear_focus_on_window_click)

    def clear_focus_on_window_click(self, event):
        """Снимает фокус с активного виджета при клике на пустое место окна."""
        if event.widget == self:
            self.focus()

    def toggle_recursive_search(self):
        """
        Обрабатывает изменение состояния чек-бокса рекурсивного поиска.
        """
        is_recursive = bool(self.recursive_checkbox.get())
        result = self.logic.set_recursive_scan(is_recursive)
        if result:
            message, status = result
            self._update_info_label(message, status)
            self._update_button_states()

    def update_extensions_and_refresh(self, event=None):
        """
        Передает строку с расширениями в логику, обновляет UI по результату.
        """
        extensions_str = self.extensions_entry.get()

        # Передаем в слой логики
        cleaned_display_str, message, status = self.logic.update_extensions(
            extensions_str
        )

        # Обновляем поле ввода, чтобы пользователь видел "очищенный" результат
        # Проверяем, отличается ли текст, чтобы избежать лишних действий
        if self.extensions_entry.get() != cleaned_display_str:
            self.extensions_entry.delete(0, "end")
            self.extensions_entry.insert(0, cleaned_display_str)

        # Если расширения изменились, логика вернет сообщение для отображения
        if message:
            self._update_info_label(message, status)
            self._update_button_states()

        # Убираем фокус с поля ввода после нажатия Enter для удобства
        if event and hasattr(event, "keysym") and event.keysym == "Return":
            self.focus()

    def refresh_ui_from_logic(self):
        """Обновляет все элементы UI на основе текущего состояния логики."""
        message, status = self.logic.refresh_file_list()
        self._update_info_label(message, status)
        self._update_button_states()

    def _update_info_label(self, text: str, status: str | None):
        """Обновляет основную информационную метку."""
        color = (
            self._error_text_color if status == "error" else self._default_text_color
        )
        self.info_label.configure(text=text, text_color=color)

    def _update_error_label(self, text: str, status: str):
        """Обновляет метку для ошибок и сообщений об успехе."""
        if status == "success":
            color = self._success_text_color
        elif status == "info":
            color = self._default_text_color
        else:  # error
            color = self._error_text_color
        self.error_label.configure(text=text, text_color=color)

    def _update_button_states(self):
        """Обновляет состояние кнопок в зависимости от состояния логики."""
        # Основная кнопка
        self.open_button.configure(
            state="normal" if self.logic.file_list else "disabled"
        )
        # Кнопки действий для последнего файла
        self.open_folder_button.configure(
            state="normal" if self.logic.last_selected_file else "disabled"
        )
        self.delete_button.configure(
            state="normal" if self.logic.last_selected_file else "disabled"
        )

    def open_random_file(self):
        """Обработчик нажатия на кнопку 'Открыть случайный файл'."""
        self._update_error_label("", "info")  # Очищаем старые сообщения

        file_path, message = self.logic.get_random_file()

        self._update_info_label(message, "info")
        self._update_button_states()

        if file_path:
            status = self.logic.open_last_file()
            if status != "success":
                self._update_error_label(status, "error")

    def select_directory(self):
        """Открывает диалог выбора директории и обновляет состояние."""
        new_directory = filedialog.askdirectory(
            initialdir=self.logic.directory_to_scan,
            title="Выберите папку для сканирования",
        )

        if new_directory:  # Пользователь выбрал папку, а не нажал "Отмена"
            result = self.logic.select_new_directory(new_directory)
            if result:
                message, status = result
                self._update_info_label(message, status)
                self._update_button_states()

    def open_containing_folder(self):
        """Открывает папку с последним выбранным файлом."""
        self._update_error_label("", "info")  # Очищаем старые сообщения
        status = self.logic.show_last_file_in_explorer()
        if status != "success":
            self._update_error_label(status, "error")
            # Если файл не найден, логика сбросила last_selected_file.
            # Обновим UI, чтобы отразить это (кнопки станут неактивными).
            self.refresh_ui_from_logic()

    def delete_last_file(self):
        """Удаляет последний выбранный файл."""
        message, status = self.logic.delete_last_file()
        self._update_error_label(message, status)
        # Состояние логики изменилось (файл удален, список обновлен),
        # поэтому полностью обновляем UI.
        self.refresh_ui_from_logic()
