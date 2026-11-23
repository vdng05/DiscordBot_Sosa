import os
import time
import logging
import discord
from discord.ext import commands
from discord import app_commands
from gtts import gTTS
from config import Config

logger = logging.getLogger("SosaBot.TTS")

class TTS(commands.Cog):
    """Module chuyển đổi văn bản thành giọng nói tiếng Việt trong Voice Channel"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="speak",
        description="Đọc văn bản thành giọng nói trong kênh thoại (Dành cho người không mic)"
    )
    @app_commands.describe(text="Nội dung văn bản bạn muốn bot đọc")
    async def say(self, interaction: discord.Interaction, text: str):
        await interaction.response.defer()

        user = interaction.guild.get_member(interaction.user.id)
        if not user or not user.voice or not user.voice.channel:
            await interaction.followup.send("❌ Bạn phải tham gia một kênh thoại trước!")
            return

        vc = interaction.guild.voice_client
        if not vc:
            vc = await user.voice.channel.connect()
        elif vc.channel != user.voice.channel:
            await vc.move_to(user.voice.channel)

        if vc.is_playing():
            vc.stop()

        timestamp = int(time.time() * 1000)
        filename = str(Config.TEMP_DIR / f"tts_{interaction.guild_id}_{timestamp}.mp3")

        try:
            tts = gTTS(text=text, lang="vi")
            tts.save(filename)

            source = discord.FFmpegPCMAudio(filename)

            def after_speaking(error):
                if error:
                    logger.error(f"Lỗi khi phát TTS: {error}")
                if os.path.exists(filename):
                    try:
                        os.remove(filename)
                    except OSError as e:
                        logger.warning(f"Không thể xóa file tạm {filename}: {e}")

            vc.play(source, after=after_speaking)
            await interaction.followup.send(f"🗣️ **{interaction.user.display_name}**: {text}")
            logger.info(f"[{interaction.guild.name}] {interaction.user.display_name} TTS: {text[:40]}")

        except Exception as e:
            logger.error(f"Lỗi xử lý giọng nói TTS: {e}", exc_info=True)
            await interaction.followup.send(f"❌ Lỗi xử lý giọng nói: {e}")
            if os.path.exists(filename):
                try:
                    os.remove(filename)
                except OSError:
                    pass

async def setup(bot: commands.Bot):
    await bot.add_cog(TTS(bot))
