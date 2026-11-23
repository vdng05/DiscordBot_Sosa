import discord
from discord.ext import commands
from discord import app_commands
import logging
from utils.canvas import draw_rank_card

logger = logging.getLogger("SosaBot.General")

def get_help_embed(category: str = "all") -> discord.Embed:
    """Tạo Embed hướng dẫn lệnh tương ứng theo từng danh mục hoặc tổng quan"""
    if category == "music":
        embed = discord.Embed(
            title="🎵 HỆ THỐNG ÂM NHẠC (MUSIC)",
            description="Phát nhạc chất lượng cao, tự động điều phối hàng đợi và tiết kiệm tài nguyên máy chủ.",
            color=discord.Color.blue()
        )
        embed.add_field(name="• `/play <query>`", value="Phát nhạc từ link (YouTube, SoundCloud, Spotify) hoặc gõ tên bài hát để bot tự tìm kiếm.", inline=False)
        embed.add_field(name="• `/pause`", value="Tạm dừng bài hát đang phát trong phòng thoại.", inline=False)
        embed.add_field(name="• `/resume`", value="Tiếp tục phát bài hát đang bị tạm dừng.", inline=False)
        embed.add_field(name="• `/skip`", value="Bỏ qua bài hát hiện tại và phát bài tiếp theo trong hàng đợi.", inline=False)
        embed.add_field(name="• `/queue`", value="Xem danh sách toàn bộ các bài hát đang chờ trong hàng đợi.", inline=False)
        embed.add_field(name="• `/leave`", value="Yêu cầu bot rời phòng thoại và làm sạch hàng đợi.", inline=False)
        embed.set_footer(text="Bot sẽ tự động rời phòng thoại sau 5 phút nếu không có bài hát hoặc phòng trống người.")
        return embed

    elif category == "tts":
        embed = discord.Embed(
            title="🗣️ GIAO TIẾP GIỌNG NÓI (VOICE TTS)",
            description="Chuyển văn bản tiếng Việt thành giọng nói tự nhiên trong kênh thoại dành cho thành viên không có micro.",
            color=discord.Color.green()
        )
        embed.add_field(name="• `/speak <text>`", value="Đọc nội dung văn bản tiếng Việt (tối đa 300 ký tự chống spam).", inline=False)
        embed.add_field(name="💡 Cơ chế điều phối âm thanh thông minh", value="Nếu bot đang phát nhạc, bot sẽ tự lưu bài hát đang nghe dở, đọc xong câu TTS rồi tự động tiếp tục phát nhạc mượt mà không lỗi xung đột.", inline=False)
        embed.set_footer(text="Hỗ trợ cả phòng chat thoại lẫn chat tin nhắn thông thường.")
        return embed

    elif category == "rank":
        embed = discord.Embed(
            title="⭐ CẤP ĐỘ & THẺ RANK ĐỒ HỌA (LEVEL & XP)",
            description="Tích lũy kinh nghiệm khi giao lưu trong server, lưu trữ trực tiếp trên SQLite Database siêu tốc.",
            color=discord.Color.gold()
        )
        embed.add_field(name="• `/rank [member]` (hoặc `!rank`)", value="Xem **Thẻ Rank đồ họa cực đỉnh** (Canvas Anime Chibi Gal Hiphop Neon) hiển thị Level, XP, thứ hạng server và thanh tiến trình.", inline=False)
        embed.add_field(name="• `/leaderboard`", value="Xem Bảng vàng vinh danh Top 10 thành viên có cấp độ và điểm kinh nghiệm cao nhất server.", inline=False)
        embed.add_field(name="📈 Cách nhận XP", value="Mỗi tin nhắn hợp lệ gửi vào server được cộng từ 15 đến 25 XP (có cooldown 60s chống spam). Quản trị viên có thể BẬT/TẮT tính năng này qua `/settings level`.", inline=False)
        embed.set_footer(text="Dữ liệu được lưu trữ tự động trong SQLite Database an toàn.")
        return embed

    elif category == "marry":
        embed = discord.Embed(
            title="💘 BÓI TÌNH DUYÊN & KẾT HÔN (LOVE & MARRY)",
            description="Hệ thống bói duyên banner đồ họa phong cách Lunari và Ngôi Nhà Cặp Đôi tương tác 3 tab.",
            color=discord.Color.pink()
        )
        embed.add_field(name="• `/lovec <target>` (hoặc `!lovec`)", value="Đo độ hợp nhau giữa 2 người (gõ `random` để bot bốc ngẫu nhiên 1 người trong server). Xuất banner đồ họa Anime Gal Hiphop tuyệt đẹp!", inline=False)
        embed.add_field(name="• `/marry <@user>` (hoặc `!marry`)", value="Cầu hôn người ấy với giao diện tương tác gồm 2 nút bấm: **💍 Đồng Ý** hoặc **💔 Từ Chối** (chờ 120s).", inline=False)
        embed.add_field(name="• `/marry`", value="Mở giao diện **Ngôi Nhà Cặp Đôi** với 3 Tab: **Trang Chủ**, **Album 6 Ảnh Kỷ Niệm** (có nút lướt ảnh) và **Ghi Chú**.", inline=False)
        embed.add_field(name="• `/marry_name <tên>` (hoặc `!name`)", value="Đổi tên ngôi nhà cặp đôi.", inline=False)
        embed.add_field(name="• `/marry_quote <nội dung>` (hoặc `!quote`)", value="Đổi câu châm ngôn tình yêu hiển thị ở trang chủ ngôi nhà.", inline=False)
        embed.add_field(name="• `/lgallery <1-6> <URL>` (hoặc `!lgallery`)", value="Lưu ảnh kỷ niệm vào 1 trong 6 slot của album gia đình.", inline=False)
        embed.add_field(name="• `/divorce` (hoặc `!divorce`)", value="Ly hôn và giải phóng ngôi nhà cặp đôi.", inline=False)
        embed.set_footer(text="Tương tác mỗi ngày để nâng cấp phẩm chất Nhẫn Cưới!")
        return embed

    elif category == "actions":
        embed = discord.Embed(
            title="✨ TƯƠNG TÁC THÂN MẬT (ACTIONS & NHẪN CƯỚI)",
            description="Các hành động tình cảm kèm GIF anime dễ thương. Khi tương tác với bạn đời đã kết hôn sẽ nhận **+10 Điểm Thân Mật**!",
            color=discord.Color.purple()
        )
        embed.add_field(name="• `/kiss <@user>` (hoặc `!kiss`)", value="Trao cho người ấy một nụ hôn ngọt ngào.", inline=False)
        embed.add_field(name="• `/hug <@user>` (hoặc `!hug`)", value="Một cái ôm ấm áp siết chặt.", inline=False)
        embed.add_field(name="• `/pat <@user>` (hoặc `!pat`)", value="Xoa đầu cưng nựng dễ thương.", inline=False)
        embed.add_field(name="• `/slap <@user>` (hoặc `!slap`)", value="Phát tát giận dỗi đáng yêu.", inline=False)
        embed.add_field(
            name="💍 Bảng 5 Cấp Bậc Nhẫn Cưới",
            value=(
                "🌿 **Tier 1 - Nhẫn Cỏ Thần Tiên:** 0 - 49 điểm\n"
                "🪙 **Tier 2 - Nhẫn Bạc Thuần Khiết:** 50 - 149 điểm\n"
                "👑 **Tier 3 - Nhẫn Vàng Vương Giả:** 150 - 299 điểm\n"
                "💎 **Tier 4 - Nhẫn Kim Cương Vĩnh Cửu:** 300 - 499 điểm\n"
                "🌌 **Tier 5 - Nhẫn Vô Cực Ngân Hà:** 500+ điểm (Huyền thoại!)"
            ),
            inline=False
        )
        embed.set_footer(text="Cooldown tương tác tăng điểm: 30 giây.")
        return embed

    elif category == "admin":
        embed = discord.Embed(
            title="⚙️ QUẢN TRỊ & CÀI ĐẶT MÁY CHỦ (ADMIN)",
            description="Các công cụ cấu hình và quản trị an ninh dành cho Quản trị viên máy chủ.",
            color=discord.Color.dark_gray()
        )
        embed.add_field(name="• `!sync` (hoặc `!sync guild`)", value="**Cực kỳ quan trọng:** Đồng bộ tức thì toàn bộ 22 lệnh Slash Commands vào server của bạn! (Dùng ngay nếu gõ `/` chưa thấy lệnh mới).", inline=False)
        embed.add_field(name="• `/settings view`", value="Xem bảng trạng thái BẬT/TẮT hiện tại của AutoMod và Level/XP trên máy chủ.", inline=False)
        embed.add_field(name="• `/settings automod <enable>`", value="BẬT hoặc TẮT bộ lọc từ cấm, chặn link rác và chống spam.", inline=False)
        embed.add_field(name="• `/settings level <enable>`", value="BẬT hoặc TẮT hệ thống tính điểm kinh nghiệm (XP) khi chat.", inline=False)
        embed.add_field(name="• `/setup-server [clear_old]`", value="Khởi tạo danh mục kênh và vai trò theo template chuẩn (3 bước xác nhận nút bấm, chỉ Chủ Server).", inline=False)
        embed.add_field(name="• `!status`", value="Kiểm tra mức RAM, CPU, ping mạng và thời gian hoạt động của bot.", inline=False)
        embed.set_footer(text="Tất cả tính năng tự động mặc định TẮT khi bot mới vào server.")
        return embed

    # MẶC ĐỊNH: TỔNG QUAN TẤT CẢ LỆNH
    embed = discord.Embed(
        title="📖 TỔNG HỢP TOÀN BỘ LỆNH SOSABOT",
        description=(
            "Chào mừng bạn đến với **SosaPy**! Dưới đây là danh sách toàn bộ các danh mục và lệnh của bot.\n\n"
            "💡 **CHÚ Ý:** Nếu bạn gõ `/` mà chưa thấy các lệnh mới, hãy gõ ngay lệnh **`!sync`** tại kênh chat để bot đồng bộ toàn bộ Slash Commands vào server của bạn tức thì!\n\n"
            "👉 *Dùng Menu chọn bên dưới để xem hướng dẫn chi tiết của từng danh mục.*"
        ),
        color=discord.Color.from_rgb(255, 105, 180)
    )

    embed.add_field(
        name="🎵 1. Âm Nhạc (Music — 6 lệnh)",
        value="`/play`, `/pause`, `/resume`, `/skip`, `/queue`, `/leave`\n*Hỗ trợ YouTube, SoundCloud, Spotify*",
        inline=False
    )
    embed.add_field(
        name="🗣️ 2. Voice TTS (1 lệnh)",
        value="`/speak <text>`: Đọc văn bản tiếng Việt thành giọng nói kênh thoại",
        inline=False
    )
    embed.add_field(
        name="⭐ 3. Level & Thẻ Rank (2 lệnh)",
        value="`/rank [member]` *(Thẻ Canvas Anime Gal Hiphop Neon)*, `/leaderboard` *(Top 10)*",
        inline=False
    )
    embed.add_field(
        name="💘 4. Bói Duyên & Kết Hôn (6 lệnh)",
        value="`/lovec` *(Bói duyên canvas)*, `/marry` *(Ngôi Nhà 3 Tab)*, `/marry_name`, `/marry_quote`, `/lgallery`, `/divorce`",
        inline=False
    )
    embed.add_field(
        name="✨ 5. Tương Tác Thân Mật (4 lệnh)",
        value="`/kiss`, `/hug`, `/pat`, `/slap` *(+10 Điểm thân mật & Nâng cấp 5 bậc Nhẫn Cưới)*",
        inline=False
    )
    embed.add_field(
        name="⚙️ 6. Quản Trị & Cài Đặt (5 lệnh)",
        value="`/settings view`, `/settings automod`, `/settings level`, `/setup-server`, `!sync`",
        inline=False
    )

    embed.set_footer(text="SosaPy v1.7.0 • Chọn menu bên dưới để xem hướng dẫn từng mục!")
    return embed


class HelpSelect(discord.ui.Select):
    """Menu chọn danh mục trợ giúp dạng Dropdown"""

    def __init__(self):
        options = [
            discord.SelectOption(label="Tất Cả Lệnh (Tổng Quan)", description="Xem toàn bộ danh mục và tóm tắt lệnh", emoji="📌", value="all"),
            discord.SelectOption(label="Âm Nhạc (Music)", description="Các lệnh nghe nhạc YouTube, SoundCloud, Spotify", emoji="🎵", value="music"),
            discord.SelectOption(label="Voice TTS (Tiếng Việt)", description="Đọc văn bản thành giọng nói kênh thoại", emoji="🗣️", value="tts"),
            discord.SelectOption(label="Cấp Độ & Rank (XP)", description="Thẻ Rank đồ họa Anime Gal Hiphop & Bảng vàng", emoji="⭐", value="rank"),
            discord.SelectOption(label="Bói Duyên & Kết Hôn", description="Love Calculator & Ngôi Nhà Cặp Đôi 3 tab", emoji="💘", value="marry"),
            discord.SelectOption(label="Tương Tác Thân Mật", description="Kiss, hug, pat, slap tăng điểm Nhẫn Cưới", emoji="✨", value="actions"),
            discord.SelectOption(label="Quản Trị & Cài Đặt", description="Bật/Tắt AutoMod, Level, Setup Server, Sync", emoji="⚙️", value="admin"),
        ]
        super().__init__(placeholder="📂 Chọn danh mục tính năng để xem chi tiết...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        category = self.values[0]
        embed = get_help_embed(category)
        await interaction.response.edit_message(embed=embed, view=self.view)


class HelpView(discord.ui.View):
    """Giao diện View chứa Menu Dropdown chọn danh mục trợ giúp"""

    def __init__(self):
        super().__init__(timeout=180.0)
        self.add_item(HelpSelect())


class General(commands.Cog):
    """Module tính năng chung: Trợ giúp (/help & !help), Cấp độ (/rank), Xếp hạng (/leaderboard) và Cài đặt (/settings)"""

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
        embed = get_help_embed("all")
        view = HelpView()
        await interaction.response.send_message(embed=embed, view=view)

    @commands.command(name="help", description="Xem danh sách đầy đủ tất cả các lệnh (!help)")
    async def help_prefix(self, ctx: commands.Context):
        embed = get_help_embed("all")
        view = HelpView()
        await ctx.reply(embed=embed, view=view, mention_author=False)

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
