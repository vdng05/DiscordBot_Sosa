import discord
from discord.ext import commands
from discord import app_commands
import logging

logger = logging.getLogger("SosaBot.General")

class General(commands.Cog):
    """Module tính năng chung: Trợ giúp (/help), Cấp độ (/rank) và Bảng xếp hạng (/leaderboard)"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="help",
        description="Xem danh sách đầy đủ tất cả các lệnh và hướng dẫn sử dụng bot"
    )
    async def help_command(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="📖 BẢNG HƯỚNG DẪN LỆNH SOSABOT",
            description=(
                "Chào mừng bạn đến với **SosaPy**! Dưới đây là danh sách toàn bộ các lệnh Slash Commands (`/`).\n"
                "Bạn chỉ cần gõ `/` kèm tên lệnh để sử dụng."
            ),
            color=discord.Color.blue()
        )

        embed.add_field(
            name="🎵 Âm Nhạc (Music)",
            value=(
                "• `/play <query>`: Phát nhạc từ link (YouTube, SoundCloud, Spotify) hoặc gõ tên bài hát\n"
                "• `/pause`: Tạm dừng bài hát đang phát\n"
                "• `/resume`: Tiếp tục phát nhạc\n"
                "• `/skip`: Bỏ qua bài hát hiện tại sang bài tiếp theo\n"
                "• `/queue`: Xem danh sách bài hát đang chờ trong hàng đợi\n"
                "• `/leave`: Đuổi bot rời phòng thoại và làm sạch hàng đợi"
            ),
            inline=False
        )

        embed.add_field(
            name="🗣️ Giao Tiếp Kênh Thoại (TTS)",
            value="• `/speak <text>`: Đọc văn bản tiếng Việt thành giọng nói (dành cho người không mic, tối đa 300 ký tự)",
            inline=False
        )

        embed.add_field(
            name="⭐ Cấp Độ & Bảng Xếp Hạng (Level & Rank)",
            value=(
                "• `/rank [member]`: Xem cấp độ (Level) và điểm kinh nghiệm (XP) hiện tại\n"
                "• `/leaderboard`: Xem Bảng vàng Top 10 thành viên năng nổ nhất server"
            ),
            inline=False
        )

        embed.add_field(
            name="⚙️ Quản Trị Server (Dành cho Chủ Server)",
            value="• `/setup-server [clear_old]`: Tự động tạo cấu trúc kênh, role theo template chuẩn (Bảo vệ qua 3 bước xác thực)",
            inline=False
        )

        embed.add_field(
            name="👑 Lệnh Quản Trị Chủ Bot (Prefix !)",
            value=(
                "• `!sync guild`: Đồng bộ tức thì các lệnh slash vào server hiện tại\n"
                "• `!reload <module>`: Tải lại module tính năng mà không cần tắt bot\n"
                "• `!status`: Kiểm tra mức tiêu thụ RAM, CPU, ping và uptime"
            ),
            inline=False
        )

        embed.set_footer(text="SosaPy • Hệ thống âm nhạc & quản trị chuẩn mực")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(
        name="rank",
        description="Xem cấp độ (Level) và điểm kinh nghiệm (XP) hiện tại của bạn hoặc thành viên khác"
    )
    @app_commands.describe(
        member="Chọn thành viên bạn muốn xem cấp độ (để trống nếu muốn xem chính mình)"
    )
    async def rank_command(self, interaction: discord.Interaction, member: discord.Member = None):
        target = member or interaction.user
        guild_id = interaction.guild.id
        user_id = target.id

        # Truy vấn dữ liệu Level từ SQLite
        async with self.bot.db._db.execute(
            "SELECT xp, level FROM user_levels WHERE guild_id = ? AND user_id = ?",
            (str(guild_id), str(user_id))
        ) as cursor:
            row = await cursor.fetchone()

        if row:
            xp, level = row
        else:
            xp, level = 0, 1

        needed_xp = int(100 * (level ** 1.5))
        progress = min(int((xp / needed_xp) * 10), 10) if needed_xp > 0 else 0
        progress_bar = "▰" * progress + "▱" * (10 - progress)

        embed = discord.Embed(
            title=f"⭐ HỒ SƠ CẤP ĐỘ — {target.display_name}",
            color=discord.Color.gold()
        )
        embed.set_thumbnail(url=target.display_avatar.url)
        embed.add_field(name="Cấp Độ (Level)", value=f"🏆 **Cấp {level}**", inline=True)
        embed.add_field(name="Kinh Nghiệm (XP)", value=f"✨ **{xp:,}** / {needed_xp:,} XP", inline=True)
        embed.add_field(name="Tiến Trình Thăng Cấp", value=f"`[{progress_bar}]` ({int(xp/needed_xp*100) if needed_xp else 0}%)", inline=False)
        embed.set_footer(text="Chat thường xuyên trong server để tích lũy thêm điểm kinh nghiệm!")

        await interaction.response.send_message(embed=embed)

    @app_commands.command(
        name="leaderboard",
        description="Xem Bảng vàng Top 10 thành viên có cấp độ và điểm kinh nghiệm cao nhất server"
    )
    async def leaderboard_command(self, interaction: discord.Interaction):
        await interaction.response.defer()
        guild_id = interaction.guild.id

        top_members = await self.bot.db.get_leaderboard(guild_id, limit=10)

        if not top_members:
            await interaction.followup.send("📭 Bảng xếp hạng hiện tại đang trống. Hãy bắt đầu chat để tích lũy XP!")
            return

        embed = discord.Embed(
            title=f"🏆 BẢNG VÀNG THÀNH VIÊN — {interaction.guild.name}",
            description="Dưới đây là Top 10 thành viên năng nổ và có cấp độ cao nhất máy chủ:",
            color=discord.Color.purple()
        )

        medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
        lines = []

        for idx, (uid, xp, level) in enumerate(top_members):
            member = interaction.guild.get_member(int(uid))
            name = member.display_name if member else f"Thành viên ({uid})"
            medal = medals[idx] if idx < len(medals) else f"`{idx+1}.`"
            lines.append(f"{medal} **{name}** — Cấp **{level}** `({xp:,} XP)`")

        embed.description += "\n\n" + "\n".join(lines)
        embed.set_footer(text="Dữ liệu được lưu trữ tự động trên SQLite Database")

        await interaction.followup.send(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(General(bot))
