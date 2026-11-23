import discord
from discord.ext import commands
import logging
import psutil
import os
import time

logger = logging.getLogger("SosaBot.Admin")

class Admin(commands.Cog):
    """Module quản trị hệ thống dành riêng cho Owner (Chủ Bot): sync lệnh, hot-reload, status"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.start_time = time.time()

    @commands.command(name="sync", description="Đồng bộ Slash Commands tức thì vào Server (!sync hoặc !sync guild)")
    async def sync_commands(self, ctx: commands.Context, scope: str = "guild"):
        """
        Cú pháp:
        !sync         -> Đồng bộ tức thì toàn bộ Slash Commands vào server hiện tại
        !sync guild   -> Tương tự (!sync)
        !sync global  -> Đồng bộ toàn cầu (chỉ dành cho Chủ Bot)
        """
        is_bot_owner = await self.bot.is_owner(ctx.author)
        is_guild_admin = ctx.guild and (ctx.author == ctx.guild.owner or ctx.author.guild_permissions.administrator)

        if not (is_bot_owner or is_guild_admin):
            await ctx.send("⛔ Lệnh này yêu cầu quyền **Quản trị viên (Administrator)** hoặc là **Chủ bot**!")
            return

        if scope.lower() == "global" and not is_bot_owner:
            await ctx.send("⛔ Đồng bộ toàn cầu (`!sync global`) chỉ dành cho Chủ Bot. Bạn hãy gõ `!sync` để đồng bộ cho server này nhé!")
            return

        msg = await ctx.send(f"⏳ Đang đồng bộ Slash Commands phạm vi: `{scope}`...")

        try:
            if scope.lower() == "global":
                synced = await self.bot.tree.sync()
                await msg.edit(content=f"✅ Đã đồng bộ thành công **{len(synced)}** Slash Commands toàn cầu!")
                logger.info(f"Owner {ctx.author} đã đồng bộ toàn cầu {len(synced)} lệnh.")
            else:
                self.bot.tree.copy_global_to(guild=ctx.guild)
                synced = await self.bot.tree.sync(guild=ctx.guild)
                await msg.edit(content=(
                    f"✅ **Đồng bộ thành công {len(synced)} Slash Commands cho máy chủ `{ctx.guild.name}`!**\n"
                    "👉 Bây giờ bạn có thể gõ `/` để thấy đầy đủ tất cả các lệnh của SosaBot."
                ))
                logger.info(f"{ctx.author} đã đồng bộ {len(synced)} lệnh cho Guild {ctx.guild.id}.")
        except Exception as e:
            await msg.edit(content=f"❌ Lỗi đồng bộ: {e}")
            logger.error(f"Lỗi sync lệnh: {e}", exc_info=True)

    @commands.command(name="reload", description="Tải lại module tính năng mà không cần tắt bot")
    @commands.is_owner()
    async def reload_module(self, ctx: commands.Context, extension_name: str):
        """
        Cú pháp:
        !reload cogs.music   -> Nạp lại nhạc mà không làm gián đoạn bot
        !reload cogs.automod -> Cập nhật bộ lọc tức thì
        """
        # Cho phép gõ tắt: 'music' thay vì 'cogs.music'
        if not extension_name.startswith("cogs."):
            extension_name = f"cogs.{extension_name}"

        try:
            await self.bot.reload_extension(extension_name)
            await ctx.send(f"🔄 Đã tải lại thành công module: `{extension_name}`!")
            logger.info(f"Owner {ctx.author} đã hot-reload module {extension_name}.")
        except Exception as e:
            await ctx.send(f"❌ Không thể reload `{extension_name}`: {e}")
            logger.error(f"Lỗi khi reload {extension_name}: {e}", exc_info=True)

    @commands.command(name="status", description="Xem trạng thái phần cứng và hiệu năng bot")
    @commands.is_owner()
    async def show_status(self, ctx: commands.Context):
        """Xem tài nguyên RAM, CPU, Uptime và Database SQLite"""
        process = psutil.Process(os.getpid())
        ram_usage = process.memory_info().rss / 1024 / 1024  # MB
        uptime_seconds = int(time.time() - self.start_time)
        hours, remainder = divmod(uptime_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        embed = discord.Embed(title="📊 Trạng Thái Vận Hành SosaBot", color=discord.Color.green())
        embed.add_field(name="Ping", value=f"{round(self.bot.latency * 1000)}ms", inline=True)
        embed.add_field(name="RAM Sử Dụng", value=f"{ram_usage:.1f} MB", inline=True)
        embed.add_field(name="Thời Gian Hoạt Động", value=f"{hours}h {minutes}m {seconds}s", inline=True)
        embed.add_field(name="Servers Phục Vụ", value=str(len(self.bot.guilds)), inline=True)
        embed.add_field(name="Extensions Đã Nạp", value=str(len(self.bot.extensions)), inline=True)
        embed.add_field(name="Cơ Sở Dữ Liệu", value="SQLite (WAL Mode - aiosqlite)", inline=True)

        await ctx.send(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(Admin(bot))
