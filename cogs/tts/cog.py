import os
import time
import asyncio
import logging
import discord
from discord.ext import commands
from discord import app_commands
from gtts import gTTS
from config import Config

logger = logging.getLogger("SosaGallery.TTS")

class TTS(commands.Cog):
    """Module chuyển đổi văn bản thành giọng nói tiếng Việt trong Voice Channel"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def _execute_say(self, ctx_or_interaction, text: str):
        is_interaction = isinstance(ctx_or_interaction, discord.Interaction)
        guild = ctx_or_interaction.guild
        author = ctx_or_interaction.user if is_interaction else ctx_or_interaction.author

        # 1. Kiểm tra độ dài văn bản
        text = text.strip()
        if not text:
            msg = "❌ Vui lòng nhập nội dung cần đọc!"
            if is_interaction:
                await ctx_or_interaction.response.send_message(msg, ephemeral=True)
            else:
                await ctx_or_interaction.reply(msg, mention_author=False)
            return

        if len(text) > Config.TTS_MAX_LENGTH:
            msg = f"❌ Nội dung quá dài ({len(text)}/{Config.TTS_MAX_LENGTH} ký tự). Vui lòng rút gọn lại!"
            if is_interaction:
                await ctx_or_interaction.response.send_message(msg, ephemeral=True)
            else:
                await ctx_or_interaction.reply(msg, mention_author=False)
            return

        if is_interaction:
            await ctx_or_interaction.response.defer()

        # 2. Kiểm tra trạng thái Voice của người dùng
        user = guild.get_member(author.id)
        if not user or not user.voice or not user.voice.channel:
            msg = "❌ Bạn phải tham gia vào một kênh thoại trước khi gọi bot nói!"
            if is_interaction:
                await ctx_or_interaction.followup.send(msg)
            else:
                await ctx_or_interaction.reply(msg, mention_author=False)
            return

        vc = guild.voice_client
        if vc and vc.channel != user.voice.channel:
            if len([m for m in vc.channel.members if not m.bot]) > 0:
                msg = f"❌ Bot đang phục vụ tại kênh thoại **{vc.channel.name}**! Vui lòng vào cùng phòng nhé."
                if is_interaction:
                    await ctx_or_interaction.followup.send(msg, ephemeral=True)
                else:
                    await ctx_or_interaction.reply(msg, mention_author=False)
                return
            await vc.move_to(user.voice.channel)
        elif not vc:
            vc = await user.voice.channel.connect()

        # 3. Đồng bộ với MusicPlayer: tạm dừng nhạc để đọc giọng nói
        music_cog = self.bot.get_cog("Music")
        player = None
        if music_cog and guild.id in music_cog.players:
            player = music_cog.players[guild.id]
            if vc.is_playing() and player.current_track:
                player.queue.insert(0, player.current_track)
                player.is_interrupted_by_tts = True
                player.tts_finished.clear()
                vc.stop()
                await asyncio.sleep(0.2)

        timestamp = int(time.time() * 1000)
        filename = str(Config.TEMP_DIR / f"tts_{guild.id}_{timestamp}.mp3")

        try:
            def generate_tts():
                tts = gTTS(text=text, lang="vi")
                tts.save(filename)

            await asyncio.to_thread(generate_tts)

            source = discord.FFmpegPCMAudio(filename)

            def after_speaking(error):
                if error:
                    logger.error(f"Lỗi khi phát TTS: {error}")
                if os.path.exists(filename):
                    try:
                        os.remove(filename)
                    except OSError:
                        pass
                if player:
                    self.bot.loop.call_soon_threadsafe(player.tts_finished.set)
                    self.bot.loop.call_soon_threadsafe(player.song_added.set)

            vc.play(source, after=after_speaking)

            reply_text = f"🗣️ **{author.display_name}**: {text}"
            if is_interaction:
                await ctx_or_interaction.followup.send(reply_text)
            else:
                await ctx_or_interaction.reply(reply_text, mention_author=False)
            logger.info(f"[{guild.name}] {author.display_name} TTS: {text[:40]}")

        except Exception as e:
            logger.error(f"Lỗi xử lý giọng nói TTS: {e}", exc_info=True)
            err_msg = f"❌ Lỗi xử lý giọng nói: {e}"
            if is_interaction:
                await ctx_or_interaction.followup.send(err_msg)
            else:
                await ctx_or_interaction.reply(err_msg, mention_author=False)
            if os.path.exists(filename):
                try:
                    os.remove(filename)
                except OSError:
                    pass
            if player:
                player.tts_finished.set()

    @app_commands.command(
        name="say",
        description="Đọc văn bản tiếng Việt thành giọng nói trong kênh thoại (Dành cho người không có mic)"
    )
    @app_commands.describe(text="Nhập nội dung văn bản tiếng Việt bạn muốn bot nói (Tối đa 300 ký tự)")
    async def say_slash(self, interaction: discord.Interaction, text: str):
        await self._execute_say(interaction, text)

    @app_commands.command(
        name="speak",
        description="Đọc văn bản tiếng Việt thành giọng nói trong kênh thoại (Lệnh tương đương /say)"
    )
    @app_commands.describe(text="Nhập nội dung văn bản tiếng Việt bạn muốn bot nói (Tối đa 300 ký tự)")
    async def speak_slash(self, interaction: discord.Interaction, text: str):
        await self._execute_say(interaction, text)

    @commands.command(name="say", aliases=["speak"], description="Đọc văn bản tiếng Việt thành giọng nói (!say <nội dung>)")
    async def say_prefix(self, ctx: commands.Context, *, text: str):
        await self._execute_say(ctx, text)

async def setup(bot: commands.Bot):
    await bot.add_cog(TTS(bot))
