import discord
from discord import app_commands
from discord.ext import commands
import logging
import uuid

logger = logging.getLogger("SosaBot.ErrorHandler")

async def global_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    """Bộ xử lý lỗi tập trung cho toàn bộ Slash Commands của Bot"""
    error_id = str(uuid.uuid4())[:8].upper()

    # 1. Người dùng thiếu quyền hạn
    if isinstance(error, app_commands.MissingPermissions):
        missing = ", ".join(f"`{p}`" for p in error.missing_permissions)
        embed = discord.Embed(
            title="⛔ Thiếu Quyền Hạn",
            description=f"Bạn cần có quyền {missing} để thực hiện lệnh này.",
            color=discord.Color.red()
        )
    # 2. Bot thiếu quyền hạn trên Server
    elif isinstance(error, app_commands.BotMissingPermissions):
        missing = ", ".join(f"`{p}`" for p in error.missing_permissions)
        embed = discord.Embed(
            title="⚠️ Bot Thiếu Quyền Hạn",
            description=f"Bot cần được cấp quyền {missing} để hoàn thành lệnh này.",
            color=discord.Color.orange()
        )
    # 3. Lệnh đang trong thời gian chờ (Cooldown)
    elif isinstance(error, app_commands.CommandOnCooldown):
        embed = discord.Embed(
            title="⏳ Lệnh Đang Chờ",
            description=f"Vui lòng thử lại sau **{error.retry_after:.1f}** giây.",
            color=discord.Color.yellow()
        )
    # 4. Kiểm tra điều kiện thất bại (Check Failure)
    elif isinstance(error, app_commands.CheckFailure):
        embed = discord.Embed(
            title="🚫 Truy Cập Bị Từ Chối",
            description="Bạn không đáp ứng đủ điều kiện để thực thi lệnh này.",
            color=discord.Color.red()
        )
    # 5. Các lỗi ngoại lệ chưa xử lý
    else:
        orig = getattr(error, "original", error)
        logger.error(f"[Mã lỗi: {error_id}] Lỗi lệnh /{interaction.command.name if interaction.command else 'Unknown'}: {orig}", exc_info=True)
        embed = discord.Embed(
            title="💥 Đã Xảy Ra Lỗi Hệ Thống",
            description=f"Đã xảy ra sự cố ngoài dự kiến khi thực thi lệnh.\n**Mã tra cứu:** `{error_id}`",
            color=discord.Color.dark_red()
        )

    try:
        if interaction.response.is_done():
            await interaction.followup.send(embed=embed, ephemeral=True)
        else:
            await interaction.response.send_message(embed=embed, ephemeral=True)
    except Exception as e:
        logger.error(f"Không thể gửi thông báo lỗi tới người dùng: {e}")
