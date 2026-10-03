#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""NewVisuals Launcher — запуск Fabric 1.21.4 напрямую, без стороннего лаунчера."""

import ctypes
import hashlib
import json
import os
import re
import shutil
import queue
import subprocess
import sys
import threading
import tkinter as tk
import urllib.request
from tkinter import colorchooser, filedialog, messagebox

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(ROOT_DIR, "launcher_config.json")
ICON_PATH = os.path.join(ROOT_DIR, "icon.png")
ICO_PATH = os.path.join(ROOT_DIR, "launcher.ico")

# ---------- палитра клиента v2 ----------
BG = "#050509"
BG_DEEP = "#07070D"
PANEL = "#0B0B14"
CARD = "#10101B"
ROW = "#141421"
ROW_HOVER = "#1A1A2C"
BORDER = "#1F1F33"
TRACK = "#232338"
DEEP = "#2B5FA8"
BLUE = "#4D9BFF"
PURPLE = "#9B6BFF"
BRIGHT = "#C7E0FF"
TEXT = "#F2F2FA"
DIM = "#A6ACBF"
FAINT = "#6A7090"
GREEN = "#37D67A"
AMBER = "#FFC86B"
RED = "#FF6B6B"
PINK = "#FF6B9D"
CYAN = "#4FDBFF"

CAT_COLORS = {
    "WORLD": BLUE,
    "VISUALS": PURPLE,
    "MOVEMENT": GREEN,
    "HUD": AMBER,
    "GUI": PINK,
    "CHAT": CYAN,
    "GAMEPLAY": "#B07CFF",
}

CATEGORIES = [
    ("WORLD", "Мир"),
    ("VISUALS", "Визуал"),
    ("MOVEMENT", "Движение"),
    ("HUD", "HUD"),
    ("GUI", "GUI"),
    ("CHAT", "Чат"),
    ("GAMEPLAY", "Управление"),
]

MODULES = [
    {"id": "sky", "name": "Небо", "cat": "WORLD", "desc": "Пресеты неба и своя палитра.",
     "settings": [
         {"type": "bool", "id": "sky_color", "label": "Свой цвет неба", "default": False},
         {"type": "slider", "id": "color_r", "label": "Красный", "min": 0, "max": 255, "step": 1, "default": 115},
         {"type": "slider", "id": "color_g", "label": "Зелёный", "min": 0, "max": 255, "step": 1, "default": 180},
         {"type": "slider", "id": "color_b", "label": "Синий", "min": 0, "max": 255, "step": 1, "default": 255},
         {"type": "slider", "id": "preset", "label": "Пресет неба", "min": 0, "max": 10, "step": 1, "default": 2}]},
    {"id": "time", "name": "Время суток", "cat": "WORLD", "desc": "Фиксирует время дня.",
     "settings": [
         {"type": "slider", "id": "fixed_time", "label": "Время (в тиках)", "min": 0, "max": 24000, "step": 100, "default": 6000}]},
    {"id": "weather", "name": "Погода", "cat": "WORLD", "desc": "Своя погода: дождь и гроза.",
     "settings": [
         {"type": "bool", "id": "rain", "label": "Дождь", "default": False},
         {"type": "slider", "id": "rain_level", "label": "Сила дождя", "min": 0, "max": 1, "step": 0.01, "default": 1.0},
         {"type": "bool", "id": "thunder", "label": "Гроза", "default": False},
         {"type": "slider", "id": "thunder_level", "label": "Сила грома", "min": 0, "max": 1, "step": 0.01, "default": 1.0}]},
    {"id": "water", "name": "Прозрачность воды", "cat": "WORLD", "desc": "Видно сквозь воду.",
     "settings": [
         {"type": "slider", "id": "water_transparency", "label": "Прозрачность", "min": 0, "max": 100, "step": 1, "default": 60}]},
    {"id": "overlay", "name": "Оверлей блоков", "cat": "WORLD", "desc": "Подсветка выбранного блока.",
     "settings": [
         {"type": "slider", "id": "overlay_r", "label": "Красный", "min": 0, "max": 255, "step": 1, "default": 80},
         {"type": "slider", "id": "overlay_g", "label": "Зелёный", "min": 0, "max": 255, "step": 1, "default": 200},
         {"type": "slider", "id": "overlay_b", "label": "Синий", "min": 0, "max": 255, "step": 1, "default": 255},
         {"type": "slider", "id": "overlay_a", "label": "Прозрачность", "min": 0, "max": 255, "step": 1, "default": 150},
         {"type": "slider", "id": "overlay_thickness", "label": "Толщина", "min": 0.01, "max": 0.3, "step": 0.005, "default": 0.06}]},
    {"id": "tnt", "name": "Таймер TNT", "cat": "WORLD", "desc": "Отсчёт до взрыва TNT.", "settings": []},
    {"id": "fullbright", "name": "Фуллбрайт", "cat": "VISUALS", "desc": "Светло как днём в темноте.", "settings": []},
    {"id": "nohud", "name": "NoHud", "cat": "VISUALS", "desc": "Прячет лишний ванильный HUD.",
     "settings": [
         {"type": "bool", "id": "no_fire", "label": "NoFire", "default": True},
         {"type": "bool", "id": "no_particles", "label": "NoParticles", "default": True},
         {"type": "bool", "id": "no_block_particles", "label": "Частицы блоков", "default": True},
         {"type": "bool", "id": "no_totem", "label": "NoTotem", "default": True}]},
    {"id": "res", "name": "Разрешение экрана", "cat": "VISUALS", "desc": "Свой формат и размер GUI.",
     "settings": [
         {"type": "options", "id": "res_preset", "label": "Формат", "options": ["Авто", "1:1", "4:3", "3:2", "16:10", "16:9", "21:9", "9:16", "3:4", "9:10", "1:3"], "default": 5},
         {"type": "slider", "id": "res_w", "label": "Ширина (пикс)", "min": 480, "max": 5120, "step": 16, "default": 1920},
         {"type": "slider", "id": "res_h", "label": "Высота (пикс)", "min": 480, "max": 2880, "step": 16, "default": 1080}]},
    {"id": "freelook", "name": "Freelook", "cat": "VISUALS", "desc": "Осмотреться, не поворачивая игрока.",
     "settings": [
         {"type": "options", "id": "freelook_key", "label": "Клавиша", "options": ["V", "C", "Левая ALT", "ПКМ"], "default": 0},
         {"type": "slider", "id": "freelook_dist", "label": "Дистанция", "min": 1, "max": 8, "step": 0.25, "default": 4}]},
    {"id": "hand", "name": "Hand Settings", "cat": "VISUALS", "desc": "Положение и размер руки.",
     "settings": [
         {"type": "slider", "id": "hand_x", "label": "Позиция X", "min": -1, "max": 1, "step": 0.01, "default": 0},
         {"type": "slider", "id": "hand_y", "label": "Позиция Y", "min": -1, "max": 1, "step": 0.01, "default": 0},
         {"type": "slider", "id": "hand_z", "label": "Позиция Z", "min": -1, "max": 1, "step": 0.01, "default": 0},
         {"type": "slider", "id": "hand_scale", "label": "Размер", "min": 0.2, "max": 3, "step": 0.05, "default": 1},
         {"type": "slider", "id": "hand_rx", "label": "Наклон", "min": -180, "max": 180, "step": 1, "default": 0},
         {"type": "slider", "id": "hand_ry", "label": "Влево-вправо", "min": -180, "max": 180, "step": 1, "default": 0},
         {"type": "slider", "id": "hand_roll", "label": "Прокрут", "min": -180, "max": 180, "step": 1, "default": 0},
         {"type": "options", "id": "hand_preset", "label": "Заготовка", "options": ["Стандарт", "Блинчик", "Вниз", "Вверх", "На себя", "За спину", "Замах"], "default": 0}]},
    {"id": "swing", "name": "Swing Animation", "cat": "VISUALS", "desc": "Свои анимации замаха.",
     "settings": [
         {"type": "options", "id": "swing_style", "label": "Стиль", "options": ["Классика", "Взмах", "Спин 360", "Спин 180", "Дуга", "Боковой", "Молот", "Пика", "Крест", "Волна"], "default": 0},
         {"type": "slider", "id": "swing_speed", "label": "Мощность", "min": 0.3, "max": 3, "step": 0.05, "default": 1},
         {"type": "slider", "id": "swing_angle", "label": "Угол, град", "min": 10, "max": 180, "step": 5, "default": 100},
         {"type": "bool", "id": "swing_sword", "label": "Только меч", "default": False}]},
    {"id": "pearl", "name": "Pearl Trajectory", "cat": "VISUALS", "desc": "Траектория эндер-жемчуга.",
     "settings": [
         {"type": "options", "id": "pt_mode", "label": "Режим", "options": ["Превью", "Только бросок"], "default": 0},
         {"type": "bool", "id": "pt_landing", "label": "Точка приземления", "default": True},
         {"type": "slider", "id": "pt_power", "label": "Сила", "min": 0.5, "max": 2.5, "step": 0.05, "default": 1.5}]},
    {"id": "hat", "name": "Китайская шляпа", "cat": "VISUALS", "desc": "Шляпа над головами игроков.",
     "settings": [
         {"type": "bool", "id": "ch_only_friends", "label": "Только друзья", "default": False},
         {"type": "bool", "id": "ch_self", "label": "Своя шляпа", "default": True},
         {"type": "color", "id": "ch_color", "label": "Цвет", "default": "#4D9BFF"},
         {"type": "slider", "id": "ch_radius", "label": "Радиус", "min": 0.15, "max": 0.6, "step": 0.05, "default": 0.35},
         {"type": "slider", "id": "ch_height", "label": "Высота", "min": -0.2, "max": 0.8, "step": 0.05, "default": 0.25},
         {"type": "slider", "id": "ch_speed", "label": "Скорость", "min": 0, "max": 3, "step": 0.1, "default": 1},
         {"type": "slider", "id": "ch_distance", "label": "Дистанция", "min": 8, "max": 128, "step": 4, "default": 64}]},
    {"id": "sprint", "name": "Auto Sprint", "cat": "MOVEMENT", "desc": "Бег без удержания Ctrl.", "settings": []},
    {"id": "clickpearl", "name": "Click Pearl", "cat": "MOVEMENT", "desc": "Бросок жемчуга по клику.",
     "settings": [
         {"type": "options", "id": "cp_trigger", "label": "Режим", "options": ["ПКМ", "Средняя кнопка", "ЛКМ"], "default": 1}]},
    {"id": "crit", "name": "Crit Sneak", "cat": "MOVEMENT", "desc": "Критованная атака из шифта.",
     "settings": [
         {"type": "slider", "id": "critsneak_duration", "label": "Длительность, тики", "min": 1, "max": 12, "step": 1, "default": 5}]},
    {"id": "playerhud", "name": "PlayerHud", "cat": "HUD", "desc": "Информация об игроках рядом.",
     "settings": [
         {"type": "slider", "id": "ph_opacity", "label": "Прозрачность", "min": 10, "max": 100, "step": 1, "default": 90},
         {"type": "slider", "id": "ph_scale", "label": "Размер", "min": 0.5, "max": 1.5, "step": 0.05, "default": 1}]},
    {"id": "wm", "name": "Watermark", "cat": "HUD", "desc": "Логотип клиента на экране.",
     "settings": [
         {"type": "slider", "id": "wm_opacity", "label": "Прозрачность", "min": 10, "max": 100, "step": 1, "default": 90},
         {"type": "slider", "id": "wm_scale", "label": "Размер", "min": 0.5, "max": 1.5, "step": 0.05, "default": 1}]},
    {"id": "coords", "name": "Coords HUD", "cat": "HUD", "desc": "Координаты и направление.",
     "settings": [
         {"type": "slider", "id": "ch_opacity", "label": "Прозрачность", "min": 10, "max": 100, "step": 1, "default": 90},
         {"type": "slider", "id": "ch_scale", "label": "Размер", "min": 0.5, "max": 1.5, "step": 0.05, "default": 1}]},
    {"id": "hitmarker", "name": "Hit Marker", "cat": "HUD", "desc": "Метка при попадании.",
     "settings": [
         {"type": "slider", "id": "hit_size", "label": "Размер", "min": 4, "max": 16, "step": 1, "default": 8},
         {"type": "bool", "id": "hit_crit", "label": "Крит золотом", "default": True}]},
    {"id": "keys", "name": "Клавиши", "cat": "HUD", "desc": "Клавиатура и мышь на экране.",
     "settings": [
         {"type": "bool", "id": "ks_keys", "label": "Клавиши WASD", "default": True},
         {"type": "bool", "id": "ks_mouse", "label": "Кнопки мыши", "default": True},
         {"type": "bool", "id": "ks_space", "label": "Пробел / шифт", "default": True},
         {"type": "bool", "id": "ks_cps", "label": "CPS", "default": True},
         {"type": "bool", "id": "ks_outline", "label": "Обводка", "default": True},
         {"type": "slider", "id": "ks_scale", "label": "Размер", "min": 0.6, "max": 1.8, "step": 0.05, "default": 1},
         {"type": "options", "id": "ks_style", "label": "Стиль", "options": ["Наш", "Стандарт", "Минимал"], "default": 0},
         {"type": "color", "id": "ks_active", "label": "Цвет нажатой", "default": "#4D9BFF"},
         {"type": "color", "id": "ks_idle", "label": "Цвет отпущенной", "default": "#1E1E2C"}]},
    {"id": "chat", "name": "Сглаживание чата", "cat": "GUI", "desc": "Плавная прокрутка сообщений.",
     "settings": [
         {"type": "slider", "id": "chat_offset", "label": "Смещение, px", "min": 0, "max": 24, "step": 1, "default": 9},
         {"type": "slider", "id": "chat_speed", "label": "Скорость", "min": 0.05, "max": 0.8, "step": 0.01, "default": 0.22}]},
    {"id": "gui", "name": "Настройки GUI", "cat": "GUI", "desc": "Внешний вид меню клиента.",
     "settings": [
         {"type": "slider", "id": "gui_opacity", "label": "Прозрачность", "min": 0.2, "max": 1, "step": 0.05, "default": 0.85},
         {"type": "slider", "id": "gui_blur", "label": "Блюр", "min": 0, "max": 8, "step": 1, "default": 4},
         {"type": "options", "id": "gui_theme", "label": "Тема", "options": ["Ночь", "День"], "default": 0}]},
    {"id": "friends", "name": "Друзья в чате", "cat": "CHAT", "desc": "Подсветка сообщений друзей.",
     "settings": [
         {"type": "bool", "id": "fr_self", "label": "Свой ник", "default": True},
         {"type": "color", "id": "fr_self_color", "label": "Цвет своего ника", "default": "#4D9BFF"},
         {"type": "color", "id": "fr_default_color", "label": "Цвет нового друга", "default": "#4D9BFF"}]},
    {"id": "login", "name": "Скрытие экрана", "cat": "CHAT", "desc": "Блюр при /login и /register.",
     "settings": [
         {"type": "slider", "id": "lb_dur", "label": "Время блюра, сек", "min": 3, "max": 15, "step": 1, "default": 7}]},
    {"id": "scroll", "name": "Перетаскивание", "cat": "GAMEPLAY", "desc": "Драг-скролл предметов в инвентаре.", "settings": []},
]

DEFAULT_LAUNCHER = {
    "memory_gb": 4,
    "priority": "Обычный",
    "java_path": "",
    "game_dir": r"D:\Minecraft\game",
    "version": "1.21.4",
    "account": "",
    "hide_on_launch": True,
}

LAUNCHER_VERSION = "1.0"
UPDATE_REPO = ""
REAL_VERSION = "1.21.4"
VERSION_DIR = "Fabric 1.21.4"
VERSIONS = ["1.21.4", "1 21 4", "1.21.4.0", "а че я должен еще и думать?"]
VERSION_WARN = "1.21.4 версию выбирай — я для всей этой херни делать не буду!"
PRIORITY_CLASSES = {"Низкий": 0x40, "Обычный": 0x20, "Высокий": 0x80}


def module_default_state():
    state = {}
    for m in MODULES:
        s = {}
        for setting in m["settings"]:
            s[setting["id"]] = setting["default"]
        state[m["id"]] = {"on": False, "settings": s}
    return state


# ---------- canvas helpers ----------
def hex_blend(c1, c2, t):
    def ch(h):
        return int(h[1:3], 16), int(h[3:5], 16), int(h[5:7], 16)
    r1, g1, b1 = ch(c1)
    r2, g2, b2 = ch(c2)
    return "#%02X%02X%02X" % (int(r1 + (r2 - r1) * t), int(g1 + (g2 - g1) * t), int(b1 + (b2 - b1) * t))


def grad_horizontal(cv, x1, y1, x2, y2, c1, c2):
    """Рисует округлённый прямоугольник с горизонтальным градиентом. Возвращает id item'ов."""
    ids = []
    span = max(1, x2 - x1)
    for i in range(span):
        t = i / span
        ids.append(cv.create_line(x1 + i, y1, x1 + i, y2, fill=hex_blend(c1, c2, t)))
    return ids


def round_rect(cv, x1, y1, x2, y2, r, **kw):
    pts = [x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r, x2, y2 - r, x2, y2,
           x2 - r, y2, x1 + r, y2, x1, y2, x1, y2 - r, x1, y1 + r, x1, y1]
    return cv.create_polygon(pts, smooth=True, **kw)


def fmt_val(v, step):
    if not float(step).is_integer():
        d = len(str(step).split(".")[1])
        t = f"{v:.{d}f}"
        if "." in t:
            t = t.rstrip("0").rstrip(".")
        return t
    return f"{int(round(v))}"


# ---------- запуск Minecraft ----------
class LaunchError(Exception):
    pass


def _java_major(java):
    try:
        proc = subprocess.run([java, "-version"], capture_output=True,
                              text=True, timeout=15,
                              creationflags=subprocess.CREATE_NO_WINDOW)
        out = (proc.stderr or "") + (proc.stdout or "")
        match = re.search(r'version "(\d+)', out)
        return int(match.group(1)) if match else 0
    except Exception:
        return 0


def _javaw_sibling(path):
    folder, base = os.path.split(path)
    if base.lower() == "java.exe":
        twin = os.path.join(folder, "javaw.exe")
        if os.path.isfile(twin):
            return twin
    return None


def find_java(java_path):
    """Ищет Java 21+. Возвращает javaw.exe где возможно — без консольных окон."""
    candidates = []
    custom = (java_path or "").strip().strip('"')
    if custom:
        if os.path.isfile(custom):
            candidates.append(custom)
        elif os.path.isdir(custom):
            candidates.append(os.path.join(custom, "bin", "java.exe"))
    candidates.append(r"D:\MCreator\jdk\bin\java.exe")
    which = shutil.which("java")
    if which:
        candidates.append(which)
    for candidate in candidates:
        if not candidate or not os.path.isfile(candidate):
            continue
        twin = _javaw_sibling(candidate)
        if twin and _java_major(twin) >= 21:
            return twin
        if _java_major(candidate) >= 21:
            return candidate
    return None


def _rule_matches(rule):
    os_rule = rule.get("os")
    if isinstance(os_rule, dict):
        if "name" in os_rule and os_rule["name"] != "windows":
            return False
    if "features" in rule:
        return False
    return True


def _entry_values(entry):
    if isinstance(entry, str):
        return [entry], True
    rules = entry.get("rules")
    if not rules:
        allowed = True
    else:
        allowed = False
        for rule in rules:
            if _rule_matches(rule):
                allowed = rule.get("action", "allow") == "allow"
                break
    value = entry.get("value", [])
    if isinstance(value, str):
        value = [value]
    return value, allowed


def _lib_path(game_dir, lib):
    downloads = lib.get("downloads") or {}
    artifact = downloads.get("artifact") or {}
    if artifact.get("path"):
        return os.path.join(game_dir, "libraries", artifact["path"].replace("/", os.sep))
    parts = lib["name"].split(":")
    group, artifact_id, version = parts[0], parts[1], parts[2]
    classifier = parts[3] if len(parts) > 3 else None
    filename = artifact_id + "-" + version
    if classifier:
        filename += "-" + classifier
    filename += ".jar"
    return os.path.join(game_dir, "libraries", *group.split("."),
                        artifact_id, version, filename)


def _offline_uuid(username):
    digest = hashlib.md5(("OfflinePlayer:" + username).encode("utf-8")).digest()
    raw = bytearray(digest)
    raw[6] = (raw[6] & 0x0F) | 0x30
    raw[8] = (raw[8] & 0x3F) | 0x80
    hx = bytes(raw).hex()
    return "%s-%s-%s-%s-%s" % (hx[:8], hx[8:12], hx[12:16], hx[16:20], hx[20:])


def _read_account(game_dir):
    try:
        with open(os.path.join(game_dir, "tlauncher_profiles.json"),
                  encoding="utf-8") as f:
            data = json.load(f)
        user_set = data.get("userSet", {})
        selected = (user_set.get("selected") or {}).get("username", "")
        found_uuid = ""
        for user in user_set.get("list", []):
            if user.get("username") == selected:
                found_uuid = user.get("uuid", "")
                break
        if selected:
            return selected, found_uuid or _offline_uuid(selected)
    except Exception:
        pass
    return "Player", _offline_uuid("Player")


def _read_client_token(game_dir):
    try:
        with open(os.path.join(game_dir, "launcher_profiles.json"),
                  encoding="utf-8") as f:
            data = json.load(f)
        token = data.get("clientToken", "")
        if isinstance(token, str) and token:
            return token
    except Exception:
        pass
    return "0"


def _subst(text, subs):
    for key, value in subs.items():
        text = text.replace("${" + key + "}", value)
    return text


def build_launch_command(cfg, accounts=None):
    game_dir = (cfg.get("game_dir") or "").strip()
    if not game_dir or not os.path.isdir(game_dir):
        raise LaunchError("Папка игры не найдена. Проверь «Настройки → Папка игры».")
    version_dir = os.path.join(game_dir, "versions", VERSION_DIR)
    version_json = os.path.join(version_dir, VERSION_DIR + ".json")
    if not os.path.isfile(version_json):
        raise LaunchError("Не найден %s.json. Проверь папку игры." % VERSION_DIR)
    with open(version_json, encoding="utf-8") as f:
        version = json.load(f)
    natives_dir = os.path.join(version_dir, "natives")
    if not os.path.isdir(natives_dir):
        raise LaunchError("Не найдена папка natives версии.")
    assets_dir = os.path.join(game_dir, "assets")
    if not os.path.isdir(assets_dir):
        raise LaunchError("Не найдена папка assets в папке игры.")

    java = find_java(cfg.get("java_path", ""))
    if not java:
        raise LaunchError("Не найдена Java 21+. Укажи путь в «Настройки → Java».")

    def _version_key(ver):
        parts = []
        for chunk in re.split(r"[.\-+_]", str(ver)):
            digits = "".join(ch for ch in chunk if ch.isdigit())
            parts.append(int(digits) if digits else 0)
        return tuple(parts)

    grouped = {}
    order = []
    for lib in version.get("libraries", []):
        _, allowed = _entry_values(lib)
        if not allowed:
            continue
        parts = lib.get("name", "").split(":")
        if len(parts) < 3 or len(parts) > 3:
            continue  # нативы уже распакованы в natives/
        key = (parts[0], parts[1])
        if key not in grouped:
            grouped[key] = []
            order.append(key)
        grouped[key].append((parts[2], lib))
    cp_entries = []
    missing = []
    for key in order:
        cands = grouped[key]
        if len(cands) > 1:
            # Две версии одной библиотеки (напр. ASM у Fabric и ваниллы):
            # Fabric падает на дублях, оставляем самую новую.
            cands = sorted(cands, key=lambda c: _version_key(c[0]), reverse=True)[:1]
        lib = cands[0][1]
        path = _lib_path(game_dir, lib)
        if os.path.isfile(path):
            cp_entries.append(path)
        else:
            missing.append(lib.get("name", "?"))
    if missing:
        shown = "\n".join(missing[:8])
        extra = "\n…и ещё %d" % (len(missing) - 8) if len(missing) > 8 else ""
        raise LaunchError("Не хватает библиотек (%d):\n%s%s" % (len(missing), shown, extra))

    client_jar = os.path.join(version_dir, VERSION_DIR + ".jar")
    if not os.path.isfile(client_jar):
        raise LaunchError("Не найден jar версии.")
    cp_entries.append(client_jar)

    try:
        memory = int(cfg.get("memory_gb", 4))
    except (TypeError, ValueError):
        memory = 4
    memory = min(max(memory, 1), 16)

    username, uuid = get_launch_account(cfg, accounts)
    subs = {
        "natives_directory": natives_dir,
        "launcher_name": "NewVisuals-Launcher",
        "launcher_version": "1.0",
        "classpath": ";".join(cp_entries),
        "auth_player_name": username,
        "version_name": VERSION_DIR,
        "game_directory": game_dir,
        "assets_root": assets_dir,
        "assets_index_name": str(version.get("assets", "19")),
        "auth_uuid": uuid,
        "auth_access_token": "0",
        "clientid": _read_client_token(game_dir),
        "auth_xuid": "0",
        "user_type": "legacy",
        "version_type": "release",
    }
    arguments = version.get("arguments") or {}
    cmd = [java, "-Xmx%dG" % memory, "-Xms%dG" % memory]
    for entry in arguments.get("jvm", []):
        values, allowed = _entry_values(entry)
        if not allowed:
            continue
        for value in values:
            if "FabricMcEmu" in value:
                continue
            cmd.append(_subst(value, subs))
    cmd.append(version.get("mainClass", "net.fabricmc.loader.impl.launch.knot.KnotClient"))
    for entry in arguments.get("game", []):
        values, allowed = _entry_values(entry)
        if not allowed:
            continue
        for value in values:
            cmd.append(_subst(value, subs))
    return cmd, game_dir


def launch_minecraft(cfg, accounts=None):
    cmd, game_dir = build_launch_command(cfg, accounts)
    try:
        proc = subprocess.Popen(
            cmd, cwd=game_dir,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            creationflags=(subprocess.DETACHED_PROCESS
                           | subprocess.CREATE_NEW_PROCESS_GROUP
                           | subprocess.CREATE_NO_WINDOW))
    except Exception as exc:
        raise LaunchError("Не смог запустить Java: %s" % exc)
    try:
        ctypes.windll.kernel32.SetPriorityClass(
            proc._handle, PRIORITY_CLASSES.get(cfg.get("priority", "Обычный"), 0x20))
    except Exception:
        pass
    return proc


# ---------- аккаунты и синхронизация мода ----------
def _tlauncher_accounts(game_dir):
    out = []
    try:
        with open(os.path.join(game_dir, "tlauncher_profiles.json"),
                  encoding="utf-8") as f:
            data = json.load(f)
        user_set = data.get("userSet") or {}
        selected = (user_set.get("selected") or {}).get("username", "")
        users = user_set.get("list", [])
        ordered = sorted(users,
                         key=lambda u: 0 if u.get("username") == selected else 1)
        for user in ordered:
            name = user.get("username", "")
            if isinstance(name, str) and re.fullmatch(r"[A-Za-z0-9_]{3,16}", name):
                out.append({"name": name,
                            "uuid": user.get("uuid") or _offline_uuid(name)})
    except Exception:
        pass
    return out


def get_launch_account(cfg, accounts):
    wanted = (cfg.get("account") or "").strip()
    for acc in accounts or []:
        if isinstance(acc, dict) and acc.get("name") == wanted:
            return acc["name"], acc.get("uuid") or _offline_uuid(acc["name"])
    return _read_account(cfg.get("game_dir", ""))


SKIP_MOD_IDS = {"cp_key", "freelook_key"}


def _mod_value(setting, value):
    kind = setting.get("type")
    if kind == "bool":
        return bool(value)
    if kind == "slider":
        try:
            return float(value)
        except (TypeError, ValueError):
            return float(setting.get("default", 0))
    if kind == "options":
        try:
            return int(value)
        except (TypeError, ValueError):
            return int(setting.get("default", 0))
    if kind == "color":
        text = str(value or "").strip().lstrip("#")
        try:
            rgb = int(text, 16) if len(text) == 6 else 0x4D9BFF
        except ValueError:
            rgb = 0x4D9BFF
        argb = 0xFF000000 | rgb
        return argb - 0x100000000 if argb >= 0x80000000 else argb
    return value


def sync_mod_config(game_dir, state):
    """Записывает вкл/выкл и настройки функций в newvisuals.json мода.

    Чужие ключи (друзья, кейбинды, цвета GUI, пресеты) не трогает.
    """
    if not game_dir or not os.path.isdir(game_dir):
        raise LaunchError("Папка игры не найдена. Проверь «Настройки → Папка игры».")
    path = os.path.join(game_dir, "newvisuals.json")
    try:
        with open(path, encoding="utf-8") as f:
            root = json.load(f)
    except Exception:
        root = {}
    if not isinstance(root, dict):
        root = {}
    modules_root = root.get("modules")
    if not isinstance(modules_root, dict):
        modules_root = {}
    by_id = {m["id"]: m for m in MODULES}
    for mid, entry in (state.get("modules") or {}).items():
        mod = by_id.get(mid)
        if mod is None or not isinstance(entry, dict):
            continue
        node = modules_root.get(mod["name"])
        if not isinstance(node, dict):
            node = {}
        node["enabled"] = bool(entry.get("on", False))
        settings = entry.get("settings") or {}
        for setting in mod.get("settings", []):
            sid = setting["id"]
            if sid in SKIP_MOD_IDS or sid not in settings:
                continue
            node[sid] = _mod_value(setting, settings[sid])
        modules_root[mod["name"]] = node
    root["modules"] = modules_root
    gui = root.get("gui")
    if not isinstance(gui, dict):
        gui = {}
    gui_settings = (state.get("modules") or {}).get("gui", {}).get("settings", {})
    for mod_key, gui_key, conv in (("gui_opacity", "opacity", float),
                                   ("gui_blur", "blur", float),
                                   ("gui_theme", "theme", int)):
        if mod_key in gui_settings:
            try:
                gui[gui_key] = conv(gui_settings[mod_key])
            except (TypeError, ValueError):
                pass
    root["gui"] = gui
    with open(path, "w", encoding="utf-8") as f:
        json.dump(root, f, ensure_ascii=False, indent=2)


def _launcher_value(setting, value):
    kind = setting.get("type")
    if kind == "bool":
        return bool(value)
    if kind == "slider":
        try:
            return float(value)
        except (TypeError, ValueError):
            return setting.get("default")
    if kind == "options":
        try:
            iv = int(value)
            if 0 <= iv < len(setting.get("options", [])):
                return iv
        except (TypeError, ValueError):
            pass
        return setting.get("default")
    if kind == "color":
        try:
            return "#%06X" % (int(value) & 0xFFFFFF)
        except (TypeError, ValueError):
            return setting.get("default")
    return value


def import_mod_config(game_dir, state):
    """Читает newvisuals.json мода обратно в состояние лаунчера.

    Возвращает число применённых модулей. Кейбинды-коды не трогает.
    """
    path = os.path.join(game_dir, "newvisuals.json")
    with open(path, encoding="utf-8") as f:
        root = json.load(f)
    if not isinstance(root, dict):
        return 0
    modules_root = root.get("modules")
    if not isinstance(modules_root, dict):
        return 0
    by_name = {m["name"]: m for m in MODULES}
    applied = 0
    for name, node in modules_root.items():
        mod = by_name.get(name)
        if mod is None or not isinstance(node, dict):
            continue
        entry = state["modules"][mod["id"]]
        if isinstance(node.get("enabled"), bool):
            entry["on"] = node["enabled"]
        settings = entry["settings"]
        for setting in mod.get("settings", []):
            sid = setting["id"]
            if sid in SKIP_MOD_IDS or sid not in node:
                continue
            settings[sid] = _launcher_value(setting, node[sid])
        applied += 1
    gui = root.get("gui")
    if isinstance(gui, dict):
        gset = state["modules"]["gui"]["settings"]
        for mod_key, gui_key, conv in (("gui_opacity", "opacity", float),
                                       ("gui_blur", "blur", float),
                                       ("gui_theme", "theme", int)):
            if gui_key in gui:
                try:
                    gset[mod_key] = conv(gui[gui_key])
                except (TypeError, ValueError):
                    pass
    return applied


# ---------- автообновление через GitHub Releases ----------
def parse_version(text):
    parts = []
    for chunk in re.split(r"[.\-+_]", str(text or "").strip().lstrip("vV")):
        digits = "".join(ch for ch in chunk if ch.isdigit())
        parts.append(int(digits) if digits else 0)
    return tuple(parts) if parts else (0,)


def check_github_release():
    """Возвращает dict(version, notes, zip_url) если есть релиз новее, иначе None."""
    if not UPDATE_REPO or "/" not in UPDATE_REPO:
        return None
    url = "https://api.github.com/repos/%s/releases/latest" % UPDATE_REPO
    req = urllib.request.Request(url, headers={"User-Agent": "NewVisuals-Launcher",
                                               "Accept": "application/vnd.github+json"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.load(resp)
    tag = str(data.get("tag_name", "")).strip()
    if not tag or parse_version(tag) <= parse_version(LAUNCHER_VERSION):
        return None
    zip_url = ""
    for asset in data.get("assets", []) or []:
        name = str(asset.get("name", ""))
        if name.lower().endswith(".zip") and asset.get("browser_download_url"):
            zip_url = asset["browser_download_url"]
            break
    if not zip_url:
        zip_url = data.get("zipball_url", "")
    if not zip_url:
        return None
    return {"version": tag.lstrip("vV"),
            "notes": data.get("body", "") or "",
            "zip_url": zip_url}


def download_update(zip_url):
    tmp = os.path.join(ROOT_DIR, "update_pending.zip")
    req = urllib.request.Request(zip_url, headers={"User-Agent": "NewVisuals-Launcher"})
    with urllib.request.urlopen(req, timeout=120) as resp, open(tmp, "wb") as f:
        shutil.copyfileobj(resp, f)
    return tmp


def run_updater_and_exit(zip_path):
    bat = os.path.join(ROOT_DIR, "update.bat")
    launcher = os.path.join(ROOT_DIR, "Launcher.py")
    with open(bat, "w", encoding="utf-8") as f:
        f.write("@echo off\n")
        f.write("timeout /t 2 /nobreak >nul\n")
        f.write("powershell -NoProfile -ExecutionPolicy Bypass -Command "
                "\"Expand-Archive -Force -Path '%s' -DestinationPath '%s'\"\n"
                % (zip_path, ROOT_DIR))
        f.write('del "%s"\n' % zip_path)
        f.write('start "" "%s" "%s"\n' % (sys.executable, launcher))
        f.write('del "%%~f0"\n')
    subprocess.Popen(["cmd", "/c", bat], cwd=ROOT_DIR,
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                     creationflags=(subprocess.DETACHED_PROCESS
                                    | subprocess.CREATE_NEW_PROCESS_GROUP
                                    | subprocess.CREATE_NO_WINDOW))
    os._exit(0)


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("NewVisuals Launcher")
        self.geometry("1010x670")
        self.minsize(900, 600)
        self.configure(bg=BG)
        self._load()
        self._icon()
        self._current = None
        self._filter = "Все"
        self._search = ""
        self._selected_module = None
        self._pulse_after = None
        self._build()

    def destroy(self):
        try:
            if self._pulse_after is not None:
                self.after_cancel(self._pulse_after)
                self._pulse_after = None
        except Exception:
            pass
        super().destroy()

    # ---------- состояния ----------
    def _load(self):
        default = {"modules": module_default_state(), "launcher": dict(DEFAULT_LAUNCHER)}
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            data = {}
        if not isinstance(data, dict):
            data = {}

        raw_modules = data.get("modules", {})
        if not isinstance(raw_modules, dict):
            raw_modules = {}
        modules = {}
        for module in MODULES:
            raw_entry = raw_modules.get(module["id"], {})
            if not isinstance(raw_entry, dict):
                raw_entry = {}
            raw_settings = raw_entry.get("settings", {})
            if not isinstance(raw_settings, dict):
                raw_settings = {}
            settings = {}
            for setting in module["settings"]:
                settings[setting["id"]] = self._sanitize_setting(
                    setting, raw_settings.get(setting["id"], setting["default"])
                )
            on = raw_entry.get("on", False)
            modules[module["id"]] = {
                "on": on if isinstance(on, bool) else False,
                "settings": settings,
            }

        raw_launcher = data.get("launcher", {})
        if not isinstance(raw_launcher, dict):
            raw_launcher = {}
        launcher = dict(DEFAULT_LAUNCHER)
        try:
            memory = int(raw_launcher.get("memory_gb", launcher["memory_gb"]))
        except (TypeError, ValueError):
            memory = launcher["memory_gb"]
        launcher["memory_gb"] = min(max(memory, 1), 16)
        priority = raw_launcher.get("priority", launcher["priority"])
        if priority not in ("Низкий", "Обычный", "Высокий"):
            priority = launcher["priority"]
        launcher["priority"] = priority
        version = raw_launcher.get("version", launcher["version"])
        if version != REAL_VERSION:
            version = REAL_VERSION
        launcher["version"] = version
        hide = raw_launcher.get("hide_on_launch", True)
        launcher["hide_on_launch"] = hide if isinstance(hide, bool) else True
        for key in ("java_path", "game_dir"):
            value = raw_launcher.get(key, launcher[key])
            launcher[key] = value if isinstance(value, str) else launcher[key]

        raw_accounts = data.get("accounts", [])
        accounts = []
        if isinstance(raw_accounts, list):
            for acc in raw_accounts:
                if not isinstance(acc, dict):
                    continue
                name = acc.get("name", "")
                if isinstance(name, str) and re.fullmatch(r"[A-Za-z0-9_]{3,16}", name):
                    accounts.append({"name": name,
                                     "uuid": acc.get("uuid") or _offline_uuid(name)})
        if not accounts:
            accounts = _tlauncher_accounts(launcher["game_dir"])
        if not accounts:
            accounts = [{"name": "Player", "uuid": _offline_uuid("Player")}]
        names = [a["name"] for a in accounts]
        selected = raw_launcher.get("account", "")
        if selected not in names:
            selected = names[0]
        launcher["account"] = selected
        self.state = {"modules": modules, "launcher": launcher, "accounts": accounts}

    @staticmethod
    def _sanitize_setting(setting, value):
        kind = setting.get("type")
        default = setting.get("default")
        if kind == "bool":
            return value if isinstance(value, bool) else default
        if kind == "slider":
            try:
                number = float(value)
            except (TypeError, ValueError):
                return default
            low = float(setting["min"])
            high = float(setting["max"])
            step = float(setting["step"])
            number = min(max(number, low), high)
            number = low + round((number - low) / step) * step
            number = min(max(number, low), high)
            if float(step).is_integer():
                return int(round(number))
            return round(number, 6)
        if kind == "options":
            options = setting.get("options", [])
            if isinstance(value, int) and 0 <= value < len(options):
                return value
            if isinstance(value, str) and value in options:
                return options.index(value)
            return default
        if kind == "color":
            if isinstance(value, str) and re.fullmatch(
                r"#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})", value.strip()
            ):
                return value.strip().upper()
            return default
        return default

    def _save(self):
        try:
            with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump(self.state, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def _icon(self):
        try:
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
                "newvisuals.launcher")
        except Exception:
            pass
        if os.path.exists(ICO_PATH):
            try:
                self.iconbitmap(default=ICO_PATH)
            except Exception:
                pass
        if os.path.exists(ICON_PATH):
            try:
                img = tk.PhotoImage(file=ICON_PATH)
                self.iconphoto(True, img)
                self._tk_icon = img
            except Exception:
                pass

    # ---------- каркас ----------
    def _build(self):
        self._ui_queue = queue.Queue()
        self._header()
        self._sidebar()
        self._pages()
        self.show_tab("play")
        self.after(2000, self._poll_mc)
        threading.Thread(target=self._check_updates_async, daemon=True).start()

    # ---------- обновления ----------
    def _post_ui(self, item):
        """Кладёт задачу для GUI-потока в очередь (потокобезопасно, без Tk)."""
        try:
            self._ui_queue.put(item)
        except Exception:
            pass

    def _drain_ui_queue(self, event=None):
        try:
            while True:
                kind, payload = self._ui_queue.get_nowait()
                if kind == "dialog":
                    self._show_update_dialog(payload)
                elif kind == "status":
                    target, text = payload
                    try:
                        target.configure(text=text)
                    except Exception:
                        pass
        except queue.Empty:
            pass

    def _check_updates_async(self):
        try:
            info = check_github_release()
        except Exception:
            return
        if info:
            self._post_ui(("dialog", info))

    def _show_update_dialog(self, info):
        if getattr(self, "_update_dialog_open", False):
            return
        self._update_dialog_open = True
        win = tk.Toplevel(self)
        win.title("Обновление")
        win.geometry("460x380")
        win.configure(bg=CARD)
        win.resizable(False, False)
        try:
            win.transient(self)
            win.grab_set()
        except Exception:
            pass
        tk.Label(win, text="Вышла новая версия: %s" % info["version"],
                 bg=CARD, fg=TEXT, font=("Segoe UI", 14, "bold")) \
            .pack(anchor="w", padx=18, pady=(16, 2))
        tk.Label(win, text="У тебя: %s" % LAUNCHER_VERSION,
                 bg=CARD, fg=DIM, font=("Segoe UI", 10)) \
            .pack(anchor="w", padx=18)
        txt = tk.Text(win, bg="#0A0A12", fg=TEXT, font=("Segoe UI", 10),
                      relief="flat", wrap="word", height=10)
        txt.pack(fill="both", expand=True, padx=18, pady=12)
        txt.insert("1.0", info["notes"] or "(без описания)")
        txt.configure(state="disabled")
        bottom = tk.Frame(win, bg=CARD)
        bottom.pack(fill="x", padx=18, pady=(0, 16))
        self._update_status = tk.Label(bottom, text="", bg=CARD, fg=BRIGHT,
                                       font=("Segoe UI", 9))
        self._update_status.pack(side="left")

        def later():
            self._update_dialog_open = False
            try:
                win.destroy()
            except Exception:
                pass

        def do_update():
            self._update_status.configure(text="Скачиваю…")
            threading.Thread(target=self._do_update_job, args=(info,),
                             daemon=True).start()

        GradButton(bottom, text="ПОЗЖЕ", w=110, h=38,
                   command=later).pack(side="right")
        GradButton(bottom, text="ОБНОВИТЬ", w=140, h=38,
                   command=do_update).pack(side="right", padx=(0, 8))
        win.protocol("WM_DELETE_WINDOW", later)

    def _do_update_job(self, info):
        try:
            zpath = download_update(info["zip_url"])
        except Exception as exc:
            self._post_ui(("status", (self._update_status,
                                       "Не скачалось: %s" % exc)))
            return
        self._post_ui(("status", (self._update_status, "Перезапускаюсь…")))
        try:
            run_updater_and_exit(zpath)
        except Exception as exc:
            self._post_ui(("status", (self._update_status, "Ошибка: %s" % exc)))

    def _manual_update_check(self):
        self._saved_lbl.configure(text="Проверяю обновления…")

        def job():
            try:
                info = check_github_release()
            except Exception as exc:
                self._post_ui(("status", (self._saved_lbl,
                                          "Не смог проверить: %s" % exc)))
                return
            if info:
                self._post_ui(("status", (self._saved_lbl, "")))
                self._post_ui(("dialog", info))
            else:
                self._post_ui(("status", (self._saved_lbl, "У тебя последняя версия")))
        threading.Thread(target=job, daemon=True).start()

    def _header(self):
        bar = tk.Frame(self, bg=PANEL, height=74)
        bar.pack(fill="x")
        bar.pack_propagate(False)

        logo = tk.Canvas(bar, width=48, height=48, bg=PANEL, highlightthickness=0)
        logo.pack(side="left", padx=(18, 14), pady=12)
        round_rect(logo, 1, 1, 47, 47, 13, fill="#161628", outline="#2C2C46", width=1)
        logo.create_oval(6, 6, 42, 29, fill=BLUE, outline="")
        logo.create_oval(11, 22, 44, 44, fill=PURPLE, outline="")
        logo.create_text(24, 22, text="NV", fill="#FFFFFF", font=("Segoe UI", 12, "bold"))

        title = tk.Label(bar, text="NewVisuals", bg=PANEL, fg=TEXT, font=("Segoe UI", 19, "bold"))
        title.pack(side="left", pady=(10, 0))
        sub = tk.Label(bar, text="LAUNCHER  •  1.21.4", bg=PANEL, fg=FAINT,
                       font=("Segoe UI", 8, "bold"))
        sub.pack(side="left", padx=(12, 0), pady=(20, 0))

        pill = tk.Label(bar, text=" ПРОТОТИП ", bg="#1A1A2C", fg=BRIGHT, font=("Segoe UI", 8, "bold"),
                        padx=10, pady=4)
        pill.pack(side="right", padx=20)

        glow = tk.Canvas(bar, width=80, height=6, bg=PANEL, highlightthickness=0)
        glow.pack(side="right", pady=(34, 0))
        grad_horizontal(glow, 0, 2, 80, 4, BLUE, PURPLE)

        line = tk.Canvas(self, height=2, bg=BG, highlightthickness=0)
        line.pack(fill="x")
        self.after(120, lambda: self._draw_header_line(line))

    def _draw_header_line(self, line):
        try:
            width = line.winfo_width()
            if width > 2:
                grad_horizontal(line, 0, 0, width, 2, BLUE, PURPLE)
        except tk.TclError:
            pass

    def _sidebar(self):
        side = tk.Frame(self, bg=BG_DEEP, width=190)
        side.pack(side="left", fill="y")
        side.pack_propagate(False)

        tk.Label(side, text="МЕНЮ", bg=BG_DEEP, fg=FAINT, font=("Segoe UI", 8, "bold")) \
            .pack(anchor="w", padx=22, pady=(18, 8))

        self._nav_btns = {}
        items = [("play", "Играть"), ("modules", "Функции"), ("versions", "Версии"),
                 ("accounts", "Аккаунты"), ("logs", "Логи"), ("settings", "Настройки")]
        for page, label in items:
            btn = NavPill(side, text=label, command=lambda p=page: self._nav_click(p),
                          w=150, h=40, icon=page)
            btn.pack(side="top", pady=3)
            self._nav_btns[page] = btn

        spr = tk.Frame(side, bg=BG_DEEP)
        spr.pack(side="top", fill="both", expand=True)

        card = tk.Frame(side, bg=CARD, highlightthickness=1, highlightbackground=BORDER)
        card.pack(side="bottom", fill="x", padx=16, pady=(0, 18))
        tk.Label(card, text="NewVisuals 1.21.4", bg=CARD, fg=TEXT, font=("Segoe UI", 9, "bold")) \
            .pack(anchor="w", padx=12, pady=(10, 0))
        tk.Label(card, text="сборка RC-прототипа", bg=CARD, fg=FAINT, font=("Segoe UI", 8)) \
            .pack(anchor="w", padx=12, pady=(0, 10))

    def _pages(self):
        self._page_play = self._build_play()
        self._page_modules = self._build_modules()
        self._page_versions = self._build_versions()
        self._page_accounts = self._build_accounts()
        self._page_logs = self._build_logs()
        self._page_settings = self._build_settings()

    def _nav_click(self, page):
        self.show_tab(page)

    def show_tab(self, page):
        for name, frame in (("play", self._page_play), ("modules", self._page_modules),
                            ("versions", self._page_versions),
                            ("accounts", self._page_accounts),
                            ("logs", self._page_logs),
                            ("settings", self._page_settings)):
            if name == page:
                frame.pack(side="left", fill="both", expand=True)
            else:
                frame.pack_forget()
        self._current = page
        for name, btn in self._nav_btns.items():
            btn.set_active(name == page)
        if page == "logs":
            self._refresh_logs()
        if page == "accounts":
            self._rebuild_accounts()

    # ---------- Игра ----------
    def _build_play(self):
        page = tk.Frame(self, bg=BG)
        wrap = tk.Frame(page, bg=BG)
        wrap.pack(fill="both", expand=True, padx=34, pady=30)

        hero = tk.Frame(wrap, bg=BG)
        hero.pack(fill="x")

        hero_text = tk.Frame(hero, bg=BG)
        hero_text.pack(side="left")
        tk.Label(hero_text, text="ГОТОВ К ЗАПУСКУ", bg=BG, fg=GREEN, font=("Segoe UI", 9, "bold")) \
            .pack(anchor="w")
        tk.Label(hero_text, text="Играть в NewVisuals", bg=BG, fg=TEXT, font=("Segoe UI", 27, "bold")) \
            .pack(anchor="w", pady=(4, 0))
        tk.Label(hero_text, text="Лёгкий клиент на 1.21.4 — красивый HUD, мир и удобство.",
                 bg=BG, fg=DIM, font=("Segoe UI", 11)).pack(anchor="w", pady=(4, 0))

        self._status = tk.Label(hero_text, text="", bg=BG, fg=AMBER, font=("Segoe UI", 10))
        self._status.pack(anchor="w", pady=(10, 0))

        btns = tk.Frame(hero, bg=BG)
        btns.pack(side="right", pady=(14, 0))
        self.play_btn = GradButton(btns, text="ИГРАТЬ", w=230, h=66,
                                   command=self._play_click)
        self.play_btn.pack()
        self.kill_btn = GradButton(btns, text="ВЫКЛЮЧИТЬ", w=230, h=44,
                                   command=self._kill_mc,
                                   c1="#FF7B7B", c2="#B33D3D")
        self._mc_proc = None
        self._mc_running = False

        tiles = tk.Frame(wrap, bg=BG)
        tiles.pack(fill="x", pady=(24, 0))
        launcher = self.state["launcher"]
        tdata = [
            ("ПАМЯТЬ", f"{launcher['memory_gb']} ГБ", BLUE),
            ("ПРИОРИТЕТ", launcher["priority"].upper(), PURPLE),
            ("ПАПКА ИГРЫ", launcher["game_dir"] or "—", GREEN),
            ("ВЕРСИЯ", launcher["version"], CYAN),
        ]
        self._tile_values = {}
        for label, value, color in tdata:
            tile = StatTile(tiles, label=label, value=value, color=color)
            tile.pack(side="left", fill="x", expand=True, padx=5)
            self._tile_values[label] = tile

        note = tk.Frame(wrap, bg=CARD, highlightthickness=1, highlightbackground=BORDER)
        note.pack(fill="x", pady=(20, 0))
        self._note_dot = tk.Canvas(note, width=14, height=14, bg=CARD, highlightthickness=0)
        self._note_dot.pack(side="left", padx=(14, 6), pady=12)
        self._note_dot_item = self._note_dot.create_oval(2, 2, 12, 12, fill=AMBER, outline="")
        tk.Label(note, text="Запуск напрямую: Fabric 1.21.4, ник выбирается во вкладке «Аккаунты».",
                 bg=CARD, fg=DIM, font=("Segoe UI", 10)).pack(side="left", pady=11)
        tk.Label(note, text="ЗАПУСК РАБОТАЕТ", bg="#12331F", fg=GREEN, font=("Segoe UI", 8, "bold"),
                 padx=8, pady=3).pack(side="right", padx=14, pady=(9, 0))

        self._pulse()

        return page

    def _play_click(self):
        if self.state["launcher"].get("version") != REAL_VERSION:
            messagebox.showwarning("Версия", VERSION_WARN)
            return
        if self._mc_proc is not None and self._mc_proc.poll() is None:
            self._status.configure(text="Minecraft уже запущен")
            return
        self._status.configure(text="Применяю функции и запускаю Minecraft…")
        self.update_idletasks()
        try:
            sync_mod_config(self.state["launcher"].get("game_dir", ""), self.state)
        except Exception as exc:
            messagebox.showwarning(
                "Конфиг мода",
                "Не смог записать newvisuals.json: %s\nЗапускаю без применения функций." % exc)
        try:
            self._mc_proc = launch_minecraft(self.state["launcher"],
                                             self.state.get("accounts"))
        except LaunchError as exc:
            self._status.configure(text="")
            messagebox.showerror("Не запустилось", str(exc))
            return
        except Exception as exc:
            self._status.configure(text="")
            messagebox.showerror("Не запустилось", "Неожиданная ошибка: %s" % exc)
            return
        self._mc_running = True
        self._status.configure(text="Minecraft запущен. Приятной игры!")
        self._show_kill(True)
        self._hidden_by_launch = bool(self.state["launcher"].get("hide_on_launch", True))
        if self._hidden_by_launch:
            try:
                self.withdraw()
            except Exception:
                pass

    def _show_kill(self, show):
        try:
            if show:
                self.kill_btn.pack(pady=(10, 0))
            else:
                self.kill_btn.pack_forget()
        except Exception:
            pass

    def _kill_mc(self):
        proc = self._mc_proc
        if proc is None:
            return
        self._status.configure(text="Закрываю Minecraft…")
        try:
            proc.terminate()
        except Exception:
            pass
        try:
            proc.wait(timeout=6)
        except Exception:
            try:
                proc.kill()
            except Exception:
                pass

    def _poll_mc(self):
        try:
            running = self._mc_proc is not None and self._mc_proc.poll() is None
        except Exception:
            running = False
        if running and not self._mc_running:
            self._mc_running = True
            try:
                self._status.configure(text="Minecraft запущен. Приятной игры!")
            except Exception:
                pass
            self._show_kill(True)
        elif not running and self._mc_running:
            self._mc_running = False
            self._mc_proc = None
            if getattr(self, "_hidden_by_launch", False):
                self._hidden_by_launch = False
                try:
                    self.deiconify()
                except Exception:
                    pass
            try:
                imported = import_mod_config(
                    self.state["launcher"].get("game_dir", ""), self.state)
            except Exception:
                imported = 0
            if imported:
                self._save()
                self._rebuild_list()
                selected = next(
                    (m for m in MODULES if m["id"] == self._selected_module), None)
                if selected is not None:
                    self._render_settings(selected)
            try:
                if imported:
                    self._status.configure(
                        text="Minecraft закрыт. Функции подтянуты из игры.")
                else:
                    self._status.configure(text="Minecraft закрыт")
            except Exception:
                pass
            self._show_kill(False)
        try:
            self.after(2000, self._poll_mc)
        except Exception:
            pass

    def _on_version_pick(self, idx):
        if idx != 0:
            messagebox.showwarning("Версия", VERSION_WARN)
            self.version_opts.value = 0
            self.version_opts._paint()
        self.state["launcher"]["version"] = REAL_VERSION
        self._save()
        self._refresh_play_tiles()

    def _refresh_play_tiles(self):
        launcher = self.state["launcher"]
        values = {
            "ПАМЯТЬ": "%s ГБ" % launcher["memory_gb"],
            "ПРИОРИТЕТ": launcher["priority"].upper(),
            "ПАПКА ИГРЫ": launcher["game_dir"] or "—",
            "ВЕРСИЯ": launcher["version"],
        }
        for label, value in values.items():
            tile = self._tile_values.get(label)
            if tile is not None:
                tile.set(value)

    # ---------- Версии ----------
    def _build_versions(self):
        page = tk.Frame(self, bg=BG)
        wrap = tk.Frame(page, bg=BG)
        wrap.pack(fill="both", expand=True, padx=34, pady=24)

        tk.Label(wrap, text="Версии", bg=BG, fg=TEXT,
                 font=("Segoe UI", 20, "bold")).pack(anchor="w")
        tk.Label(wrap, text="Рабочая только 1.21.4 — остальные для красоты.",
                 bg=BG, fg=DIM, font=("Segoe UI", 10)).pack(anchor="w", pady=(4, 0))

        card = tk.Frame(wrap, bg=CARD, highlightthickness=1, highlightbackground=BORDER)
        card.pack(fill="x", pady=(18, 0))
        self._title(card, "Выбор версии", BLUE)
        body = tk.Frame(card, bg=CARD)
        body.pack(fill="x", padx=20, pady=(0, 18))
        try:
            ver_index = VERSIONS.index(self.state["launcher"].get("version", REAL_VERSION))
        except ValueError:
            ver_index = 0
        self.version_opts = Options(body, setting={"options": VERSIONS},
                                    value=ver_index, on_change=self._on_version_pick)
        self.version_opts.pack(anchor="w")

        info = tk.Frame(wrap, bg=CARD, highlightthickness=1, highlightbackground=BORDER)
        info.pack(fill="x", pady=(16, 0))
        self._title(info, "Что ставится", PURPLE)
        info_body = tk.Frame(info, bg=CARD)
        info_body.pack(fill="x", padx=20, pady=(0, 18))
        game_dir = self.state["launcher"].get("game_dir", "")
        mod_jar = os.path.join(game_dir, "mods", "newvisuals-1.0.0.jar")
        rows = [("Minecraft", "1.21.4"),
                ("Fabric Loader", "0.19.5"),
                ("Fabric API", "0.119.4"),
                ("Мод", "newvisuals-1.0.0.jar " +
                 ("найден" if os.path.isfile(mod_jar) else "НЕ НАЙДЕН в mods/"))]
        for label, value in rows:
            row = tk.Frame(info_body, bg=CARD)
            row.pack(fill="x", pady=4)
            tk.Label(row, text=label, bg=CARD, fg=FAINT,
                     font=("Segoe UI", 10)).pack(side="left")
            tk.Label(row, text=value, bg=CARD, fg=TEXT,
                     font=("Segoe UI", 10, "bold")).pack(side="right")
        return page

    # ---------- Аккаунты ----------
    def _build_accounts(self):
        page = tk.Frame(self, bg=BG)
        wrap = tk.Frame(page, bg=BG)
        wrap.pack(fill="both", expand=True, padx=34, pady=24)

        tk.Label(wrap, text="Аккаунты", bg=BG, fg=TEXT,
                 font=("Segoe UI", 20, "bold")).pack(anchor="w")
        tk.Label(wrap, text="Ники без пароля. Выбранный ник подставляется при запуске.",
                 bg=BG, fg=DIM, font=("Segoe UI", 10)).pack(anchor="w", pady=(4, 0))

        self._acc_list = tk.Frame(wrap, bg=BG)
        self._acc_list.pack(fill="both", expand=True, pady=(16, 0))

        add_row = tk.Frame(wrap, bg=CARD, highlightthickness=1, highlightbackground=BORDER)
        add_row.pack(fill="x", pady=(12, 0))
        self._title(add_row, "Новый аккаунт", GREEN)
        add_body = tk.Frame(add_row, bg=CARD)
        add_body.pack(fill="x", padx=20, pady=(0, 18))
        self._acc_var = tk.StringVar()
        nick = tk.Entry(add_body, textvariable=self._acc_var, bg="#151527", fg=TEXT,
                        relief="flat", insertbackground=TEXT, font=("Segoe UI", 11),
                        highlightthickness=0, width=24)
        nick.pack(side="left", ipady=6)
        nick.bind("<Return>", lambda e: self._add_account())
        add_btn = tk.Button(add_body, text="Добавить", bg=ROW, fg=TEXT, relief="flat",
                            font=("Segoe UI", 10, "bold"),
                            activebackground=ROW_HOVER, activeforeground=TEXT,
                            cursor="hand2", padx=16, pady=4,
                            command=self._add_account)
        add_btn.pack(side="left", padx=(10, 0))

        self._rebuild_accounts()
        return page

    def _rebuild_accounts(self):
        for child in self._acc_list.winfo_children():
            child.destroy()
        selected = self.state["launcher"].get("account", "")
        for acc in self.state.get("accounts", []):
            name = acc.get("name", "")
            is_sel = name == selected
            card = tk.Frame(self._acc_list, bg=CARD if is_sel else ROW,
                            highlightthickness=1,
                            highlightbackground=BLUE if is_sel else BORDER)
            card.pack(fill="x", pady=4)
            dot = tk.Canvas(card, width=10, height=34, bg=card.cget("bg"),
                            highlightthickness=0)
            dot.pack(side="left", padx=(12, 8))
            dot.create_oval(1, 12, 9, 20,
                            fill=GREEN if is_sel else FAINT, outline="")
            tk.Label(card, text=name, bg=card.cget("bg"), fg=TEXT,
                     font=("Segoe UI", 12, "bold"), anchor="w").pack(side="left")
            if is_sel:
                tk.Label(card, text="• выбран", bg=card.cget("bg"), fg=GREEN,
                         font=("Segoe UI", 9, "bold")).pack(side="left", padx=(10, 0))
            tk.Label(card, text=acc.get("uuid", "")[:8] + "…", bg=card.cget("bg"),
                     fg=FAINT, font=("Segoe UI", 9)).pack(side="left", padx=(10, 0))
            if len(self.state.get("accounts", [])) > 1:
                tk.Button(card, text="✕", bg=card.cget("bg"), fg=FAINT, relief="flat",
                          font=("Segoe UI", 9, "bold"), cursor="hand2",
                          activebackground=ROW_HOVER, activeforeground=RED,
                          command=lambda n=name: self._delete_account(n)) \
                    .pack(side="right", padx=10)
            for w in (card, dot):
                w.bind("<Button-1>", lambda e, n=name: self._select_account(n))

    def _select_account(self, name):
        self.state["launcher"]["account"] = name
        self._save()
        self._rebuild_accounts()

    def _add_account(self):
        name = (self._acc_var.get() or "").strip()
        if not re.fullmatch(r"[A-Za-z0-9_]{3,16}", name):
            messagebox.showerror("Ник", "Ник: 3–16 символов, латиница, цифры и _")
            return
        names = [a.get("name") for a in self.state.get("accounts", [])]
        if name in names:
            messagebox.showerror("Ник", "Такой аккаунт уже есть")
            return
        self.state["accounts"].append({"name": name, "uuid": _offline_uuid(name)})
        self.state["launcher"]["account"] = name
        self._acc_var.set("")
        self._save()
        self._rebuild_accounts()

    def _delete_account(self, name):
        self.state["accounts"] = [a for a in self.state.get("accounts", [])
                                  if a.get("name") != name]
        if self.state["launcher"].get("account") == name:
            rest = self.state["accounts"]
            self.state["launcher"]["account"] = rest[0]["name"] if rest else ""
        self._save()
        self._rebuild_accounts()

    # ---------- Логи ----------
    def _build_logs(self):
        page = tk.Frame(self, bg=BG)
        wrap = tk.Frame(page, bg=BG)
        wrap.pack(fill="both", expand=True, padx=34, pady=24)

        top = tk.Frame(wrap, bg=BG)
        top.pack(fill="x")
        tk.Label(top, text="Логи", bg=BG, fg=TEXT,
                 font=("Segoe UI", 20, "bold")).pack(side="left")
        tk.Button(top, text="Обновить", bg=ROW, fg=TEXT, relief="flat",
                  font=("Segoe UI", 10, "bold"), cursor="hand2",
                  activebackground=ROW_HOVER, activeforeground=TEXT,
                  padx=14, pady=4, command=self._refresh_logs).pack(side="right")

        body = tk.Frame(wrap, bg=BG)
        body.pack(fill="both", expand=True, pady=(16, 0))

        left = tk.Frame(body, bg=BG, width=250)
        left.pack(side="left", fill="y")
        left.pack_propagate(False)
        tk.Label(left, text="КРАШ-РЕПОРТЫ", bg=BG, fg=FAINT,
                 font=("Segoe UI", 8, "bold")).pack(anchor="w", pady=(0, 6))
        self._crash_list = tk.Frame(left, bg=BG)
        self._crash_list.pack(fill="both", expand=True)

        right = tk.Frame(body, bg=CARD, highlightthickness=1, highlightbackground=BORDER)
        right.pack(side="left", fill="both", expand=True, padx=(16, 0))
        self._log_title = tk.Label(right, text="latest.log", bg=CARD, fg=TEXT,
                                   font=("Segoe UI", 11, "bold"))
        self._log_title.pack(anchor="w", padx=14, pady=(10, 0))
        text_frame = tk.Frame(right, bg=CARD)
        text_frame.pack(fill="both", expand=True, padx=14, pady=10)
        scroll = tk.Scrollbar(text_frame)
        scroll.pack(side="right", fill="y")
        self._log_text = tk.Text(text_frame, bg="#0A0A12", fg=DIM,
                                 font=("Consolas", 9), relief="flat",
                                 wrap="none", yscrollcommand=scroll.set,
                                 state="disabled")
        self._log_text.pack(side="left", fill="both", expand=True)
        scroll.config(command=self._log_text.yview)
        return page

    def _refresh_logs(self):
        if getattr(self, "_crash_list", None) is None:
            return
        for child in self._crash_list.winfo_children():
            child.destroy()
        game_dir = self.state["launcher"].get("game_dir", "")
        crash_dir = os.path.join(game_dir, "crash-reports")
        files = []
        try:
            for name in os.listdir(crash_dir):
                if name.endswith(".txt"):
                    full = os.path.join(crash_dir, name)
                    files.append((os.path.getmtime(full), full))
        except Exception:
            pass
        files.sort(reverse=True)
        latest = tk.Button(self._crash_list, text="latest.log (текущий)", bg=ROW, fg=TEXT,
                           relief="flat", font=("Segoe UI", 9), anchor="w",
                           activebackground=ROW_HOVER, activeforeground=TEXT,
                           cursor="hand2",
                           command=lambda: self._show_log_file(
                               os.path.join(game_dir, "logs", "latest.log"),
                               "latest.log", tail=250))
        latest.pack(fill="x", pady=2)
        if not files:
            tk.Label(self._crash_list, text="Крашей нет — и это хорошо.",
                     bg=BG, fg=FAINT, font=("Segoe UI", 9)).pack(anchor="w", pady=6)
        for _, full in files[:30]:
            name = os.path.basename(full)
            btn = tk.Button(self._crash_list, text=name, bg=ROW, fg=AMBER,
                            relief="flat", font=("Segoe UI", 9), anchor="w",
                            activebackground=ROW_HOVER, activeforeground=AMBER,
                            cursor="hand2",
                            command=lambda p=full, n=name: self._show_log_file(p, n))
            btn.pack(fill="x", pady=2)
        self._show_log_file(os.path.join(game_dir, "logs", "latest.log"),
                            "latest.log", tail=250)

    def _show_log_file(self, path, title, tail=None):
        try:
            with open(path, encoding="utf-8", errors="replace") as f:
                if tail:
                    lines = f.readlines()[-tail:]
                    text = "".join(lines)
                else:
                    text = f.read()
            if not text.strip():
                text = "(файл пустой)"
        except Exception as exc:
            text = "Не смог прочитать файл: %s" % exc
        try:
            self._log_title.configure(text=title)
            self._log_text.configure(state="normal")
            self._log_text.delete("1.0", "end")
            self._log_text.insert("1.0", text)
            self._log_text.see("end")
            self._log_text.configure(state="disabled")
        except Exception:
            pass

    def _pulse(self):
        step = getattr(self, "_pulse_step", 0) + 1
        self._pulse_step = step
        try:
            self._drain_ui_queue()
        except Exception:
            pass
        try:
            if self._current == "play" and self._note_dot is not None:
                t = (step % 20) / 20
                self._note_dot.itemconfigure(self._note_dot_item, fill=hex_blend("#3A2A15", AMBER, t))
        except Exception:
            pass
        try:
            self._pulse_after = self.after(90, self._pulse)
        except Exception:
            self._pulse_after = None

    # ---------- Функции ----------
    def _build_modules(self):
        page = tk.Frame(self, bg=BG)
        wrap = tk.Frame(page, bg=BG)
        wrap.pack(fill="both", expand=True, padx=34, pady=24)

        top = tk.Frame(wrap, bg=BG)
        top.pack(fill="x")
        tk.Label(top, text="Функции", bg=BG, fg=TEXT, font=("Segoe UI", 20, "bold")).pack(side="left")
        tk.Label(top, text="Включите модули и настройте их под себя.",
                 bg=BG, fg=DIM, font=("Segoe UI", 10)).pack(side="left", padx=(12, 0), pady=(8, 0))
        self._count_label = tk.Label(top, text="", bg=BG, fg=FAINT, font=("Segoe UI", 10))
        self._count_label.pack(side="right", pady=(8, 0))

        chips = tk.Frame(wrap, bg=BG)
        chips.pack(fill="x", pady=(14, 0))
        self._chip_btns = []
        all_chip = Chip(chips, text="Все", color=BRIGHT, command=lambda: self._set_filter("Все"))
        all_chip.pack(side="left")
        self._chip_btns.append(("Все", all_chip))
        for cid, cname in CATEGORIES:
            chip = Chip(chips, text=cname, color=CAT_COLORS[cid],
                        command=lambda c=cid: self._set_filter(c))
            chip.pack(side="left", padx=(6, 0))
            self._chip_btns.append((cid, chip))

        body = tk.Frame(wrap, bg=BG)
        body.pack(fill="both", expand=True, pady=(16, 0))

        # список
        left = tk.Frame(body, bg=BG, width=320)
        left.pack(side="left", fill="y")
        left.pack_propagate(False)

        search_row = tk.Frame(left, bg=CARD, highlightthickness=1, highlightbackground=BORDER)
        search_row.pack(fill="x")
        tk.Label(search_row, text="🔎", bg=CARD, fg=FAINT, font=("Segoe UI", 10)).pack(side="left", padx=(12, 6))
        self._search_var = tk.StringVar()
        entry = tk.Entry(search_row, textvariable=self._search_var, bg=CARD, fg=TEXT,
                         relief="flat", insertbackground=TEXT, font=("Segoe UI", 10),
                         highlightthickness=0, width=24)
        entry.pack(side="left", fill="x", expand=True, ipady=5, padx=(0, 10))
        entry.bind("<KeyRelease>", lambda e: self._set_search(self._search_var.get()))

        self._list_canvas = tk.Canvas(left, bg=BG, highlightthickness=0)
        self._list_canvas.pack(fill="both", expand=True, pady=(10, 0))
        self._list_frame = tk.Frame(self._list_canvas, bg=BG)
        self._list_window = self._list_canvas.create_window((0, 0), window=self._list_frame, anchor="nw")

        self._list_frame.bind("<Configure>",
                              lambda e: self._list_canvas.configure(scrollregion=self._list_canvas.bbox("all")))
        self._list_canvas.bind("<Configure>",
                               lambda e: self._list_canvas.itemconfig(self._list_window, width=e.width))
        self._list_canvas.bind("<Enter>", lambda e: self._bind_wheel(self._list_canvas))
        self._list_canvas.bind("<Leave>", lambda e: self._unbind_wheel())

        self._module_rows = {}
        self._rebuild_list()

        # панель настроек
        right = tk.Frame(body, bg=BG, width=400)
        right.pack(side="left", fill="y", padx=(16, 0))
        right.pack_propagate(False)

        self._card = tk.Frame(right, bg=CARD, highlightthickness=1, highlightbackground=BORDER)
        self._card.pack(fill="both", expand=True)

        self._panel_header = tk.Label(self._card, text="", bg=CARD, fg=TEXT,
                                      font=("Segoe UI", 15, "bold"))
        self._panel_desc = tk.Label(self._card, text="", bg=CARD, fg=DIM, font=("Segoe UI", 9,),
                                    justify="left", anchor="w")
        self._panel_sep = tk.Frame(self._card, bg=BORDER, height=1)

        self._settings_wrap = tk.Frame(self._card, bg=CARD)
        self._settings_wrap.pack(fill="both", expand=True, padx=22, pady=(0, 18))
        self._panel_header.configure(text="Выберите функцию")
        self._panel_desc.configure(
            text="Кнопка ВКЛ у названия включает сразу. Нажмите на строку, чтобы настроить.")
        self._panel_header.pack(anchor="w", padx=22, pady=(18, 0))
        self._panel_desc.pack(fill="x", padx=22, pady=(4, 0))

        self._select_module(None)
        self._update_count()

        return page

    def _bind_wheel(self, canv):
        self._list_canvas.bind_all("<MouseWheel>",
                                   lambda e: self._list_canvas.yview_scroll(int(-e.delta / 120) * 2, "units"))

    def _unbind_wheel(self):
        self._list_canvas.unbind_all("<MouseWheel>")

    def _visible_modules(self):
        for m in MODULES:
            if self._filter != "Все" and m["cat"] != self._filter:
                continue
            if self._search:
                if self._search.lower() not in m["name"].lower():
                    continue
            yield m

    def _rebuild_list(self):
        for child in self._list_frame.winfo_children():
            child.destroy()
        self._module_rows = {}
        for module in self._visible_modules():
            row = tk.Frame(self._list_frame, bg=BG)
            row.pack(fill="x", pady=3)

            entry = self.state["modules"][module["id"]]
            card = tk.Frame(row, bg=CARD if entry["on"] else ROW,
                            highlightthickness=1,
                            highlightbackground=BLUE if entry["on"] else BORDER)
            card.pack(fill="x", padx=(0, 4))

            dot = tk.Canvas(card, width=10, height=34, bg=card.cget("bg"), highlightthickness=0)
            dot.pack(side="left", padx=(12, 8))
            dot.create_oval(1, 12, 9, 20, fill=CAT_COLORS[module["cat"]], outline="")

            name = tk.Label(card, text=module["name"], bg=card.cget("bg"), fg=TEXT,
                            font=("Segoe UI", 10, "bold" if entry["on"] else "normal"),
                            anchor="w")
            name.pack(side="left", fill="both", expand=True, padx=(0, 6))

            toggle = ToggleBtn(card, state=entry["on"],
                                 command=lambda m=module: self._toggle_module(m))
            toggle.pack(side="right", padx=(0, 10))

            for w in (row, card, name, dot, toggle):
                w.bind("<Button-1>", lambda e, m=module: self._select_module(m))
                w.bind("<Enter>", lambda e, c=card, is_on=entry["on"]: c.configure(bg=ROW_HOVER,
                                                                                    highlightbackground=BRIGHT if is_on else "#2A2A46"))
                w.bind("<Leave>", lambda e, c=card, is_on=entry["on"]: c.configure(
                    bg=CARD if is_on else ROW,
                    highlightbackground=BLUE if is_on else BORDER))

            self._module_rows[module["id"]] = card
        self._update_count()

    def _update_count(self):
        on = sum(1 for m in MODULES if self.state["modules"][m["id"]]["on"])
        if self._count_label is not None:
            self._count_label.configure(text=f"включено {on} из {len(MODULES)}")

    def _set_filter(self, cat):
        self._filter = cat
        for cid, chip in self._chip_btns:
            chip.set_active(cid == cat)
        self._rebuild_list()

    def _set_search(self, text):
        self._search = text.strip()
        self._rebuild_list()

    def _toggle_module(self, module):
        entry = self.state["modules"][module["id"]]
        entry["on"] = not entry["on"]
        self._save()
        self._rebuild_list()
        if self._selected_module == module["id"]:
            self._render_settings(module)

    def _select_module(self, module):
        for child in self._settings_wrap.winfo_children():
            child.destroy()
        if module is None:
            self._selected_module = None
            self._panel_header.configure(text="Выберите функцию")
            self._panel_desc.configure(
                text="Кнопка ВКЛ у названия включает сразу. Нажмите на строку, чтобы настроить.")
            self._panel_sep.pack_forget()
            return
        self._selected_module = module["id"]
        self._panel_header.configure(text=module["name"])
        self._panel_desc.configure(text=module["desc"])
        self._panel_header.pack(anchor="w", padx=22, pady=(18, 0), before=self._settings_wrap)
        self._panel_desc.pack(fill="x", padx=22, pady=(4, 0), before=self._settings_wrap)
        self._panel_sep.pack(fill="x", padx=22, pady=(12, 0), before=self._settings_wrap)
        self._render_settings(module)

    def _render_settings(self, module):
        for child in self._settings_wrap.winfo_children():
            child.destroy()
        entry = self.state["modules"][module["id"]]

        on_row = tk.Frame(self._settings_wrap, bg=CARD)
        on_row.pack(fill="x", pady=(0, 8))
        tk.Label(on_row, text="Включить", bg=CARD, fg=TEXT, font=("Segoe UI", 11, "bold")) \
            .pack(side="left")
        Switch(on_row, state=entry["on"], command=lambda: self._toggle_module(module)) \
            .pack(side="right")

        if not module["settings"]:
            tk.Label(self._settings_wrap, text="У этой функции нет дополнительных настроек.",
                     bg=CARD, fg=FAINT, font=("Segoe UI", 10), justify="left", anchor="w") \
                .pack(anchor="w", pady=(12, 0))
            return

        for setting in module["settings"]:
            row = tk.Frame(self._settings_wrap, bg=CARD)
            row.pack(fill="x", pady=7)
            tk.Frame(row, bg=BORDER, height=1).pack(fill="x", pady=(9, 7))
            tk.Label(row, text=setting["label"], bg=CARD, fg=DIM, font=("Segoe UI", 10),
                     width=14, anchor="w").pack(side="left")
            value = entry["settings"].get(setting["id"], setting["default"])
            if setting["type"] == "slider":
                Slider(row, setting=setting, value=value,
                       on_change=lambda v, s=setting: self._set_setting(module, s, v)) \
                    .pack(side="right")
            elif setting["type"] == "bool":
                Switch(row, state=bool(value),
                       command=lambda s=setting: self._set_setting(
                           module, s, not entry["settings"].get(s["id"], s["default"]))) \
                    .pack(side="right")
            elif setting["type"] == "options":
                Options(row, setting=setting, value=value,
                        on_change=lambda v, s=setting: self._set_setting(module, s, v)) \
                    .pack(side="right")
            elif setting["type"] == "color":
                ColorWidget(row, value=value,
                            on_change=lambda c, s=setting: self._set_setting(module, s, c)) \
                    .pack(side="right")
        self._save()

    def _set_setting(self, module, setting, value):
        self.state["modules"][module["id"]]["settings"][setting["id"]] = value
        self._save()

    # ---------- Настройки ----------
    def _build_settings(self):
        page = tk.Frame(self, bg=BG)
        wrap = tk.Frame(page, bg=BG)
        wrap.pack(fill="both", expand=True, padx=34, pady=24)

        tk.Label(wrap, text="Настройки", bg=BG, fg=TEXT, font=("Segoe UI", 20, "bold")).pack(anchor="w")
        tk.Label(wrap, text="Базовые настройки запуска игры.", bg=BG, fg=DIM,
                 font=("Segoe UI", 10)).pack(anchor="w", pady=(4, 0))

        grid = tk.Frame(wrap, bg=BG)
        grid.pack(fill="both", expand=True, pady=(18, 0))

        launcher = self.state["launcher"]
        self._path_vars = {}

        card_hw = tk.Frame(grid, bg=CARD, highlightthickness=1, highlightbackground=BORDER)
        card_hw.pack(side="left", fill="both", expand=True, padx=(0, 8))
        self._title(card_hw, "Запуск", BLUE)
        body_hw = tk.Frame(card_hw, bg=CARD)
        body_hw.pack(fill="both", expand=True, padx=20, pady=(0, 18))
        tk.Label(body_hw, text="Память (ГБ)", bg=CARD, fg=DIM, font=("Segoe UI", 10)) \
            .pack(anchor="w")
        self.mem_slider = Slider(body_hw, setting={"min": 1, "max": 8, "step": 1},
                                 value=launcher["memory_gb"],
                                 on_change=lambda v: self._set_launcher("memory_gb", int(round(v))), wide=True)
        self.mem_slider.pack(fill="x", pady=(6, 16))
        tk.Label(body_hw, text="Приоритет", bg=CARD, fg=DIM, font=("Segoe UI", 10)).pack(anchor="w")
        self.prio = Options(body_hw, setting={"options": ["Низкий", "Обычный", "Высокий"]},
                            value=launcher["priority"],
                            on_change=lambda v: self._set_launcher(
                                "priority", ["Низкий", "Обычный", "Высокий"][v]))
        self.prio.pack(anchor="w", pady=(6, 0))
        hide_row = tk.Frame(body_hw, bg=CARD)
        hide_row.pack(fill="x", pady=(12, 0))
        tk.Label(hide_row, text="Скрывать при запуске", bg=CARD, fg=DIM,
                 font=("Segoe UI", 10)).pack(side="left")
        Switch(hide_row, state=bool(launcher.get("hide_on_launch", True)),
               command=lambda: self._set_launcher(
                   "hide_on_launch",
                   not self.state["launcher"].get("hide_on_launch", True))).pack(side="right")

        card_path = tk.Frame(grid, bg=CARD, highlightthickness=1, highlightbackground=BORDER)
        card_path.pack(side="left", fill="both", expand=True, padx=8)
        self._title(card_path, "Пути", PURPLE)
        body_path = tk.Frame(card_path, bg=CARD)
        body_path.pack(fill="both", expand=True, padx=20, pady=(0, 18))
        self._path_entry(body_path, "Java (JAVA_HOME)", "java_path")
        self._path_entry(body_path, "Папка игры", "game_dir")

        card_info = tk.Frame(grid, bg=CARD, highlightthickness=1, highlightbackground=BORDER)
        card_info.pack(side="left", fill="both", expand=True, padx=8)

        self._title(card_info, "О клиенте", GREEN)
        body_info = tk.Frame(card_info, bg=CARD)
        body_info.pack(fill="both", expand=True, padx=20, pady=(0, 18))
        rows = [("Версия", "1.21.4"), ("Категория", "Косметика и удобство"),
                ("Функций", str(len(MODULES))), ("Лаунчер", LAUNCHER_VERSION),
                ("Статус", "Прототип лаунчера")]
        for label, value in rows:
            r = tk.Frame(body_info, bg=CARD)
            r.pack(fill="x", pady=4)
            tk.Label(r, text=label, bg=CARD, fg=FAINT, font=("Segoe UI", 10)).pack(side="left")
            tk.Label(r, text=value, bg=CARD, fg=TEXT, font=("Segoe UI", 10, "bold")).pack(side="right")
        tk.Button(body_info, text="Проверить обновления", bg=ROW, fg=TEXT, relief="flat",
                  font=("Segoe UI", 10, "bold"), cursor="hand2",
                  activebackground=ROW_HOVER, activeforeground=TEXT,
                  padx=12, pady=5, command=self._manual_update_check).pack(anchor="w", pady=(10, 0))

        self._saved_lbl = tk.Label(wrap, text="", bg=BG, fg=GREEN, font=("Segoe UI", 10, "bold"))
        self._saved_lbl.pack(anchor="e", pady=(12, 0))
        save = GradButton(wrap, text="СОХРАНИТЬ", w=180, h=44, command=self._save_settings)
        save.pack(anchor="e")

        return page

    def _title(self, parent, text, color):
        head = tk.Frame(parent, bg=CARD)
        head.pack(fill="x", padx=20, pady=(18, 14))
        tk.Frame(head, bg=color, width=3).pack(side="left", fill="y")
        tk.Label(head, text=text, bg=CARD, fg=TEXT, font=("Segoe UI", 13, "bold")) \
            .pack(side="left", padx=(10, 0))

    def _path_entry(self, parent, label, key):
        row = tk.Frame(parent, bg=CARD)
        row.pack(fill="x", pady=6)
        tk.Label(row, text=label, bg=CARD, fg=DIM, font=("Segoe UI", 10)).pack(anchor="w", pady=(0, 4))
        entry_row = tk.Frame(row, bg=CARD)
        entry_row.pack(fill="x")
        var = tk.StringVar(value=self.state["launcher"].get(key, ""))
        ent = tk.Entry(entry_row, textvariable=var, bg="#151527", fg=TEXT, relief="flat",
                       insertbackground=TEXT, font=("Segoe UI", 9), highlightthickness=0)
        ent.pack(side="left", fill="x", expand=True, ipady=6)
        btn = tk.Button(entry_row, text="…", bg=ROW, fg=TEXT, relief="flat", font=("Segoe UI", 10, "bold"),
                        activebackground=ROW_HOVER, activeforeground=TEXT, cursor="hand2",
                        command=lambda: self._pick_path(var))
        btn.pack(side="left", padx=(6, 0))
        self._path_vars[key] = var

    def _pick_path(self, var):
        path = filedialog.askdirectory(title="Выберите папку")
        if path:
            var.set(path)

    def _set_launcher(self, key, value):
        self.state["launcher"][key] = value
        self._save()
        if getattr(self, "_tile_values", None):
            self._refresh_play_tiles()

    def _save_settings(self):
        for key, var in self._path_vars.items():
            self.state["launcher"][key] = var.get().strip()
        self._save()
        if getattr(self, "_tile_values", None):
            self._refresh_play_tiles()
        self._saved_lbl.configure(text="Настройки сохранены")
        self.after(2500, lambda: self._saved_lbl.configure(text=""))


# ---------- виджеты ----------
class NavPill(tk.Canvas):
    def __init__(self, master, text, command, w=150, h=40, icon=""):
        super().__init__(master, width=w, height=h, bg=master.cget("bg"), highlightthickness=0)
        self.text = text
        self.command = command
        self.active = False
        self.hover = False
        self.bind("<Button-1>", lambda e: self.command())
        self.bind("<Enter>", lambda e: self._hover(True))
        self.bind("<Leave>", lambda e: self._hover(False))
        self._draw()

    def set_active(self, value):
        self.active = value
        self._draw()

    def _hover(self, value):
        self.hover = value
        self._draw()

    def _draw(self):
        self.delete("all")
        if self.active:
            grad_horizontal(self, 0, 0, 150, 40, BLUE, PURPLE)
            round_rect(self, 0, 0, 150, 40, 11, fill=None, outline="#DFF0FF", width=1)
            self.create_text(76, 21, text=self.text, fill="#0B0B18", font=("Segoe UI", 11, "bold"))
            self.create_text(75, 20, text=self.text, fill="#FFFFFF", font=("Segoe UI", 11, "bold"))
        else:
            fill = "#12121F" if self.hover else master_bg(self)
            round_rect(self, 0, 0, 150, 40, 11, fill=fill, outline="#202038")
            self.create_text(75, 20, text=self.text, fill=TEXT if self.hover else DIM,
                             font=("Segoe UI", 11))


def master_bg(widget):
    try:
        return widget.master.cget("bg")
    except Exception:
        return BG


class Chip(tk.Canvas):
    def __init__(self, master, text, color, command, w=None, h=26):
        super().__init__(master, height=h, bg=master.cget("bg"), highlightthickness=0)
        self.text = text
        self.color = color
        self.command = command
        self.active = False
        self.w = w
        self.bind("<Button-1>", lambda e: self.command())
        self.bind("<Enter>", lambda e: self.configure(cursor="hand2"))
        pad = 14
        f = ("Segoe UI", 9, "bold")
        if w is None:
            w = pad * 2 + int(self._textlen(text, f)) + 10
        self.configure(width=w)
        self._cw = w
        self._draw()

    def _textlen(self, text, f):
        try:
            import tkinter.font as tkfont
            return tkfont.Font(font=f).measure(text)
        except Exception:
            return len(text) * 8

    def set_active(self, value):
        self.active = value
        self._draw()

    def _draw(self):
        self.delete("all")
        import tkinter.font as tkfont
        f = ("Segoe UI", 9, "bold")
        tw = tkfont.Font(font=f).measure(self.text)
        w = self._cw if self._cw else 14 * 2 + tw + 10
        if self.active:
            grad_horizontal(self, 0, 0, w, 26, self.color, hex_blend(self.color, PURPLE, 0.5))
            round_rect(self, 0, 0, w, 26, 13, fill=None, outline="#E8F6FF", width=1)
            self.create_text(w / 2 + 1, 14, text=self.text, fill="#0B0B18", font=f)
            self.create_text(w / 2, 13, text=self.text, fill="#FFFFFF", font=f)
        else:
            round_rect(self, 0, 0, w, 26, 13, fill="#141421", outline="#24243C")
            self.create_text(w / 2, 13, text=self.text, fill=DIM, font=f)


class GradButton(tk.Canvas):
    def __init__(self, master, text, command, w, h, c1=None, c2=None):
        super().__init__(master, width=w, height=h, bg=master.cget("bg"), highlightthickness=0)
        self.text = text
        self.command = command
        self.hover = False
        self.w = w
        self.h = h
        self.c1 = c1 or BLUE
        self.c2 = c2 or PURPLE
        self.bind("<Button-1>", lambda e: self.command())
        self.bind("<Enter>", lambda e: self._enter(True))
        self.bind("<Leave>", lambda e: self._enter(False))
        self._draw()

    def _enter(self, v):
        self.hover = v
        self._draw()

    def _draw(self):
        self.delete("all")
        c1, c2 = (BRIGHT, self.c1) if self.hover else (self.c1, self.c2)
        grad_horizontal(self, 0, 0, self.w, self.h, c1, c2)
        round_rect(self, 0, 0, self.w, self.h, 16, outline="#DFF0FF", width=1)
        self.create_text(self.w / 2 + 1, self.h / 2 + 1, text=self.text, fill="#0B0B18",
                         font=("Segoe UI", 14, "bold"))
        self.create_text(self.w / 2, self.h / 2, text=self.text, fill="#FFFFFF",
                         font=("Segoe UI", 14, "bold"))


class StatTile(tk.Frame):
    def __init__(self, master, label, value, color):
        super().__init__(master, bg=CARD, highlightthickness=1, highlightbackground=BORDER)
        self.value = value
        self.color_label = None
        head = tk.Frame(self, bg=CARD)
        head.pack(fill="x", padx=14, pady=(12, 0))
        tk.Frame(head, bg=color, width=10).pack(side="left")
        tk.Label(head, text=label, bg=CARD, fg=FAINT, font=("Segoe UI", 8, "bold")) \
            .pack(side="left", padx=(8, 0))
        self.color_label = tk.Label(self, text=value, bg=CARD, fg=TEXT, font=("Segoe UI", 13, "bold"),
                                    anchor="w", justify="left", wraplength=200)
        self.color_label.pack(fill="x", padx=14, pady=(6, 12))

    def set(self, value):
        self.value = value
        self.color_label.configure(text=value)


class Switch(tk.Frame):
    def __init__(self, master, state=False, command=None):
        super().__init__(master, bg=master.cget("bg"))
        self.state = state
        self.command = command
        self.canvas = tk.Canvas(self, width=40, height=22, bg=master.cget("bg"),
                                highlightthickness=0, cursor="hand2")
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self._click)
        self._draw()

    def _draw(self):
        c = self.canvas
        c.delete("all")
        fill = BLUE if self.state else TRACK
        round_rect(c, 2, 2, 38, 20, 10, fill=fill, outline="#2A2A46")
        if self.state:
            c.create_oval(22, 5, 36, 19, fill="#FFFFFF", outline="")
        else:
            c.create_oval(4, 5, 18, 19, fill="#5B5B72", outline="")

    def _click(self, e):
        self.state = not self.state
        self._draw()
        if self.command:
            self.command()


class ToggleBtn(tk.Canvas):
    """Одна большая кнопка ВКЛ/ВЫКЛ у функции — нажал и готово."""

    def __init__(self, master, state=False, command=None, w=76, h=30):
        super().__init__(master, width=w, height=h, bg=master.cget("bg"),
                         highlightthickness=0, cursor="hand2")
        self.state = state
        self.command = command
        self.w = w
        self.h = h
        self.bind("<Button-1>", self._click)
        self._draw()

    def _draw(self):
        self.delete("all")
        if self.state:
            grad_horizontal(self, 0, 0, self.w, self.h, BLUE, PURPLE)
            round_rect(self, 0, 0, self.w, self.h, 15,
                       fill=None, outline="#DFF0FF", width=1)
            self.create_text(self.w / 2 + 1, self.h / 2 + 1, text="ВКЛ",
                             fill="#0B0B18", font=("Segoe UI", 10, "bold"))
            self.create_text(self.w / 2, self.h / 2, text="ВКЛ",
                             fill="#FFFFFF", font=("Segoe UI", 10, "bold"))
        else:
            round_rect(self, 0, 0, self.w, self.h, 15,
                       fill=TRACK, outline="#2A2A46", width=1)
            self.create_text(self.w / 2, self.h / 2, text="ВЫКЛ",
                             fill=DIM, font=("Segoe UI", 10, "bold"))

    def _click(self, e):
        if self.command:
            self.command()


class Slider(tk.Frame):
    def __init__(self, master, setting=None, value=None, on_change=None, label=None, wide=False, extra=None):
        super().__init__(master, bg=master.cget("bg"))
        self.on_change = on_change
        if extra:
            lo, hi, step = extra
            setting = {"min": lo, "max": hi, "step": step}
        self.setting = setting
        self.min = float(setting["min"])
        self.max = float(setting["max"])
        self.step = float(setting["step"])
        if value is not None:
            self.value = float(value)
        else:
            self.value = float(setting.get("default", setting["min"]))
        self.drag = False
        self.track_w = 180 if wide else 150

        if label is not None:
            tk.Label(self, text=label, bg=master.cget("bg"), fg=DIM, font=("Segoe UI", 10),
                     width=16, anchor="w").pack(side="left")

        self.canvas = tk.Canvas(self, width=self.track_w + 70, height=24,
                                bg=master.cget("bg"), highlightthickness=0, cursor="hand2")
        self.canvas.pack(side="left")
        self.canvas.bind("<Button-1>", self._press)
        self.canvas.bind("<B1-Motion>", self._drag)
        self.canvas.bind("<ButtonRelease-1>", self._release)
        self._draw()

    def _clamp(self, v):
        return min(self.max, max(self.min, v))

    def _draw(self):
        c = self.canvas
        c.delete("all")
        y = 13
        w = self.track_w
        c.create_line(10, y, w - 10, y, fill=TRACK, width=5)
        frac = min(max((self.value - self.min) / (self.max - self.min), 0), 1)
        end = 10 + frac * (w - 20)
        if end > 10:
            grad_horizontal(c, 10, y - 2, int(end), y + 2, BLUE, PURPLE)
        c.create_oval(end - 7, y - 7, end + 7, y + 7, fill="#2A3360", outline=BLUE, width=1)
        c.create_oval(end - 3, y - 3, end + 3, y + 3, fill=BRIGHT, outline="")
        text = fmt_val(self.value, self.step)
        c.create_text(w + 42, y, text=text, fill=BRIGHT, font=("Segoe UI", 9, "bold"))

    def _value_at(self, x):
        w = self.track_w
        frac = (x - 10) / (w - 20)
        frac = min(max(frac, 0), 1)
        raw = self.min + frac * (self.max - self.min)
        steps = round((raw - self.min) / self.step)
        return self._clamp(self.min + steps * self.step)

    def _press(self, e):
        self.drag = True
        self.value = self._value_at(e.x)
        self._draw()
        if self.on_change:
            self.on_change(self.value)

    def _drag(self, e):
        if self.drag:
            self.value = self._value_at(e.x)
            self._draw()
            if self.on_change:
                self.on_change(self.value)

    def _release(self, e):
        self.drag = False
        self._draw()
        if self.on_change:
            self.on_change(self.value)


class Options(tk.Frame):
    def __init__(self, master, setting=None, value=0, on_change=None):
        super().__init__(master, bg=master.cget("bg"))
        self.on_change = on_change
        self.options = setting["options"]
        if isinstance(value, int):
            self.value = value if 0 <= value < len(self.options) else 0
        else:
            self.value = self.options.index(value) if value in self.options else 0
        self.btns = []
        if len(self.options) > 4:
            for start in range(0, len(self.options), 4):
                chunk = tk.Frame(self, bg=master.cget("bg"))
                chunk.pack(anchor="w", pady=1)
                for i in range(start, min(start + 4, len(self.options))):
                    chip = Chip(chunk, text=self.options[i], color=BLUE,
                                command=lambda idx=i: self._select(idx), h=24)
                    chip.pack(side="left", padx=1)
                    self.btns.append(chip)
        else:
            for i, opt in enumerate(self.options):
                chip = Chip(self, text=opt, color=BLUE, command=lambda idx=i: self._select(idx), h=24)
                chip.pack(side="left", padx=1)
                self.btns.append(chip)
        self._paint()

    def _select(self, idx):
        self.value = idx
        self._paint()
        if self.on_change:
            self.on_change(self.value)

    def _paint(self):
        for i, b in enumerate(self.btns):
            b.set_active(i == self.value)


class ColorWidget(tk.Frame):
    def __init__(self, master, value="#4D9BFF", on_change=None):
        super().__init__(master, bg=master.cget("bg"))
        self.value = value
        self.on_change = on_change
        self.swatch = tk.Canvas(self, width=26, height=18, bg=master.cget("bg"),
                                highlightthickness=0, cursor="hand2")
        self.swatch.pack(side="left")
        self.swatch.bind("<Button-1>", self._pick)
        self.label = tk.Label(self, text=value, bg=master.cget("bg"), fg=DIM, font=("Segoe UI", 9))
        self.label.pack(side="left", padx=(5, 0))
        self._draw()

    def _draw(self):
        self.swatch.delete("all")
        round_rect(self.swatch, 0, 0, 26, 18, 5, fill=self.value, outline="#2A2A46")

    def _pick(self, e):
        rgb, hexv = colorchooser.askcolor(color=self.value, title="Цвет")
        if hexv:
            self.value = hexv
            self.label.configure(text=hexv)
            self._draw()
            if self.on_change:
                self.on_change(hexv)


if __name__ == "__main__":
    app = App()
    app.mainloop()