#!/bin/bash
set -e

# Check Wayland
if [ "$XDG_SESSION_TYPE" != "wayland" ]; then
    echo "Error: This requires a Wayland session" >&2
    exit 1
fi

# System deps
DEPS=("grim" "slurp" "wl-copy" "tesseract-ocr")
echo "[+] Checking dependencies..."
for dep in "${DEPS[@]}"; do
    if ! command -v $dep >/dev/null 2>&1; then
        echo "Installing $dep..."
        if command -v apt >/dev/null 2>&1; then
            sudo apt install -y $dep
        elif command -v dnf >/dev/null 2>&1; then
            sudo dnf install -y $dep
        elif command -v pacman >/dev/null 2>&1; then
            sudo pacman -S --noconfirm $dep
        else
            echo "Please install $dep manually" >&2
            exit 1
        fi
    fi
done

# Python deps
PY_DEPS=("pillow" "pytesseract")
echo "[+] Installing Python dependencies..."
pip install --user ${PY_DEPS[@]}

# Install script
echo "[+] Installing wayland-text-snatcher..."
sudo cp bin/wayland-text-snatcher /usr/local/bin/
sudo chmod +x /usr/local/bin/wayland-text-snatcher

# Desktop integration
echo "[+] Setting up desktop integration..."
cat <<EOF | sudo tee /usr/share/applications/wayland-text-snatcher.desktop
[Desktop Entry]
Name=Wayland Text Snatcher
Comment=OCR screen text to clipboard
Exec=wayland-text-snatcher --capture
Icon=accessories-text-editor
Terminal=false
Type=Application
Categories=Utility;
EOF

echo "Installation complete! Configure your hotkey:"
echo
echo "For Sway:"
echo "  bindsym \$mod+Shift+T exec wayland-text-snatcher --capture"
echo
echo "For GNOME/KDE:"
echo "  Set Ctrl+Shift+T to run: wayland-text-snatcher --capture"
