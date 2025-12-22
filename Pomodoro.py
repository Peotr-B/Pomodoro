# -*- coding: utf-8 -*-
"""
Created on Mon Dec 22 11:38:43 2025
С использованием ChatGPT
D:\ИИ\Нейросети\Программирование с нейросетью\Помодоро с нейросетью
Scriptor
@author: рс
"""

import tkinter as tk
import winsound
import threading
from pystray import Icon, Menu, MenuItem
from PIL import Image, ImageDraw

# ---------- Цвета ----------
BG_COLOR = "#d6e86c"
WORK_BG = "#f4a742"
BREAK_BG = "#6ec6ff"

WORK_BTN_IDLE = "#f7c58a"
WORK_BTN_ACTIVE = "#ff8c00"

BREAK_BTN_IDLE = "#b3e5fc"
BREAK_BTN_ACTIVE = "#00a2ff"

TEXT_COLOR = "black"

# ---------- Состояния ----------
mode = None
running = False
timer_id = None
time_left = 0
tray_icon = None

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
    mins = time_left // 60
    secs = time_left % 60
    timer_label.config(text=f"{mins:02}:{secs:02}")

def reset_buttons():
    work_btn.config(bg=WORK_BTN_IDLE)
    break_btn.config(bg=BREAK_BTN_IDLE)

def stop_timer():
    global running, timer_id
    running = False
    if timer_id:
        root.after_cancel(timer_id)

def set_default_time():
    global time_left
    if mode == "work":
        time_left = minutes_to_seconds(work_entry)
    elif mode == "break":
        time_left = minutes_to_seconds(break_entry)
    update_display()

def tick():
    global time_left, timer_id
    if running and time_left > 0:
        time_left -= 1
        update_display()
        timer_id = root.after(1000, tick)
    elif time_left == 0:
        stop_timer()
        reset_buttons()
        play_sound()
        set_default_time()

def toggle_work():
    global mode, running, time_left
    if mode == "work" and running:
        stop_timer()
        work_btn.config(bg=WORK_BTN_IDLE)
        return

    stop_timer()
    mode = "work"
    reset_buttons()
    work_btn.config(bg=WORK_BTN_ACTIVE)

    if time_left == 0:
        time_left = minutes_to_seconds(work_entry)

    running = True
    update_display()
    tick()

def toggle_break():
    global mode, running, time_left
    if mode == "break" and running:
        stop_timer()
        break_btn.config(bg=BREAK_BTN_IDLE)
        return

    stop_timer()
    mode = "break"
    reset_buttons()
    break_btn.config(bg=BREAK_BTN_ACTIVE)

    if time_left == 0:
        time_left = minutes_to_seconds(break_entry)

    running = True
    update_display()
    tick()

# ---------- Трей ----------
def create_image():
    img = Image.new("RGB", (64, 64), "green")
    d = ImageDraw.Draw(img)
    d.rectangle((16, 16, 48, 48), fill="yellow")
    return img

def show_window(icon, item):
    icon.stop()
    root.after(0, root.deiconify)

def exit_app(icon, item):
    icon.stop()
    root.after(0, root.destroy)

def hide_window():
    root.withdraw()
    threading.Thread(target=run_tray, daemon=True).start()

def run_tray():
    global tray_icon
    tray_icon = Icon(
        "Pomodoro",
        create_image(),
        "Таймер помодоро",
        menu=Menu(
            MenuItem("Открыть", show_window),
            MenuItem("Выход", exit_app)
        )
    )
    tray_icon.run()

# ---------- UI ----------
root = tk.Tk()
root.title("Таймер помодоро – эффективность в работе")
root.geometry("400x320")
root.configure(bg=BG_COLOR)
root.resizable(False, False)

root.protocol("WM_DELETE_WINDOW", hide_window)

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
    text="25:00",
    font=("Arial", 36, "bold"),
    bg=BG_COLOR,
    fg=TEXT_COLOR
)
timer_label.pack(pady=10)

frame = tk.Frame(root, bg=BG_COLOR)
frame.pack()

tk.Label(frame, text="Работа (мин)", bg=WORK_BG).grid(row=0, column=0, padx=5, pady=5)
work_entry = tk.Entry(frame, width=5, fg=TEXT_COLOR, justify="center")
work_entry.insert(0, "25")
work_entry.grid(row=1, column=0)

tk.Label(frame, text="Перерыв (мин)", bg=BREAK_BG).grid(row=0, column=1, padx=5, pady=5)
break_entry = tk.Entry(frame, width=5, fg=TEXT_COLOR, justify="center")
break_entry.insert(0, "5")
break_entry.grid(row=1, column=1)

btn_frame = tk.Frame(root, bg=BG_COLOR)
btn_frame.pack(pady=20)

work_btn = tk.Button(btn_frame, text="Работа", bg=WORK_BTN_IDLE, width=12, command=toggle_work)
work_btn.grid(row=0, column=0, padx=10)

break_btn = tk.Button(btn_frame, text="Перерыв", bg=BREAK_BTN_IDLE, width=12, command=toggle_break)
break_btn.grid(row=0, column=1, padx=10)

root.mainloop()
