import configparser
from pathlib import Path

# --- КОНСТАНТЫ ---
CONFIG_FILE = "settings.ini"
CONFIG_SECTION = "Settings"
DEFAULT_EXTENSIONS = ".mp4, .mkv, .avi"
# Путь к папке "Видео" пользователя для использования по умолчанию.
DEFAULT_SCAN_PATH = str(Path.home() / "Videos")


def load_or_create_config(config_file: str) -> tuple[str, list[str], bool]:
    """Загружает конфигурацию из .ini файла или создает его с настройками по умолчанию."""
    config = configparser.ConfigParser()
    config_path = Path(config_file)

    if not config_path.exists():
        # Создаем конфиг по умолчанию, если файл не найден
        config[CONFIG_SECTION] = {
            "directory": DEFAULT_SCAN_PATH,
            "extensions": DEFAULT_EXTENSIONS,
            "recursive": "true",
        }
        with config_path.open("w", encoding="utf-8") as f:
            config.write(f)

    config.read(config_path, encoding="utf-8")

    directory = config.get(CONFIG_SECTION, "directory", fallback=DEFAULT_SCAN_PATH)
    extensions_str = config.get(
        CONFIG_SECTION, "extensions", fallback=DEFAULT_EXTENSIONS
    )
    recursive = config.getboolean(CONFIG_SECTION, "recursive", fallback=True)
    extensions = [ext.strip() for ext in extensions_str.split(",")]
    return directory, extensions, recursive


def save_config(
    directory: str, extensions: list[str], recursive: bool, config_file: str
):
    """Сохраняет конфигурацию в .ini файл."""
    config = configparser.ConfigParser()
    config_path = Path(config_file)
    # Читаем существующий файл, чтобы не потерять другие секции, если они есть
    config.read(config_path, encoding="utf-8")

    if not config.has_section(CONFIG_SECTION):
        config.add_section(CONFIG_SECTION)

    config.set(CONFIG_SECTION, "directory", directory)
    config.set(CONFIG_SECTION, "extensions", ", ".join(extensions))
    config.set(CONFIG_SECTION, "recursive", str(recursive))

    with config_path.open("w", encoding="utf-8") as f:
        config.write(f)
