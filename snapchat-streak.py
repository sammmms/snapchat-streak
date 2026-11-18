#!/usr/bin/env python3
"""
👻 Snapchat Streak Auto-Saver & Helper Hub
Automated Snap Dispatcher & Streak Maintenance via web.snapchat.com
Author: Sam & Antigravity (Advanced Agentic Pair Programming)
License: MIT
Bilingual Support: English (Default) & Bahasa Indonesia
"""

import os
import sys
import re
import json
import time
import random
import signal
import socket
import shutil
import platform
import argparse
import subprocess
from datetime import datetime, date, timedelta

OS_NAME = platform.system()
IS_CRON = "--cron" in sys.argv
APP_NAME = "snapchat-streak"
CURRENT_VERSION = "1.4.3"

PRIMARY_UPDATE_URL = f"https://script.wsnsam.my.id/api/updates?app={APP_NAME}"
FALLBACK_UPDATE_URL = f"https://raw.githubusercontent.com/sammmms/{APP_NAME}/main/version.json"
SCRIPT_RAW_URL = f"https://raw.githubusercontent.com/sammmms/{APP_NAME}/main/snapchat-streak.py"

HOME_DIR = os.path.expanduser("~")
BASE_DIR = os.path.join(HOME_DIR, ".snapchat-streak")
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")
STATE_FILE = os.path.join(BASE_DIR, "last_run.json")
LOG_DIR = os.path.join(BASE_DIR, "logs")
PROFILE_DIR = os.path.join(BASE_DIR, "browser_profile")
STORAGE_STATE_FILE = os.path.join(BASE_DIR, "storage_state.json")
TEMP_SNAP_IMAGE = os.path.join(BASE_DIR, "temp_snap.png")

SNAPCHAT_WEB_URL = "https://web.snapchat.com"
SNAPCHAT_LOGIN_URL = "https://accounts.snapchat.com/v2/login?continue=https%3A%2F%2Fweb.snapchat.com"

# ==============================================================================
# Internationalization (i18n): EN (Default) & ID
# ==============================================================================

DEFAULT_LANG = "en"
CURRENT_LANG = "en"

TRANSLATIONS = {
    "en": {
        "sigint_exit": "\n\n👋 Operation cancelled by user (Exit). Goodbye!\n",
        "checking_updates": "Checking for updates",
        "update_offline": "[*] Checking for updates... [Done / Offline Mode ✓]",
        "update_latest": "[*] Checking for updates... [Latest Version: v{ver} ✓]",
        "update_already_latest": "\n[✓] You are already on the latest version (v{ver}).\n",
        "press_key_continue": "Press any key to continue...",
        "press_key_return": "Press any key to return to menu...",
        "update_available": "🎉 Snapchat Streak Update v{ver} Available! (Current: v{current})",
        "changelog": "Release Notes (Changelog):",
        "update_confirm": "Install update v{ver} now directly from the app?",
        "update_downloading": "\n[*] Downloading snapchat-streak.py v{ver}...",
        "update_download_fail": "[!] Failed to download update file.",
        "update_success": "[✓] Successfully updated to version v{ver}!\n",
        "restarting_app": "[*] Restarting application...",
        "sched_macos_active": "Active (macOS LaunchAgent @ {time} with Wake-up Catch-up)",
        "sched_macos_loaded": "Loaded (macOS LaunchAgent)",
        "sched_win_active": "Active (Windows Task Scheduler)",
        "sched_linux_active": "Active (Linux Crontab)",
        "sched_not_configured": "Not Configured",
        "sched_unsupported": "Unsupported OS",
        "sched_installed_mac": "[✓] macOS LaunchAgent registered successfully at {time} with multi-interval wake-up catch-up!",
        "sched_installed_win": "[✓] Windows Task Scheduler registered successfully at {time}.",
        "sched_installed_linux": "[✓] Linux Crontab registered successfully at {time}.",
        "sched_removed_mac": "[✓] macOS LaunchAgent removed.",
        "sched_removed_win": "[✓] Windows Task Scheduler removed.",
        "sched_removed_linux": "[✓] Linux Crontab removed.",
        "wait_internet": "Checking internet connection",
        "internet_connected": "[*] Internet connection: [Connected ✓] ({elapsed:.1f}s)",
        "internet_connected_http": "[*] Internet connection: [Connected via HTTP ✓] ({elapsed:.1f}s)",
        "internet_failed": "[!] Internet connection: [Failed / Timed Out]",
        "dash_title": "👻 Snapchat Streak Auto-Saver & Helper Hub",
        "dash_account_status": "👤 Account Session : ",
        "dash_status_valid": "🟢 VALID (Active)",
        "dash_status_unauthed": "🔴 NOT LOGGED IN",
        "dash_today_status": "📅 Today's Status  : ",
        "dash_today_sent": " 🟢 Already Sent Today",
        "dash_today_failed": " 🔴 Failed Today",
        "dash_today_pending": " ⌛ Not Sent Today",
        "dash_recipient_mode": "👥 Recipient Mode  : ",
        "dash_schedule": "⏰ Auto Schedule   : ",
        "dash_warn_unauthed_title": "⚠️  ACCOUNT STATUS: NOT LOGGED IN / EMPTY SESSION",
        "dash_warn_unauthed_desc1": "👉 You have not connected your Snapchat account yet.",
        "dash_warn_unauthed_desc2": "   Streak automation cannot run before you log in.",
        "dash_warn_unauthed_desc3": "👉 Please select [🔑 LOGIN NOW] in the menu below!",
        "dash_mode_all": "Select All (All Friends)",
        "dash_mode_groups": "Groups / Labeling",
        "menu_select": "Select Menu:",
        "menu_opt_login_req": "🔑 [REQUIRED] LOGIN / CONNECT ACCOUNT NOW (Open Browser)",
        "menu_opt_run_need_login": "🚀 Send Streak Now (Login Required)",
        "menu_opt_run": "🚀 Send Streak Now (Run Snap Check-in)",
        "menu_opt_recipients": "👥 Manage Recipients & Caption (Recipients, Groups & Templates)",
        "menu_opt_speed": "⚡ Dispatch Speed & Safety (Pace & Browser Mode)",
        "menu_opt_scheduler": "⏰ Daily Auto Schedule (LaunchAgent @ {time} + Wake-up Catch-up)",
        "menu_opt_logs": "📜 Activity History & Logs (3-Day Retention)",
        "menu_opt_account": "🔑 Account & Scan Contacts (Login & Scan Snapchat Friends)",
        "menu_opt_notifications": "🔔 Notification Settings (Telegram / Discord)",
        "menu_opt_check_update": "🔄 Check for Updates",
        "menu_opt_lang": "🌐 Language / Bahasa (Current: {current})",
        "menu_opt_exit": "🚪 Exit",
        "goodbye": "\n👋 Goodbye! Your Snap streak is safe.\n",
        "lang_menu_title": "🌐 Select Language / Pilih Bahasa:",
        "lang_opt_en": "🇬🇧 English (Default)",
        "lang_opt_id": "🇮🇩 Bahasa Indonesia",
        "lang_opt_back": "🔙 Back / Kembali",
        "lang_changed": "\n[✓] Language changed to: {lang}\n",
        "current_lang_label": "Current",
        "login_title": "🔑 LOGIN / CONNECT SNAPCHAT ACCOUNT (OFFICIAL BROWSER)",
        "login_step_1": "1. An official browser window will open directly to Snapchat Web.",
        "login_step_2": "2. Enter your Username / Email / Phone and Password.",
        "login_step_3": "3. If prompted for 2FA or mobile app verification, please approve it.",
        "login_step_4": "4. Make sure you can see the Snapchat Chat interface in the browser.",
        "login_step_5": "5. RETURN TO THIS TERMINAL and press [ENTER].",
        "login_step_5_sub": "   👉 The browser window will be closed automatically (do not close manually).",
        "login_press_enter": "Press [ENTER] to open login browser window...",
        "login_browser_opened": "\n[*] Browser window opened.",
        "login_browser_hint": "[*] Please log in to your Snapchat account in the browser window.",
        "login_wait_confirm": "\n👉 Once you have FINISHED LOGGING IN and can see the Chat page, press [ENTER] here...\n   (Browser will be closed automatically by script, do not close manually)",
        "login_success": "\n[✓] Login SUCCESSFUL! Account session saved on computer.",
        "login_failed_prompt": "\n[!] Notice: No active login session detected.\n    Make sure you completed login to the Chat screen before pressing [ENTER].\n    Please try again from Login menu.",
        "scan_starting": "[*] Scanning friends list and streak status on Snapchat Web...",
        "scan_not_connected": "\n[!] Your Snapchat account is not connected (Empty Session).\n    👉 Please select [🔑 Login / Connect Account] first to log in.",
        "scan_session_expired": "\n[!] Snapchat account session expired or not logged in.\n    👉 Please select [🔑 Login / Connect Account] to re-login.",
        "scan_found_summary": "\n[✓] Successfully saved {count} friends to contact list.\n",
        "scan_none_detected": "[-] No friend conversations detected automatically.\n    Make sure you are logged in and have the Chat tab visible on Snapchat Web.",
        "scan_error": "[!] Failed to scan contacts: {err}",
        "logout_confirm": "Are you sure you want to log out and clear saved session and friend cache?",
        "logout_success": "\n[✓] Logout successful! Session and friend cache cleared.\n",
        "logout_failed": "\n[!] Logout failed: {err}\n",
        "streak_skipped_today": "Streak today ({date}) was already sent at {time}.",
        "streak_no_targets": "No target contacts selected. Please Scan Contacts or assign Groups in Menu 2.",
        "streak_offline": "Failed to connect to internet within tolerance window.",
        "streak_starting_banner": "🚀 STARTING SNAP STREAK DISPATCH ({count} Contacts)",
        "streak_session_expired": "Snapchat login session expired or not logged in. Please log in via terminal menu.",
        "streak_exec_result": "🏁 SNAP STREAK EXECUTION RESULT: {summary}",
        "recip_menu_title": "👥 Manage Recipients & Caption [Mode: {mode}]:",
        "recip_toggle_mode": "🔄 Switch Mode (Current: {mode})",
        "recip_checklist": "📋 Contact Checklist & Assign Groups (Multi-select)",
        "recip_groups": "🏷️  Manage Group Labels",
        "recip_caption": "💬 Configure Snap Caption (Default, Random Pool & Custom)",
        "recip_exclude": "🚫 Manage Exclude / Blacklist",
        "recip_preview": "👁️  Preview Caption to be Sent",
        "recip_back": "🔙 Back to Main Menu",
        "recip_mode_changed": "\n[✓] Recipient mode changed to: {mode}\n",
        "sched_menu_title": "⏰ Daily Schedule Manager [{os}] (Status: {badge}):",
        "sched_opt_install": "⏰ Enable / Install Daily Schedule (Runs at {time} + Auto Catch-up)",
        "sched_opt_change_time": "🕒 Change Run Time (Current: {time})",
        "sched_opt_remove": "🗑️  Disable / Remove Schedule",
        "sched_prompt_new_time": "Enter new time (Format HH:MM, e.g. 08:30):",
        "sched_time_changed": "\n[✓] Schedule time changed to {time}.",
        "sched_time_invalid": "\n[!] Invalid time format.",
        "notif_menu_title": "🔔 Notification Settings:",
        "notif_telegram": "📱 Telegram Bot: {status}",
        "notif_discord": "💬 Discord Webhook: {status}",
        "notif_test_all": "🔔 Test All Active Notifications",
        "notif_back": "🔙 Back to Main Menu",
        "notif_test_sending": "\n[*] Sending test notification to all active channels...",
        "notif_test_done": "[✓] Test notifications dispatched!\n",
        "status_active_upper": "🟢 ACTIVE",
        "status_inactive_upper": "⚪ INACTIVE",
        "account_menu_title": "🔑 Snapchat Account & Contact Management:",
        "account_opt_scan": "🔍 Scan Friends from Snapchat (Saved: {count} friends)",
        "account_opt_login": "🔑 Login / Connect Snapchat Account (Open Browser)",
        "account_opt_check": "ℹ️  Re-check Session Status (Status: {status})",
        "account_opt_logout": "🚪 Logout / Clear Session & Reset Friend Cache",
        "account_opt_back": "🔙 Back to Main Menu",
        "logs_menu_title": "📜 Activity History & Logs (3-Day Retention):",
        "logs_opt_all": "📜 View All Logs (Last 3 Days)",
        "logs_opt_job": "🚀 Filter Snap Execution Logs (JOB)",
        "logs_opt_config": "⚙️  Filter Configuration Changes (CONFIG)",
        "logs_opt_clean": "🧹 Clear Logs Manually Now",
        "logs_opt_back": "🔙 Back to Main Menu",
        "logs_clean_confirm": "Delete all activity logs now?",
        "logs_cleaned": "\n[✓] All activity logs cleared successfully!\n",
        "notif_streak_success_title": "Snapchat Streak Success",
        "notif_streak_fail_title": "Snapchat Streak Failed",
    },
    "id": {
        "sigint_exit": "\n\n👋 Operasi dibatalkan oleh pengguna (Keluar). Sampai jumpa!\n",
        "checking_updates": "Memeriksa pembaruan terbaru",
        "update_offline": "[*] Memeriksa pembaruan terbaru... [Selesai / Mode Offline ✓]",
        "update_latest": "[*] Memeriksa pembaruan terbaru... [Versi Terbaru: v{ver} ✓]",
        "update_already_latest": "\n[✓] Anda sudah menggunakan versi paling baru (v{ver}).\n",
        "press_key_continue": "Tekan tombol apa saja untuk melanjutkan...",
        "press_key_return": "Tekan tombol apa saja untuk kembali ke menu...",
        "update_available": "🎉 Pembaruan Snapchat Streak v{ver} Tersedia! (Versi saat ini: v{current})",
        "changelog": "Catatan Rilis (Changelog):",
        "update_confirm": "Pasang pembaruan v{ver} sekarang langsung dari aplikasi?",
        "update_downloading": "\n[*] Mengunduh snapchat-streak.py v{ver}...",
        "update_download_fail": "[!] Gagal mengunduh berkas pembaruan.",
        "update_success": "[✓] Berhasil diperbarui ke versi v{ver}!\n",
        "restarting_app": "[*] Memulai ulang aplikasi...",
        "sched_macos_active": "Active (macOS LaunchAgent @ {time} with Wake-up Catch-up)",
        "sched_macos_loaded": "Loaded (macOS LaunchAgent)",
        "sched_win_active": "Active (Windows Task Scheduler)",
        "sched_linux_active": "Active (Linux Crontab)",
        "sched_not_configured": "Belum Dikonfigurasi",
        "sched_unsupported": "Sistem Operasi Tidak Didukung",
        "sched_installed_mac": "[✓] Jadwal harian berhasil didaftarkan pukul {time} dengan multi-interval catch-up via macOS LaunchAgent!",
        "sched_installed_win": "[✓] Windows Task Scheduler berhasil didaftarkan pukul {time}.",
        "sched_installed_linux": "[✓] Linux Crontab berhasil didaftarkan pukul {time}.",
        "sched_removed_mac": "[✓] macOS LaunchAgent berhasil dihapus.",
        "sched_removed_win": "[✓] Windows Task Scheduler berhasil dihapus.",
        "sched_removed_linux": "[✓] Linux Crontab berhasil dihapus.",
        "wait_internet": "Memeriksa koneksi internet",
        "internet_connected": "[*] Koneksi internet: [Terhubung ✓] ({elapsed:.1f}s)",
        "internet_connected_http": "[*] Koneksi internet: [Terhubung via HTTP ✓] ({elapsed:.1f}s)",
        "internet_failed": "[!] Koneksi internet: [Gagal / Batas Waktu Habis]",
        "dash_title": "👻 Snapchat Streak Auto-Saver & Helper Hub",
        "dash_account_status": "👤 Akun Sesi      : ",
        "dash_status_valid": "🟢 VALID (Aktif)",
        "dash_status_unauthed": "🔴 BELUM LOGIN",
        "dash_today_status": "📅 Status Hari Ini: ",
        "dash_today_sent": " 🟢 Sudah Terkirim Hari Ini",
        "dash_today_failed": " 🔴 Gagal Hari Ini",
        "dash_today_pending": " ⌛ Belum Terkirim Hari Ini",
        "dash_recipient_mode": "👥 Mode Penerima  : ",
        "dash_schedule": "⏰ Jadwal Auto    : ",
        "dash_warn_unauthed_title": "⚠️  STATUS AKUN: BELUM LOGIN / SESI KOSONG",
        "dash_warn_unauthed_desc1": "👉 Anda belum menghubungkan akun Snapchat.",
        "dash_warn_unauthed_desc2": "   Otomasi streak tidak dapat berjalan sebelum Anda login terlebih dahulu.",
        "dash_warn_unauthed_desc3": "👉 Silakan pilih menu [🔑 LOGIN SEKARANG] di bawah ini!",
        "dash_mode_all": "Select All (Semua Teman)",
        "dash_mode_groups": "Groups / Labeling",
        "menu_select": "Pilih Menu:",
        "menu_opt_login_req": "🔑 [WAJIB] LOGIN / HUBUNGKAN AKUN SEKARANG (Buka Browser)",
        "menu_opt_run_need_login": "🚀 Kirim Streak Sekarang (Perlu Login Terlebih Dahulu)",
        "menu_opt_run": "🚀 Kirim Streak Sekarang (Run Snap Check-in)",
        "menu_opt_recipients": "👥 Kelola Penerima & Caption (Penerima, Grup & Template)",
        "menu_opt_speed": "⚡ Pengaturan Kecepatan & Keamanan (Pace & Mode Browser)",
        "menu_opt_scheduler": "⏰ Jadwal Otomatis Harian (LaunchAgent @ {time} + Wake-up Catch-up)",
        "menu_opt_logs": "📜 Riwayat Aktivitas & Log (Tersimpan 3 Hari)",
        "menu_opt_account": "🔑 Akun & Pindai Kontak (Login & Scan Teman Snapchat)",
        "menu_opt_notifications": "🔔 Pengaturan Notifikasi (Telegram / Discord)",
        "menu_opt_check_update": "🔄 Cek Pembaruan Aplikasi (Check for Updates)",
        "menu_opt_lang": "🌐 Language / Bahasa (Saat ini: {current})",
        "menu_opt_exit": "🚪 Keluar",
        "goodbye": "\n👋 Sampai jumpa! Snap streak Anda aman.\n",
        "lang_menu_title": "🌐 Pilih Bahasa / Select Language:",
        "lang_opt_en": "🇬🇧 English (Default)",
        "lang_opt_id": "🇮🇩 Bahasa Indonesia",
        "lang_opt_back": "🔙 Kembali / Back",
        "lang_changed": "\n[✓] Bahasa berhasil diubah ke: {lang}\n",
        "current_lang_label": "Saat ini",
        "login_title": "🔑 LOGIN / HUBUNGKAN AKUN SNAPCHAT (BROWSER RESMI)",
        "login_step_1": "1. Jendela browser resmi akan terbuka langsung ke Snapchat Web.",
        "login_step_2": "2. Masukkan Username / Email / Nomor HP dan Password Anda.",
        "login_step_3": "3. Jika diminta verifikasi 2FA atau notifikasi di aplikasi HP, silakan setujui.",
        "login_step_4": "4. Pastikan Anda sudah melihat halaman obrolan / daftar Chat di browser.",
        "login_step_5": "5. KEMBALI KE TERMINAL INI dan tekan [ENTER].",
        "login_step_5_sub": "   👉 Jendela browser akan ditutup otomatis oleh script (jangan tutup manual).",
        "login_press_enter": "Tekan [ENTER] untuk membuka jendela browser login...",
        "login_browser_opened": "\n[*] Jendela browser telah terbuka.",
        "login_browser_hint": "[*] Silakan login akun Snapchat Anda di browser tersebut.",
        "login_wait_confirm": "\n👉 Setelah Anda SUDAH SELESAI LOGIN dan melihat halaman obrolan/Chat di browser, tekan [ENTER] di sini...\n   (Browser akan ditutup otomatis oleh script, jangan ditutup manual)",
        "login_success": "\n[✓] Login BERHASIL! Sesi akun tersimpan rapi di komputer.",
        "login_failed_prompt": "\n[!] Perhatian: Belum terdeteksi sesi login aktif.\n    Pastikan Anda sudah menyelesaikan proses login sampai halaman Chat sebelum menekan [ENTER].\n    Silakan coba lagi dari menu Login.",
        "scan_starting": "[*] Memindai daftar teman dan status streak di Snapchat Web...",
        "scan_not_connected": "\n[!] Akun Snapchat Anda belum terhubung (Sesi Kosong).\n    👉 Silakan pilih menu [🔑 Login / Hubungkan Akun] terlebih dahulu untuk login.",
        "scan_session_expired": "\n[!] Sesi akun Snapchat kedaluwarsa atau belum login.\n    👉 Silakan pilih menu [🔑 Login / Hubungkan Akun] untuk login ulang.",
        "scan_found_summary": "\n[✓] Berhasil menyimpan {count} teman ke daftar kontak.\n",
        "scan_none_detected": "[-] Tidak ada percakapan teman yang terdeteksi secara otomatis.\n    Pastikan Anda sudah login dan membuka tab Chat di Snapchat Web.",
        "scan_error": "[!] Gagal memindai kontak: {err}",
        "logout_confirm": "Yakin ingin logout dan menghapus sesi akun serta cache teman?",
        "logout_success": "\n[✓] Berhasil logout! Sesi akun dan cache teman telah dibersihkan.\n",
        "logout_failed": "\n[!] Gagal logout: {err}\n",
        "streak_skipped_today": "Streak hari ini ({date}) sudah terkirim pada {time}.",
        "streak_no_targets": "Tidak ada kontak target yang dipilih. Silakan Pindai Kontak atau tentukan Grup di Menu 2.",
        "streak_offline": "Gagal terhubung ke internet dalam batas waktu toleransi.",
        "streak_starting_banner": "🚀 MEMULAI PENGIRIMAN SNAP STREAK ({count} Kontak)",
        "streak_session_expired": "Sesi login Snapchat kedaluwarsa atau belum login. Silakan login via menu terminal.",
        "streak_exec_result": "🏁 HASIL EKSEKUSI SNAP STREAK: {summary}",
        "recip_menu_title": "👥 Kelola Penerima & Caption [Mode: {mode}]:",
        "recip_toggle_mode": "🔄 Ganti Mode Pengiriman (Saat ini: {mode})",
        "recip_checklist": "📋 Checklist Kontak & Tetapkan Grup (Multi-select)",
        "recip_groups": "🏷️  Kelola Label Grup",
        "recip_caption": "💬 Konfigurasi Caption Snap (Default, Pool Acak & Khusus)",
        "recip_exclude": "🚫 Kelola Daftar Pengecualian (Blacklist / Exclude)",
        "recip_preview": "👁️  Pratinjau Caption yang Akan Dikirim (Preview)",
        "recip_back": "🔙 Kembali ke Menu Utama",
        "recip_mode_changed": "\n[✓] Mode pengiriman diubah ke: {mode}\n",
        "sched_menu_title": "⏰ Pengatur Jadwal Harian [{os}] (Status: {badge}):",
        "sched_opt_install": "⏰ Pasang / Aktifkan Jadwal Harian (Jam {time} + Auto Catch-up)",
        "sched_opt_change_time": "🕒 Ubah Jam Eksekusi (Saat ini: Jam {time})",
        "sched_opt_remove": "🗑️  Matikan / Hapus Jadwal",
        "sched_prompt_new_time": "Masukkan jam baru (Format JJ:MM, contoh: 08:30):",
        "sched_time_changed": "\n[✓] Waktu jadwal diubah ke {time}.",
        "sched_time_invalid": "\n[!] Format waktu salah.",
        "notif_menu_title": "🔔 Pengaturan Notifikasi ke HP:",
        "notif_telegram": "📱 Telegram Bot: {status}",
        "notif_discord": "💬 Discord Webhook: {status}",
        "notif_test_all": "🔔 Tes Semua Notifikasi Aktif",
        "notif_back": "🔙 Kembali ke Menu Utama",
        "notif_test_sending": "\n[*] Mengirim notifikasi tes ke semua channel aktif...",
        "notif_test_done": "[✓] Notifikasi tes selesai dikirim!\n",
        "status_active_upper": "🟢 AKTIF",
        "status_inactive_upper": "⚪ NONAKTIF",
        "account_menu_title": "🔑 Manajemen Akun & Kontak Snapchat:",
        "account_opt_scan": "🔍 Pindai Kontak Teman dari Snapchat (Tersimpan: {count} teman)",
        "account_opt_login": "🔑 Login / Hubungkan Akun Snapchat (Buka Jendela Browser)",
        "account_opt_check": "ℹ️  Cek Ulang Status Sesi Login (Status: {status})",
        "account_opt_logout": "🚪 Logout / Hapus Sesi Akun & Reset Cache Teman",
        "account_opt_back": "🔙 Kembali ke Menu Utama",
        "logs_menu_title": "📜 Riwayat Aktivitas & Log (Retensi Otomatis 3 Hari):",
        "logs_opt_all": "📜 Lihat Semua Log (3 Hari Terakhir)",
        "logs_opt_job": "🚀 Filter Log Eksekusi Snap (JOB)",
        "logs_opt_config": "⚙️  Filter Perubahan Pengaturan (CONFIG)",
        "logs_opt_clean": "🧹 Bersihkan Log Manual Sekarang",
        "logs_opt_back": "🔙 Kembali ke Menu Utama",
        "logs_clean_confirm": "Hapus semua log aktivitas sekarang?",
        "logs_cleaned": "\n[✓] Seluruh riwayat log berhasil dibersihkan!\n",
        "notif_streak_success_title": "Snapchat Streak Berhasil",
        "notif_streak_fail_title": "Snapchat Streak Gagal",
    }
}

def t(key: str, default: str = None, **kwargs) -> str:
    lang = CURRENT_LANG if CURRENT_LANG in TRANSLATIONS else DEFAULT_LANG
    s = TRANSLATIONS.get(lang, {}).get(key)
    if s is None:
        s = TRANSLATIONS.get(DEFAULT_LANG, {}).get(key, default if default is not None else key)
    if kwargs:
        try:
            return s.format(**kwargs)
        except Exception:
            return s
    return s

def set_language(lang_code: str):
    global CURRENT_LANG
    if str(lang_code).lower() in ("id", "in", "indonesia", "indonesian"):
        CURRENT_LANG = "id"
    else:
        CURRENT_LANG = "en"

def handle_sigint(sig=None, frame=None):
    print(t("sigint_exit"))
    sys.exit(0)

signal.signal(signal.SIGINT, handle_sigint)

# Third-party dependencies (managed in venv)
try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
    import questionary
    from questionary import Choice, Separator
    import requests
except ImportError:
    print("\n[!] Missing dependencies. Run './install.sh' or 'pip install playwright questionary requests pillow'\n")
    sys.exit(1)

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
    import threading
    res = {"done": False, "result": None, "error": None}

    def target():
        try:
            res["result"] = worker_fn()
        except Exception as e:
            res["error"] = e
        finally:
            res["done"] = True

    thread = threading.Thread(target=target, daemon=True)
    thread.start()

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
    def fetch_remote():
        for target_url in [PRIMARY_UPDATE_URL, FALLBACK_UPDATE_URL]:
            try:
                resp = requests.get(target_url, timeout=3.5)
                if resp.status_code == 200:
                    return resp.json()
            except Exception:
                continue
        return None

    update_data, _ = run_with_progress(t("checking_updates"), fetch_remote, timeout=3.5)

    if not update_data or not isinstance(update_data, dict) or "version" not in update_data:
        sys.stdout.write(f"{t('update_offline')}\n")
        sys.stdout.flush()
        if prompt_if_latest:
            questionary.press_any_key_to_continue(t("press_key_continue")).ask()
        return

    try:
        remote_ver_str = update_data.get("version", CURRENT_VERSION)
        remote_ver = parse_semver(remote_ver_str)
        local_ver = parse_semver(CURRENT_VERSION)

        if remote_ver > local_ver:
            print(f"\r[*] {t('checking_updates')}... [v{remote_ver_str}]")
            changelogs = update_data.get("changelog", [])
            print("\n" + "=" * 60)
            print(t("update_available", ver=remote_ver_str, current=CURRENT_VERSION))
            print("=" * 60)
            if changelogs:
                print(t("changelog"))
                for c in changelogs:
                    print(f"  • {c}")
            print("=" * 60 + "\n")

            update_now = questionary.confirm(
                t("update_confirm", ver=remote_ver_str),
                default=True
            ).ask()

            if update_now:
                print(t("update_downloading", ver=remote_ver_str))
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
                    print(t("update_success", ver=remote_ver_str))
                    log_activity("SYSTEM", f"App updated from v{CURRENT_VERSION} to v{remote_ver_str}")
                    print(t("restarting_app"))
                    time.sleep(1.5)
                    os.execv(sys.executable, [sys.executable] + sys.argv)
                else:
                    print(t("update_download_fail"))
                    questionary.press_any_key_to_continue(t("press_key_continue")).ask()
        else:
            sys.stdout.write(f"\r{t('update_latest', ver=CURRENT_VERSION)}\n")
            sys.stdout.flush()
            if prompt_if_latest:
                print(t("update_already_latest", ver=CURRENT_VERSION))
                questionary.press_any_key_to_continue(t("press_key_continue")).ask()
    except Exception:
        sys.stdout.write(f"\r{t('update_offline')}\n")
        sys.stdout.flush()
        if prompt_if_latest:
            questionary.press_any_key_to_continue(t("press_key_continue")).ask()

DEFAULT_CONFIG = {
    "language": "en",  # "en" or "id"
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
        "mode": "single",
        "pool": [
            "🔥",
            "Streak 🔥⚡",
            "Good {time_greeting} {first_name}! Streak 🔥",
            "Happy {day} {first_name}! 🔥",
            "Streak for today {first_name} 🔥✨",
            "Good morning {first_name}! Don't forget our streak 🔥",
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
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "last_date": "",
        "last_time": "",
        "success": False,
        "sent_count": 0,
        "failed_count": 0,
        "summary": "Never executed"
    }

def save_state(success: bool, sent: int, failed: int, summary: str = "", session_expired: bool = None):
    now = datetime.now()
    state = load_state()
    state.update({
        "last_date": now.strftime("%Y-%m-%d"),
        "last_time": now.strftime("%H:%M:%S"),
        "success": success,
        "sent_count": sent,
        "failed_count": failed,
        "summary": summary
    })
    if session_expired is not None:
        state["session_expired"] = session_expired
    elif success:
        state["session_expired"] = False
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

def clean_expired_logs(retention_days: int = 3):
    ensure_dirs()
    cutoff_date = datetime.now() - timedelta(days=retention_days)
    pattern = re.compile(r"^activity_(\d{4}-\d{2}-\d{2})\.log$")

    for fname in os.listdir(LOG_DIR):
        m = pattern.match(fname)
        if m:
            try:
                fdate = datetime.strptime(m.group(1), "%Y-%m-%d")
                if fdate < cutoff_date:
                    os.remove(os.path.join(LOG_DIR, fname))
            except Exception:
                pass

def log_activity(category: str, message: str, print_to_console: bool = False):
    ensure_dirs()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{now_str}] [{category:<6}] {message}"
    if print_to_console and not IS_CRON:
        print(f"[*] {message}")

    today_log = os.path.join(LOG_DIR, f"activity_{datetime.now().strftime('%Y-%m-%d')}.log")
    try:
        with open(today_log, "a", encoding="utf-8") as f:
            f.write(entry + "\n")
    except Exception:
        pass

    global_log = os.path.join(BASE_DIR, "streak.log")
    try:
        with open(global_log, "a", encoding="utf-8") as f:
            f.write(entry + "\n")
    except Exception:
        pass

def log_message(msg: str):
    log_activity("JOB", msg, print_to_console=True)

# ==============================================================================
# Caption Template Engine & Placeholders
# ==============================================================================

def format_caption(template: str, contact_name: str) -> str:
    now = datetime.now()
    hour = now.hour

    if CURRENT_LANG == "id":
        if 4 <= hour < 11:
            time_greeting = "Pagi"
        elif 11 <= hour < 15:
            time_greeting = "Siang"
        elif 15 <= hour < 18:
            time_greeting = "Sore"
        else:
            time_greeting = "Malam"
        days_map = {0: "Senin", 1: "Selasa", 2: "Rabu", 3: "Kamis", 4: "Jumat", 5: "Sabtu", 6: "Minggu"}
        months_map = {1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "Mei", 6: "Jun", 7: "Jul", 8: "Agu", 9: "Sep", 10: "Okt", 11: "Nov", 12: "Des"}
        default_name = "Teman"
    else:
        if 4 <= hour < 12:
            time_greeting = "Morning"
        elif 12 <= hour < 17:
            time_greeting = "Afternoon"
        elif 17 <= hour < 21:
            time_greeting = "Evening"
        else:
            time_greeting = "Night"
        days_map = {0: "Monday", 1: "Tuesday", 2: "Wednesday", 3: "Thursday", 4: "Friday", 5: "Saturday", 6: "Sunday"}
        months_map = {1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "May", 6: "Jun", 7: "Jul", 8: "Aug", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec"}
        default_name = "Friend"

    day_name = days_map.get(now.weekday(), "Day")
    month_name = months_map.get(now.month, "")
    date_str = f"{now.day} {month_name}"
    first_name = contact_name.split()[0] if contact_name else default_name

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

def get_action_delay() -> float:
    cfg = load_config()
    pace = cfg.get("safety", {}).get("pace", "normal")
    if pace == "fast":
        return round(random.uniform(1.2, 2.0), 2)
    elif pace == "relaxed":
        return round(random.uniform(5.0, 7.5), 2)
    else:  # normal
        return round(random.uniform(2.5, 4.0), 2)

def is_within_safe_hours() -> tuple:
    cfg = load_config()
    safe_cfg = cfg.get("safety", {}).get("safe_hours", {})
    if not safe_cfg.get("enabled", True):
        return True, "Safe hours restriction disabled"

    now_hour = datetime.now().hour
    start = safe_cfg.get("start", 7)
    end = safe_cfg.get("end", 23)

    if start <= end:
        in_range = start <= now_hour < end
    else:
        in_range = now_hour >= start or now_hour < end

    if in_range:
        return True, "Within safe hours"
    else:
        reason = f"Outside safe dispatch hours ({start:02d}:00 - {end:02d}:00)" if CURRENT_LANG == "en" else f"Di luar jam aman pengiriman ({start:02d}:00 - {end:02d}:00)"
        return False, reason

def wait_for_internet(timeout: int = 180, check_interval: int = 2, verbose: bool = False) -> bool:
    start_time = time.time()
    frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    i = 0

    while time.time() - start_time < timeout:
        elapsed = time.time() - start_time
        pct = min(int((elapsed / timeout) * 100), 99)
        filled = pct // 10
        bar = "█" * filled + "░" * (10 - filled)

        if verbose:
            sys.stdout.write(f"\r[*] {t('wait_internet')}... {frames[i % len(frames)]} [{bar}] {int(elapsed)}s/{timeout}s")
            sys.stdout.flush()

        try:
            sock = socket.create_connection(("1.1.1.1", 53), timeout=2)
            sock.close()
            if verbose:
                sys.stdout.write("\r" + " " * 80 + "\r")
                print(t("internet_connected", elapsed=elapsed))
            return True
        except (socket.timeout, OSError):
            pass

        try:
            r = requests.get("https://web.snapchat.com", timeout=2)
            if r.status_code in (200, 301, 302, 403):
                if verbose:
                    sys.stdout.write("\r" + " " * 80 + "\r")
                    print(t("internet_connected_http", elapsed=elapsed))
                return True
        except Exception:
            pass

        time.sleep(check_interval)
        i += 1

    if verbose:
        sys.stdout.write("\r" + " " * 80 + "\r")
        print(t("internet_failed"))
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
        msg = f"{icon} <b>{safe_title}</b>\n\n{safe_text}\n\n<i>Time: {now_str}</i>"

        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        resp = requests.post(url, json={
            "chat_id": chat_id,
            "text": msg,
            "parse_mode": "HTML"
        }, timeout=10)

        data = resp.json()
        if resp.status_code == 200 and data.get("ok"):
            return True, "Successfully sent to Telegram!"
        else:
            desc = data.get("description", resp.text)
            return False, f"Telegram API Error ({resp.status_code}): {desc}"
    except Exception as e:
        return False, f"Telegram Connection Error: {e}"

def send_discord_notification(webhook_url: str, title: str, text: str, success: bool) -> tuple:
    try:
        color = 0x2ecc71 if success else 0xe74c3c
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        embed = {
            "title": f"{'✅' if success else '❌'} {title}",
            "description": text,
            "color": color,
            "footer": {"text": f"Snapchat Streak Helper • {now_str}"}
        }
        resp = requests.post(webhook_url, json={"embeds": [embed]}, timeout=10)
        if resp.status_code in (200, 204):
            return True, "Successfully sent to Discord!"
        else:
            return False, f"Discord Webhook Error ({resp.status_code}): {resp.text}"
    except Exception as e:
        return False, f"Discord Connection Error: {e}"

def send_notification(title: str, text: str, success: bool = True):
    cfg = load_config()
    notifs = cfg.get("notifications", {})

    if notifs.get("macos", {}).get("enabled", True) and OS_NAME == "Darwin":
        try:
            clean_text = text.replace(chr(34), chr(92) + chr(34)).replace(chr(10), " ")
            clean_title = title.replace(chr(34), chr(92) + chr(34))
            osa = f'display notification "{clean_text}" with title "{clean_title}"'
            subprocess.run(["osascript", "-e", osa], capture_output=True, timeout=5)
        except Exception:
            pass

    tg = notifs.get("telegram", {})
    if tg.get("enabled") and tg.get("bot_token") and tg.get("chat_id"):
        ok, msg = send_telegram_notification(tg["bot_token"], tg["chat_id"], title, text, success)
        log_activity("NOTIF", f"Telegram dispatch: {'Success' if ok else 'Failed'} ({msg})")

    dc = notifs.get("discord", {})
    if dc.get("enabled") and dc.get("webhook_url"):
        ok, msg = send_discord_notification(dc["webhook_url"], title, text, success)
        log_activity("NOTIF", f"Discord dispatch: {'Success' if ok else 'Failed'} ({msg})")

# ==============================================================================
# Auto-Scheduler (macOS LaunchAgent / Windows / Linux)
# ==============================================================================

def get_scheduler_status() -> tuple:
    cfg = load_config()
    sched = cfg.get("schedule", {"hour": 9, "minute": 0})
    time_str = f"{sched.get('hour', 9):02d}:{sched.get('minute', 0):02d}"

    if OS_NAME == "Darwin":
        plist = os.path.expanduser("~/Library/LaunchAgents/com.user.snapchat-streak.plist")
        if os.path.exists(plist):
            res = subprocess.run(["launchctl", "list"], capture_output=True, text=True)
            if "com.user.snapchat-streak" in res.stdout:
                return True, t("sched_macos_active", time=time_str)
            return True, t("sched_macos_loaded")
        return False, t("sched_not_configured")
    elif OS_NAME == "Windows":
        res = subprocess.run(["schtasks", "/Query", "/TN", "SnapchatStreakDaily"], capture_output=True, text=True)
        if res.returncode == 0:
            return True, t("sched_win_active")
        return False, t("sched_not_configured")
    else:
        res = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
        if "snapchat-streak" in res.stdout:
            return True, t("sched_linux_active")
        return False, t("sched_not_configured")

def install_scheduler():
    cfg = load_config()
    sched = cfg.get("schedule", {"hour": 9, "minute": 0})
    h = sched.get("hour", 9)
    m = sched.get("minute", 0)
    time_str = f"{h:02d}:{m:02d}"
    script_path = os.path.abspath(__file__)
    python_bin = sys.executable

    if OS_NAME == "Darwin":
        plist_path = os.path.expanduser("~/Library/LaunchAgents/com.user.snapchat-streak.plist")
        os.makedirs(os.path.dirname(plist_path), exist_ok=True)
        log_file = os.path.join(BASE_DIR, "streak.log")

        intervals = []
        for hour in range(h, 24):
            intervals.append(f"""        <dict>
            <key>Hour</key>
            <integer>{hour}</integer>
            <key>Minute</key>
            <integer>{m}</integer>
        </dict>""")
        intervals_xml = "\n".join(intervals)

        content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.user.snapchat-streak</string>
    <key>ProgramArguments</key>
    <array>
        <string>{python_bin}</string>
        <string>{script_path}</string>
        <string>--cron</string>
    </array>
    <key>StartCalendarInterval</key>
    <array>
{intervals_xml}
    </array>
    <key>StandardOutPath</key>
    <string>{log_file}</string>
    <key>StandardErrorPath</key>
    <string>{log_file}</string>
</dict>
</plist>
"""
        with open(plist_path, "w", encoding="utf-8") as f:
            f.write(content)

        subprocess.run(["launchctl", "unload", plist_path], capture_output=True)
        subprocess.run(["launchctl", "load", plist_path], check=True)
        print(t("sched_installed_mac", time=time_str))
        log_activity("CONFIG", f"Scheduler LaunchAgent installed at {time_str}")
        return True

    elif OS_NAME == "Windows":
        cmd = [
            "schtasks", "/Create", "/SC", "DAILY", "/TN", "SnapchatStreakDaily",
            "/TR", f'"{python_bin}" "{script_path}" --cron',
            "/ST", time_str, "/F"
        ]
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode == 0:
            print(t("sched_installed_win", time=time_str))
            log_activity("CONFIG", f"Windows Task Scheduler installed at {time_str}")
            return True
        return False

    elif OS_NAME == "Linux":
        res = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
        existing = res.stdout if res.returncode == 0 else ""
        filtered = [l for l in existing.splitlines() if "snapchat-streak" not in l]
        filtered.append(f"{m} {h} * * * {python_bin} {script_path} --cron >> {os.path.join(BASE_DIR, 'streak.log')} 2>&1")
        new_cron = "\n".join(filtered) + "\n"
        p = subprocess.Popen(["crontab", "-"], stdin=subprocess.PIPE, text=True)
        p.communicate(input=new_cron)
        print(t("sched_installed_linux", time=time_str))
        log_activity("CONFIG", f"Linux Crontab installed at {time_str}")
        return True

    return False

def remove_scheduler():
    if OS_NAME == "Darwin":
        plist_path = os.path.expanduser("~/Library/LaunchAgents/com.user.snapchat-streak.plist")
        if os.path.exists(plist_path):
            subprocess.run(["launchctl", "unload", plist_path], capture_output=True)
            os.remove(plist_path)
            print(t("sched_removed_mac"))
            log_activity("CONFIG", "macOS LaunchAgent removed")
            return True
    elif OS_NAME == "Windows":
        res = subprocess.run(["schtasks", "/Delete", "/TN", "SnapchatStreakDaily", "/F"], capture_output=True, text=True)
        if res.returncode == 0:
            print(t("sched_removed_win"))
            log_activity("CONFIG", "Windows Task Scheduler removed")
            return True
    elif OS_NAME == "Linux":
        res = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
        if res.returncode == 0:
            filtered = [l for l in res.stdout.splitlines() if "snapchat-streak" not in l]
            new_cron = "\n".join(filtered) + "\n"
            p = subprocess.Popen(["crontab", "-"], stdin=subprocess.PIPE, text=True)
            p.communicate(input=new_cron)
            print(t("sched_removed_linux"))
            log_activity("CONFIG", "Linux Crontab removed")
            return True
    return False

# ==============================================================================
# Browser & Automation Engine (Playwright)
# ==============================================================================

def save_auth_session(context) -> bool:
    try:
        ensure_dirs()
        context.storage_state(path=STORAGE_STATE_FILE)
        log_activity("AUTH", "Auth session saved to storage_state.json.")
        return True
    except Exception as e:
        log_activity("ERROR", f"Failed to save auth state: {e}")
        return False

def restore_auth_session(context) -> bool:
    if os.path.exists(STORAGE_STATE_FILE):
        try:
            with open(STORAGE_STATE_FILE, "r", encoding="utf-8") as f:
                state = json.load(f)
            cookies = state.get("cookies", [])
            if cookies:
                context.add_cookies(cookies)
                return True
        except Exception:
            pass
    return False

def launch_browser_context(p, headless: bool = True):
    ensure_dirs()
    user_agent = (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    )

    launch_args = [
        "--disable-blink-features=AutomationControlled",
        "--use-fake-ui-for-media-stream",
        "--use-fake-device-for-media-stream",
    ]

    def setup_context(ctx):
        ctx.set_default_timeout(30000)
        ctx.grant_permissions(["camera", "microphone", "notifications"], origin="https://web.snapchat.com")
        ctx.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
            window.chrome = { runtime: {} };
        """)
        restore_auth_session(ctx)
        return ctx

    # 1. Try launching Google Chrome with persistent profile (Best compatibility)
    try:
        context = p.chromium.launch_persistent_context(
            user_data_dir=PROFILE_DIR,
            channel="chrome",
            headless=headless,
            viewport={"width": 1440, "height": 900},
            user_agent=user_agent,
            args=launch_args
        )
        return setup_context(context)
    except Exception:
        pass

    # 2. Try default Chromium with persistent profile
    try:
        context = p.chromium.launch_persistent_context(
            user_data_dir=PROFILE_DIR,
            headless=headless,
            viewport={"width": 1440, "height": 900},
            user_agent=user_agent,
            args=launch_args
        )
        return setup_context(context)
    except Exception:
        pass

    # 3. Fallback to launched browser
    try:
        browser = p.chromium.launch(
            channel="chrome",
            headless=headless,
            args=launch_args
        )
        context = browser.new_context(
            viewport={"width": 1440, "height": 900},
            user_agent=user_agent
        )
        return setup_context(context)
    except Exception:
        pass

    browser = p.chromium.launch(
        headless=headless,
        args=launch_args
    )
    context = browser.new_context(
        viewport={"width": 1440, "height": 900},
        user_agent=user_agent
    )
    return setup_context(context)

def is_page_logged_in(page) -> bool:
    try:
        current_url = page.url.lower()
        if "accounts.snapchat.com/v2/login" in current_url:
            return False
        if "/?original_referrer" in current_url or "original_referrer" in current_url:
            return False

        login_button = page.locator("button:has-text('Log In'), a:has-text('Log In')")
        if login_button.count() > 0:
            for i in range(login_button.count()):
                if login_button.nth(i).is_visible():
                    return False

        chat_indicators = [
            '[aria-label="Friends Feed"]',
            '[aria-label="Chat Feed"]',
            '[data-testid="chat-feed"]',
            'button.fE2D5',
            'button.qJKfS'
        ]
        for sel in chat_indicators:
            if page.locator(sel).first.is_visible(timeout=1500):
                return True

        if "web.snapchat.com" in current_url or "snapchat.com/web" in current_url:
            return True
        return False
    except Exception:
        return False

def check_login_status() -> bool:
    try:
        st = load_state()
        if st.get("session_expired"):
            return False
        if not st.get("success", True) and "session expired" in str(st.get("summary", "")).lower():
            st_mtime = os.path.getmtime(STATE_FILE) if os.path.exists(STATE_FILE) else 0
            auth_mtime = os.path.getmtime(STORAGE_STATE_FILE) if os.path.exists(STORAGE_STATE_FILE) else 0
            if auth_mtime <= st_mtime:
                return False
    except Exception:
        pass

    if os.path.exists(STORAGE_STATE_FILE):
        try:
            with open(STORAGE_STATE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            cookies = data.get("cookies", [])
            now = time.time()
            for c in cookies:
                if "snapchat" in c.get("domain", ""):
                    name = c.get("name", "").lower()
                    expires = c.get("expires", -1)
                    if expires > 0 and expires < now:
                        continue
                    if "sc-a-" in name or ("session" in name and "blizzard" not in name) or "auth" in name or "sastate" in name:
                        return True
        except Exception:
            pass

    cookie_paths = [
        os.path.join(PROFILE_DIR, "Default", "Network", "Cookies"),
        os.path.join(PROFILE_DIR, "Default", "Cookies"),
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
                        OR name LIKE '%sastate%'
                    )
                """)
                count = cur.fetchone()[0]
                conn.close()
                if count >= 1:
                    return True
            except Exception:
                pass
    return False

def interactive_login():
    ensure_dirs()
    print("\n" + "=" * 68)
    print(t("login_title"))
    print("=" * 68)
    print(t("login_step_1"))
    print(t("login_step_2"))
    print(t("login_step_3"))
    print(t("login_step_4"))
    print(t("login_step_5"))
    print(t("login_step_5_sub"))
    print("=" * 68 + "\n")

    input(t("login_press_enter"))

    import threading
    login_confirmed = False

    with sync_playwright() as p:
        context = launch_browser_context(p, headless=False)
        page = context.pages[0] if context.pages else context.new_page()
        try:
            page.goto("https://web.snapchat.com", wait_until="domcontentloaded", timeout=60000)
        except Exception:
            pass

        print(t("login_browser_opened"))
        print(t("login_browser_hint"))

        stop_monitor = False
        def monitor_worker():
            while not stop_monitor:
                try:
                    if not page.is_closed() and is_page_logged_in(page):
                        save_auth_session(context)
                except Exception:
                    pass
                time.sleep(1.5)

        mon_thread = threading.Thread(target=monitor_worker, daemon=True)
        mon_thread.start()

        input(t("login_wait_confirm"))
        stop_monitor = True

        try:
            if not page.is_closed():
                time.sleep(1)
                save_auth_session(context)
                if is_page_logged_in(page):
                    login_confirmed = True
        except Exception:
            pass

        try:
            cookies = context.cookies()
            has_auth = any(
                ("sc-a-" in c["name"] or ("session" in c["name"].lower() and "blizzard" not in c["name"].lower()) or "auth" in c["name"].lower() or "sastate" in c["name"].lower())
                for c in cookies if "snapchat" in c.get("domain", "")
            )
            if has_auth:
                save_auth_session(context)
                login_confirmed = True
        except Exception:
            pass

        try:
            context.close()
        except Exception:
            pass

    if not login_confirmed:
        login_confirmed = check_login_status()

    if login_confirmed:
        print(t("login_success"))
        log_activity("AUTH", "Snapchat login successful and verified.")
        save_state(True, 0, 0, "Logged in successfully", session_expired=False)
        scan_snapchat_friends(verbose=True)
    else:
        print(t("login_failed_prompt"))

def logout_snapchat(verbose: bool = True) -> bool:
    try:
        if os.path.exists(STORAGE_STATE_FILE):
            os.remove(STORAGE_STATE_FILE)
        if os.path.exists(PROFILE_DIR):
            shutil.rmtree(PROFILE_DIR, ignore_errors=True)
            os.makedirs(PROFILE_DIR, exist_ok=True)

        st = load_state()
        st["session_expired"] = True
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(st, f, indent=2)

        cfg = load_config()
        cfg["contacts"] = []
        cfg["streak_data"] = {}
        for g_name in cfg.get("groups", {}):
            cfg["groups"][g_name]["members"] = []
        save_config(cfg)

        log_activity("AUTH", "User logged out. Session and friends cache cleared.")
        if verbose:
            print(t("logout_success"))
        return True
    except Exception as e:
        log_activity("ERROR", f"Logout error: {e}")
        if verbose:
            print(t("logout_failed", err=e))
        return False

# ==============================================================================
# Friends & Streak Scanning Engine
# ==============================================================================

def parse_snapchat_friends_protobuf(raw_bytes: bytes) -> dict:
    """Extract {display_name: username} from Snapchat SyncFriendData gRPC response."""
    if not raw_bytes or len(raw_bytes) < 10:
        return {}

    # Handle gRPC-web 5-byte frame prefix (1 byte flag + 4 bytes big-endian length)
    if raw_bytes[0] in (0, 1):
        import struct
        msg_len = struct.unpack(">I", raw_bytes[1:5])[0]
        data = raw_bytes[5:5+msg_len]
    else:
        data = raw_bytes

    def decode_varint(buf, pos):
        res = 0; shift = 0
        while pos < len(buf):
            b = buf[pos]; pos += 1
            res |= (b & 0x7f) << shift
            if not (b & 0x80): break
            shift += 7
        return res, pos

    def parse_chunks(buf):
        pos = 0; items = []
        while pos < len(buf):
            try:
                key, next_pos = decode_varint(buf, pos)
                fn = key >> 3; wt = key & 7
                if fn == 0 or wt not in (0, 1, 2, 5): break
                pos = next_pos
                if wt == 0:
                    v, pos = decode_varint(buf, pos); items.append((fn, wt, v))
                elif wt == 1: pos += 8
                elif wt == 2:
                    length, pos = decode_varint(buf, pos)
                    val = buf[pos:pos+length]; pos += length
                    items.append((fn, wt, val))
                elif wt == 5: pos += 4
            except Exception: break
        return items

    result = {}
    try:
        top = parse_chunks(data)
        for fn, wt, val in top:
            if wt == 2 and fn == 1:
                sub = parse_chunks(val)
                for f2, w2, v2 in sub:
                    if w2 == 2:
                        fields = parse_chunks(v2)
                        uname = ""
                        dname = ""
                        public_uname = ""
                        for f3, w3, v3 in fields:
                            if w3 == 2:
                                try:
                                    t = v3.decode("utf-8").strip()
                                    if f3 == 2 and not uname:
                                        uname = t
                                    elif f3 == 3 and not dname:
                                        dname = t
                                    elif f3 == 36 and not public_uname:
                                        public_uname = t
                                except Exception:
                                    pass
                        final_uname = public_uname or uname
                        if dname and final_uname:
                            result[dname] = final_uname
    except Exception:
        pass
    return result

def scan_snapchat_friends_using_page(page, verbose: bool = True, captured_usernames: dict = None) -> list:
    cfg = load_config()
    existing_contacts = cfg.get("contacts", [])
    found_contacts = []
    streak_data = cfg.get("streak_data", {})
    usernames = cfg.setdefault("usernames", {})
    if captured_usernames:
        usernames.update(captured_usernames)

    if verbose:
        print(t("scan_starting"))

    try:
        page.wait_for_timeout(4000)
    except Exception:
        return []

    ignore_names = {
        "chat", "new chat", "camera", "search", "stories", "spotlight", 
        "settings", "snapchat", "my story", "add friends", "log in", 
        "sign up", "terms", "privacy", "download", "lenses", "snapchat+",
        "browser not supported", "my ai", "view", "new snap", "delivered",
        "opened", "received", "tap to chat", "keep up with your friends",
        "learn more about enabling notifications", "team snapchat"
    }

    try:
        feed = page.locator('[aria-label="Friends Feed"], .ReactVirtualized__Grid').first
        if feed.is_visible(timeout=2000):
            try:
                feed.evaluate("el => el.scrollTop = 0")
            except Exception:
                pass
        page.wait_for_timeout(1000)

        for _ in range(16):
            if page.is_closed():
                break
            rows = page.locator('[role="listitem"]')
            count = rows.count()
            for i in range(count):
                try:
                    txt = rows.nth(i).inner_text().strip()
                    if not txt:
                        continue
                    lines = [l.strip() for l in txt.split("\n") if l.strip()]
                    if not lines:
                        continue
                    name = lines[1] if (len(lines[0]) <= 2 or lines[0] in ["😊", "🔥", "1", "2"]) and len(lines) > 1 else lines[0]
                    if name.lower() in ignore_names or len(name) > 35:
                        continue
                    has_streak = "🔥" in txt
                    m = re.search(r"(\d+)\s*🔥", txt)
                    st_count = m.group(1) if m else ""
                    
                    if name not in found_contacts:
                        found_contacts.append(name)
                        if st_count:
                            streak_data[name] = st_count
                        if verbose:
                            badge = f" ({st_count} 🔥)" if st_count else (" 🔥" if has_streak else "")
                            u = usernames.get(name)
                            u_badge = f" (@{u})" if u and u.lower() != name.lower() else ""
                            print(f"  • {name}{u_badge}{badge}")
                except Exception:
                    continue

            if feed.is_visible(timeout=500):
                feed.evaluate("el => el.scrollTop += 600")
            else:
                page.mouse.wheel(0, 600)
            page.wait_for_timeout(400)

    except Exception as e:
        if verbose:
            print(t("scan_error", err=e))

    if found_contacts:
        merged = sorted(list(set(existing_contacts + found_contacts)))
        cfg["contacts"] = merged
        cfg["streak_data"] = streak_data
        cfg["usernames"] = usernames
        save_config(cfg)
        log_activity("JOB", f"Contact scan completed: found {len(found_contacts)} friends.")
        if verbose:
            print(t("scan_found_summary", count=len(merged)))
    else:
        if verbose:
            print(t("scan_none_detected"))

    return found_contacts

def scan_snapchat_friends(verbose: bool = True) -> list:
    if not check_login_status():
        if verbose:
            print(t("scan_not_connected"))
        return []

    with sync_playwright() as p:
        try:
            context = launch_browser_context(p, headless=True)
            page = context.new_page()

            captured_usernames = {}
            def on_response(res):
                if "SyncFriendData" in res.url:
                    try:
                        b = res.body()
                        parsed = parse_snapchat_friends_protobuf(b)
                        if parsed:
                            captured_usernames.update(parsed)
                    except Exception:
                        pass

            page.on("response", on_response)
            page.goto(SNAPCHAT_WEB_URL, wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(5000)

            if not is_page_logged_in(page):
                if verbose:
                    print(t("scan_session_expired"))
                context.close()
                return []

            res = scan_snapchat_friends_using_page(page, verbose=verbose, captured_usernames=captured_usernames)
            context.close()
            return res
        except Exception as e:
            if verbose:
                print(t("scan_error", err=e))
            return []

# ==============================================================================
# Snap Sending Engine (Camera Capture & Dispatch)
# ==============================================================================

def take_and_send_snap(page, recipient_names: list, caption_text: str = "🔥") -> tuple:
    sent = []
    failed = []

    try:
        page.wait_for_timeout(3000)

        send_to_btn = None
        for attempt in range(1, 4):
            shutter = page.locator("button.fE2D5, button.gK0xL, button[class*='fE2D5'], button[class*='gK0xL']").first
            if not shutter.is_visible(timeout=1500):
                cam_btn = page.locator("button.qJKfS, div.Jq_5_ button, button:has-text('Click the Camera')").first
                if cam_btn.is_visible(timeout=1500):
                    cam_btn.click()
                    page.wait_for_timeout(2500)
                shutter = page.locator("button.fE2D5, button.gK0xL, button[class*='fE2D5'], button[class*='gK0xL']").first

            if shutter.is_visible(timeout=2000):
                shutter.click()
            else:
                page.mouse.click(724, 755)

            page.wait_for_timeout(2500)

            candidate = page.locator("button:has-text('Send To'), button.fGS78").first
            try:
                if candidate.is_visible(timeout=3000):
                    send_to_btn = candidate
                    break
            except Exception:
                pass

            log_activity("DEBUG", f"Shutter attempt #{attempt} waiting for 'Send To'...")
            page.wait_for_timeout(2000)

        if caption_text and send_to_btn:
            try:
                cap_btn = page.locator("button[title='Add a caption'], button.xHw7V:has-text('T'), button:has-text('T')").first
                if cap_btn.is_visible(timeout=1500):
                    cap_btn.click()
                    page.wait_for_timeout(600)
                    page.keyboard.type(caption_text)
                    page.keyboard.press("Enter")
                    page.wait_for_timeout(600)
            except Exception as e:
                log_activity("DEBUG", f"Caption add skipped/failed: {e}")

        if send_to_btn and send_to_btn.is_visible(timeout=3000):
            send_to_btn.click()
            page.wait_for_timeout(2500)
        else:
            raise RuntimeError("Button 'Send To' not found after 3 camera shutter attempts.")

        selected_via_shortcut = False
        streak_pill = page.locator("button:has-text('Streak')").first
        if streak_pill.is_visible(timeout=2500):
            streak_pill.click()
            page.wait_for_timeout(1500)
            select_btn = page.locator("button:has-text('Select')").first
            if select_btn.is_visible(timeout=2500):
                select_btn.click()
                page.wait_for_timeout(1500)
                selected_via_shortcut = True

        if not selected_via_shortcut:
            modal_container = page.locator(".Zoysu, .SZJHC, form.tvul8").first
            modal_search = modal_container.locator("input").first
            cfg = load_config()
            usernames = cfg.get("usernames", {})

            for target in recipient_names:
                try:
                    if modal_search.is_visible(timeout=1000):
                        uname = usernames.get(target)
                        search_term = uname if uname else target
                        modal_search.fill(search_term)
                        page.wait_for_timeout(1000)
                        item_checkbox = modal_container.locator("li, [role='listitem'], div[class*='Ewflr']").first
                        if not item_checkbox.is_visible(timeout=1000) and uname:
                            modal_search.fill(target)
                            page.wait_for_timeout(1000)
                            item_checkbox = modal_container.locator("li, [role='listitem'], div[class*='Ewflr']").first

                        if item_checkbox.is_visible(timeout=1500):
                            item_checkbox.click()
                            sent.append(target)
                            modal_search.fill("")
                            page.wait_for_timeout(int(get_action_delay() * 1000))
                        else:
                            failed.append(target)
                    else:
                        row = modal_container.locator(f"text='{target}'").first
                        if row.is_visible(timeout=1000):
                            row.click()
                            sent.append(target)
                        else:
                            failed.append(target)
                except Exception:
                    failed.append(target)

        send_btn = page.locator("button:has-text('Send'):not(:has-text('Send To')), button.TYX6O").first
        if send_btn.is_visible(timeout=4000):
            send_btn.click()
            page.wait_for_timeout(4000)
            if selected_via_shortcut:
                sent = list(recipient_names)
            log_activity("JOB", f"Snap dispatched to {len(sent)} contacts.")
        else:
            raise RuntimeError("Final 'Send' button not active or not found in modal.")

    except Exception as e:
        log_activity("JOB", f"Error during take_and_send_snap: {e}")
        failed = [r for r in recipient_names if r not in sent]
        sent = []

    return sent, failed

def get_active_recipients(cfg) -> list:
    contacts = cfg.get("contacts", [])
    if "recipients" in cfg:
        return [c for c in contacts if c in cfg["recipients"]]
    if cfg.get("mode") == "groups":
        group_members = set()
        for g in cfg.get("groups", {}).values():
            group_members.update(g.get("members", []))
        return [c for c in contacts if c in group_members]
    excludes = cfg.get("select_all", {}).get("exclude", [])
    return [c for c in contacts if c not in excludes]

def run_send_streak(force: bool = False, verbose: bool = True) -> dict:
    ensure_dirs()
    clean_expired_logs(retention_days=3)
    today_str = datetime.now().strftime("%Y-%m-%d")
    state = load_state()

    if not force and state.get("last_date") == today_str and state.get("success"):
        msg = t("streak_skipped_today", date=today_str, time=state.get('last_time'))
        if verbose:
            print(f"\n[i] {msg}")
        return {"status": "skipped", "message": msg}

    cfg = load_config()
    target_recipients = get_active_recipients(cfg)
    mode = "checklist" if "recipients" in cfg else cfg.get("mode", "all")

    if not target_recipients:
        msg = t("streak_no_targets")
        if verbose:
            print(f"\n[!] {msg}")
        return {"status": "no_targets", "message": msg}

    if not wait_for_internet(timeout=180, verbose=verbose):
        err = t("streak_offline")
        log_activity("JOB", err)
        send_notification(t("notif_streak_fail_title"), err, success=False)
        return {"status": "offline", "message": err}

    if verbose:
        print("\n" + "=" * 65)
        print(t("streak_starting_banner", count=len(target_recipients)))
        print(f"   Mode: {mode.upper()} | Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 65)

    with sync_playwright() as p:
        try:
            context = launch_browser_context(p, headless=True)
            page = context.new_page()
            page.goto(SNAPCHAT_WEB_URL, wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(5000)

            if not is_page_logged_in(page):
                err_msg = t("streak_session_expired")
                log_activity("JOB", err_msg)
                save_state(False, 0, len(target_recipients), err_msg, session_expired=True)
                if os.path.exists(STORAGE_STATE_FILE):
                    try:
                        os.remove(STORAGE_STATE_FILE)
                    except Exception:
                        pass
                send_notification(t("notif_streak_fail_title"), err_msg, success=False)
                context.close()
                return {"status": "error", "message": err_msg, "is_auth_error": True}

            default_cap = cfg.get("default_caption", "🔥")
            resolved_cap = format_caption(default_cap, target_recipients[0] if target_recipients else ("Friend" if CURRENT_LANG == "en" else "Teman"))

            sent, failed = take_and_send_snap(page, target_recipients, caption_text=resolved_cap)
            context.close()

            success = len(sent) > 0 and len(failed) == 0
            summary = f"Sent: {len(sent)} | Failed: {len(failed)}" if CURRENT_LANG == "en" else f"Terkirim: {len(sent)} | Gagal: {len(failed)}"

            save_state(success, len(sent), len(failed), summary)
            log_activity("JOB", f"Streak execution completed. {summary}")

            names_preview = ", ".join(sent[:4]) + ("..." if len(sent) > 4 else "")
            notif_text = f"Sent: {len(sent)} | Failed: {len(failed)}\nRecipients: {names_preview or 'None'}"
            send_notification(t("notif_streak_success_title") if success else t("notif_streak_fail_title"), notif_text, success=success)

            if verbose:
                print("\n" + "=" * 65)
                print(t("streak_exec_result", summary=summary))
                print("=" * 65 + "\n")

            if success:
                return {"status": "success", "sent": len(sent), "failed": len(failed)}
            else:
                return {"status": "error", "sent": len(sent), "failed": len(failed), "message": summary}

        except Exception as e:
            err_msg = f"Playwright Exception: {e}"
            log_activity("JOB", err_msg)
            save_state(False, 0, len(target_recipients), err_msg)
            send_notification(t("notif_streak_fail_title"), err_msg, success=False)
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

    contacts = cfg.get("contacts", [])
    active_recips = get_active_recipients(cfg)
    sched_active, sched_desc = get_scheduler_status()

    is_logged_in = check_login_status()
    login_badge = t("dash_status_valid") if is_logged_in else t("dash_status_unauthed")

    status_today = t("dash_today_pending")
    if state.get("last_date") == today_str:
        status_today = t("dash_today_sent") if state.get("success") else t("dash_today_failed")

    sched_badge = "🟢 " + sched_desc if sched_active else "⚪ " + sched_desc

    print("==================================================================")
    print(t("dash_title"))
    print("==================================================================")
    print(f"{t('dash_account_status')}{login_badge}")
    print(f"{t('dash_today_status')}{status_today}")
    pace_name = cfg.get("safety", {}).get("pace", "normal").capitalize()
    print(f"{t('dash_recipient_mode')}{len(active_recips)} active / {len(contacts)} total (Checklist) | ⚡ Pace: {pace_name}")
    print(f"{t('dash_schedule')}{sched_badge}")
    print("==================================================================")

    if not is_logged_in:
        print("\n" + "╔" + "═" * 64 + "╗")
        print(f"║  {t('dash_warn_unauthed_title'):<60}  ║")
        print(f"║  {t('dash_warn_unauthed_desc1'):<60}  ║")
        print(f"║  {t('dash_warn_unauthed_desc2'):<60}  ║")
        print("║                                                                ║")
        print(f"║  {t('dash_warn_unauthed_desc3'):<60}  ║")
        print("╚" + "═" * 64 + "╝\n")

def menu_manage_recipients():
    while True:
        cfg = load_config()
        contacts = cfg.get("contacts", [])
        active_recipients = get_active_recipients(cfg)
        usernames = cfg.get("usernames", {})
        streak_data = cfg.get("streak_data", {})

        def format_recipient_choice(name):
            u = usernames.get(name)
            st = streak_data.get(name)
            st_badge = f" ({st} 🔥)" if st else ""
            if u and u.lower() != name.lower():
                return f"{name} (@{u}){st_badge}"
            elif u:
                return f"@{u}{st_badge}"
            return f"{name}{st_badge}"

        choices = [
            Choice(
                f"☑️  Select Recipients ({len(active_recipients)} of {len(contacts)} active)" if CURRENT_LANG == "en" else f"☑️  Pilih Penerima ({len(active_recipients)} dari {len(contacts)} aktif)",
                value="checklist"
            ),
            Choice("⚡ Set Snap Dispatch Speed (Pace)" if CURRENT_LANG == "en" else "⚡ Atur Kecepatan Pengiriman Snap", value="speed"),
            Choice("✏️  Edit / Set Friend Username" if CURRENT_LANG == "en" else "✏️  Atur / Ubah Username Teman", value="edit_username"),
            Choice("💬 Edit Default Caption" if CURRENT_LANG == "en" else "💬 Ubah Caption Default", value="caption"),
            Choice("👁️  Preview Recipient List" if CURRENT_LANG == "en" else "👁️  Lihat Daftar Penerima", value="preview"),
            Separator(),
            Choice(t("recip_back"), value="back")
        ]

        action = questionary.select(
            "Manage Streak Recipients:" if CURRENT_LANG == "en" else "Kelola Penerima Streak:",
            choices=choices
        ).ask()

        if action in ("back", None):
            break
        elif action == "speed":
            menu_safety_settings()
        elif action == "checklist":
            if not contacts:
                print("\n[!] No contacts saved. Please scan friends in Account menu first.\n" if CURRENT_LANG == "en" else "\n[!] Belum ada kontak tersimpan. Silakan Pindai Teman di Menu Akun terlebih dahulu.\n")
                questionary.press_any_key_to_continue(t("press_key_continue")).ask()
                continue

            choices_c = [
                Choice(title=format_recipient_choice(c), value=c, checked=(c in active_recipients))
                for c in contacts
            ]

            print("\n💡 Controls: [Space] Toggle, [a] Select All / Invert, [Enter] Save\n" if CURRENT_LANG == "en" else "\n💡 Navigasi: [Spasi] Pilih, [a] Pilih Semua, [Enter] Simpan\n")

            selected = questionary.checkbox(
                "Select friends who will receive streaks:" if CURRENT_LANG == "en" else "Pilih teman yang akan menerima streak:",
                choices=choices_c,
                instruction="(Space: toggle, a: all, Enter: save)" if CURRENT_LANG == "en" else "(Spasi: pilih, a: semua, Enter: simpan)"
            ).ask()

            if selected is not None:
                cfg["recipients"] = list(selected)
                save_config(cfg)
                print(f"\n[✓] Saved! {len(selected)} of {len(contacts)} friends selected.\n" if CURRENT_LANG == "en" else f"\n[✓] Tersimpan! {len(selected)} dari {len(contacts)} teman dipilih.\n")
                questionary.press_any_key_to_continue(t("press_key_continue")).ask()

        elif action == "edit_username":
            if not contacts:
                print("\n[!] No friends saved.\n" if CURRENT_LANG == "en" else "\n[!] Belum ada teman tersimpan.\n")
                questionary.press_any_key_to_continue(t("press_key_continue")).ask()
                continue
            friend_choices = [
                Choice(title=format_recipient_choice(c), value=c)
                for c in contacts
            ] + [Separator(), Choice(t("recip_back"), value="back")]
            chosen = questionary.select(
                "Select friend to set/edit username:" if CURRENT_LANG == "en" else "Pilih teman untuk atur/ubah username:",
                choices=friend_choices
            ).ask()
            if chosen and chosen != "back":
                current_u = usernames.get(chosen, "")
                new_u = questionary.text(
                    f"Username for '{chosen}':" if CURRENT_LANG == "en" else f"Username untuk '{chosen}':",
                    default=current_u
                ).ask()
                if new_u is not None:
                    new_u = new_u.strip().lstrip("@")
                    if new_u:
                        cfg.setdefault("usernames", {})[chosen] = new_u
                    elif chosen in cfg.get("usernames", {}):
                        del cfg["usernames"][chosen]
                    save_config(cfg)
                    print("\n[✓] Username updated!\n" if CURRENT_LANG == "en" else "\n[✓] Username berhasil diperbarui!\n")
                    questionary.press_any_key_to_continue(t("press_key_continue")).ask()

        elif action == "caption":
            curr_def = cfg.get("default_caption", "🔥")
            new_def = questionary.text("Default Snap Caption:" if CURRENT_LANG == "en" else "Caption Default Snap:", default=curr_def).ask()
            if new_def:
                cfg["default_caption"] = new_def
                save_config(cfg)
                print("\n[✓] Saved!\n")

        elif action == "preview":
            print("\n" + "=" * 60)
            print("📋 ACTIVE RECIPIENTS (Will receive streak 🔥):" if CURRENT_LANG == "en" else "📋 PENERIMA AKTIF (Menerima streak 🔥):")
            print("=" * 60)
            for idx, c in enumerate(contacts, 1):
                status = "✅ YES" if c in active_recipients else "❌ SKIP"
                disp = format_recipient_choice(c)
                print(f" {idx:2d}. {disp:<38} [{status}]")
            print("=" * 60 + "\n")
            questionary.press_any_key_to_continue(t("press_key_continue")).ask()

def menu_safety_settings():
    while True:
        cfg = load_config()
        safety = cfg.setdefault("safety", {})
        pace = safety.get("pace", "normal")
        safe_hours = safety.get("safe_hours", {"enabled": True, "start": 7, "end": 23})
        headless = cfg.get("headless", True)

        pace_label = {
            "fast": "🚀 Fast (1.2 - 2.0s)" if CURRENT_LANG == "en" else "🚀 Cepat (1.2 - 2.0 detik)",
            "normal": "⚡ Normal / Natural (2.5 - 4.0s)" if CURRENT_LANG == "en" else "⚡ Normal / Natural (2.5 - 4.0 detik)",
            "relaxed": "🛡️ Relaxed / Anti-Limit (5.0 - 7.5s)" if CURRENT_LANG == "en" else "🛡️ Santai / Anti-Limit (5.0 - 7.5 detik)"
        }.get(pace, "⚡ Normal (2.5 - 4.0s)")

        sh_status = (f"🟢 Active ({safe_hours.get('start', 7):02d}:00 - {safe_hours.get('end', 23):02d}:00)" if CURRENT_LANG == "en" else f"🟢 Aktif ({safe_hours.get('start', 7):02d}:00 - {safe_hours.get('end', 23):02d}:00)") if safe_hours.get("enabled", True) else ("⚪ Disabled" if CURRENT_LANG == "en" else "⚪ Nonaktif")
        hl_status = ("🟢 Background (Headless)" if CURRENT_LANG == "en" else "🟢 Latar Belakang (Headless)") if headless else ("🖥️ Visible Window" if CURRENT_LANG == "en" else "🖥️ Jendela Terlihat")

        choices = [
            Choice(f"⚡ {'Dispatch Speed / Pace:' if CURRENT_LANG == 'en' else 'Kecepatan Pengiriman:'} {pace_label}", value="change_pace"),
            Choice(f"🌙 {'Safe Dispatch Hours:' if CURRENT_LANG == 'en' else 'Batas Jam Aman:'} {sh_status}", value="toggle_safe_hours"),
            Choice(f"🖥️  {'Browser Window Mode:' if CURRENT_LANG == 'en' else 'Mode Jendela Browser:'} {hl_status}", value="toggle_headless"),
            Separator(),
            Choice(t("recip_back"), value="back")
        ]

        action = questionary.select(
            "⚙️  Dispatch Speed & Safety Settings:" if CURRENT_LANG == "en" else "⚙️  Pengaturan Kecepatan & Keamanan Pengiriman:",
            choices=choices
        ).ask()

        if action in ("back", None):
            break

        if action == "change_pace":
            new_pace = questionary.select(
                "Select snap dispatch speed / delay between actions:" if CURRENT_LANG == "en" else "Pilih kecepatan jeda pengiriman snap:",
                choices=[
                    Choice("⚡ Normal / Natural (2.5 - 4.0s) [Recommended]" if CURRENT_LANG == "en" else "⚡ Normal / Natural (Jeda 2.5 - 4.0 detik) [Direkomendasikan]", value="normal"),
                    Choice("🚀 Fast (1.2 - 2.0s) [Faster dispatch]" if CURRENT_LANG == "en" else "🚀 Cepat (Jeda 1.2 - 2.0 detik) [Pengiriman lebih cepat]", value="fast"),
                    Choice("🛡️ Relaxed (5.0 - 7.5s) [Maximum safety / anti-limit]" if CURRENT_LANG == "en" else "🛡️ Santai (Jeda 5.0 - 7.5 detik) [Aman maksimal anti-limit]", value="relaxed")
                ]
            ).ask()
            if new_pace:
                cfg.setdefault("safety", {})["pace"] = new_pace
                save_config(cfg)
                log_activity("CONFIG", f"Snap dispatch speed updated to: {new_pace.upper()}")
                print(f"\n[✓] {'Dispatch speed updated to:' if CURRENT_LANG == 'en' else 'Kecepatan pengiriman diubah ke:'} {new_pace.upper()}\n")
                questionary.press_any_key_to_continue(t("press_key_continue")).ask()

        elif action == "toggle_safe_hours":
            is_enabled = safe_hours.get("enabled", True)
            toggle_choice = questionary.select(
                "Safe Hours Settings:" if CURRENT_LANG == "en" else "Pengaturan Batas Jam Aman:",
                choices=[
                    Choice(f"{'⚪ Disable' if is_enabled else '🟢 Enable'} Safe Hours" if CURRENT_LANG == "en" else f"{'⚪ Matikan' if is_enabled else '🟢 Aktifkan'} Batas Jam Aman", value="toggle"),
                    Choice("🕒 Change Safe Hours Range" if CURRENT_LANG == "en" else "🕒 Ubah Rentang Jam Aman", value="edit_hours"),
                    Choice("🔙 Cancel" if CURRENT_LANG == "en" else "🔙 Batal", value="back")
                ]
            ).ask()
            if toggle_choice == "toggle":
                safe_hours["enabled"] = not is_enabled
                cfg.setdefault("safety", {})["safe_hours"] = safe_hours
                save_config(cfg)
                status = "ENABLED" if safe_hours["enabled"] else "DISABLED"
                log_activity("CONFIG", f"Safe hours changed to: {status}")
                print(f"\n[✓] Safe hours: {status}\n")
                questionary.press_any_key_to_continue(t("press_key_continue")).ask()
            elif toggle_choice == "edit_hours":
                s_str = questionary.text("Start hour (0-23):" if CURRENT_LANG == "en" else "Mulai jam berapa (0-23):", default=str(safe_hours.get("start", 7))).ask()
                e_str = questionary.text("End hour (0-23):" if CURRENT_LANG == "en" else "Sampai jam berapa (0-23):", default=str(safe_hours.get("end", 23))).ask()
                try:
                    s_int = int(s_str)
                    e_int = int(e_str)
                    if 0 <= s_int <= 23 and 0 <= e_int <= 23:
                        safe_hours["start"] = s_int
                        safe_hours["end"] = e_int
                        cfg.setdefault("safety", {})["safe_hours"] = safe_hours
                        save_config(cfg)
                        print(f"\n[✓] Safe hours range updated: {s_int:02d}:00 - {e_int:02d}:00\n")
                        questionary.press_any_key_to_continue(t("press_key_continue")).ask()
                except ValueError:
                    print("\n[!] Invalid hour format.\n")

        elif action == "toggle_headless":
            cfg["headless"] = not headless
            save_config(cfg)
            status = "HEADLESS (Background)" if cfg["headless"] else "VISIBLE WINDOW"
            log_activity("CONFIG", f"Browser mode changed to: {status}")
            print(f"\n[✓] Browser display mode: {status}\n")
            questionary.press_any_key_to_continue(t("press_key_continue")).ask()

def show_telegram_guide():
    print("\n" + "=" * 62)
    if CURRENT_LANG == "en":
        print("📖 Telegram Bot Quick Integration Guide (1 Minute):")
        print("=" * 62)
        print("1. Open Telegram on your Phone or Laptop.")
        print("2. Search for @BotFather (verified official bot).")
        print("3. Send /newbot command and follow instructions:")
        print("   -> Set bot display name (e.g., 'Snapchat Helper')")
        print("   -> Set bot username ending in 'bot' (e.g., 'sam_snap_bot')")
        print("   -> BotFather will provide your HTTP API Token.")
        print("4. Get your personal Chat ID:")
        print("   -> Search @userinfobot on Telegram, click Start.")
        print("   -> It immediately replies with your 'Id: 123456789' (Chat ID).")
        print("5. CRITICAL: Open your created bot (step 3) and click START!")
    else:
        print("📖 Panduan Singkat Integrasi Telegram (Cuma 1 Menit):")
        print("=" * 62)
        print("1. Buka aplikasi Telegram di HP / Laptop kamu.")
        print("2. Cari @BotFather (bot resmi centang biru dari Telegram).")
        print("3. Kirim perintah /newbot dan ikuti instruksi:")
        print("   -> Masukkan nama tampilan bot (misal: 'Streak Helper')")
        print("   -> Masukkan username bot (harus berakhiran 'bot', misal: 'sam_snap_bot')")
        print("   -> BotFather akan memberikan HTTP API Token.")
        print("4. Ambil Chat ID pribadi kamu:")
        print("   -> Cari @userinfobot di Telegram, klik Start.")
        print("   -> Bot tersebut langsung membalas nomor 'Id: 123456789' (Chat ID).")
        print("5. PENTING: Buka bot buatanmu (dari langkah 3) lalu klik tombol START!")
    print("=" * 62 + "\n")
    questionary.press_any_key_to_continue(t("press_key_continue")).ask()

def menu_notifications():
    while True:
        cfg = load_config()
        notifs = cfg.setdefault("notifications", {})
        tg = notifs.setdefault("telegram", {})
        dc = notifs.setdefault("discord", {})

        choices = [
            Choice(t("notif_telegram", status=t('status_active_upper') if tg.get('enabled') else t('status_inactive_upper')), value="telegram"),
            Choice(t("notif_discord", status=t('status_active_upper') if dc.get('enabled') else t('status_inactive_upper')), value="discord"),
            Choice(t("notif_test_all"), value="test_all"),
            Separator(),
            Choice(t("notif_back"), value="back")
        ]

        action = questionary.select(t("notif_menu_title"), choices=choices).ask()
        if action in ("back", None):
            break
        elif action == "telegram":
            t_act = questionary.select("Telegram Settings:" if CURRENT_LANG == "en" else "Pengaturan Telegram:", choices=[
                "🔄 Toggle Enable/Disable" if CURRENT_LANG == "en" else "🔄 Aktifkan / Nonaktifkan",
                "✏️  Configure Bot Token & Chat ID" if CURRENT_LANG == "en" else "✏️  Atur Token & Chat ID",
                "🔔 Test Send Notification" if CURRENT_LANG == "en" else "🔔 Tes Kirim Notifikasi",
                "📖 Guide" if CURRENT_LANG == "en" else "📖 Panduan Singkat",
                "🔙 Back" if CURRENT_LANG == "en" else "🔙 Kembali"
            ]).ask()
            if t_act and "Toggle" in t_act:
                tg["enabled"] = not tg.get("enabled", False)
                save_config(cfg)
            elif t_act and "Configure" in t_act or (t_act and "Atur" in t_act):
                token = questionary.text("Bot Token:", default=tg.get("bot_token", "")).ask()
                chat_id = questionary.text("Chat ID:", default=tg.get("chat_id", "")).ask()
                if token: tg["bot_token"] = token.strip()
                if chat_id: tg["chat_id"] = chat_id.strip()
                if tg.get("bot_token") and tg.get("chat_id"): tg["enabled"] = True
                save_config(cfg)
            elif t_act and "Test" in t_act or (t_act and "Tes" in t_act):
                ok, msg = send_telegram_notification(tg.get("bot_token", ""), tg.get("chat_id", ""), "Snapchat Streak Test", "Test alert from Snapchat Streak! 🎉", True)
                print(f"[{'✓' if ok else '!'}] {msg}")
                questionary.press_any_key_to_continue(t("press_key_continue")).ask()
            elif t_act and "Guide" in t_act or (t_act and "Panduan" in t_act):
                show_telegram_guide()

        elif action == "discord":
            d_act = questionary.select("Discord Settings:" if CURRENT_LANG == "en" else "Pengaturan Discord:", choices=[
                "🔄 Toggle Enable/Disable" if CURRENT_LANG == "en" else "🔄 Aktifkan / Nonaktifkan",
                "✏️  Configure Webhook URL" if CURRENT_LANG == "en" else "✏️  Atur Webhook URL",
                "🔔 Test Send Notification" if CURRENT_LANG == "en" else "🔔 Tes Kirim Notifikasi",
                "🔙 Back" if CURRENT_LANG == "en" else "🔙 Kembali"
            ]).ask()
            if d_act and "Toggle" in d_act:
                dc["enabled"] = not dc.get("enabled", False)
                save_config(cfg)
            elif d_act and "Configure" in d_act or (d_act and "Atur" in d_act):
                url = questionary.text("Discord Webhook URL:", default=dc.get("webhook_url", "")).ask()
                if url: dc["webhook_url"] = url.strip(); dc["enabled"] = True
                save_config(cfg)
            elif d_act and "Test" in d_act or (d_act and "Tes" in d_act):
                ok, msg = send_discord_notification(dc.get("webhook_url", ""), "Snapchat Streak Test", "Test alert from Snapchat Streak! 🎉", True)
                print(f"[{'✓' if ok else '!'}] {msg}")
                questionary.press_any_key_to_continue(t("press_key_continue")).ask()

        elif action == "test_all":
            print(t("notif_test_sending"))
            send_notification("Snapchat Streak Test", "All active notifications delivered successfully! 🎉", True)
            print(t("notif_test_done"))
            questionary.press_any_key_to_continue(t("press_key_continue")).ask()

def menu_account():
    while True:
        is_logged_in = check_login_status()
        contacts = load_config().get("contacts", [])
        status_label = t("dash_status_valid") if is_logged_in else t("dash_status_unauthed")

        choices = [
            Choice(t("account_opt_scan", count=len(contacts)), value="scan"),
            Choice(t("account_opt_login"), value="login"),
            Choice(t("account_opt_check", status=status_label), value="check"),
            Choice(t("account_opt_logout"), value="logout"),
            Separator(),
            Choice(t("account_opt_back"), value="back")
        ]

        action = questionary.select(t("account_menu_title"), choices=choices).ask()
        if action in ("back", None):
            break
        elif action == "scan":
            scan_snapchat_friends(verbose=True)
            questionary.press_any_key_to_continue(t("press_key_return")).ask()
        elif action == "login":
            interactive_login()
            questionary.press_any_key_to_continue(t("press_key_return")).ask()
        elif action == "check":
            ok = check_login_status()
            print(f"[{'✓' if ok else '!'}] Status: {t('dash_status_valid') if ok else t('dash_status_unauthed')}\n")
            questionary.press_any_key_to_continue(t("press_key_return")).ask()
        elif action == "logout":
            confirm = questionary.confirm(t("logout_confirm"), default=False).ask()
            if confirm:
                logout_snapchat(verbose=True)
            questionary.press_any_key_to_continue(t("press_key_return")).ask()

def menu_manage_scheduler():
    while True:
        is_active, desc = get_scheduler_status()
        cfg = load_config()
        sched = cfg.get("schedule", {"hour": 9, "minute": 0})
        time_str = f"{sched.get('hour', 9):02d}:{sched.get('minute', 0):02d}"

        choices = [
            Choice(t("sched_opt_install", time=time_str), value="install"),
            Choice(t("sched_opt_change_time", time=time_str), value="change_time"),
            Choice(t("sched_opt_remove"), value="remove"),
            Separator(),
            Choice("🔙 Back to Main Menu" if CURRENT_LANG == "en" else "🔙 Kembali ke Menu Utama", value="back")
        ]

        action = questionary.select(
            t("sched_menu_title", os=OS_NAME, badge='🟢 ' + desc if is_active else '⚪ ' + desc),
            choices=choices
        ).ask()

        if action in ("back", None):
            break
        elif action == "install":
            install_scheduler()
            questionary.press_any_key_to_continue(t("press_key_continue")).ask()
        elif action == "change_time":
            new_time = questionary.text(t("sched_prompt_new_time"), default=time_str).ask()
            if new_time and ":" in new_time:
                try:
                    h, m = map(int, new_time.split(":", 1))
                    if 0 <= h <= 23 and 0 <= m <= 59:
                        cfg["schedule"] = {"hour": h, "minute": m}
                        save_config(cfg)
                        print(t("sched_time_changed", time=f"{h:02d}:{m:02d}"))
                        if is_active:
                            install_scheduler()
                    else:
                        print(t("sched_time_invalid"))
                except ValueError:
                    print(t("sched_time_invalid"))
            questionary.press_any_key_to_continue(t("press_key_continue")).ask()
        elif action == "remove":
            remove_scheduler()
            questionary.press_any_key_to_continue(t("press_key_continue")).ask()

def menu_view_logs():
    while True:
        choices = [
            Choice(t("logs_opt_all"), value="all"),
            Choice(t("logs_opt_job"), value="job"),
            Choice(t("logs_opt_config"), value="config"),
            Choice(t("logs_opt_clean"), value="clean"),
            Separator(),
            Choice(t("logs_opt_back"), value="back")
        ]

        act = questionary.select(t("logs_menu_title"), choices=choices).ask()
        if act in ("back", None):
            break
        elif act in ("all", "job", "config"):
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
            print(f"📜 LOGS ({'All' if not cat else cat}):" if CURRENT_LANG == "en" else f"📜 RIWAYAT AKTIVITAS & LOG ({'Semua' if not cat else cat}):")
            print("=" * 70)
            if not all_entries:
                print("  (No logs recorded)")
            else:
                for entry in all_entries[-40:]:
                    print(f"  {entry}")
            print("=" * 70 + "\n")
            questionary.press_any_key_to_continue(t("press_key_continue")).ask()

        elif act == "clean":
            if questionary.confirm(t("logs_clean_confirm")).ask():
                for f in os.listdir(LOG_DIR):
                    if f.startswith("activity_"):
                        try:
                            os.remove(os.path.join(LOG_DIR, f))
                        except Exception:
                            pass
                print(t("logs_cleaned"))
                questionary.press_any_key_to_continue(t("press_key_continue")).ask()

def menu_language():
    cfg = load_config()
    choices = [
        Choice(t("lang_opt_en"), value="en"),
        Choice(t("lang_opt_id"), value="id"),
        Separator(),
        Choice(t("lang_opt_back"), value="back")
    ]
    chosen = questionary.select(t("lang_menu_title"), choices=choices).ask()
    if chosen and chosen != "back":
        cfg["language"] = chosen
        save_config(cfg)
        set_language(chosen)
        lang_name = "English" if chosen == "en" else "Bahasa Indonesia"
        print(t("lang_changed", lang=lang_name))

def interactive_hub():
    while True:
        cfg = load_config()
        set_language(cfg.get("language", "en"))
        print_dashboard()
        is_logged_in = check_login_status()

        sched = cfg.get("schedule", {"hour": 9, "minute": 0})
        time_str = f"{sched.get('hour', 9):02d}:{sched.get('minute', 0):02d}"
        lang_name = "English" if CURRENT_LANG == "en" else "Bahasa Indonesia"

        if not is_logged_in:
            choices = [
                Choice(t("menu_opt_login_req"), value="login"),
                Choice(t("menu_opt_run_need_login"), value="run"),
                Choice(t("menu_opt_recipients"), value="recipients"),
                Choice(t("menu_opt_speed"), value="safety"),
                Choice(t("menu_opt_scheduler", time=time_str), value="scheduler"),
                Choice(t("menu_opt_logs"), value="logs"),
                Choice(t("menu_opt_notifications"), value="notifications"),
                Choice(t("menu_opt_check_update"), value="check_update"),
                Choice(t("menu_opt_lang", current=lang_name), value="language"),
                Separator(),
                Choice(t("menu_opt_exit"), value="exit")
            ]
        else:
            choices = [
                Choice(t("menu_opt_run"), value="run"),
                Choice(t("menu_opt_recipients"), value="recipients"),
                Choice(t("menu_opt_speed"), value="safety"),
                Choice(t("menu_opt_scheduler", time=time_str), value="scheduler"),
                Choice(t("menu_opt_logs"), value="logs"),
                Choice(t("menu_opt_account"), value="account"),
                Choice(t("menu_opt_notifications"), value="notifications"),
                Choice(t("menu_opt_check_update"), value="check_update"),
                Choice(t("menu_opt_lang", current=lang_name), value="language"),
                Separator(),
                Choice(t("menu_opt_exit"), value="exit")
            ]

        action = questionary.select(
            t("menu_select"),
            choices=choices,
            use_indicator=True
        ).ask()

        if action in ("exit", None):
            print(t("goodbye"))
            break
        elif action == "login":
            interactive_login()
            questionary.press_any_key_to_continue(t("press_key_return")).ask()
        elif action == "run":
            if not check_login_status():
                print("\n[!] Not logged in to Snapchat." if CURRENT_LANG == "en" else "\n[!] Anda belum login ke akun Snapchat.")
                do_login = questionary.confirm("Open browser window to log in now?" if CURRENT_LANG == "en" else "Buka jendela browser untuk login sekarang?", default=True).ask()
                if do_login:
                    interactive_login()
            else:
                run_send_streak(force=True, verbose=True)
                questionary.press_any_key_to_continue(t("press_key_return")).ask()
        elif action == "recipients":
            menu_manage_recipients()
        elif action == "safety":
            menu_safety_settings()
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
        elif action == "language":
            menu_language()

# ==============================================================================
# CLI Entry Point & Background Worker
# ==============================================================================

def run_cron_job(max_retries: int = 1, retry_delay: int = 40):
    log_activity("SYSTEM", "Snapchat Streak auto-worker triggered by scheduler.")

    state = load_state()
    today_str = datetime.now().strftime("%Y-%m-%d")

    # If streak already succeeded today, skip
    if state.get("last_date") == today_str and state.get("success"):
        log_activity("SYSTEM", f"Cron check: Streak today ({today_str}) already sent. Done.")
        return

    # If session is marked as expired, do not keep retrying or spamming notifications every hour
    if state.get("session_expired"):
        log_activity("SYSTEM", "Cron skipped: Snapchat login session expired. Please log in via terminal menu.")
        return

    if not wait_for_internet(timeout=180, verbose=False):
        err = "Cron cancelled: Laptop not connected to internet after 180s."
        log_activity("SYSTEM", err)
        return

    is_safe, desc = is_within_safe_hours()
    if not is_safe:
        log_activity("SYSTEM", f"Cron postponed: Outside safe hours {desc}.")
        return

    for attempt in range(1, max_retries + 1):
        res = run_send_streak(force=False, verbose=False)
        st = res.get("status")
        if st in ("success", "skipped"):
            log_activity("SYSTEM", f"Cron completed on attempt #{attempt}: {st}")
            return
        else:
            msg = res.get("message", st)
            log_activity("SYSTEM", f"Cron attempt #{attempt} failed ({msg}).")
            if res.get("is_auth_error") or "login session expired" in str(msg).lower():
                log_activity("SYSTEM", "Cron aborted: Login required. Will not retry until logged in.")
                return
            if attempt < max_retries:
                log_activity("SYSTEM", f"Retrying in {retry_delay}s...")
                time.sleep(retry_delay)

    log_activity("SYSTEM", f"Cron finished after {max_retries} attempts.")

def main():
    parser = argparse.ArgumentParser(description="Snapchat Streak Auto-Saver Hub")
    parser.add_argument("--cron", action="store_true", help="Background automation mode for LaunchAgent / Task Scheduler")
    parser.add_argument("--force", action="store_true", help="Force send even if streak already sent today")
    parser.add_argument("--scan", action="store_true", help="Scan Snapchat friends and exit")
    parser.add_argument("--login", action="store_true", help="Launch interactive login window")
    parser.add_argument("--logout", action="store_true", help="Logout Snapchat and clear saved session and contacts")
    parser.add_argument("--lang", "--language", choices=["en", "id"], help="Set UI language (en/id)")
    args = parser.parse_args()

    cfg = load_config()
    if args.lang:
        set_language(args.lang)
    else:
        set_language(cfg.get("language", "en"))

    if args.cron:
        run_cron_job()
    elif args.scan:
        scan_snapchat_friends(verbose=True)
    elif args.login:
        interactive_login()
    elif args.logout:
        logout_snapchat(verbose=True)
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
