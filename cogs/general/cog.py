import discord
from discord.ext import commands
from discord import app_commands
import logging
from utils.canvas import draw_rank_card

logger = logging.getLogger("SosaBot.General")

class General(commands.Cog):
    """Module tính năng chung: Trợ giúp (/help), Cấp độ (/rank), Xếp hạng (/leaderboard) và Cài đặt (/settings)"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # Nhóm lệnh /settings dành cho Quản trị viên Server
    settings_group = app_commands.Group(
        name="settings",
        description="Quản lý và BẬT/TẮT các tính năng tự động chạy ngầm của máy chủ (Chỉ dành cho Admin)"
    )

    @settings_group.command(
        name="view",
        description="Xem bảng trạng thái BẬT/TẮT hiện tại của các tính năng tự động trên máy chủ"
    )
    @app_commands.default_permissions(manage_guild=True)
    async def settings_view(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        guild_id = interaction.guild.id
        settings = await self.bot.db.get_guild_settings(guild_id)

        automod_status = "🟢 **ĐANG BẬT**" if settings.get("automod_enabled") else "🔴 **ĐANG TẮT (Mặc định)**"
        level_status = "🟢 **ĐANG BẬT**" if settings.get("level_system_enabled") else "🔴 **ĐANG TẮT (Mặc định)**"

        embed = discord.Embed(
            title=f"⚙️ CẤU HÌNH TÍNH NĂNG — {interaction.guild.name}",
            description=(
                "Khi bot mới vào server, tất cả tính năng chạy ngầm đều **mặc định TẮT** để tôn trọng sự riêng tư của server.\n"
                "Quản trị viên có thể dùng các lệnh dưới đây để BẬT hoặc TẮT tùy ý."
            ),
            color=discord.Color.blue()
        )

        embed.add_field(
            name="🛡️ AutoMod (Lọc từ cấm, link rác, chống spam)",
            value=f"Trạng thái: {automod_status}\n*Lệnh đổi:* `/settings automod <enable>`",
            inline=False
        )

        embed.add_field(
            name="⭐ Hệ Thống Level / Rank (Cộng XP khi chat)",
            value=f"Trạng thái: {level_status}\n*Lệnh đổi:* `/settings level <enable>`",
            inline=False
        )

        embed.set_footer(text="Cấu hình được lưu tự động theo từng server trên SQLite Database")
        await interaction.followup.send(embed=embed, ephemeral=True)

    @settings_group.command(
        name="automod",
        description="BẬT hoặc TẮT tính năng tự động lọc từ cấm, link rác và chống spam"
    )
    @app_commands.describe(
        enable="Chọn True để BẬT AutoMod, False để TẮT AutoMod"
    )
    @app_commands.default_permissions(manage_guild=True)
    async def settings_automod(self, interaction: discord.Interaction, enable: bool):
        await interaction.response.defer(ephemeral=True)
        guild_id = interaction.guild.id

        await self.bot.db.update_guild_setting(guild_id, "automod_enabled", 1 if enable else 0)
        status_text = "🟢 **ĐÃ BẬT**" if enable else "🔴 **ĐÃ TẮT**"

        embed = discord.Embed(
            title="⚙️ CẬP NHẬT AUTOMOD THÀNH CÔNG",
            description=f"Tính năng **AutoMod (Chống spam, lọc link rác & từ cấm)** hiện tại: {status_text} cho máy chủ này.",
            color=discord.Color.green() if enable else discord.Color.red()
        )
        logger.info(f"[{interaction.guild.name}] {interaction.user} đã chuyển AutoMod thành: {enable}")
        await interaction.followup.send(embed=embed, ephemeral=True)

    @settings_group.command(
        name="level",
        description="BẬT hoặc TẮT hệ thống tính điểm kinh nghiệm (XP) và thông báo lên cấp khi chat"
    )
    @app_commands.describe(
        enable="Chọn True để BẬT hệ thống Level/XP, False để TẮT"
    )
    @app_commands.default_permissions(manage_guild=True)
    async def settings_level(self, interaction: discord.Interaction, enable: bool):
        await interaction.response.defer(ephemeral=True)
        guild_id = interaction.guild.id

        await self.bot.db.update_guild_setting(guild_id, "level_system_enabled", 1 if enable else 0)
        status_text = "🟢 **ĐÃ BẬT**" if enable else "🔴 **ĐÃ TẮT**"

        embed = discord.Embed(
            title="⚙️ CẬP NHẬT HỆ THỐNG LEVEL THÀNH CÔNG",
            description=f"Tính năng **Level / Rank XP** hiện tại: {status_text} cho máy chủ này.",
            color=discord.Color.green() if enable else discord.Color.red()
        )
        logger.info(f"[{interaction.guild.name}] {interaction.user} đã chuyển Level System thành: {enable}")
        await interaction.followup.send(embed=embed, ephemeral=True)

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
                "• `/rank [member]` (hoặc `!rank`): Xem Thẻ Rank đồ họa cá nhân cực xịn\n"
                "• `/leaderboard`: Xem Bảng vàng Top 10 thành viên năng nổ nhất server"
            ),
            inline=False
        )

        embed.add_field(
            name="💘 Bói Tình Duyên & Cặp Đôi (Love & Marry)",
            value=(
                "• `/lovec <target>` (hoặc `!lovec`): Đo độ hợp nhau (hỗ trợ `random` ghép đôi ngẫu nhiên)\n"
                "• `/marry <@user>` (hoặc `!marry`): Cầu hôn thành viên khác\n"
                "• `/marry`: Mở Ngôi Nhà Cặp Đôi tương tác (Trang chủ, Album ảnh, Ghi chú)\n"
                "• `/marry_name <tên>` (hoặc `!name`): Đổi tên ngôi nhà\n"
                "• `/marry_quote <nội dung>` (hoặc `!quote`): Đổi châm ngôn tình yêu\n"
                "• `/lgallery <1-6> <link>` (hoặc `!lgallery`): Thêm ảnh vào album kỷ niệm\n"
                "• `/divorce` (hoặc `!divorce`): Ly hôn giải phóng ngôi nhà"
            ),
            inline=False
        )

        embed.add_field(
            name="✨ Tương Tác Thân Mật (Tăng Điểm Nhẫn Cưới)",
            value=(
                "• `/kiss`, `/hug`, `/pat`, `/slap` (hoặc `!kiss`, `!hug`...):\n"
                "  Tương tác với người ấy để nhận +10 Điểm thân mật & nâng cấp Nhẫn Cưới"
            ),
            inline=False
        )

        embed.add_field(
            name="⚙️ Quản Trị & Cấu Hình Máy Chủ",
            value=(
                "• `/settings view`: Xem trạng thái các tính năng tự động (AutoMod, Level)\n"
                "• `/settings automod <enable>`: BẬT hoặc TẮT tính năng AutoMod cho server\n"
                "• `/settings level <enable>`: BẬT hoặc TẮT tính năng cộng điểm XP cho server\n"
                "• `/setup-server [clear_old]`: Tự động tạo cấu trúc kênh, role theo template (3 bước xác nhận, chỉ Chủ Server)"
            ),
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
        description="Xem Thẻ Rank đồ họa cực chất hiển thị Level, XP và thứ hạng của bạn hoặc người khác"
    )
    @app_commands.describe(
        member="Chọn thành viên bạn muốn xem cấp độ (để trống nếu muốn xem chính mình)"
    )
    async def rank_command(self, interaction: discord.Interaction, member: discord.Member = None):
        await interaction.response.defer()
        target = member or interaction.user
        guild_id = interaction.guild.id
        user_id = target.id

        rank_pos, xp, level = await self.bot.db.get_user_rank(guild_id, user_id)
        needed_xp = int(100 * (level ** 1.5))

        try:
            image_buf = await draw_rank_card(
                avatar_url=target.display_avatar.url,
                username=target.display_name,
                level=level,
                current_xp=xp,
                needed_xp=needed_xp,
                rank_num=rank_pos
            )
            file = discord.File(fp=image_buf, filename=f"rank_{target.id}.png")
            await interaction.followup.send(file=file)
        except Exception as e:
            logger.error(f"Lỗi khi vẽ Thẻ Rank: {e}", exc_info=True)
            # Fallback sang Embed nếu lỗi đồ họa
            embed = discord.Embed(
                title=f"⭐ HỒ SƠ CẤP ĐỘ — {target.display_name}",
                description=f"Thứ hạng: **#{rank_pos}** | Cấp độ: **{level}** | XP: **{xp:,}** / {needed_xp:,}",
                color=discord.Color.gold()
            )
            embed.set_thumbnail(url=target.display_avatar.url)
            await interaction.followup.send(embed=embed)

    @commands.command(name="rank", description="Xem Thẻ Rank đồ họa (!rank [@member])")
    async def rank_prefix(self, ctx: commands.Context, member: discord.Member = None):
        target = member or ctx.author
        guild_id = ctx.guild.id
        user_id = target.id

        rank_pos, xp, level = await self.bot.db.get_user_rank(guild_id, user_id)
        needed_xp = int(100 * (level ** 1.5))

        try:
            image_buf = await draw_rank_card(
                avatar_url=target.display_avatar.url,
                username=target.display_name,
                level=level,
                current_xp=xp,
                needed_xp=needed_xp,
                rank_num=rank_pos
            )
            file = discord.File(fp=image_buf, filename=f"rank_{target.id}.png")
            await ctx.reply(file=file, mention_author=False)
        except Exception as e:
            logger.error(f"Lỗi khi vẽ Thẻ Rank: {e}", exc_info=True)
            embed = discord.Embed(
                title=f"⭐ HỒ SƠ CẤP ĐỘ — {target.display_name}",
                description=f"Thứ hạng: **#{rank_pos}** | Cấp độ: **{level}** | XP: **{xp:,}** / {needed_xp:,}",
                color=discord.Color.gold()
            )
            embed.set_thumbnail(url=target.display_avatar.url)
            await ctx.reply(embed=embed, mention_author=False)

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
