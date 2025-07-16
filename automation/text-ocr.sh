#!/usr/bin/env bash

# Create directories if they don't exist
mkdir -p ~/Pictures/Ocr

# Find the next available incremental number
find_next_number() {
    local count=1
    while [[ -f ~/Pictures/Ocr/${count}.png ]]; do
        ((count++))
    done
    echo $count
}

# Get screen region from user
region=$(slurp)

if [[ -z "$region" ]]; then
    notify-send "OCR Extractor" "Selection canceled"
    exit 1
fi

# Generate filename
filename=$(find_next_number)
filepath=~/Pictures/Screenshots/${filename}.png

# Capture the selected region
grim -g "$region" "$filepath"

# Perform OCR and copy to clipboard
text=$(tesseract "$filepath" stdout 2>/dev/null)
echo "$text" | wl-copy

# Notification
notify-send "OCR Extractor" "Text extracted and copied to clipboard\nImage saved as ${filename}.png"
