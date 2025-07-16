#!/bin/bash
set -e

echo "[+] Removing wayland-text-snatcher..."
sudo rm -f /usr/local/bin/wayland-text-snatcher
sudo rm -f /usr/share/applications/wayland-text-snatcher.desktop

echo "[+] Removing Python dependencies..."
pip uninstall -y pillow pytesseract

echo "Uninstallation complete"
