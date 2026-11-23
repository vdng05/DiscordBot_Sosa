import logging
import sys
from logging.handlers import RotatingFileHandler
from config import Config

def setup_logging(name: str = "SosaBot") -> logging.Logger:
    """
    Thiết lập hệ thống logging chuẩn:
    - Ghi log ra màn hình Console (stdout)
    - Ghi log ra file logs/bot.log với cơ chế xoay vòng (rotating, tối đa 5MB/file)
    """
    Config.ensure_directories()
    log_file = Config.LOGS_DIR / "bot.log"

    level = getattr(logging, Config.LOG_LEVEL, logging.INFO)

    formatter = logging.Formatter(
        fmt="[%(asctime)s] [%(levelname)-8s] [%(name)s]: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Tránh gắn handler nhiều lần nếu gọi hàm nhiều lần
    if not logger.handlers:
        # Handler xuất ra Console
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        console_handler.setLevel(level)
        logger.addHandler(console_handler)

        # Handler ghi file có xoay vòng (5MB mỗi file, lưu tối đa 5 file backup)
        file_handler = RotatingFileHandler(
            filename=log_file,
            maxBytes=5 * 1024 * 1024,
            backupCount=5,
            encoding="utf-8"
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(level)
        logger.addHandler(file_handler)

    return logger
