import asyncio
import logging
import discord
import yt_dlp
from .sources import YTDL_STREAM_OPTIONS, FFMPEG_OPTIONS

logger = logging.getLogger("SosaBot.Music.Player")

class MusicPlayer:
    """Quản lý hàng đợi và tác vụ phát nhạc độc lập theo từng Server (Guild)"""

    def __init__(self, ctx: discord.Interaction):
        self.bot = ctx.client
        self.guild = ctx.guild
        self.queue = []

        self.song_added = asyncio.Event()
        self.song_finished = asyncio.Event()

        self.audio_player_task = self.bot.loop.create_task(self.audio_player_loop())
        self.current_track = None

    async def audio_player_loop(self):
        await self.bot.wait_until_ready()

        while not self.bot.is_closed():
            if not self.queue:
                self.song_added.clear()
                try:
                    # Chờ tối đa 5 phút nếu không có bài hát mới thì tự động rời kênh thoại
                    await asyncio.wait_for(self.song_added.wait(), timeout=300)
                except asyncio.TimeoutError:
                    if self.guild.voice_client:
                        await self.guild.voice_client.disconnect()

                    self.queue.clear()
                    cog = self.bot.get_cog('Music')
                    if cog and self.guild.id in cog.players:
                        del cog.players[self.guild.id]
                    logger.info(f"[{self.guild.name}] Tự động rời phòng thoại sau 5 phút không có bài mới.")
                    return

            if not self.queue:
                continue

            self.current_track = self.queue.pop(0)

            loop = self.bot.loop or asyncio.get_event_loop()
            stream_url = None

            with yt_dlp.YoutubeDL(YTDL_STREAM_OPTIONS) as ytdl:
                try:
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

            if stream_url:
                self.song_finished.clear()
                try:
                    source = discord.FFmpegPCMAudio(stream_url, **FFMPEG_OPTIONS)

                    def after_play(error):
                        if error:
                            logger.error(f"[{self.guild.name}] Lỗi playback: {error}")
                        self.bot.loop.call_soon_threadsafe(self.song_finished.set)

                    self.guild.voice_client.play(source, after=after_play)
                    await self.song_finished.wait()
                except Exception as e:
                    logger.error(f"[{self.guild.name}] Lỗi phát nhạc qua FFmpeg: {e}")
            else:
                continue
