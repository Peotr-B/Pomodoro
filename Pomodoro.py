# -*- coding: utf-8 -*-
"""
Created on Mon Dec 22 11:38:43 2025
Pomodoro.py
С использованием ChatGPT
D:\ИИ\Нейросети\Программирование с нейросетью\Помодоро с нейросетью
Scriptor
@author: рс
"""

import tkinter as tk
import threading
import time
import json
import os
import winsound

from pystray import Icon, Menu, MenuItem
from PIL import Image, ImageDraw

# ================== НАСТРОЙКИ ==================
SETTINGS_FILE = "settings.json"

DEFAULT_WORK_MIN = 25
DEFAULT_BREAK_MIN = 5

COLOR_BG = "#e6f4a3"

COLOR_WORK_ACTIVE = "#ff9800"
COLOR_WORK_INACTIVE = "#ffd8a8"

COLOR_BREAK_ACTIVE = "#00bcd4"
COLOR_BREAK_INACTIVE = "#b2ebf2"

COLOR_STOP = "#8d6e63"
COLOR_EXIT = "#e53935"

# ================== СОСТОЯНИЕ ==================
current_mode = None        # "work" / "break"
timer_running = False
remaining_seconds = 0
tray_icon = None

# ================== СОХРАНЕНИЕ ==================
def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"work": DEFAULT_WORK_MIN, "break": DEFAULT_BREAK_MIN}

def save_settings():
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump({
            "work": int(entry_work.get()),
            "break": int(entry_break.get())
        }, f)

settings = load_settings()

# ================== ТАЙМЕР ==================
def start_timer():
    global timer_running
    if timer_running or remaining_seconds <= 0:
        return
    timer_running = True
    update_mode_buttons()
    threading.Thread(target=timer_loop, daemon=True).start()

def pause_timer():
    global timer_running
    timer_running = False
    update_mode_buttons()

def timer_loop():
    global remaining_seconds, timer_running
    while timer_running and remaining_seconds > 0:
        time.sleep(1)
        remaining_seconds -= 1
        update_timer_label()

    if remaining_seconds == 0:
        timer_running = False
        winsound.PlaySound("SystemHand", winsound.SND_ALIAS)
        reset_to_default(current_mode)
        update_mode_buttons()

def reset_to_default(mode):
    global remaining_seconds
    if mode == "work":
        remaining_seconds = int(entry_work.get()) * 60
    elif mode == "break":
        remaining_seconds = int(entry_break.get()) * 60
    update_timer_label()

def update_timer_label():
    m = remaining_seconds // 60
    s = remaining_seconds % 60
    label_timer.config(text=f"{m:02d}:{s:02d}")

# ================== РЕЖИМЫ ==================
def start_mode(mode):
    global current_mode

    if current_mode != mode:
        pause_timer()
        current_mode = mode
        reset_to_default(mode)
    else:
        if remaining_seconds <= 0:
            reset_to_default(mode)

    start_timer()

def start_work():
    start_mode("work")

def start_break():
    start_mode("break")

# ================== ЦВЕТА КНОПОК ==================
def update_mode_buttons():
    if current_mode == "work":
        btn_work.config(bg=COLOR_WORK_ACTIVE if timer_running else COLOR_WORK_INACTIVE)
        btn_break.config(bg=COLOR_BREAK_INACTIVE)
    elif current_mode == "break":
        btn_break.config(bg=COLOR_BREAK_ACTIVE if timer_running else COLOR_BREAK_INACTIVE)
        btn_work.config(bg=COLOR_WORK_INACTIVE)
    else:
        btn_work.config(bg=COLOR_WORK_INACTIVE)
        btn_break.config(bg=COLOR_BREAK_INACTIVE)

# ================== ТРЕЙ ==================
def create_tray_image():
    img = Image.new("RGB", (64, 64), "yellow")
    d = ImageDraw.Draw(img)
    d.ellipse((8, 8, 56, 56), fill="orange")
    return img

def hide_window():
    root.withdraw()
    run_tray()

def show_window(icon=None, item=None):
    root.after(0, root.deiconify)

def exit_app(icon=None, item=None):
    pause_timer()
    save_settings()
    if tray_icon:
        tray_icon.stop()
    root.destroy()

def run_tray():
    global tray_icon
    if tray_icon:
        return

    tray_icon = Icon(
        "Pomodoro",
        create_tray_image(),
        "Таймер помодоро",
        menu=Menu(
            MenuItem("Открыть", show_window, default=True),
            MenuItem("Выход", exit_app)
        )
    )
    threading.Thread(target=tray_icon.run, daemon=True).start()

# ================== UI ==================
root = tk.Tk()
root.title("Таймер помодоро")
root.geometry("300x225")
root.configure(bg=COLOR_BG)
root.protocol("WM_DELETE_WINDOW", hide_window)

tk.Label(
    root,
    text="Таймер помодоро\nэффективность в работе",
    font=("Arial", 14, "bold"),
    bg=COLOR_BG,
    justify="center"
).pack(pady=5)

frame_settings = tk.Frame(root, bg=COLOR_BG)
frame_settings.pack()

tk.Label(frame_settings, text="Работа (мин)", bg=COLOR_BG).grid(row=0, column=0)
entry_work = tk.Entry(frame_settings, width=5)
entry_work.insert(0, settings["work"])
entry_work.grid(row=0, column=1)

tk.Label(frame_settings, text="Перерыв (мин)", bg=COLOR_BG).grid(row=1, column=0)
entry_break = tk.Entry(frame_settings, width=5)
entry_break.insert(0, settings["break"])
entry_break.grid(row=1, column=1)

label_timer = tk.Label(root, text="00:00", font=("Arial", 24, "bold"), bg=COLOR_BG)
label_timer.pack(pady=5)

frame_buttons = tk.Frame(root, bg=COLOR_BG)
frame_buttons.pack()

btn_work = tk.Button(frame_buttons, text="Работа", width=8, command=start_work)
btn_work.grid(row=0, column=0, padx=3)

btn_break = tk.Button(frame_buttons, text="Перерыв", width=8, command=start_break)
btn_break.grid(row=0, column=1, padx=3)

btn_stop = tk.Button(frame_buttons, text="Останов", bg=COLOR_STOP, width=8, command=pause_timer)
btn_stop.grid(row=1, column=0, pady=3)

btn_exit = tk.Button(frame_buttons, text="Выход", bg=COLOR_EXIT, width=8, command=exit_app)
btn_exit.grid(row=1, column=1, pady=3)

current_mode = "work"
reset_to_default("work")
update_mode_buttons()

root.mainloop()
