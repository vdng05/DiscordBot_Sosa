# 🤖 SosaGallery — All-in-One Discord Bot

<p align="center">
  <b>Hệ thống Discord Bot đa chức năng, kiến trúc từng tính năng một thư mục riêng biệt (Feature-Folder Architecture), tích hợp SQLite bất đồng bộ (aiosqlite WAL Mode) siêu nhẹ, hỗ trợ đồ họa canvas Anime/Gal và tối ưu cho VPS.</b>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python Version" />
  <img src="https://img.shields.io/badge/discord.py-v2.3+-5865F2?style=for-the-badge&logo=discord&logoColor=white" alt="discord.py" />
  <img src="https://img.shields.io/badge/Architecture-Feature--Folder-success?style=for-the-badge" alt="Architecture" />
  <img src="https://img.shields.io/badge/Database-SQLite%20(WAL%20Mode)-blue?style=for-the-badge" alt="Database" />
  <img src="https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker" />
</p>

---

## 📑 Mục Lục
- [1. Giới Thiệu Dự Án](#1-giới-thiệu-dự-án)
- [2. Kiến Trúc Cơ Sở Dữ Liệu & Triển Khai: SQLite vs Docker](#2-kiến-trúc-cơ-sở-dữ-liệu--triển-khai-sqlite-vs-docker)
- [3. Kiến Trúc Hệ Thống & Tính Năng Nổi Bật](#3-kiến-trúc-hệ-thống--tính-năng-nổi-bật)
- [4. Cấu Trúc Thư Mục Chuẩn Hóa (Feature-Folder)](#4-cấu-trúc-thư-mục-chuẩn-hóa-feature-folder)
- [5. Hướng Dẫn Cài Đặt & Triển Khai Toàn Diện](#5-hướng-dẫn-cài-đặt--triển-khai-toàn-diện)
  - [Cách 1: Chạy trực tiếp (Python trên Windows / Linux) — Khuyên dùng & Đơn giản nhất](#cách-1-chạy-trực-tiếp-python-trên-windows--linux)
  - [Cách 2: Triển khai bằng Docker trên VPS (Tùy chọn)](#cách-2-triển-khai-1-click-bằng-docker-trên-vps)
- [6. Cấu Hình Biến Môi Trường (.env)](#6-cấu-hình-biến-môi-trường-env)
- [7. Hướng Dẫn Sử Dụng & Bảng Lệnh Đầy Đủ](#7-hướng-dẫn-sử-dụng--bảng-lệnh-đầy-đủ)
  - [7.1. Lệnh Quản Trị Hệ Thống Dành Cho Owner (!sync, !reload, !status)](#71-lệnh-quản-trị-hệ-thống-dành-cho-owner-sync-reload)
  - [7.2. Nhóm Lệnh Chung, Cài Đặt & Thẻ Rank Đồ Họa (/help, /rank, /leaderboard, /settings)](#72-nhóm-lệnh-chung-cài-đặt--thẻ-rank-đồ-họa-help-rank-leaderboard-settings)
  - [7.3. Nhóm Bói Tình Duyên & Cặp Đôi (Love Calculator & Marry System)](#73-nhóm-bói-tình-duyên--cặp-đôi-love-calculator--marry-system)
  - [7.4. Nhóm Tương Tác Thân Mật Tăng Điểm Nhẫn Cưới (/kiss, /hug, /pat, /slap)](#74-nhóm-tương-tác-thân-mật-tăng-điểm-nhẫn-cưới-kiss-hug-pat-slap)
  - [7.5. Nhóm Âm Nhạc (Music)](#75-nhóm-âm-nhạc-music)
  - [7.6. Nhóm Giao Tiếp Voice (TTS)](#76-nhóm-giao-tiếp-voice-tts)
  - [7.7. Nhóm Thiết Lập Server 3 Bước Xác Nhận (/setup-server)](#77-nhóm-thiết-lập-server-3-bước-xác-nhận-setup-server)
  - [7.8. Nhóm Quản Trị Tự Động (AutoMod)](#78-nhóm-quản-trị-tự-động-automod)
- [8. Cơ Chế Xử Lý Lỗi Tập Trung & Bảo Vệ Tài Nguyên](#8-cơ-chế-xử-lý-lỗi-tập-trung--bảo-vệ-tài-nguyên)
- [9. Nhật Ký Cập Nhật & Tiến Độ Làm Việc (Worklog & Changelog)](#9-nhật-ký-cập-nhật--tiến-độ-làm-việc-worklog--changelog)
- [10. Kế Hoạch Phát Triển (Roadmap)](#10-kế-hoạch-phát-triển-roadmap)

---

## 1. Giới Thiệu Dự Án

**SosaPy** là một Discord Bot toàn diện được thiết kế theo kiến trúc **Feature-Folder (Vertical Slice Architecture)**: mỗi tính năng lớn được tổ chức độc lập trong một thư mục riêng trong `cogs/`, giúp loại bỏ hoàn toàn sự phụ thuộc chéo và dễ dàng bảo trì, phát triển lâu dài.

Hệ thống cung cấp đầy đủ các chức năng quan trọng nhất cho cộng đồng Discord:
- **Âm nhạc đa nguồn:** Hỗ trợ YouTube, SoundCloud, Spotify, tự động dọn dẹp hàng đợi và tự rời phòng khi không còn ai nghe.
- **Voice Text-To-Speech (TTS tiếng Việt):** Đọc văn bản bằng giọng nói Google TTS, tự động điều phối với luồng phát nhạc mà không gây xung đột âm thanh.
- **Quản trị an ninh thông minh (AutoMod):** Lọc từ cấm, chặn link ngoài có Whitelist kênh nhạc/media, chống spam tin nhắn và tự động phạt timeout.
- **Hệ thống Level / Rank thời gian thực:** Cộng điểm kinh nghiệm (XP) khi chat hợp lệ và lưu trữ trực tiếp vào SQLite.
- **Thiết lập Server mẫu bảo mật cao:** Dùng hộp thoại **Discord Modal** ẩn mật khẩu, tự động tạo Category, Channel, Role từ file template JSON với cơ chế chống Rate Limit API.

---

## 2. Kiến Trúc Cơ Sở Dữ Liệu & Triển Khai: SQLite vs Docker

> [!IMPORTANT]
> **Câu hỏi quan trọng: "Docker có cần thiết không? Tôi tưởng chỉ cần SQLite là đủ rồi chứ?"**
>
> 💡 **Giải đáp chuẩn xác:**
> 1. **Về Cơ sở dữ liệu: SQLite là ĐỦ 100%!**  
>    SQLite là một database hoàn chỉnh được tích hợp sẵn bên trong Python. Bạn **KHÔNG CẦN** bất kỳ cơ sở dữ liệu rời nào khác (như MySQL, PostgreSQL, MongoDB, Redis). Toàn bộ dữ liệu của bot (Cấu hình server, Level/Rank, Nhà kết hôn, Album ảnh, Nhẫn cưới, Log AutoMod) được lưu gọn trong **1 file duy nhất `data/sosapy.db`**.
>
> 2. **Về Docker: Hoàn toàn TÙY CHỌN (Optional)!**  
>    - **Docker KHÔNG PHẢI là database:** Docker chỉ là một "hộp đóng gói" giúp gom Python + FFmpeg lại một chỗ.
>    - **Nếu bạn KHÔNG muốn dùng Docker:** Bạn hoàn toàn có thể chạy bot trực tiếp trên VPS Ubuntu / Debian cực kỳ nhẹ nhàng: chỉ cần chạy 1 dòng `sudo apt install ffmpeg python3-pip` rồi `python main.py`. Dùng `pm2` hoặc `systemd` để bot tự chạy ngầm 24/7.
>    - **Nếu bạn thích Docker:** Dự án đã viết sẵn `Dockerfile` & `docker-compose.yml` để bạn gõ đúng 1 lệnh là xong mà không cần cài FFmpeg thủ công.

### Ưu điểm vượt trội của SQLite (`aiosqlite` WAL Mode) trong SosaPy:
1. **Không nghẽn Disk I/O:** JSON buộc phải đọc và ghi lại toàn bộ file mỗi lần thay đổi 1 giá trị. SQLite chỉ ghi đúng dòng (row) cần cập nhật.
2. **Chế độ WAL (Write-Ahead Logging):** Kích hoạt sẵn qua `PRAGMA journal_mode = WAL;`. Chế độ này cho phép nhiều lệnh đọc và ghi diễn ra đồng thời mà không bao giờ bị lỗi `database is locked`.
3. **Bảng xếp hạng (Leaderboard) siêu tốc:** SQLite hỗ trợ câu lệnh SQL truy vấn trực tiếp:
   ```sql
   SELECT user_id, xp, level FROM user_levels WHERE guild_id = ? ORDER BY xp DESC LIMIT 10;
   ```
4. **Vẫn là 1 file duy nhất:** Toàn bộ dữ liệu nằm gọn trong file `data/sosapy.db`. Khi cần sao lưu, bạn chỉ cần copy đúng file này sang máy khác.

---

## 3. Kiến Trúc Hệ Thống & Tính Năng Nổi Bật

```mermaid
flowchart TD
    subgraph Discord_Platform["Discord Gateway"]
        Events["Tin nhắn / Slash Commands / Nút bấm tương tác UI"]
    end

    subgraph Core_Engine["Core & Shared Utilities"]
        Main["main.py (Auto-Loader & Lifecycle)"]
        Config["config.py (.env Reader)"]
        Logger["utils/logger.py (Rotating Logs)"]
        Database["utils/database.py (aiosqlite WAL)"]
        CanvasEngine["utils/canvas.py (Pillow Graphics Renderer)"]
        ErrorHandler["utils/error_handler.py (Global Errors)"]
    end

    subgraph Feature_Folders["Feature Modules (cogs/)"]
        subgraph Admin_Module["cogs/admin/"]
            CmdSync["!sync (On-Demand Sync)"]
            CmdReload["!reload (Hot Reload Cogs)"]
            CmdStatus["!status (Resource Monitor)"]
        end

        subgraph General_Module["cogs/general/"]
            CmdRank["/rank & !rank (Thẻ đồ họa Chibi Gal)"]
            CmdLb["/leaderboard (Bảng vàng Top 10)"]
            CmdHelp["/help (Bảng hướng dẫn lệnh)"]
            CmdSettings["/settings (Bật/Tắt tự động từng Guild)"]
        end

        subgraph Marry_Module["cogs/marry/"]
            CmdLovec["/lovec & !lovec (Bói tình duyên Canvas)"]
            CmdMarry["/marry & !marry (Ngôi Nhà Cặp Đôi 3 Tab)"]
            CmdGallery["/lgallery (Album 6 ảnh kỷ niệm)"]
            CmdSocial["/kiss, /hug, /pat, /slap (Tăng điểm Nhẫn Cưới)"]
        end

        subgraph Music_Module["cogs/music/"]
            M_Cog["cog.py (Slash Commands)"]
            M_Player["player.py (Loop & Idle Timeout)"]
            M_Src["sources.py (Secure Protocols)"]
        end

        subgraph TTS_Module["cogs/tts/"]
            T_Cog["cog.py (TTS & Audio Coordination)"]
        end

        subgraph Setup_Module["cogs/setup_server/"]
            S_Cog["cog.py (Xác thực 3 Bước & Rate Limiting)"]
            S_Json["templates.json (Template Data)"]
        end

        subgraph AutoMod_Module["cogs/automod/"]
            A_Cog["cog.py (Whitelist & XP Rewards)"]
        end
    end

    subgraph Storage_Layer["Persistent Storage"]
        DBFile["data/sosapy.db (SQLite WAL Database)"]
        LogsFolder["logs/bot.log (Log File)"]
        TempFolder["temp/ (Auto-Cleaned Files)"]
    end

    Events <--> Main
    Main --> Config & Logger & Database & CanvasEngine & ErrorHandler
    Main --> Feature_Folders
    Feature_Folders <--> Database
    General_Module --> CanvasEngine
    Marry_Module --> CanvasEngine
    Database <--> DBFile
    Logger --> LogsFolder
    T_Cog --> TempFolder
```

---

## 4. Cấu Trúc Thư Mục Chuẩn Hóa (Feature-Folder)

```text
SosaPy/
├── .env                          # Lưu biến môi trường bí mật (Token, Key) - KHÔNG ĐẨY LÊN GIT
├── .env.example                  # Mẫu cấu hình môi trường chuẩn
├── .gitignore                    # Bỏ qua cache, file tạm, file database nhạy cảm (*.db)
├── Dockerfile                    # Đóng gói Docker cài sẵn Python 3.12 + FFmpeg cho VPS (Tùy chọn)
├── docker-compose.yml            # Khởi chạy bot 1-click bằng Docker (Tùy chọn)
├── config.py                     # Quản lý tập trung cấu hình hệ thống
├── main.py                       # Khởi chạy: nạp cogs, SQLite, dọn rác temp, error handler
├── requirements.txt              # Danh sách thư viện (aiosqlite, pillow, discord.py, ...)
├── README.md                     # Tài liệu kỹ thuật trung tâm
│
├── cogs/                         # THƯ MỤC CHỨC NĂNG (MỖI CHỨC NĂNG 1 FOLDER)
│   ├── admin/                    # [QUẢN TRỊ OWNER] Lệnh !sync, !reload, !status
│   │   ├── __init__.py
│   │   └── cog.py
│   │
│   ├── general/                  # [CHUNG & CÀI ĐẶT] /help, /rank đồ họa, /leaderboard, /settings
│   │   ├── __init__.py
│   │   └── cog.py
│   │
│   ├── marry/                    # [BÓI DUYÊN & KẾT HÔN] /lovec, /marry, /lgallery, /kiss, /hug...
│   │   ├── __init__.py
│   │   ├── cog.py                # Lệnh slash & prefix, tính toán seed, hành động tương tác
│   │   └── views.py              # Giao diện UI: Lời cầu hôn 💍, Ngôi Nhà 3 Tab (Home, Gallery, Notes)
│   │
│   ├── music/                    # [NGHE NHẠC] YouTube, SoundCloud, Spotify
│   │   ├── __init__.py
│   │   ├── cog.py                # Lệnh slash, kiểm tra phòng trống tự rời
│   │   ├── player.py             # Queue loop, đồng bộ ngắt khi có TTS
│   │   └── sources.py            # yt-dlp và trích xuất Spotify non-blocking
│   │
│   ├── setup_server/             # [SETUP SERVER] Template mẫu và Xác nhận 3 Bước
│   │   ├── __init__.py
│   │   ├── cog.py                # 3 bước confirm nút bấm, chỉ Server Owner
│   │   └── templates.json        # Dữ liệu JSON mô tả Category, Channel và Role
│   │
│   ├── tts/                      # [VOICE TTS] Text-To-Speech tiếng Việt
│   │   ├── __init__.py
│   │   └── cog.py                # Lệnh /speak, giới hạn 300 ký tự, non-blocking gTTS
│   │
│   └── automod/                  # [AUTOMOD & XP] Lọc từ cấm, link rác, cộng XP
│       ├── __init__.py
│       └── cog.py                # Whitelist kênh nhạc, chống rò rỉ RAM, cộng XP SQLite
│
├── data/                         # THƯ MỤC CƠ SỞ DỮ LIỆU
│   └── sosapy.db                 # File SQLite Database đơn giản, siêu nhẹ (WAL Mode)
│
├── utils/                        # TIỆN ÍCH DÙNG CHUNG
│   ├── __init__.py
│   ├── database.py               # DatabaseManager quản lý SQLite (bảng settings, levels, marriages)
│   ├── canvas.py                 # Bộ vẽ đồ họa Pillow (Thẻ Rank Cyberpunk, Banner Love Calculator Lunari-style)
│   ├── error_handler.py          # Bộ xử lý lỗi tập trung cho toàn bộ Slash Commands
│   ├── logger.py                 # Hệ thống ghi log (Console + Rotating File bot.log)
│   └── storage.py                # Hỗ trợ đọc/ghi file JSON an toàn (Lock + Atomic)
│
├── logs/                         # File bot.log xoay vòng tối đa 5MB/file
└── temp/                         # File âm thanh tạm thời (tự dọn dẹp lúc khởi động)
```

---

## 5. Hướng Dẫn Cài Đặt & Triển Khai Toàn Diện

### Cách 1: Chạy trực tiếp (Python trên Windows / Linux)

#### Bước 1: Chuẩn bị FFmpeg & Python
- **Python**: Phiên bản 3.10 trở lên (khuyên dùng Python 3.12).
- **FFmpeg**:
  - *Windows*: Tải từ [gyan.dev FFmpeg](https://www.gyan.dev/ffmpeg/builds/) và thêm vào `Path`.
  - *Ubuntu/Debian VPS*: `sudo apt update && sudo apt install -y ffmpeg python3-venv python3-pip`

#### Bước 2: Tạo môi trường ảo & Cài đặt thư viện
```bash
# Tạo môi trường ảo
python -m venv venv

# Kích hoạt (Windows PowerShell):
.\venv\Scripts\Activate.ps1
# Kích hoạt (Linux VPS):
source venv/bin/activate

# Cài đặt thư viện
pip install -r requirements.txt
```

#### Bước 3: Cấu hình và Khởi chạy
1. Sao chép `.env.example` thành `.env` và điền token:
   ```bash
   cp .env.example .env
   ```
2. Khởi chạy bot:
   ```bash
   python main.py
   ```

---

### Cách 2: Triển khai 1-click bằng Docker trên VPS

Nếu VPS của bạn đã cài sẵn Docker và Docker Compose, bạn không cần phải cài Python hay FFmpeg thủ công:

```bash
# 1. Clone repository về VPS
git clone https://github.com/vdng05/DiscordBot_Sosa.git
cd DiscordBot_Sosa

# 2. Tạo file cấu hình .env
cp .env.example .env
nano .env  # Điền DISCORD_TOKEN và OWNER_IDS của bạn

# 3. Khởi chạy container ngầm trong nền
docker compose up -d --build
```
> [!TIP]
> Container sẽ tự động giữ dữ liệu trong thư mục `./data` và log trong `./logs` ngay trên ổ cứng VPS. Khi reboot VPS, bot sẽ tự động chạy lại nhờ thiết lập `restart: unless-stopped`.

---

## 6. Cấu Hình Biến Môi Trường (.env)

| Tên biến | Mặc định | Ý nghĩa & Khuyến nghị |
| :--- | :--- | :--- |
| `DISCORD_TOKEN` | *(Bắt buộc)* | Token xác thực bot từ Discord Developer Portal. |
| `OWNER_IDS` | *Rỗng* | ID tài khoản Discord của bạn (để sử dụng lệnh `!sync`, `!reload`). |
| `COMMAND_PREFIX` | `!` | Tiền tố lệnh quản trị (dành cho các lệnh `!sync`, `!reload`). |
| `SYNC_ON_STARTUP`| `false` | **Khuyên dùng false**: Không tự động sync khi restart để tránh bị Discord khóa API (Rate Limit). Dùng lệnh `!sync` khi cần. |
| `TTS_MAX_LENGTH` | `300` | Giới hạn số lượng ký tự tối đa cho mỗi lần đọc `/speak` (chống spam âm thanh). |
| `BAD_WORDS` | `từ_cấm_1,toxic` | Danh sách từ cấm ngăn chặn qua AutoMod. |
| `SPAM_LIMIT` | `5` | Số tin nhắn tối đa gửi trong `SPAM_TIME` giây trước khi bị timeout. |
| `SPAM_TIME` | `3` | Khung thời gian kiểm tra spam (giây). |
| `LOG_LEVEL` | `INFO` | Mức độ log: `INFO`, `DEBUG`, `WARNING`, `ERROR`. |

---

## 7. Hướng Dẫn Sử Dụng & Bảng Lệnh Đầy Đủ

### 7.1. Lệnh Quản Trị Hệ Thống Dành Cho Owner (!sync, !reload, !status)
*Các lệnh này chỉ có chủ bot (`OWNER_IDS`) mới dùng được, dùng tiền tố prefix (`!`):*

- `!sync guild`: Đồng bộ toàn bộ Slash Commands vào Server hiện tại ngay tức thì (dùng khi thử nghiệm tính năng mới mà không lo dính Rate Limit).
- `!sync global`: Đồng bộ toàn bộ Slash Commands ra toàn cầu (Discord mất khoảng 1-10 phút để hiển thị trên tất cả server).
- `!reload <module>`: Tải lại tức thì một module cog (ví dụ: `!reload marry`, `!reload general`, `!reload music`) mà không cần tắt bot, không làm gián đoạn phòng nghe nhạc.
- `!status`: Kiểm tra Ping mạng, mức chiếm dụng RAM (MB), thời gian hoạt động liên tục (Uptime) và trạng thái SQLite.

---

### 7.2. Nhóm Lệnh Chung, Cài Đặt & Thẻ Rank Đồ Họa (/help, /rank, /leaderboard, /settings)
- `/help` (hoặc `!help`): Xem hướng dẫn sử dụng và danh sách toàn bộ câu lệnh của bot (hỗ trợ hiển thị song song cả cú pháp Slash Command `/` và Prefix `!`).
- `/rank [member]` (hoặc `!rank [@member]`): **Thẻ Rank đồ họa phong cách Chibi Gal Hiphop Neon cực đỉnh!** Vẽ trực tiếp bằng Canvas (Pillow) với avatar bo tròn viền phát sáng kép, cấp độ, thứ hạng server, điểm kinh nghiệm XP và thanh tiến trình thăng cấp neon rực rỡ.
- `/leaderboard` (hoặc `!leaderboard` / `!top`): Xem Bảng vàng Top 10 thành viên có cấp độ và điểm kinh nghiệm cao nhất server (truy vấn SQLite siêu tốc).
- `/settings view`: Xem bảng trạng thái BẬT/TẮT hiện tại của các tính năng tự động chạy ngầm trên máy chủ và tiền tố lệnh đang dùng.
- `/settings prefix <ký_tự>` (hoặc `!prefix <ký_tự>`): Đổi tiền tố gõ lệnh của bot trên server (ví dụ: `$`, `.`, `?`).
- `/settings automod <enable>`: BẬT hoặc TẮT bộ lọc từ cấm, link rác và chống spam.
- `/settings level <enable>`: BẬT hoặc TẮT hệ thống tính điểm kinh nghiệm (XP) khi chat.

---

### 7.3. Nhóm Bói Tình Duyên & Cặp Đôi (Love Calculator & Marry System)
Hệ thống lấy cảm hứng từ Lunari Bot nhưng được nâng cấp toàn diện và đồng bộ với SQLite Database:

#### 1. Bói Tình Duyên (Love Calculator):
- **Cú pháp:** `/lovec <target> [target2]` hoặc `!lovec <@user | tên | ID | random>`
- **Cơ chế ngẫu nhiên công bằng:**
  - Nếu chọn `@user`: Tính toán độ hợp nhau giữa bạn và người đó.
  - Nếu gõ `random`: Bot sẽ tự động chọn ngẫu nhiên một thành viên đang có mặt trong server để ghép đôi với bạn!
  - Seed ngẫu nhiên được neo theo ngày (mỗi ngày có một chỉ số duyên phận riêng, sang ngày hôm sau sẽ đổi).
- **Banner đồ họa Canvas:** Vẽ banner tông pastel cute (hồng đào / kem) với 2 avatar bo tròn có viền phát sáng, trái tim ở giữa hiển thị tỷ lệ `%`, đường xung nhịp tim tình yêu (ECG line) và thanh đo độ hợp (Love Meter) ở cạnh dưới, kèm lời bình hài hước, dí dỏm.

#### 2. Hệ Thống Kết Hôn & Ngôi Nhà Cặp Đôi (Marry System):
- `/marry <@user>` (hoặc `!marry @user`): Gửi lời cầu hôn ngọt ngào đến người ấy. Bot sẽ xuất hiện giao diện tương tác gồm 2 nút bấm: **💍 Đồng Ý** hoặc **💔 Từ Chối** (chỉ người được cầu hôn mới bấm được, thời gian chờ 120s).
- `/marry` (hoặc `!marry`): Mở giao diện **Ngôi Nhà Cặp Đôi (Marry House)** với 3 nút bấm tương tác:
  - 🏠 **Trang Chủ:** Hiển thị Tên ngôi nhà, Châm ngôn tình yêu, Ngày kết hôn, Điểm thân mật, Cấp bậc Nhẫn Cưới và ảnh nền tùy biến.
  - 🖼️ **Ảnh & Video (Gallery):** Thư viện ảnh kỷ niệm với 6 slot ảnh. Người dùng có thể bấm nút **⬅️ Ảnh Trước** và **➡️ Ảnh Sau** để lướt xem từng kỷ niệm đã lưu.
  - 📝 **Ghi Chú:** Bảng danh sách 5 cấp bậc Nhẫn Cưới cùng hướng dẫn chi tiết các lệnh tương tác.
- `/marry_name <tên mới>` (hoặc `!name <tên mới>`): Đổi tên cho ngôi nhà cặp đôi.
- `/marry_quote <châm ngôn>` (hoặc `!quote <châm ngôn>`): Đổi câu nói/châm ngôn tình yêu hiển thị ở trang chủ.
- `/lgallery <slot 1-6> <URL ảnh>` (hoặc `!lgallery <1-6> <URL>`): Lưu ảnh kỷ niệm vào 1 trong 6 vị trí của album.
- `/divorce` (hoặc `!divorce`): Ly hôn và giải phóng ngôi nhà cặp đôi khi không còn chung đường.

---

### 7.4. Nhóm Tương Tác Thân Mật Tăng Điểm Nhẫn Cưới (/kiss, /hug, /pat, /slap)
- **Các câu lệnh hành động:**
  - `/kiss <@user>` hoặc `!kiss <@user>`: Trao nụ hôn ngọt ngào.
  - `/hug <@user>` hoặc `!hug <@user>`: Cái ôm ấm áp.
  - `/pat <@user>` hoặc `!pat <@user>`: Xoa đầu cưng nựng.
  - `/slap <@user>` hoặc `!slap <@user>`: Phát tát yêu thương / giận dỗi.
- **Cơ chế Điểm Thân Mật & Nâng Cấp Nhẫn Cưới:**
  - Khi bạn thực hiện bất kỳ hành động nào trên với **người bạn đời đã kết hôn**, cả hai sẽ được cộng **+10 Điểm Thân Mật** (cooldown 30 giây chống spam).
  - Điểm thân mật càng cao, Nhẫn Cưới của hai bạn càng được nâng cấp sang phẩm cấp cao hơn:

| Cấp bậc | Tên Nhẫn Cưới | Điểm yêu cầu | Biểu tượng & Mô tả |
| :---: | :--- | :---: | :--- |
| **Tier 1** | **Nhẫn Cỏ Thần Tiên** | 0 – 49 điểm | 🌿 Mộc mạc, giản dị thuở mới về chung một nhà |
| **Tier 2** | **Nhẫn Bạc Thuần Khiết** | 50 – 149 điểm | 🪙 Tình cảm êm đềm, gắn bó qua từng ngày |
| **Tier 3** | **Nhẫn Vàng Vương Giả** | 150 – 299 điểm | 👑 Sang trọng, tình yêu đằm thắm và bền chặt |
| **Tier 4** | **Nhẫn Kim Cương Vĩnh Cửu** | 300 – 499 điểm | 💎 Lấp lánh, tình cảm son sắt không thể chia lìa |
| **Tier 5** | **Nhẫn Vô Cực Ngân Hà** | 500+ điểm | 🌌 Tình yêu huyền thoại vượt qua không gian và thời gian! |

---

### 7.5. Nhóm Âm Nhạc (Music) & Giao Diện Nút Bấm Điều Khiển
Hỗ trợ đầy đủ cả **Lệnh Gạch Chéo (`/`)**, **Lệnh Tiền Tố (`!`)**, và **4 Nút Bấm Trực Tiếp** dưới tin nhắn bot:
- **4 Nút Bấm Tiện Lợi (Không Cần Gõ Lệnh):**
  - ⏯️ **Tạm Dừng / Tiếp Tục:** Tạm dừng bài hát đang nghe hoặc nghe tiếp.
  - ⏭️ **Chuyển Bài:** Bỏ qua bài hát hiện tại và sang bài tiếp theo.
  - 📜 **Xem Hàng Đợi:** Xem danh sách bài hát đang chờ (chỉ bạn nhìn thấy).
  - ⏹️ **Dừng & Thoát:** Tắt nhạc và mời bot rời khỏi phòng thoại.
- `/play <query>` (hoặc `!play <tên/link>`, `!p`): Phát nhạc từ đường link (YouTube, SoundCloud, Spotify) hoặc tìm kiếm theo tên bài hát.
- `/pause` (hoặc `!pause`): Tạm dừng bài hát đang phát trong phòng thoại.
- `/resume` (hoặc `!resume`): Tiếp tục phát bài hát đang bị tạm dừng.
- `/skip` (hoặc `!skip`, `!s`): Bỏ qua bài hát hiện tại và tự động chuyển sang bài tiếp theo trong hàng đợi.
- `/queue` (hoặc `!queue`, `!q`): Xem danh sách các bài hát đang chờ phát trong hàng đợi của máy chủ.
- `/leave` (hoặc `!leave`, `!stop`): Yêu cầu bot ngắt kết nối khỏi kênh thoại và làm sạch hàng đợi.
- **Tự động tiết kiệm tài nguyên:** Nếu tất cả người dùng rời khỏi phòng (chỉ còn bot) hoặc sau 5 phút không có bài hát mới, bot sẽ tự động ngắt kết nối để giải phóng RAM và CPU.

---

### 7.6. Nhóm Giao Tiếp Voice (Say / TTS)
- `/say <text>` (hoặc `!say <nội dung>`, alias `/speak`, `!speak`): Chuyển văn bản tiếng Việt thành giọng nói trong kênh thoại (tối đa 300 ký tự).
- **Điều phối âm thanh thông minh:** Nếu đang phát nhạc, bot sẽ tự động lưu lại bài hát đang nghe dở, đọc thông báo TTS xong rồi mới tiếp tục phát nhạc, không gây xung đột âm thanh `Already playing audio`.

---

### 7.7. Nhóm Thiết Lập Server 3 Bước Xác Nhận (/setup-server)
- `/setup-server [clear_old]`: Khởi tạo toàn bộ cấu trúc Danh mục, Kênh và Quyền theo template mẫu chuẩn.
- **Xác thực 3 Bước nghiêm ngặt:** Chỉ duy nhất **Chủ Server (Server Owner)** mới có quyền thực thi. Hệ thống yêu cầu xác nhận lần lượt qua 3 nút bấm tương tác (Bước 1: Giới thiệu quy mô $\rightarrow$ Bước 2: Cảnh báo mất dữ liệu cũ $\rightarrow$ Bước 3: Xác nhận tối hậu 100%).
- **Loại bỏ Master Key:** Hoàn toàn không cần ghi nhớ hay nhập mật mã thủ công, bảo vệ tối cao dựa trên quyền sở hữu Guild Owner.
- **Chống Rate Limit:** Quá trình xóa và tạo Category/Channel có độ trễ 0.3s đảm bảo không bị lỗi dở dang do Discord giới hạn tần suất tạo phòng.

---

### 7.8. Nhóm Quản Trị Tự Động (AutoMod)
- **Lọc từ cấm:** Tự động xóa tin nhắn vi phạm và nhắc nhở 5s.
- **Lọc link có Whitelist:** Chặn các liên kết ngoài, nhưng cho phép gửi link YouTube/SoundCloud/Spotify trong các kênh âm nhạc hoặc media.
- **Chống Spam:** Tự động phát hiện spam và phạt timeout 5 phút, tự động giải phóng bộ nhớ RAM.
- **Tích hợp Level / Rank thời gian thực:** Mỗi tin nhắn hợp lệ sẽ được cộng điểm XP vào SQLite. Khi đủ điểm, bot sẽ gửi thông báo chúc mừng thăng cấp.

---

## 8. Cơ Chế Xử Lý Lỗi Tập Trung & Bảo Vệ Tài Nguyên

1. **Bộ xử lý lỗi tập trung ([./utils/error_handler.py](./utils/error_handler.py)):**
   - Mọi lỗi phát sinh từ Slash Commands (thiếu quyền, lệnh đang cooldown, lỗi ngoại lệ) đều được hiển thị bằng Embed Discord thân thiện kèm mã định danh lỗi (`Error ID`) thay vì thông báo vô nghĩa *"The application did not respond"*.
2. **Khởi động sạch sẽ (Lifecycle Management):**
   - Mỗi lần khởi động, bot tự động quét và xóa sạch các file âm thanh `.mp3` hoặc file đệm `.tmp` còn sót lại trong thư mục `temp/`.
3. **Đóng tài nguyên an toàn (Graceful Shutdown):**
   - Khi nhận tín hiệu dừng (Ctrl+C hoặc tắt container), bot tự động ngắt kết nối Voice, giải phóng FFmpeg và đóng kết nối cơ sở dữ liệu SQLite an toàn.

---

## 9. Nhật Ký Cập Nhật & Tiến Độ Làm Việc (Worklog & Changelog)

| Phiên bản | Ngày cập nhật | Người thực hiện | Nội dung chi tiết |
| :---: | :---: | :---: | :--- |
| **v1.8.0** | 2026-11-23 | Antigravity & User | **Đổi tên bot thành SosaGallery, Nút bấm Music & Nâng cấp Help:**<br>• Đổi tên định danh bot thành **SosaGallery** trên toàn bộ hệ thống giao diện và log.<br>• Chuyển lệnh Voice TTS chính sang `/say` và `!say` (với alias `/speak`, `!speak`).<br>• Bổ sung nhóm nút bấm tương tác trực tiếp `MusicControlView` (⏯️ Tạm dừng/Tiếp tục, ⏭️ Bỏ qua, 📜 Xem hàng đợi, ⏹️ Dừng & Thoát) không cần gõ lệnh.<br>• Thêm tính năng đổi tiền tố lệnh cho từng server qua `/settings prefix` và `!prefix`.<br>• Viết lại toàn bộ hệ thống `/help` và `!help` với văn phong hướng dẫn người dùng thân thiện, dễ hiểu, hiển thị song song cả cú pháp Slash Command và Prefix. |
| **v1.7.0** | 2026-11-23 | Antigravity & User | **Hệ thống Marry House, Bói Tình Duyên & Thẻ Rank Canvas Đồ Họa:**<br>• Tích hợp bộ vẽ hình ảnh trực tiếp qua RAM với Pillow (`utils/canvas.py`): Thẻ Rank Chibi Gal Hiphop Neon và Banner Love Calculator Lunari-style pastel cute.<br>• Bổ sung module `cogs/marry/`: Lệnh `/lovec` (hỗ trợ `random` ghép đôi cùng server), `/marry` cầu hôn tương tác 💍, giao diện Ngôi Nhà Cặp Đôi 3 Tab (Trang Chủ, Album 6 ảnh, Ghi Chú).<br>• Lệnh tương tác tình cảm: `/kiss`, `/hug`, `/pat`, `/slap` tích lũy điểm thân mật (+10đ) và tự động nâng cấp 5 bậc Nhẫn Cưới.<br>• Mở rộng SQLite với bảng `marriages` và các hàm truy vấn quan hệ hôn nhân. |
| **v1.6.0** | 2026-11-23 | Antigravity & User | **Mặc định TẮT tính năng tự động khi vào server mới & Nhóm lệnh /settings:**<br>• Lắng nghe sự kiện `on_guild_join`: Tự động lưu cấu hình server vào SQLite với trạng thái TẮT toàn bộ tính năng tự động (AutoMod, Level/XP) để tôn trọng quyền riêng tư.<br>• Bổ sung nhóm lệnh `/settings` (`view`, `automod`, `level`) cho Quản trị viên chủ động BẬT/TẮT từng tính năng theo nhu cầu.<br>• Phân tách rạch ròi giữa lệnh chủ động (Slash Commands) và tiến trình chạy ngầm thời gian thực (Background Listeners). |
| **v1.5.0** | 2026-11-23 | Antigravity & User | **Xác thực 3 Bước & Hoàn thiện Slash Commands:**<br>• Nâng cấp `/setup-server` với quy trình xác thực 3 lần qua nút bấm tương tác (ConfirmationStepView), loại bỏ hoàn toàn Master Key.<br>• Bổ sung module `cogs/general/` với các lệnh `/help`, `/rank`, `/leaderboard`.<br>• Rà soát và cập nhật đầy đủ mô tả chi tiết, rõ ràng cho tất cả 11 Slash Commands.<br>• Tích hợp tính năng tự động thoát phòng thoại khi phòng trống người. |
| **v1.4.0** | 2026-11-23 | Antigravity & User | **Tích hợp SQLite bất đồng bộ (aiosqlite WAL Mode):** Xây dựng `DatabaseManager`, lệnh Admin `!sync`, `!reload`, `!status`, xử lý lỗi tập trung. |
| **v1.3.0** | 2026-11-23 | Antigravity & User | **Rà soát bảo mật & Khắc phục xung đột hệ thống:** Đồng bộ hóa Voice giữa TTS và Music, chuyển I/O sang `asyncio.to_thread`. |
| **v1.2.0** | 2026-11-23 | Antigravity & User | **Tái cấu trúc Feature-Folder:** Tách mỗi tính năng thành 1 folder riêng trong `cogs/`. |
| **v1.1.0** | 2026-11-23 | Antigravity & User | **Chuẩn hóa Enterprise Architecture:** Tách `.env`, `config.py`, `utils/logger.py`. |
| **v1.0.0** | 2026-07-10 | User | **Khởi tạo dự án ban đầu:** 4 cogs phẳng cơ bản. |

---

## 10. Kế Hoạch Phát Triển (Roadmap)

- [x] **Lệnh xem bảng xếp hạng `/leaderboard` & xem cấp độ `/rank`:** Tích hợp trực tiếp từ SQLite Database.
- [x] **Interactive Buttons cho Music:** Thêm hàng nút Pause, Resume, Skip, Stop trực tiếp dưới tin nhắn phản hồi của `/play`.
- [ ] **Hệ thống Welcome Banner:** Tạo ảnh thẻ chào mừng tự động lưu ảnh tạm trong `temp/`.
- [ ] **Hệ thống Ticket:** Mở kênh chat riêng với Ban Quản Trị bằng Discord Button.

---

<p align="center">
  Được phát triển với đam mê và tinh thần mã nguồn mở ❤️<br>
  <i>Tài liệu này được duy trì và cập nhật liên tục theo tiến trình phát triển dự án.</i>
</p>
