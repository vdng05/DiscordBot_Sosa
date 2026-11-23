import asyncio
import logging
import discord
import yt_dlp
from .sources import YTDL_STREAM_OPTIONS, FFMPEG_OPTIONS

logger = logging.getLogger("SosaBot.Music.Player")

class MusicPlayer:
    """Quản lý hàng đợi và tác vụ phát nhạc độc lập theo từng Server (Guild)"""

    def __init__(self, bot_or_ctx, guild: discord.Guild = None):
        if guild is not None:
            self.bot = bot_or_ctx
            self.guild = guild
        elif hasattr(bot_or_ctx, 'client'):
            self.bot = bot_or_ctx.client
            self.guild = bot_or_ctx.guild
        else:
            self.bot = bot_or_ctx.bot
            self.guild = bot_or_ctx.guild
        self.queue = []

        self.song_added = asyncio.Event()
        self.song_finished = asyncio.Event()

        # Cờ và sự kiện đồng bộ khi TTS xen ngang
        self.is_interrupted_by_tts = False
        self.tts_finished = asyncio.Event()
        self.tts_finished.set()

        self.audio_player_task = self.bot.loop.create_task(self.audio_player_loop())
        self.current_track = None

    async def audio_player_loop(self):
        await self.bot.wait_until_ready()

        while not self.bot.is_closed():
            # 1. Chờ bài hát mới nếu hàng đợi trống
            if not self.queue:
                self.song_added.clear()
                try:
                    await asyncio.wait_for(self.song_added.wait(), timeout=300)
                except asyncio.TimeoutError:
                    if self.guild.voice_client:
                        try:
                            await self.guild.voice_client.disconnect()
                        except Exception:
                            pass

                    self.queue.clear()
                    cog = self.bot.get_cog('Music')
                    if cog and self.guild.id in cog.players:
                        del cog.players[self.guild.id]
                    logger.info(f"[{self.guild.name}] Tự động rời phòng thoại sau 5 phút không có bài mới.")
                    return

            if not self.queue:
                continue

            # 2. Nếu TTS đang nói, chờ cho đến khi TTS nói xong
            if self.is_interrupted_by_tts:
                await self.tts_finished.wait()
                self.is_interrupted_by_tts = False

            # 3. Lấy bài hát tiếp theo
            self.current_track = self.queue.pop(0)

            # 4. Trích xuất Stream Audio an toàn
            stream_url = None
            try:
                loop = asyncio.get_running_loop()
                with yt_dlp.YoutubeDL(YTDL_STREAM_OPTIONS) as ytdl:
                    data = await loop.run_in_executor(
                        None,
                        lambda: ytdl.extract_info(self.current_track['url'], download=False)
                    )
                    if data:
                        if 'entries' in data and data['entries']:
                            data = data['entries'][0]
                        stream_url = data.get('url')
            except Exception as e:
                logger.error(f"[{self.guild.name}] Lỗi trích xuất stream nhạc: {e}")

            # 5. Kiểm tra Voice Client trước khi gọi play (chống AttributeError: NoneType)
            vc = self.guild.voice_client
            if not vc or not vc.is_connected():
                logger.warning(f"[{self.guild.name}] Voice client đã ngắt kết nối trước khi phát nhạc.")
                return

            if stream_url:
                self.song_finished.clear()
                try:
                    source = discord.FFmpegPCMAudio(stream_url, **FFMPEG_OPTIONS)

                    def after_play(error):
                        if error:
                            logger.error(f"[{self.guild.name}] Lỗi playback: {error}")
                        self.bot.loop.call_soon_threadsafe(self.song_finished.set)

                    vc.play(source, after=after_play)
                    await self.song_finished.wait()

                    # 6. Nếu bị ngắt bởi TTS, đợi TTS đọc xong để tiếp tục
                    if self.is_interrupted_by_tts:
                        await self.tts_finished.wait()
                        self.is_interrupted_by_tts = False

                except discord.ClientException as e:
                    logger.warning(f"[{self.guild.name}] Voice client bận (có thể do TTS): {e}")
                    await asyncio.sleep(1)
                except Exception as e:
                    logger.error(f"[{self.guild.name}] Lỗi phát nhạc qua FFmpeg: {e}")
            else:
                # Tránh lặp vô hạn (tight loop) nếu URL lỗi liên tục
                await asyncio.sleep(0.5)
