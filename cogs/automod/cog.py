import discord
from discord.ext import commands
import re
import time
import logging
from datetime import timedelta
from config import Config

logger = logging.getLogger("SosaBot.AutoMod")
LINK_REGEX = r"(http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+)"

class AutoMod(commands.Cog):
    """Module tự động quản trị: lọc từ cấm, link rác và chống spam chat"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.spam_control = {}

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return

        if message.author.guild_permissions.administrator:
            return

        content = message.content.lower()

        # 1. LỌC TỪ NGỮ CẤM
        if any(bad_word in content for bad_word in Config.BAD_WORDS):
            try:
                await message.delete()
                await message.channel.send(
                    f"⚠️ {message.author.mention}, bạn vi phạm quy tắc: Sử dụng từ ngữ cấm!",
                    delete_after=5
                )
                logger.info(f"[{message.guild.name}] Xóa tin nhắn chứa từ cấm từ {message.author}")
            except discord.Forbidden:
                logger.warning(f"[{message.guild.name}] Không đủ quyền xóa tin nhắn vi phạm từ cấm.")
            return

        # 2. LỌC LINK RÁC
        if re.search(LINK_REGEX, content):
            try:
                await message.delete()
                await message.channel.send(
                    f"🚫 {message.author.mention}, không được phép gửi link tại kênh này!",
                    delete_after=5
                )
                logger.info(f"[{message.guild.name}] Xóa tin nhắn chứa liên kết từ {message.author}")
            except discord.Forbidden:
                logger.warning(f"[{message.guild.name}] Không đủ quyền xóa tin nhắn chứa link.")
            return

        # 3. CHỐNG SPAM VÀ TỰ ĐỘNG TIMEOUT
        user_id = message.author.id
        current_time = time.time()

        if user_id not in self.spam_control:
            self.spam_control[user_id] = []

        self.spam_control[user_id].append(current_time)
        self.spam_control[user_id] = [
            t for t in self.spam_control[user_id]
            if current_time - t <= Config.SPAM_TIME
        ]

        if len(self.spam_control[user_id]) >= Config.SPAM_LIMIT:
            try:
                await message.delete()
            except discord.Forbidden:
                pass

            self.spam_control[user_id].clear()

            try:
                duration = timedelta(minutes=5)
                await message.author.timeout(duration, reason="Spam tin nhắn liên tục")
                await message.channel.send(
                    f"🛑 {message.author.mention} đã bị cấm chat 5 phút do spam!"
                )
                logger.info(f"[{message.guild.name}] Đã timeout {message.author} 5 phút do spam.")
            except discord.Forbidden:
                logger.warning(f"[{message.guild.name}] Bot thiếu quyền timeout thành viên: {message.author}")

async def setup(bot: commands.Bot):
    await bot.add_cog(AutoMod(bot))
