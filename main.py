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
logger = setup_logging("SosaGallery")

async def get_prefix(bot: commands.Bot, message: discord.Message):
    """Xác định tiền tố lệnh động theo từng server từ SQLite Database"""
    if not message.guild:
        return Config.COMMAND_PREFIX
    prefix = await bot.db.get_prefix(message.guild.id)
    return commands.when_mentioned_or(prefix)(bot, message)

class SosaBot(commands.Bot):
    """Lớp Bot chính kế thừa commands.Bot với cơ chế tự động nạp cogs, SQLite và quản lý tài nguyên"""

    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(
            command_prefix=get_prefix,
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
                name="SosaGallery | !help | /help"
            )
        )

    async def on_guild_join(self, guild: discord.Guild):
        """Kích hoạt khi bot được mời vào server mới: Tự động đăng ký với trạng thái TẮT TẤT CẢ TÍNH NĂNG TỰ ĐỘNG"""
        logger.info(f"Bot vừa tham gia Server mới: {guild.name} (ID: {guild.id}) - Thành viên: {guild.member_count}")
        await self.db.register_guild(guild.id)

        target_channel = guild.system_channel
        if not target_channel:
            target_channel = next((ch for ch in guild.text_channels if ch.permissions_for(guild.me).send_messages), None)

        if target_channel:
            embed = discord.Embed(
                title="👋 CẢM ƠN BẠN ĐÃ MỜI SOSAGALLERY VÀO SERVER!",
                description=(
                    f"Xin chào **{guild.name}**! Mình là **SosaGallery** — bot âm nhạc, giải trí và kết nối bạn bè.\n\n"
                    "🛡️ **Mặc định tính năng:** Để không làm phiền server, các tính năng tự động (chặn từ cấm, tính điểm level) đều đang tắt.\n\n"
                    "👉 **Một số lệnh cơ bản để bạn làm quen:**\n"
                    "• `/help` hoặc `!help`: Xem toàn bộ hướng dẫn sử dụng.\n"
                    "• `/play <tên bài>` hoặc `!play <tên bài>`: Phát nhạc từ YouTube, Spotify (có các nút bấm tiện lợi).\n"
                    "• `/say <nội dung>` hoặc `!say <nội dung>`: Nhờ bot đọc tiếng Việt trong phòng voice.\n"
                    "• `/settings`: Dành cho Quản trị viên để bật tính năng tự động hoặc đổi prefix gọi lệnh."
                ),
                color=discord.Color.green()
            )
            embed.set_footer(text="SosaPy • Cấu hình đã được lưu an toàn trên SQLite")
            try:
                await target_channel.send(embed=embed)
            except discord.HTTPException:
                pass

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
