# -*- coding: utf-8 -*-
"""
Xiaomi HyperTool Pro - Backend Server & Desktop App Launcher
Khởi chạy giao diện Web-Desktop hiện đại, siêu mượt bằng Bottle & Microsoft Edge App Mode.
"""

import sys
import os
import subprocess
import threading
import time
import socket
import webbrowser
from bottle import Bottle, request, response, static_file, run
from adb_manager import ADBManager
from debloat_list import DEBLOAT_APPS

app = Bottle()
adb = ADBManager()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WEB_DIR = os.path.join(BASE_DIR, "web")

# Trạng thái tiến trình thực thi thời gian thực
execution_state = {
    "is_running": False,
    "percentage": 0,
    "current_task": "Sẵn sàng",
    "step_index": 1,
    "logs": [],
    "last_log_index": 0,
    "finished": False,
    "success": True
}
execution_lock = threading.Lock()

def add_log(msg, log_type="info"):
    with execution_lock:
        execution_state["logs"].append({"msg": msg, "type": log_type})

def find_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('127.0.0.1', 0))
        return s.getsockname()[1]

# ================= ROUTING =================
@app.route('/')
def index():
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return static_file('index.html', root=WEB_DIR)

@app.route('/static/<filepath:path>')
def serve_static(filepath):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    return static_file(filepath, root=WEB_DIR)

@app.route('/api/devices')
def api_devices():
    devices = adb.get_devices()
    if not devices:
        # Kiểm tra xem có máy nào ở chế độ Fastboot không
        fb_devs = adb.get_fastboot_devices()
        if fb_devs:
            fb_info = adb.get_fastboot_device_info(fb_devs[0]["serial"])
            return {
                "connected": True,
                "status": "fastboot",
                "serial": fb_devs[0]["serial"],
                "model": f"Fastboot ({fb_info.get('product', '')})",
                "marketname": f"Xiaomi Fastboot ({fb_info.get('product', '')})",
                "product": fb_info.get("product"),
                "bootloader_unlocked": fb_info.get("unlocked"),
                "anti": fb_info.get("anti")
            }
        return {"connected": False, "status": "none"}
    
    dev = devices[0]
    serial = dev["serial"]
    status = dev["status"]

    if status != "device":
        return {"connected": True, "status": status, "serial": serial}

    info = adb.get_device_info(serial)
    return {
        "connected": True,
        "status": "device",
        "serial": serial,
        "model": info["model"],
        "marketname": info["marketname"],
        "chipset": info.get("chipset", "Snapdragon/MediaTek"),
        "android_version": info["android_version"],
        "os_version": info["os_version"],
        "battery": info["battery"],
        "usb_debugging": info.get("usb_debugging", True),
        "security_ready": info["security_ready"],
        "security_warning": info["security_warning"],
        "ram_expand_disabled": info.get("ram_expand_disabled", False),
        "joyose_disabled": info.get("joyose_disabled", False),
        "gemini_ready": info.get("gemini_ready", False),
        "fcm_ready": info.get("fcm_ready", False),
        "morelocale_ready": info.get("morelocale_ready", False)
    }

import json

@app.route('/api/debloat-list')
def api_debloat_list():
    response.content_type = 'application/json; charset=utf-8'
    return json.dumps([
        {
            "package": a["package"],
            "name": a["name"],
            "desc": a["desc"],
            "safe": a["safe"],
            "default": a.get("default", False)
        }
        for a in DEBLOAT_APPS
    ], ensure_ascii=False)

@app.route('/api/action/fcm-diag', method='POST')
def api_action_fcm_diag():
    devices = adb.get_devices()
    if devices and devices[0]["status"] == "device":
        adb.open_fcm_diagnostics(devices[0]["serial"])
        return {"success": True}
    return {"success": False, "message": "Chưa có thiết bị hợp lệ"}

@app.route('/api/action/test-gemini', method='POST')
def api_action_test_gemini():
    devices = adb.get_devices()
    if devices and devices[0]["status"] == "device":
        adb.test_launch_gemini(devices[0]["serial"])
        return {"success": True}
    return {"success": False, "message": "Chưa có thiết bị hợp lệ"}

@app.route('/api/action/gemini-playstore', method='POST')
def api_action_gemini_playstore():
    devices = adb.get_devices()
    if devices and devices[0]["status"] == "device":
        adb.open_gemini_playstore(devices[0]["serial"])
        return {"success": True}
    return {"success": False, "message": "Chưa có thiết bị hợp lệ"}

@app.route('/api/action/restore-joyose', method='POST')
def api_action_restore_joyose():
    devices = adb.get_devices()
    if devices and devices[0]["status"] == "device":
        succ = adb.restore_joyose(devices[0]["serial"])
        return {"success": succ}
    return {"success": False, "message": "Chưa có thiết bị hợp lệ"}

@app.route('/api/action/reboot', method='POST')
def api_action_reboot():
    devices = adb.get_devices()
    if devices and devices[0]["status"] == "device":
        adb.reboot(devices[0]["serial"])
        return {"success": True}
    return {"success": False, "message": "Chưa có thiết bị hợp lệ"}

@app.route('/api/action/lock-usb', method='POST')
def api_action_lock_usb():
    devices = adb.get_devices()
    if devices and devices[0]["status"] == "device":
        succ = adb.lock_usb_debugging(devices[0]["serial"], add_log)
        return {"success": succ}
    return {"success": False, "message": "Chưa có thiết bị hợp lệ"}

# ================= FASTBOOT API =================
@app.route('/api/fastboot/status')
def api_fastboot_status():
    fb_devs = adb.get_fastboot_devices()
    if not fb_devs:
        # Cũng trả về xem có thiết bị adb đang cắm không
        adb_devs = adb.get_devices()
        return {
            "fastboot_connected": False,
            "adb_connected": bool(adb_devs and adb_devs[0]["status"] == "device"),
            "adb_serial": adb_devs[0]["serial"] if adb_devs else None
        }
    
    serial = fb_devs[0]["serial"]
    info = adb.get_fastboot_device_info(serial)
    return {
        "fastboot_connected": True,
        "serial": serial,
        "product": info.get("product"),
        "unlocked": info.get("unlocked"),
        "anti": info.get("anti"),
        "is_userspace": info.get("is_userspace")
    }

@app.route('/api/fastboot/reboot-to-fastboot', method='POST')
def api_fastboot_reboot_to_fastboot():
    devices = adb.get_devices()
    if devices and devices[0]["status"] == "device":
        add_log("-> Đang chuyển thiết bị vào chế độ Fastboot (adb reboot bootloader)...", "info")
        adb.reboot_to_fastboot(devices[0]["serial"])
        return {"success": True}
    return {"success": False, "message": "Không tìm thấy thiết bị ADB đang kết nối"}

@app.route('/api/fastboot/reboot-system', method='POST')
def api_fastboot_reboot_system():
    add_log("-> Đang khởi động lại từ Fastboot vào Android (fastboot reboot)...", "info")
    succ, out = adb.fastboot_reboot_system()
    return {"success": succ, "output": out}

@app.route('/api/fastboot/reboot-recovery', method='POST')
def api_fastboot_reboot_recovery():
    add_log("-> Đang khởi động lại vào Recovery (fastboot reboot recovery)...", "info")
    succ, out = adb.fastboot_reboot_recovery()
    return {"success": succ, "output": out}

@app.route('/api/fastboot/lock', method='POST')
def api_fastboot_lock():
    data = request.json or {}
    confirmed = data.get("confirmed", False)
    if not confirmed:
        return {"success": False, "message": "Bạn chưa xác nhận cam kết máy đã chạy đúng ROM China!"}
    
    fb_devs = adb.get_fastboot_devices()
    if not fb_devs:
        return {"success": False, "message": "Không tìm thấy thiết bị trong chế độ Fastboot!"}
    
    succ, out = adb.fastboot_lock_bootloader(fb_devs[0]["serial"], add_log)
    return {"success": succ, "output": out}

@app.route('/api/run/single', method='POST')
def api_run_single():
    with execution_lock:
        if execution_state["is_running"]:
            return {"success": False, "message": "Tiến trình khác đang chạy!"}
        
        devices = adb.get_devices()
        if not devices or devices[0]["status"] != "device":
            return {"success": False, "message": "Thiết bị chưa sẵn sàng!"}

        data = request.json or {}
        module_name = data.get("module")
        options = data.get("options", {})
        serial = devices[0]["serial"]

        # Reset state
        execution_state["is_running"] = True
        execution_state["percentage"] = 10
        execution_state["current_task"] = f"Khởi động module {module_name}..."
        execution_state["step_index"] = 1
        execution_state["logs"] = []
        execution_state["last_log_index"] = 0
        execution_state["finished"] = False
        execution_state["success"] = True

        threading.Thread(target=run_single_module_worker, args=(serial, module_name, options), daemon=True).start()
        return {"success": True}

def run_single_module_worker(serial, module_name, options):
    def log_cb(msg, mtype="info"):
        add_log(msg, mtype)

    try:
        with execution_lock:
            execution_state["percentage"] = 25

        if module_name == "viethoa":
            execution_state["current_task"] = "Kích hoạt Tiếng Việt cho hệ thống và ứng dụng..."
            adb.apply_vietnamese(serial, log_cb)
        elif module_name == "fcm":
            execution_state["current_task"] = "Tối ưu hóa kết nối Google FCM & Shizuku..."
            adb.apply_fcm_fix(
                serial,
                install_shizuku=bool(options.get("shizuku", True)),
                install_fcm_fix=bool(options.get("fcm_fix", True)),
                log_cb=log_cb
            )
        elif module_name == "gemini":
            execution_state["current_task"] = "Thiết lập Google Gemini làm AI chính..."
            adb.apply_gemini_assistant(
                serial,
                disable_xiaoai=bool(options.get("disable_xiaoai", True)),
                remap_power_key=bool(options.get("gemini_power_key", True)),
                log_cb=log_cb
            )
        elif module_name == "performance":
            execution_state["current_task"] = "Tối ưu hiệu năng & Cứu tinh đi phượt..."
            adb.apply_performance_boost(
                serial,
                disable_ram_expand=bool(options.get("disable_ram_expand", True)),
                disable_joyose=bool(options.get("disable_joyose", True)),
                compile_art=bool(options.get("compile_art", True)),
                run_fstrim=bool(options.get("run_fstrim", True)),
                log_cb=log_cb
            )
        elif module_name == "debloat":
            execution_state["current_task"] = "Gỡ bỏ ứng dụng rác nội địa..."
            adb.debloat_apps(serial, options.get("selected_apps", []), log_cb)
        elif module_name == "restore_joyose":
            execution_state["current_task"] = "Khôi phục lại Joyose..."
            adb.restore_joyose(serial, log_cb)
        elif module_name == "lock_usb":
            execution_state["current_task"] = "Khóa Developer Options & Tắt USB Debugging..."
            adb.lock_usb_debugging(serial, log_cb)

        with execution_lock:
            execution_state["percentage"] = 100
            execution_state["current_task"] = "Hoàn tất thành công!"
            execution_state["finished"] = True
            execution_state["is_running"] = False
            execution_state["success"] = True

    except Exception as e:
        log_cb(f"✕ Xảy ra lỗi: {str(e)}", "error")
        with execution_lock:
            execution_state["finished"] = True
            execution_state["is_running"] = False
            execution_state["success"] = False

@app.route('/api/start', method='POST')
def api_start():
    with execution_lock:
        if execution_state["is_running"]:
            return {"success": False, "message": "Tiến trình đang chạy!"}
        
        devices = adb.get_devices()
        if not devices or devices[0]["status"] != "device":
            return {"success": False, "message": "Thiết bị chưa sẵn sàng!"}

        options = request.json or {}
        serial = devices[0]["serial"]

        # Reset state
        execution_state["is_running"] = True
        execution_state["percentage"] = 0
        execution_state["current_task"] = "Khởi động..."
        execution_state["step_index"] = 1
        execution_state["logs"] = []
        execution_state["last_log_index"] = 0
        execution_state["finished"] = False
        execution_state["success"] = True

        threading.Thread(target=run_optimization_worker, args=(serial, options), daemon=True).start()
        return {"success": True}

@app.route('/api/progress')
def api_progress():
    with execution_lock:
        current_logs = execution_state["logs"]
        last_idx = execution_state["last_log_index"]
        new_logs = current_logs[last_idx:]
        execution_state["last_log_index"] = len(current_logs)

        return {
            "is_running": execution_state["is_running"],
            "percentage": execution_state["percentage"],
            "current_task": execution_state["current_task"],
            "step_index": execution_state["step_index"],
            "new_logs": new_logs,
            "finished": execution_state["finished"],
            "success": execution_state["success"]
        }

# ================= WORKER THREAD =================
def run_optimization_worker(serial, options):
    def log_cb(msg, mtype="info"):
        add_log(msg, mtype)

    try:
        tasks = []
        if options.get("viethoa"):
            tasks.append(("viethoa", 2, "Kích hoạt Tiếng Việt cho hệ thống và ứng dụng"))
        if options.get("fcm"):
            tasks.append(("fcm", 3, "Tối ưu hóa & giữ kết nối Google FCM"))
        if options.get("gemini"):
            tasks.append(("gemini", 4, "Thiết lập Google Gemini làm AI chính thay thế Xiaomi AI"))
        if options.get("performance"):
            tasks.append(("performance", 5, "Tối ưu hóa hiệu năng & Cứu tinh đi phượt (Tắt RAM ảo, Joyose, ART Compile)"))
        if options.get("debloat") and options.get("selected_apps"):
            tasks.append(("debloat", 6, f"Gỡ bỏ {len(options.get('selected_apps'))} ứng dụng rác nội địa"))
        if options.get("fcm_diag"):
            tasks.append(("fcm_diag", 6, "Mở kiểm tra Google FCM Diagnostics"))
        if options.get("lock_usb_debugging"):
            tasks.append(("lock_usb", 6, "Khóa Developer Options & Tắt USB Debugging (Bảo mật)"))
        if options.get("reboot"):
            tasks.append(("reboot", 6, "Khởi động lại thiết bị"))

        total = len(tasks)
        for idx, (t_code, step_num, t_name) in enumerate(tasks):
            with execution_lock:
                execution_state["current_task"] = t_name
                execution_state["step_index"] = step_num
                execution_state["percentage"] = int((idx / total) * 95)

            if t_code == "viethoa":
                adb.apply_vietnamese(serial, log_cb)
            elif t_code == "fcm":
                adb.apply_fcm_fix(
                    serial,
                    install_shizuku=bool(options.get("shizuku", True)),
                    install_fcm_fix=bool(options.get("fcm_fix", True)),
                    log_cb=log_cb
                )
            elif t_code == "gemini":
                adb.apply_gemini_assistant(
                    serial,
                    disable_xiaoai=bool(options.get("disable_xiaoai", True)),
                    remap_power_key=bool(options.get("gemini_power_key", True)),
                    log_cb=log_cb
                )
            elif t_code == "performance":
                adb.apply_performance_boost(
                    serial,
                    disable_ram_expand=bool(options.get("disable_ram_expand", True)),
                    disable_joyose=bool(options.get("disable_joyose", True)),
                    compile_art=bool(options.get("compile_art", True)),
                    run_fstrim=bool(options.get("run_fstrim", True)),
                    log_cb=log_cb
                )
            elif t_code == "debloat":
                adb.debloat_apps(serial, options.get("selected_apps", []), log_cb)
            elif t_code == "fcm_diag":
                adb.open_fcm_diagnostics(serial)
                log_cb("  ✓ Đã mở trang chẩn đoán FCM trên màn hình điện thoại.", "success")
            elif t_code == "lock_usb":
                adb.lock_usb_debugging(serial, log_cb)
            elif t_code == "reboot":
                log_cb("  -> Đang gửi lệnh khởi động lại thiết bị...", "info")
                adb.reboot(serial)

            time.sleep(0.4)

        with execution_lock:
            execution_state["percentage"] = 100
            execution_state["current_task"] = "Hoàn thành toàn bộ!"
            execution_state["step_index"] = 7
            execution_state["finished"] = True
            execution_state["is_running"] = False
            execution_state["success"] = True

    except Exception as e:
        log_cb(f"✕ Xảy ra lỗi trong tiến trình: {str(e)}", "error")
        with execution_lock:
            execution_state["finished"] = True
            execution_state["is_running"] = False
            execution_state["success"] = False

last_heartbeat = time.time()

@app.route('/api/heartbeat', method='POST')
def api_heartbeat():
    global last_heartbeat
    last_heartbeat = time.time()
    return {"status": "ok"}

@app.route('/api/shutdown', method='POST')
def api_shutdown():
    def do_exit():
        time.sleep(1)
        os._exit(0)
    threading.Thread(target=do_exit, daemon=True).start()
    return {"status": "shutting down"}

# ================= LAUNCH DESKTOP APP =================
def find_edge_path():
    candidates = [
        os.path.expandvars(r"%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe"),
        os.path.expandvars(r"%ProgramFiles%\Microsoft\Edge\Application\msedge.exe"),
        os.path.expandvars(r"%LocalAppData%\Microsoft\Edge\Application\msedge.exe"),
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    return None

def wait_for_server(port, timeout=8):
    start = time.time()
    while time.time() - start < timeout:
        try:
            with socket.create_connection(('127.0.0.1', port), timeout=0.3):
                return True
        except OSError:
            time.sleep(0.1)
    return False

def launch_app_window(url, port):
    # Đợi máy chủ sẵn sàng 100% trước khi mở trình duyệt
    if not wait_for_server(port):
        print("[LỖI] Máy chủ không phản hồi kịp thời!")
        return

    edge = find_edge_path()
    if edge:
        try:
            # Khởi chạy Edge dưới dạng Cửa sổ ứng dụng Native (không thanh URL, không tab)
            subprocess.Popen([
                edge,
                f"--app={url}",
                "--window-size=1180,860"
            ])
            return
        except Exception:
            pass
    
    # Fallback to default browser
    webbrowser.open(url)

def heartbeat_watcher():
    time.sleep(15)  # Thời gian chờ lúc mới khởi động
    while True:
        time.sleep(5)
        # Nếu không có tín hiệu heartbeat quá 15 giây (cửa sổ đã đóng) -> Tự tắt process
        if time.time() - last_heartbeat > 15:
            os._exit(0)

if __name__ == '__main__':
    port = 58888
    # Kiểm tra cổng có bị chiếm không
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('127.0.0.1', port))
    except OSError:
        port = find_free_port()

    server_url = f"http://127.0.0.1:{port}"
    print(f"==================================================")
    print(f"  Xiaomi HyperTool Pro dang khoi chay...")
    print(f"  Dia chi: {server_url}")
    print(f"==================================================")

    # Mở cửa sổ ứng dụng ở luồng riêng
    threading.Thread(target=launch_app_window, args=(server_url, port), daemon=True).start()
    threading.Thread(target=heartbeat_watcher, daemon=True).start()

    # Chạy Bottle server
    run(app, host='127.0.0.1', port=port, quiet=True)

