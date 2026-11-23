import discord
from discord.ext import commands

class MusicControlView(discord.ui.View):
    """Giao diện 4 nút bấm điều khiển nhạc trực quan: Tạm dừng, Bỏ qua, Hàng đợi, Rời phòng"""

    def __init__(self, bot: commands.Bot, guild_id: int):
        super().__init__(timeout=None)
        self.bot = bot
        self.guild_id = guild_id

    def get_vc(self, interaction: discord.Interaction):
        return interaction.guild.voice_client if interaction.guild else None

    def get_player(self):
        music_cog = self.bot.get_cog("Music")
        if music_cog and self.guild_id in music_cog.players:
            return music_cog.players[self.guild_id]
        return None

    @discord.ui.button(label="⏯️ Tạm Dừng / Tiếp Tục", style=discord.ButtonStyle.primary, custom_id="music_btn_pause_resume")
    async def pause_resume(self, interaction: discord.Interaction, button: discord.ui.Button):
        vc = self.get_vc(interaction)
        if not vc:
            await interaction.response.send_message("❌ Bot không ở trong kênh thoại nào.", ephemeral=True)
            return

        if vc.is_playing():
            vc.pause()
            await interaction.response.send_message("⏸️ Đã tạm dừng bài hát!", ephemeral=True)
        elif vc.is_paused():
            vc.resume()
            await interaction.response.send_message("▶️ Đã tiếp tục phát nhạc!", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Hiện không có bài hát nào đang phát.", ephemeral=True)

    @discord.ui.button(label="⏭️ Bỏ Qua", style=discord.ButtonStyle.secondary, custom_id="music_btn_skip")
    async def skip(self, interaction: discord.Interaction, button: discord.ui.Button):
        vc = self.get_vc(interaction)
        player = self.get_player()
        if not vc or not (vc.is_playing() or vc.is_paused()):
            await interaction.response.send_message("❌ Không có bài hát nào đang phát để bỏ qua.", ephemeral=True)
            return

        next_title = player.queue[0]['title'] if (player and player.queue) else "Hàng đợi đã hết bài"
        vc.stop()
        await interaction.response.send_message(f"⏭️ Đã bỏ qua bài hát! (Tiếp theo: **{next_title}**)", ephemeral=True)

    @discord.ui.button(label="📜 Xem Hàng Đợi", style=discord.ButtonStyle.secondary, custom_id="music_btn_queue")
    async def view_queue(self, interaction: discord.Interaction, button: discord.ui.Button):
        player = self.get_player()
        if not player or (not player.queue and not player.current_track):
            await interaction.response.send_message("📭 Hàng đợi bài hát hiện tại đang trống.", ephemeral=True)
            return

        embed = discord.Embed(title="📋 DANH SÁCH BÀI HÁT ĐANG CHỜ", color=discord.Color.from_rgb(255, 105, 180))
        if player.current_track:
            embed.description = f"🎶 **Đang phát:** {player.current_track['title']}\n\n**Các bài hát tiếp theo:**"

        lines = [f"`{i}.` {t['title']}" for i, t in enumerate(player.queue[:10], 1)]
        if len(player.queue) > 10:
            lines.append(f"*...và còn {len(player.queue) - 10} bài khác*")

        embed.add_field(name="Hàng chờ", value="\n".join(lines) if lines else "Không còn bài nào.", inline=False)
        embed.set_footer(text="SosaGallery • Bấm nút ⏭️ để chuyển bài tiếp theo")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(label="⏹️ Dừng & Thoát", style=discord.ButtonStyle.danger, custom_id="music_btn_stop")
    async def stop_leave(self, interaction: discord.Interaction, button: discord.ui.Button):
        vc = self.get_vc(interaction)
        music_cog = self.bot.get_cog("Music")
        if vc:
            if music_cog and self.guild_id in music_cog.players:
                p = music_cog.players[self.guild_id]
                p.queue.clear()
                p.audio_player_task.cancel()
                del music_cog.players[self.guild_id]
            try:
                await vc.disconnect()
            except Exception:
                pass
            await interaction.response.send_message("⏹️ Đã dừng phát nhạc và rời khỏi phòng thoại. Hẹn gặp lại bạn nhé!", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Bot không ở trong kênh thoại nào.", ephemeral=True)
