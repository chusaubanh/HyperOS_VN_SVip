// ==========================================================================
// HYPEROS VN SVIP — REDESIGN: SPA NAVIGATION + MODULE EXECUTION
// ==========================================================================

let debloatApps = [];
let selectedDebloatPackages = new Set();
let isRunning = false;
let currentSerial = null;
let currentFastbootProduct = null;
let terminalMinimized = false;

document.addEventListener("DOMContentLoaded", () => {
  if (window.lucide) lucide.createIcons();

  // Clock
  updateClock();
  setInterval(updateClock, 30000);

  // Heartbeat
  setInterval(() => {
    fetch('/api/heartbeat', { method: 'POST' }).catch(() => {});
  }, 3000);

  window.addEventListener('beforeunload', () => {
    navigator.sendBeacon('/api/shutdown');
  });

  // Initial data
  fetchDebloatList();
  pollDeviceStatus();
  setInterval(pollDeviceStatus, 3500);

  // Setup
  setupNavigation();
  setupEventListeners();

  // Show disclaimer on first visit
  if (!localStorage.getItem('svip-disclaimer-accepted')) {
    document.getElementById("disclaimerModal").style.display = "flex";
  }
});

function updateClock() {
  const now = new Date();
  const h = String(now.getHours()).padStart(2, "0");
  const m = String(now.getMinutes()).padStart(2, "0");
  const el = document.getElementById("scrClock");
  if (el) el.textContent = `${h}:${m}`;
}

// ==========================================================================
// SPA NAVIGATION
// ==========================================================================
function setupNavigation() {
  const navItems = document.querySelectorAll(".sb-nav .sb-item[data-page]");
  navItems.forEach(item => {
    item.addEventListener("click", (e) => {
      e.preventDefault();
      const targetPage = item.dataset.page;
      navigateTo(targetPage);
    });
  });
}

function navigateTo(pageName) {
  // Update sidebar active state
  document.querySelectorAll(".sb-nav .sb-item").forEach(el => el.classList.remove("active"));
  const activeNav = document.querySelector(`.sb-nav .sb-item[data-page="${pageName}"]`);
  if (activeNav) activeNav.classList.add("active");

  // Switch page
  document.querySelectorAll(".page").forEach(p => p.classList.remove("active"));
  const targetPage = document.querySelector(`.page[data-page="${pageName}"]`);
  if (targetPage) targetPage.classList.add("active");

  // Scroll to top
  document.querySelector(".main").scrollTop = 0;

  // Refresh icons
  if (window.lucide) lucide.createIcons();

  if (pageName === "romfastboot") {
    pollFastbootStatus();
  }
}

// ==========================================================================
// TELEMETRY POLLING
// ==========================================================================
async function pollDeviceStatus() {
  if (isRunning) return;
  try {
    const res = await fetch("/api/devices");
    const data = await res.json();
    updateDeviceUI(data);
  } catch (err) {
    console.warn("Telemetry error:", err);
  }
}

function updateDeviceUI(data) {
  const sbConn = document.getElementById("sbConn");
  const sbText = document.getElementById("sbConnText");
  const deviceName = document.getElementById("deviceName");
  const statOs = document.getElementById("statOs");
  const statAndroid = document.getElementById("statAndroid");
  const statBattery = document.getElementById("statBattery");
  const statSecurity = document.getElementById("statSecurity");
  const scrBatt = document.getElementById("scrBatt");
  const scrFcm = document.getElementById("scrFcm");
  const scrGem = document.getElementById("scrGem");
  const btnExecute = document.getElementById("btnExecute");
  const btnQuickFcm = document.getElementById("btnQuickFcm");
  const btnQuickReboot = document.getElementById("btnQuickReboot");
  const btnLockUsb = document.getElementById("btnLockUsb");
  const btnLockUsbBanner = document.getElementById("btnLockUsbBanner");
  const btnRunLockUsbPage = document.getElementById("btnRunLockUsbPage");
  const btnTestGemini = document.getElementById("btnTestGemini");
  const btnGeminiPlayStore = document.getElementById("btnGeminiPlayStore");
  const warnBanner = document.getElementById("securityWarningBanner");

  // Module run buttons
  const moduleRunBtns = document.querySelectorAll(".btn-run");

  if (!data.connected) {
    currentSerial = null;
    sbConn.className = "sb-conn";
    sbText.textContent = "Chưa kết nối USB";
    deviceName.textContent = "Chưa phát hiện thiết bị";
    deviceName.style.color = "var(--text-3)";

    statOs.textContent = "HyperOS --";
    statAndroid.textContent = "Android --";
    statBattery.textContent = "--%";
    statSecurity.textContent = "Chưa kết nối";
    statSecurity.className = "stat-v";

    if (scrBatt) scrBatt.textContent = "--%";
    if (scrFcm) scrFcm.style.opacity = "0.3";
    if (scrGem) scrGem.style.opacity = "0.3";

    btnExecute.disabled = true;
    btnQuickFcm.disabled = true;
    btnQuickReboot.disabled = true;
    if (btnLockUsb) btnLockUsb.disabled = true;
    if (btnLockUsbBanner) btnLockUsbBanner.disabled = true;
    if (btnRunLockUsbPage) btnRunLockUsbPage.disabled = true;
    if (btnTestGemini) btnTestGemini.disabled = true;
    if (btnGeminiPlayStore) btnGeminiPlayStore.disabled = true;
    moduleRunBtns.forEach(b => b.disabled = true);
    warnBanner.style.display = "none";

    updateHealthMatrix(null);

  } else if (data.status === "unauthorized") {
    currentSerial = null;
    sbConn.className = "sb-conn";
    sbText.textContent = "Chờ xác nhận...";
    deviceName.textContent = "Mở khóa & Bấm 'Cho phép gỡ lỗi USB'";
    deviceName.style.color = "var(--accent)";

    btnExecute.disabled = true;
    btnQuickFcm.disabled = true;
    btnQuickReboot.disabled = true;
    if (btnLockUsb) btnLockUsb.disabled = true;
    if (btnLockUsbBanner) btnLockUsbBanner.disabled = true;
    if (btnRunLockUsbPage) btnRunLockUsbPage.disabled = true;
    if (btnTestGemini) btnTestGemini.disabled = true;
    if (btnGeminiPlayStore) btnGeminiPlayStore.disabled = true;
    moduleRunBtns.forEach(b => b.disabled = true);
    warnBanner.style.display = "none";

    updateHealthMatrix(null);

  } else {
    currentSerial = data.serial;
    sbConn.className = "sb-conn connected";
    sbText.textContent = data.marketname || data.model;
    deviceName.textContent = `${data.marketname} (${data.model})`;
    deviceName.style.color = "var(--text-1)";

    statOs.textContent = data.os_version;
    statAndroid.textContent = data.android_version;
    statBattery.textContent = data.battery;

    if (scrBatt) scrBatt.textContent = data.battery;
    if (scrFcm) scrFcm.style.opacity = "1";
    if (scrGem) scrGem.style.opacity = "1";

    btnExecute.disabled = isRunning;
    btnQuickFcm.disabled = false;
    btnQuickReboot.disabled = false;
    if (btnLockUsb) btnLockUsb.disabled = isRunning;
    if (btnLockUsbBanner) btnLockUsbBanner.disabled = isRunning;
    if (btnRunLockUsbPage) btnRunLockUsbPage.disabled = isRunning;
    if (btnTestGemini) btnTestGemini.disabled = false;
    if (btnGeminiPlayStore) btnGeminiPlayStore.disabled = false;
    moduleRunBtns.forEach(b => b.disabled = isRunning);

    if (data.security_ready) {
      statSecurity.textContent = "Đầy đủ quyền";
      statSecurity.className = "stat-v text-emerald";
      warnBanner.style.display = "none";
    } else {
      statSecurity.textContent = "Chưa bật bảo mật";
      statSecurity.className = "stat-v text-amber";
      warnBanner.style.display = "flex";
      document.getElementById("warnMessage").textContent = data.security_warning || "";
    }

    updateHealthMatrix(data);
  }

  if (window.lucide) lucide.createIcons();
}

function updateHealthMatrix(data) {
  const setHealth = (dotId, valId, ok, text) => {
    const dot = document.getElementById(dotId);
    const val = document.getElementById(valId);
    if (dot) dot.className = ok === null ? "h-dot" : ok ? "h-dot ok" : "h-dot bad";
    if (val) val.textContent = text;
  };

  if (!data) {
    setHealth("hdUsb", "hUsb", null, "Đang kiểm tra...");
    setHealth("hdSec", "hSec", null, "Đang kiểm tra...");
    setHealth("hdFcm", "hFcm", null, "Đang kiểm tra...");
    setHealth("hdGem", "hGem", null, "Đang kiểm tra...");
    setHealth("hdJoy", "hJoy", null, "Đang kiểm tra...");
    setHealth("hdMlc", "hMlc", null, "Đang kiểm tra...");
    return;
  }

  setHealth("hdUsb", "hUsb", data.usb_debugging !== false, data.usb_debugging !== false ? "Đã bật" : "Chưa bật");
  setHealth("hdSec", "hSec", data.security_ready, data.security_ready ? "Đầy đủ quyền" : "Chưa bật");
  setHealth("hdFcm", "hFcm", data.fcm_ready, data.fcm_ready ? "Đã tối ưu" : "Chưa tối ưu");
  setHealth("hdGem", "hGem", data.gemini_ready, data.gemini_ready ? "Đã thiết lập" : "Chưa thiết lập");
  setHealth("hdJoy", "hJoy", data.joyose_disabled, data.joyose_disabled ? "Đã vô hiệu" : "Đang hoạt động");
  setHealth("hdMlc", "hMlc", data.morelocale_ready, data.morelocale_ready ? "Đã cài đặt" : "Chưa cài");
}

// ==========================================================================
// DEBLOAT LIST & MODAL
// ==========================================================================
async function fetchDebloatList() {
  try {
    const res = await fetch("/api/debloat-list");
    debloatApps = await res.json();
    debloatApps.forEach(app => {
      if (app.default) selectedDebloatPackages.add(app.package);
    });
    updateDebloatCounterUI();
    renderModalAppList();
  } catch (err) {
    console.error("Debloat list error:", err);
  }
}

function updateDebloatCounterUI() {
  const countEl = document.getElementById("debloatSelectedCount");
  if (countEl) {
    countEl.innerHTML = `<i data-lucide="package-check"></i> Đang chọn <strong>${selectedDebloatPackages.size}</strong> ứng dụng an toàn`;
    if (window.lucide) lucide.createIcons();
  }
  const modalCount = document.getElementById("modalCounterText");
  if (modalCount) {
    modalCount.textContent = `Đã chọn: ${selectedDebloatPackages.size} / ${debloatApps.length} ứng dụng`;
  }
}

function renderModalAppList(query = "") {
  const container = document.getElementById("modalAppList");
  container.innerHTML = "";
  const q = query.trim().toLowerCase();
  const filtered = debloatApps.filter(app =>
    !q || app.name.toLowerCase().includes(q) || app.package.toLowerCase().includes(q) || app.desc.toLowerCase().includes(q)
  );

  filtered.forEach(app => {
    const isChecked = selectedDebloatPackages.has(app.package);
    const card = document.createElement("div");
    card.className = "package-item";
    card.innerHTML = `
      <label class="opt-row" style="margin-top:2px;">
        <input type="checkbox" data-pkg="${app.package}" ${isChecked ? "checked" : ""}>
        <span class="cb"></span>
      </label>
      <div class="pkg-info">
        <div class="pkg-name-row"><span>${app.name}</span>${app.safe ? '<span class="badge-verified">Đã kiểm nghiệm</span>' : ''}</div>
        <div class="pkg-code">${app.package}</div>
        <div class="pkg-desc">${app.desc}</div>
      </div>`;

    card.querySelector("input").addEventListener("change", (e) => {
      if (e.target.checked) selectedDebloatPackages.add(app.package);
      else selectedDebloatPackages.delete(app.package);
      updateDebloatCounterUI();
    });
    container.appendChild(card);
  });
}

// ==========================================================================
// EVENT LISTENERS
// ==========================================================================
function setupEventListeners() {
  // Rescan
  document.getElementById("btnRescan").addEventListener("click", () => {
    const icon = document.getElementById("iconRescan");
    icon.style.animation = "spin 0.6s linear";
    pollDeviceStatus().then(() => setTimeout(() => icon.style.animation = "", 600));
  });

  // Quick actions
  document.getElementById("btnQuickFcm").addEventListener("click", async () => {
    appendLog("Lệnh: Mở FCM Diagnostics (*#*#426#*#*)...", "info");
    await fetch("/api/action/fcm-diag", { method: "POST" });
  });

  document.getElementById("btnQuickReboot").addEventListener("click", async () => {
    if (confirm("Khởi động lại thiết bị ngay bây giờ?")) {
      appendLog("Lệnh: Khởi động lại thiết bị...", "warning");
      await fetch("/api/action/reboot", { method: "POST" });
    }
  });

  const triggerLockUsbConfirm = () => {
    if (!currentSerial || isRunning) return;
    const ok = confirm("🔒 BẠN CÓ CHẮC CHẮN MUỐN KHÓA DEVELOPER OPTIONS & TẮT USB DEBUGGING?\n\n- Thao tác này sẽ tắt chế độ nhà phát triển và ngắt kết nối USB với máy tính.\n- Rất hữu ích để điện thoại mở được các ứng dụng Ngân hàng, Ví điện tử, VNeID mà không bị báo lỗi phát hiện USB Debug.\n\n(Lần sau nếu muốn kết nối lại máy tính, bạn chỉ cần vào Cài đặt > Giới thiệu điện thoại > Nhấn 7 lần vào Phiên bản OS).");
    if (ok) {
      lockUsbDebugging();
    }
  };

  const btnLockUsb = document.getElementById("btnLockUsb");
  if (btnLockUsb) btnLockUsb.addEventListener("click", triggerLockUsbConfirm);

  const btnLockUsbBanner = document.getElementById("btnLockUsbBanner");
  if (btnLockUsbBanner) btnLockUsbBanner.addEventListener("click", triggerLockUsbConfirm);

  const btnRunLockUsbPage = document.getElementById("btnRunLockUsbPage");
  if (btnRunLockUsbPage) btnRunLockUsbPage.addEventListener("click", triggerLockUsbConfirm);

  // Gemini actions
  const btnTestGemini = document.getElementById("btnTestGemini");
  if (btnTestGemini) {
    btnTestGemini.addEventListener("click", async () => {
      appendLog("Lệnh: Test gọi Gemini trên điện thoại...", "info");
      const res = await fetch("/api/action/test-gemini", { method: "POST" });
      const d = await res.json();
      appendLog(d.success ? "✓ Đã gửi lệnh gọi Gemini." : `[!] ${d.message}`, d.success ? "success" : "warning");
    });
  }

  const btnGeminiPS = document.getElementById("btnGeminiPlayStore");
  if (btnGeminiPS) {
    btnGeminiPS.addEventListener("click", async () => {
      appendLog("Lệnh: Mở CH Play → Google Gemini...", "info");
      const res = await fetch("/api/action/gemini-playstore", { method: "POST" });
      const d = await res.json();
      appendLog(d.success ? "✓ Đã mở Google Play Store." : `[!] ${d.message}`, d.success ? "success" : "warning");
    });
  }

  // Module run buttons (individual)
  document.querySelectorAll(".btn-run[data-module]").forEach(btn => {
    btn.addEventListener("click", () => runSingleModule(btn.dataset.module));
  });

  // Debloat modal
  document.getElementById("btnOpenDebloatModal").addEventListener("click", () => {
    document.getElementById("debloatModal").style.display = "flex";
    renderModalAppList();
  });
  document.getElementById("btnCloseModal").addEventListener("click", () => {
    document.getElementById("debloatModal").style.display = "none";
  });
  document.getElementById("btnSaveModal").addEventListener("click", () => {
    document.getElementById("debloatModal").style.display = "none";
    updateDebloatCounterUI();
  });
  document.getElementById("modalSearchInput").addEventListener("input", (e) => {
    renderModalAppList(e.target.value);
  });
  document.getElementById("btnSelectSafe").addEventListener("click", () => {
    debloatApps.forEach(app => { if (app.safe) selectedDebloatPackages.add(app.package); });
    renderModalAppList(document.getElementById("modalSearchInput").value);
    updateDebloatCounterUI();
  });
  document.getElementById("btnDeselectAll").addEventListener("click", () => {
    selectedDebloatPackages.clear();
    renderModalAppList(document.getElementById("modalSearchInput").value);
    updateDebloatCounterUI();
  });

  // Disclaimer modal
  document.getElementById("btnDisclaimer").addEventListener("click", () => {
    document.getElementById("disclaimerModal").style.display = "flex";
  });
  document.getElementById("btnCloseDisclaimer").addEventListener("click", () => {
    document.getElementById("disclaimerModal").style.display = "none";
  });
  document.getElementById("btnAcceptDisclaimer").addEventListener("click", () => {
    localStorage.setItem('svip-disclaimer-accepted', 'true');
    document.getElementById("disclaimerModal").style.display = "none";
  });

  // Fastboot controls
  setupFastbootListeners();

  // Terminal controls
  document.getElementById("btnClearLog").addEventListener("click", () => {
    document.getElementById("terminalConsole").innerHTML = "";
  });
  document.getElementById("btnMinTerm").addEventListener("click", () => {
    terminalMinimized = !terminalMinimized;
    const body = document.getElementById("terminalConsole");
    const chevron = document.getElementById("termChevron");
    body.classList.toggle("collapsed", terminalMinimized);
    if (chevron) {
      chevron.setAttribute("data-lucide", terminalMinimized ? "chevrons-up" : "chevrons-down");
      lucide.createIcons();
    }
  });

  // Run All
  document.getElementById("btnExecute").addEventListener("click", startFullExecution);
}

// ==========================================================================
// SINGLE MODULE EXECUTION
// ==========================================================================
async function runSingleModule(moduleName) {
  if (!currentSerial || isRunning) return;

  const options = {};
  if (moduleName === "fcm") {
    options.shizuku = document.getElementById("swShizuku")?.checked ?? true;
    options.fcm_fix = document.getElementById("swFcmFix")?.checked ?? true;
  } else if (moduleName === "gemini") {
    options.disable_xiaoai = document.getElementById("swDisableXiaoAi")?.checked ?? true;
    options.gemini_power_key = document.getElementById("swGeminiPowerKey")?.checked ?? true;
  } else if (moduleName === "debloat") {
    options.selected_apps = Array.from(selectedDebloatPackages);
  } else if (moduleName === "performance") {
    options.disable_ram_expand = document.getElementById("swRamExpand")?.checked ?? true;
    options.disable_joyose = document.getElementById("swJoyose")?.checked ?? true;
    options.compile_art = document.getElementById("swArt")?.checked ?? true;
    options.run_fstrim = document.getElementById("swFstrim")?.checked ?? true;
  }

  isRunning = true;
  document.querySelectorAll(".btn-run").forEach(b => b.disabled = true);
  appendLog(`>>> Khởi động module: ${moduleName.toUpperCase()} <<<`, "info");

  // Expand terminal if minimized
  if (terminalMinimized) {
    terminalMinimized = false;
    document.getElementById("terminalConsole").classList.remove("collapsed");
  }

  try {
    const res = await fetch("/api/run/single", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ module: moduleName, options })
    });
    const data = await res.json();
    if (data.success) {
      pollProgressStream(() => {
        isRunning = false;
        document.querySelectorAll(".btn-run").forEach(b => b.disabled = false);
        pollDeviceStatus();
      });
    } else {
      appendLog(`Lỗi: ${data.message}`, "error");
      isRunning = false;
      document.querySelectorAll(".btn-run").forEach(b => b.disabled = false);
    }
  } catch (err) {
    appendLog(`Lỗi: ${err.message}`, "error");
    isRunning = false;
    document.querySelectorAll(".btn-run").forEach(b => b.disabled = false);
  }
}

// ==========================================================================
// FULL PIPELINE EXECUTION
// ==========================================================================
async function startFullExecution() {
  if (!currentSerial || isRunning) return;

  const payload = {
    viethoa: document.getElementById("swViethoa")?.checked,
    fcm: document.getElementById("swFcm")?.checked,
    shizuku: document.getElementById("swShizuku")?.checked ?? true,
    fcm_fix: document.getElementById("swFcmFix")?.checked ?? true,
    gemini: document.getElementById("swGemini")?.checked,
    disable_xiaoai: document.getElementById("swDisableXiaoAi")?.checked ?? true,
    gemini_power_key: document.getElementById("swGeminiPowerKey")?.checked ?? true,
    debloat: document.getElementById("swDebloat")?.checked,
    selected_apps: Array.from(selectedDebloatPackages),
    fcm_diag: document.getElementById("swOpenDiag")?.checked,
    lock_usb_debugging: document.getElementById("swLockUsb")?.checked,
    reboot: document.getElementById("swReboot")?.checked
  };

  if (!payload.viethoa && !payload.fcm && !payload.gemini && !payload.debloat && !payload.fcm_diag && !payload.reboot) {
    alert("Vui lòng kích hoạt ít nhất 1 mục!");
    return;
  }

  isRunning = true;
  document.getElementById("btnExecute").disabled = true;
  document.getElementById("btnExecuteText").textContent = "ĐANG TỐI ƯU HÓA... GIỮ CÁP USB";
  resetPipelineSteps();

  // Expand terminal
  if (terminalMinimized) {
    terminalMinimized = false;
    document.getElementById("terminalConsole").classList.remove("collapsed");
  }

  try {
    const res = await fetch("/api/start", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    if (data.success) {
      appendLog(">>> KHỞI ĐỘNG PIPELINE TỐI ƯU HÓA [SVIP ENGINE] <<<", "info");
      pollProgressStream(() => {
        finishExecution(true);
      });
    } else {
      appendLog(`Lỗi: ${data.message}`, "error");
      resetExecuteButton();
    }
  } catch (err) {
    appendLog(`Lỗi: ${err.message}`, "error");
    resetExecuteButton();
  }
}

// ==========================================================================
// LOCK USB & DEVELOPER OPTIONS
// ==========================================================================
async function lockUsbDebugging() {
  if (!currentSerial || isRunning) return;
  isRunning = true;
  appendLog(">>> Đang khóa Developer Options & Tắt USB Debugging... <<<", "warning");

  if (terminalMinimized) {
    terminalMinimized = false;
    document.getElementById("terminalConsole").classList.remove("collapsed");
  }

  try {
    const res = await fetch("/api/action/lock-usb", { method: "POST" });
    const data = await res.json();
    if (data.success) {
      appendLog("✓ ĐÃ KHÓA THÀNH CÔNG: Chế độ nhà phát triển & USB Debugging đã tắt!", "success");
      appendLog("  Máy tính đã tự động ngắt kết nối USB. Bạn có thể mở app ngân hàng, VNeID bình thường.", "info");
      alert("ĐÃ KHÓA THÀNH CÔNG!\n\n1. Chế độ Nhà phát triển (Developer Options) đã được ẩn đi.\n2. Chế độ Gỡ lỗi USB (USB Debugging) đã tắt hoàn toàn.\n3. Điện thoại bây giờ có thể sử dụng các ứng dụng Ngân hàng, Ví điện tử, VNeID mà không lo bị chặn bảo mật.\n\n(Nếu sau này cần tối ưu tiếp, bạn chỉ cần vào Cài đặt > Giới thiệu điện thoại > Nhấn 7 lần vào Phiên bản OS để mở lại).");
    } else {
      appendLog(`Lỗi: ${data.message || 'Không thể khóa'}`, "error");
    }
  } catch (err) {
    appendLog("✓ Đã áp dụng thiết lập. Kết nối ADB đã tự động ngắt.", "success");
  } finally {
    isRunning = false;
    pollDeviceStatus();
  }
}

function pollProgressStream(onComplete) {
  const interval = setInterval(async () => {
    try {
      const res = await fetch("/api/progress");
      const data = await res.json();

      const progFill = document.getElementById("progressBarFill");
      const progPct = document.getElementById("progressPercentage");
      const progStatus = document.getElementById("progressStatusText");

      if (progFill) progFill.style.width = `${data.percentage}%`;
      if (progPct) progPct.textContent = `${data.percentage}%`;
      if (progStatus) progStatus.textContent = data.current_task || "Đang xử lý...";

      updatePipelineNode(data.step_index);

      if (data.new_logs && data.new_logs.length > 0) {
        data.new_logs.forEach(log => appendLog(log.msg, log.type));
      }

      if (data.finished) {
        clearInterval(interval);
        if (data.success) {
          appendLog(">>> TẤT CẢ TÁC VỤ ĐÃ HOÀN TẤT THÀNH CÔNG! <<<", "success");
          triggerCelebration();
          playChime();
        }
        if (onComplete) onComplete();
      }
    } catch (err) {
      console.error("Progress poll error:", err);
    }
  }, 400);
}

function updatePipelineNode(stepIndex) {
  for (let i = 1; i <= 6; i++) {
    const node = document.getElementById(`stepNode${i}`);
    const line = document.getElementById(`stepLine${i}`);
    if (!node) continue;
    if (i < stepIndex) {
      node.className = "pipe-step completed";
      if (line) line.className = "pipe-line completed";
    } else if (i === stepIndex) {
      node.className = "pipe-step active";
    } else {
      node.className = "pipe-step";
      if (line) line.className = "pipe-line";
    }
  }
}

function resetPipelineSteps() {
  for (let i = 1; i <= 6; i++) {
    const node = document.getElementById(`stepNode${i}`);
    const line = document.getElementById(`stepLine${i}`);
    if (node) node.className = "pipe-step";
    if (line) line.className = "pipe-line";
  }
  const first = document.getElementById("stepNode1");
  if (first) first.className = "pipe-step active";
}

function finishExecution(success) {
  updatePipelineNode(7);
  const lastNode = document.getElementById("stepNode6");
  if (lastNode) lastNode.className = "pipe-step completed";

  const progFill = document.getElementById("progressBarFill");
  const progPct = document.getElementById("progressPercentage");
  const progStatus = document.getElementById("progressStatusText");
  if (progFill) progFill.style.width = "100%";
  if (progPct) progPct.textContent = "100%";
  if (progStatus) progStatus.textContent = "Hoàn tất xuất sắc!";

  resetExecuteButton();
  pollDeviceStatus();
}

function resetExecuteButton() {
  isRunning = false;
  const btn = document.getElementById("btnExecute");
  if (btn) btn.disabled = false;
  const text = document.getElementById("btnExecuteText");
  if (text) text.textContent = "BẮT ĐẦU TỐI ƯU HÓA [SVIP ENGINE]";
}

// ==========================================================================
// TERMINAL LOGGING
// ==========================================================================
function appendLog(message, type = "info") {
  const consoleEl = document.getElementById("terminalConsole");
  const now = new Date();
  const ts = `[${String(now.getHours()).padStart(2,"0")}:${String(now.getMinutes()).padStart(2,"0")}:${String(now.getSeconds()).padStart(2,"0")}]`;
  const line = document.createElement("div");
  line.className = `log-entry log-${type}`;
  line.innerHTML = `<span class="log-ts">${ts}</span> ${escapeHtml(message)}`;
  consoleEl.appendChild(line);
  consoleEl.scrollTop = consoleEl.scrollHeight;
}

function escapeHtml(text) {
  const map = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' };
  return text.replace(/[&<>"']/g, m => map[m]);
}

// ==========================================================================
// CELEBRATION
// ==========================================================================
function triggerCelebration() {
  if (typeof confetti === "function") {
    confetti({ particleCount: 90, spread: 75, origin: { y: 0.65 }, colors: ['#f59e0b','#06b6d4','#10b981','#fbbf24','#f43f5e'] });
  }
}

function playChime() {
  try {
    const ctx = new (window.AudioContext || window.webkitAudioContext)();
    const now = ctx.currentTime;
    [587.33, 739.99, 880, 1174.66].forEach((freq, i) => {
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = "sine";
      osc.frequency.setValueAtTime(freq, now + i * 0.08);
      gain.gain.setValueAtTime(0.14, now + i * 0.08);
      gain.gain.exponentialRampToValueAtTime(0.001, now + i * 0.08 + 0.35);
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.start(now + i * 0.08);
      osc.stop(now + i * 0.08 + 0.4);
    });
  } catch (e) {}
}

// ==========================================================================
// FASTBOOT & BOOTLOADER LOGIC
// ==========================================================================
async function pollFastbootStatus() {
  try {
    const res = await fetch("/api/fastboot/status");
    const data = await res.json();

    const dot = document.getElementById("fbStatusDot");
    const text = document.getElementById("fbStatusText");
    const sub = document.getElementById("fbStatusSub");
    const codename = document.getElementById("fbCodename");
    const blStatus = document.getElementById("fbBootloaderStatus");

    const boxCodename = document.getElementById("fbBoxCodename");
    const boxBl = document.getElementById("fbBoxBootloader");
    const boxSerial = document.getElementById("fbBoxSerial");
    const boxAnti = document.getElementById("fbBoxAnti");

    const btnRebootSys = document.getElementById("btnFbRebootSys");
    const btnRebootRec = document.getElementById("btnFbRebootRec");
    const btnOpenLock = document.getElementById("btnOpenLockModal");

    if (data.fastboot_connected) {
      currentFastbootProduct = data.product || "garnet";
      if (dot) dot.className = "fb-qb-indicator connected";
      if (text) text.textContent = `Đã kết nối Fastboot [${data.serial}]`;
      if (sub) sub.textContent = "Thiết bị đã sẵn sàng cho các bước tiếp theo";

      const prodName = data.product || "Không xác định";
      if (codename) codename.textContent = prodName;
      if (boxCodename) boxCodename.textContent = prodName;

      let blText = "--";
      let blColor = "";
      if (data.unlocked === true) {
        blText = "ĐÃ MỞ (UNLOCKED)";
        blColor = "#fbbf24";
      } else if (data.unlocked === false) {
        blText = "ĐÃ KHÓA (LOCKED)";
        blColor = "#34d399";
      } else {
        blText = "Không xác định";
      }

      if (blStatus) {
        blStatus.textContent = blText;
        if (blColor) blStatus.style.color = blColor;
      }
      if (boxBl) {
        boxBl.textContent = blText;
        if (blColor) boxBl.style.color = blColor;
      }

      if (boxSerial) boxSerial.textContent = data.serial || "--";
      if (boxAnti) boxAnti.textContent = data.anti || "Không có (0)";

      if (btnRebootSys) btnRebootSys.disabled = false;
      if (btnRebootRec) btnRebootRec.disabled = false;
      if (btnOpenLock) btnOpenLock.disabled = false;

    } else {
      if (dot) dot.className = "fb-qb-indicator";
      if (text) text.textContent = data.adb_connected ? `Máy đang ở Android ADB (${data.adb_serial})` : "Chưa phát hiện thiết bị Fastboot";
      if (sub) sub.textContent = data.adb_connected ? "Nhấn nút ở Bước 1 để tự động đưa máy vào Fastboot" : "Cắm cáp USB và bắt đầu từ Bước 1";

      if (codename) codename.textContent = "--";
      if (blStatus) { blStatus.textContent = "--"; blStatus.style.color = ""; }
      if (boxCodename) boxCodename.textContent = "--";
      if (boxBl) { boxBl.textContent = "--"; boxBl.style.color = ""; }
      if (boxSerial) boxSerial.textContent = "--";
      if (boxAnti) boxAnti.textContent = "--";

      if (btnRebootSys) btnRebootSys.disabled = true;
      if (btnRebootRec) btnRebootRec.disabled = true;
      if (btnOpenLock) btnOpenLock.disabled = true;
    }

  } catch (err) {
    console.warn("Fastboot status poll error:", err);
  }
}

function setupFastbootListeners() {
  // Reboot to Fastboot from ADB (Bước 1)
  const btnRebootToFb = document.getElementById("btnRebootToFb");
  if (btnRebootToFb) {
    btnRebootToFb.addEventListener("click", async () => {
      appendLog("-> Đang gửi lệnh chuyển máy vào Fastboot (adb reboot bootloader)...", "info");
      const res = await fetch("/api/fastboot/reboot-to-fastboot", { method: "POST" });
      const data = await res.json();
      if (data.success) {
        appendLog("✓ Đang khởi động lại vào Fastboot. Màn hình máy sẽ hiện chữ FASTBOOT màu cam!", "success");
        setTimeout(pollFastbootStatus, 3500);
      } else {
        appendLog(`[!] Không thể vào Fastboot: ${data.message}`, "warning");
      }
    });
  }

  // Quét thiết bị Fastboot (Bước 2)
  const btnStep2Scan = document.getElementById("btnStep2ScanFb");
  if (btnStep2Scan) {
    btnStep2Scan.addEventListener("click", () => {
      appendLog("-> Đang quét thiết bị Fastboot và đọc thông số máy...", "info");
      pollFastbootStatus();
    });
  }

  // Fastboot Rescan (Nút nhỏ trên thanh status bar)
  const btnFbRescan = document.getElementById("btnFbRescan");
  if (btnFbRescan) {
    btnFbRescan.addEventListener("click", () => {
      appendLog("Đang làm mới trạng thái Fastboot...", "info");
      pollFastbootStatus();
    });
  }

  // Fastboot Reboot System
  const btnFbRebootSys = document.getElementById("btnFbRebootSys");
  if (btnFbRebootSys) {
    btnFbRebootSys.addEventListener("click", async () => {
      appendLog("Lệnh: Khởi động vào Hệ thống (fastboot reboot)...", "info");
      const res = await fetch("/api/fastboot/reboot-system", { method: "POST" });
      const data = await res.json();
      appendLog(data.success ? "✓ Lệnh gửi thành công. Điện thoại đang khởi động lại." : `✕ Lỗi: ${data.output}`, data.success ? "success" : "error");
      setTimeout(pollFastbootStatus, 3000);
    });
  }

  // Fastboot Reboot Recovery
  const btnFbRebootRec = document.getElementById("btnFbRebootRec");
  if (btnFbRebootRec) {
    btnFbRebootRec.addEventListener("click", async () => {
      appendLog("Lệnh: Khởi động vào Recovery (fastboot reboot recovery)...", "info");
      const res = await fetch("/api/fastboot/reboot-recovery", { method: "POST" });
      const data = await res.json();
      appendLog(data.success ? "✓ Đã gửi lệnh reboot recovery." : `✕ Lỗi: ${data.output}`, data.success ? "success" : "error");
    });
  }

  // External Links (Bước 3)
  const btnOpenMifirm = document.getElementById("btnOpenMifirm");
  if (btnOpenMifirm) {
    btnOpenMifirm.addEventListener("click", () => {
      appendLog("Mở trang chủ Mifirm.net để tự tìm ROM...", "info");
      window.open("https://mifirm.net/", "_blank");
    });
  }

  const btnOpenXiaomiFw = document.getElementById("btnOpenXiaomiFw");
  if (btnOpenXiaomiFw) {
    btnOpenXiaomiFw.addEventListener("click", () => {
      appendLog("Mở trang chủ XM Firmware Updater để tự tìm ROM...", "info");
      window.open("https://xmfirmwareupdater.com/", "_blank");
    });
  }

  const btnOpenMiFlash = document.getElementById("btnOpenMiFlashLink");
  if (btnOpenMiFlash) {
    btnOpenMiFlash.addEventListener("click", () => {
      appendLog("Mở trang tải phần mềm MiFlash Tool chính hãng...", "info");
      window.open("https://xiaomiflashtool.com/", "_blank");
    });
  }

  // Lock Modal
  const btnOpenLockModal = document.getElementById("btnOpenLockModal");
  const modal = document.getElementById("fastbootLockModal");
  const btnCloseLockModal = document.getElementById("btnCloseLockModal");
  const chkConfirm = document.getElementById("chkConfirmChinaRom");
  const btnConfirmLock = document.getElementById("btnConfirmFastbootLock");

  if (btnOpenLockModal && modal) {
    btnOpenLockModal.addEventListener("click", () => {
      if (chkConfirm) chkConfirm.checked = false;
      if (btnConfirmLock) btnConfirmLock.disabled = true;
      modal.style.display = "flex";
    });
  }

  if (btnCloseLockModal && modal) {
    btnCloseLockModal.addEventListener("click", () => {
      modal.style.display = "none";
    });
  }

  if (chkConfirm && btnConfirmLock) {
    chkConfirm.addEventListener("change", () => {
      btnConfirmLock.disabled = !chkConfirm.checked;
    });
  }

  if (btnConfirmLock) {
    btnConfirmLock.addEventListener("click", async () => {
      if (!chkConfirm.checked) return;
      modal.style.display = "none";
      appendLog(">>> ĐANG GỬI LỆNH KHÓA BOOTLOADER QUA FASTBOOT... <<<", "warning");

      if (terminalMinimized) {
        terminalMinimized = false;
        document.getElementById("terminalConsole").classList.remove("collapsed");
      }

      try {
        const res = await fetch("/api/fastboot/lock", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ confirmed: true })
        });
        const data = await res.json();
        if (data.success) {
          appendLog("✓ ĐÃ GỬI LỆNH THÀNH CÔNG!", "success");
          appendLog("  Vui lòng nhìn màn hình điện thoại, chọn 'Lock the bootloader' và bấm Nguồn để hoàn tất.", "info");
          alert("LỆNH ĐÃ ĐƯỢC GỬI!\n\nVui lòng nhìn màn hình điện thoại:\n1. Dùng phím Âm lượng để di chuyển vệt sáng đến 'Lock the bootloader'.\n2. Bấm phím Nguồn để xác nhận.\n3. Điện thoại sẽ tự Format Factory và khởi động lại với Bootloader đã khóa 100%!");
        } else {
          appendLog(`✕ Thất bại: ${data.message || data.output}`, "error");
          alert(`Không thể khóa: ${data.message || data.output}`);
        }
      } catch (err) {
        appendLog(`✕ Lỗi kết nối: ${err.message}`, "error");
      } finally {
        setTimeout(pollFastbootStatus, 3000);
      }
    });
  }
}
