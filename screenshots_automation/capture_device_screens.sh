#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RAW_PHONE="$SCRIPT_DIR/raw/phone"
mkdir -p "$RAW_PHONE"

echo "==> Ensuring device is ready..."
adb shell input keyevent KEYCODE_WAKEUP
adb shell am start -n appinventor.ai_grmapal2.Navegator/.MainActivity
sleep 2

echo "==> Capturing Screen 1: Home Browser..."
adb exec-out screencap -p > "$RAW_PHONE/screen1_home.png"

echo "==> Capturing Screen 2: Search / URL Input..."
adb shell input tap 400 160
sleep 1
adb shell input text "Easy%sNavigator"
sleep 1
adb exec-out screencap -p > "$RAW_PHONE/screen2_search.png"
adb shell input keyevent KEYCODE_BACK
sleep 1

echo "==> Capturing Screen 4: Bottom Sheet Menu..."
adb shell input tap 1020 160
sleep 1
adb exec-out screencap -p > "$RAW_PHONE/screen4_menu.png"

echo "==> Capturing Screen 3: QR Share Dialog..."
# Tap on 'Mostrar código QR' in bottom sheet
adb shell input tap 540 1605
sleep 1
adb exec-out screencap -p > "$RAW_PHONE/screen3_qr.png"
adb shell input keyevent KEYCODE_BACK
sleep 1

echo "==> Capturing Screen 5: Incinerate / Quick Wipe..."
adb shell input tap 920 160
sleep 1
adb exec-out screencap -p > "$RAW_PHONE/screen5_wipe.png"
adb shell input keyevent KEYCODE_BACK

echo "==> All raw screenshots captured successfully in $RAW_PHONE:"
ls -lh "$RAW_PHONE"
