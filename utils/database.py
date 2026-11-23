import aiosqlite
from pathlib import Path
from typing import Any, List, Optional, Tuple, Dict
import logging
import time

logger = logging.getLogger("SosaBot.Database")

class DatabaseManager:
    """
    Quản lý SQLite bất đồng bộ (aiosqlite) siêu nhẹ và tối ưu cho VPS:
    - Bật chế độ WAL (Write-Ahead Logging) cho phép đọc và ghi song song không nghẽn.
    - Lưu toàn bộ dữ liệu trong 1 file đơn giản (data/sosapy.db).
    - Mặc định TẮT tất cả các tính năng tự động (AutoMod, Level/XP) khi bot vào server mới.
    """

    def __init__(self, db_path: Path):
        self.db_path = Path(db_path)
        self._db: Optional[aiosqlite.Connection] = None

    async def initialize(self):
        """Khởi tạo kết nối, bật chế độ WAL và tạo bảng tự động"""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._db = await aiosqlite.connect(self.db_path)

        # Bật chế độ WAL và tối ưu hóa hiệu năng I/O trên máy chủ
        await self._db.execute("PRAGMA journal_mode = WAL;")
        await self._db.execute("PRAGMA synchronous = NORMAL;")
        await self._db.execute("PRAGMA foreign_keys = ON;")

        # 1. Bảng cấu hình từng server (Mặc định automod và level ĐỀU TẮT: 0)
        await self._db.execute("""
            CREATE TABLE IF NOT EXISTS guild_settings (
                guild_id TEXT PRIMARY KEY,
                prefix TEXT DEFAULT '!',
                welcome_channel_id TEXT,
                music_channel_id TEXT,
                automod_enabled INTEGER DEFAULT 0,
                level_system_enabled INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # Migration an toàn nếu bảng cũ chưa có cột level_system_enabled
        try:
            await self._db.execute("ALTER TABLE guild_settings ADD COLUMN level_system_enabled INTEGER DEFAULT 0;")
        except Exception:
            pass  # Cột đã tồn tại

        # 2. Bảng Hệ thống Level / Rank (kinh nghiệm chat)
        await self._db.execute("""
            CREATE TABLE IF NOT EXISTS user_levels (
                guild_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                xp INTEGER DEFAULT 0,
                level INTEGER DEFAULT 1,
                last_xp_time REAL DEFAULT 0,
                PRIMARY KEY (guild_id, user_id)
            );
        """)

        # 3. Bảng Nhật ký AutoMod / Quản trị
        await self._db.execute("""
            CREATE TABLE IF NOT EXISTS mod_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                action TEXT NOT NULL,
                reason TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        await self._db.commit()
        logger.info(f"Đã kết nối và khởi tạo cơ sở dữ liệu SQLite tại: {self.db_path}")

    async def close(self):
        """Đóng kết nối an toàn khi bot tắt"""
        if self._db:
            await self._db.close()
            logger.info("Đã đóng kết nối SQLite Database an toàn.")

    # ==========================
    # QUẢN LÝ GUILD SETTINGS
    # ==========================
    async def register_guild(self, guild_id: int):
        """Đăng ký server mới vào DB: Mặc định TẮT tất cả tính năng tự động (0)"""
        await self._db.execute("""
            INSERT INTO guild_settings (guild_id, automod_enabled, level_system_enabled)
            VALUES (?, 0, 0)
            ON CONFLICT(guild_id) DO NOTHING;
        """, (str(guild_id),))
        await self._db.commit()
        logger.info(f"Đã đăng ký server {guild_id} vào Database (Tính năng tự động: Mặc định TẮT).")

    async def get_guild_settings(self, guild_id: int) -> Dict[str, Any]:
        """Lấy toàn bộ thiết lập của một guild (Nếu chưa có trong DB, trả về mặc định TẮT)"""
        async with self._db.execute(
            "SELECT prefix, welcome_channel_id, music_channel_id, automod_enabled, level_system_enabled FROM guild_settings WHERE guild_id = ?",
            (str(guild_id),)
        ) as cursor:
            row = await cursor.fetchone()
            if row:
                return {
                    "prefix": row[0] or "!",
                    "welcome_channel_id": row[1],
                    "music_channel_id": row[2],
                    "automod_enabled": bool(row[3]),
                    "level_system_enabled": bool(row[4])
                }
            return {
                "prefix": "!",
                "welcome_channel_id": None,
                "music_channel_id": None,
                "automod_enabled": False,
                "level_system_enabled": False
            }

    async def update_guild_setting(self, guild_id: int, column: str, value: Any):
        """Cập nhật một trường cấu hình của server (Upsert)"""
        valid_columns = ("prefix", "welcome_channel_id", "music_channel_id", "automod_enabled", "level_system_enabled")
        if column not in valid_columns:
            raise ValueError(f"Cột {column} không hợp lệ!")

        await self._db.execute(f"""
            INSERT INTO guild_settings (guild_id, {column})
            VALUES (?, ?)
            ON CONFLICT(guild_id) DO UPDATE SET {column} = excluded.{column};
        """, (str(guild_id), value))
        await self._db.commit()

    # ==========================
    # HỆ THỐNG LEVEL / RANK
    # ==========================
    async def add_xp(self, guild_id: int, user_id: int, xp_to_add: int = 15, cooldown_seconds: float = 60.0) -> Tuple[bool, int, int]:
        """Cộng điểm kinh nghiệm cho người dùng (có cooldown chống spam)"""
        gid = str(guild_id)
        uid = str(user_id)
        now = time.time()

        async with self._db.execute(
            "SELECT xp, level, last_xp_time FROM user_levels WHERE guild_id = ? AND user_id = ?",
            (gid, uid)
        ) as cursor:
            row = await cursor.fetchone()

        if row:
            xp, level, last_xp_time = row
            if now - last_xp_time < cooldown_seconds:
                return False, xp, level

            new_xp = xp + xp_to_add
            needed_xp = int(100 * (level ** 1.5))
            leveled_up = False
            new_level = level

            if new_xp >= needed_xp:
                new_level += 1
                leveled_up = True

            await self._db.execute("""
                UPDATE user_levels 
                SET xp = ?, level = ?, last_xp_time = ?
                WHERE guild_id = ? AND user_id = ?;
            """, (new_xp, new_level, now, gid, uid))
            await self._db.commit()
            return leveled_up, new_xp, new_level
        else:
            await self._db.execute("""
                INSERT INTO user_levels (guild_id, user_id, xp, level, last_xp_time)
                VALUES (?, ?, ?, 1, ?);
            """, (gid, uid, xp_to_add, now))
            await self._db.commit()
            return False, xp_to_add, 1

    async def get_leaderboard(self, guild_id: int, limit: int = 10) -> List[Tuple[str, int, int]]:
        """Lấy bảng xếp hạng Level trong Guild với tốc độ siêu nhanh"""
        async with self._db.execute("""
            SELECT user_id, xp, level 
            FROM user_levels 
            WHERE guild_id = ? 
            ORDER BY xp DESC 
            LIMIT ?;
        """, (str(guild_id), limit)) as cursor:
            return await cursor.fetchall()

    # ==========================
    # NHẬT KÝ QUẢN TRỊ (MOD LOGS)
    # ==========================
    async def log_action(self, guild_id: int, user_id: int, action: str, reason: str = ""):
        """Ghi nhận hành vi kỷ luật thành viên vào SQLite"""
        await self._db.execute("""
            INSERT INTO mod_logs (guild_id, user_id, action, reason)
            VALUES (?, ?, ?, ?);
        """, (str(guild_id), str(user_id), action, reason))
        await self._db.commit()
