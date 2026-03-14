import configparser
from pathlib import Path

# --- КОНСТАНТЫ ---
CONFIG_FILE = "settings.ini"
CONFIG_SECTION = "Settings"
DEFAULT_EXTENSIONS = ".mp4, .mkv, .avi"
# Путь к папке "Видео" пользователя для использования по умолчанию.
DEFAULT_SCAN_PATH = str(Path.home() / "Videos")


def load_or_create_config(
    config_file: str,
) -> tuple[str, list[str], bool, bool, list[str], list[str], bool, bool]:
    """Загружает конфигурацию из .ini файла или создает его с настройками по умолчанию."""
    config = configparser.ConfigParser()
    config_path = Path(config_file)

    if not config_path.exists():
        # Создаем конфиг по умолчанию, если файл не найден
        config[CONFIG_SECTION] = {
            "directory": DEFAULT_SCAN_PATH,
            "extensions": DEFAULT_EXTENSIONS,
            "recursive": "true",
            "toplevel_only": "true",
            "prefixes": "",
            "postfixes": "",
            "not_prefix": "false",
            "not_postfix": "false",
        }
        with config_path.open("w", encoding="utf-8") as f:
            config.write(f)

    config.read(config_path, encoding="utf-8")

    directory = config.get(CONFIG_SECTION, "directory", fallback=DEFAULT_SCAN_PATH)
    extensions_str = config.get(
        CONFIG_SECTION, "extensions", fallback=DEFAULT_EXTENSIONS
    )
    recursive = config.getboolean(CONFIG_SECTION, "recursive", fallback=True)
    toplevel_only = config.getboolean(CONFIG_SECTION, "toplevel_only", fallback=True)
    prefixes_str = config.get(CONFIG_SECTION, "prefixes", fallback="")
    postfixes_str = config.get(CONFIG_SECTION, "postfixes", fallback="")
    not_prefix = config.getboolean(CONFIG_SECTION, "not_prefix", fallback=False)
    not_postfix = config.getboolean(CONFIG_SECTION, "not_postfix", fallback=False)
    
    extensions = [ext.strip() for ext in extensions_str.split(",") if ext.strip()]
    prefixes = [p.strip() for p in prefixes_str.split(",") if p.strip()]
    postfixes = [p.strip() for p in postfixes_str.split(",") if p.strip()]
    
    return directory, extensions, recursive, toplevel_only, prefixes, postfixes, not_prefix, not_postfix


def save_config(
    directory: str,
    extensions: list[str],
    recursive: bool,
    toplevel_only: bool,
    prefixes: list[str],
    postfixes: list[str],
    not_prefix: bool,
    not_postfix: bool,
    config_file: str,
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
    config.set(CONFIG_SECTION, "toplevel_only", str(toplevel_only))
    config.set(CONFIG_SECTION, "prefixes", ", ".join(prefixes))
    config.set(CONFIG_SECTION, "postfixes", ", ".join(postfixes))
    config.set(CONFIG_SECTION, "not_prefix", str(not_prefix))
    config.set(CONFIG_SECTION, "not_postfix", str(not_postfix))

    with config_path.open("w", encoding="utf-8") as f:
        config.write(f)
