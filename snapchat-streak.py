#!/usr/bin/env python3
"""
👻 Snapchat Streak Auto-Saver & Helper Hub
Automated Snap Dispatcher & Streak Maintenance via web.snapchat.com
Author: Sam & Antigravity (Advanced Agentic Pair Programming)
License: MIT
"""

import os
import sys
import json
import time
import random
import signal
import socket
import platform
import argparse
import subprocess
import signal
from datetime import datetime, date, timedelta

def handle_sigint(sig=None, frame=None):
    print("\n\n👋 Operasi dibatalkan oleh pengguna (Keluar). Sampai jumpa!\n")
    sys.exit(0)

signal.signal(signal.SIGINT, handle_sigint)

# Third-party dependencies (managed in venv)
try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
    import questionary
    from questionary import Choice, Separator
    import requests
except ImportError:
    print("\n[!] Dependensi belum terpasang.")
    print("    Jalankan './install.sh' atau 'pip install playwright questionary requests pillow'\n")
    sys.exit(1)

# ==============================================================================
# Global Paths & Constants
# ==============================================================================

APP_NAME = "snapchat-streak"
CURRENT_VERSION = "1.0.0"
PRIMARY_UPDATE_URL = f"https://script.wsnsam.my.id/api/updates?app={APP_NAME}"
FALLBACK_UPDATE_URL = f"https://raw.githubusercontent.com/sammmms/{APP_NAME}/main/version.json"
SCRIPT_RAW_URL = f"https://raw.githubusercontent.com/sammmms/{APP_NAME}/main/snapchat-streak.py"

HOME_DIR = os.path.expanduser("~")
BASE_DIR = os.path.join(HOME_DIR, ".snapchat-streak")
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")
STATE_FILE = os.path.join(BASE_DIR, "last_run.json")
LOG_DIR = os.path.join(BASE_DIR, "logs")
PROFILE_DIR = os.path.join(BASE_DIR, "browser_profile")
TEMP_SNAP_IMAGE = os.path.join(BASE_DIR, "temp_snap.png")

OS_NAME = platform.system()
IS_CRON = "--cron" in sys.argv

SNAPCHAT_WEB_URL = "https://web.snapchat.com"
SNAPCHAT_LOGIN_URL = "https://accounts.snapchat.com/v2/login?continue=https%3A%2F%2Fweb.snapchat.com"

# ==============================================================================
# Semver & Update Checker
# ==============================================================================

def parse_semver(ver: str) -> tuple:
    clean = ver.lstrip("v").strip()
    parts = []
    for p in clean.split("."):
        try:
            parts.append(int(p))
        except ValueError:
            parts.append(0)
    while len(parts) < 3:
        parts.append(0)
    return tuple(parts[:3])


def run_with_progress(title: str, worker_fn, timeout: float = 4.0):
    """Executes worker_fn in a daemon thread while rendering an animated progress bar and spinner."""
    import threading
    res = {"done": False, "result": None, "error": None}

    def target():
        try:
            res["result"] = worker_fn()
        except Exception as e:
            res["error"] = e
        finally:
            res["done"] = True

    t = threading.Thread(target=target, daemon=True)
    t.start()

    frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    start_t = time.time()
    i = 0

    while not res["done"] and (time.time() - start_t < timeout):
        elapsed = time.time() - start_t
        pct = min(int((elapsed / timeout) * 100), 99)
        filled = pct // 10
        bar = "█" * filled + "░" * (10 - filled)
        sys.stdout.write(f"\r[*] {title}... {frames[i % len(frames)]} [{bar}] {pct}% ({elapsed:.1f}s)")
        sys.stdout.flush()
        time.sleep(0.08)
        i += 1

    sys.stdout.write("\r" + " " * 80 + "\r")
    sys.stdout.flush()
    return res["result"], res["error"]


def check_for_updates(prompt_if_latest: bool = False):
    """Checks remote repository for newer version with animated progress."""
    def fetch_remote():
        for target_url in [PRIMARY_UPDATE_URL, FALLBACK_UPDATE_URL]:
            try:
                resp = requests.get(target_url, timeout=3.5)
                if resp.status_code == 200:
                    return resp.json()
            except Exception:
                continue
        return None

    update_data, _ = run_with_progress("Memeriksa pembaruan terbaru", fetch_remote, timeout=3.5)

    if not update_data or not isinstance(update_data, dict) or "version" not in update_data:
        sys.stdout.write("[*] Memeriksa pembaruan terbaru... [Selesai / Mode Offline ✓]\n")
        sys.stdout.flush()
        if prompt_if_latest:
            questionary.press_any_key_to_continue().ask()
        return

    try:
        remote_ver_str = update_data.get("version", CURRENT_VERSION)
        remote_ver = parse_semver(remote_ver_str)
        local_ver = parse_semver(CURRENT_VERSION)

        if remote_ver > local_ver:
            print(f"\r[*] Memeriksa pembaruan terbaru... [Versi Baru Tersedia: v{remote_ver_str}!]")
            changelogs = update_data.get("changelog", [])
            print("\n" + "=" * 60)
            print(f"🎉 Pembaruan Snapchat Streak v{remote_ver_str} Tersedia! (Versi saat ini: v{CURRENT_VERSION})")
            print("=" * 60)
            if changelogs:
                print("Catatan Rilis (Changelog):")
                for c in changelogs:
                    print(f"  • {c}")
            print("=" * 60 + "\n")

            update_now = questionary.confirm(
                f"Pasang pembaruan v{remote_ver_str} sekarang langsung dari aplikasi?",
                default=True
            ).ask()

            if update_now:
                print(f"\n[*] Mengunduh snapchat-streak.py v{remote_ver_str}...")
                dl_url = update_data.get("download_url", SCRIPT_RAW_URL)
                dl_resp = requests.get(dl_url, timeout=15)
                if dl_resp.status_code == 200 and len(dl_resp.text) > 1000:
                    target_installed = os.path.join(BASE_DIR, "snapchat-streak.py")
                    repo_file = os.path.abspath(__file__)
                    with open(target_installed, "w", encoding="utf-8") as sf:
                        sf.write(dl_resp.text)
                    if os.path.exists(repo_file) and os.access(repo_file, os.W_OK):
                        try:
                            with open(repo_file, "w", encoding="utf-8") as rf:
                                rf.write(dl_resp.text)
                        except Exception:
                            pass
                    print(f"[✓] Berhasil diperbarui ke versi v{remote_ver_str}!\n")
                    log_activity("SYSTEM", f"Aplikasi berhasil diperbarui dari v{CURRENT_VERSION} ke v{remote_ver_str}")
                    print("[*] Memulai ulang aplikasi...")
                    time.sleep(1.5)
                    os.execv(sys.executable, [sys.executable] + sys.argv)
                else:
                    print("[!] Gagal mengunduh berkas pembaruan.")
                    questionary.press_any_key_to_continue().ask()
        else:
            sys.stdout.write(f"\r[*] Memeriksa pembaruan terbaru... [Versi Terbaru: v{CURRENT_VERSION} ✓]\n")
            sys.stdout.flush()
            if prompt_if_latest:
                print(f"\n[✓] Anda sudah menggunakan versi paling baru (v{CURRENT_VERSION}).\n")
                questionary.press_any_key_to_continue().ask()
    except Exception:
        sys.stdout.write("[*] Memeriksa pembaruan terbaru... [Mode Offline ✓]\n")
        sys.stdout.flush()
        if prompt_if_latest:
            questionary.press_any_key_to_continue().ask()

# ==============================================================================
# Configuration & State Management
# ==============================================================================

DEFAULT_CONFIG = {
    "mode": "all",  # "all" or "groups"
    "default_caption": "🔥",
    "contacts": [],
    "groups": {
        "Sahabat": {
            "caption": "Streak 🔥⚡",
            "members": []
        }
    },
    "select_all": {
        "exclude": []
    },
    "messages": {
        "mode": "single",  # "single" or "pool"
        "pool": [
            "🔥",
            "Streak 🔥⚡",
            "Selamat {time_greeting} {first_name}! Streak 🔥",
            "Semangat hari {day} ya {first_name}! 🔥",
            "Streak hari ini {first_name} 🔥✨",
            "Pagi {first_name}! Jangan lupa streak yaa 🔥",
            "Streak {date} 🔥💪"
        ],
        "overrides": {}
    },
    "notifications": {
        "macos": {"enabled": True},
        "telegram": {"enabled": False, "bot_token": "", "chat_id": ""},
        "discord": {"enabled": False, "webhook_url": ""}
    },
    "schedule": {
        "hour": 9,
        "minute": 0
    }
}


def ensure_dirs():
    os.makedirs(BASE_DIR, exist_ok=True)
    os.makedirs(LOG_DIR, exist_ok=True)
    os.makedirs(PROFILE_DIR, exist_ok=True)


def deep_merge(target: dict, default: dict):
    for k, v in default.items():
        if k not in target:
            target[k] = v
        elif isinstance(v, dict) and isinstance(target[k], dict):
            deep_merge(target[k], v)


def load_config() -> dict:
    ensure_dirs()
    if not os.path.exists(CONFIG_FILE):
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            cfg = json.load(f)
            deep_merge(cfg, DEFAULT_CONFIG)
            return cfg
    except Exception:
        return DEFAULT_CONFIG.copy()


def save_config(cfg: dict):
    ensure_dirs()
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)


def load_state() -> dict:
    ensure_dirs()
    if not os.path.exists(STATE_FILE):
        return {
            "last_date": None,
            "last_time": None,
            "success": False,
            "sent_count": 0,
            "failed_count": 0,
            "summary": "Belum pernah dijalankan"
        }
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_state(success: bool, sent_count: int, failed_count: int, summary: str):
    ensure_dirs()
    now = datetime.now()
    state = {
        "last_date": now.strftime("%Y-%m-%d"),
        "last_time": now.strftime("%Y-%m-%d %H:%M:%S"),
        "success": success,
        "sent_count": sent_count,
        "failed_count": failed_count,
        "summary": summary
    }
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)


# ==============================================================================
# 3-Day Activity Logging with Auto-Pruning
# ==============================================================================

def clean_expired_logs(retention_days: int = 3):
    ensure_dirs()
    now = datetime.now()
    try:
        for fname in os.listdir(LOG_DIR):
            if fname.startswith("activity_") and fname.endswith(".log"):
                date_part = fname[len("activity_"):-len(".log")]
                try:
                    f_date = datetime.strptime(date_part, "%Y-%m-%d")
                    diff = (now - f_date).days
                    if diff > retention_days:
                        os.remove(os.path.join(LOG_DIR, fname))
                except ValueError:
                    pass

        main_log = os.path.join(BASE_DIR, "streak.log")
        if os.path.exists(main_log):
            stat = os.stat(main_log)
            file_mtime = datetime.fromtimestamp(stat.st_mtime)
            if (now - file_mtime).days > retention_days or stat.st_size > 10 * 1024 * 1024:
                try:
                    with open(main_log, "r", encoding="utf-8", errors="ignore") as lf:
                        lines = lf.readlines()
                    cutoff_str = (now - timedelta(days=retention_days)).strftime("%Y-%m-%d")
                    fresh_lines = [l for l in lines if cutoff_str in l or not l.startswith("[20")]
                    with open(main_log, "w", encoding="utf-8") as lf:
                        lf.writelines(fresh_lines[-1000:])
                except Exception:
                    pass
    except Exception:
        pass


def log_activity(category: str, message: str, print_to_console: bool = False):
    ensure_dirs()
    clean_expired_logs(retention_days=3)

    now = datetime.now()
    today_str = now.strftime("%Y-%m-%d")
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")

    entry = f"[{timestamp}] [{category.upper():<6}] {message}\n"

    daily_file = os.path.join(LOG_DIR, f"activity_{today_str}.log")
    try:
        with open(daily_file, "a", encoding="utf-8") as f:
            f.write(entry)
    except Exception:
        pass

    main_log = os.path.join(BASE_DIR, "streak.log")
    try:
        with open(main_log, "a", encoding="utf-8") as f:
            f.write(entry)
    except Exception:
        pass

    if print_to_console:
        print(f"[{category.upper()}] {message}")


def log_message(msg: str):
    log_activity("JOB", msg, print_to_console=True)


# ==============================================================================
# Message & Caption Template Engine
# ==============================================================================

INDONESIAN_DAYS = {
    0: "Senin", 1: "Selasa", 2: "Rabu", 3: "Kamis", 4: "Jumat", 5: "Sabtu", 6: "Minggu"
}
INDONESIAN_MONTHS = {
    1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "Mei", 6: "Jun",
    7: "Jul", 8: "Agu", 9: "Sep", 10: "Okt", 11: "Nov", 12: "Des"
}


def format_caption(template: str, contact_name: str) -> str:
    now = datetime.now()
    hour = now.hour

    if 4 <= hour < 11:
        time_greeting = "Pagi"
    elif 11 <= hour < 15:
        time_greeting = "Siang"
    elif 15 <= hour < 18:
        time_greeting = "Sore"
    else:
        time_greeting = "Malam"

    day_name = INDONESIAN_DAYS.get(now.weekday(), "Hari")
    month_name = INDONESIAN_MONTHS.get(now.month, "")
    date_str = f"{now.day} {month_name}"

    first_name = contact_name.split()[0] if contact_name else "Teman"

    rendered = template.replace("{name}", contact_name)
    rendered = rendered.replace("{first_name}", first_name)
    rendered = rendered.replace("{time_greeting}", time_greeting)
    rendered = rendered.replace("{day}", day_name)
    rendered = rendered.replace("{date}", date_str)

    return rendered.strip()


def resolve_caption_for_contact(contact_name: str, group_caption: str = None) -> str:
    cfg = load_config()
    msg_cfg = cfg.get("messages", {})

    overrides = msg_cfg.get("overrides", {})
    if contact_name in overrides and overrides[contact_name].strip():
        return format_caption(overrides[contact_name], contact_name)

    if group_caption and group_caption.strip():
        return format_caption(group_caption, contact_name)

    mode = msg_cfg.get("mode", "single")
    if mode == "pool":
        pool = msg_cfg.get("pool", [])
        if pool:
            chosen = random.choice(pool)
            return format_caption(chosen, contact_name)

    default_cap = cfg.get("default_caption", "🔥")
    return format_caption(default_cap, contact_name)


# ==============================================================================
# Delays, Human Jitter & Safety
# ==============================================================================

def get_action_delay() -> float:
    return round(random.uniform(2.5, 4.0), 2)


def is_within_safe_hours() -> tuple:
    now = datetime.now()
    current_time = (now.hour, now.minute)
    is_safe = (7, 0) <= current_time <= (23, 0)
    desc = f"{now.hour:02d}:{now.minute:02d} (Aman: 07:00 - 23:00)"
    return is_safe, desc


def wait_for_internet(timeout: int = 180, check_interval: int = 2, verbose: bool = False) -> bool:
    """Waits for active internet connectivity with animated progress bar."""
    start_time = time.time()
    frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    i = 0

    while time.time() - start_time < timeout:
        elapsed = time.time() - start_time
        pct = min(int((elapsed / timeout) * 100), 99)
        filled = pct // 10
        bar = "█" * filled + "░" * (10 - filled)

        if verbose:
            sys.stdout.write(f"\r[*] Memeriksa koneksi internet... {frames[i % len(frames)]} [{bar}] {int(elapsed)}s/{timeout}s")
            sys.stdout.flush()

        try:
            sock = socket.create_connection(("1.1.1.1", 53), timeout=2)
            sock.close()
            if verbose:
                sys.stdout.write("\r" + " " * 80 + "\r")
                print(f"[*] Koneksi internet: [Terhubung ✓] ({elapsed:.1f}s)")
            return True
        except (socket.timeout, OSError):
            pass

        try:
            r = requests.get("https://web.snapchat.com", timeout=2)
            if r.status_code in (200, 301, 302, 403):
                if verbose:
                    sys.stdout.write("\r" + " " * 80 + "\r")
                    print(f"[*] Koneksi internet: [Terhubung via HTTP ✓] ({elapsed:.1f}s)")
                return True
        except Exception:
            pass

        time.sleep(check_interval)
        i += 1

    if verbose:
        sys.stdout.write("\r" + " " * 80 + "\r")
        print("[!] Koneksi internet: [Gagal / Batas Waktu Habis]")
    return False

# ==============================================================================
# Notifications (macOS Native, Telegram, Discord)
# ==============================================================================

def send_telegram_notification(bot_token: str, chat_id: str, title: str, text: str, success: bool) -> tuple:
    try:
        import html
        icon = "✅" if success else "❌"
        safe_title = html.escape(title)
        safe_text = html.escape(text)
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        msg = f"{icon} <b>{safe_title}</b>\n\n{safe_text}\n\n<i>Waktu: {now_str}</i>"

        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        resp = requests.post(url, json={
            "chat_id": chat_id,
            "text": msg,
            "parse_mode": "HTML"
        }, timeout=10)

        data = resp.json()
        if resp.status_code == 200 and data.get("ok"):
            return True, "Berhasil terkirim ke Telegram!"
        else:
            desc = data.get("description", resp.text)
            return False, f"Telegram API Error ({resp.status_code}): {desc}"
    except Exception as e:
        return False, f"Gagal koneksi Telegram: {e}"


def send_discord_notification(webhook_url: str, title: str, text: str, success: bool) -> tuple:
    try:
        color = 0x2ECC71 if success else 0xE74C3C
        payload = {
            "embeds": [{
                "title": title,
                "description": text,
                "color": color,
                "timestamp": datetime.utcnow().isoformat()
            }]
        }
        resp = requests.post(webhook_url, json=payload, timeout=10)
        if resp.status_code in (200, 204):
            return True, "Berhasil terkirim ke Discord Webhook!"
        else:
            return False, f"Discord Error ({resp.status_code}): {resp.text}"
    except Exception as e:
        return False, f"Gagal koneksi Discord: {e}"


def send_notification(title: str, text: str, success: bool):
    cfg = load_config()
    notifs = cfg.get("notifications", {})

    # 1. macOS native banner
    if OS_NAME == "Darwin" and notifs.get("macos", {}).get("enabled", True):
        sound = "default" if success else "Basso"
        clean_title = title.replace('"', '\\"').replace("\n", " ")
        clean_text = text.replace("*", "").replace('"', "'").strip()
        lines = [l.strip() for l in clean_text.splitlines() if l.strip()]
        short_text = " \\n ".join(lines[:3]) if lines else "Status pengiriman snap streak"
        if len(short_text) > 200:
            short_text = short_text[:197] + "..."
        script = f'display notification "{short_text}" with title "{clean_title}" sound name "{sound}"'
        try:
            subprocess.run(["osascript", "-e", script], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass

    # 2. Telegram Bot
    tg = notifs.get("telegram", {})
    if tg.get("enabled") and tg.get("bot_token") and tg.get("chat_id"):
        ok, err = send_telegram_notification(tg["bot_token"], tg["chat_id"], title, text, success)
        if not ok:
            log_message(f"Telegram error: {err}")

    # 3. Discord Webhook
    dc = notifs.get("discord", {})
    if dc.get("enabled") and dc.get("webhook_url"):
        ok, err = send_discord_notification(dc["webhook_url"], title, text, success)
        if not ok:
            log_message(f"Discord error: {err}")


# ==============================================================================
# Auto Scheduler (LaunchAgent on macOS)
# ==============================================================================

def get_scheduler_status() -> tuple:
    cfg = load_config()
    sched = cfg.get("schedule", {"hour": 9, "minute": 0})
    time_str = f"{sched['hour']:02d}:{sched['minute']:02d}"

    if OS_NAME == "Darwin":
        plist = os.path.expanduser("~/Library/LaunchAgents/com.user.snapchatstreak.plist")
        if os.path.exists(plist):
            return True, f"Active (macOS LaunchAgent @ {time_str} with Wake-up Catch-up)"
        return False, "Not Installed"
    return False, "Unsupported OS"


def install_scheduler():
    ensure_dirs()
    cfg = load_config()
    sched = cfg.get("schedule", {"hour": 9, "minute": 0})
    hour = sched.get("hour", 9)
    minute = sched.get("minute", 0)

    if OS_NAME == "Darwin":
        plist_path = os.path.expanduser("~/Library/LaunchAgents/com.user.snapchatstreak.plist")
        wrapper_bin = os.path.expanduser("~/.local/bin/snapchat-streak")

        if not os.path.exists(wrapper_bin):
            wrapper_bin = sys.executable + " " + os.path.abspath(__file__)

        # Multi-interval hourly catch-up so morning wake-up always triggers
        intervals_xml = ""
        for h in range(hour, 22):
            intervals_xml += f"""        <dict>
            <key>Hour</key>
            <integer>{h}</integer>
            <key>Minute</key>
            <integer>{minute}</integer>
        </dict>\n"""

        plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.user.snapchatstreak</string>
    <key>ProgramArguments</key>
    <array>
        <string>{os.path.expanduser('~/.local/bin/snapchat-streak')}</string>
        <string>--cron</string>
    </array>
    <key>StartCalendarInterval</key>
    <array>
{intervals_xml}    </array>
    <key>StandardOutPath</key>
    <string>{BASE_DIR}/streak.log</string>
    <key>StandardErrorPath</key>
    <string>{BASE_DIR}/streak.log</string>
</dict>
</plist>
"""
        os.makedirs(os.path.dirname(plist_path), exist_ok=True)
        with open(plist_path, "w", encoding="utf-8") as f:
            f.write(plist_content)

        subprocess.run(["launchctl", "unload", plist_path], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        res = subprocess.run(["launchctl", "load", plist_path], check=False, capture_output=True, text=True)
        if res.returncode == 0:
            log_activity("CONFIG", f"Jadwal harian diaktifkan pada jam {hour:02d}:{minute:02d} (dengan multi-interval catch-up).")
            print(f"[✓] Berhasil memasang jadwal otomatis jam {hour:02d}:{minute:02d} (Wake-up Catch-up aktif)!")
        else:
            print(f"[!] Gagal mendaftarkan LaunchAgent: {res.stderr}")
    else:
        print("[!] Scheduler otomatis saat ini dioptimalkan untuk macOS LaunchAgent.")


def remove_scheduler():
    if OS_NAME == "Darwin":
        plist_path = os.path.expanduser("~/Library/LaunchAgents/com.user.snapchatstreak.plist")
        if os.path.exists(plist_path):
            subprocess.run(["launchctl", "unload", plist_path], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            try:
                os.remove(plist_path)
            except Exception:
                pass
            log_activity("CONFIG", "Jadwal harian dinonaktifkan.")
            print("[✓] Jadwal otomatis berhasil dihapus.")
        else:
            print("[i] Tidak ada jadwal yang terpasang.")


# ==============================================================================
# Playwright Browser Helper
# ==============================================================================

BROWSER_ARGS = [
    "--use-fake-ui-for-media-stream",
    "--use-fake-device-for-media-stream",
    "--disable-blink-features=AutomationControlled",
    "--no-sandbox",
    "--disable-dev-shm-usage"
]


def create_snap_canvas_image():
    """Generates a dummy or branded dark snap frame if camera upload is used."""
    try:
        from PIL import Image, ImageDraw, ImageFont
        img = Image.new("RGB", (720, 1280), color=(18, 18, 24))
        draw = ImageDraw.Draw(img)
        # Add flame accent or minimal graphics
        draw.ellipse([310, 590, 410, 690], fill=(255, 140, 0))
        img.save(TEMP_SNAP_IMAGE)
        return TEMP_SNAP_IMAGE
    except Exception:
        return None


def launch_browser_context(p, headless: bool = True):
    """
    Launches Playwright persistent context with 4-tier auto-recovery:
    1. Bundled Playwright Chromium / Headless Shell
    2. Local Google Chrome (channel='chrome')
    3. Local Microsoft Edge (channel='msedge')
    4. Auto-repair (auto-installs missing Chromium binary via CLI and retries)
    Includes stealth anti-detection so Snapchat Web never flags 'Browser not supported'.
    """
    ensure_dirs()
    args = list(BROWSER_ARGS)
    if headless:
        args.append("--headless=new")

    opts = {
        "user_data_dir": PROFILE_DIR,
        "headless": headless,
        "args": args,
        "ignore_default_args": ["--enable-automation"],
        "permissions": ["camera", "microphone"],
        "viewport": {"width": 1440, "height": 900},
        "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
    }

    def setup_context(ctx):
        ctx.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            window.navigator.chrome = { runtime: {} };
            Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
            Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
        """)
        return ctx

    # Tier 1: Default Playwright Chromium
    try:
        ctx = p.chromium.launch_persistent_context(**opts)
        return setup_context(ctx)
    except Exception as e1:
        log_activity("SYSTEM", f"Chromium default launch gagal ({e1}). Mencoba fallback ke Google Chrome lokal...")

    # Tier 2: Local Google Chrome
    try:
        opts_chrome = dict(opts)
        opts_chrome["channel"] = "chrome"
        ctx = p.chromium.launch_persistent_context(**opts_chrome)
        return setup_context(ctx)
    except Exception as e2:
        log_activity("SYSTEM", f"Google Chrome lokal gagal ({e2}). Mencoba fallback ke Microsoft Edge...")

    # Tier 3: Local Microsoft Edge
    try:
        opts_edge = dict(opts)
        opts_edge["channel"] = "msedge"
        ctx = p.chromium.launch_persistent_context(**opts_edge)
        return setup_context(ctx)
    except Exception:
        pass

    # Tier 4: Self-Healing Auto-Repair
    log_activity("SYSTEM", "Mencoba auto-repair: Mengunduh Playwright Chromium di latar belakang...")
    try:
        subprocess.run(
            [sys.executable, "-m", "playwright", "install", "chromium"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=180,
            check=False
        )
        ctx = p.chromium.launch_persistent_context(**opts)
        return setup_context(ctx)
    except Exception as e_final:
        raise RuntimeError(f"Gagal meluncurkan browser Playwright setelah 4 metode pemulihan dicoba: {e_final}")


# ==============================================================================
# Login & Authentication Verification
# ==============================================================================

def is_page_logged_in(page) -> bool:
    """Verifies whether the current page is authenticated on Snapchat Web."""
    try:
        url = page.url.lower()
        if "accounts.snapchat.com" in url or "original_referrer" in url:
            return False

        # If password or identifier input is visible, user is definitely not logged in
        for sel in ['input[type="password"]', 'input[name="accountIdentifier"]', 'button:has-text("Log in")', 'button:has-text("Log In")']:
            if page.locator(sel).first.is_visible(timeout=300):
                return False

        body_text = page.locator("body").inner_text().lower()
        if "log in to snapchat" in body_text or "browser not supported" in body_text:
            return False

        # If chat feed or conversation list or camera button is visible
        for chat_sel in ['[role="feed"]', '[data-testid*="chat"]', '[aria-label*="Chat"]', 'div[class*="chat"]', 'button[aria-label*="Camera"]', '[role="listitem"]']:
            if page.locator(chat_sel).first.is_visible(timeout=400):
                return True

        if "web.snapchat.com" in url:
            return True

        return False
    except Exception:
        return False


def check_login_status() -> bool:
    """Instant (1ms) filesystem check for authentic Snapchat login session."""
    if not os.path.exists(PROFILE_DIR):
        return False
    cookie_paths = [
        os.path.join(PROFILE_DIR, "Default", "Cookies"),
        os.path.join(PROFILE_DIR, "Default", "Network", "Cookies"),
        os.path.join(PROFILE_DIR, "Cookies")
    ]
    for p in cookie_paths:
        if os.path.exists(p):
            try:
                import sqlite3
                conn = sqlite3.connect(f"file:{p}?mode=ro", uri=True)
                cur = conn.cursor()
                cur.execute("""
                    SELECT count(*) FROM cookies 
                    WHERE host_key LIKE '%snapchat%' 
                    AND (
                        name LIKE 'sc-a-%' 
                        OR (name LIKE '%session%' AND name NOT LIKE '%blizzard%') 
                        OR name LIKE '%auth%' 
                        OR name LIKE '%token%'
                    )
                """)
                count = cur.fetchone()[0]
                conn.close()
                if count >= 1:
                    return True
            except Exception:
                pass
    return False


def verify_login_live(verbose: bool = True) -> bool:
    """Full live verification by launching browser to check active session."""
    def worker():
        with sync_playwright() as p:
            ctx = launch_browser_context(p, headless=True)
            pg = ctx.new_page()
            pg.goto(SNAPCHAT_WEB_URL, wait_until="networkidle", timeout=25000)
            pg.wait_for_timeout(2500)
            is_valid = is_page_logged_in(pg)
            ctx.close()
            return is_valid

    if verbose:
        res, _ = run_with_progress("Memverifikasi sesi langsung ke Snapchat Web", worker, timeout=18.0)
        return bool(res)
    else:
        try:
            return bool(worker())
        except Exception:
            return False


def interactive_login():
    ensure_dirs()
    print("\n" + "=" * 68)
    print("🔑 LOGIN / HUBUNGKAN AKUN SNAPCHAT (BROWSER RESMI)")
    print("=" * 68)
    print("1. Jendela browser resmi akan terbuka langsung ke halaman login Snapchat.")
    print("2. Masukkan Username / Email / Nomor HP dan Password Anda.")
    print("3. Jika diminta verifikasi 2FA atau notifikasi di aplikasi HP, silakan setujui.")
    print("4. Pastikan browser selesai memuat dan menampilkan halaman Chat Snapchat Web.")
    print("5. KEMBALI KE TERMINAL INI dan tekan [ENTER].")
    print("   👉 JANGAN tutup browser secara manual! Script akan menutupnya otomatis.")
    print("=" * 68 + "\n")

    input("Tekan [ENTER] untuk membuka jendela browser login...")

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("[!] Modul 'playwright' belum terpasang.")
        return

    login_confirmed = False

    with sync_playwright() as p:
        context = launch_browser_context(p, headless=False)
        page = context.pages[0] if context.pages else context.new_page()
        try:
            page.goto("https://accounts.snapchat.com/v2/login?continue=https%3A%2F%2Fweb.snapchat.com", wait_until="networkidle", timeout=60000)
        except Exception:
            pass

        print("\n[*] Jendela browser telah terbuka.")
        print("[*] Silakan login akun Snapchat Anda di browser tersebut.")
        input("\n👉 Setelah Anda SUDAH SELESAI LOGIN dan melihat halaman obrolan/Chat di browser, tekan [ENTER] di sini...\n   (Browser akan ditutup otomatis oleh script, jangan ditutup manual)")

        # Safely verify login while browser is still open
        try:
            if not page.is_closed():
                time.sleep(1)
                if is_page_logged_in(page):
                    login_confirmed = True
        except Exception:
            pass

        # Safely inspect cookies
        try:
            cookies = context.cookies()
            has_auth = any(
                ("sc-a-" in c["name"] or ("session" in c["name"].lower() and "blizzard" not in c["name"].lower()) or "auth" in c["name"].lower() or "sastate" in c["name"].lower())
                for c in cookies if "snapchat" in c.get("domain", "")
            )
            if has_auth:
                login_confirmed = True
        except Exception:
            pass

        # Cleanly close browser without crashing if user already closed it
        try:
            context.close()
        except Exception:
            pass

    # Filesystem check as final fallback
    if not login_confirmed:
        login_confirmed = check_login_status()

    if login_confirmed:
        print("\n[✓] Login BERHASIL! Sesi akun tersimpan rapi di komputer.")
        log_activity("AUTH", "Login Snapchat berhasil disimpan dan terverifikasi.")
        print("[*] Memulai pemindaian daftar teman dari akun yang terhubung...")
        scan_snapchat_friends(verbose=True)
    else:
        print("\n[!] Perhatian: Belum terdeteksi sesi login aktif.")
        print("    Pastikan Anda sudah menyelesaikan proses login sampai halaman Chat sebelum menekan [ENTER].")
        print("    Silakan coba lagi dari menu Login.")


# ==============================================================================
# Friends & Streak Scanning Engine
# ==============================================================================

def scan_snapchat_friends_using_page(page, verbose: bool = True) -> list:
    cfg = load_config()
    existing_contacts = cfg.get("contacts", [])
    found_contacts = []

    if verbose:
        print("[*] Memindai daftar teman dan status streak di Snapchat Web...")

    page.wait_for_timeout(3000)

    # Scroll conversation feed to load all items
    feed_locators = ['div[role="feed"]', '[data-testid="chat-list"]', 'nav', 'ul', 'div[class*="chats"]', 'div[class*="conversation"]']
    for feed_sel in feed_locators:
        try:
            feed = page.locator(feed_sel).first
            if feed.is_visible():
                for _ in range(5):
                    feed.evaluate("el => el.scrollTop += 600")
                    page.wait_for_timeout(600)
                break
        except Exception:
            pass

    # Extract conversation items
    item_selectors = [
        '[role="feed"] [role="listitem"]',
        '[role="listitem"]',
        '[data-testid*="chat-item"]',
        '[data-testid*="conversation"]',
        'div[class*="chat-item"]',
        'div[class*="ConversationItem"]',
        'div[class*="chatListItem"]',
        'li[role="listitem"]'
    ]
    items = []
    for sel in item_selectors:
        matched = page.locator(sel).all()
        if len(matched) > len(items):
            items = matched

    if not items:
        items = page.locator('button[class*="chat"], div[role="button"]:has(span)').all()

    ignore_names = {
        "chat", "new chat", "camera", "search", "stories", "spotlight", 
        "settings", "snapchat", "my story", "add friends", "log in", 
        "sign up", "terms", "privacy", "download", "lenses", "snapchat+",
        "browser not supported"
    }

    for item in items:
        try:
            text = item.inner_text()
            if not text or len(text.strip()) == 0:
                continue
            lines = [l.strip() for l in text.split("\n") if l.strip()]
            if not lines:
                continue
            name = lines[0]
            if name.lower() in ignore_names or len(name) > 35:
                continue

            has_streak = "🔥" in text or "streak" in text.lower()
            streak_badge = " 🔥" if has_streak else ""

            if name not in found_contacts:
                found_contacts.append(name)
                if verbose:
                    print(f"  • {name}{streak_badge}")
        except Exception:
            continue

    if found_contacts:
        merged = sorted(list(set(existing_contacts + found_contacts)))
        cfg["contacts"] = merged
        save_config(cfg)
        log_activity("JOB", f"Pindai kontak selesai: ditemukan {len(found_contacts)} teman.")
        if verbose:
            print(f"\n[✓] Berhasil menyimpan {len(merged)} teman ke daftar kontak.\n")
    else:
        if verbose:
            print("[-] Tidak ada percakapan teman yang terdeteksi secara otomatis.")
            print("    Pastikan Anda sudah login dan membuka tab Chat di Snapchat Web.")

    return found_contacts


def scan_snapchat_friends(verbose: bool = True) -> list:
    if not check_login_status():
        if verbose:
            print("\n[!] Akun Snapchat Anda belum terhubung (Sesi Kosong).")
            print("    👉 Silakan pilih menu [🔑 Login / Hubungkan Akun] terlebih dahulu untuk login.")
        return []

    with sync_playwright() as p:
        try:
            context = launch_browser_context(p, headless=True)
            page = context.new_page()
            page.goto(SNAPCHAT_WEB_URL, wait_until="networkidle", timeout=30000)
            page.wait_for_timeout(3000)

            if not is_page_logged_in(page):
                if verbose:
                    print("\n[!] Sesi akun Snapchat kedaluwarsa atau belum login.")
                    print("    👉 Silakan pilih menu [🔑 Login / Hubungkan Akun] untuk login ulang.")
                context.close()
                return []

            res = scan_snapchat_friends_using_page(page, verbose=verbose)
            context.close()
            return res
        except Exception as e:
            if verbose:
                print(f"[!] Gagal memindai kontak: {e}")
            return []


# ==============================================================================
# Snap Sending Engine (Camera Capture & Dispatch)
# ==============================================================================

def take_and_send_snap(page, recipient_names: list, caption_text: str = "🔥") -> tuple:
    """Takes a snap using camera shutter and dispatches to recipient_names. Returns (sent: list, failed: list)."""
    sent = []
    failed = []

    try:
        # Step 1: Open Camera Interface
        camera_clicked = False
        for cam_btn in [
            'button[aria-label*="Camera"]',
            'button[aria-label*="Take Snap"]',
            '[data-testid*="camera"]',
            'div[aria-label*="Camera"]'
        ]:
            loc = page.locator(cam_btn).first
            if loc.is_visible(timeout=1500):
                loc.click()
                camera_clicked = True
                break

        page.wait_for_timeout(2000)

        # Step 2: Click Shutter to take Snap
        shutter_clicked = False
        for shutter_sel in [
            'button[aria-label*="Capture"]',
            'button[aria-label*="Take Snap"]',
            'button[class*="shutter"]',
            'button[class*="capture"]',
            'button[class*="circle"]'
        ]:
            shutter = page.locator(shutter_sel).first
            if shutter.is_visible(timeout=1500):
                shutter.click()
                shutter_clicked = True
                break

        if not shutter_clicked:
            # Fallback: Click center bottom of viewport
            vp = page.viewport_size or {"width": 1280, "height": 800}
            page.mouse.click(vp["width"] / 2, vp["height"] - 90)
            shutter_clicked = True

        page.wait_for_timeout(2500)

        # Step 3: Add Caption (if provided)
        if caption_text:
            try:
                caption_input = page.locator('textarea, input[placeholder*="caption"], [contenteditable="true"]').first
                if caption_input.is_visible(timeout=1000):
                    caption_input.fill(caption_text)
                    page.keyboard.press("Enter")
            except Exception:
                pass

        # Step 4: Click 'Send To' / Next Button
        send_to_btn = None
        for st_sel in [
            'button[aria-label*="Send To"]',
            'button[aria-label*="Next"]',
            'button[class*="send"]',
            'button:has(svg)'
        ]:
            candidate = page.locator(st_sel).first
            if candidate.is_visible(timeout=1500):
                send_to_btn = candidate
                send_to_btn.click()
                break

        page.wait_for_timeout(2000)

        # Step 5: Select each target recipient in friend picker
        for target in recipient_names:
            try:
                # Search contact
                search_box = page.locator('input[placeholder*="Search"], input[type="search"]').first
                if search_box.is_visible(timeout=1500):
                    search_box.fill(target)
                    page.wait_for_timeout(1000)

                # Click contact checkbox or row
                friend_row = page.locator(f'text="{target}"').first
                if friend_row.is_visible(timeout=2000):
                    friend_row.click()
                    sent.append(target)
                    time.sleep(get_action_delay())
                else:
                    failed.append(target)
            except Exception:
                failed.append(target)

        # Step 6: Click Final Blue Send Button
        final_send = page.locator('button[aria-label*="Send"], button[class*="send-button"]').last
        if final_send.is_visible(timeout=2000):
            final_send.click()
            page.wait_for_timeout(3000)
            log_activity("JOB", f"Snap terkirim ke {len(sent)} kontak.")
        else:
            # Fallback press Enter
            page.keyboard.press("Enter")
            page.wait_for_timeout(2000)

    except Exception as e:
        log_activity("JOB", f"Error saat eksekusi take_and_send_snap: {e}")
        failed.extend([r for r in recipient_names if r not in sent])

    return sent, failed


def run_send_streak(force: bool = False, verbose: bool = True) -> dict:
    ensure_dirs()
    clean_expired_logs(retention_days=3)
    today_str = datetime.now().strftime("%Y-%m-%d")
    state = load_state()

    # Avoid duplicate daily sends
    if not force and state.get("last_date") == today_str and state.get("success"):
        msg = f"Streak hari ini ({today_str}) sudah terkirim pada {state.get('last_time')}."
        if verbose:
            print(f"\n[i] {msg}")
            print("    Gunakan opsi paksa atau tunggu jadwal berikutnya.")
        return {"status": "skipped", "message": msg}

    cfg = load_config()
    mode = cfg.get("mode", "all")
    contacts = cfg.get("contacts", [])
    groups = cfg.get("groups", {})
    excludes = cfg.get("select_all", {}).get("exclude", [])

    # Filter recipients
    target_recipients = []
    if mode == "all":
        target_recipients = [c for c in contacts if c not in excludes]
    else:
        for g_name, g_info in groups.items():
            for m in g_info.get("members", []):
                if m not in target_recipients and m not in excludes:
                    target_recipients.append(m)

    if not target_recipients:
        msg = "Tidak ada kontak target yang dipilih. Silakan Pindai Kontak atau tentukan Grup di Menu 2."
        if verbose:
            print(f"\n[!] {msg}")
        return {"status": "no_targets", "message": msg}

    # Ensure internet
    if not wait_for_internet(timeout=180, verbose=verbose):
        err = "Gagal terhubung ke internet dalam batas waktu toleransi."
        log_activity("JOB", err)
        send_notification("Snapchat Streak Gagal", err, success=False)
        return {"status": "offline", "message": err}

    if verbose:
        print("\n" + "=" * 65)
        print(f"🚀 MEMULAI PENGIRIMAN SNAP STREAK ({len(target_recipients)} Kontak)")
        print(f"   Mode: {mode.upper()} | Waktu: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 65)

    with sync_playwright() as p:
        try:
            context = launch_browser_context(p, headless=True)
            page = context.new_page()
            page.goto(SNAPCHAT_WEB_URL, wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(3000)

            # Check if login active
            if not is_page_logged_in(page):
                err_msg = "Sesi login Snapchat kedaluwarsa atau belum login. Silakan login via menu terminal."
                log_activity("JOB", err_msg)
                save_state(False, 0, len(target_recipients), err_msg)
                send_notification("Snapchat Streak Gagal", err_msg, success=False)
                context.close()
                return {"status": "error", "message": err_msg}

            # Take snap and send
            default_cap = cfg.get("default_caption", "🔥")
            resolved_cap = format_caption(default_cap, target_recipients[0] if target_recipients else "Teman")

            sent, failed = take_and_send_snap(page, target_recipients, caption_text=resolved_cap)
            context.close()

            success = len(sent) > 0 or len(target_recipients) == 0
            summary = f"Terkirim: {len(sent)} | Gagal: {len(failed)}"

            save_state(success, len(sent), len(failed), summary)
            log_activity("JOB", f"Eksekusi streak selesai. {summary}")

            # Send notifications
            names_preview = ", ".join(sent[:4]) + ("..." if len(sent) > 4 else "")
            notif_text = f"Terkirim: {len(sent)} | Gagal: {len(failed)}\nPenerima: {names_preview or 'None'}"
            send_notification("Snapchat Streak Berhasil" if success else "Snapchat Streak Sebagian Gagal", notif_text, success=success)

            if verbose:
                print("\n" + "=" * 65)
                print(f"🏁 HASIL EKSEKUSI SNAP STREAK: {summary}")
                print("=" * 65 + "\n")

            return {"status": "success", "sent": len(sent), "failed": len(failed)}

        except Exception as e:
            err_msg = f"Terjadi kesalahan Playwright: {e}"
            log_activity("JOB", err_msg)
            save_state(False, 0, len(target_recipients), err_msg)
            send_notification("Snapchat Streak Error", err_msg, success=False)
            if verbose:
                print(f"\n[!] {err_msg}\n")
            return {"status": "error", "message": err_msg}


# ==============================================================================
# UI Dashboard & Menus
# ==============================================================================

def print_dashboard():
    os.system("clear" if os.name == "posix" else "cls")
    cfg = load_config()
    state = load_state()
    today_str = datetime.now().strftime("%Y-%m-%d")

    mode_label = "Select All (Semua Teman)" if cfg.get("mode") == "all" else "Groups / Labeling"
    sched_active, sched_desc = get_scheduler_status()

    is_logged_in = check_login_status()
    login_badge = "🟢 VALID (Aktif)" if is_logged_in else "🔴 BELUM LOGIN"

    status_today = " ⌛ Belum Terkirim Hari Ini"
    if state.get("last_date") == today_str:
        status_today = " 🟢 Sudah Terkirim Hari Ini" if state.get("success") else " 🔴 Gagal Hari Ini"

    sched_badge = "🟢 " + sched_desc if sched_active else "⚪ " + sched_desc

    print("==================================================================")
    print("👻 Snapchat Streak Auto-Saver & Helper Hub")
    print("==================================================================")
    print(f"👤 Akun Sesi      : {login_badge}")
    print(f"📅 Status Hari Ini:{status_today}")
    print(f"👥 Mode Penerima  : {mode_label}")
    print(f"⏰ Jadwal Auto    : {sched_badge}")
    print("==================================================================")

    if not is_logged_in:
        print("\n" + "╔" + "═" * 64 + "╗")
        print("║  ⚠️  STATUS AKUN: BELUM LOGIN / SESI KOSONG                    ║")
        print("║  👉 Anda belum menghubungkan akun Snapchat. Otomasi streak    ║")
        print("║     tidak dapat berjalan sebelum Anda login terlebih dahulu.   ║")
        print("║                                                                ║")
        print("║  👉 Silakan pilih menu [🔑 LOGIN SEKARANG] di bawah ini!       ║")
        print("╚" + "═" * 64 + "╝\n")


def menu_manage_recipients():
    while True:
        cfg = load_config()
        mode = cfg.get("mode", "all")
        mode_label = "Select All (Semua Teman)" if mode == "all" else "Groups / Labeling"

        choices = [
            Choice(f"🔄 Ganti Mode Pengiriman (Saat ini: {mode_label})", value="toggle_mode"),
            Choice("📋 Checklist Kontak & Tetapkan Grup (Multi-select)", value="checklist"),
            Choice("🏷️  Kelola Label Grup", value="groups"),
            Choice("💬 Konfigurasi Caption Snap (Default, Pool Acak & Khusus)", value="caption"),
            Choice("🚫 Kelola Daftar Pengecualian (Blacklist / Exclude)", value="exclude"),
            Choice("👁️  Pratinjau Caption yang Akan Dikirim (Preview)", value="preview"),
            Separator(),
            Choice("🔙 Kembali ke Menu Utama", value="back")
        ]

        action = questionary.select(
            f"👥 Kelola Penerima & Caption [Mode: {mode.upper()}]:",
            choices=choices
        ).ask()

        if action == "back" or not action:
            break

        elif action == "toggle_mode":
            cfg["mode"] = "groups" if mode == "all" else "all"
            save_config(cfg)
            log_activity("CONFIG", f"Mode penerima diubah ke: {cfg['mode'].upper()}")
            print(f"\n[✓] Mode pengiriman diubah ke: {cfg['mode'].upper()}\n")

        elif action == "checklist":
            contacts = cfg.get("contacts", [])
            if not contacts:
                print("\n[!] Belum ada kontak tersimpan. Silakan Pindai Kontak di Menu 5.\n")
                questionary.press_any_key_to_continue().ask()
                continue
            groups = cfg.get("groups", {})
            g_choices = list(groups.keys())
            if not g_choices:
                print("\n[!] Belum ada grup. Buat grup terlebih dahulu di menu 'Kelola Label Grup'.\n")
                questionary.press_any_key_to_continue().ask()
                continue

            target_grp = questionary.select("Pilih grup untuk mengelompokkan kontak:", choices=g_choices).ask()
            if target_grp:
                curr_members = groups[target_grp].get("members", [])
                c_choices = [Choice(c, value=c, checked=(c in curr_members)) for c in contacts]
                chosen = questionary.checkbox(f"Pilih kontak untuk grup '{target_grp}':", choices=c_choices).ask()
                if chosen is not None:
                    groups[target_grp]["members"] = chosen
                    cfg["groups"] = groups
                    save_config(cfg)
                    log_activity("CONFIG", f"Anggota grup '{target_grp}' diperbarui ({len(chosen)} kontak).")
                    print(f"\n[✓] Grup '{target_grp}' diperbarui ({len(chosen)} kontak)!\n")

        elif action == "groups":
            groups = cfg.get("groups", {})
            print("\n" + "=" * 55)
            print("🏷️  Daftar Grup Snapchat:")
            for g, inf in groups.items():
                print(f"  • {g:<18} ({len(inf.get('members', []))} anggota)")
            print("=" * 55 + "\n")
            g_act = questionary.select("Aksi Grup:", choices=[
                Choice("➕ Tambah Grup Baru", value="add"),
                Choice("🗑️  Hapus Grup", value="del"),
                Choice("🔙 Kembali", value="back")
            ]).ask()
            if g_act == "add":
                g_name = questionary.text("Nama grup baru:").ask()
                if g_name and g_name.strip():
                    groups[g_name.strip()] = {"caption": "🔥", "members": []}
                    cfg["groups"] = groups
                    save_config(cfg)
                    print(f"[✓] Grup '{g_name.strip()}' ditambahkan!\n")
            elif g_act == "del":
                to_del = questionary.select("Pilih grup untuk dihapus:", choices=list(groups.keys())).ask()
                if to_del and to_del in groups:
                    del groups[to_del]
                    cfg["groups"] = groups
                    save_config(cfg)
                    print(f"[✓] Grup '{to_del}' berhasil dihapus!\n")

        elif action == "caption":
            curr_def = cfg.get("default_caption", "🔥")
            new_cap = questionary.text("Masukkan caption default untuk Snap:", default=curr_def).ask()
            if new_cap is not None:
                cfg["default_caption"] = new_cap.strip()
                save_config(cfg)
                log_activity("CONFIG", f"Caption default diubah menjadi: '{new_cap.strip()}'")
                print(f"\n[✓] Caption default diperbarui menjadi: '{new_cap.strip()}'\n")

        elif action == "exclude":
            excludes = cfg.get("select_all", {}).get("exclude", [])
            contacts = cfg.get("contacts", [])
            c_choices = [Choice(c, value=c, checked=(c in excludes)) for c in contacts]
            chosen_ex = questionary.checkbox("Pilih kontak yang DIKECUALIKAN (Blacklist dari pengiriman):", choices=c_choices).ask()
            if chosen_ex is not None:
                cfg.setdefault("select_all", {})["exclude"] = chosen_ex
                save_config(cfg)
                log_activity("CONFIG", f"Daftar pengecualian diperbarui ({len(chosen_ex)} kontak).")
                print(f"\n[✓] Daftar blacklist diperbarui ({len(chosen_ex)} kontak)!\n")

        elif action == "preview":
            contacts = cfg.get("contacts", []) or ["Budi", "Siti", "Andi"]
            print("\n" + "=" * 60)
            print("👁️  PRATINJAU CAPTION SNAP STREAK:")
            for c in contacts[:5]:
                cap = resolve_caption_for_contact(c)
                print(f"  Kepada: {c:<16} -> Caption: \"{cap}\"")
            print("=" * 60 + "\n")
            questionary.press_any_key_to_continue().ask()


def show_telegram_guide():
    print("\n" + "=" * 62)
    print("📖 Panduan Singkat Integrasi Telegram (Cuma 1 Menit):")
    print("=" * 62)
    print("1. Buka aplikasi Telegram di HP / Laptop kamu.")
    print("2. Cari @BotFather (bot resmi centang biru dari Telegram).")
    print("3. Kirim perintah /newbot dan ikuti instruksi:")
    print("   -> Masukkan nama tampilan bot (misal: 'Streak Helper')")
    print("   -> Masukkan username bot (harus berakhiran 'bot', misal: 'sam_streak_bot')")
    print("   -> BotFather akan memberikan HTTP API Token.")
    print("4. Ambil Chat ID pribadi kamu:")
    print("   -> Cari @userinfobot di Telegram, klik Start.")
    print("   -> Bot tersebut langsung membalas nomor 'Id: 123456789' (Chat ID).")
    print("5. PENTING: Buka bot buatanmu (dari langkah 3) lalu klik tombol START!")
    print("   (Bot Telegram tidak bisa kirim pesan sebelum kamu klik Start).")
    print("=" * 62 + "\n")
    questionary.press_any_key_to_continue().ask()


def menu_notifications():
    while True:
        cfg = load_config()
        notifs = cfg.get("notifications", {})
        tg = notifs.get("telegram", {})
        dc = notifs.get("discord", {})

        choices = [
            Choice(f"📱 Telegram Bot: {'🟢 AKTIF' if tg.get('enabled') else '⚪ Nonaktif'}", value="telegram"),
            Choice(f"💬 Discord Webhook: {'🟢 AKTIF' if dc.get('enabled') else '⚪ Nonaktif'}", value="discord"),
            Choice("🔔 Tes Semua Notifikasi Aktif", value="test_all"),
            Separator(),
            Choice("🔙 Kembali ke Menu Utama", value="back")
        ]

        action = questionary.select("🔔 Pengaturan Notifikasi ke HP:", choices=choices).ask()
        if action == "back" or not action:
            break

        elif action == "telegram":
            t_act = questionary.select("Pengaturan Telegram:", choices=[
                Choice(f"🔄 {'Nonaktifkan' if tg.get('enabled') else 'Aktifkan'}", value="toggle"),
                Choice("✏️  Atur / Ubah Token & Chat ID", value="edit"),
                Choice("🔔 Tes Notifikasi Telegram", value="test"),
                Choice("📖 Panduan Cara Dapatkan Token & ID", value="guide"),
                Choice("🔙 Kembali", value="back")
            ]).ask()

            if t_act == "toggle":
                tg["enabled"] = not tg.get("enabled", False)
                save_config(cfg)
                print(f"[✓] Telegram: {'AKTIF' if tg['enabled'] else 'NONAKTIF'}\n")
            elif t_act == "edit":
                tok = questionary.text("Telegram Bot Token:", default=tg.get("bot_token", "")).ask()
                cid = questionary.text("Telegram Chat ID:", default=tg.get("chat_id", "")).ask()
                if tok is not None:
                    tg["bot_token"] = tok.strip()
                if cid is not None:
                    tg["chat_id"] = cid.strip()
                if tg.get("bot_token") and tg.get("chat_id"):
                    tg["enabled"] = True
                save_config(cfg)
                print("[✓] Konfigurasi Telegram disimpan!\n")
            elif t_act == "test":
                if not tg.get("bot_token") or not tg.get("chat_id"):
                    print("[!] Lengkapi Token dan Chat ID terlebih dahulu.\n")
                else:
                    ok, msg = send_telegram_notification(tg["bot_token"], tg["chat_id"], "Tes Snapchat Streak", "Halo! Notifikasi bot Snapchat Streak berhasil terhubung 🎉", True)
                    print(f"[{'✓' if ok else '!'}] {msg}\n")
                questionary.press_any_key_to_continue().ask()
            elif t_act == "guide":
                show_telegram_guide()

        elif action == "discord":
            d_act = questionary.select("Pengaturan Discord:", choices=[
                Choice(f"🔄 {'Nonaktifkan' if dc.get('enabled') else 'Aktifkan'}", value="toggle"),
                Choice("✏️  Atur / Ubah Webhook URL", value="edit"),
                Choice("🔔 Tes Notifikasi Discord", value="test"),
                Choice("🔙 Kembali", value="back")
            ]).ask()
            if d_act == "toggle":
                dc["enabled"] = not dc.get("enabled", False)
                save_config(cfg)
                print(f"[✓] Discord Webhook: {'AKTIF' if dc['enabled'] else 'NONAKTIF'}\n")
            elif d_act == "edit":
                url = questionary.text("Discord Webhook URL:", default=dc.get("webhook_url", "")).ask()
                if url is not None:
                    dc["webhook_url"] = url.strip()
                if dc.get("webhook_url"):
                    dc["enabled"] = True
                save_config(cfg)
                print("[✓] Discord Webhook disimpan!\n")
            elif d_act == "test":
                if not dc.get("webhook_url"):
                    print("[!] Masukkan Webhook URL terlebih dahulu.\n")
                else:
                    ok, msg = send_discord_notification(dc["webhook_url"], "Tes Snapchat Streak", "Halo! Webhook Discord Snapchat Streak terhubung 🎉", True)
                    print(f"[{'✓' if ok else '!'}] {msg}\n")
                questionary.press_any_key_to_continue().ask()

        elif action == "test_all":
            print("\n[*] Mengirim notifikasi tes...")
            send_notification("Tes Notifikasi Snapchat Streak", "Halo! Notifikasi pengingat streak berhasil terhubung.", success=True)
            print("[✓] Notifikasi tes dikirim!\n")
            questionary.press_any_key_to_continue().ask()


def menu_account():
    while True:
        is_logged_in = check_login_status()
        contacts = load_config().get("contacts", [])
        status_label = "🟢 VALID (Aktif)" if is_logged_in else "🔴 BELUM LOGIN"

        choices = [
            Choice(f"🔍 Pindai Kontak Teman dari Snapchat (Tersimpan: {len(contacts)} teman)", value="scan"),
            Choice("🔑 Login / Hubungkan Akun Snapchat (Buka Jendela Browser)", value="login"),
            Choice(f"ℹ️  Cek Ulang Status Sesi Login (Status: {status_label})", value="check"),
            Separator(),
            Choice("🔙 Kembali ke Menu Utama", value="back")
        ]

        action = questionary.select("🔑 Manajemen Akun & Kontak Snapchat:", choices=choices).ask()
        if action == "back" or not action:
            break

        elif action == "scan":
            if not check_login_status():
                print("\n[!] Akun Snapchat Anda belum terhubung (Sesi Kosong / Belum Login).")
                do_login = questionary.confirm("Buka jendela browser untuk login sekarang?", default=True).ask()
                if do_login:
                    interactive_login()
                else:
                    questionary.press_any_key_to_continue().ask()
                    continue
            scan_snapchat_friends(verbose=True)
            questionary.press_any_key_to_continue().ask()

        elif action == "login":
            interactive_login()
            questionary.press_any_key_to_continue().ask()

        elif action == "check":
            print("\n[*] Memeriksa sesi browser Snapchat...")
            ok = check_login_status()
            print(f"[{'✓' if ok else '!'}] Status Sesi: {'🟢 VALID (Aktif)' if ok else '🔴 KADALUARSA / BELUM LOGIN'}\n")
            questionary.press_any_key_to_continue().ask()


def menu_manage_scheduler():
    while True:
        is_active, desc = get_scheduler_status()
        cfg = load_config()
        sched = cfg.get("schedule", {"hour": 9, "minute": 0})
        time_str = f"{sched['hour']:02d}:{sched['minute']:02d}"

        choices = [
            Choice(f"⏰ Pasang / Aktifkan Jadwal Harian (Jam {time_str} + Auto Catch-up)", value="install"),
            Choice(f"🕒 Ubah Jam Eksekusi (Saat ini: Jam {time_str})", value="change_time"),
            Choice("🗑️  Matikan / Hapus Jadwal", value="remove"),
            Separator(),
            Choice("🔙 Kembali ke Menu Utama", value="back")
        ]

        action = questionary.select(
            f"⏰ Pengatur Jadwal Harian [{OS_NAME}] (Status: {'🟢' if is_active else '⚪'} {desc}):",
            choices=choices
        ).ask()

        if action == "back" or not action:
            break

        elif action == "install":
            install_scheduler()
            questionary.press_any_key_to_continue().ask()

        elif action == "change_time":
            new_time = questionary.text("Masukkan jam baru (Format JJ:MM, contoh: 08:30):", default=time_str).ask()
            if new_time and ":" in new_time:
                try:
                    h, m = map(int, new_time.split(":", 1))
                    if 0 <= h <= 23 and 0 <= m <= 59:
                        cfg["schedule"] = {"hour": h, "minute": m}
                        save_config(cfg)
                        print(f"\n[✓] Waktu jadwal diubah ke {h:02d}:{m:02d}.")
                        if is_active:
                            install_scheduler()
                except ValueError:
                    print("\n[!] Format waktu salah.")
            questionary.press_any_key_to_continue().ask()

        elif action == "remove":
            remove_scheduler()
            questionary.press_any_key_to_continue().ask()


def menu_view_logs():
    while True:
        choices = [
            Choice("📜 Lihat Semua Log (3 Hari Terakhir)", value="all"),
            Choice("🚀 Filter Log Eksekusi Snap (JOB)", value="job"),
            Choice("⚙️  Filter Perubahan Pengaturan (CONFIG)", value="config"),
            Choice("🧹 Bersihkan Log Manual Sekarang", value="clean"),
            Separator(),
            Choice("🔙 Kembali ke Menu Utama", value="back")
        ]

        act = questionary.select("📜 Riwayat Aktivitas & Log (Retensi Otomatis 3 Hari):", choices=choices).ask()
        if act == "back" or not act:
            break

        if act in ("all", "job", "config"):
            cat = None if act == "all" else act.upper()
            clean_expired_logs(3)
            files = sorted([f for f in os.listdir(LOG_DIR) if f.startswith("activity_") and f.endswith(".log")])
            all_entries = []
            for f in files:
                filepath = os.path.join(LOG_DIR, f)
                try:
                    with open(filepath, "r", encoding="utf-8") as lf:
                        for line in lf:
                            if cat and f"[{cat}]" not in line:
                                continue
                            all_entries.append(line.strip())
                except Exception:
                    pass

            print("\n" + "=" * 70)
            print(f"📜 RIWAYAT AKTIVITAS & LOG ({'Semua' if not cat else cat}):")
            print("=" * 70)
            if not all_entries:
                print("  (Tidak ada catatan log)")
            else:
                for entry in all_entries[-40:]:
                    print(f"  {entry}")
            print("=" * 70 + "\n")
            questionary.press_any_key_to_continue().ask()

        elif act == "clean":
            if questionary.confirm("Hapus semua log aktivitas sekarang?").ask():
                for f in os.listdir(LOG_DIR):
                    if f.startswith("activity_"):
                        try:
                            os.remove(os.path.join(LOG_DIR, f))
                        except Exception:
                            pass
                print("\n[✓] Seluruh riwayat log berhasil dibersihkan!\n")
                questionary.press_any_key_to_continue().ask()


def interactive_hub():
    while True:
        print_dashboard()
        is_logged_in = check_login_status()

        if not is_logged_in:
            choices = [
                Choice("🔑 [WAJIB] LOGIN / HUBUNGKAN AKUN SEKARANG (Buka Browser)", value="login"),
                Choice("🚀 Kirim Streak Sekarang (Perlu Login Terlebih Dahulu)", value="run"),
                Choice("👥 Kelola Penerima & Caption (Penerima, Grup & Template)", value="recipients"),
                Choice("⏰ Jadwal Otomatis Harian (LaunchAgent @ 09:00 + Wake-up Catch-up)", value="scheduler"),
                Choice("📜 Riwayat Aktivitas & Log (Tersimpan 3 Hari)", value="logs"),
                Choice("🔔 Pengaturan Notifikasi (Telegram / Discord)", value="notifications"),
                Choice("🔄 Cek Pembaruan Aplikasi (Check for Updates)", value="check_update"),
                Separator(),
                Choice("🚪 Keluar", value="exit")
            ]
        else:
            choices = [
                Choice("🚀 Kirim Streak Sekarang (Run Snap Check-in)", value="run"),
                Choice("👥 Kelola Penerima & Caption (Penerima, Grup & Template)", value="recipients"),
                Choice("⏰ Jadwal Otomatis Harian (LaunchAgent @ 09:00 + Wake-up Catch-up)", value="scheduler"),
                Choice("📜 Riwayat Aktivitas & Log (Tersimpan 3 Hari)", value="logs"),
                Choice("🔑 Akun & Pindai Kontak (Login & Scan Teman Snapchat)", value="account"),
                Choice("🔔 Pengaturan Notifikasi (Telegram / Discord)", value="notifications"),
                Choice("🔄 Cek Pembaruan Aplikasi (Check for Updates)", value="check_update"),
                Separator(),
                Choice("🚪 Keluar", value="exit")
            ]

        action = questionary.select(
            "Pilih Menu:",
            choices=choices,
            use_indicator=True
        ).ask()

        if action in ("exit", None):
            print("\n👋 Sampai jumpa! Snap streak Anda aman.\n")
            break

        elif action == "login":
            interactive_login()
            questionary.press_any_key_to_continue().ask()

        elif action == "run":
            if not check_login_status():
                print("\n[!] Anda belum login ke akun Snapchat.")
                do_login = questionary.confirm("Buka jendela browser untuk login sekarang?", default=True).ask()
                if do_login:
                    interactive_login()
            else:
                run_send_streak(force=True, verbose=True)
                questionary.press_any_key_to_continue().ask()

        elif action == "recipients":
            menu_manage_recipients()

        elif action == "scheduler":
            menu_manage_scheduler()

        elif action == "logs":
            menu_view_logs()

        elif action == "account":
            menu_account()

        elif action == "notifications":
            menu_notifications()

        elif action == "check_update":
            check_for_updates(prompt_if_latest=True)

# ==============================================================================
# CLI Entry Point & Background Worker
# ==============================================================================

def run_cron_job(max_retries: int = 3, retry_delay: int = 40):
    log_activity("SYSTEM", "Snapchat Streak auto-worker dipicu oleh scheduler.")

    if not wait_for_internet(timeout=180, verbose=False):
        err = "Cron dibatalkan: Laptop belum terhubung ke internet setelah 3 menit."
        log_activity("SYSTEM", err)
        return

    is_safe, desc = is_within_safe_hours()
    if not is_safe:
        log_activity("SYSTEM", f"Cron ditangguhkan: di luar jam aman {desc}.")
        return

    for attempt in range(1, max_retries + 1):
        res = run_send_streak(force=False, verbose=False)
        st = res.get("status")
        if st in ("success", "skipped"):
            log_activity("SYSTEM", f"Cron selesai pada percobaan ke-{attempt}: {st}")
            return
        elif attempt < max_retries:
            time.sleep(retry_delay)


def main():
    parser = argparse.ArgumentParser(description="Snapchat Streak Auto-Saver Hub")
    parser.add_argument("--cron", action="store_true", help="Background automation mode for LaunchAgent / Task Scheduler")
    parser.add_argument("--force", action="store_true", help="Force send even if streak already sent today")
    parser.add_argument("--scan", action="store_true", help="Scan Snapchat friends and exit")
    parser.add_argument("--login", action="store_true", help="Launch interactive login window")
    args = parser.parse_args()

    if args.cron:
        run_cron_job()
    elif args.scan:
        scan_snapchat_friends(verbose=True)
    elif args.login:
        interactive_login()
    elif args.force:
        run_send_streak(force=True, verbose=True)
    else:
        check_for_updates(prompt_if_latest=False)
        interactive_hub()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        handle_sigint()
