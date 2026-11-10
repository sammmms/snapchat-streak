# 👻 snapchat-streak — Snapchat Streak Auto-Saver & Helper Hub

<p align="center">
  <img src="assets/banner.png" alt="snapchat-streak Banner" width="100%" />
</p>

[![Python 3](https://img.shields.io/badge/Python-3.8+-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg?style=flat-square)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-macOS%20%7C%20Linux%20%7C%20Windows-lightgrey?style=flat-square)](#)
[![Interface](https://img.shields.io/badge/UI-100%25%20Interactive%20Cursor%20TUI-FFFC00?style=flat-square&logoColor=black)](#)

A zero-hassle, cross-platform **100% interactive cursor CLI hub** and daily streak maintenance assistant for **Snapchat**.

Modeled around the same simple philosophy as **tiktok-streak** and **hoyolab-checkin**: **"Run and pick options easily."** No manual python execution commands, no JSON hacking, full arrow-key cursor navigation, multi-select checkboxes, in-app auto-updating, and automatic background snap streak sending with wake-up catch-up whenever you want it.

---

## 💡 Mengapa Butuh Snapchat Streak Auto-Saver?

Berbeda dengan TikTok di mana pesan teks atau stiker biasa sudah dihitung untuk mempertahankan streak, **Snapchat mewajibkan pengiriman SNAP (Foto / Video)** setiap 24 jam untuk menjaga api streak (🔥) tetap hidup. Mengirim chat teks saja **TIDAK** memperpanjang streak di Snapchat!

`snapchat-streak` memecahkan masalah ini dengan mengotomatiskan pengambilan Snap foto (didukung *synthetic fake media stream*) dan mengirimkannya ke teman-teman target Anda di `web.snapchat.com` secara berkala setiap hari.

---

## 🌟 Fitur Utama

- **100% Interactive Cursor TUI**: Tampilan visual terminal modern dengan navigasi panah (`↑` / `↓`), pilihan checklist spasi (`Space`), dan `Enter` untuk konfirmasi. Cukup ketik `snapchat-streak` di terminal!
- **Automated Snap Shutter & Dispatch**: Mengambil Snap foto secara otomatis via browser Playwright terisolasi dan mengirimkannya ke kontak teman target.
- **Deteksi Teman & Status Streak**: Memindai teman di Snapchat Web dan mendeteksi siapa saja yang memiliki api streak aktif (🔥).
- **Template Caption Dinamis**:
  - Dukungan variabel: `{name}`, `{first_name}`, `{time_greeting}` (Pagi/Siang/Sore/Malam), `{day}`, dan `{date}`.
  - Pool variasi caption acak dan personalisasi khusus per kontak.
- **Ritme Natural & Anti-Deteksi**:
  - Jeda antar aksi menggunakan *natural human jitter* (2.5 – 4.0s).
  - Pengecekan jam aman (07:00 – 23:00) agar tidak mengirim snap di tengah malam.
- **Sistem Audit Logging (Retensi 3 Hari)**:
  - Mencatat riwayat pengiriman snap dan perubahan pengaturan.
  - Berkas log otomatis dibersihkan (*pruned*) jika sudah lebih tua dari 3 hari.
- **macOS LaunchAgent Auto-Scheduler**:
  - Didaftarkan otomatis jam 09:00 pagi.
  - Dilengkapi *Hourly Wake-up Catch-up*: jika laptop baru dibuka siang atau sore hari, aplikasi otomatis mengejar pengiriman streak hari itu segera setelah internet terhubung.
- **Notifikasi Laporan ke HP**:
  - **Telegram Bot**: Laporan instan ke Telegram pribadi Anda dengan status terkirim dan ringkasan nama penerima.
  - **Discord Webhook**: Kirim pesan embed ke channel Discord pilihan Anda.
  - **macOS Native Banner**: Pop-up banner notifikasi langsung di sudut layar Mac.

---

## 🚀 Panduan Instalasi (1-Klik)

### macOS & Linux
Cukup jalankan satu perintah ini di terminal:

```bash
curl -fsSL https://raw.githubusercontent.com/sammmms/snapchat-streak/main/install.sh | bash
```

*Atau clone repository secara lokal:*
```bash
git clone https://github.com/sammmms/snapchat-streak.git
cd snapchat-streak
./install.sh
```

Setelah instalasi selesai, Anda cukup mengetik perintah ini di mana saja:
```bash
snapchat-streak
```

---

## 📱 Panduan Integrasi Telegram Bot

1. Buka Telegram, cari **`@BotFather`** dan kirim `/newbot` untuk membuat bot baru. Simpan **Bot Token** yang diberikan.
2. Buka **`@userinfobot`** di Telegram untuk melihat nomor **Chat ID** Anda.
3. Buka bot buatan Anda lalu klik tombol **START**.
4. Buka aplikasi di terminal (`snapchat-streak`) -> pilih menu **`[6] 🔔 Pengaturan Notifikasi`** -> masukkan Bot Token & Chat ID -> pilih **Tes Notifikasi**.

---

## 🛠️ Opsi Perintah CLI (Lanjutan)

Selain menu interaktif, Anda juga dapat menjalankan flag perintah langsung:

```bash
# Menjalankan pengiriman streak di background (dipakai LaunchAgent)
snapchat-streak --cron

# Memaksa kirim streak sekarang meskipun hari ini sudah pernah terkirim
snapchat-streak --force

# Pindai teman Snapchat dan perbarui kontak
snapchat-streak --scan

# Buka jendela browser untuk login / menghubungkan akun
snapchat-streak --login
```

---

## ⚖️ Lisensi
Dilisensikan di bawah [MIT License](LICENSE).
Dikembangkan untuk mempermudah backup dan pemeliharaan streak personal. Patuhi ketentuan penggunaan layanan Snapchat.
