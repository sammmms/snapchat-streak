#!/usr/bin/env bash
# ==============================================================================
# 👻 Snapchat Streak Hub One-Line Installer for macOS & Linux
# ==============================================================================
set -e

INSTALL_DIR="$HOME/.snapchat-streak"
BIN_DIR="$HOME/.local/bin"
SCRIPT_PATH="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/snapchat-streak.py"

echo "======================================================="
echo "👻 Installing Snapchat Streak Auto-Saver Hub..."
echo "======================================================="

# 1. Create directories
mkdir -p "$INSTALL_DIR"
mkdir -p "$BIN_DIR"

# 2. Copy script to install dir
if [ -f "$SCRIPT_PATH" ]; then
    cp "$SCRIPT_PATH" "$INSTALL_DIR/snapchat-streak.py"
elif [ -f "snapchat-streak.py" ]; then
    cp snapchat-streak.py "$INSTALL_DIR/snapchat-streak.py"
else
    echo "[!] Error: File snapchat-streak.py tidak ditemukan."
    exit 1
fi
chmod +x "$INSTALL_DIR/snapchat-streak.py"

# 3. Setup Shared Python Virtual Environment in ~/.automation-hub/venv
SHARED_HUB="$HOME/.automation-hub"
VENV_DIR="$SHARED_HUB/venv"
mkdir -p "$SHARED_HUB"

if [ ! -d "$VENV_DIR" ]; then
    echo "📦 Membuat shared virtual environment di $VENV_DIR..."
    python3 -m venv "$VENV_DIR"
fi

echo "⬇️  Memastikan pustaka pendukung terpasang (Playwright, Requests, Questionary, Pillow)..."
"$VENV_DIR/bin/pip" install --upgrade pip >/dev/null 2>&1 || true
"$VENV_DIR/bin/pip" install -q playwright requests questionary pillow >/dev/null 2>&1 || true

echo "🌐 Memastikan browser Chromium Playwright tersedia..."
"$VENV_DIR/bin/playwright" install chromium >/dev/null 2>&1 || true

# Link to app dir for backward compatibility
ln -sfn "$VENV_DIR" "$INSTALL_DIR/venv"

# 4. Create executable wrapper in ~/.local/bin/snapchat-streak
WRAPPER_FILE="$BIN_DIR/snapchat-streak"
rm -f "$WRAPPER_FILE"
cat <<EOF > "$WRAPPER_FILE"
#!/usr/bin/env bash
exec "$VENV_DIR/bin/python" "$INSTALL_DIR/snapchat-streak.py" "\$@"
EOF
chmod +x "$WRAPPER_FILE"

# 5. Ensure ~/.local/bin is in PATH
CURRENT_SHELL="$(basename "$SHELL")"
PROFILE_FILE="$HOME/.zshrc"
[ "$CURRENT_SHELL" = "bash" ] && PROFILE_FILE="$HOME/.bashrc"

if ! grep -q "$BIN_DIR" "$PROFILE_FILE" 2>/dev/null; then
    echo "export PATH=\"\$HOME/.local/bin:\$PATH\"" >> "$PROFILE_FILE"
    echo "ℹ️  Menambahkan $BIN_DIR ke $PROFILE_FILE"
fi

# 6. Setup macOS LaunchAgent with multi-interval wake-up catch-up
if [ "$(uname)" = "Darwin" ]; then
    PLIST_PATH="$HOME/Library/LaunchAgents/com.user.snapchatstreak.plist"
    cat <<EOF > "$PLIST_PATH"
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.user.snapchatstreak</string>
    <key>ProgramArguments</key>
    <array>
        <string>$WRAPPER_FILE</string>
        <string>--cron</string>
    </array>
    <key>StartCalendarInterval</key>
    <array>
        <dict><key>Hour</key><integer>9</integer><key>Minute</key><integer>0</integer></dict>
        <dict><key>Hour</key><integer>10</integer><key>Minute</key><integer>0</integer></dict>
        <dict><key>Hour</key><integer>11</integer><key>Minute</key><integer>0</integer></dict>
        <dict><key>Hour</key><integer>12</integer><key>Minute</key><integer>0</integer></dict>
        <dict><key>Hour</key><integer>13</integer><key>Minute</key><integer>0</integer></dict>
        <dict><key>Hour</key><integer>14</integer><key>Minute</key><integer>0</integer></dict>
        <dict><key>Hour</key><integer>15</integer><key>Minute</key><integer>0</integer></dict>
        <dict><key>Hour</key><integer>16</integer><key>Minute</key><integer>0</integer></dict>
        <dict><key>Hour</key><integer>17</integer><key>Minute</key><integer>0</integer></dict>
        <dict><key>Hour</key><integer>18</integer><key>Minute</key><integer>0</integer></dict>
        <dict><key>Hour</key><integer>19</integer><key>Minute</key><integer>0</integer></dict>
        <dict><key>Hour</key><integer>20</integer><key>Minute</key><integer>0</integer></dict>
        <dict><key>Hour</key><integer>21</integer><key>Minute</key><integer>0</integer></dict>
    </array>
    <key>StandardOutPath</key>
    <string>$INSTALL_DIR/streak.log</string>
    <key>StandardErrorPath</key>
    <string>$INSTALL_DIR/streak.log</string>
</dict>
</plist>
EOF
    launchctl unload "$PLIST_PATH" 2>/dev/null || true
    launchctl load "$PLIST_PATH"
    echo "⏰ Jadwal harian otomatis terdaftar jam 09:00 pagi (dengan macOS wake-up catch-up)!"
fi

echo ""
echo "======================================================="
echo "✅ Instalasi Selesai!"
echo "👉 Sekarang Anda cukup ketik perintah ini di terminal:"
echo "   snapchat-streak"
echo "======================================================="
