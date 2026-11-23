import os
import time
import asyncio
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
        # 1. Kiểm tra độ dài văn bản (Chống DoS / lạm dụng spam âm thanh)
        text = text.strip()
        if len(text) > Config.TTS_MAX_LENGTH:
            await interaction.response.send_message(
                f"❌ Nội dung quá dài ({len(text)}/{Config.TTS_MAX_LENGTH} ký tự). Vui lòng rút gọn lại!",
                ephemeral=True
            )
            return

        await interaction.response.defer()

        # 2. Kiểm tra trạng thái Voice của người dùng
        user = interaction.guild.get_member(interaction.user.id)
        if not user or not user.voice or not user.voice.channel:
            await interaction.followup.send("❌ Bạn phải tham gia một kênh thoại trước!")
            return

        vc = interaction.guild.voice_client
        # 3. Chống bắt cóc bot sang phòng khác khi đang có người nghe
        if vc and vc.channel != user.voice.channel:
            if len([m for m in vc.channel.members if not m.bot]) > 0:
                await interaction.followup.send(
                    f"❌ Bot đang phục vụ tại kênh thoại **{vc.channel.name}**! Vui lòng vào cùng phòng.",
                    ephemeral=True
                )
                return
            await vc.move_to(user.voice.channel)
        elif not vc:
            vc = await user.voice.channel.connect()

        # 4. Đồng bộ với MusicPlayer: Nếu đang phát nhạc, tạm lưu bài hát và phối hợp với Music loop
        music_cog = self.bot.get_cog("Music")
        player = None
        if music_cog and interaction.guild_id in music_cog.players:
            player = music_cog.players[interaction.guild_id]
            if vc.is_playing() and player.current_track:
                # Đưa lại bài hát hiện tại vào đầu queue để sau khi TTS nói xong sẽ tiếp tục phát
                player.queue.insert(0, player.current_track)
                player.is_interrupted_by_tts = True
                player.tts_finished.clear()
                vc.stop()
                await asyncio.sleep(0.2)  # Chờ Discord giải phóng audio source cũ

        timestamp = int(time.time() * 1000)
        filename = str(Config.TEMP_DIR / f"tts_{interaction.guild_id}_{timestamp}.mp3")

        try:
            # 5. Gọi Google API bất đồng bộ (chạy qua asyncio.to_thread để KHÔNG chặn Event Loop)
            def generate_tts():
                tts = gTTS(text=text, lang="vi")
                tts.save(filename)

            await asyncio.to_thread(generate_tts)

            # 6. Phát âm thanh qua FFmpeg và tự dọn dẹp
            source = discord.FFmpegPCMAudio(filename)

            def after_speaking(error):
                if error:
                    logger.error(f"Lỗi khi phát TTS: {error}")
                if os.path.exists(filename):
                    try:
                        os.remove(filename)
                    except OSError as e:
                        logger.warning(f"Không thể xóa file tạm {filename}: {e}")
                # Báo hiệu cho MusicPlayer là TTS đã nói xong
                if player:
                    self.bot.loop.call_soon_threadsafe(player.tts_finished.set)
                    self.bot.loop.call_soon_threadsafe(player.song_added.set)

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
            if player:
                player.tts_finished.set()

async def setup(bot: commands.Bot):
    await bot.add_cog(TTS(bot))
