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
import winsound
import json
import os
import threading

from pystray import Icon, Menu, MenuItem
from PIL import Image, ImageDraw

# ---------- Файл настроек ----------
SETTINGS_FILE = "settings.json"

# ---------- Цвета ----------
BG_COLOR = "#d6e86c"
WORK_BG = "#f4a742"
BREAK_BG = "#6ec6ff"

WORK_BTN = "#ff8c00"
BREAK_BTN = "#00a2ff"
STOP_BTN = "#8b5a2b"
EXIT_BTN = "#cc0000"

TEXT_COLOR = "black"

# ---------- Состояние ----------
mode = None
paused_mode = None
running = False
timer_id = None
time_left = 0
tray_icon = None

# ---------- Настройки ----------
def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("work", 25), data.get("break", 5)
        except:
            pass
    return 25, 5

def save_settings():
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump({
            "work": int(work_entry.get()),
            "break": int(break_entry.get())
        }, f)

# ---------- Звук ----------
def play_sound():
    winsound.PlaySound("SystemExclamation", winsound.SND_ALIAS)

# ---------- Таймер ----------
def minutes_to_seconds(entry):
    try:
        return int(entry.get()) * 60
    except:
        return 0

def update_display():
    m = time_left // 60
    s = time_left % 60
    timer_label.config(text=f"{m:02}:{s:02}")

def stop_timer():
    global running, timer_id, paused_mode
    running = False
    paused_mode = mode
    if timer_id:
        root.after_cancel(timer_id)

def tick():
    global time_left, timer_id
    if running and time_left > 0:
        time_left -= 1
        update_display()
        timer_id = root.after(1000, tick)
    elif time_left == 0:
        stop_timer()
        play_sound()

# ---------- Управление ----------
def start_work():
    global mode, running, time_left
    save_settings()
    stop_timer()

    if paused_mode == "work" and time_left > 0:
        pass  # продолжаем
    else:
        time_left = minutes_to_seconds(work_entry)

    mode = "work"
    running = True
    update_display()
    tick()

def start_break():
    global mode, running, time_left
    save_settings()
    stop_timer()

    if paused_mode == "break" and time_left > 0:
        pass
    else:
        time_left = minutes_to_seconds(break_entry)

    mode = "break"
    running = True
    update_display()
    tick()

def stop_only():
    stop_timer()

def exit_app(icon=None, item=None):
    save_settings()
    stop_timer()
    if tray_icon:
        tray_icon.stop()
    root.after(0, root.destroy)

# ---------- Трей ----------
def create_tray_image():
    img = Image.new("RGB", (64, 64), BG_COLOR)
    d = ImageDraw.Draw(img)
    d.rectangle((18, 18, 46, 46), fill=WORK_BTN)
    return img

def show_window(icon=None, item=None):
    root.after(0, root.deiconify)

def hide_window():
    root.withdraw()
    threading.Thread(target=run_tray, daemon=True).start()

def on_tray_double_click(icon, button, time):
    show_window()

def run_tray():
    global tray_icon
    if tray_icon:
        return

    tray_icon = Icon(
        "Pomodoro",
        create_tray_image(),
        "Таймер помодоро",
        menu=Menu(
            MenuItem("Открыть", show_window),
            MenuItem("Выход", exit_app)
        )
    )
    tray_icon.on_double_click = on_tray_double_click
    tray_icon.run()

# ---------- UI ----------
root = tk.Tk()
root.title("Таймер помодоро – эффективность в работе")
root.geometry("420x380")
root.configure(bg=BG_COLOR)
root.resizable(False, False)

root.protocol("WM_DELETE_WINDOW", hide_window)

work_default, break_default = load_settings()

title = tk.Label(
    root,
    text="Таймер помодоро – эффективность в работе",
    bg=BG_COLOR,
    fg=TEXT_COLOR,
    font=("Arial", 12, "bold")
)
title.pack(pady=10)

timer_label = tk.Label(
    root,
    text=f"{work_default:02}:00",
    font=("Arial", 40, "bold"),
    bg=BG_COLOR,
    fg=TEXT_COLOR
)
timer_label.pack(pady=10)

frame = tk.Frame(root, bg=BG_COLOR)
frame.pack()

tk.Label(frame, text="Работа (мин)", bg=WORK_BG).grid(row=0, column=0, padx=10)
work_entry = tk.Entry(frame, width=5, justify="center", fg=TEXT_COLOR)
work_entry.insert(0, str(work_default))
work_entry.grid(row=1, column=0)

tk.Label(frame, text="Отдых (мин)", bg=BREAK_BG).grid(row=0, column=1, padx=10)
break_entry = tk.Entry(frame, width=5, justify="center", fg=TEXT_COLOR)
break_entry.insert(0, str(break_default))
break_entry.grid(row=1, column=1)

btn_frame = tk.Frame(root, bg=BG_COLOR)
btn_frame.pack(pady=25)

tk.Button(btn_frame, text="Работа", width=12, bg=WORK_BTN, command=start_work)\
    .grid(row=0, column=0, padx=5)

tk.Button(btn_frame, text="Перерыв", width=12, bg=BREAK_BTN, command=start_break)\
    .grid(row=0, column=1, padx=5)

tk.Button(btn_frame, text="Останов", width=12, bg=STOP_BTN, fg="white", command=stop_only)\
    .grid(row=1, column=0, padx=5, pady=10)

tk.Button(btn_frame, text="Выход", width=12, bg=EXIT_BTN, fg="white", command=exit_app)\
    .grid(row=1, column=1, padx=5, pady=10)

root.mainloop()
