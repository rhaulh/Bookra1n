import logging
import os
import time
from logging.handlers import RotatingFileHandler

def setup_logger():
    logs_dir = "logs"
    os.makedirs(logs_dir, exist_ok=True)

    timestamp = int(time.time())
    final_log_name = f"applogs_{timestamp}.log"

    log_path = os.path.join(logs_dir, final_log_name)

    logger = logging.getLogger("bookra1n")
    logger.setLevel(logging.DEBUG)

    if not logger.handlers:
        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s"
        )

        file_handler = RotatingFileHandler(
            log_path, maxBytes=2_000_000, backupCount=5, encoding="utf-8"
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.DEBUG)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(logging.DEBUG)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger
