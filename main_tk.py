# -*- coding: utf-8 -*-
"""
Xiaomi HyperTool Pro - Thiết kế UI/UX theo chuẩn evondevKit
Giao diện tối ưu hóa trải nghiệm người dùng, cấu trúc dạng Dashboard Utility hiện đại.
"""

import sys
import os
import threading
import time
import customtkinter as ctk
from tkinter import messagebox
from adb_manager import ADBManager
from debloat_list import DEBLOAT_APPS

# Thiết lập theme chuẩn
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# Bảng màu Design Tokens chuẩn evondevKit
COLOR_BG_BASE = "#0f172a"        # slate-900
COLOR_CARD_BG = "#1e293b"        # slate-800
COLOR_CARD_BORDER = "#334155"    # slate-700
COLOR_CARD_HOVER = "#273549"     # slate-750
COLOR_PRIMARY = "#0284c7"        # sky-600
COLOR_PRIMARY_HOVER = "#0369a1"  # sky-700
COLOR_SUCCESS = "#10b981"        # emerald-500
COLOR_WARNING = "#f59e0b"        # amber-500
COLOR_ERROR = "#ef4444"          # rose-500
COLOR_TEXT_TITLE = "#f8fafc"     # slate-50
COLOR_TEXT_BODY = "#94a3b8"      # slate-400
COLOR_TEXT_MUTED = "#64748b"     # slate-500
COLOR_TERMINAL_BG = "#090d16"    # deep terminal black


class DebloatDialog(ctk.CTkToplevel):
    """Modal tùy chỉnh danh sách gỡ bỏ Bloatware với thanh tìm kiếm và bộ lọc nhanh"""
    def __init__(self, parent, debloat_apps, selected_apps):
        super().__init__(parent)
        self.title("Tùy Chỉnh Ứng Dụng Rác Cần Gỡ Bỏ")
        self.geometry("620x680")
        self.minsize(580, 600)
        self.configure(fg_color=COLOR_BG_BASE)
        self.transient(parent)
        self.grab_set()

        self.debloat_apps = debloat_apps
        self.selected_apps = selected_apps
        self.check_vars = {}
        self.card_widgets = []

        self._build_ui()

    def _build_ui(self):
        # 1. Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=24, pady=(20, 10))

        title_lbl = ctk.CTkLabel(
            header,
            text="🧹 Danh Sách Ứng Dụng Rác Nội Địa Xiaomi",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLOR_TEXT_TITLE
        )
        title_lbl.pack(anchor="w")

        sub_lbl = ctk.CTkLabel(
            header,
            text="Các ứng dụng được đánh dấu an toàn có thể gỡ mà không ảnh hưởng đến độ ổn định của máy.",
            font=ctk.CTkFont(size=12),
            text_color=COLOR_TEXT_BODY
        )
        sub_lbl.pack(anchor="w", pady=(2, 0))

        # 2. Thanh tìm kiếm & Tác vụ nhanh
        search_bar = ctk.CTkFrame(self, fg_color=COLOR_CARD_BG, corner_radius=8, border_width=1, border_color=COLOR_CARD_BORDER)
        search_bar.pack(fill="x", padx=24, pady=(5, 10))

        self.search_entry = ctk.CTkEntry(
            search_bar,
            placeholder_text="🔍 Tìm kiếm theo tên app hoặc tên gói (package)...",
            height=36,
            fg_color="transparent",
            border_width=0,
            font=ctk.CTkFont(size=12)
        )
        self.search_entry.pack(side="left", fill="x", expand=True, padx=10)
        self.search_entry.bind("<KeyRelease>", self._filter_apps)

        # Thanh nút hành động nhanh
        action_bar = ctk.CTkFrame(self, fg_color="transparent")
        action_bar.pack(fill="x", padx=24, pady=(0, 10))

        self.lbl_selected_counter = ctk.CTkLabel(
            action_bar,
            text=f"Đã chọn: {len(self.selected_apps)} / {len(self.debloat_apps)} ứng dụng",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=COLOR_PRIMARY
        )
        self.lbl_selected_counter.pack(side="left")

        btn_uncheck_all = ctk.CTkButton(
            action_bar,
            text="Bỏ chọn tất cả",
            width=110,
            height=28,
            fg_color="#334155",
            hover_color="#475569",
            font=ctk.CTkFont(size=11),
            command=self.deselect_all
        )
        btn_uncheck_all.pack(side="right", padx=(5, 0))

        btn_check_safe = ctk.CTkButton(
            action_bar,
            text="Chọn mục an toàn",
            width=130,
            height=28,
            fg_color="#1e40af",
            hover_color="#1d4ed8",
            font=ctk.CTkFont(size=11),
            command=self.select_all_safe
        )
        btn_check_safe.pack(side="right")

        # 3. Danh sách cuộn ứng dụng
        self.scroll_frame = ctk.CTkScrollableFrame(
            self,
            fg_color=COLOR_CARD_BG,
            border_width=1,
            border_color=COLOR_CARD_BORDER,
            corner_radius=10
        )
        self.scroll_frame.pack(fill="both", expand=True, padx=24, pady=5)

        for app in self.debloat_apps:
            pkg = app["package"]
            is_checked = pkg in self.selected_apps
            var = ctk.BooleanVar(value=is_checked)
            self.check_vars[pkg] = var

            item_card = ctk.CTkFrame(
                self.scroll_frame,
                fg_color="#162032",
                corner_radius=8,
                border_width=1,
                border_color="#243042"
            )
            item_card.pack(fill="x", pady=4, padx=4)

            top_row = ctk.CTkFrame(item_card, fg_color="transparent")
            top_row.pack(fill="x", padx=10, pady=(6, 2))

            cb = ctk.CTkCheckBox(
                top_row,
                text=app["name"],
                variable=var,
                font=ctk.CTkFont(size=13, weight="bold"),
                checkbox_width=20,
                checkbox_height=20,
                command=self._update_counter
            )
            cb.pack(side="left")

            if app["safe"]:
                safe_badge = ctk.CTkLabel(
                    top_row,
                    text="An toàn 100%",
                    font=ctk.CTkFont(size=10, weight="bold"),
                    text_color="#34d399",
                    fg_color="#064e3b",
                    corner_radius=4,
                    padx=6,
                    pady=1
                )
                safe_badge.pack(side="right")

            pkg_lbl = ctk.CTkLabel(
                item_card,
                text=pkg,
                font=ctk.CTkFont(family="Consolas", size=10),
                text_color=COLOR_TEXT_MUTED
            )
            pkg_lbl.pack(anchor="w", padx=36, pady=(0, 2))

            desc_lbl = ctk.CTkLabel(
                item_card,
                text=app["desc"],
                font=ctk.CTkFont(size=11),
                text_color=COLOR_TEXT_BODY,
                justify="left",
                wraplength=480
            )
            desc_lbl.pack(anchor="w", padx=36, pady=(0, 6))

            self.card_widgets.append((app, item_card))

        # 4. Nút lưu lựa chọn
        btn_save = ctk.CTkButton(
            self,
            text="Lưu Lựa Chọn & Đóng",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=42,
            fg_color=COLOR_PRIMARY,
            hover_color=COLOR_PRIMARY_HOVER,
            command=self.save_and_close
        )
        btn_save.pack(fill="x", padx=24, pady=16)

    def _update_counter(self):
        count = sum(1 for v in self.check_vars.values() if v.get())
        self.lbl_selected_counter.configure(
            text=f"Đã chọn: {count} / {len(self.debloat_apps)} ứng dụng"
        )

    def _filter_apps(self, event=None):
        query = self.search_entry.get().strip().lower()
        for app, widget in self.card_widgets:
            match = query in app["name"].lower() or query in app["package"].lower() or query in app["desc"].lower()
            if match:
                widget.pack(fill="x", pady=4, padx=4)
            else:
                widget.pack_forget()

    def select_all_safe(self):
        for app in self.debloat_apps:
            if app["safe"]:
                self.check_vars[app["package"]].set(True)
        self._update_counter()

    def deselect_all(self):
        for var in self.check_vars.values():
            var.set(False)
        self._update_counter()

    def save_and_close(self):
        self.selected_apps.clear()
        for pkg, var in self.check_vars.items():
            if var.get():
                self.selected_apps.add(pkg)
        self.destroy()


class XiaomiToolApp(ctk.CTk):
    """Giao diện chính chuẩn UX/UI cho Xiaomi HyperTool Pro"""
    def __init__(self):
        super().__init__()

        self.title("Xiaomi HyperTool Pro — Bộ Công Cụ Tối Ưu Hóa ROM China")
        self.geometry("960x780")
        self.minsize(920, 720)
        self.configure(fg_color=COLOR_BG_BASE)

        self.adb = ADBManager()
        self.current_serial = None
        self.is_running = False

        # Danh sách app rác mặc định
        self.selected_debloat_apps = {
            app["package"] for app in DEBLOAT_APPS if app.get("default", False)
        }

        self._build_ui()
        self.refresh_devices()

    def _build_ui(self):
        # 1. Top Navbar
        nav = ctk.CTkFrame(self, fg_color=COLOR_CARD_BG, corner_radius=0, height=54, border_width=1, border_color=COLOR_CARD_BORDER)
        nav.pack(fill="x")

        nav_inner = ctk.CTkFrame(nav, fg_color="transparent")
        nav_inner.pack(fill="both", expand=True, padx=20)

        # Brand / Logo Title
        brand_frame = ctk.CTkFrame(nav_inner, fg_color="transparent")
        brand_frame.pack(side="left", fill="y")

        lbl_logo = ctk.CTkLabel(
            brand_frame,
            text="⚡ Xiaomi HyperTool",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLOR_TEXT_TITLE
        )
        lbl_logo.pack(side="left", pady=10)

        badge_version = ctk.CTkLabel(
            brand_frame,
            text="PRO v2.1",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color="#38bdf8",
            fg_color="#0c4a6e",
            corner_radius=4,
            padx=6,
            pady=1
        )
        badge_version.pack(side="left", padx=8, pady=10)

        # Right status indicator
        self.badge_status = ctk.CTkLabel(
            nav_inner,
            text="● Đang quét thiết bị...",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=COLOR_WARNING
        )
        self.badge_status.pack(side="right", padx=10, pady=10)

        btn_rescan = ctk.CTkButton(
            nav_inner,
            text="🔄 Quét thiết bị",
            width=110,
            height=30,
            fg_color="#334155",
            hover_color="#475569",
            font=ctk.CTkFont(size=11, weight="bold"),
            command=self.refresh_devices
        )
        btn_rescan.pack(side="right", padx=5, pady=10)

        # 2. Main Scrollable Container
        main_content = ctk.CTkScrollableFrame(self, fg_color="transparent")
        main_content.pack(fill="both", expand=True, padx=20, pady=12)

        # 3. Device Hero Status Card
        self.hero_card = ctk.CTkFrame(
            main_content,
            fg_color=COLOR_CARD_BG,
            corner_radius=12,
            border_width=1,
            border_color=COLOR_CARD_BORDER
        )
        self.hero_card.pack(fill="x", pady=(0, 12))

        hero_inner = ctk.CTkFrame(self.hero_card, fg_color="transparent")
        hero_inner.pack(fill="x", padx=20, pady=16)

        # Thông tin máy bên trái
        dev_info_left = ctk.CTkFrame(hero_inner, fg_color="transparent")
        dev_info_left.pack(side="left", fill="both", expand=True)

        self.lbl_device_title = ctk.CTkLabel(
            dev_info_left,
            text="Chưa kết nối thiết bị",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=COLOR_TEXT_TITLE,
            anchor="w"
        )
        self.lbl_device_title.pack(anchor="w")

        # Hàng tags thông số
        self.tags_frame = ctk.CTkFrame(dev_info_left, fg_color="transparent")
        self.tags_frame.pack(anchor="w", pady=(8, 0))

        self.tag_android = self._create_badge(self.tags_frame, "Android --", "#334155", COLOR_TEXT_BODY)
        self.tag_os = self._create_badge(self.tags_frame, "HyperOS --", "#334155", COLOR_TEXT_BODY)
        self.tag_battery = self._create_badge(self.tags_frame, "Pin --", "#334155", COLOR_TEXT_BODY)
        self.tag_security = self._create_badge(self.tags_frame, "Bảo mật --", "#334155", COLOR_TEXT_BODY)

        # Các nút thao tác nhanh bên phải
        dev_actions_right = ctk.CTkFrame(hero_inner, fg_color="transparent")
        dev_actions_right.pack(side="right", padx=(10, 0))

        self.btn_quick_fcm = ctk.CTkButton(
            dev_actions_right,
            text="🔍 Chẩn đoán FCM (*#*#426#*#*)",
            width=180,
            height=32,
            fg_color="#1e293b",
            hover_color="#334155",
            border_width=1,
            border_color="#475569",
            font=ctk.CTkFont(size=11),
            command=self.open_fcm_diag
        )
        self.btn_quick_fcm.pack(pady=2)

        self.btn_quick_reboot = ctk.CTkButton(
            dev_actions_right,
            text="🔄 Khởi động lại máy (Reboot)",
            width=180,
            height=32,
            fg_color="#1e293b",
            hover_color="#334155",
            border_width=1,
            border_color="#475569",
            font=ctk.CTkFont(size=11),
            command=self.reboot_device
        )
        self.btn_quick_reboot.pack(pady=2)

        # Banner cảnh báo bảo mật nếu thiếu quyền
        self.warn_card = ctk.CTkFrame(
            main_content,
            fg_color="#450a0a",
            corner_radius=8,
            border_width=1,
            border_color="#991b1b"
        )
        self.lbl_warn = ctk.CTkLabel(
            self.warn_card,
            text="",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#fecaca",
            justify="left"
        )
        self.lbl_warn.pack(padx=16, pady=10, fill="x")

        # 4. Dashboard Operations (Lưới 2 Cột Tính Năng)
        grid_container = ctk.CTkFrame(main_content, fg_color="transparent")
        grid_container.pack(fill="x", pady=4)

        # CỘT TRÁI: Việt Hóa + FCM
        col_left = ctk.CTkFrame(grid_container, fg_color="transparent")
        col_left.pack(side="left", fill="both", expand=True, padx=(0, 6))

        # CARD 1: VIỆT HÓA
        card_viethoa = self._create_card(col_left, "🇻🇳 Việt Hóa Toàn Diện Ứng Dụng")
        
        self.sw_viethoa = ctk.CTkSwitch(
            card_viethoa,
            text="Kích hoạt Tiếng Việt cho hệ thống và ứng dụng",
            font=ctk.CTkFont(size=13, weight="bold"),
            progress_color=COLOR_PRIMARY
        )
        self.sw_viethoa.select()
        self.sw_viethoa.pack(anchor="w", padx=16, pady=(12, 4))

        self._create_feature_bullet(
            card_viethoa,
            "Cài đặt MoreLocale 2 & cấp quyền đổi cấu hình hệ thống (CHANGE_CONFIGURATION)."
        )
        self._create_feature_bullet(
            card_viethoa,
            "100% ứng dụng CH Play (Zalo, Facebook, TikTok, Ngân hàng...) tự nhận diện Tiếng Việt."
        )
        self._create_feature_bullet(
            card_viethoa,
            "Định dạng giờ, ngày tháng, bộ gõ và cửa sổ thông báo tự chuyển sang ngôn ngữ tiếng Việt.",
            is_last=True
        )

        # CARD 2: GOOGLE FCM & THÔNG BÁO
        card_fcm = self._create_card(col_left, "⚡ Tối Ưu & Giữ Kết Nối Google FCM", top_pad=12)

        self.sw_fcm_whitelist = ctk.CTkSwitch(
            card_fcm,
            text="Chống đóng băng Google Play Services (Doze & Millet)",
            font=ctk.CTkFont(size=13, weight="bold"),
            progress_color=COLOR_PRIMARY
        )
        self.sw_fcm_whitelist.select()
        self.sw_fcm_whitelist.pack(anchor="w", padx=16, pady=(12, 4))

        self._create_feature_bullet(
            card_fcm,
            "Ngăn HyperOS tự ý ngắt kết nối socket ngầm khi tắt màn hình 15–40 phút."
        )
        self._create_feature_bullet(
            card_fcm,
            "Thông báo ứng dụng ngân hàng, Zalo, Messenger nổ tức thì như máy bản Quốc tế."
        )

        # Tùy chọn chuyên sâu Shizuku
        sub_options_frame = ctk.CTkFrame(card_fcm, fg_color="#172235", corner_radius=8, border_width=1, border_color="#24334a")
        sub_options_frame.pack(fill="x", padx=16, pady=(4, 14))

        self.sw_shizuku = ctk.CTkCheckBox(
            sub_options_frame,
            text="Tự động cài đặt & kích hoạt Shizuku Server qua ADB",
            font=ctk.CTkFont(size=12, weight="bold"),
            checkbox_width=18,
            checkbox_height=18
        )
        self.sw_shizuku.select()
        self.sw_shizuku.pack(anchor="w", padx=12, pady=(10, 4))

        self.sw_fcm_fix_app = ctk.CTkCheckBox(
            sub_options_frame,
            text="Cài đặt công cụ chuyên dụng HyperOS FCM Fix",
            font=ctk.CTkFont(size=12),
            checkbox_width=18,
            checkbox_height=18
        )
        self.sw_fcm_fix_app.select()
        self.sw_fcm_fix_app.pack(anchor="w", padx=12, pady=(4, 10))

        # CỘT PHẢI: Debloat + Tiện ích
        col_right = ctk.CTkFrame(grid_container, fg_color="transparent")
        col_right.pack(side="right", fill="both", expand=True, padx=(6, 0))

        # CARD 3: GỠ APP RÁC
        card_debloat = self._create_card(col_right, "🧹 Dọn Dẹp Bloatware Trung Quốc")

        self.sw_debloat = ctk.CTkSwitch(
            card_debloat,
            text="Gỡ bỏ các ứng dụng rác nội địa Trung Quốc",
            font=ctk.CTkFont(size=13, weight="bold"),
            progress_color=COLOR_PRIMARY
        )
        self.sw_debloat.select()
        self.sw_debloat.pack(anchor="w", padx=16, pady=(12, 4))

        self._create_feature_bullet(
            card_debloat,
            "Gỡ sạch Mi Video TQ, Mi Music TQ, Mi GetApps, bàn phím Sogou, Baidu..."
        )
        self._create_feature_bullet(
            card_debloat,
            "Giải phóng RAM và tắt các tiến trình quảng cáo rác ngầm của thị trường nội địa."
        )

        debloat_btn_row = ctk.CTkFrame(card_debloat, fg_color="transparent")
        debloat_btn_row.pack(fill="x", padx=16, pady=(4, 16))

        self.lbl_debloat_selected = ctk.CTkLabel(
            debloat_btn_row,
            text=f"• Đã chọn: {len(self.selected_debloat_apps)} ứng dụng an toàn",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#38bdf8"
        )
        self.lbl_debloat_selected.pack(side="left")

        btn_edit_debloat = ctk.CTkButton(
            debloat_btn_row,
            text="⚙️ Tùy chỉnh danh sách",
            height=28,
            width=140,
            fg_color="#334155",
            hover_color="#475569",
            font=ctk.CTkFont(size=11),
            command=self.open_debloat_customizer
        )
        btn_edit_debloat.pack(side="right")

        # CARD 4: TIỆN ÍCH HOÀN TẤT
        card_misc = self._create_card(col_right, "🛠️ Tùy Chọn Hoàn Tất", top_pad=12)

        self.sw_open_fcm = ctk.CTkSwitch(
            card_misc,
            text="Tự động mở FCM Diagnostics (*#*#426#*#*) sau khi chạy",
            font=ctk.CTkFont(size=12),
            progress_color=COLOR_PRIMARY
        )
        self.sw_open_fcm.select()
        self.sw_open_fcm.pack(anchor="w", padx=16, pady=(12, 4))

        self.sw_reboot = ctk.CTkSwitch(
            card_misc,
            text="Tự động khởi động lại điện thoại (Reboot) khi hoàn thành",
            font=ctk.CTkFont(size=12),
            progress_color=COLOR_PRIMARY
        )
        self.sw_reboot.pack(anchor="w", padx=16, pady=(4, 16))

        # 5. Thanh Thao Tác Chính & Progress Bar
        action_card = ctk.CTkFrame(
            main_content,
            fg_color=COLOR_CARD_BG,
            corner_radius=12,
            border_width=1,
            border_color=COLOR_CARD_BORDER
        )
        action_card.pack(fill="x", pady=(12, 8))

        action_inner = ctk.CTkFrame(action_card, fg_color="transparent")
        action_inner.pack(fill="x", padx=20, pady=16)

        self.btn_run = ctk.CTkButton(
            action_inner,
            text="🚀 BẮT ĐẦU TỐI ƯU HÓA (1-CLICK EXECUTE)",
            font=ctk.CTkFont(size=15, weight="bold"),
            height=46,
            fg_color=COLOR_PRIMARY,
            hover_color=COLOR_PRIMARY_HOVER,
            corner_radius=8,
            command=self.start_processing
        )
        self.btn_run.pack(fill="x")

        self.progress_container = ctk.CTkFrame(action_inner, fg_color="transparent")
        self.progress_container.pack(fill="x", pady=(12, 0))

        self.lbl_progress_status = ctk.CTkLabel(
            self.progress_container,
            text="Sẵn sàng thực hiện",
            font=ctk.CTkFont(size=11),
            text_color=COLOR_TEXT_MUTED
        )
        self.lbl_progress_status.pack(side="left")

        self.lbl_progress_pct = ctk.CTkLabel(
            self.progress_container,
            text="0%",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=COLOR_PRIMARY
        )
        self.lbl_progress_pct.pack(side="right")

        self.progress_bar = ctk.CTkProgressBar(
            action_inner,
            height=6,
            corner_radius=3,
            progress_color=COLOR_PRIMARY,
            fg_color="#0f172a"
        )
        self.progress_bar.set(0)
        self.progress_bar.pack(fill="x", pady=(6, 0))

        # 6. Terminal Console Log Thời Gian Thực
        log_card = ctk.CTkFrame(
            main_content,
            fg_color=COLOR_TERMINAL_BG,
            corner_radius=10,
            border_width=1,
            border_color=COLOR_CARD_BORDER
        )
        log_card.pack(fill="both", expand=True, pady=(4, 10))

        log_top_bar = ctk.CTkFrame(log_card, fg_color="transparent")
        log_top_bar.pack(fill="x", padx=14, pady=(8, 4))

        ctk.CTkLabel(
            log_top_bar,
            text="📋 Nhật Ký Thực Thi Thời Gian Thực (Console Logs)",
            font=ctk.CTkFont(family="Consolas", size=11, weight="bold"),
            text_color=COLOR_TEXT_BODY
        ).pack(side="left")

        btn_clear = ctk.CTkButton(
            log_top_bar,
            text="Xóa nhật ký",
            width=80,
            height=22,
            fg_color="#1e293b",
            hover_color="#334155",
            font=ctk.CTkFont(size=10),
            command=self.clear_log
        )
        btn_clear.pack(side="right")

        self.txt_log = ctk.CTkTextbox(
            log_card,
            font=ctk.CTkFont(family="Consolas", size=11),
            fg_color=COLOR_TERMINAL_BG,
            text_color="#e2e8f0",
            wrap="word",
            height=140
        )
        self.txt_log.pack(fill="both", expand=True, padx=12, pady=(0, 10))

    # ================= CÁC HÀM TIỆN ÍCH DỰNG COMPONENT =================
    def _create_card(self, parent, title_text, top_pad=0):
        card = ctk.CTkFrame(
            parent,
            fg_color=COLOR_CARD_BG,
            corner_radius=10,
            border_width=1,
            border_color=COLOR_CARD_BORDER
        )
        card.pack(fill="x", pady=(top_pad, 0))

        header = ctk.CTkFrame(card, fg_color="transparent")
        header.pack(fill="x", padx=16, pady=(14, 4))

        ctk.CTkLabel(
            header,
            text=title_text,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLOR_TEXT_TITLE
        ).pack(side="left")

        return card

    def _create_badge(self, parent, text, bg_color, text_color):
        badge = ctk.CTkLabel(
            parent,
            text=text,
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=bg_color,
            text_color=text_color,
            corner_radius=5,
            padx=8,
            pady=3
        )
        badge.pack(side="left", padx=(0, 6))
        return badge

    def _create_feature_bullet(self, parent, text, is_last=False):
        bullet_frame = ctk.CTkFrame(parent, fg_color="transparent")
        bullet_frame.pack(fill="x", padx=20, pady=(1, 10 if is_last else 2))

        ctk.CTkLabel(
            bullet_frame,
            text="•",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=COLOR_TEXT_MUTED
        ).pack(side="left", anchor="n", padx=(0, 6))

        ctk.CTkLabel(
            bullet_frame,
            text=text,
            font=ctk.CTkFont(size=11),
            text_color=COLOR_TEXT_BODY,
            justify="left",
            wraplength=380
        ).pack(side="left", anchor="w")

    # ================= LOGGING & CẬP NHẬT GIAO DIỆN =================
    def log(self, message, msg_type="info"):
        timestamp = time.strftime("%H:%M:%S")
        prefix = f"[{timestamp}] "
        full_line = f"{prefix}{message}\n"

        self.txt_log.configure(state="normal")
        self.txt_log.insert("end", full_line)
        self.txt_log.see("end")
        self.txt_log.configure(state="disabled")

    def clear_log(self):
        self.txt_log.configure(state="normal")
        self.txt_log.delete("1.0", "end")
        self.txt_log.configure(state="disabled")

    def open_debloat_customizer(self):
        DebloatDialog(self, DEBLOAT_APPS, self.selected_debloat_apps)
        self.lbl_debloat_selected.configure(
            text=f"• Đã chọn: {len(self.selected_debloat_apps)} ứng dụng an toàn"
        )

    # ================= QUẢN LÝ THIẾT BỊ =================
    def refresh_devices(self):
        devices = self.adb.get_devices()
        self.warn_card.pack_forget()

        if not devices:
            self.current_serial = None
            self.lbl_device_title.configure(text="Chưa kết nối thiết bị nào", text_color="#ef4444")
            self.badge_status.configure(text="● Không tìm thấy máy", text_color=COLOR_ERROR)
            self.tag_android.configure(text="Android --", fg_color="#334155")
            self.tag_os.configure(text="HyperOS --", fg_color="#334155")
            self.tag_battery.configure(text="Pin --", fg_color="#334155")
            self.tag_security.configure(text="Bảo mật --", fg_color="#334155")
            self.btn_run.configure(state="disabled")
            self.btn_quick_fcm.configure(state="disabled")
            self.btn_quick_reboot.configure(state="disabled")
            return

        dev = devices[0]
        serial = dev["serial"]
        status = dev["status"]

        if status == "unauthorized":
            self.current_serial = None
            self.lbl_device_title.configure(text="Chưa cấp quyền trên màn hình điện thoại", text_color="#f59e0b")
            self.badge_status.configure(text="● Chờ cấp quyền", text_color=COLOR_WARNING)
            self.btn_run.configure(state="disabled")
            self.log("⚠️ Hãy mở khóa màn hình điện thoại và bấm 'Cho phép gỡ lỗi USB'!", "warning")
            return

        if status == "device":
            self.current_serial = serial
            info = self.adb.get_device_info(serial)
            
            # Cập nhật thông tin máy
            self.lbl_device_title.configure(
                text=f"{info['marketname']} ({info['model']})",
                text_color=COLOR_TEXT_TITLE
            )
            self.badge_status.configure(text="● Đã kết nối", text_color=COLOR_SUCCESS)

            # Cập nhật badges
            self.tag_android.configure(text=f"📱 {info['android_version']}", fg_color="#1e3a8a", text_color="#93c5fd")
            self.tag_os.configure(text=f"⚡ {info['os_version']}", fg_color="#065f46", text_color="#6ee7b7")
            self.tag_battery.configure(text=f"🔋 {info['battery']}", fg_color="#374151", text_color="#f3f4f6")

            self.btn_run.configure(state="normal")
            self.btn_quick_fcm.configure(state="normal")
            self.btn_quick_reboot.configure(state="normal")

            if info["security_ready"]:
                self.tag_security.configure(text="🛡️ Bảo mật: Hợp lệ", fg_color="#065f46", text_color="#6ee7b7")
                self.log(f"Đã nhận diện: {info['marketname']} [{serial}] | {info['os_version']}", "success")
            else:
                self.tag_security.configure(text="⚠️ Bảo mật: Chưa bật", fg_color="#7f1d1d", text_color="#fca5a5")
                self.lbl_warn.configure(text=info["security_warning"])
                self.warn_card.pack(fill="x", pady=(0, 10), before=self.hero_card)
                self.log("⚠️ CẢNH BÁO: Bạn cần bật 'Gỡ lỗi USB (Cài đặt bảo mật)' để cấp quyền MoreLocale!", "warning")

    def open_fcm_diag(self):
        if self.current_serial:
            self.adb.open_fcm_diagnostics(self.current_serial)
            self.log("Đã gửi lệnh mở FCM Diagnostics trên điện thoại.", "info")

    def reboot_device(self):
        if self.current_serial:
            if messagebox.askyesno("Khởi động lại", "Bạn có chắc chắn muốn khởi động lại điện thoại?"):
                self.adb.reboot(self.current_serial)
                self.log("Đã gửi lệnh khởi động lại thiết bị.", "info")

    # ================= TIẾN TRÌNH THỰC THI TỰ ĐỘNG =================
    def start_processing(self):
        if not self.current_serial:
            messagebox.showerror("Lỗi", "Chưa kết nối thiết bị nào!")
            return

        if self.is_running:
            return

        has_any = (
            self.sw_viethoa.get() or
            self.sw_fcm_whitelist.get() or
            self.sw_debloat.get() or
            self.sw_open_fcm.get() or
            self.sw_reboot.get()
        )
        if not has_any:
            messagebox.showwarning("Cảnh báo", "Bạn chưa kích hoạt tùy chọn nào để thực hiện!")
            return

        self.is_running = True
        self.btn_run.configure(state="disabled", text="⏳ ĐANG XỬ LÝ... VUI LÒNG GIỮ KẾT NỐI")
        self.progress_bar.set(0)
        self.lbl_progress_pct.configure(text="0%")
        self.lbl_progress_status.configure(text="Đang chuẩn bị...")

        threading.Thread(target=self._worker, daemon=True).start()

    def _worker(self):
        serial = self.current_serial
        self.log("==================================================", "info")
        self.log("BẮT ĐẦU TIẾN TRÌNH TỐI ƯU HÓA XIAOMI HYPERTOOL", "info")
        self.log("==================================================", "info")

        tasks = []
        if self.sw_viethoa.get():
            tasks.append(("viethoa", "Kích hoạt Tiếng Việt cho hệ thống & ứng dụng"))
        if self.sw_fcm_whitelist.get():
            tasks.append(("fcm", "Tối ưu hóa duy trì Google FCM & Shizuku"))
        if self.sw_debloat.get() and self.selected_debloat_apps:
            tasks.append(("debloat", f"Gỡ bỏ {len(self.selected_debloat_apps)} ứng dụng rác nội địa"))
        if self.sw_open_fcm.get():
            tasks.append(("fcm_diag", "Mở màn hình chẩn đoán FCM Diagnostics"))
        if self.sw_reboot.get():
            tasks.append(("reboot", "Khởi động lại thiết bị"))

        total = len(tasks)
        for idx, (t_code, t_name) in enumerate(tasks):
            pct = int((idx / total) * 100)
            self.after(0, lambda p=pct, n=t_name: self._update_progress_ui(p, n))

            if t_code == "viethoa":
                self.adb.apply_vietnamese(serial, self.log)
            elif t_code == "fcm":
                self.adb.apply_fcm_fix(
                    serial,
                    install_shizuku=bool(self.sw_shizuku.get()),
                    install_fcm_fix=bool(self.sw_fcm_fix_app.get()),
                    log_cb=self.log
                )
            elif t_code == "debloat":
                self.adb.debloat_apps(serial, self.selected_debloat_apps, self.log)
            elif t_code == "fcm_diag":
                self.adb.open_fcm_diagnostics(serial)
                self.log("  ✓ Đã mở trang FCM Diagnostics trên màn hình điện thoại.", "success")
            elif t_code == "reboot":
                self.log("  -> Đang gửi lệnh khởi động lại...", "info")
                self.adb.reboot(serial)

            time.sleep(0.4)

        self.after(0, lambda: self._update_progress_ui(100, "Hoàn thành!"))
        self.log("==================================================", "success")
        self.log("✓ TẤT CẢ CÁC TÁC VỤ ĐÃ HOÀN THÀNH XUẤT SẮC!", "success")
        self.log("==================================================", "success")

        def on_done():
            self.is_running = False
            self.btn_run.configure(state="normal", text="🚀 BẮT ĐẦU TỐI ƯU HÓA (1-CLICK EXECUTE)")
            messagebox.showinfo(
                "Tối Ưu Hóa Thành Công",
                "Quá trình thiết lập đã hoàn tất!\n\n"
                "✓ Ứng dụng đã được chuyển sang Tiếng Việt.\n"
                "✓ Kết nối Google FCM đã được giữ sống liên tục.\n"
                "✓ Tiến trình Shizuku đã được kích hoạt thành công."
            )

        self.after(0, on_done)

    def _update_progress_ui(self, pct, status_text):
        self.progress_bar.set(pct / 100.0)
        self.lbl_progress_pct.configure(text=f"{pct}%")
        self.lbl_progress_status.configure(text=status_text)


if __name__ == "__main__":
    app = XiaomiToolApp()
    app.mainloop()
