# ⚡ HyperOS VN SVip - Xiaomi ROM Precision Optimizer

Bộ công cụ tối ưu hóa hệ thống, duy trì kết nối **Google FCM (Khắc phục trễ thông báo)**, **Việt Hóa 100% ứng dụng**, **Tối ưu hiệu năng** và **Quản lý Fastboot / Khóa lại Bootloader** an toàn cho các thiết bị Xiaomi / Redmi / POCO chạy ROM nội địa Trung Quốc (MIUI & HyperOS).

Được thiết kế theo tiêu chuẩn chống slop (**taste-skill**) với phong cách Linear / Dark Engineering, tự động hóa toàn bộ thao tác một chạm (1-click) qua giao thức ADB & Fastboot chính thức của Google.

---

## 🌟 Tính Năng Nổi Bật (SVIP Engine)

1. **Duy Trì Kết Nối Google FCM Thời Gian Thực (Chống dồn / chậm thông báo):**
   * Đưa `Google Play Services` vào danh sách trắng Doze (Chống ngủ đông hệ thống).
   * Tắt cơ chế ngắt socket TCP `Millet` của Xiaomi HyperOS.
   * Tự động kích hoạt **Shizuku Server** bằng cách nạp trực tiếp binary `shizuku_starter` qua ADB.
   * Tích hợp công cụ chuyên dụng **HyperOS FCM Fix**.

2. **Việt Hóa Toàn Diện Ứng Dụng (MoreLocale 2 & Locale vi-VN):**
   * Tự động cài đặt MoreLocale 2 và cấp đặc quyền hệ thống `CHANGE_CONFIGURATION`.
   * Thiết lập vùng hệ thống sang `vi-VN` để **100% ứng dụng tải từ CH Play (Zalo, Facebook, TikTok, Ngân hàng, Maps, Chrome...)** tự động hiển thị Tiếng Việt.

3. **Chuyển Đổi AI Hệ Thống - Google Gemini (Thay Thế Xiao AI):**
   * Vô hiệu hóa triệt để trợ lý ảo tiếng Trung **Xiao AI** (`com.miui.voiceassist`, `com.miui.voicetrigger`, `com.xiaomi.mibrain.speech`).
   * Gán dịch vụ **Google Voice Interaction** làm Trợ lý số mặc định (Digital Assistant).
   * Gán phím **Nguồn (giữ 0.5s)** hoặc cử chỉ vuốt góc để mở nhanh Gemini / Google Assistant (phím Nguồn + Tăng âm lượng giữ chức năng Power Menu).
   * Cấp quyền Doze Whitelist & AppOps chạy nền không giới hạn giúp Gemini phản hồi tức thì.

4. **Tối Ưu Hiệu Năng Hệ Thống (Performance Boost):**
   * Tắt RAM Extension (RAM ảo) để ngừng swap bộ nhớ, giảm giật lag khi đa nhiệm.
   * Vô hiệu hóa Joyose nhằm loại bỏ giới hạn throttle hiệu năng và chặn tự dìm tối màn hình ngoài trời nắng.
   * Biên dịch ART AOT (`cmd package compile -m speed-profile -a`) tối ưu hóa bytecode cho toàn bộ ứng dụng mở tức thì.
   * Thực thi `fstrim` dọn dẹp phân mảnh chip nhớ UFS/eMMC.

5. **Gỡ Bỏ Bloatware Nội Địa Trung Quốc (Debloat Engine):**
   * Gỡ sạch các ứng dụng rác, trang vàng danh bạ, nhạc/video TQ, bàn phím Sogou, Baidu...
   * Cửa sổ tùy chỉnh tìm kiếm và lọc danh sách ứng dụng an toàn 100%.

6. **Khóa USB Debug & Developer Options (Bảo Mật Ngân Hàng / VNeID):**
   * Tự động tắt ADB và ẩn menu Cài đặt nhà phát triển sau khi tối ưu xong.
   * Giúp thiết bị vượt qua cơ chế kiểm tra bảo mật của các ứng dụng ngân hàng (VNeID, Techcombank, Vietcombank, Cake, MB Bank, ZaloPay...).

7. **Về ROM Gốc & Khóa Bootloader (Fastboot Engine):**
   * Tự động chuyển thiết bị vào chế độ Fastboot chỉ với 1 cú click.
   * Quét và đọc chính xác thông số phần cứng: Cổng Serial, Mã máy (Codename), tình trạng Bootloader (`UNLOCKED` / `LOCKED`), Anti-Rollback (ARB).
   * Tích hợp liên kết tra cứu ROM chính hãng trên Mifirm.net, XM Firmware Updater và MiFlash Tool.
   * Hướng dẫn trực quan quy tắc chọn chế độ flash (`clean all and lock` vs `clean all`) để tránh brick máy.
   * Lệnh 1-click gửi tín hiệu khóa lại Bootloader (`fastboot flashing lock`) kèm hướng dẫn phím cứng trên màn hình.

8. **Chạy Tất Cả (Pipeline Automation):**
   * Thực thi toàn bộ quy trình tối ưu hóa liên hoàn chỉ bằng một nút bấm.

---

## 🚀 Hướng Dẫn Sử Dụng

### Yêu Cầu Trên Máy Tính
* Hệ điều hành Windows 10 / 11.
* Python 3.8+ (khuyên dùng Python 3.10 trở lên).

### Khởi Chạy Nhanh
Chỉ cần **click đúp vào 1 trong 2 file** trong thư mục:
* 👉 **`Mo_Ung_Dung.vbs`** *(Khuyên dùng)*: Mở giao diện ngay lập tức dưới dạng cửa sổ ứng dụng độc lập (Native Window), không nhấp nháy màn hình đen.
* 👉 **`run.bat`**: Khởi chạy nhanh qua script lệnh.

Hoặc khởi chạy thủ công bằng dòng lệnh:
```bash
pip install -r requirements.txt
python main.py
```

---

## 📱 Chuẩn Bị Trên Điện Thoại Xiaomi

1. Mở **Cài đặt** > **Giới thiệu điện thoại** > Nhấn liên tục 7 lần vào dòng **Phiên bản OS / HyperOS** để kích hoạt chế độ nhà phát triển.
2. Vào **Cài đặt bổ sung** > **Tùy chọn nhà phát triển** > Bật 3 mục:
   * ✅ **Gỡ lỗi USB (USB debugging)**
   * ✅ **Cài đặt qua USB (Install via USB)**
   * ✅ **Gỡ lỗi USB - Cài đặt bảo mật (USB debugging - Security settings)** *(Bắt buộc để phân quyền)*
3. Cắm cáp USB nối điện thoại với máy tính, trên màn hình điện thoại chọn **"Luôn cho phép từ máy tính này"** và nhấn **OK**.

---

## ⚖️ Miễn Trừ Trách Nhiệm (Disclaimer)

* HyperOS VN SVip là công cụ tối ưu hóa thực hiện thông qua giao thức ADB và Fastboot chính thức của Android / Google.
* Hãy sao lưu dữ liệu quan trọng trước khi can thiệp sâu vào hệ thống hoặc nạp ROM / khóa Bootloader.
* Người dùng chịu trách nhiệm với các thao tác lựa chọn trên thiết bị của mình.
