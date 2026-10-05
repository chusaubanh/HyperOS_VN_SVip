<div align="center">

# ⚡ HyperOS VN SVip
### Bộ Công Cụ Tối Ưu Hóa Xiaomi / Redmi / POCO Toàn Diện Nhất

[![GitHub License](https://img.shields.io/badge/license-MIT-blue.svg?style=for-the-badge)](LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.8+-yellow.svg?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/platform-Windows%2010%20%7C%2011-0078D6.svg?style=for-the-badge&logo=windows&logoColor=white)](https://www.microsoft.com/windows)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=for-the-badge)](CONTRIBUTING.md)
[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20A%20Coffee-Donate-orange.svg?style=for-the-badge&logo=buy-me-a-coffee&logoColor=white)](#-ủng-hộ-tác-giả-buy-me-a-coffee)

<p align="center">
  <b>Khắc phục triệt để trễ thông báo FCM • Việt hóa 100% ứng dụng • Chuyển Xiao AI sang Google Gemini • Tăng tốc hiệu năng • Quản lý Fastboot & Khóa lại Bootloader an toàn</b>
</p>

[Tính Năng](#-tính-năng-nổi-bật) • [Cài Đặt & Chạy](#-hướng-dẫn-khởi-chạy) • [Chuẩn Bị Điện Thoại](#-chuẩn-bị-trên-điện-thoại-xiaomi) • [Ủng Hộ Tác Giả](#-ủng-hộ-tác-giả-buy-me-a-coffee) • [Đóng Góp](#-đóng-góp)

</div>

---

## 📖 Giới Thiệu

**HyperOS VN SVip** là giải pháp all-in-one được xây dựng nhằm giải quyết các phiền toái phổ biến nhất của người dùng Xiaomi khi mua máy xách tay nội địa Trung Quốc. Công cụ hoạt động qua giao thức chuẩn **ADB & Fastboot** chính thức của Google, **không yêu cầu root**, hoàn toàn tự động hóa 1-click mà không cần gõ lệnh thủ công.

Giao diện ứng dụng được thiết kế theo tiêu chuẩn chống slop (**taste-skill**) mang phong cách Dark Engineering cao cấp (Linear / Apple Obsidian Bento Grid), mượt mà và trực quan.

---

## 🌟 Tính Năng Nổi Bật

### 1. 🔔 Duy Trì Kết Nối Google FCM Thời Gian Thực (Fix Trễ Thông Báo)
* Tự động đưa `Google Play Services` vào danh sách trắng Doze (Chống ngủ đông hệ thống).
* Vô hiệu hóa cơ chế ngắt socket TCP `Millet` của Xiaomi HyperOS.
* Tự động nạp trực tiếp binary `shizuku_starter` qua ADB và tích hợp tiện ích **HyperOS FCM Fix**.
* Cung cấp phím tắt mở trực tiếp trình chẩn đoán **Google FCM Diagnostics (`*#*#426#*#*`)** trên màn hình điện thoại.

### 2. 🌐 Việt Hóa 100% Ứng Dụng (MoreLocale 2 & Locale vi-VN)
* Cài đặt tự động MoreLocale 2 và gán đặc quyền hệ thống `android.permission.CHANGE_CONFIGURATION`.
* Cấu hình vùng hệ thống sang `vi-VN`: Toàn bộ ứng dụng cài từ Google Play Store (Zalo, Facebook, TikTok, Ngân hàng, Google Maps, Chrome...) tự động nhận diện giao diện Tiếng Việt hoàn toàn.

### 3. ✨ Thay Thế Xiao AI Bằng Google Gemini
* Vô hiệu hóa triệt để trợ lý ảo nội địa Trung Quốc **Xiao AI** (`com.miui.voiceassist`, `com.miui.voicetrigger`, `com.xiaomi.mibrain.speech`).
* Gán **Google Voice Interaction** làm Trợ lý số mặc định (Digital Assistant).
* Gán phím **Nguồn (giữ 0.5s)** hoặc cử chỉ vuốt góc để đánh thức nhanh Google Gemini (phím Nguồn + Tăng âm lượng giữ chức năng Power Menu tắt/mở máy).
* Mở khóa quyền chạy nền tối đa cho Gemini phản hồi tức thì.

### 4. ⚡ Tối Ưu Hiệu Năng & Pin (Performance Boost)
* **Tắt RAM ảo (RAM Extension):** Giảm hao mòn chip nhớ UFS và chấm dứt hiện tượng reload giật lag khi đa nhiệm.
* **Vô hiệu hóa Joyose:** Loại bỏ giới hạn bóp hiệu năng và chặn Xiaomi tự dìm tối màn hình ngoài trời nắng gắt.
* **Biên dịch mã máy Android Runtime (ART AOT):** Tối ưu hóa trước bytecode giúp mọi ứng dụng khởi động tức thì.
* **Thực thi FSTRIM:** Tự động dọn rác và sắp xếp lại khối chip nhớ phần cứng.

### 5. 🗑️ Gỡ Bỏ Bloatware Nội Địa Trung Quốc (Debloat Engine)
* Dọn dẹp sạch các ứng dụng rác, trang vàng TQ, kho nhạc/video TQ, bàn phím Sogou, Baidu...
* Bộ lọc trực quan cho phép tùy chọn danh sách an toàn 100%.

### 6. 🔒 Khóa USB Debug & Developer Options (Bảo Mật Ngân Hàng / VNeID)
* Tự động tắt ADB và ẩn menu Cài đặt nhà phát triển sau khi tối ưu xong.
* Giúp điện thoại vượt qua cơ chế kiểm tra an ninh của các App Ngân hàng (Techcombank, Vietcombank, MB Bank, Cake, VNeID, ZaloPay...).

### 7. 🛠️ Về ROM Gốc & Khóa Lại Bootloader (Fastboot Engine)
* **Lộ trình 5 bước tự động hóa:** Chuyển máy vào Fastboot, quét thông số phần cứng, mã máy (Codename), tình trạng Bootloader (`UNLOCKED` / `LOCKED`) và Anti-Rollback (ARB) bằng 1-click.
* Tích hợp link tra cứu ROM chính hãng trên **Mifirm.net**, **XM Firmware Updater** và **MiFlash Tool**.
* Hướng dẫn trực quan quy tắc chọn chế độ flash (`clean all and lock` vs `clean all`) để tránh rủi ro brick máy.
* Lệnh 1-click gửi tín hiệu khóa lại Bootloader (`fastboot flashing lock`) kèm hướng dẫn phím cứng chi tiết.

---

## 🚀 Hướng Dẫn Khởi Chạy

### Yêu Cầu Hệ Thống
* Hệ điều hành Windows 10 hoặc Windows 11.
* Python 3.8 trở lên (Khuyên dùng Python 3.10+).

### Cách 1: Khởi Chạy Nhanh (1-Click)
Sau khi tải mã nguồn về máy, bạn chỉ cần **click đúp vào 1 trong 2 file**:
* 👉 **`Mo_Ung_Dung.vbs`** *(Khuyên dùng)*: Mở giao diện ngay lập tức dưới dạng Cửa sổ ứng dụng Native riêng biệt (không thanh URL, không tab, không nháy màn hình đen CMD).
* 👉 **`run.bat`**: Khởi chạy nhanh qua kịch bản Batch.

### Cách 2: Khởi Chạy Bằng Dòng Lệnh
```bash
# 1. Clone repository
git clone https://github.com/chusaubanh/HyperOS_VN_SVip.git
cd HyperOS_VN_SVip

# 2. Cài đặt thư viện phụ thuộc
pip install -r requirements.txt

# 3. Khởi chạy máy chủ
python main.py
```

---

## 📱 Chuẩn Bị Trên Điện Thoại Xiaomi

1. Mở **Cài đặt (Settings)** > **Giới thiệu điện thoại (About phone)** > Nhấn liên tục 7 lần vào dòng **Phiên bản OS / HyperOS** cho đến khi có thông báo *"Bạn đã là nhà phát triển"*.
2. Vào **Cài đặt bổ sung (Additional settings)** > **Tùy chọn nhà phát triển (Developer options)** > Bật 3 mục:
   * ✅ **Gỡ lỗi USB (USB debugging)**
   * ✅ **Cài đặt qua USB (Install via USB)**
   * ✅ **Gỡ lỗi USB - Cài đặt bảo mật (USB debugging - Security settings)**
3. Cắm cáp USB nối điện thoại với máy tính. Trên màn hình điện thoại sẽ hiện hộp thoại xác nhận RSA: tích chọn **"Luôn cho phép từ máy tính này"** và nhấn **OK**.

---

## ☕ Ủng Hộ Tác Giả & Góp Ý Phát Triển (Buy Me A Coffee & Contact)

Nếu bạn thấy công cụ **HyperOS VN SVip** hữu ích, giúp bạn tiết kiệm thời gian hoặc tối ưu chiếc điện thoại của mình ưng ý hơn, bạn có thể **ủng hộ mình một ly cafe nhé ☕!**

Nếu bạn có ý tưởng muốn phát triển thêm tính năng gì, cần tối ưu lại điều gì hay gặp bất kỳ lỗi nào trong quá trình sử dụng, cứ thoải mái liên hệ hoặc nhắn tin riêng cho mình qua Facebook:

👉 **Facebook Cá Nhân:** [facebook.com/chu6banh](https://www.facebook.com/chu6banh)

<div align="center">

<img src="assets/donate_qr_clean.jpg" alt="Mã QR Chuyển Khoản Techcombank - DO THE ANH PHUONG" width="280" style="border-radius: 12px; box-shadow: 0 8px 24px rgba(0,0,0,0.15);" />

<br/>

| Thông Tin Chuyển Khoản | Chi Tiết |
| :--- | :--- |
| **Ngân hàng** | **Techcombank (TCB)** |
| **Chủ tài khoản** | **DO THE ANH PHUONG** |
| **Số tài khoản** | `1903 7923 5280 26` *(Sao chép dễ dàng)* |

<p><i>☕ Cảm ơn bạn rất nhiều vì đã luôn đồng hành, ủng hộ và đóng góp ý kiến cho dự án! ❤️</i></p>

</div>

---

## 🤝 Đóng Góp

Mọi đóng góp nhằm cải thiện công cụ đều rất được trân trọng! Vui lòng đọc [CONTRIBUTING.md](CONTRIBUTING.md) để biết cách tham gia phát triển dự án.

## ⚖️ Giấy Phép (License)

Dự án được phân phối dưới giấy phép **MIT License**. Xem file [LICENSE](LICENSE) để biết thêm chi tiết.
