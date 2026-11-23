import json
from pathlib import Path
import asyncio
import logging
import discord
from discord.ext import commands
from discord import app_commands
from config import Config

logger = logging.getLogger("SosaBot.SetupServer")
TEMPLATE_PATH = Path(__file__).resolve().parent / "templates.json"

class SetupSecurityModal(discord.ui.Modal, title="Xác Thực Thiết Lập Server Cấp Cao"):
    """Modal giao diện hộp thoại nhập mã bảo mật (Ẩn hoàn toàn khỏi kênh chat công khai)"""

    passcode = discord.ui.TextInput(
        label="Mã Bảo Mật Cấp Cao (Master Key)",
        placeholder="Nhập mã bảo mật để kích hoạt thiết lập cấu trúc...",
        required=True,
        style=discord.TextStyle.short
    )

    def __init__(self, cog: "SetupServer", interaction: discord.Interaction, clear_old: bool):
        super().__init__()
        self.cog = cog
        self.original_interaction = interaction
        self.clear_old = clear_old

    async def on_submit(self, interaction: discord.Interaction):
        # Kiểm tra mã bảo mật từ Config
        if self.passcode.value.strip() != Config.MASTER_KEY:
            logger.warning(f"[{interaction.guild.name}] {interaction.user} nhập sai mã bảo mật trên Modal!")
            await interaction.response.send_message(
                "❌ MÃ BẢO MẬT KHÔNG CHÍNH XÁC! Hành động đã bị chặn.",
                ephemeral=True
            )
            return

        # Thực thi quy trình thiết lập server an toàn
        await interaction.response.defer(thinking=True, ephemeral=True)
        await self.cog.execute_setup(interaction, self.clear_old)


class SetupServer(commands.Cog):
    """Module tự động thiết lập cấu trúc Server từ file mẫu JSON (templates.json) với bảo mật Modal"""

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
        description="Tự động setup toàn bộ Server theo Template chuẩn (Bảo mật qua hộp thoại Modal)"
    )
    @app_commands.describe(
        clear_old="XÓA TOÀN BỘ kênh cũ trước khi setup? (True/False)"
    )
    @app_commands.default_permissions(administrator=True)
    async def setup_server_command(self, interaction: discord.Interaction, clear_old: bool = False):
        guild = interaction.guild

        # LỚP BẢO MẬT 1: CHỈ DUY NHẤT SERVER OWNER MỚI ĐƯỢC PHÉP CHẠY
        if interaction.user.id != guild.owner_id:
            await interaction.response.send_message(
                "❌ Quyền lực tối cao bị từ chối! Chỉ duy nhất **Chủ Server (Server Owner)** mới có thể thực thi lệnh này.",
                ephemeral=True
            )
            return

        # LỚP BẢO MẬT 2: BẬT MODAL HỘP THOẠI ĐỂ NHẬP MẬT MÃ (KHÔNG LỘ MẬT KHẨU TRÊN THANH LỆNH)
        modal = SetupSecurityModal(cog=self, interaction=interaction, clear_old=clear_old)
        await interaction.response.send_modal(modal)

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

        logger.info(f"[{guild.name}] Bắt đầu thực thi /setup-server bởi Owner {interaction.user}")

        # 1. TÙY CHỌN XÓA KÊNH CŨ (Có độ trễ tránh Rate Limit 429)
        if clear_old:
            for channel in list(guild.channels):
                if channel.id != interaction.channel_id:
                    try:
                        await channel.delete(reason="Reset server theo template")
                        await asyncio.sleep(0.3)  # Giảm tải Discord API Rate Limit
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

        # 4. TỰ ĐỘNG TẠO CATEGORY VÀ KÊNH TỪ TEMPLATE JSON (Có độ trễ chống Rate Limit)
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
            title="✅ HOÀN TẤT SETUP SERVER",
            description="Bot đã tạo xong toàn bộ cấu trúc từ file mẫu `templates.json`!\n\n"
                        "**Roles:** `Admin`, `Member`\n"
                        "**Hệ thống quyền:** Phân chia khu vực Public/Private thành công.\n"
                        "**Bảo mật:** Mã xác thực được bảo vệ an toàn qua hộp thoại Discord Modal.",
            color=discord.Color.green()
        )
        await interaction.followup.send(embed=embed)
        logger.info(f"[{guild.name}] Hoàn tất setup server thành công.")

async def setup(bot: commands.Bot):
    await bot.add_cog(SetupServer(bot))
