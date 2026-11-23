import asyncio
import logging
import os
from pathlib import Path
import discord
from discord.ext import commands
from config import Config
from utils.logger import setup_logging
from utils.database import DatabaseManager
from utils.error_handler import global_app_command_error

# Khởi tạo logger hệ thống
logger = setup_logging("SosaBot")

class SosaBot(commands.Bot):
    """Lớp Bot chính kế thừa commands.Bot với cơ chế tự động nạp cogs, SQLite và quản lý tài nguyên"""

    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(
            command_prefix=Config.COMMAND_PREFIX,
            intents=intents,
            help_command=None,
            owner_ids=set(Config.OWNER_IDS) if Config.OWNER_IDS else None
        )
        # Tích hợp DatabaseManager tập trung (Singleton Pattern)
        self.db = DatabaseManager(Config.DB_PATH)

    def clean_temp_directory(self):
        """Dọn dẹp sạch sẽ các file tạm (.mp3, .tmp) sót lại khi bot bị tắt đột ngột lần trước"""
        if Config.TEMP_DIR.exists():
            cleaned_count = 0
            for file in Config.TEMP_DIR.glob("*"):
                if file.is_file() and file.suffix in (".mp3", ".tmp"):
                    try:
                        file.unlink()
                        cleaned_count += 1
                    except OSError:
                        pass
            if cleaned_count > 0:
                logger.info(f"Đã dọn dẹp {cleaned_count} file rác trong thư mục temp/ khi khởi động.")

    async def setup_hook(self):
        """Khởi động cơ sở dữ liệu SQLite, dọn rác, gắn error handler và nạp cogs"""
        # 1. Khởi tạo cơ sở dữ liệu SQLite (WAL Mode)
        await self.db.initialize()

        # 2. Dọn dẹp thư mục tạm
        self.clean_temp_directory()

        # 3. Gắn bộ xử lý lỗi tập trung cho toàn bộ Slash Commands
        self.tree.on_error = global_app_command_error

        # 4. Quét và nạp tất cả cogs
        logger.info("Đang nạp các module cogs...")
        cogs_dir = Config.BASE_DIR / "cogs"

        if not cogs_dir.exists():
            logger.warning(f"Thư mục cogs không tồn tại tại: {cogs_dir}")
            return

        for item in sorted(cogs_dir.iterdir()):
            cog_module = None

            if item.is_dir() and not item.name.startswith((".", "_")):
                if (item / "__init__.py").exists():
                    cog_module = f"cogs.{item.name}"
                elif (item / "cog.py").exists():
                    cog_module = f"cogs.{item.name}.cog"

            elif item.is_file() and item.suffix == ".py":
                if item.stem != "__init__" and not item.stem.startswith(("_", ".")):
                    cog_module = f"cogs.{item.stem}"

            if cog_module:
                try:
                    await self.load_extension(cog_module)
                    logger.info(f"-> Nạp thành công module: {cog_module}")
                except Exception as e:
                    logger.error(f"-> Lỗi khi nạp {cog_module}: {e}", exc_info=True)

        # 5. Đồng bộ Slash Commands thông minh (Chống Rate Limit lúc restart)
        if Config.SYNC_ON_STARTUP:
            try:
                synced = await self.tree.sync()
                logger.info(f"Đã tự động đồng bộ {len(synced)} Slash Commands (SYNC_ON_STARTUP=True).")
            except Exception as e:
                logger.error(f"Lỗi khi đồng bộ Slash Commands: {e}", exc_info=True)
        else:
            logger.info("Đã bỏ qua tự động sync lúc khởi động để chống Rate Limit. Dùng lệnh '!sync' khi cần cập nhật lệnh.")

    async def on_ready(self):
        """Kích hoạt khi bot đã kết nối thành công với Discord"""
        logger.info(f"Bot {self.user} (ID: {self.user.id}) đã trực tuyến!")
        logger.info(f"Đang phục vụ {len(self.guilds)} server. Database: SQLite (aiosqlite).")
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.listening,
                name="/play | /speak | !sync"
            )
        )

    async def close(self):
        """Dọn dẹp và đóng an toàn database khi bot dừng hoạt động"""
        logger.info("Đang đóng các dịch vụ của bot...")
        await self.db.close()
        await super().close()


async def main():
    if not Config.DISCORD_TOKEN or Config.DISCORD_TOKEN == "your_bot_token_here":
        logger.critical(
            "CHƯA CẤU HÌNH DISCORD_TOKEN! "
            "Vui lòng mở file .env và điền Token Bot của bạn."
        )
        return

    bot = SosaBot()
    async with bot:
        await bot.start(Config.DISCORD_TOKEN)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot đã nhận lệnh dừng (KeyboardInterrupt). Đang thoát...")
