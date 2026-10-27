#!/usr/bin/env bash
set -e

TARGET_DIR="$HOME/.gemini/config/skills/zgidno-vidpovidno"
echo "Встановлення скіла 'zgidno-vidpovidno'..."
echo "Цільова папка: $TARGET_DIR"

mkdir -p "$HOME/.gemini/config/skills"

if command -v git &>/dev/null; then
    if [ -d "$TARGET_DIR/.git" ]; then
        echo "Оновлення через git pull..."
        git -C "$TARGET_DIR" pull
    else
        rm -rf "$TARGET_DIR"
        git clone https://github.com/mrmelatonin/zgidno-vidpovidno.git "$TARGET_DIR"
    fi
else
    echo "Git не знайдено, завантаження архіву з GitHub..."
    rm -rf "$TARGET_DIR"
    mkdir -p "$TARGET_DIR"
    curl -sSL "https://github.com/mrmelatonin/zgidno-vidpovidno/archive/refs/heads/main.tar.gz" | tar -xz -C "$TARGET_DIR" --strip-components=1
fi

echo ""
echo "[+] Скіл 'zgidno-vidpovidno' успішно встановлено!"
echo "Тепер він автоматично доступний усім агентам Antigravity на вашому комп'ютері."
