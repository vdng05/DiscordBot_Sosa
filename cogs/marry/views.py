import discord
from discord.ext import commands
import datetime
from utils.database import RING_TIERS

class ProposalView(discord.ui.View):
    """Giao diện cầu hôn tương tác với 2 nút: Đồng ý hoặc Từ chối"""

    def __init__(self, proposer: discord.Member, target: discord.Member, bot: commands.Bot):
        super().__init__(timeout=120.0)
        self.proposer = proposer
        self.target = target
        self.bot = bot
        self.answered = False

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.target.id:
            await interaction.response.send_message(
                f"⛔ Lời cầu hôn này dành riêng cho **{self.target.display_name}**!",
                ephemeral=True
            )
            return False
        return True

    @discord.ui.button(label="💍 Đồng Ý", style=discord.ButtonStyle.success)
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.answered = True
        self.clear_items()

        # Tạo mối quan hệ hôn nhân trên SQLite
        success = await self.bot.db.create_marriage(interaction.guild_id, self.proposer.id, self.target.id)
        if success:
            embed = discord.Embed(
                title="💒 LỄ THÀNH HÔN CHÍNH THỨC — HAPPY WEDDING!",
                description=(
                    f"🎉 Chúc mừng **{self.proposer.mention}** và **{self.target.mention}** đã chính thức về chung một nhà!\n\n"
                    "🏡 Cả hai đã được cấp một **Ngôi Nhà Cặp Đôi**.\n"
                    "👉 Gõ `/marry` để mở Trang chủ ngôi nhà của hai bạn!\n"
                    "👉 Tương tác `/kiss`, `/hug`, `/pat` mỗi ngày để tích lũy điểm thân mật và nâng cấp nhẫn cưới!"
                ),
                color=discord.Color.gold()
            )
            embed.set_image(url="https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExaWVmNXh0NnVndWpvYWNxcmpja3NvdTJtOTJpYTB3c3VvNWVnNG83ZSZlcD12MV9naWZzX3NlYXJjaCZjdD1n/DyQrKMpqkAhNHZ1aWE/giphy.gif")
        else:
            embed = discord.Embed(
                title="❌ KHÔNG THỂ KẾT HÔN",
                description="Một trong hai người đã có gia đình trong server này rồi!",
                color=discord.Color.red()
            )

        await interaction.response.edit_message(embed=embed, view=None)
        self.stop()

    @discord.ui.button(label="💔 Từ Chối", style=discord.ButtonStyle.danger)
    async def reject(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.answered = True
        self.clear_items()
        embed = discord.Embed(
            title="🥀 LỜI CẦU HÔN BỊ TỪ CHỐI",
            description=f"Rất tiếc, **{self.target.display_name}** đã từ chối lời cầu hôn của {self.proposer.mention}. Đừng buồn, người tốt hơn đang đợi bạn ở phía trước!",
            color=discord.Color.dark_gray()
        )
        await interaction.response.edit_message(embed=embed, view=None)
        self.stop()

    async def on_timeout(self):
        self.clear_items()


class MarryHouseView(discord.ui.View):
    """Giao diện Ngôi Nhà Cặp Đôi với 3 nút bấm: Trang Chủ, Ảnh & Video, Ghi Chú"""

    def __init__(self, marriage: dict, guild: discord.Guild, bot: commands.Bot, current_tab: str = "home", gallery_index: int = 0):
        super().__init__(timeout=180.0)
        self.marriage = marriage
        self.guild = guild
        self.bot = bot
        self.current_tab = current_tab
        self.gallery_index = gallery_index
        self.update_components()

    def update_components(self):
        self.clear_items()

        # 3 Nút Menu chính
        btn_home = discord.ui.Button(
            label="🏠 Trang Chủ",
            style=discord.ButtonStyle.primary if self.current_tab == "home" else discord.ButtonStyle.secondary,
            custom_id="tab_home"
        )
        btn_home.callback = self.goto_home
        self.add_item(btn_home)

        btn_gallery = discord.ui.Button(
            label="🖼️ Ảnh & Video",
            style=discord.ButtonStyle.primary if self.current_tab == "gallery" else discord.ButtonStyle.secondary,
            custom_id="tab_gallery"
        )
        btn_gallery.callback = self.goto_gallery
        self.add_item(btn_gallery)

        btn_notes = discord.ui.Button(
            label="📝 Ghi Chú",
            style=discord.ButtonStyle.primary if self.current_tab == "notes" else discord.ButtonStyle.secondary,
            custom_id="tab_notes"
        )
        btn_notes.callback = self.goto_notes
        self.add_item(btn_notes)

        # Nếu đang ở Tab Gallery, thêm 2 nút Lướt ảnh Trước / Sau
        if self.current_tab == "gallery":
            btn_prev = discord.ui.Button(label="⬅️ Ảnh Trước", style=discord.ButtonStyle.secondary, custom_id="gal_prev")
            btn_prev.callback = self.prev_image
            self.add_item(btn_prev)

            btn_next = discord.ui.Button(label="➡️ Ảnh Sau", style=discord.ButtonStyle.secondary, custom_id="gal_next")
            btn_next.callback = self.next_image
            self.add_item(btn_next)

    async def goto_home(self, interaction: discord.Interaction):
        self.current_tab = "home"
        self.update_components()
        embed = self.build_home_embed()
        await interaction.response.edit_message(embed=embed, view=self)

    async def goto_gallery(self, interaction: discord.Interaction):
        self.current_tab = "gallery"
        self.update_components()
        embed = self.build_gallery_embed()
        await interaction.response.edit_message(embed=embed, view=self)

    async def goto_notes(self, interaction: discord.Interaction):
        self.current_tab = "notes"
        self.update_components()
        embed = self.build_notes_embed()
        await interaction.response.edit_message(embed=embed, view=self)

    async def prev_image(self, interaction: discord.Interaction):
        self.gallery_index = (self.gallery_index - 1) % 6
        embed = self.build_gallery_embed()
        await interaction.response.edit_message(embed=embed, view=self)

    async def next_image(self, interaction: discord.Interaction):
        self.gallery_index = (self.gallery_index + 1) % 6
        embed = self.build_gallery_embed()
        await interaction.response.edit_message(embed=embed, view=self)

    def build_home_embed(self) -> discord.Embed:
        u1 = self.guild.get_member(int(self.marriage["user1_id"]))
        u2 = self.guild.get_member(int(self.marriage["user2_id"]))
        name1 = u1.display_name if u1 else f"User ({self.marriage['user1_id']})"
        name2 = u2.display_name if u2 else f"User ({self.marriage['user2_id']})"

        tier = self.marriage["ring_tier"]
        ring_info = RING_TIERS.get(tier, RING_TIERS[1])
        points = self.marriage["intimacy_points"]

        # Tính số ngày bên nhau
        married_date_str = str(self.marriage["married_at"])[:10]
        try:
            m_date = datetime.datetime.strptime(married_date_str, "%Y-%m-%d").date()
            days = (datetime.date.today() - m_date).days
        except Exception:
            days = 0

        embed = discord.Embed(
            title=f"🏡 {self.marriage['house_name']}",
            description=f"*\"{self.marriage['quote']}\"*\n\n❤️ **Cặp đôi:** {name1} 💕 {name2}",
            color=ring_info["color"]
        )
        if u1:
            embed.set_thumbnail(url=u1.display_avatar.url)

        embed.add_field(name="💍 Nhẫn Cưới", value=f"**{ring_info['name']}**\n*{ring_info['desc']}*", inline=True)
        embed.add_field(name="💖 Điểm Thân Mật", value=f"**{points:,}** Điểm", inline=True)
        embed.add_field(name="🗓️ Ngày Cưới", value=f"{married_date_str} *(Đã bên nhau {days} ngày)*", inline=False)
        embed.set_footer(text="Dùng /kiss, /hug, /pat với bạn đời để tăng điểm thân mật!")
        return embed

    def build_gallery_embed(self) -> discord.Embed:
        gallery = self.marriage["gallery"]
        current_img = gallery[self.gallery_index]

        embed = discord.Embed(
            title=f"🖼️ THƯ VIỆN ẢNH KỶ NIỆM ({self.gallery_index + 1}/6)",
            description=(
                "Lưu giữ những khoảnh khắc đáng nhớ của hai bạn!\n"
                f"• **Cách thêm ảnh:** `/lgallery <vị trí: 1-6> <link_ảnh>`\n"
                f"• **Vị trí hiện tại:** Ô số **{self.gallery_index + 1}**"
            ),
            color=discord.Color.purple()
        )

        if current_img and current_img.startswith("http"):
            embed.set_image(url=current_img)
        else:
            embed.add_field(
                name="Ô này chưa có ảnh",
                value=f"Hãy dùng lệnh `/lgallery {self.gallery_index + 1} <link_ảnh>` để thêm ảnh kỷ niệm!",
                inline=False
            )

        # Nếu có background tùy chỉnh cho thư viện
        if self.marriage.get("background_url"):
            embed.set_thumbnail(url=self.marriage["background_url"])

        return embed

    def build_notes_embed(self) -> discord.Embed:
        embed = discord.Embed(
            title="📝 GHI CHÚ & BẢNG CẤP BẬC NHẪN CƯỚI",
            description=(
                "Điểm thân mật càng cao, chiếc nhẫn của hai bạn sẽ càng tỏa sáng lộng lẫy!\n\n"
                "**BẢNG CẤP BẬC NHẪN:**\n"
                "• 🌿 **Nhẫn Cỏ Thần Tiên**: 0 – 49 điểm thân mật\n"
                "• 🪙 **Nhẫn Bạc Thuần Khiết**: 50 – 149 điểm thân mật\n"
                "• 👑 **Nhẫn Vàng Vương Giả**: 150 – 299 điểm thân mật\n"
                "• 💎 **Nhẫn Kim Cương Vĩnh Cửu**: 300 – 499 điểm thân mật\n"
                "• 🌌 **Nhẫn Vô Cực Ngân Hà**: 500+ điểm thân mật (Tối thượng)\n\n"
                "**CÁC LỆNH TƯƠNG TÁC TĂNG ĐIỂM (Cooldown 30s):**\n"
                "• `/kiss <@user>`: Trao nụ hôn ngọt ngào (+10 điểm)\n"
                "• `/hug <@user>`: Ôm ấm áp (+10 điểm)\n"
                "• `/pat <@user>`: Xoa đầu cưng nựng (+10 điểm)\n"
                "• `/slap <@user>`: Phát yêu / tát vui vẻ (+10 điểm)\n\n"
                "**CÁC LỆNH QUẢN LÝ NHÀ:**\n"
                "• `/marry_name <tên_mới>`: Đổi tên ngôi nhà\n"
                "• `/marry_quote <câu_nói>`: Đổi châm ngôn tình yêu\n"
                "• `/lgallery <vị_trí: 1-6> <link>`: Đổi ảnh kỷ niệm\n"
                "• `/divorce`: Ly hôn (Xóa dữ liệu nhà)"
            ),
            color=discord.Color.teal()
        )
        return embed
