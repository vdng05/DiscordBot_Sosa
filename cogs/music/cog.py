import discord
from discord.ext import commands
from discord import app_commands
import yt_dlp
import asyncio
import logging
from .sources import YTDL_SEARCH_OPTIONS, get_clean_url, get_title, resolve_spotify_link
from .player import MusicPlayer
from .views import MusicControlView

logger = logging.getLogger("SosaGallery.Music")

class Music(commands.Cog):
    """Module phát nhạc chất lượng cao hỗ trợ YouTube, SoundCloud, Spotify và nút điều khiển trực quan"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.players = {}

    def get_player(self, guild_id: int, guild: discord.Guild = None) -> MusicPlayer:
        if guild_id not in self.players:
            if not guild:
                guild = self.bot.get_guild(guild_id)
            self.players[guild_id] = MusicPlayer(self.bot, guild)
        return self.players[guild_id]

    async def _play_internal(self, ctx_or_interaction, query: str):
        """Xử lý phát nhạc chung cho cả Slash command và Prefix command"""
        is_interaction = isinstance(ctx_or_interaction, discord.Interaction)
        guild = ctx_or_interaction.guild
        author = ctx_or_interaction.user if is_interaction else ctx_or_interaction.author
        user = guild.get_member(author.id)

        async def send_response(text: str, view: discord.ui.View = None, ephemeral: bool = False):
            if is_interaction:
                if ctx_or_interaction.response.is_done():
                    return await ctx_or_interaction.followup.send(text, view=view, ephemeral=ephemeral)
                else:
                    return await ctx_or_interaction.response.send_message(text, view=view, ephemeral=ephemeral)
            else:
                return await ctx_or_interaction.reply(text, view=view, mention_author=False)

        if not user or not user.voice or not user.voice.channel:
            await send_response("❌ Bạn hãy tham gia vào một kênh thoại trước khi bật nhạc nhé!", ephemeral=True)
            return

        vc = guild.voice_client
        # Nếu bot đang ở phòng khác có người nghe
        if vc and vc.channel != user.voice.channel:
            active_listeners = [m for m in vc.channel.members if not m.bot]
            if len(active_listeners) > 0:
                await send_response(
                    f"❌ Bot đang phát nhạc tại kênh **{vc.channel.name}**!\n"
                    "Bạn hãy vào cùng phòng nghe chung hoặc đợi bài hát kết thúc nha.",
                    ephemeral=True
                )
                return
            await vc.move_to(user.voice.channel)
        elif not vc:
            vc = await user.voice.channel.connect()

        # Link Spotify
        if "spotify.com" in query:
            spotify_query = await asyncio.to_thread(resolve_spotify_link, query)
            if spotify_query:
                query = spotify_query
            else:
                await send_response("❌ Bot chưa thể đọc link Spotify này. Bạn thử gõ tên bài hát để tìm kiếm xem sao nhé!")
                return

        player = self.get_player(guild.id, guild)
        loop = asyncio.get_running_loop()

        with yt_dlp.YoutubeDL(YTDL_SEARCH_OPTIONS) as ytdl:
            data = await loop.run_in_executor(None, lambda: ytdl.extract_info(query, download=False))

        if not data:
            await send_response("❌ Không tìm thấy bài hát nào phù hợp. Bạn kiểm tra lại tên bài hoặc link nhé!")
            return

        control_view = MusicControlView(self.bot, guild.id)

        if 'entries' in data:
            entries = [e for e in data['entries'] if e]
            if not entries:
                await send_response("❌ Không tìm thấy bài hát nào!")
                return

            if data.get('extractor_key') == 'YoutubeSearch' or not query.startswith('http'):
                entry = entries[0]
                url = get_clean_url(entry)
                if url:
                    title = get_title(entry)
                    player.queue.append({'url': url, 'title': title})
                    player.song_added.set()
                    await send_response(
                        f"⏳ Đã thêm vào hàng đợi: **{title}**\n*(Bạn có thể bấm các nút bên dưới để điều khiển nhạc)*",
                        view=control_view
                    )
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
                    await send_response(
                        f"✅ Đã thêm thành công **{count}** bài hát từ danh sách phát vào hàng đợi!\n*(Bạn có thể bấm các nút bên dưới để điều khiển nhạc)*",
                        view=control_view
                    )
        else:
            url = get_clean_url(data) if not query.startswith('http') else (data.get('webpage_url') or data.get('original_url') or query)
            if url:
                title = get_title(data)
                player.queue.append({'url': url, 'title': title})
                player.song_added.set()
                await send_response(
                    f"⏳ Đã thêm vào hàng đợi: **{title}**\n*(Bạn có thể bấm các nút bên dưới để điều khiển nhạc)*",
                    view=control_view
                )

    # ==========================
    # SLASH COMMANDS
    # ==========================
    @app_commands.command(
        name="play",
        description="Phát nhạc từ link (YouTube, SoundCloud, Spotify) hoặc tìm theo tên bài hát"
    )
    @app_commands.describe(
        query="Nhập link bài hát hoặc gõ tên bài hát (Ví dụ: Nơi này có anh, Đi về nhà...)"
    )
    async def play_slash(self, interaction: discord.Interaction, query: str):
        await interaction.response.defer()
        await self._play_internal(interaction, query)

    @app_commands.command(name="pause", description="Tạm dừng bài hát đang phát")
    async def pause_slash(self, interaction: discord.Interaction):
        vc = interaction.guild.voice_client
        if vc and vc.is_playing():
            vc.pause()
            await interaction.response.send_message("⏸️ Đã tạm dừng phát nhạc.")
        else:
            await interaction.response.send_message("❌ Hiện tại bot không phát bài hát nào.", ephemeral=True)

    @app_commands.command(name="resume", description="Tiếp tục phát bài hát đang tạm dừng")
    async def resume_slash(self, interaction: discord.Interaction):
        vc = interaction.guild.voice_client
        if vc and vc.is_paused():
            vc.resume()
            await interaction.response.send_message("▶️ Tiếp tục phát nhạc.")
        else:
            await interaction.response.send_message("❌ Nhạc không ở trạng thái tạm dừng.", ephemeral=True)

    @app_commands.command(name="skip", description="Bỏ qua bài hát hiện tại và chuyển sang bài tiếp theo")
    async def skip_slash(self, interaction: discord.Interaction):
        vc = interaction.guild.voice_client
        player = self.get_player(interaction.guild_id, interaction.guild)

        if vc and (vc.is_playing() or vc.is_paused()):
            if player.queue:
                next_song = player.queue[0]['title']
                msg = f"⏭️ Đã chuyển bài hát!\n🎶 **Đang phát tiếp theo:** {next_song}"
            else:
                msg = "⏭️ Đã chuyển bài hát!\n📭 Hàng đợi bài hát hiện tại đã hết."

            vc.stop()
            await interaction.response.send_message(msg)
        else:
            await interaction.response.send_message("❌ Không có bài hát nào đang phát để bỏ qua.", ephemeral=True)

    @app_commands.command(name="queue", description="Xem danh sách các bài hát đang chờ phát")
    async def queue_slash(self, interaction: discord.Interaction):
        player = self.get_player(interaction.guild_id, interaction.guild)
        if not player.queue and not (interaction.guild.voice_client and player.current_track):
            await interaction.response.send_message("📭 Hàng đợi bài hát hiện tại đang trống.")
            return

        embed = discord.Embed(title="📋 DANH SÁCH BÀI HÁT ĐANG CHỜ", color=discord.Color.from_rgb(255, 105, 180))
        if player.current_track:
            embed.description = f"**🎶 Đang phát:** {player.current_track['title']}\n\n**Các bài hát tiếp theo:**"

        queue_list = "\n".join(f"`{i}.` {track['title']}" for i, track in enumerate(player.queue[:10], 1))
        if len(player.queue) > 10:
            queue_list += f"\n*...Và còn {len(player.queue) - 10} bài khác*"

        embed.add_field(name="Hàng chờ", value=queue_list or "Không còn bài nào.", inline=False)
        embed.set_footer(text="SosaGallery • Bấm nút ⏭️ bên dưới để chuyển bài")
        await interaction.response.send_message(embed=embed, view=MusicControlView(self.bot, interaction.guild_id))

    @app_commands.command(name="leave", description="Dừng phát nhạc và rời khỏi phòng thoại")
    async def leave_slash(self, interaction: discord.Interaction):
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
            await interaction.response.send_message("👋 Đã rời khỏi phòng thoại. Hẹn gặp lại bạn nha!")
        else:
            await interaction.response.send_message("❌ Bot đang không ở trong kênh thoại nào.", ephemeral=True)

    # ==========================
    # PREFIX COMMANDS (!play, !pause, !resume, !skip, !queue, !leave)
    # ==========================
    @commands.command(name="play", aliases=["p"], description="Phát nhạc (!play <tên bài/link>)")
    async def play_text(self, ctx: commands.Context, *, query: str):
        await self._play_internal(ctx, query)

    @commands.command(name="pause", description="Tạm dừng bài hát (!pause)")
    async def pause_text(self, ctx: commands.Context):
        vc = ctx.guild.voice_client
        if vc and vc.is_playing():
            vc.pause()
            await ctx.reply("⏸️ Đã tạm dừng phát nhạc.", mention_author=False)
        else:
            await ctx.reply("❌ Hiện tại bot không phát bài hát nào.", mention_author=False)

    @commands.command(name="resume", description="Tiếp tục phát nhạc (!resume)")
    async def resume_text(self, ctx: commands.Context):
        vc = ctx.guild.voice_client
        if vc and vc.is_paused():
            vc.resume()
            await ctx.reply("▶️ Tiếp tục phát nhạc.", mention_author=False)
        else:
            await ctx.reply("❌ Nhạc không ở trạng thái tạm dừng.", mention_author=False)

    @commands.command(name="skip", aliases=["s"], description="Chuyển sang bài tiếp theo (!skip hoặc !s)")
    async def skip_text(self, ctx: commands.Context):
        vc = ctx.guild.voice_client
        player = self.get_player(ctx.guild.id, ctx.guild)

        if vc and (vc.is_playing() or vc.is_paused()):
            if player.queue:
                next_song = player.queue[0]['title']
                msg = f"⏭️ Đã chuyển bài hát!\n🎶 **Đang phát tiếp theo:** {next_song}"
            else:
                msg = "⏭️ Đã chuyển bài hát!\n📭 Hàng đợi bài hát hiện tại đã hết."

            vc.stop()
            await ctx.reply(msg, mention_author=False)
        else:
            await ctx.reply("❌ Không có bài hát nào đang phát để bỏ qua.", mention_author=False)

    @commands.command(name="queue", aliases=["q"], description="Xem danh sách bài hát đang chờ (!queue hoặc !q)")
    async def queue_text(self, ctx: commands.Context):
        player = self.get_player(ctx.guild.id, ctx.guild)
        if not player.queue and not (ctx.guild.voice_client and player.current_track):
            await ctx.reply("📭 Hàng đợi bài hát hiện tại đang trống.", mention_author=False)
            return

        embed = discord.Embed(title="📋 DANH SÁCH BÀI HÁT ĐANG CHỜ", color=discord.Color.from_rgb(255, 105, 180))
        if player.current_track:
            embed.description = f"**🎶 Đang phát:** {player.current_track['title']}\n\n**Các bài hát tiếp theo:**"

        queue_list = "\n".join(f"`{i}.` {track['title']}" for i, track in enumerate(player.queue[:10], 1))
        if len(player.queue) > 10:
            queue_list += f"\n*...Và còn {len(player.queue) - 10} bài khác*"

        embed.add_field(name="Hàng chờ", value=queue_list or "Không còn bài nào.", inline=False)
        embed.set_footer(text="SosaGallery • Bấm nút bên dưới để điều khiển")
        await ctx.reply(embed=embed, view=MusicControlView(self.bot, ctx.guild.id), mention_author=False)

    @commands.command(name="leave", aliases=["stop"], description="Dừng phát và rời phòng (!leave hoặc !stop)")
    async def leave_text(self, ctx: commands.Context):
        vc = ctx.guild.voice_client
        if vc:
            if ctx.guild.id in self.players:
                player = self.players[ctx.guild.id]
                player.queue.clear()
                player.audio_player_task.cancel()
                del self.players[ctx.guild.id]
            try:
                await vc.disconnect()
            except Exception:
                pass
            await ctx.reply("👋 Đã rời khỏi phòng thoại. Hẹn gặp lại bạn nha!", mention_author=False)
        else:
            await ctx.reply("❌ Bot đang không ở trong kênh thoại nào.", mention_author=False)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        """Nếu tất cả người dùng rời phòng (chỉ còn bot), tự động ngắt kết nối để giải phóng tài nguyên"""
        if member.bot:
            return

        if before.channel and (not after.channel or before.channel != after.channel):
            guild = before.channel.guild
            vc = guild.voice_client

            if vc and vc.channel == before.channel:
                non_bot_members = [m for m in before.channel.members if not m.bot]
                if len(non_bot_members) == 0:
                    logger.info(f"[{guild.name}] Mọi người đã rời phòng thoại. Tự động thoát để tiết kiệm tài nguyên.")
                    if guild.id in self.players:
                        player = self.players[guild.id]
                        player.queue.clear()
                        player.audio_player_task.cancel()
                        del self.players[guild.id]
                    try:
                        await vc.disconnect()
                    except Exception:
                        pass

async def setup(bot: commands.Bot):
    await bot.add_cog(Music(bot))
