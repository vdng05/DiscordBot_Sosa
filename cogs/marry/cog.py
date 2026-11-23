import discord
from discord.ext import commands
from discord import app_commands
import random
import datetime
import hashlib
import logging
from typing import Optional, Tuple, Dict, Any
from utils.canvas import draw_love_calculator
from utils.database import RING_TIERS
from .views import ProposalView, MarryHouseView

logger = logging.getLogger("SosaGallery.Marry")

# GIF kho hành động anime dễ thương
ACTION_GIFS = {
    "kiss": [
        "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExenFkZG5nbXZhMHNqZmp3ZXNvaDVpMXhjcXB5YjA3dmExMm01b2drZSZlcD12MV9naWZzX3NlYXJjaCZjdD1n/FqBTvSNjNzeZG/giphy.gif",
        "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExenFkZG5nbXZhMHNqZmp3ZXNvaDVpMXhjcXB5YjA3dmExMm01b2drZSZlcD12MV9naWZzX3NlYXJjaCZjdD1n/G3va31oEEnIkM/giphy.gif",
        "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExenFkZG5nbXZhMHNqZmp3ZXNvaDVpMXhjcXB5YjA3dmExMm01b2drZSZlcD12MV9naWZzX3NlYXJjaCZjdD1n/11rWoznEAKPIpa/giphy.gif"
    ],
    "hug": [
        "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExbDVtc2N6am13ZDVwZWZ1M2M1a3h3dTNjc2wzcmZ4eXVyN2ZpOTJodyZlcD12MV9naWZzX3NlYXJjaCZjdD1n/u9BxQbM5bxvwY/giphy.gif",
        "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExbDVtc2N6am13ZDVwZWZ1M2M1a3h3dTNjc2wzcmZ4eXVyN2ZpOTJodyZlcD12MV9naWZzX3NlYXJjaCZjdD1n/od5H3PmEG5EVq/giphy.gif"
    ],
    "pat": [
        "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExNndnOHludnNqbDkxdGhpYm5udXRlZTZ0MXk0MnBscGVudnltMW5kNSZlcD12MV9naWZzX3NlYXJjaCZjdD1n/L2z7dnOduq50Gpn00z/giphy.gif",
        "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExNndnOHludnNqbDkxdGhpYm5udXRlZTZ0MXk0MnBscGVudnltMW5kNSZlcD12MV9naWZzX3NlYXJjaCZjdD1n/5tmRHwTlHAA9WvKBDZ/giphy.gif"
    ],
    "slap": [
        "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExdW40N2FjMDhxdzRycHFod2xrbWJ0MW0wOWl3MXF4NnVld3dpNGZtNCZlcD12MV9naWZzX3NlYXJjaCZjdD1n/Zau0yrl15uzdK/giphy.gif",
        "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExdW40N2FjMDhxdzRycHFod2xrbWJ0MW0wOWl3MXF4NnVld3dpNGZtNCZlcD12MV9naWZzX3NlYXJjaCZjdD1n/jLeyZWgtwWP2U/giphy.gif"
    ]
}


def get_love_quote(pct: int) -> Tuple[str, str, str]:
    """Trả về danh hiệu, đánh giá và lời khuyên dựa trên phần trăm độ hợp"""
    if pct <= 20:
        return "🐸 Hợp làm bạn nhậu hơn là người yêu", "Độ tương thích ở mức báo động 💀", "➡️ Oan gia ngõ hẹp, đi chung khéo đấm nhau đó!"
    elif pct <= 40:
        return "🐸 Hợp làm bạn hơn là người yêu", "Độ tương thích ở mức nhẹ nhẹ", "➡️ Đi ăn chung thì được đó 👀"
    elif pct <= 60:
        return "✨ Trên tình bạn nhưng dưới tình yêu", "Tương thích ở mức khá ổn áp", "➡️ Bật đèn xanh thử xem sao, có triển vọng đấy!"
    elif pct <= 80:
        return "💘 Tâm đầu ý hợp - Cặp đôi hoàn hảo", "Độ hòa hợp cực kỳ cao", "➡️ Mau set quan hệ thôi còn chờ gì nữa!"
    else:
        return "💍 Định mệnh của đời nhau - Trời sinh một cặp", "Tương thích 100% tuyệt đối!", "➡️ Cưới ngay kẻo lỡ, phát cẩu lương cho cả server đi!"


class Marry(commands.Cog):
    """Hệ thống Kết Hôn, Nhà Cặp Đôi, Đo Độ Hợp (Love Calculator) và Tương Tác Thân Mật"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # ==========================
    # LOVE CALCULATOR (/lovec & !lovec)
    # ==========================
    @app_commands.command(
        name="lovec",
        description="Đo mức độ hợp nhau giữa hai người (có hỗ trợ ghép đôi ngẫu nhiên)"
    )
    @app_commands.describe(
        target="Chọn người bạn muốn đo độ hợp (hoặc gõ 'random' để ghép ngẫu nhiên)",
        target2="Chọn người thứ hai nếu bạn muốn gán ghép 2 người khác nhau"
    )
    async def love_calculator_slash(self, interaction: discord.Interaction, target: str = None, target2: discord.Member = None):
        await self.execute_lovec(interaction, target, target2)

    @commands.command(name="lovec", description="Đo độ hợp nhau (lovec <@user|name|ID|random>)")
    async def love_calculator_text(self, ctx: commands.Context, target: str = None, target2: discord.Member = None):
        await self.execute_lovec(ctx, target, target2)

    async def execute_lovec(self, ctx_or_interaction, target_str: Optional[str], target2_member: Optional[discord.Member]):
        is_interaction = isinstance(ctx_or_interaction, discord.Interaction)
        guild = ctx_or_interaction.guild
        author = ctx_or_interaction.user if is_interaction else ctx_or_interaction.author

        # Trả lời đang xử lý
        if is_interaction:
            await ctx_or_interaction.response.defer()
        else:
            await ctx_or_interaction.typing()

        # 1. Xác định 2 đối tượng ghép đôi
        user1 = author
        user2 = None

        # Kiểm tra nếu có target2
        if target2_member:
            user1 = await self.resolve_member(guild, target_str) or author
            user2 = target2_member
        elif target_str:
            if target_str.lower() in ("random", "rd", "ngaunhien"):
                # Ghép ngẫu nhiên với 1 thành viên trong server (không tính bot và chính mình)
                candidates = [m for m in guild.members if not m.bot and m.id != author.id]
                if candidates:
                    user2 = random.choice(candidates)
                else:
                    msg = "❌ Không tìm thấy thành viên phù hợp nào khác trong server để ghép đôi!"
                    return await (ctx_or_interaction.followup.send(msg) if is_interaction else ctx_or_interaction.send(msg))
            else:
                user2 = await self.resolve_member(guild, target_str)

        # Nếu không chọn ai, mặc định ghép ngẫu nhiên
        if not user2:
            candidates = [m for m in guild.members if not m.bot and m.id != author.id]
            if candidates:
                user2 = random.choice(candidates)
            else:
                user2 = author

        # 2. Tính toán phần trăm duyên phận (Thuật toán đối xứng, chống trùng lặp, đổi tỉ lệ theo tuần)
        if user1.id == user2.id:
            percentage = 100
        else:
            # Lấy Năm và Tuần ISO hiện tại (Từ Thứ Hai đến Chủ Nhật cùng 1 tuần sẽ có cùng 1 kết quả duyên phận)
            iso_year, iso_week, _ = datetime.date.today().isocalendar()
            # Ghép ID theo thứ tự min_max để đảm bảo tính đối xứng tuyệt đối (A bói B == B bói A)
            pair_key = f"{min(user1.id, user2.id)}_{max(user1.id, user2.id)}_{iso_year}_w{iso_week}"
            # Sử dụng SHA-256 phân bổ đồng đều ngẫu nhiên từ 1% đến 100% không lo va chạm cộng số
            hash_int = int(hashlib.sha256(pair_key.encode("utf-8")).hexdigest(), 16)
            percentage = (hash_int % 100) + 1

        # Lấy lời bình
        tag_line, desc_line, advice_line = get_love_quote(percentage)

        # 3. Vẽ banner đồ họa qua Canvas (Pillow)
        avatar1_url = user1.display_avatar.with_format("png").url
        avatar2_url = user2.display_avatar.with_format("png").url
        image_buffer = await draw_love_calculator(
            avatar1_url=avatar1_url,
            avatar2_url=avatar2_url,
            user1_name=user1.display_name,
            user2_name=user2.display_name,
            percentage=percentage
        )

        discord_file = discord.File(fp=image_buffer, filename="love_calc.png")

        content_msg = (
            f"**{user1.display_name}** và **{user2.display_name}** có mức độ hợp nhau là **({percentage}%)**\n"
            f"{tag_line}\n"
            f"{desc_line}\n"
            f"{advice_line}"
        )

        if is_interaction:
            await ctx_or_interaction.followup.send(content=content_msg, file=discord_file)
        else:
            await ctx_or_interaction.send(content=content_msg, file=discord_file)

    async def resolve_member(self, guild: discord.Guild, query: str) -> Optional[discord.Member]:
        """Tìm thành viên qua Mention, ID hoặc Tên"""
        if not query:
            return None
        clean_id = query.strip("<@!>")
        if clean_id.isdigit():
            member = guild.get_member(int(clean_id))
            if member:
                return member
        # Tìm theo tên
        for member in guild.members:
            if query.lower() in member.name.lower() or query.lower() in member.display_name.lower():
                return member
        return None

    # ==========================
    # HỆ THỐNG KẾT HÔN (/marry & !marry)
    # ==========================
    @app_commands.command(
        name="marry",
        description="Cầu hôn một người bạn yêu thích hoặc mở xem Ngôi Nhà Cặp Đôi của bạn"
    )
    @app_commands.describe(
        partner="Chọn người bạn muốn cầu hôn (để trống nếu muốn mở xem Ngôi Nhà của bạn)"
    )
    async def marry_slash(self, interaction: discord.Interaction, partner: Optional[discord.Member] = None):
        await self.execute_marry(interaction, partner)

    @commands.command(name="marry", description="Cầu hôn hoặc xem nhà marry (!marry [@user])")
    async def marry_text(self, ctx: commands.Context, partner: Optional[discord.Member] = None):
        await self.execute_marry(ctx, partner)

    async def execute_marry(self, ctx_or_interaction, partner: Optional[discord.Member]):
        is_interaction = isinstance(ctx_or_interaction, discord.Interaction)
        guild = ctx_or_interaction.guild
        author = ctx_or_interaction.user if is_interaction else ctx_or_interaction.author

        # Trường hợp 1: Người dùng muốn cầu hôn ai đó
        if partner:
            if partner.id == author.id:
                msg = "❌ Bạn không thể tự kết hôn với chính mình được!"
                return await (ctx_or_interaction.response.send_message(msg, ephemeral=True) if is_interaction else ctx_or_interaction.send(msg))
            if partner.bot:
                msg = "❌ Bot không thể kết hôn với bạn được đâu nha!"
                return await (ctx_or_interaction.response.send_message(msg, ephemeral=True) if is_interaction else ctx_or_interaction.send(msg))

            # Kiểm tra xem ai đã cưới chưa
            mar_author = await self.bot.db.get_marriage(guild.id, author.id)
            if mar_author:
                msg = "❌ Bạn đã có gia đình trong server này rồi! Hãy ly hôn trước nếu muốn đi bước nữa."
                return await (ctx_or_interaction.response.send_message(msg, ephemeral=True) if is_interaction else ctx_or_interaction.send(msg))

            mar_partner = await self.bot.db.get_marriage(guild.id, partner.id)
            if mar_partner:
                msg = f"❌ **{partner.display_name}** đã kết hôn với người khác trong server này rồi!"
                return await (ctx_or_interaction.response.send_message(msg, ephemeral=True) if is_interaction else ctx_or_interaction.send(msg))

            # Gửi lời cầu hôn kèm nút tương tác
            view = ProposalView(proposer=author, target=partner, bot=self.bot)
            embed = discord.Embed(
                title="💍 LỜI CẦU HÔN LÃNG MẠN",
                description=(
                    f"💖 **{author.mention}** đã quỳ gối trao nhẫn và cầu hôn **{partner.mention}**!\n\n"
                    f"*\"{partner.display_name} à, bạn có đồng ý cùng mình xây dựng một Ngôi Nhà Hạnh Phúc không?\"*\n\n"
                    "👉 **Hãy chọn câu trả lời bằng 2 nút bấm bên dưới (Thời hạn 2 phút):**"
                ),
                color=discord.Color.pink()
            )
            embed.set_thumbnail(url=author.display_avatar.url)

            if is_interaction:
                await ctx_or_interaction.response.send_message(embed=embed, view=view)
            else:
                await ctx_or_interaction.send(embed=embed, view=view)
            return

        # Trường hợp 2: Xem ngôi nhà marry của chính mình
        marriage = await self.bot.db.get_marriage(guild.id, author.id)
        if not marriage:
            msg = "💔 Bạn hiện tại chưa kết hôn với ai! Hãy dùng `/marry <@user>` để tìm kiếm một nửa của mình."
            return await (ctx_or_interaction.response.send_message(msg, ephemeral=True) if is_interaction else ctx_or_interaction.send(msg))

        # Hiển thị Ngôi Nhà Marry với 3 Tab
        view = MarryHouseView(marriage=marriage, guild=guild, bot=self.bot, current_tab="home")
        embed = view.build_home_embed()

        if is_interaction:
            await ctx_or_interaction.response.send_message(embed=embed, view=view)
        else:
            await ctx_or_interaction.send(embed=embed, view=view)

    # ==========================
    # CÁC LỆNH PHỤ MARRY (Đổi tên, đổi quote, thư viện ảnh)
    # ==========================
    @app_commands.command(name="marry_name", description="Đổi tên ngôi nhà marry của hai bạn")
    @app_commands.describe(new_name="Tên mới cho ngôi nhà cặp đôi")
    async def marry_name_slash(self, interaction: discord.Interaction, new_name: str):
        success = await self.bot.db.update_house_name(interaction.guild_id, interaction.user.id, new_name.strip())
        if success:
            await interaction.response.send_message(f"🏡 Đã đổi tên nhà thành công: **{new_name.strip()}**!")
        else:
            await interaction.response.send_message("❌ Bạn chưa có gia đình trong server để đổi tên nhà!", ephemeral=True)

    @commands.command(name="name", description="Đổi tên nhà marry (!name <tên mới>)")
    async def marry_name_text(self, ctx: commands.Context, *, new_name: str):
        success = await self.bot.db.update_house_name(ctx.guild.id, ctx.author.id, new_name.strip())
        if success:
            await ctx.send(f"🏡 Đã đổi tên nhà thành công: **{new_name.strip()}**!")
        else:
            await ctx.send("❌ Bạn chưa có gia đình trong server để đổi tên nhà!")

    @app_commands.command(name="marry_quote", description="Đổi câu châm ngôn tình yêu cho ngôi nhà của bạn")
    @app_commands.describe(new_quote="Nội dung lời nhắn hoặc câu trích dẫn mới")
    async def marry_quote_slash(self, interaction: discord.Interaction, new_quote: str):
        success = await self.bot.db.update_house_quote(interaction.guild_id, interaction.user.id, new_quote.strip())
        if success:
            await interaction.response.send_message(f"💬 Đã cập nhật châm ngôn nhà: *\"{new_quote.strip()}\"*")
        else:
            await interaction.response.send_message("❌ Bạn chưa có gia đình trong server để đổi câu trích dẫn!", ephemeral=True)

    @commands.command(name="quote", description="Đổi quote nhà marry (!quote <lời nhắn>)")
    async def marry_quote_text(self, ctx: commands.Context, *, new_quote: str):
        success = await self.bot.db.update_house_quote(ctx.guild.id, ctx.author.id, new_quote.strip())
        if success:
            await ctx.send(f"💬 Đã cập nhật châm ngôn nhà: *\"{new_quote.strip()}\"*")
        else:
            await ctx.send("❌ Bạn chưa có gia đình trong server để đổi câu trích dẫn!")

    @app_commands.command(name="lgallery", description="Thêm hoặc cập nhật ảnh vào thư viện của nhà marry (slot 1-6)")
    @app_commands.describe(
        slot="Chọn vị trí ô ảnh từ 1 đến 6",
        image_url="Đường link hình ảnh (URL)"
    )
    async def lgallery_slash(self, interaction: discord.Interaction, slot: int, image_url: str):
        if slot < 1 or slot > 6:
            return await interaction.response.send_message("❌ Vị trí ô ảnh chỉ từ 1 đến 6!", ephemeral=True)

        success = await self.bot.db.update_gallery_slot(interaction.guild_id, interaction.user.id, slot, image_url.strip())
        if success:
            await interaction.response.send_message(f"🖼️ Đã lưu ảnh vào ô số **{slot}** trong Thư viện ảnh thành công!")
        else:
            await interaction.response.send_message("❌ Bạn chưa kết hôn nên không thể dùng thư viện ảnh cặp đôi!", ephemeral=True)

    @commands.command(name="lgallery", description="Thêm ảnh vào thư viện (!lgallery <1-6> <link>)")
    async def lgallery_text(self, ctx: commands.Context, slot: int, image_url: str):
        if slot < 1 or slot > 6:
            return await ctx.send("❌ Vị trí ô ảnh chỉ từ 1 đến 6!")

        success = await self.bot.db.update_gallery_slot(ctx.guild.id, ctx.author.id, slot, image_url.strip())
        if success:
            await ctx.send(f"🖼️ Đã lưu ảnh vào ô số **{slot}** trong Thư viện ảnh thành công!")
        else:
            await ctx.send("❌ Bạn chưa kết hôn nên không thể dùng thư viện ảnh cặp đôi!")

    @app_commands.command(name="divorce", description="Ly hôn và xóa Ngôi Nhà Cặp Đôi hiện tại")
    async def divorce_slash(self, interaction: discord.Interaction):
        success = await self.bot.db.divorce(interaction.guild_id, interaction.user.id)
        if success:
            await interaction.response.send_message("💔 Bạn đã chính thức ly hôn. Ngôi nhà và dữ liệu cặp đôi đã được giải phóng.")
        else:
            await interaction.response.send_message("❌ Bạn hiện đang độc thân, không có cuộc hôn nhân nào để ly hôn!", ephemeral=True)

    @commands.command(name="divorce", description="Ly hôn (!divorce)")
    async def divorce_text(self, ctx: commands.Context):
        success = await self.bot.db.divorce(ctx.guild.id, ctx.author.id)
        if success:
            await ctx.send("💔 Bạn đã chính thức ly hôn. Ngôi nhà và dữ liệu cặp đôi đã được giải phóng.")
        else:
            await ctx.send("❌ Bạn hiện đang độc thân, không có cuộc hôn nhân nào để ly hôn!")

    # ==========================
    # CÁC LỆNH TƯƠNG TÁC TĂNG ĐIỂM THÂN MẬT (kiss, hug, pat, slap)
    # ==========================
    async def handle_interaction_action(self, ctx_or_interaction, action_type: str, target: discord.Member):
        is_interaction = isinstance(ctx_or_interaction, discord.Interaction)
        author = ctx_or_interaction.user if is_interaction else ctx_or_interaction.author
        guild = ctx_or_interaction.guild

        if target.id == author.id:
            msg = "Bạn tự làm điều đó với chính mình sao? Tự yêu bản thân cũng tốt đấy! 😄"
            return await (ctx_or_interaction.response.send_message(msg, ephemeral=True) if is_interaction else ctx_or_interaction.send(msg))

        gifs = ACTION_GIFS.get(action_type, ACTION_GIFS["hug"])
        gif_url = random.choice(gifs)

        action_names = {
            "kiss": "trao nụ hôn ngọt ngào cho",
            "hug": "ôm thật chặt",
            "pat": "xoa đầu cưng nựng",
            "slap": "phát yêu / tát vui vẻ"
        }
        verb = action_names.get(action_type, "tương tác với")

        # Kiểm tra nếu tương tác với người bạn đời đã cưới -> Cộng điểm thân mật!
        marriage = await self.bot.db.get_marriage(guild.id, author.id)
        intimacy_msg = ""

        if marriage and marriage["partner_id"] == str(target.id):
            success, new_points, ring_tier, tier_up = await self.bot.db.add_intimacy(guild.id, author.id, points=10)
            if success:
                ring_info = RING_TIERS.get(ring_tier, RING_TIERS[1])
                intimacy_msg = f"\n\n💖 **Điểm thân mật tăng:** `+10` (Hiện tại: **{new_points}** điểm)\n💍 **Nhẫn:** {ring_info['name']}"
                if tier_up:
                    intimacy_msg += f"\n🎉 **CHÚC MỪNG!** Nhẫn của hai bạn đã được nâng cấp lên **{ring_info['name']}**!"
            else:
                intimacy_msg = f"\n*(Điểm thân mật đang trong thời gian chờ 30s giữa các lần tương tác)*"

        embed = discord.Embed(
            description=f"✨ **{author.display_name}** đã {verb} **{target.display_name}**!{intimacy_msg}",
            color=discord.Color.pink() if action_type in ("kiss", "hug") else discord.Color.orange()
        )
        embed.set_image(url=gif_url)

        if is_interaction:
            await ctx_or_interaction.response.send_message(embed=embed)
        else:
            await ctx_or_interaction.send(embed=embed)

    @app_commands.command(name="kiss", description="Trao nụ hôn ngọt ngào (Tăng điểm thân mật nếu đã kết hôn)")
    @app_commands.describe(member="Người bạn muốn hôn")
    async def kiss_slash(self, interaction: discord.Interaction, member: discord.Member):
        await self.handle_interaction_action(interaction, "kiss", member)

    @commands.command(name="kiss")
    async def kiss_text(self, ctx: commands.Context, member: discord.Member):
        await self.handle_interaction_action(ctx, "kiss", member)

    @app_commands.command(name="hug", description="Trao cái ôm ấm áp (Tăng điểm thân mật nếu đã kết hôn)")
    @app_commands.describe(member="Người bạn muốn ôm")
    async def hug_slash(self, interaction: discord.Interaction, member: discord.Member):
        await self.handle_interaction_action(interaction, "hug", member)

    @commands.command(name="hug")
    async def hug_text(self, ctx: commands.Context, member: discord.Member):
        await self.handle_interaction_action(ctx, "hug", member)

    @app_commands.command(name="pat", description="Xoa đầu cưng nựng (Tăng điểm thân mật nếu đã kết hôn)")
    @app_commands.describe(member="Người bạn muốn xoa đầu")
    async def pat_slash(self, interaction: discord.Interaction, member: discord.Member):
        await self.handle_interaction_action(interaction, "pat", member)

    @commands.command(name="pat")
    async def pat_text(self, ctx: commands.Context, member: discord.Member):
        await self.handle_interaction_action(ctx, "pat", member)

    @app_commands.command(name="slap", description="Tát yêu / đánh thức người ấy (Tăng điểm thân mật nếu đã kết hôn)")
    @app_commands.describe(member="Người bạn muốn tát yêu")
    async def slap_slash(self, interaction: discord.Interaction, member: discord.Member):
        await self.handle_interaction_action(interaction, "slap", member)

    @commands.command(name="slap")
    async def slap_text(self, ctx: commands.Context, member: discord.Member):
        await self.handle_interaction_action(ctx, "slap", member)

async def setup(bot: commands.Bot):
    await bot.add_cog(Marry(bot))
