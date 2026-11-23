import aiosqlite
from pathlib import Path
from typing import Any, List, Optional, Tuple, Dict
import logging
import time
from config import Config

logger = logging.getLogger("SosaGallery.Database")

# Định nghĩa các bậc nhẫn cưới (Ring Tiers) dựa trên điểm thân mật
RING_TIERS = {
    1: {"name": "Nhẫn Cỏ Thần Tiên 🌿", "min_points": 0, "color": 0x85E3B3, "desc": "Mộc mạc, ngọt ngào những ngày đầu mới về chung nhà."},
    2: {"name": "Nhẫn Bạc Thuần Khiết 🪙", "min_points": 50, "color": 0xC0C0C0, "desc": "Tình cảm bắt đầu gắn kết và thấu hiểu lẫn nhau."},
    3: {"name": "Nhẫn Vàng Vương Giả 👑", "min_points": 150, "color": 0xFFD700, "desc": "Tình yêu chín muồi, rực rỡ và bền chặt như kim loại quý."},
    4: {"name": "Nhẫn Kim Cương Vĩnh Cửu 💎", "min_points": 300, "color": 0x7DF9FF, "desc": "Tình cảm kiên cố, không bão giông nào có thể chia lìa."},
    5: {"name": "Nhẫn Vô Cực Ngân Hà 🌌", "min_points": 500, "color": 0xE0B0FF, "desc": "Tình yêu huyền thoại vượt qua thời gian và không gian!"}
}

def calculate_ring_tier(points: int) -> int:
    """Xác định cấp bậc nhẫn dựa trên điểm thân mật"""
    if points >= 500:
        return 5
    elif points >= 300:
        return 4
    elif points >= 150:
        return 3
    elif points >= 50:
        return 2
    return 1


class DatabaseManager:
    """
    Quản lý SQLite bất đồng bộ (aiosqlite) siêu nhẹ và tối ưu cho VPS:
    - Bật chế độ WAL (Write-Ahead Logging) cho phép đọc và ghi song song không nghẽn.
    - Hỗ trợ các bảng: cấu hình guild, level/rank, mod logs, kết hôn & nhà cặp đôi (marriages).
    """

    def __init__(self, db_path: Path):
        self.db_path = Path(db_path)
        self._db: Optional[aiosqlite.Connection] = None
        self._prefix_cache: Dict[str, str] = {}

    async def initialize(self):
        """Khởi tạo kết nối, bật chế độ WAL và tạo bảng tự động"""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._db = await aiosqlite.connect(self.db_path)

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

        # Migration an toàn
        try:
            await self._db.execute("ALTER TABLE guild_settings ADD COLUMN level_system_enabled INTEGER DEFAULT 0;")
        except Exception:
            pass

        # 2. Bảng Hệ thống Level / Rank
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

        # 4. Bảng Kết Hôn & Ngôi Nhà Cặp Đôi (Marry System)
        await self._db.execute("""
            CREATE TABLE IF NOT EXISTS marriages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id TEXT NOT NULL,
                user1_id TEXT NOT NULL,
                user2_id TEXT NOT NULL,
                house_name TEXT DEFAULT 'Ngôi Nhà Hạnh Phúc',
                quote TEXT DEFAULT 'Bên nhau trọn đời 💕',
                intimacy_points INTEGER DEFAULT 0,
                ring_tier INTEGER DEFAULT 1,
                married_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                gallery_slot_1 TEXT,
                gallery_slot_2 TEXT,
                gallery_slot_3 TEXT,
                gallery_slot_4 TEXT,
                gallery_slot_5 TEXT,
                gallery_slot_6 TEXT,
                background_url TEXT,
                last_interaction_time REAL DEFAULT 0
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

    async def get_guild_settings(self, guild_id: int) -> Dict[str, Any]:
        """Lấy toàn bộ thiết lập của một guild"""
        async with self._db.execute(
            "SELECT prefix, welcome_channel_id, music_channel_id, automod_enabled, level_system_enabled FROM guild_settings WHERE guild_id = ?",
            (str(guild_id),)
        ) as cursor:
            row = await cursor.fetchone()
            if row:
                return {
                    "prefix": row[0] or Config.COMMAND_PREFIX,
                    "welcome_channel_id": row[1],
                    "music_channel_id": row[2],
                    "automod_enabled": bool(row[3]),
                    "level_system_enabled": bool(row[4])
                }
            return {
                "prefix": Config.COMMAND_PREFIX,
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
        if column == "prefix":
            self._prefix_cache[str(guild_id)] = str(value)

    async def get_prefix(self, guild_id: int) -> str:
        """Lấy tiền tố lệnh (prefix) của một server (sử dụng in-memory cache)"""
        gid = str(guild_id)
        if gid in self._prefix_cache:
            return self._prefix_cache[gid]

        async with self._db.execute(
            "SELECT prefix FROM guild_settings WHERE guild_id = ?",
            (gid,)
        ) as cursor:
            row = await cursor.fetchone()
            prefix = row[0] if (row and row[0]) else Config.COMMAND_PREFIX
            self._prefix_cache[gid] = prefix
            return prefix

    async def set_prefix(self, guild_id: int, new_prefix: str):
        """Thay đổi tiền tố lệnh của server"""
        await self.update_guild_setting(guild_id, "prefix", new_prefix)

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

    async def get_user_rank(self, guild_id: int, user_id: int) -> Tuple[int, int, int]:
        """Lấy thứ hạng (rank), XP và level của người dùng trong server"""
        gid = str(guild_id)
        uid = str(user_id)

        # Lấy thông tin XP của user
        async with self._db.execute(
            "SELECT xp, level FROM user_levels WHERE guild_id = ? AND user_id = ?",
            (gid, uid)
        ) as cursor:
            row = await cursor.fetchone()

        if not row:
            return 1, 0, 1

        xp, level = row
        # Tính số người có XP cao hơn user này
        async with self._db.execute(
            "SELECT COUNT(*) FROM user_levels WHERE guild_id = ? AND xp > ?",
            (gid, xp)
        ) as cursor:
            rank_above = (await cursor.fetchone())[0]

        return rank_above + 1, xp, level

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
    # HỆ THỐNG KẾT HÔN & NHÀ CẶP ĐÔI (MARRY)
    # ==========================
    async def get_marriage(self, guild_id: int, user_id: int) -> Optional[Dict[str, Any]]:
        """Lấy thông tin hôn nhân của một người dùng trong Server"""
        gid = str(guild_id)
        uid = str(user_id)

        async with self._db.execute("""
            SELECT id, user1_id, user2_id, house_name, quote, intimacy_points, ring_tier, 
                   married_at, gallery_slot_1, gallery_slot_2, gallery_slot_3, 
                   gallery_slot_4, gallery_slot_5, gallery_slot_6, background_url, last_interaction_time
            FROM marriages
            WHERE guild_id = ? AND (user1_id = ? OR user2_id = ?)
        """, (gid, uid, uid)) as cursor:
            row = await cursor.fetchone()

        if not row:
            return None

        return {
            "id": row[0],
            "user1_id": row[1],
            "user2_id": row[2],
            "partner_id": row[2] if row[1] == uid else row[1],
            "house_name": row[3] or "Ngôi Nhà Hạnh Phúc",
            "quote": row[4] or "Bên nhau trọn đời 💕",
            "intimacy_points": row[5] or 0,
            "ring_tier": row[6] or 1,
            "married_at": row[7],
            "gallery": [row[8], row[9], row[10], row[11], row[12], row[13]],
            "background_url": row[14],
            "last_interaction_time": row[15] or 0
        }

    async def create_marriage(self, guild_id: int, user1_id: int, user2_id: int) -> bool:
        """Tạo mối quan hệ hôn nhân mới giữa 2 người dùng"""
        gid = str(guild_id)
        u1 = str(user1_id)
        u2 = str(user2_id)

        # Kiểm tra xem một trong hai người đã cưới ai khác trong server chưa
        existing1 = await self.get_marriage(guild_id, user1_id)
        existing2 = await self.get_marriage(guild_id, user2_id)
        if existing1 or existing2:
            return False

        await self._db.execute("""
            INSERT INTO marriages (guild_id, user1_id, user2_id, ring_tier, intimacy_points)
            VALUES (?, ?, ?, 1, 0);
        """, (gid, u1, u2))
        await self._db.commit()
        return True

    async def update_house_name(self, guild_id: int, user_id: int, new_name: str) -> bool:
        """Đổi tên ngôi nhà marry"""
        marriage = await self.get_marriage(guild_id, user_id)
        if not marriage:
            return False

        await self._db.execute(
            "UPDATE marriages SET house_name = ? WHERE id = ?",
            (new_name, marriage["id"])
        )
        await self._db.commit()
        return True

    async def update_house_quote(self, guild_id: int, user_id: int, new_quote: str) -> bool:
        """Đổi câu trích dẫn/châm ngôn của ngôi nhà marry"""
        marriage = await self.get_marriage(guild_id, user_id)
        if not marriage:
            return False

        await self._db.execute(
            "UPDATE marriages SET quote = ? WHERE id = ?",
            (new_quote, marriage["id"])
        )
        await self._db.commit()
        return True

    async def update_gallery_slot(self, guild_id: int, user_id: int, slot: int, url: str) -> bool:
        """Cập nhật ảnh vào 1 trong 6 vị trí của thư viện (slot 1-6)"""
        if slot < 1 or slot > 6:
            return False

        marriage = await self.get_marriage(guild_id, user_id)
        if not marriage:
            return False

        col_name = f"gallery_slot_{slot}"
        await self._db.execute(
            f"UPDATE marriages SET {col_name} = ? WHERE id = ?",
            (url, marriage["id"])
        )
        await self._db.commit()
        return True

    async def update_house_background(self, guild_id: int, user_id: int, background_url: str) -> bool:
        """Cập nhật ảnh nền cho thư viện ảnh"""
        marriage = await self.get_marriage(guild_id, user_id)
        if not marriage:
            return False

        await self._db.execute(
            "UPDATE marriages SET background_url = ? WHERE id = ?",
            (background_url, marriage["id"])
        )
        await self._db.commit()
        return True

    async def add_intimacy(self, guild_id: int, user_id: int, points: int = 10, cooldown_seconds: float = 30.0) -> Tuple[bool, int, int, bool]:
        """
        Cộng điểm thân mật khi tương tác với người bạn đời (kiss, hug, pat, slap).
        Trả về: (success, new_points, ring_tier, tier_up)
        """
        marriage = await self.get_marriage(guild_id, user_id)
        if not marriage:
            return False, 0, 1, False

        now = time.time()
        last_time = marriage["last_interaction_time"]

        if now - last_time < cooldown_seconds:
            return False, marriage["intimacy_points"], marriage["ring_tier"], False

        old_tier = marriage["ring_tier"]
        new_points = marriage["intimacy_points"] + points
        new_tier = calculate_ring_tier(new_points)
        tier_up = new_tier > old_tier

        await self._db.execute("""
            UPDATE marriages 
            SET intimacy_points = ?, ring_tier = ?, last_interaction_time = ?
            WHERE id = ?;
        """, (new_points, new_tier, now, marriage["id"]))
        await self._db.commit()

        return True, new_points, new_tier, tier_up

    async def divorce(self, guild_id: int, user_id: int) -> bool:
        """Hủy bỏ mối quan hệ hôn nhân (Ly hôn)"""
        marriage = await self.get_marriage(guild_id, user_id)
        if not marriage:
            return False

        await self._db.execute("DELETE FROM marriages WHERE id = ?", (marriage["id"],))
        await self._db.commit()
        return True

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
