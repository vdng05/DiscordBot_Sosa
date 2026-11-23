import json
from pathlib import Path
import asyncio
import logging
import discord
from discord.ext import commands
from discord import app_commands

logger = logging.getLogger("SosaBot.SetupServer")
TEMPLATE_PATH = Path(__file__).resolve().parent / "templates.json"


class ConfirmationStepView(discord.ui.View):
    """Giao diện xác nhận tương tác nhiều bước (3-Step Confirmation) dành riêng cho Chủ Server"""

    def __init__(self, cog: "SetupServer", owner_id: int, clear_old: bool, current_step: int = 1):
        super().__init__(timeout=60.0)
        self.cog = cog
        self.owner_id = owner_id
        self.clear_old = clear_old
        self.current_step = current_step
        self.confirmed = False

        # Cấu hình nút theo từng bước
        self.update_buttons()

    def update_buttons(self):
        self.clear_items()

        if self.current_step == 1:
            next_btn = discord.ui.Button(
                label="👉 Tiếp Tục Sang Bước 2",
                style=discord.ButtonStyle.primary,
                custom_id="step_next"
            )
            next_btn.callback = self.handle_next
            self.add_item(next_btn)

        elif self.current_step == 2:
            next_btn = discord.ui.Button(
                label="⚠️ Tôi Hiểu Rủi Ro - Sang Bước Cuối",
                style=discord.ButtonStyle.danger,
                custom_id="step_next"
            )
            next_btn.callback = self.handle_next
            self.add_item(next_btn)

        elif self.current_step == 3:
            final_btn = discord.ui.Button(
                label="🛑 XÁC NHẬN 100% - THIẾT LẬP SERVER NGAY",
                style=discord.ButtonStyle.danger,
                custom_id="step_final"
            )
            final_btn.callback = self.handle_final
            self.add_item(final_btn)

        # Nút Hủy Bỏ luôn có sẵn ở mọi bước
        cancel_btn = discord.ui.Button(
            label="❌ Hủy Bỏ Toàn Bộ",
            style=discord.ButtonStyle.secondary,
            custom_id="step_cancel"
        )
        cancel_btn.callback = self.handle_cancel
        self.add_item(cancel_btn)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """Đảm bảo chỉ DUY NHẤT Chủ Server mới có quyền bấm các nút này"""
        if interaction.user.id != self.owner_id:
            await interaction.response.send_message(
                "⛔ Bạn không phải là **Chủ Server**! Chỉ có Chủ Server mới được phép thao tác nút này.",
                ephemeral=True
            )
            return False
        return True

    async def handle_next(self, interaction: discord.Interaction):
        self.current_step += 1
        self.update_buttons()

        if self.current_step == 2:
            embed = discord.Embed(
                title="🚨 CẢNH BÁO BƯỚC 2/3: NGUY CƠ MẤT DỮ LIỆU KHÔNG THỂ KHÔI PHỤC",
                description=(
                    "**Vui lòng đọc thật kỹ trước khi tiếp tục:**\n\n"
                    f"• **Chế độ xóa kênh cũ:** `{'BẬT (Xóa sạch toàn bộ kênh)' if self.clear_old else 'TẮT (Giữ nguyên kênh cũ)'}`\n"
                    "• Nếu bật xóa kênh cũ, **mọi tin nhắn, hình ảnh và lịch sử chat cũ sẽ biến mất vĩnh viễn** và không thể hoàn tác.\n"
                    "• Các vai trò `Admin`, `Member` sẽ được tạo mới và phân chia quyền Public / Private theo template.\n\n"
                    "👉 **Bạn đã lưu trữ các dữ liệu cần thiết và sẵn sàng tiếp tục?**"
                ),
                color=discord.Color.red()
            )
            embed.set_footer(text="Hết hạn sau 60 giây nếu không tương tác.")
            await interaction.response.edit_message(embed=embed, view=self)

        elif self.current_step == 3:
            embed = discord.Embed(
                title="🛑 XÁC NHẬN TỐI HẬU BƯỚC 3/3: BẮT ĐẦU THỰC THI",
                description=(
                    "**ĐÂY LÀ BƯỚC CUỐI CÙNG!**\n\n"
                    "Khi bạn nhấn nút xác nhận bên dưới:\n"
                    "1. Hệ thống sẽ bắt đầu khởi tạo toàn bộ cấu trúc máy chủ tự động.\n"
                    "2. Quá trình này sẽ mất khoảng 10-30 giây tùy số lượng kênh (có điều tiết chống Rate Limit Discord).\n"
                    "3. Trong lúc chạy, vui lòng không xóa kênh hay ngắt kết nối bot.\n\n"
                    "👉 **Bạn có chắc chắn 100% muốn thực hiện việc này ngay bây giờ?**"
                ),
                color=discord.Color.dark_red()
            )
            embed.set_footer(text="Hết hạn sau 60 giây nếu không tương tác.")
            await interaction.response.edit_message(embed=embed, view=self)

    async def handle_final(self, interaction: discord.Interaction):
        self.confirmed = True
        self.clear_items()
        
        embed = discord.Embed(
            title="⏳ ĐANG THỰC THI THIẾT LẬP SERVER...",
            description="Đã xác nhận đầy đủ 3 bước! Bot đang bắt đầu xây dựng lại cấu trúc server của bạn. Vui lòng đợi trong giây lát...",
            color=discord.Color.gold()
        )
        await interaction.response.edit_message(embed=embed, view=None)
        self.stop()
        await self.cog.execute_setup(interaction, self.clear_old)

    async def handle_cancel(self, interaction: discord.Interaction):
        self.clear_items()
        embed = discord.Embed(
            title="🛡️ ĐÃ HỦY THAO TÁC AN TOÀN",
            description="Bạn đã hủy bỏ lệnh thiết lập Server. Cấu trúc và dữ liệu hiện tại của Server được giữ nguyên 100%.",
            color=discord.Color.green()
        )
        await interaction.response.edit_message(embed=embed, view=None)
        self.stop()

    async def on_timeout(self):
        """Khóa nút nếu quá 60 giây không phản hồi"""
        self.clear_items()


class SetupServer(commands.Cog):
    """Module tự động thiết lập cấu trúc Server từ file mẫu JSON với quy trình 3 bước xác thực nghiêm ngặt"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def load_template(self) -> dict:
        """Đọc template từ file templates.json"""
        try:
            if TEMPLATE_PATH.exists():
                with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Lỗi khi đọc templates.json: {e}")
        return {}

    @app_commands.command(
        name="setup-server",
        description="Khởi tạo toàn bộ danh mục, kênh và quyền theo mẫu chuẩn (Chỉ dành cho Chủ Server)"
    )
    @app_commands.describe(
        clear_old="Chọn True nếu muốn xóa sạch các kênh cũ trước khi tạo mẫu mới, False để giữ lại kênh cũ"
    )
    @app_commands.default_permissions(administrator=True)
    async def setup_server_command(self, interaction: discord.Interaction, clear_old: bool = False):
        guild = interaction.guild

        # 1. KIỂM TRA QUYỀN LỰC TỐI CAO: CHỈ DUY NHẤT CHỦ SERVER MỚI ĐƯỢC CHẠY
        if interaction.user.id != guild.owner_id:
            await interaction.response.send_message(
                "❌ **Quyền lực tối cao bị từ chối!**\n"
                "Lệnh này có khả năng thay đổi toàn bộ cấu trúc máy chủ, chỉ duy nhất **Chủ Server (Server Owner)** mới có quyền thực thi.",
                ephemeral=True
            )
            return

        # 2. BẮT ĐẦU QUY TRÌNH XÁC THỰC 3 BƯỚC (BƯỚC 1/3)
        view = ConfirmationStepView(cog=self, owner_id=guild.owner_id, clear_old=clear_old, current_step=1)

        embed = discord.Embed(
            title="⚠️ CẢNH BÁO BƯỚC 1/3: BẠN ĐANG YÊU CẦU THIẾT LẬP LẠI TOÀN BỘ SERVER",
            description=(
                f"Xin chào **{interaction.user.display_name}** (Chủ sở hữu máy chủ `{guild.name}`),\n\n"
                "Bạn vừa yêu cầu khởi chạy tính năng thiết lập cấu trúc tự động theo template:\n"
                "• **Danh mục sẽ tạo:** THÔNG TIN CHUNG, STAFF, CHAT, VUI VẺ, ROOM ADMIN, PHÒNG TIẾP KHÁCH.\n"
                "• **Vai trò (Role) sẽ tạo:** `Admin` (Đỏ - Toàn quyền), `Member` (Xanh - Thành viên).\n"
                f"• **Chế độ xóa kênh cũ:** **`{'BẬT (Sẽ xóa toàn bộ kênh)' if clear_old else 'TẮT (Giữ lại kênh cũ)'}`**.\n\n"
                "👉 Để bảo vệ server khỏi các thao tác nhầm lẫn, hệ thống yêu cầu bạn xác nhận qua **3 bước cảnh báo**.\n"
                "Nhấn **'Tiếp Tục Sang Bước 2'** nếu bạn hiểu và muốn tiếp tục, hoặc nhấn **'Hủy Bỏ'** để dừng lại."
            ),
            color=discord.Color.gold()
        )
        embed.set_footer(text="Bước 1 trên 3 • Chỉ có bạn mới có thể nhấn nút")
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    async def execute_setup(self, interaction: discord.Interaction, clear_old: bool):
        """Thực thi tạo kênh và phân quyền với cơ chế chống Rate Limit 429"""
        guild = interaction.guild
        server_template = self.load_template()

        if not server_template:
            await interaction.followup.send(
                "❌ Lỗi: Không tìm thấy hoặc file `templates.json` bị lỗi cấu trúc!",
                ephemeral=True
            )
            return

        logger.info(f"[{guild.name}] Bắt đầu thực thi /setup-server bởi Chủ Server {interaction.user}")

        # 1. TÙY CHỌN XÓA KÊNH CŨ (Có độ trễ 0.3s tránh Rate Limit 429)
        if clear_old:
            for channel in list(guild.channels):
                if channel.id != interaction.channel_id:
                    try:
                        await channel.delete(reason="Reset server theo template bởi Chủ Server")
                        await asyncio.sleep(0.3)
                    except (discord.NotFound, discord.Forbidden, discord.HTTPException) as e:
                        logger.warning(f"Không thể xóa kênh {channel.name}: {e}")
            await asyncio.sleep(1)

        # 2. KHỞI TẠO ROLE CƠ BẢN
        admin_role = discord.utils.get(guild.roles, name="Admin")
        if not admin_role:
            try:
                admin_role = await guild.create_role(
                    name="Admin",
                    permissions=discord.Permissions(administrator=True),
                    color=discord.Color.red()
                )
            except discord.HTTPException as e:
                logger.warning(f"Không thể tạo role Admin: {e}")

        member_role = discord.utils.get(guild.roles, name="Member")
        if not member_role:
            try:
                member_role = await guild.create_role(
                    name="Member",
                    color=discord.Color.blue()
                )
            except discord.HTTPException as e:
                logger.warning(f"Không thể tạo role Member: {e}")

        # 3. ĐỊNH NGHĨA QUYỀN HẠN
        everyone = guild.default_role
        admin_target = admin_role or everyone
        permission_map = {
            "read_only": {
                everyone: discord.PermissionOverwrite(read_messages=True, send_messages=False),
                admin_target: discord.PermissionOverwrite(read_messages=True, send_messages=True)
            },
            "private": {
                everyone: discord.PermissionOverwrite(read_messages=False, connect=False),
                admin_target: discord.PermissionOverwrite(read_messages=True, send_messages=True, connect=True)
            },
            "public": {
                everyone: discord.PermissionOverwrite(read_messages=True, send_messages=True, connect=True)
            }
        }

        # 4. TỰ ĐỘNG TẠO CATEGORY VÀ KÊNH TỪ TEMPLATE JSON
        for cat_name, cat_data in server_template.items():
            perm_type = cat_data.get("permission", "public")
            overwrites = permission_map.get(perm_type, permission_map["public"])

            try:
                category = await guild.create_category(name=cat_name, overwrites=overwrites)
                await asyncio.sleep(0.3)

                for ch in cat_data.get("channels", []):
                    if ch["type"] == "text":
                        await guild.create_text_channel(name=ch["name"], category=category)
                    elif ch["type"] == "voice":
                        await guild.create_voice_channel(name=ch["name"], category=category)
                    await asyncio.sleep(0.3)
            except discord.HTTPException as e:
                logger.error(f"Lỗi khi tạo category {cat_name}: {e}")

        # 5. THÔNG BÁO HOÀN TẤT
        embed = discord.Embed(
            title="🎉 HOÀN TẤT THIẾT LẬP SERVER THÀNH CÔNG!",
            description=(
                "Bot đã khởi tạo xong toàn bộ cấu trúc máy chủ chuẩn cho bạn:\n\n"
                "✅ **Danh mục & Kênh:** Đã tạo đầy đủ các phòng Chat, Voice, Staff và Thông tin.\n"
                "✅ **Vai trò:** Đã tạo `Admin` (Toàn quyền) và `Member` (Thành viên).\n"
                "✅ **Bảo mật phân quyền:** Các khu vực nhạy cảm (Staff, Admin Room) được khóa riêng tư an toàn.\n"
                "✅ **An toàn hệ thống:** Đã vượt qua 3 lần xác thực từ chính Chủ Server."
            ),
            color=discord.Color.green()
        )
        await interaction.followup.send(embed=embed, ephemeral=True)
        logger.info(f"[{guild.name}] Hoàn tất setup server thành công bởi Chủ Server.")

async def setup(bot: commands.Bot):
    await bot.add_cog(SetupServer(bot))
