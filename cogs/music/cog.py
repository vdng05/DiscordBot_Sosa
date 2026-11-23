import discord
from discord.ext import commands
from discord import app_commands
import yt_dlp
import asyncio
import logging
from .sources import YTDL_SEARCH_OPTIONS, get_clean_url, get_title, resolve_spotify_link
from .player import MusicPlayer

logger = logging.getLogger("SosaBot.Music")

class Music(commands.Cog):
    """Module phát nhạc hỗ trợ YouTube, SoundCloud, Spotify và từ khóa tìm kiếm"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.players = {}

    def get_player(self, interaction: discord.Interaction) -> MusicPlayer:
        guild_id = interaction.guild_id
        if guild_id not in self.players:
            self.players[guild_id] = MusicPlayer(interaction)
        return self.players[guild_id]

    @app_commands.command(name="play", description="Phát nhạc từ YouTube, SoundCloud, Spotify hoặc Từ khóa")
    @app_commands.describe(query="Link bài hát hoặc từ khóa tìm kiếm")
    async def play(self, interaction: discord.Interaction, query: str):
        await interaction.response.defer()

        user = interaction.guild.get_member(interaction.user.id)
        if not user or not user.voice or not user.voice.channel:
            await interaction.followup.send("❌ Bạn phải tham gia một kênh thoại trước!")
            return

        vc = interaction.guild.voice_client
        # Chống bắt cóc bot: Nếu bot đang ở phòng khác có người nghe, yêu cầu vào cùng phòng
        if vc and vc.channel != user.voice.channel:
            if len([m for m in vc.channel.members if not m.bot]) > 0:
                await interaction.followup.send(
                    f"❌ Bot đang phát nhạc tại kênh thoại **{vc.channel.name}**! "
                    "Vui lòng tham gia cùng phòng hoặc đợi bài hát kết thúc.",
                    ephemeral=True
                )
                return
            await vc.move_to(user.voice.channel)
        elif not vc:
            vc = await user.voice.channel.connect()

        # Giải quyết link Spotify không gây nghẽn Event Loop (chạy qua asyncio.to_thread)
        if "spotify.com" in query:
            spotify_query = await asyncio.to_thread(resolve_spotify_link, query)
            if spotify_query:
                query = spotify_query
            else:
                await interaction.followup.send("❌ Không thể đọc link Spotify này. Hãy thử gõ tên bài hát!")
                return

        player = self.get_player(interaction)
        loop = asyncio.get_running_loop()

        with yt_dlp.YoutubeDL(YTDL_SEARCH_OPTIONS) as ytdl:
            data = await loop.run_in_executor(None, lambda: ytdl.extract_info(query, download=False))

        if not data:
            await interaction.followup.send("❌ Không tìm thấy bài hát!")
            return

        if 'entries' in data:
            entries = [e for e in data['entries'] if e]
            if not entries:
                await interaction.followup.send("❌ Không tìm thấy bài hát!")
                return

            if data.get('extractor_key') == 'YoutubeSearch' or not query.startswith('http'):
                entry = entries[0]
                url = get_clean_url(entry)
                if url:
                    title = get_title(entry)
                    player.queue.append({'url': url, 'title': title})
                    player.song_added.set()
                    await interaction.followup.send(f"⏳ Đã thêm: **{title}**")
            else:
                count = 0
                for entry in entries:
                    url = get_clean_url(entry)
                    if url:
                        title = get_title(entry)
                        player.queue.append({'url': url, 'title': title})
                        count += 1
                if count > 0:
                    player.song_added.set()
                    await interaction.followup.send(f"✅ Đã nạp **{count}** bài từ playlist!")
        else:
            url = get_clean_url(data) if not query.startswith('http') else (data.get('webpage_url') or data.get('original_url') or query)
            if url:
                title = get_title(data)
                player.queue.append({'url': url, 'title': title})
                player.song_added.set()
                await interaction.followup.send(f"⏳ Đã thêm: **{title}**")

    @app_commands.command(name="pause", description="Tạm dừng nhạc")
    async def pause(self, interaction: discord.Interaction):
        vc = interaction.guild.voice_client
        if vc and vc.is_playing():
            vc.pause()
            await interaction.response.send_message("⏸️ Đã tạm dừng.")
        else:
            await interaction.response.send_message("❌ Hiện tại bot không phát nhạc.", ephemeral=True)

    @app_commands.command(name="resume", description="Tiếp tục phát nhạc")
    async def resume(self, interaction: discord.Interaction):
        vc = interaction.guild.voice_client
        if vc and vc.is_paused():
            vc.resume()
            await interaction.response.send_message("▶️ Tiếp tục phát nhạc.")
        else:
            await interaction.response.send_message("❌ Nhạc không ở trạng thái tạm dừng.", ephemeral=True)

    @app_commands.command(name="skip", description="Bỏ qua bài hát hiện tại")
    async def skip(self, interaction: discord.Interaction):
        vc = interaction.guild.voice_client
        player = self.get_player(interaction)

        if vc and (vc.is_playing() or vc.is_paused()):
            if player.queue:
                next_song = player.queue[0]['title']
                msg = f"⏭️ Đã chuyển bài hát!\n🎶 Đang phát tiếp theo: **{next_song}**"
            else:
                msg = "⏭️ Đã chuyển bài hát!\n📭 Hàng đợi đã trống."

            vc.stop()
            await interaction.response.send_message(msg)
        else:
            await interaction.response.send_message("❌ Không có nhạc đang phát để bỏ qua.", ephemeral=True)

    @app_commands.command(name="queue", description="Hiển thị hàng đợi")
    async def queue(self, interaction: discord.Interaction):
        player = self.get_player(interaction)
        if not player.queue and not (interaction.guild.voice_client and player.current_track):
            await interaction.response.send_message("📭 Hàng đợi hiện tại đang trống.")
            return

        embed = discord.Embed(title="📋 Danh sách nhạc đang chờ", color=discord.Color.blue())
        if player.current_track:
            embed.description = f"**Đang phát:** {player.current_track['title']}\n\n**Tiếp theo:**"

        queue_list = "\n".join(f"`{i}.` {track['title']}" for i, track in enumerate(player.queue[:10], 1))
        if len(player.queue) > 10:
            queue_list += f"\n*...Và {len(player.queue) - 10} bài khác*"

        embed.add_field(name="Hàng đợi", value=queue_list or "Trống", inline=False)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="leave", description="Đuổi bot khỏi kênh thoại và xóa hàng đợi")
    async def leave(self, interaction: discord.Interaction):
        vc = interaction.guild.voice_client
        if vc:
            if interaction.guild_id in self.players:
                player = self.players[interaction.guild_id]
                player.queue.clear()
                player.audio_player_task.cancel()
                del self.players[interaction.guild_id]
            try:
                await vc.disconnect()
            except Exception:
                pass
            await interaction.response.send_message("👋 Đã rời khỏi phòng và làm sạch bộ nhớ.")
        else:
            await interaction.response.send_message("❌ Bot đang không ở trong phòng.", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(Music(bot))
