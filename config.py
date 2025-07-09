import configparser
import os
from pathlib import Path

# --- КОНСТАНТЫ ---
CONFIG_FILE = "settings.ini"
CONFIG_SECTION = "Settings"
DEFAULT_EXTENSIONS = ".mp4, .mkv, .avi"
# Путь к папке "Видео" пользователя для использования по умолчанию.
DEFAULT_SCAN_PATH = str(Path.home() / "Videos")


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
