# 🎨 Hướng Dẫn Tải & Tùy Biến Template Đồ Họa Cho Bot

Hệ thống SosaPy hỗ trợ cơ chế **Hybrid Template**:
- Nếu bạn bỏ file ảnh tĩnh thiết kế sẵn vào thư mục này, bot sẽ dùng nó làm phôi nền và ghép avatar, tên, số %, level lên ảnh.
- Nếu không có file, bot sẽ tự động vẽ bằng code (chế độ fallback).

---

## 1. Template Bói Tình Duyên (`love_template.png`)

- **Tên file bắt buộc:** `love_template.png`
- **Kích thước chuẩn khuyến nghị:** `840 x 360` px (Định dạng PNG chất lượng cao)
- **Tọa độ căn chỉnh trên template:**
  - **Ô Avatar 1 (Người thứ nhất):** Góc trái tại tọa độ `(X: 120, Y: 105)`, đường kính avatar là `130px`.
  - **Ô Avatar 2 (Người thứ hai):** Góc phải tại tọa độ `(X: 590, Y: 105)`, đường kính avatar là `130px`.
  - **Trái tim ở giữa:** Tâm nằm tại `(X: 420, Y: 170)` — Bot sẽ in con số `%` vào đây.
  - **Tên 2 người:** Bot sẽ in bên dưới 2 avatar (tại `Y: 250`).
  - **Thanh đo Love Meter Bar:** Nằm ở đáy tại `(X: 260, Y: 285)`, chiều rộng `320px`, chiều cao `20px`. Bạn có thể vẽ sẵn khung rãnh rỗng, bot sẽ đổ màu tiến trình theo phần trăm vào rãnh này.

---

## 2. Template Thẻ Rank Cá Nhân (`rank_template.png`)

- **Tên file bắt buộc:** `rank_template.png`
- **Kích thước chuẩn khuyến nghị:** `880 x 260` px (Định dạng PNG)
- **Tọa độ căn chỉnh:**
  - **Ô Avatar:** Góc trái tại `(X: 50, Y: 55)`, đường kính avatar là `150px`.
  - **Tên người dùng:** Bắt đầu từ `(X: 240, Y: 60)`.
  - **Thông số Rank & Level:** Nằm ở góc trên bên phải.
  - **Thanh tiến trình XP:** Bắt đầu từ `(X: 240, Y: 150)` với chiều rộng `590px`, cao `32px`.

---

💡 **Mẹo:** Bạn có thể dùng Figma, Photoshop hoặc Canva để vẽ hình chibi, thêm hoa tuyết, trái tim, góc cạnh hiphop/anime gal tùy thích rồi xuất ra file PNG đặt vào đây!
