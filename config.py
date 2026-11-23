import os
from pathlib import Path

# Đường dẫn thư mục gốc của project
BASE_DIR = Path(__file__).resolve().parent

def _load_env_file(env_path: Path):
    """Tự động đọc file .env (có fallback nếu chưa cài python-dotenv)"""
    try:
        from dotenv import load_dotenv
        load_dotenv(dotenv_path=env_path)
        return
    except ImportError:
        pass

    if not env_path.exists():
        return

    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, val = line.split("=", 1)
            key = key.strip()
            val = val.strip().strip("'\"")
            if key and key not in os.environ:
                os.environ[key] = val

_load_env_file(BASE_DIR / ".env")


class Config:
    """Quản lý tập trung mọi cấu hình của Bot"""

    BASE_DIR: Path = BASE_DIR
    DATA_DIR: Path = BASE_DIR / "data"
    TEMP_DIR: Path = BASE_DIR / "temp"
    LOGS_DIR: Path = BASE_DIR / "logs"

    # Discord Bot Settings
    DISCORD_TOKEN: str = os.getenv("DISCORD_TOKEN", "")
    COMMAND_PREFIX: str = os.getenv("COMMAND_PREFIX", "!")

    # Security Settings
    MASTER_KEY: str = os.getenv("SETUP_MASTER_KEY", "ditmemay")

    # AutoMod Settings
    SPAM_LIMIT: int = int(os.getenv("SPAM_LIMIT", "5"))
    SPAM_TIME: int = int(os.getenv("SPAM_TIME", "3"))
    BAD_WORDS: list[str] = [
        w.strip().lower()
        for w in os.getenv("BAD_WORDS", "từ_cấm_1,từ_cấm_2,toxic").split(",")
        if w.strip()
    ]

    # Logging Settings
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO").upper()

    @classmethod
    def ensure_directories(cls):
        """Khởi tạo các thư mục cần thiết nếu chưa tồn tại"""
        cls.DATA_DIR.mkdir(parents=True, exist_ok=True)
        cls.TEMP_DIR.mkdir(parents=True, exist_ok=True)
        cls.LOGS_DIR.mkdir(parents=True, exist_ok=True)


Config.ensure_directories()
