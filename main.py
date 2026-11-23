import asyncio
import logging
from pathlib import Path
import discord
from discord.ext import commands
from config import Config
from utils.logger import setup_logging

# Khởi tạo logger hệ thống
logger = setup_logging("SosaBot")

class SosaBot(commands.Bot):
    """Lớp Bot chính kế thừa commands.Bot với cơ chế tự động nạp cogs dạng thư mục hoặc file đơn"""

    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(
            command_prefix=Config.COMMAND_PREFIX,
            intents=intents,
            help_command=None
        )

    async def setup_hook(self):
        """Tự động quét và nạp tất cả cogs (hỗ trợ cả dạng folder và file đơn)"""
        logger.info("Đang nạp các cogs...")
        cogs_dir = Config.BASE_DIR / "cogs"

        if not cogs_dir.exists():
            logger.warning(f"Thư mục cogs không tồn tại tại: {cogs_dir}")
            return

        # Quét các thư mục con trong cogs/ (ví dụ: cogs/music, cogs/tts...)
        for item in sorted(cogs_dir.iterdir()):
            cog_module = None

            # 1. Nếu là thư mục tính năng có file __init__.py (hoặc cog.py)
            if item.is_dir() and not item.name.startswith((".", "_")):
                if (item / "__init__.py").exists():
                    cog_module = f"cogs.{item.name}"
                elif (item / "cog.py").exists():
                    cog_module = f"cogs.{item.name}.cog"

            # 2. Nếu là file Python đơn lẻ (ví dụ: cogs/example.py)
            elif item.is_file() and item.suffix == ".py":
                if item.stem != "__init__" and not item.stem.startswith(("_", ".")):
                    cog_module = f"cogs.{item.stem}"

            if cog_module:
                try:
                    await self.load_extension(cog_module)
                    logger.info(f"-> Nạp thành công module: {cog_module}")
                except Exception as e:
                    logger.error(f"-> Lỗi khi nạp {cog_module}: {e}", exc_info=True)

        # Đồng bộ Slash Commands với Discord API
        try:
            synced = await self.tree.sync()
            logger.info(f"Đã đồng bộ {len(synced)} lệnh Slash Commands thành công.")
        except Exception as e:
            logger.error(f"Lỗi khi đồng bộ Slash Commands: {e}", exc_info=True)

    async def on_ready(self):
        """Kích hoạt khi bot đã kết nối thành công với Discord"""
        logger.info(f"Bot {self.user} (ID: {self.user.id}) đã trực tuyến!")
        logger.info(f"Đang phục vụ {len(self.guilds)} server.")
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.listening,
                name="/play | /speak"
            )
        )


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
