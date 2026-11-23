import json
import asyncio
from pathlib import Path
from typing import Any, Dict, Optional
import logging

logger = logging.getLogger("SosaBot.Storage")

class JsonDatabase:
    """
    Hệ thống lưu trữ JSON thay thế Database nhẹ, có cơ chế an toàn:
    - Async Lock: Ngăn chặn xung đột ghi đè (Race Condition) khi nhiều lệnh chạy song song.
    - Atomic Write: Ghi ra file tạm trước khi đổi tên, chống hỏng file nếu bot tắt đột ngột.
    - Tự động nạp và tạo file mặc định nếu chưa tồn tại.
    """

    def __init__(self, file_path: Path, default_data: Optional[Dict[str, Any]] = None):
        self.file_path = Path(file_path)
        self.default_data = default_data or {}
        self._lock = asyncio.Lock()
        self._data: Dict[str, Any] = {}
        self._loaded = False

    async def load(self) -> Dict[str, Any]:
        """Nạp dữ liệu từ file JSON vào bộ nhớ (Cache)"""
        async with self._lock:
            if not self.file_path.exists():
                self.file_path.parent.mkdir(parents=True, exist_ok=True)
                self._data = self.default_data.copy()
                await self._save_unlocked()
            else:
                try:
                    loop = asyncio.get_event_loop()
                    content = await loop.run_in_executor(
                        None, lambda: self.file_path.read_text(encoding="utf-8")
                    )
                    self._data = json.loads(content) if content.strip() else self.default_data.copy()
                except Exception as e:
                    logger.error(f"Lỗi khi đọc file JSON {self.file_path}: {e}")
                    self._data = self.default_data.copy()
            self._loaded = True
            return self._data

    async def _save_unlocked(self):
        """Ghi dữ liệu an toàn kiểu Atomic (Write to temp -> Replace)"""
        temp_file = self.file_path.with_suffix(".tmp")
        loop = asyncio.get_event_loop()

        def _write():
            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump(self._data, f, ensure_ascii=False, indent=2)
            temp_file.replace(self.file_path)

        await loop.run_in_executor(None, _write)

    async def save(self):
        """Ghi dữ liệu hiện tại trong RAM xuống đĩa"""
        async with self._lock:
            await self._save_unlocked()

    async def get(self, key: str, default: Any = None) -> Any:
        """Lấy giá trị theo khóa"""
        if not self._loaded:
            await self.load()
        return self._data.get(str(key), default)

    async def set(self, key: str, value: Any):
        """Cập nhật giá trị và tự động lưu an toàn"""
        if not self._loaded:
            await self.load()
        async with self._lock:
            self._data[str(key)] = value
            await self._save_unlocked()

    async def delete(self, key: str) -> bool:
        """Xóa một khóa khỏi dữ liệu"""
        if not self._loaded:
            await self.load()
        async with self._lock:
            if str(key) in self._data:
                del self._data[str(key)]
                await self._save_unlocked()
                return True
            return False

    async def all(self) -> Dict[str, Any]:
        """Lấy toàn bộ dữ liệu dưới dạng dictionary"""
        if not self._loaded:
            await self.load()
        return self._data.copy()
