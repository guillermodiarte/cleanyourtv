#!/usr/bin/env python3
"""Audit a TV's CleanYourTV installation state.

Usage:
  TV_HOST=192.168.1.50 tools/venv/bin/python tools/tv_status.py
"""
import os
import sys

# Ensure tools/ is on sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tv


def run_cmd(cmd):
    dev = tv.connect()
    try:
        return dev.shell(cmd, read_timeout_s=15).strip()
    finally:
        dev.close()


def audit():
    host = os.environ.get("TV_HOST")
    if not host:
        print("ERROR: Set TV_HOST, e.g. TV_HOST=192.168.1.50 tools/venv/bin/python tools/tv_status.py", file=sys.stderr)
        return 1

    print(f"=== Diagnóstico de CleanYourTV para {host} ===")

    # 1. Device info
    model = run_cmd("getprop ro.product.model")
    android = run_cmd("getprop ro.build.version.release")
    sdk = run_cmd("getprop ro.build.version.sdk")
    adb = run_cmd("settings get global adb_enabled")
    print(f"Dispositivo: {model} (Android {android}, SDK {sdk})")
    print(f"Depuración USB (ADB): {'ACTIVA (OK)' if adb == '1' else 'DESACTIVADA (Requiere activar)'}")

    # 2. Launcher
    installed = run_cmd("pm list packages com.gathin.tvhome")
    if "com.gathin.tvhome" not in installed:
        print("Launcher CleanYourTV: NO INSTALADO")
    else:
        version = run_cmd("dumpsys package com.gathin.tvhome | grep -m 1 versionCode").strip()
        home = run_cmd("cmd package resolve-activity --brief -a android.intent.action.MAIN -c android.intent.category.HOME").strip()
        is_default = "com.gathin.tvhome" in home
        print(f"Launcher CleanYourTV: Instalado ({version}) | Home por defecto: {'SÍ (OK)' if is_default else 'NO'}")

    # 3. Screensaver
    dream = run_cmd("settings get secure screensaver_components")
    enabled = run_cmd("settings get secure screensaver_enabled")
    timeout = run_cmd("settings get system screen_off_timeout")
    timeout_min = int(timeout) // 60000 if timeout.isdigit() else 0
    backdrop_pkg = run_cmd("pm list packages -u com.google.android.backdrop")
    backdrop_enabled = run_cmd("pm list packages com.google.android.backdrop")

    print(f"Protector de pantalla activo: {dream} (Habilitado: {enabled}, Tiempo: {timeout_min} min)")
    if "com.google.android.backdrop" in backdrop_enabled:
        print("  - Google Backdrop (Paisajes): HABILITADO (OK)")
    elif "com.google.android.backdrop" in backdrop_pkg:
        print("  - Google Backdrop (Paisajes): INSTALADO pero DESHABILITADO (Requiere reactivar)")
    else:
        print("  - Google Backdrop (Paisajes): No disponible en esta ROM")

    # 4. Wallpapers & Theme
    wp_files = run_cmd("ls -la /sdcard/Android/data/com.gathin.tvhome/files/wallpapers/ 2>/dev/null")
    png_count = wp_files.count(".png")
    webp_count = wp_files.count(".webp")
    jpg_count = wp_files.count(".jpg")
    print(f"Colección de Wallpapers en TV: {webp_count} WebP, {png_count} PNG, {jpg_count} JPG")
    if png_count > 0:
        print("  - Formatos: Contiene PNGs antiguos pesados (Requiere migrar a WebP 1080p)")
    elif webp_count > 0:
        print("  - Formatos: Optimizado en WebP (OK)")

    # 5. Config JSON on TV
    config_json = run_cmd("cat /sdcard/Android/data/com.gathin.tvhome/files/config.json 2>/dev/null")
    if config_json:
        print("Configuración activa (Tema en TV):")
        for key in ["reorder_button", "wifi_status_color", "wifi_status_warnings", "wallpaper_rotation_minutes", "sky_intensity", "rows_below_dock"]:
            val = "No configurado (Default)"
            for line in config_json.splitlines():
                if f'"{key}"' in line:
                    val = line.strip().rstrip(",")
                    break
            print(f"  - {key}: {val}")
    else:
        print("Tema en TV: No hay config.json personalizado (usa valores nativos del launcher)")

    print("==================================================")
    return 0


if __name__ == "__main__":
    sys.exit(audit())

