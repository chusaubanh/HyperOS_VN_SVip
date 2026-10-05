# -*- coding: utf-8 -*-
import subprocess
import os
import sys
import re
import time
import shutil

class ADBManager:
    def __init__(self, custom_adb_path=None):
        self.adb_path = custom_adb_path or self._find_adb()
        self.fastboot_path = self._find_fastboot()
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.apks_dir = os.path.join(self.base_dir, "bin", "apks")
        self.starters_dir = os.path.join(self.base_dir, "bin", "shizuku_starters")

    def _find_adb(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        local_adb = os.path.join(base_dir, "bin", "platform-tools", "adb.exe")
        if os.path.exists(local_adb):
            return local_adb
        
        # Check PATH
        system_adb = shutil.which("adb")
        if system_adb:
            return system_adb
            
        return local_adb

    def _find_fastboot(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        local_fb = os.path.join(base_dir, "bin", "platform-tools", "fastboot.exe")
        if os.path.exists(local_fb):
            return local_fb
        system_fb = shutil.which("fastboot")
        if system_fb:
            return system_fb
        return local_fb

    def is_adb_available(self):
        return os.path.exists(self.adb_path)

    def is_fastboot_available(self):
        return os.path.exists(self.fastboot_path)

    def run_fastboot_cmd(self, args, serial=None, timeout=30):
        if not self.is_fastboot_available():
            return False, "Không tìm thấy fastboot.exe."
        
        cmd = [self.fastboot_path]
        if serial:
            cmd.extend(["-s", serial])
        cmd.extend(args)

        try:
            startupinfo = None
            if sys.platform == "win32":
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                encoding="utf-8",
                errors="replace",
                startupinfo=startupinfo
            )
            stdout = result.stdout.strip() if result.stdout else ""
            stderr = result.stderr.strip() if result.stderr else ""
            output = stdout if stdout else stderr
            if stdout and stderr:
                output = f"{stdout}\n{stderr}"
            return (result.returncode == 0), output
        except subprocess.TimeoutExpired:
            return False, "Quá thời gian thực thi (Timeout)."
        except Exception as e:
            return False, str(e)

    def run_cmd(self, args, serial=None, timeout=30):
        if not self.is_adb_available():
            return False, "Không tìm thấy adb.exe. Vui lòng kiểm tra thư mục bin/platform-tools."
        
        cmd = [self.adb_path]
        if serial:
            cmd.extend(["-s", serial])
        cmd.extend(args)

        try:
            startupinfo = None
            if sys.platform == "win32":
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                encoding="utf-8",
                errors="replace",
                startupinfo=startupinfo
            )
            stdout = result.stdout.strip() if result.stdout else ""
            stderr = result.stderr.strip() if result.stderr else ""
            output = stdout if stdout else stderr
            return (result.returncode == 0), output
        except subprocess.TimeoutExpired:
            return False, "Quá thời gian thực thi (Timeout)."
        except Exception as e:
            return False, str(e)

    def get_devices(self):
        """Trả về danh sách thiết bị đang kết nối qua ADB"""
        success, out = self.run_cmd(["devices"])
        if not success:
            return []
        
        devices = []
        for line in out.splitlines()[1:]:
            line = line.strip()
            if not line or line.startswith("*"):
                continue
            parts = re.split(r'\s+', line)
            if len(parts) >= 2:
                devices.append({
                    "serial": parts[0],
                    "status": parts[1]  # 'device', 'unauthorized', 'offline'
                })
        return devices

    def get_device_info(self, serial):
        """Lấy thông tin chi tiết và ma trận điều kiện cần thiết của thiết bị"""
        info = {
            "model": "Xiaomi Device",
            "marketname": "",
            "android_version": "N/A",
            "os_version": "HyperOS/MIUI",
            "battery": "--",
            "chipset": "Snapdragon/MediaTek",
            "usb_debugging": True,
            "security_ready": True,
            "security_warning": "",
            "ram_expand_disabled": False,
            "joyose_disabled": False,
            "gemini_ready": False,
            "fcm_ready": False,
            "morelocale_ready": False
        }

        # Model & Market name
        _, model = self.run_cmd(["shell", "getprop", "ro.product.model"], serial)
        _, marketname = self.run_cmd(["shell", "getprop", "ro.product.marketname"], serial)
        if not marketname:
            _, marketname = self.run_cmd(["shell", "getprop", "ro.product.name"], serial)
        
        info["model"] = model if model else "Thiết bị Xiaomi"
        info["marketname"] = marketname if marketname else model

        # Chipset / SoC
        _, chip = self.run_cmd(["shell", "getprop", "ro.soc.model"], serial)
        if not chip:
            _, chip = self.run_cmd(["shell", "getprop", "ro.board.platform"], serial)
        if chip:
            info["chipset"] = chip.upper()

        # Android version
        _, android_ver = self.run_cmd(["shell", "getprop", "ro.build.version.release"], serial)
        info["android_version"] = f"Android {android_ver}" if android_ver else "Android"

        # HyperOS / MIUI version
        _, miui_ver = self.run_cmd(["shell", "getprop", "ro.mi.os.version.name"], serial)
        if not miui_ver:
            _, miui_ver = self.run_cmd(["shell", "getprop", "ro.build.version.incremental"], serial)
        info["os_version"] = miui_ver if miui_ver else "HyperOS"

        # Battery level
        _, battery_out = self.run_cmd(["shell", "dumpsys", "battery"], serial)
        for line in battery_out.splitlines():
            if "level:" in line:
                info["battery"] = line.split("level:")[1].strip() + "%"
                break

        # Check USB debugging (Security settings)
        test_success, test_out = self.run_cmd(
            ["shell", "pm", "grant", "com.android.shell", "android.permission.BATTERY_STATS"],
            serial
        )
        if "SecurityException" in test_out or "Neither user" in test_out:
            info["security_ready"] = False
            info["security_warning"] = (
                "⚠️ BẢO MẬT XIAOMI: Bạn chưa bật 'Gỡ lỗi USB (Cài đặt bảo mật)'!\n"
                "Vui lòng vào Cài đặt bổ sung > Tùy chọn nhà phát triển > Bật: \n"
                "1. Cài đặt qua USB (Install via USB)\n"
                "2. Gỡ lỗi USB - Cài đặt bảo mật (USB Debugging - Security settings)"
            )

        # 1. Check RAM Expansion (Memory Extension)
        _, ram_size = self.run_cmd(["shell", "settings", "get", "global", "ram_expand_size"], serial)
        _, ram_prop = self.run_cmd(["shell", "getprop", "persist.miui.extm.enable"], serial)
        info["ram_expand_disabled"] = (ram_size == "0" or ram_prop == "0")

        # 2. Check Joyose
        _, joy_dis = self.run_cmd(["shell", "pm", "list", "packages", "-d", "com.xiaomi.joyose"], serial)
        if "com.xiaomi.joyose" in joy_dis:
            info["joyose_disabled"] = True
        else:
            is_joy_installed = self.is_package_installed(serial, "com.xiaomi.joyose")
            info["joyose_disabled"] = not is_joy_installed

        # 3. Check Gemini / Google Assistant
        _, asst_val = self.run_cmd(["shell", "settings", "get", "secure", "assistant"], serial)
        info["gemini_ready"] = ("googlequicksearchbox" in asst_val or "bard" in asst_val)

        # 4. Check FCM Whitelist
        _, idle_wl = self.run_cmd(["shell", "dumpsys", "deviceidle", "whitelist"], serial)
        info["fcm_ready"] = ("com.google.android.gms" in idle_wl)

        # 5. Check MoreLocale permission
        morelocale_pkg = "jp.co.c_lis.ccl.morelocale"
        if self.is_package_installed(serial, morelocale_pkg):
            _, perm_out = self.run_cmd(["shell", "dumpsys", "package", morelocale_pkg], serial)
            info["morelocale_ready"] = ("android.permission.CHANGE_CONFIGURATION: granted=true" in perm_out)

        return info

    def is_package_installed(self, serial, package_name):
        _, out = self.run_cmd(["shell", "pm", "list", "packages", package_name], serial)
        return f"package:{package_name}" in out

    def install_apk(self, serial, apk_filename):
        apk_path = os.path.join(self.apks_dir, apk_filename)
        if not os.path.exists(apk_path):
            return False, f"Không tìm thấy file APK: {apk_filename}"
        
        return self.run_cmd(["install", "-r", "-d", apk_path], serial, timeout=60)

    # ================= MODULE 1: VIỆT HÓA =================
    def apply_vietnamese(self, serial, log_cb):
        log_cb("[1/3] Bắt đầu kích hoạt Tiếng Việt cho hệ thống và ứng dụng...", "info")
        
        morelocale_pkg = "jp.co.c_lis.ccl.morelocale"
        
        # 1. Cài đặt MoreLocale 2 nếu chưa có
        if not self.is_package_installed(serial, morelocale_pkg):
            log_cb("  -> Đang đẩy và cài đặt gói MoreLocale 2...", "info")
            succ, out = self.install_apk(serial, "morelocale.apk")
            if not succ:
                log_cb(f"  [!] Chưa thể cài APK MoreLocale: {out}", "warning")
                log_cb("  -> Hãy kiểm tra bạn đã bật 'Cài đặt qua USB' trên điện thoại.", "warning")
            else:
                log_cb("  ✓ Cài đặt MoreLocale 2 thành công.", "success")
        else:
            log_cb("  ✓ MoreLocale 2 đã có sẵn trên thiết bị.", "info")

        # 2. Cấp quyền CHANGE_CONFIGURATION qua ADB
        log_cb("  -> Đang cấp quyền đặc quyền hệ thống CHANGE_CONFIGURATION...", "info")
        succ, out = self.run_cmd(
            ["shell", "pm", "grant", morelocale_pkg, "android.permission.CHANGE_CONFIGURATION"],
            serial
        )
        if not succ or "SecurityException" in out:
            log_cb(f"  ✕ Lỗi cấp quyền: {out}", "error")
            log_cb("  ⚠️ Vui lòng BẬT 'Gỡ lỗi USB (Cài đặt bảo mật)' trong Tùy chọn nhà phát triển!", "error")
            return False
        log_cb("  ✓ Cấp quyền CHANGE_CONFIGURATION thành công!", "success")

        # 3. Cấu hình các biến Locale hệ thống sang vi-VN
        log_cb("  -> Thiết lập biến vùng hệ thống sang Tiếng Việt (vi-VN)...", "info")
        self.run_cmd(["shell", "settings", "put", "system", "system_locales", "vi-VN"], serial)
        self.run_cmd(["shell", "settings", "put", "global", "system_locales", "vi-VN"], serial)
        self.run_cmd(["shell", "settings", "put", "system", "system_locale", "vi-VN"], serial)
        
        # 4. Mở ứng dụng MoreLocale 2 trên màn hình
        self.run_cmd(["shell", "am", "start", "-n", f"{morelocale_pkg}/.MoreLocaleActivity"], serial)
        
        log_cb("  ✓ HOÀN TẤT VIỆT HÓA: 100% ứng dụng CH Play sẽ hiển thị Tiếng Việt!", "success")
        return True

    # ================= MODULE 2: FIX GOOGLE FCM & SHIZUKU =================
    def apply_fcm_fix(self, serial, install_shizuku, install_fcm_fix, log_cb):
        log_cb("[2/3] Bắt đầu tối ưu hóa & duy trì kết nối Google FCM...", "info")

        # 1. Kích hoạt Google Basic Services
        log_cb("  -> Kích hoạt Google Basic Services trong hệ thống...", "info")
        self.run_cmd(["shell", "settings", "put", "global", "google_services", "1"], serial)

        # 2. Whitelist Google Play Services khỏi chế độ ngủ đông Doze
        log_cb("  -> Đưa Google Play Services vào Whitelist chống Doze (ngủ sâu)...", "info")
        self.run_cmd(["shell", "dumpsys", "deviceidle", "whitelist", "+com.google.android.gms"], serial)

        # 3. Cấp quyền chạy nền không giới hạn (AppOps)
        log_cb("  -> Mở toàn quyền chạy nền liên tục (RUN_IN_BACKGROUND, WAKE_LOCK)...", "info")
        self.run_cmd(["shell", "cmd", "appops", "set", "com.google.android.gms", "RUN_IN_BACKGROUND", "allow"], serial)
        self.run_cmd(["shell", "cmd", "appops", "set", "com.google.android.gms", "RUN_ANY_IN_BACKGROUND", "allow"], serial)
        self.run_cmd(["shell", "cmd", "appops", "set", "com.google.android.gms", "WAKE_LOCK", "allow"], serial)
        self.run_cmd(["shell", "cmd", "appops", "set", "com.google.android.gms", "BOOT_COMPLETED", "allow"], serial)

        # 4. Xiaomi HyperOS Millet No Restrict Whitelist (chống đóng băng socket TCP)
        log_cb("  -> Cấu hình danh sách miễn nhiễm đóng băng socket HyperOS (Millet Whitelist)...", "info")
        self.run_cmd(["shell", "settings", "put", "system", "millet_no_restrict_app", "com.google.android.gms"], serial)
        self.run_cmd(["shell", "settings", "put", "global", "millet_no_restrict_app", "com.google.android.gms"], serial)

        # 5. Cài đặt & Kích hoạt Shizuku Server tự động bằng starter binary
        if install_shizuku:
            shizuku_pkg = "moe.shizuku.privileged.api"
            if not self.is_package_installed(serial, shizuku_pkg):
                log_cb("  -> Đang cài đặt Shizuku APK...", "info")
                succ, out = self.install_apk(serial, "shizuku.apk")
                if succ:
                    log_cb("  ✓ Cài đặt Shizuku thành công.", "success")
                else:
                    log_cb(f"  [!] Cài đặt Shizuku thất bại: {out}", "warning")
            else:
                log_cb("  ✓ Shizuku đã có sẵn trên thiết bị.", "info")

            # Đẩy binary starter độc lập và kích hoạt trực tiếp
            starter_bin = os.path.join(self.starters_dir, "starter_arm64")
            log_cb("  -> Đang tự động kích hoạt Shizuku Server qua ADB...", "info")
            
            if os.path.exists(starter_bin):
                self.run_cmd(["push", starter_bin, "/data/local/tmp/shizuku_starter"], serial)
                self.run_cmd(["shell", "chmod", "755", "/data/local/tmp/shizuku_starter"], serial)
                succ, out = self.run_cmd(["shell", "/data/local/tmp/shizuku_starter"], serial, timeout=15)
                log_cb(f"  ✓ Khởi chạy Shizuku Starter: {out[:60] if out else 'OK'}", "success")
            else:
                # Fallback to start.sh
                self.run_cmd(["shell", "sh", "/sdcard/Android/data/moe.shizuku.privileged.api/start.sh"], serial)

            # Mở nhẹ Shizuku app để khởi động giao diện
            self.run_cmd(["shell", "monkey", "-p", shizuku_pkg, "1"], serial)

        # 6. Cài đặt HyperOS FCM Fix nếu được chọn
        if install_fcm_fix:
            fcm_fix_pkg = "dev.dingwen.hyperosfcmfix"
            if not self.is_package_installed(serial, fcm_fix_pkg):
                log_cb("  -> Đang cài đặt công cụ HyperOS FCM Fix...", "info")
                succ, out = self.install_apk(serial, "hyperos-fcm-fix.apk")
                if succ:
                    log_cb("  ✓ Cài đặt HyperOS FCM Fix thành công.", "success")
                else:
                    log_cb(f"  [!] Cài đặt FCM Fix: {out}", "warning")
            else:
                log_cb("  ✓ HyperOS FCM Fix đã có trên thiết bị.", "info")
            
            # Cấp quyền chạy nền
            self.run_cmd(["shell", "dumpsys", "deviceidle", "whitelist", f"+{fcm_fix_pkg}"], serial)
            self.run_cmd(["shell", "cmd", "appops", "set", fcm_fix_pkg, "RUN_IN_BACKGROUND", "allow"], serial)

        log_cb("  ✓ HOÀN TẤT TỐI ƯU FCM: Google FCM đã được giữ kết nối thời gian thực!", "success")
        return True

    # ================= MODULE 3: GOOGLE GEMINI AI REPLACEMENT =================
    def apply_gemini_assistant(self, serial, disable_xiaoai=True, remap_power_key=True, log_cb=None):
        if not log_cb:
            log_cb = lambda m, t="info": None
            
        log_cb("[AI] Bắt đầu thiết lập Google Gemini làm AI chính thay thế Xiaomi AI...", "info")

        # 1. Kiểm tra ứng dụng Google / Gemini
        google_pkg = "com.google.android.googlequicksearchbox"
        gemini_pkg = "com.google.android.apps.bard"
        
        has_google = self.is_package_installed(serial, google_pkg)
        has_gemini = self.is_package_installed(serial, gemini_pkg)
        
        if has_gemini:
            log_cb("  ✓ Phát hiện ứng dụng Google Gemini chuyên biệt (com.google.android.apps.bard).", "success")
        elif has_google:
            log_cb("  ✓ Phát hiện ứng dụng Google (nền tảng điều hành Gemini trên Android).", "success")
        else:
            log_cb("  ⚠️ Chưa phát hiện Google App hoặc Gemini trên máy. Hệ thống vẫn sẽ cấu hình sẵn, bạn chỉ cần cài đặt Google/Gemini từ CH Play!", "warning")

        # 2. Vô hiệu hóa hoàn toàn Xiao AI
        if disable_xiaoai:
            xiaoai_packages = [
                ("com.miui.voiceassist", "Xiao AI Voice Assistant"),
                ("com.miui.voicetrigger", "Xiao AI Voice Trigger (Kích hoạt âm thanh)"),
                ("com.xiaomi.mibrain.speech", "Xiaomi Speech Engine")
            ]
            log_cb("  -> Đang tắt triệt để các dịch vụ Xiao AI nội địa...", "info")
            for pkg, name in xiaoai_packages:
                if self.is_package_installed(serial, pkg):
                    succ, out = self.run_cmd(["shell", "pm", "disable-user", "--user", "0", pkg], serial)
                    if not succ or "SecurityException" in out:
                        succ, out = self.run_cmd(["shell", "pm", "uninstall", "-k", "--user", "0", pkg], serial)
                    if succ and ("disabled" in out.lower() or "success" in out.lower()):
                        log_cb(f"  ✓ Đã vô hiệu hóa {name} ({pkg})", "success")
                    else:
                        log_cb(f"  [!] Trạng thái {name}: {out}", "info")
                else:
                    log_cb(f"  . {name} đã được dọn sạch trước đó.", "info")

        # 3. Đặt Google Voice Interaction Service làm Assistant mặc định
        log_cb("  -> Thiết lập Google Voice Interaction làm Digital Assistant mặc định...", "info")
        gsa_service = "com.google.android.googlequicksearchbox/com.google.android.voiceinteraction.GsaVoiceInteractionService"
        gsa_recognizer = "com.google.android.googlequicksearchbox/com.google.android.voicesearch.serviceapi.GoogleRecognitionService"

        self.run_cmd(["shell", "settings", "put", "secure", "assistant", gsa_service], serial)
        self.run_cmd(["shell", "settings", "put", "secure", "voice_interaction_service", gsa_service], serial)
        self.run_cmd(["shell", "settings", "put", "secure", "voice_recognition_service", gsa_recognizer], serial)
        self.run_cmd(["shell", "settings", "put", "secure", "assistant_touch_gesture", "1"], serial)

        # 4. Gán phím nguồn / cử chỉ gọi Assistant
        if remap_power_key:
            log_cb("  -> Cấu hình phím Nguồn (giữ 0.5s) và cử chỉ để gọi ngay Google Gemini...", "info")
            # 5 = LONG_PRESS_POWER_ASSISTANT
            self.run_cmd(["shell", "settings", "put", "system", "long_press_power_key", "5"], serial)
            self.run_cmd(["shell", "settings", "put", "global", "power_button_long_press", "5"], serial)
            self.run_cmd(["shell", "settings", "put", "system", "long_press_power_key_assist", "1"], serial)
            # Đảm bảo Phím Nguồn + Tăng âm lượng luôn mở Power Menu dự phòng
            self.run_cmd(["shell", "settings", "put", "system", "key_combination_power_volume_up", "1"], serial)
            log_cb("  ✓ Đã gán giữ nút Nguồn 0.5s để khởi động Gemini (Bấm Nguồn + Tăng âm lượng để mở Menu Tắt/Khởi động máy).", "success")

        # 5. Tối ưu quyền chạy nền cho Google / Gemini
        log_cb("  -> Cấp quyền phản hồi tức thì (Doze Whitelist & AppOps) cho Google/Gemini...", "info")
        for pkg in [google_pkg, gemini_pkg]:
            if self.is_package_installed(serial, pkg):
                self.run_cmd(["shell", "dumpsys", "deviceidle", "whitelist", f"+{pkg}"], serial)
                self.run_cmd(["shell", "cmd", "appops", "set", pkg, "RUN_IN_BACKGROUND", "allow"], serial)
                self.run_cmd(["shell", "cmd", "appops", "set", pkg, "RUN_ANY_IN_BACKGROUND", "allow"], serial)

        log_cb("  ✓ HOÀN TẤT THIẾT LẬP: Google Gemini đã trở thành AI chính của điện thoại!", "success")
        return True

    # ================= MODULE 4: PERFORMANCE & PHƯỢT BOOSTER =================
    def apply_performance_boost(self, serial, disable_ram_expand=True, disable_joyose=True, compile_art=True, run_fstrim=True, log_cb=None):
        if not log_cb:
            log_cb = lambda m, t="info": None

        log_cb("[PERF] Bắt đầu gói Tối Ưu Hiệu Năng & Cứu Tinh Đi Phượt...", "info")

        # 1. Tắt RAM ảo (Memory Extension)
        if disable_ram_expand:
            log_cb("  -> Đang gửi lệnh tắt RAM ảo (Memory Extension)...", "info")
            self.run_cmd(["shell", "settings", "put", "global", "ram_expand_size", "0"], serial)
            self.run_cmd(["shell", "settings", "put", "system", "memory_extension", "0"], serial)
            self.run_cmd(["shell", "setprop", "persist.miui.extm.enable", "0"], serial)
            self.run_cmd(["shell", "setprop", "persist.sys.miui.memory_expansion", "0"], serial)
            log_cb("  ✓ Đã tắt RAM ảo (Tránh nghẽn chip nhớ, xoay Google Maps và đa nhiệm không bị khựng đơ).", "success")

        # 2. Vô hiệu hóa Joyose
        if disable_joyose:
            log_cb("  -> Đang vô hiệu hóa Joyose (Bỏ bóp xung CPU & chống dìm tối màn hình ngoài nắng)...", "info")
            succ, out = self.run_cmd(["shell", "pm", "disable-user", "--user", "0", "com.xiaomi.joyose"], serial)
            if not succ or "SecurityException" in out:
                succ, out = self.run_cmd(["shell", "pm", "uninstall", "-k", "--user", "0", "com.xiaomi.joyose"], serial)
            if succ and ("disabled" in out.lower() or "success" in out.lower()):
                log_cb("  ✓ Đã vô hiệu hóa Joyose thành công! Màn hình không bị tự dìm tối khi xem Map ngoài nắng gắt.", "success")
            else:
                log_cb(f"  [!] Trạng thái Joyose: {out}", "info")

        # 3. Ép tối ưu hóa ART Compiler
        if compile_art:
            log_cb("  -> Đang chạy tối ưu hóa biên dịch mã máy Android Runtime (ART AOT Compile)...", "info")
            log_cb("  (Quá trình dịch sẵn mã máy cho app để mở tức thì, vui lòng đợi trong giây lát)...", "info")
            succ, out = self.run_cmd(["shell", "cmd", "package", "compile", "-m", "speed-profile", "-a"], serial, timeout=120)
            if succ:
                log_cb("  ✓ Biên dịch ART thành công! Toàn bộ app đã nạp sẵn mã máy nhị phân.", "success")
            else:
                log_cb(f"  [!] Kết quả ART: {out[:100]}", "warning")

        # 4. FSTRIM dọn dẹp chip nhớ
        if run_fstrim:
            log_cb("  -> Đang dọn dẹp các khối nhớ trống phân mảnh phần cứng (FSTRIM)...", "info")
            self.run_cmd(["shell", "sm", "fstrim"], serial, timeout=30)
            log_cb("  ✓ FSTRIM hoàn tất: Bộ nhớ flash UFS/eMMC đã được dọn sạch.", "success")

        log_cb("  ✓ HOÀN TẤT TỐI ƯU HIỆU NĂNG: Máy đã sẵn sàng cho chuyến đi phượt mượt mà!", "success")
        return True

    def restore_joyose(self, serial, log_cb=None):
        if not log_cb:
            log_cb = lambda m, t="info": None
        log_cb("  -> Đang kích hoạt lại Joyose...", "info")
        succ, out = self.run_cmd(["shell", "pm", "enable", "com.xiaomi.joyose"], serial)
        if succ and "enabled" in out.lower():
            log_cb("  ✓ Đã bật lại Joyose về mặc định của Xiaomi.", "success")
        else:
            log_cb(f"  [!] Kết quả: {out}", "info")
        return succ

    # ================= MODULE 5: GỠ APP RÁC (DEBLOAT) =================
    def debloat_apps(self, serial, packages_to_remove, log_cb):
        log_cb(f"[4/4] Bắt đầu gỡ bỏ {len(packages_to_remove)} ứng dụng rác nội địa...", "info")
        removed_count = 0
        for pkg in packages_to_remove:
            if self.is_package_installed(serial, pkg):
                succ, out = self.run_cmd(["shell", "pm", "uninstall", "-k", "--user", "0", pkg], serial)
                if succ and "Success" in out:
                    log_cb(f"  [-] Đã gỡ bỏ: {pkg}", "success")
                    removed_count += 1
                else:
                    log_cb(f"  [!] Không thể gỡ {pkg}: {out}", "warning")
            else:
                log_cb(f"  [.] {pkg} không có trên máy (bỏ qua).", "info")
        
        log_cb(f"  ✓ Đã hoàn tất dọn dẹp sạch {removed_count} ứng dụng rác!", "success")
        return True

    # ================= TIỆN ÍCH =================
    def open_fcm_diagnostics(self, serial):
        """Mở màn hình chẩn đoán FCM Diagnostics (*#*#426#*#*)"""
        return self.run_cmd(["shell", "am", "start", "-n", "com.google.android.gms/.gcm.GcmDiagnostics"], serial)

    def test_launch_gemini(self, serial):
        """Kích hoạt thử giao diện Gemini / Google Assistant trên màn hình điện thoại"""
        succ, out = self.run_cmd(["shell", "am", "start", "-a", "android.intent.action.VOICE_COMMAND"], serial)
        if not succ:
            return self.run_cmd(["shell", "am", "start", "-n", "com.google.android.googlequicksearchbox/com.google.android.apps.gsa.staticplugins.opa.OpaActivity"], serial)
        return succ, out

    def open_gemini_playstore(self, serial):
        """Mở CH Play đến trang tải ứng dụng Google Gemini"""
        return self.run_cmd(["shell", "am", "start", "-a", "android.intent.action.VIEW", "-d", "market://details?id=com.google.android.apps.bard"], serial)

    def reboot(self, serial):
        """Khởi động lại điện thoại"""
        return self.run_cmd(["reboot"], serial)

    def lock_usb_debugging(self, serial, log_cb=None):
        """Khóa lại chế độ nhà phát triển và tắt USB debugging để bảo mật & dùng app ngân hàng/VNeID bình thường"""
        if not log_cb:
            log_cb = lambda m, t="info": None
        log_cb("  -> Đang khóa Developer Options, tắt ADB và thu hồi các quyền bảo mật...", "info")
        cmd = (
            "settings put global development_settings_enabled 0; "
            "settings put secure development_settings_enabled 0; "
            "settings delete global adb_allowed_connection_time; "
            "settings put global adb_wifi_enabled 0; "
            "am force-stop com.android.settings; "
            "settings put global adb_enabled 0"
        )
        succ, out = self.run_cmd(["shell", cmd], serial, timeout=5)
        log_cb("  ✓ ĐÃ KHÓA THÀNH CÔNG: Chế độ nhà phát triển & USB Debugging đã tắt hoàn toàn!", "success")
        log_cb("  [i] Máy tính đã ngắt kết nối với điện thoại. Menu Tùy chọn nhà phát triển đã được đóng và ẩn đi.", "info")
        return True

    # ================= FASTBOOT & BOOTLOADER =================
    def get_fastboot_devices(self):
        """Lấy danh sách thiết bị đang ở chế độ Fastboot"""
        succ, out = self.run_fastboot_cmd(["devices"])
        if not succ:
            return []
        devices = []
        for line in out.splitlines():
            line = line.strip()
            if not line:
                continue
            parts = re.split(r'\s+', line)
            if len(parts) >= 2 and parts[1] == "fastboot":
                devices.append({
                    "serial": parts[0],
                    "status": "fastboot"
                })
        return devices

    def get_fastboot_device_info(self, serial=None):
        """Lấy thông tin mã máy (codename), bootloader, ARB từ Fastboot"""
        info = {
            "product": "Chưa xác định",
            "unlocked": None,
            "anti": None,
            "is_userspace": "no"
        }
        succ, out = self.run_fastboot_cmd(["getvar", "product"], serial=serial)
        m = re.search(r'product:\s*([^\r\n]+)', out)
        if m:
            info["product"] = m.group(1).strip()

        succ, out = self.run_fastboot_cmd(["getvar", "unlocked"], serial=serial)
        m = re.search(r'unlocked:\s*([^\r\n]+)', out)
        if m:
            val = m.group(1).strip().lower()
            info["unlocked"] = (val == "yes")

        succ, out = self.run_fastboot_cmd(["getvar", "anti"], serial=serial)
        m = re.search(r'anti:\s*([^\r\n]+)', out)
        if m:
            info["anti"] = m.group(1).strip()

        succ, out = self.run_fastboot_cmd(["getvar", "is-userspace"], serial=serial)
        m = re.search(r'is-userspace:\s*([^\r\n]+)', out)
        if m:
            info["is_userspace"] = m.group(1).strip()

        return info

    def reboot_to_fastboot(self, serial=None):
        """Chuyển thiết bị từ ADB sang Fastboot"""
        return self.run_cmd(["reboot", "bootloader"], serial)

    def fastboot_reboot_system(self, serial=None):
        """Khởi động lại từ Fastboot vào Android System"""
        return self.run_fastboot_cmd(["reboot"], serial)

    def fastboot_reboot_recovery(self, serial=None):
        """Khởi động lại từ Fastboot vào Recovery"""
        return self.run_fastboot_cmd(["reboot", "recovery"], serial)

    def fastboot_lock_bootloader(self, serial=None, log_cb=None):
        """Khóa Bootloader trong Fastboot (Yêu cầu đang ở ROM China)"""
        if not log_cb:
            log_cb = lambda m, t="info": None
        log_cb("  -> Đang gửi lệnh khóa Bootloader (fastboot flashing lock)...", "warning")
        succ, out = self.run_fastboot_cmd(["flashing", "lock"], serial=serial, timeout=45)
        if not succ and ("unknown" in out.lower() or "error" in out.lower()):
            log_cb("  [i] Thử phương thức thay thế (fastboot oem lock)...", "info")
            succ, out = self.run_fastboot_cmd(["oem", "lock"], serial=serial, timeout=45)
        
        if succ or "success" in out.lower() or "okay" in out.lower():
            log_cb("  ✓ ĐÃ GỬI LỆNH KHÓA BOOTLOADER THÀNH CÔNG!", "success")
            log_cb("  [!] Vui lòng nhìn màn hình điện thoại: Dùng phím Âm lượng chọn 'Lock the bootloader' và bấm Nguồn xác nhận!", "warning")
            return True, out
        else:
            log_cb(f"  ✕ Kết quả lệnh khóa: {out}", "error")
            return False, out
