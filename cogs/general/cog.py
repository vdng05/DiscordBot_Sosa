import discord
from discord.ext import commands
from discord import app_commands
import logging
from utils.canvas import draw_rank_card

logger = logging.getLogger("SosaGallery.General")

def get_help_embed(category: str = "all", prefix: str = "!") -> discord.Embed:
    """Tạo Embed hướng dẫn lệnh thân thiện, dễ hiểu cho người dùng theo từng danh mục"""
    if category == "music":
        embed = discord.Embed(
            title="🎵 HƯỚNG DẪN NGHE NHẠC (MUSIC)",
            description=(
                "Phát nhạc chất lượng cao từ YouTube, SoundCloud hoặc Spotify.\n\n"
                "💡 **TIỆN LỢI:** Bạn có thể bấm trực tiếp các **Nút Điều Khiển** bên dưới tin nhắn phát nhạc của bot mà không cần phải gõ lệnh!"
            ),
            color=discord.Color.from_rgb(255, 105, 180)
        )
        embed.add_field(
            name="🕹️ 4 Nút Bấm Điều Khiển Nhanh",
            value=(
                "• ⏯️ **Tạm Dừng / Tiếp Tục:** Tạm dừng bài hát đang nghe hoặc tiếp tục phát.\n"
                "• ⏭️ **Chuyển Bài:** Bỏ qua bài hát hiện tại và sang bài tiếp theo trong hàng đợi.\n"
                "• 📜 **Xem Hàng Đợi:** Xem danh sách bài hát đang chờ phát (chỉ bạn nhìn thấy).\n"
                "• ⏹️ **Dừng & Thoát:** Tắt nhạc và mời bot rời khỏi phòng thoại."
            ),
            inline=False
        )
        embed.add_field(
            name="📋 Danh Sách Câu Lệnh",
            value=(
                f"• `{prefix}play <tên bài/link>` (hoặc `/play`, `{prefix}p`): Tìm kiếm và phát bài hát.\n"
                f"• `{prefix}pause` (hoặc `/pause`): Tạm dừng bài hát đang phát.\n"
                f"• `{prefix}resume` (hoặc `/resume`): Tiếp tục phát nhạc.\n"
                f"• `{prefix}skip` (hoặc `/skip`, `{prefix}s`): Chuyển sang bài tiếp theo.\n"
                f"• `{prefix}queue` (hoặc `/queue`, `{prefix}q`): Xem danh sách bài hát đang chờ.\n"
                f"• `{prefix}leave` (hoặc `/leave`, `{prefix}stop`): Yêu cầu bot rời phòng thoại."
            ),
            inline=False
        )
        embed.set_footer(text="SosaGallery • Bot sẽ tự rời phòng sau 5 phút nếu phòng trống người để tiết kiệm tài nguyên.")
        return embed

    elif category == "tts":
        embed = discord.Embed(
            title="🗣️ CHỊ GOOGLE ĐỌC TIN NHẮN (VOICE SAY)",
            description=(
                "Chuyển văn bản tiếng Việt thành giọng nói tự nhiên trong phòng thoại.\n"
                "Rất thích hợp khi bạn đang nghe nhạc hoặc chơi game mà không tiện bật micro!"
            ),
            color=discord.Color.green()
        )
        embed.add_field(
            name="📋 Câu Lệnh",
            value=f"• `{prefix}say <nội dung>` (hoặc `/say`, `{prefix}speak`): Bot sẽ tham gia phòng và đọc to nội dung bạn gõ (tối đa 300 ký tự).",
            inline=False
        )
        embed.add_field(
            name="💡 Cơ Chế Thông Minh",
            value="Nếu bot đang phát nhạc, bot sẽ tự lưu vị trí bài hát, đọc xong câu nói của bạn rồi tự động phát nhạc tiếp tục mượt mà mà không lo bị ngắt quãng hay lỗi xung đột.",
            inline=False
        )
        embed.set_footer(text="SosaGallery • Hỗ trợ đọc cả trong phòng voice lẫn kênh chat văn bản.")
        return embed

    elif category == "rank":
        embed = discord.Embed(
            title="⭐ CẤP ĐỘ & BẢNG XẾP HẠNG (LEVEL & RANK)",
            description="Tích lũy kinh nghiệm mỗi khi bạn trò chuyện trong server để thăng cấp và khoe thẻ hồ sơ cá nhân tuyệt đẹp!",
            color=discord.Color.gold()
        )
        embed.add_field(
            name="📋 Danh Sách Câu Lệnh",
            value=(
                f"• `{prefix}rank [@thành_viên]` (hoặc `/rank`): Xem thẻ thông tin cá nhân hiển thị Cấp độ (Level), Điểm kinh nghiệm (XP) và Thứ hạng máy chủ.\n"
                f"• `{prefix}leaderboard` (hoặc `/leaderboard`): Xem Bảng vàng vinh danh Top 10 thành viên năng nổ nhất máy chủ."
            ),
            inline=False
        )
        embed.add_field(
            name="📈 Cách Tính Điểm (XP)",
            value="Mỗi khi bạn gửi tin nhắn trò chuyện hợp lệ sẽ nhận được từ 15 đến 25 XP (mỗi phút tính điểm một lần để chống spam). Quản trị viên có thể BẬT hoặc TẮT tính năng này trong cài đặt server.",
            inline=False
        )
        embed.set_footer(text="SosaGallery • Dữ liệu cấp độ được lưu trữ an toàn, độc lập cho từng server.")
        return embed

    elif category == "marry":
        embed = discord.Embed(
            title="💘 BÓI TÌNH DUYÊN & KẾT HÔN (LOVE & MARRY)",
            description="Khám phá mức độ tâm đầu ý hợp giữa hai người, cầu hôn người ấy và cùng nhau xây dựng ngôi nhà hạnh phúc!",
            color=discord.Color.pink()
        )
        embed.add_field(
            name="🔮 Bói Tình Duyên (Love Calculator)",
            value=f"• `{prefix}lovec <@người_ấy hoặc tên>` (hoặc `/lovec`): Đo tỷ lệ phần trăm hợp nhau kèm bức ảnh phong cách anime cực xinh xắn!\n*(Mẹo: Gõ `{prefix}lovec random` để bot bốc ngẫu nhiên một người trong server xem bạn có duyên với ai nha)*",
            inline=False
        )
        embed.add_field(
            name="💍 Cầu Hôn & Ngôi Nhà Cặp Đôi",
            value=(
                f"• `{prefix}marry <@người_ấy>` (hoặc `/marry`): Gửi lời cầu hôn ngọt ngào (người ấy có 2 phút để bấm Đồng Ý hoặc Từ Chối).\n"
                f"• `{prefix}marry`: Mở giao diện Ngôi Nhà Cặp Đôi tương tác 3 phần:\n"
                "  - **Trang Chủ:** Xem thông tin hai bạn, ngày cưới và nhẫn cưới.\n"
                "  - **Ảnh & Video:** Lướt xem album 6 bức ảnh kỷ niệm gia đình.\n"
                "  - **Ghi Chú:** Xem ý nghĩa tình yêu và bảng 5 cấp bậc nhẫn cưới.\n"
                f"• `{prefix}name <tên mới>` (hoặc `/marry_name`): Đổi tên cho ngôi nhà của hai bạn.\n"
                f"• `{prefix}quote <câu châm ngôn>` (hoặc `/marry_quote`): Cập nhật câu nói tình yêu cho tổ ấm.\n"
                f"• `{prefix}lgallery <1-6> <link ảnh>` (hoặc `/lgallery`): Tải ảnh kỷ niệm vào 1 trong 6 ô của album.\n"
                f"• `{prefix}divorce` (hoặc `/divorce`): Chia tay và giải phóng ngôi nhà cặp đôi nếu không còn chung đường."
            ),
            inline=False
        )
        embed.set_footer(text="SosaGallery • Tương tác ngọt ngào mỗi ngày để nâng cấp nhẫn cưới lung linh!")
        return embed

    elif category == "actions":
        embed = discord.Embed(
            title="✨ HÀNH ĐỘNG DỄ THƯƠNG & NÂNG CẤP NHẪN CƯỚI",
            description=(
                "Trao cho nhau những cử chỉ ngọt ngào kèm hình ảnh hoạt hình sống động.\n"
                "Đặc biệt: Khi tương tác với bạn đời đã kết hôn, hai bạn sẽ nhận được **+10 Điểm Thân Mật** để cùng nhau nâng cấp nhẫn cưới!"
            ),
            color=discord.Color.purple()
        )
        embed.add_field(
            name="📋 Các Hành Động Thân Mật",
            value=(
                f"• `{prefix}kiss <@thành_viên>` (hoặc `/kiss`): Trao một nụ hôn ngọt ngào.\n"
                f"• `{prefix}hug <@thành_viên>` (hoặc `/hug`): Gửi một cái ôm ấm áp siết chặt.\n"
                f"• `{prefix}pat <@thành_viên>` (hoặc `/pat`): Xoa đầu cưng nựng dễ thương.\n"
                f"• `{prefix}slap <@thành_viên>` (hoặc `/slap`): Tát yêu hoặc đánh thức bạn bè."
            ),
            inline=False
        )
        embed.add_field(
            name="💍 Bảng 5 Cấp Bậc Nhẫn Cưới",
            value=(
                "🌿 **Cấp 1 - Nhẫn Cỏ Thần Tiên:** 0 - 49 điểm\n"
                "🪙 **Cấp 2 - Nhẫn Bạc Thuần Khiết:** 50 - 149 điểm\n"
                "👑 **Cấp 3 - Nhẫn Vàng Vương Giả:** 150 - 299 điểm\n"
                "💎 **Cấp 4 - Nhẫn Kim Cương Vĩnh Cửu:** 300 - 499 điểm\n"
                "🌌 **Cấp 5 - Nhẫn Vô Cực Ngân Hà:** 500+ điểm (Phẩm chất huyền thoại cao quý nhất!)"
            ),
            inline=False
        )
        embed.set_footer(text="SosaGallery • Thời gian chờ giữa mỗi lần cộng điểm thân mật là 30 giây.")
        return embed

    elif category == "admin":
        embed = discord.Embed(
            title="⚙️ QUẢN TRỊ & CÀI ĐẶT MÁY CHỦ (ADMIN)",
            description="Các công cụ quản trị và thiết lập hệ thống dành riêng cho Quản trị viên máy chủ.",
            color=discord.Color.dark_gray()
        )
        embed.add_field(
            name="📋 Danh Sách Lệnh Quản Trị",
            value=(
                f"• `{prefix}prefix [ký_tự_mới]` (hoặc `/settings prefix <ký_tự>`): Xem hoặc đổi tiền tố gõ lệnh của bot trên máy chủ của bạn (Ví dụ đổi thành `$`, `.`, `?`).\n"
                f"• `{prefix}sync`: **Cực kỳ hữu ích!** Đồng bộ ngay lập tức toàn bộ lệnh gạch chéo `/` vào server nếu bạn gõ `/` mà chưa thấy xuất hiện.\n"
                f"• `/settings view`: Xem bảng trạng thái BẬT/TẮT hiện tại của các tính năng tự động trên server.\n"
                f"• `/settings automod <true/false>`: Bật hoặc tắt bộ lọc tự động xóa tin nhắn spam, từ cấm và liên kết rác.\n"
                f"• `/settings level <true/false>`: Bật hoặc tắt tính điểm kinh nghiệm (XP) khi thành viên chat.\n"
                f"• `/setup-server`: Khởi tạo hệ sinh thái danh mục kênh và vai trò mẫu cho server (Chỉ Chủ Server có quyền dùng, có 3 bước xác nhận an toàn)."
            ),
            inline=False
        )
        embed.set_footer(text="SosaGallery • Tất cả tính năng chạy ngầm mặc định TẮT khi bot mới vào server để đảm bảo riêng tư.")
        return embed

    # MẶC ĐỊNH: TỔNG QUAN TẤT CẢ LỆNH
    embed = discord.Embed(
        title="🌸 SOSAGALLERY - HƯỚNG DẪN SỬ DỤNG",
        description=(
            "Chào mừng bạn đến với **SosaGallery**! Dưới đây là tóm tắt toàn bộ tính năng của bot.\n"
            f"Bạn có thể dùng cả **Lệnh Gạch Chéo (`/`)** hoặc gõ **Tiền Tố (`{prefix}`)** phía trước tên lệnh nhé!\n\n"
            f"💡 **Mẹo:** Nếu bạn gõ `/` mà chưa thấy danh sách lệnh, hãy gõ ngay lệnh `{prefix}sync` để bot cập nhật tức thì nha.\n\n"
            "👉 *Hãy chọn danh mục ở Menu bên dưới để xem hướng dẫn chi tiết từng tính năng.*"
        ),
        color=discord.Color.from_rgb(255, 105, 180)
    )

    embed.add_field(
        name="🎵 1. Âm Nhạc (Music)",
        value=f"`{prefix}play`, `{prefix}skip`, `{prefix}queue`, `{prefix}leave`...\n*(Hỗ trợ nút bấm trực tiếp không cần gõ lệnh)*",
        inline=False
    )
    embed.add_field(
        name="🗣️ 2. Chị Google Đọc Tin Nhắn (Voice Say)",
        value=f"`{prefix}say <nội dung>` (hoặc `/say`): Đọc tin nhắn bằng giọng nói trong phòng voice",
        inline=False
    )
    embed.add_field(
        name="⭐ 3. Cấp Độ & Bảng Xếp Hạng (Rank & XP)",
        value=f"`{prefix}rank`: Xem thẻ thông tin cá nhân cực đẹp | `{prefix}leaderboard`: Xem Top 10 server",
        inline=False
    )
    embed.add_field(
        name="💘 4. Bói Tình Duyên & Kết Hôn (Love & Marry)",
        value=f"`{prefix}lovec`: Đo độ hợp đôi anime | `{prefix}marry`: Ngôi nhà cặp đôi 3 tab & album ảnh",
        inline=False
    )
    embed.add_field(
        name="✨ 5. Hành Động Thân Mật (Actions)",
        value=f"`{prefix}kiss`, `{prefix}hug`, `{prefix}pat`, `{prefix}slap` *(+10 Điểm thân mật & nâng cấp 5 bậc Nhẫn Cưới)*",
        inline=False
    )
    embed.add_field(
        name="⚙️ 6. Cài Đặt Máy Chủ (Admin & Settings)",
        value=f"`{prefix}prefix`: Đổi tiền tố lệnh | `/settings`: Bật/Tắt AutoMod & Level | `{prefix}sync`: Cập nhật lệnh",
        inline=False
    )

    embed.set_footer(text=f"SosaGallery • Tiền tố hiện tại: {prefix} • Chọn menu bên dưới để xem chi tiết!")
    return embed


class HelpSelect(discord.ui.Select):
    """Menu chọn danh mục trợ giúp dạng Dropdown"""

    def __init__(self, prefix: str = "!"):
        self.prefix = prefix
        options = [
            discord.SelectOption(label="Tất Cả Tính Năng (Tổng Quan)", description="Xem toàn bộ danh mục và tóm tắt nhanh", emoji="📌", value="all"),
            discord.SelectOption(label="Âm Nhạc (Music)", description="Nghe nhạc YouTube, Spotify cùng các nút điều khiển", emoji="🎵", value="music"),
            discord.SelectOption(label="Đọc Chữ Thành Giọng Nói (Say)", description="Chuyển tin nhắn thành giọng nói trong kênh thoại", emoji="🗣️", value="tts"),
            discord.SelectOption(label="Cấp Độ & Bảng Xếp Hạng (Rank)", description="Xem thẻ hồ sơ cá nhân và top thành viên sôi nổi", emoji="⭐", value="rank"),
            discord.SelectOption(label="Bói Duyên & Kết Hôn (Love & Marry)", description="Bói độ hợp nhau, cưới hỏi và album ảnh gia đình", emoji="💘", value="marry"),
            discord.SelectOption(label="Hành Động Dễ Thương & Nhẫn Cưới", description="Kiss, hug, pat, slap và nâng cấp nhẫn cưới", emoji="✨", value="actions"),
            discord.SelectOption(label="Cài Đặt Máy Chủ (Admin)", description="Đổi tiền tố prefix, bật/tắt tính năng tự động", emoji="⚙️", value="admin"),
        ]
        super().__init__(placeholder="📂 Bấm vào đây để chọn chủ đề bạn muốn xem hướng dẫn...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        category = self.values[0]
        embed = get_help_embed(category, self.prefix)
        await interaction.response.edit_message(embed=embed, view=self.view)


class HelpView(discord.ui.View):
    """Giao diện View chứa Menu Dropdown chọn danh mục trợ giúp"""

    def __init__(self, prefix: str = "!"):
        super().__init__(timeout=180.0)
        self.add_item(HelpSelect(prefix))


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
        current_prefix = await self.bot.db.get_prefix(guild_id)

        automod_status = "🟢 **ĐANG BẬT**" if settings.get("automod_enabled") else "🔴 **ĐANG TẮT (Mặc định)**"
        level_status = "🟢 **ĐANG BẬT**" if settings.get("level_system_enabled") else "🔴 **ĐANG TẮT (Mặc định)**"

        embed = discord.Embed(
            title=f"⚙️ CẤU HÌNH TÍNH NĂNG — {interaction.guild.name}",
            description=(
                "Khi bot mới vào server, các tính năng chạy ngầm đều **mặc định TẮT** để tôn trọng sự riêng tư của server.\n"
                "Quản trị viên có thể dùng các lệnh dưới đây để BẬT hoặc TẮT tùy ý."
            ),
            color=discord.Color.blue()
        )

        embed.add_field(
            name="📌 Tiền Tố Lệnh (Prefix)",
            value=f"Hiện tại: `{current_prefix}`\n*Lệnh đổi:* `/settings prefix <tiền_tố>` hoặc `{current_prefix}prefix <tiền_tố>`",
            inline=False
        )

        embed.add_field(
            name="🛡️ AutoMod (Lọc từ cấm, link rác, chống spam)",
            value=f"Trạng thái: {automod_status}\n*Lệnh đổi:* `/settings automod <true/false>`",
            inline=False
        )

        embed.add_field(
            name="⭐ Hệ Thống Level / Rank (Cộng XP khi chat)",
            value=f"Trạng thái: {level_status}\n*Lệnh đổi:* `/settings level <true/false>`",
            inline=False
        )

        embed.set_footer(text="SosaGallery • Cấu hình được lưu tự động theo từng server")
        await interaction.followup.send(embed=embed, ephemeral=True)

    @settings_group.command(
        name="prefix",
        description="Đổi tiền tố (prefix) gõ lệnh của bot cho máy chủ này"
    )
    @app_commands.describe(
        new_prefix="Nhập tiền tố mới bạn muốn đổi (Ví dụ: $, ., ?, !)"
    )
    @app_commands.default_permissions(manage_guild=True)
    async def settings_prefix(self, interaction: discord.Interaction, new_prefix: str):
        await interaction.response.defer(ephemeral=True)
        if len(new_prefix) > 5 or " " in new_prefix:
            await interaction.followup.send("❌ Tiền tố không được dài quá 5 ký tự và không chứa khoảng trắng!", ephemeral=True)
            return

        await self.bot.db.set_prefix(interaction.guild_id, new_prefix)
        embed = discord.Embed(
            title="⚙️ ĐỔI TIỀN TỐ THÀNH CÔNG",
            description=(
                f"Tiền tố lệnh mới của **SosaGallery** trên máy chủ này là: `{new_prefix}`\n\n"
                f"Ví dụ: `{new_prefix}help`, `{new_prefix}say`, `{new_prefix}play`"
            ),
            color=discord.Color.green()
        )
        logger.info(f"[{interaction.guild.name}] {interaction.user} đã đổi tiền tố thành: {new_prefix}")
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

    @commands.command(name="prefix", description="Xem hoặc đổi tiền tố lệnh (!prefix [kí tự mới])")
    async def prefix_text(self, ctx: commands.Context, new_prefix: str = None):
        current_prefix = await self.bot.db.get_prefix(ctx.guild.id)
        if not new_prefix:
            await ctx.reply(
                f"📌 Tiền tố lệnh hiện tại của bot tại máy chủ này là: `{current_prefix}`\n"
                f"💡 Quản trị viên có thể đổi tiền tố bằng cách gõ: `{current_prefix}prefix <tiền_tố_mới>` (Ví dụ: `{current_prefix}prefix $`)",
                mention_author=False
            )
            return

        if not ctx.author.guild_permissions.manage_guild and not ctx.author.guild_permissions.administrator:
            await ctx.reply("❌ Chỉ Quản trị viên máy chủ mới có quyền thay đổi tiền tố lệnh!", mention_author=False)
            return

        if len(new_prefix) > 5 or " " in new_prefix:
            await ctx.reply("❌ Tiền tố không được dài quá 5 ký tự và không chứa khoảng trắng!", mention_author=False)
            return

        await self.bot.db.set_prefix(ctx.guild.id, new_prefix)
        await ctx.reply(
            f"✅ Đã đổi tiền tố thành công sang `{new_prefix}`!\n"
            f"Bây giờ bạn có thể dùng: `{new_prefix}help`, `{new_prefix}say`, `{new_prefix}play`...",
            mention_author=False
        )

    @app_commands.command(
        name="help",
        description="Xem danh sách đầy đủ tất cả các lệnh và hướng dẫn sử dụng bot"
    )
    async def help_command(self, interaction: discord.Interaction):
        prefix = await self.bot.db.get_prefix(interaction.guild_id)
        embed = get_help_embed("all", prefix)
        view = HelpView(prefix)
        await interaction.response.send_message(embed=embed, view=view)

    @commands.command(name="help", description="Xem danh sách đầy đủ tất cả các lệnh (!help)")
    async def help_prefix(self, ctx: commands.Context):
        prefix = await self.bot.db.get_prefix(ctx.guild.id)
        embed = get_help_embed("all", prefix)
        view = HelpView(prefix)
        await ctx.reply(embed=embed, view=view, mention_author=False)

    @app_commands.command(
        name="rank",
        description="Xem Thẻ Hồ Sơ hiển thị Cấp độ, XP và Thứ hạng của bạn hoặc người khác"
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
            embed = discord.Embed(
                title=f"⭐ HỒ SƠ CẤP ĐỘ — {target.display_name}",
                description=f"Thứ hạng: **#{rank_pos}** | Cấp độ: **{level}** | XP: **{xp:,}** / {needed_xp:,}",
                color=discord.Color.gold()
            )
            embed.set_thumbnail(url=target.display_avatar.url)
            await interaction.followup.send(embed=embed)

    @commands.command(name="rank", description="Xem Thẻ Hồ Sơ Cấp Độ (!rank [@thành_viên])")
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
        description="Xem Bảng vàng Top 10 thành viên có cấp độ cao nhất máy chủ"
    )
    async def leaderboard_command(self, interaction: discord.Interaction):
        await interaction.response.defer()
        guild_id = interaction.guild.id

        top_members = await self.bot.db.get_leaderboard(guild_id, limit=10)

        if not top_members:
            await interaction.followup.send("📭 Bảng xếp hạng hiện tại đang trống. Hãy bắt đầu trò chuyện để tích lũy XP nhé!")
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
        embed.set_footer(text="SosaGallery • Bảng xếp hạng cập nhật tự động theo thời gian thực")

        await interaction.followup.send(embed=embed)

    @commands.command(name="leaderboard", aliases=["lb", "top"], description="Xem Bảng vàng Top 10 (!leaderboard hoặc !top)")
    async def leaderboard_prefix(self, ctx: commands.Context):
        guild_id = ctx.guild.id
        top_members = await self.bot.db.get_leaderboard(guild_id, limit=10)

        if not top_members:
            await ctx.reply("📭 Bảng xếp hạng hiện tại đang trống. Hãy bắt đầu trò chuyện để tích lũy XP nhé!", mention_author=False)
            return

        embed = discord.Embed(
            title=f"🏆 BẢNG VÀNG THÀNH VIÊN — {ctx.guild.name}",
            description="Dưới đây là Top 10 thành viên năng nổ và có cấp độ cao nhất máy chủ:",
            color=discord.Color.purple()
        )

        medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
        lines = []

        for idx, (uid, xp, level) in enumerate(top_members):
            member = ctx.guild.get_member(int(uid))
            name = member.display_name if member else f"Thành viên ({uid})"
            medal = medals[idx] if idx < len(medals) else f"`{idx+1}.`"
            lines.append(f"{medal} **{name}** — Cấp **{level}** `({xp:,} XP)`")

        embed.description += "\n\n" + "\n".join(lines)
        embed.set_footer(text="SosaGallery • Bảng xếp hạng cập nhật tự động theo thời gian thực")

        await ctx.reply(embed=embed, mention_author=False)

async def setup(bot: commands.Bot):
    await bot.add_cog(General(bot))
