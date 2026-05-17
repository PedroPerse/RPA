import logging
from pathlib import Path

_logger: logging.Logger | None = None

LOG_FILE = "log_cnpj.txt"


def get_logger(log_dir: str = "logs") -> logging.Logger:
    global _logger
    if _logger is not None:
        return _logger

    Path(log_dir).mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("bot_verifica_cnpj")
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)-8s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    file_handler = logging.FileHandler(
        Path(log_dir) / LOG_FILE, encoding="utf-8", mode="a"
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    _logger = logger
    return logger
