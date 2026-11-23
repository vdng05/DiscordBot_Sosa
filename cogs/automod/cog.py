import discord
from discord.ext import commands
import re
import time
import logging
from datetime import timedelta
from config import Config

logger = logging.getLogger("SosaBot.AutoMod")
LINK_REGEX = r"(http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+)"

# Các nền tảng âm thanh/video giải trí được phép gửi trong kênh nhạc/media
MEDIA_DOMAINS = ("youtube.com", "youtu.be", "soundcloud.com", "spotify.com")
MEDIA_CHANNEL_KEYWORDS = ("nhac", "music", "media", "video", "share", "gọi-bot-nhạc")

class AutoMod(commands.Cog):
    """Module tự động quản trị: lọc từ cấm, link rác, chống spam và hỗ trợ Whitelist"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.spam_control = {}

    def is_exempt(self, member: discord.Member) -> bool:
        """Kiểm tra thành viên có thuộc diện miễn trừ không (Admin, Quản lý)"""
        if member.guild_permissions.administrator:
            return True
        if member.guild_permissions.manage_guild or member.guild_permissions.manage_messages:
            return True
        return False

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return

        # 1. Bỏ qua nếu là Ban Quản Trị
        if self.is_exempt(message.author):
            return

        # 2. Kiểm tra xem Guild có bật AutoMod trong SQLite hay không
        try:
            guild_settings = await self.bot.db.get_guild_settings(message.guild.id)
            if not guild_settings.get("automod_enabled", True):
                return
        except Exception:
            pass

        content = message.content.lower()
        channel_name = message.channel.name.lower()

        # 3. LỌC TỪ NGỮ CẤM
        if any(bad_word in content for bad_word in Config.BAD_WORDS):
            try:
                await message.delete()
                await message.channel.send(
                    f"⚠️ {message.author.mention}, bạn vi phạm quy tắc: Sử dụng từ ngữ cấm!",
                    delete_after=5
                )
                logger.info(f"[{message.guild.name}] Xóa tin nhắn chứa từ cấm từ {message.author}")
                await self.bot.db.log_action(message.guild.id, message.author.id, "DELETE_BAD_WORD", "Dùng từ cấm")
            except (discord.NotFound, discord.Forbidden, discord.HTTPException) as e:
                logger.warning(f"[{message.guild.name}] Không thể xóa tin nhắn vi phạm từ cấm: {e}")
            return

        # 4. LỌC LINK RÁC CÓ WHITELIST
        link_match = re.search(LINK_REGEX, content)
        if link_match:
            found_url = link_match.group(0).lower()
            # Kiểm tra xem kênh có phải kênh nhạc/media và link có hợp lệ không
            is_media_channel = any(kw in channel_name for kw in MEDIA_CHANNEL_KEYWORDS)
            is_media_url = any(domain in found_url for domain in MEDIA_DOMAINS)

            # Nếu là link nhạc gửi ở kênh nhạc -> Cho phép (Whitelist)
            if not (is_media_channel and is_media_url):
                try:
                    await message.delete()
                    await message.channel.send(
                        f"🚫 {message.author.mention}, không được phép gửi link tại kênh này!",
                        delete_after=5
                    )
                    logger.info(f"[{message.guild.name}] Xóa tin nhắn chứa liên kết ngoài từ {message.author}")
                    await self.bot.db.log_action(message.guild.id, message.author.id, "DELETE_LINK", found_url[:100])
                except (discord.NotFound, discord.Forbidden, discord.HTTPException) as e:
                    logger.warning(f"[{message.guild.name}] Không thể xóa tin nhắn chứa link: {e}")
                return

        # 5. CHỐNG SPAM VÀ TỰ ĐỘNG TIMEOUT (Có dọn dẹp bộ nhớ)
        user_id = message.author.id
        current_time = time.time()

        if user_id not in self.spam_control:
            self.spam_control[user_id] = []

        self.spam_control[user_id].append(current_time)
        self.spam_control[user_id] = [
            t for t in self.spam_control[user_id]
            if current_time - t <= Config.SPAM_TIME
        ]

        if not self.spam_control[user_id]:
            del self.spam_control[user_id]
            return

        if len(self.spam_control[user_id]) >= Config.SPAM_LIMIT:
            try:
                await message.delete()
            except (discord.NotFound, discord.Forbidden, discord.HTTPException):
                pass

            del self.spam_control[user_id]

            try:
                duration = timedelta(minutes=5)
                await message.author.timeout(duration, reason="Spam tin nhắn liên tục")
                await message.channel.send(
                    f"🛑 {message.author.mention} đã bị cấm chat 5 phút do spam!"
                )
                logger.info(f"[{message.guild.name}] Đã timeout {message.author} 5 phút do spam.")
                await self.bot.db.log_action(message.guild.id, message.author.id, "TIMEOUT_SPAM", "Spam tin nhắn")
            except (discord.Forbidden, discord.HTTPException) as e:
                logger.warning(f"[{message.guild.name}] Không thể timeout {message.author}: {e}")

        # 6. TÍCH HỢP HỆ THỐNG LEVEL / RANK (Cộng XP khi chat hợp lệ)
        try:
            leveled_up, new_xp, new_level = await self.bot.db.add_xp(message.guild.id, message.author.id)
            if leveled_up:
                await message.channel.send(
                    f"🎉 Chúc mừng {message.author.mention} đã thăng lên **Cấp {new_level}**! ⭐",
                    delete_after=10
                )
        except Exception as e:
            logger.error(f"Lỗi khi cộng điểm XP: {e}")

async def setup(bot: commands.Bot):
    await bot.add_cog(AutoMod(bot))
