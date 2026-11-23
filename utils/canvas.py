import io
import math
from pathlib import Path
from typing import Tuple, Optional
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter
import aiohttp
import logging

logger = logging.getLogger("SosaBot.Canvas")

def get_font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    """Tải font chữ hệ thống trên Windows / Linux hoặc fallback an toàn"""
    font_names = (
        ["arialbd.ttf", "segoeuib.ttf", "comicbd.ttf"]
        if bold
        else ["arial.ttf", "segoeui.ttf", "comic.ttf", "DejaVuSans.ttf"]
    )
    for name in font_names:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            pass

    # Thử đường dẫn Linux phổ biến
    linux_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf" if bold else "/usr/share/fonts/truetype/freefont/FreeSans.ttf"
    ]
    for path in linux_paths:
        if Path(path).exists():
            try:
                return ImageFont.truetype(path, size)
            except OSError:
                pass

    return ImageFont.load_default()


def create_smooth_circle_mask(size: Tuple[int, int]) -> Image.Image:
    """Tạo mask hình tròn siêu mịn với kỹ thuật 4x Supersampling khử hoàn toàn răng cưa (Anti-aliasing)"""
    scale = 4
    big_size = (size[0] * scale, size[1] * scale)
    big_mask = Image.new("L", big_size, 0)
    big_draw = ImageDraw.Draw(big_mask)
    big_draw.ellipse((0, 0, big_size[0] - 1, big_size[1] - 1), fill=255)
    return big_mask.resize(size, Image.Resampling.LANCZOS)


async def fetch_avatar_image(avatar_url: str, size: Tuple[int, int] = (128, 128)) -> Image.Image:
    """Tải avatar của người dùng qua URL và chuyển thành ảnh bo tròn siêu mượt không răng cưa"""
    mask = create_smooth_circle_mask(size)
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(avatar_url, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                if resp.status == 200:
                    data = await resp.read()
                    avatar = Image.open(io.BytesIO(data)).convert("RGBA")
                    avatar = avatar.resize(size, Image.Resampling.LANCZOS)

                    output = Image.new("RGBA", size, (0, 0, 0, 0))
                    output.paste(avatar, (0, 0), mask=mask)
                    return output
    except Exception as e:
        logger.warning(f"Không thể tải avatar từ {avatar_url}: {e}")

    # Tạo avatar mặc định nếu không tải được
    fallback = Image.new("RGBA", size, (130, 130, 200, 255))
    output = Image.new("RGBA", size, (0, 0, 0, 0))
    output.paste(fallback, (0, 0), mask=mask)
    return output


def draw_circle_avatar(base: Image.Image, avatar: Image.Image, pos: Tuple[int, int], border_color=(255, 117, 151), border_width=4):
    """Vẽ avatar hình tròn kèm viền phát sáng lên ảnh nền"""
    w, h = avatar.size
    x, y = pos

    # Vẽ vòng tròn viền ngoài
    draw = ImageDraw.Draw(base)
    draw.ellipse(
        (x - border_width, y - border_width, x + w + border_width, y + h + border_width),
        fill=border_color
    )
    # Dán avatar tròn vào tâm
    base.paste(avatar, (x, y), mask=avatar)


def draw_heart(draw: ImageDraw.ImageDraw, center: Tuple[int, int], size: int, fill_color=(255, 75, 120)):
    """Vẽ một trái tim cân đối tại vị trí tâm"""
    cx, cy = center
    r = size // 2

    # Trái tim vẽ bằng 2 hình tròn và 1 tam giác
    top_y = cy - r // 2
    left_x = cx - r // 2
    right_x = cx + r // 2

    draw.ellipse((left_x - r // 2, top_y - r // 2, left_x + r // 2, top_y + r // 2), fill=fill_color)
    draw.ellipse((right_x - r // 2, top_y - r // 2, right_x + r // 2, top_y + r // 2), fill=fill_color)
    draw.polygon([
        (cx - r, top_y),
        (cx + r, top_y),
        (cx, cy + r)
    ], fill=fill_color)


TEMPLATE_DIR = Path("assets/templates")

async def draw_love_calculator(
    avatar1_url: str,
    avatar2_url: str,
    user1_name: str,
    user2_name: str,
    percentage: int
) -> io.BytesIO:
    """
    Vẽ banner Love Calculator:
    - Nếu có file assets/templates/love_template.png: Sử dụng ảnh mẫu đồ họa tĩnh của người dùng
      và dán 2 avatar, in số %, thanh progress bar và tên 2 người lên các vị trí chuẩn.
    - Nếu không có: Tự động vẽ bằng code (Fallback).
    """
    love_template_path = TEMPLATE_DIR / "love_template.png"

    if love_template_path.exists():
        try:
            template = Image.open(love_template_path).convert("RGBA")
            W, H = template.size
            base = Image.new("RGBA", (W, H), (255, 255, 255, 255))

            # 1. Tải 2 Avatar người dùng siêu mịn
            av1 = await fetch_avatar_image(avatar1_url, (130, 130))
            av2 = await fetch_avatar_image(avatar2_url, (127, 127))

            # 2. Dán avatar dưới template để viền, tai nghe, mũ và cánh dơi đè lên tự nhiên
            base.paste(av1, (185, 115), mask=av1)
            base.paste(av2, (704, 117), mask=av2)

            # 3. Vẽ thanh tiến trình tình yêu DƯỚI template (để khung viền và chữ LOVE luôn ở trên cùng)
            draw_base = ImageDraw.Draw(base)
            bar_x = 346
            bar_y = 352
            bar_max_w = 374
            bar_h = 35
            fill_w = max(int(bar_max_w * (percentage / 100)), 20)
            draw_base.rounded_rectangle((bar_x, bar_y, bar_x + fill_w, bar_y + bar_h), radius=17, fill=(255, 75, 140))

            # 4. Phủ template lên trên (bảo vệ tuyệt đối khung viền và chữ LOVE)
            base.alpha_composite(template)
            draw = ImageDraw.Draw(base)

            # 5. In tên 2 người vào khung trắng phía dưới avatar
            font_name = get_font(20, bold=True)
            clean_name1 = user1_name[:12] + ("..." if len(user1_name) > 12 else "")
            clean_name2 = user2_name[:12] + ("..." if len(user2_name) > 12 else "")
            draw.text((250, 292), clean_name1, fill=(90, 45, 80), font=font_name, anchor="mm")
            draw.text((763, 291), clean_name2, fill=(90, 45, 80), font=font_name, anchor="mm")

            # 6. In con số % vào giữa trái tim trung tâm (chữ trắng có viền bóng đậm)
            font_pct = get_font(56, bold=True)
            pct_str = f"{percentage}%"
            for ox, oy in [(-3, -3), (3, -3), (-3, 3), (3, 3), (0, 3), (0, -3), (-3, 0), (3, 0)]:
                draw.text((510 + ox, 208 + oy), pct_str, fill=(170, 35, 75), font=font_pct, anchor="mm")
            draw.text((510, 208), pct_str, fill=(255, 255, 255), font=font_pct, anchor="mm")

            output = io.BytesIO()
            base.save(output, format="PNG")
            output.seek(0)
            return output
        except Exception as e:
            logger.warning(f"Lỗi khi xử lý love_template.png ({e}), chuyển sang chế độ tự vẽ.")

    # FALLBACK: Tự động vẽ hoàn toàn bằng code nếu chưa có file template
    WIDTH, HEIGHT = 840, 360
    base = Image.new("RGBA", (WIDTH, HEIGHT), (255, 245, 245, 255))
    draw = ImageDraw.Draw(base)

    # 1. Vẽ nền gradient nhẹ
    for y in range(HEIGHT):
        ratio = y / HEIGHT
        r = int(255 - ratio * 10)
        g = int(245 - ratio * 18)
        b = int(240 - ratio * 15)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b, 255))

    # 2. Vẽ viền khung tranh bo tròn bên trong
    inner_box = (20, 20, WIDTH - 20, HEIGHT - 20)
    draw.rounded_rectangle(inner_box, radius=24, outline=(255, 205, 215, 255), width=3, fill=(255, 250, 248, 200))

    # 3. Tiêu đề Header
    font_title = get_font(26, bold=True)
    header_text = "~ Sosa Love Calculator ~"
    draw.text((WIDTH // 2, 45), header_text, fill=(255, 105, 145), font=font_title, anchor="mm")

    # 4. Tải và dán 2 Avatar
    AVATAR_SIZE = 130
    av1 = await fetch_avatar_image(avatar1_url, (AVATAR_SIZE, AVATAR_SIZE))
    av2 = await fetch_avatar_image(avatar2_url, (AVATAR_SIZE, AVATAR_SIZE))

    pos1 = (120, 105)
    pos2 = (WIDTH - 120 - AVATAR_SIZE, 105)

    # Đường nhịp tim ECG kết nối 2 avatar
    heartbeat_y = 170
    draw.line([(pos1[0] + AVATAR_SIZE, heartbeat_y), (WIDTH // 2 - 80, heartbeat_y)], fill=(255, 185, 195), width=3)
    draw.line([(WIDTH // 2 + 80, heartbeat_y), (pos2[0], heartbeat_y)], fill=(255, 185, 195), width=3)

    # Dán 2 Avatar với viền
    draw_circle_avatar(base, av1, pos1, border_color=(255, 130, 160), border_width=4)
    draw_circle_avatar(base, av2, pos2, border_color=(255, 130, 160), border_width=4)

    # 5. Tên người dùng dưới avatar
    font_name = get_font(18, bold=True)
    clean_name1 = user1_name[:12] + ("..." if len(user1_name) > 12 else "")
    clean_name2 = user2_name[:12] + ("..." if len(user2_name) > 12 else "")
    draw.text((pos1[0] + AVATAR_SIZE // 2, pos1[1] + AVATAR_SIZE + 20), clean_name1, fill=(120, 80, 95), font=font_name, anchor="mm")
    draw.text((pos2[0] + AVATAR_SIZE // 2, pos2[1] + AVATAR_SIZE + 20), clean_name2, fill=(120, 80, 95), font=font_name, anchor="mm")

    # 6. Trái tim trung tâm và %
    heart_center = (WIDTH // 2, 170)
    heart_size = 90
    draw_heart(draw, heart_center, heart_size, fill_color=(255, 80, 125))

    font_pct = get_font(28, bold=True)
    pct_text = f"{percentage}%"
    draw.text((heart_center[0], heart_center[1] + 5), pct_text, fill=(255, 255, 255), font=font_pct, anchor="mm")

    # 7. Thanh tim tiến trình (Love Meter Bar) ở cạnh dưới
    bar_width = 320
    bar_height = 20
    bar_x = (WIDTH - bar_width) // 2
    bar_y = 285

    draw.rounded_rectangle((bar_x, bar_y, bar_x + bar_width, bar_y + bar_height), radius=10, fill=(255, 225, 230), outline=(255, 180, 195), width=2)
    fill_w = max(int(bar_width * (percentage / 100)), 15) if percentage > 0 else 0
    if fill_w > 0:
        draw.rounded_rectangle((bar_x, bar_y, bar_x + fill_w, bar_y + bar_height), radius=10, fill=(255, 90, 135))

    # Xuất ra bộ đệm RAM
    output = io.BytesIO()
    base.save(output, format="PNG")
    output.seek(0)
    return output

    # Xuất ra bộ đệm RAM
    output = io.BytesIO()
    base.save(output, format="PNG")
    output.seek(0)
    return output


async def draw_rank_card(
    avatar_url: str,
    username: str,
    level: int,
    current_xp: int,
    needed_xp: int,
    rank_num: int
) -> io.BytesIO:
    """
    Vẽ thẻ Rank phong cách Anime / Chibi Gal Hiphop:
    - Nếu có file assets/templates/rank_template.png: Dùng ảnh mẫu tĩnh do người dùng thiết kế.
    - Nếu không: Tự vẽ nền neon deep navy / magenta bo góc công nghệ (Fallback).
    """
    rank_template_path = TEMPLATE_DIR / "rank_template.png"
    has_template = rank_template_path.exists()

    if has_template:
        try:
            base = Image.open(rank_template_path).convert("RGBA")
            WIDTH, HEIGHT = base.size
            draw = ImageDraw.Draw(base)
        except Exception as e:
            logger.warning(f"Không thể mở rank_template.png ({e}), chuyển sang chế độ tự vẽ.")
            has_template = False

    if not has_template:
        WIDTH, HEIGHT = 880, 260
        base = Image.new("RGBA", (WIDTH, HEIGHT), (20, 18, 38, 255))
        draw = ImageDraw.Draw(base)

        # 1. Nền gradient đường phố neon (Deep Navy -> Dark Magenta)
        for x in range(WIDTH):
            ratio = x / WIDTH
            r = int(22 + ratio * 20)
            g = int(20 + ratio * 8)
            b = int(45 + ratio * 15)
            draw.line([(x, 0), (x, HEIGHT)], fill=(r, g, b, 255))

        # Khung bo góc công nghệ
        draw.rounded_rectangle((15, 15, WIDTH - 15, HEIGHT - 15), radius=20, outline=(255, 46, 147, 180), width=3)

    # 2. Tải và dán Avatar
    AVATAR_SIZE = 150
    avatar = await fetch_avatar_image(avatar_url, (AVATAR_SIZE, AVATAR_SIZE))
    av_pos = (50, 55)

    # Vẽ viền neon phát sáng cho avatar
    draw.ellipse((av_pos[0] - 6, av_pos[1] - 6, av_pos[0] + AVATAR_SIZE + 6, av_pos[1] + AVATAR_SIZE + 6), fill=(255, 46, 147))
    draw.ellipse((av_pos[0] - 2, av_pos[1] - 2, av_pos[0] + AVATAR_SIZE + 2, av_pos[1] + AVATAR_SIZE + 2), fill=(10, 10, 25))
    base.paste(avatar, av_pos, mask=avatar)

    # 3. Tên người dùng (Street / Gal style)
    content_x = 240
    font_name = get_font(32, bold=True)
    clean_username = username[:16] + ("..." if len(username) > 16 else "")
    draw.text((content_x, 60), clean_username, fill=(255, 255, 255), font=font_name)

    # 4. Badge RANK và LEVEL
    font_badge = get_font(20, bold=True)
    font_num = get_font(28, bold=True)

    # Rank Badge (bên phải trên)
    draw.text((WIDTH - 250, 60), "RANK", fill=(180, 180, 220), font=font_badge)
    draw.text((WIDTH - 180, 55), f"#{rank_num}", fill=(255, 46, 147), font=font_num)

    # Level Badge
    draw.text((WIDTH - 130, 60), "LVL", fill=(180, 180, 220), font=font_badge)
    draw.text((WIDTH - 75, 55), f"{level}", fill=(0, 240, 255), font=font_num)

    # 5. Thanh tiến trình XP (XP Progress Bar)
    pct = min(max(current_xp / needed_xp, 0.0), 1.0) if needed_xp > 0 else 0.0
    bar_x = content_x
    bar_y = 150
    bar_w = WIDTH - content_x - 50
    bar_h = 32

    # Vẽ nền thanh bar
    draw.rounded_rectangle((bar_x, bar_y, bar_x + bar_w, bar_y + bar_h), radius=16, fill=(35, 30, 60), outline=(80, 70, 120), width=2)

    # Vẽ phần trăm đã nạp (Gradient Neon Pink -> Neon Orange)
    fill_w = int(bar_w * pct)
    if fill_w > 16:
        draw.rounded_rectangle((bar_x, bar_y, bar_x + fill_w, bar_y + bar_h), radius=16, fill=(255, 46, 147))

    # 6. Thông số XP hiển thị bên trên thanh bar
    font_xp = get_font(18, bold=True)
    xp_str = f"{current_xp:,} / {needed_xp:,} XP ({int(pct * 100)}%)"
    draw.text((content_x, 120), "EXP PROGRESS", fill=(150, 140, 180), font=get_font(16, bold=True))
    draw.text((WIDTH - 50, 120), xp_str, fill=(255, 230, 240), font=font_xp, anchor="ra")

    # 7. Nhãn trang trí Gal / Street Hiphop vibe
    font_tag = get_font(14, bold=True)
    draw.text((content_x, 205), "⚡ SOSAPY STREET LEVEL SYSTEM", fill=(255, 46, 147, 200), font=font_tag)

    output = io.BytesIO()
    base.save(output, format="PNG")
    output.seek(0)
    return output
