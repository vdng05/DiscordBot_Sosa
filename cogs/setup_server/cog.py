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

class SetupServer(commands.Cog):
    """Module tự động thiết lập cấu trúc Server từ file mẫu JSON (templates.json)"""

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
        description="Tự động setup toàn bộ Server theo Template chuẩn từ templates.json"
    )
    @app_commands.describe(
        clear_old="XÓA TOÀN BỘ kênh cũ trước khi setup? (True/False)",
        security_code="Nhập mã xác thực bảo mật cấp cao để thực thi lệnh"
    )
    @app_commands.default_permissions(administrator=True)
    async def setup_server(self, interaction: discord.Interaction, clear_old: bool = False, security_code: str = ""):
        await interaction.response.defer(thinking=True, ephemeral=True)
        guild = interaction.guild

        # LỚP BẢO MẬT 1: CHỈ DUY NHẤT SERVER OWNER MỚI ĐƯỢC CHẠY
        if interaction.user.id != guild.owner_id:
            await interaction.followup.send(
                "❌ Quyền lực tối cao bị từ chối! Chỉ duy nhất **Chủ Server (Server Owner)** mới có thể thực thi lệnh này.",
                ephemeral=True
            )
            return

        # LỚP BẢO MẬT 2: KIỂM TRA MÃ BẢO MẬT MASTER KEY TỪ CONFIG
        if security_code != Config.MASTER_KEY:
            logger.warning(
                f"[{guild.name}] {interaction.user} nhập sai mã bảo mật khi gọi /setup-server!"
            )
            await interaction.followup.send(
                "❌ MÃ BẢO MẬT SAI! Hệ thống đã chặn hành vi thiết lập lại cấu trúc Server này.",
                ephemeral=True
            )
            return

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
                        "**Hệ thống quyền:** Đã phân chia khu vực Public và Private thành công.\n"
                        "**Tốc độ xử lý:** Được điều tiết chống Rate Limit Discord.",
            color=discord.Color.green()
        )
        await interaction.followup.send(embed=embed)
        logger.info(f"[{guild.name}] Hoàn tất setup server thành công.")

async def setup(bot: commands.Bot):
    await bot.add_cog(SetupServer(bot))
