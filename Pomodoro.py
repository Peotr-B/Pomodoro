# -*- coding: utf-8 -*-
"""
Created on Mon Dec 22 11:38:43 2025
Pomodoro.py
С использованием ChatGPT
D:\ИИ\Нейросети\Программирование с нейросетью\Помодоро с нейросетью
Scriptor
@author: рс

Created on Mon Dec 24 11:38:43 2025
Создание второго варианта, экзешник под именем:
pomodoro_circle.py


"""

import tkinter as tk
import json
import os
import math
import time
from PIL import Image, ImageDraw, ImageFont
import pystray

# ================== НАСТРОЙКИ ==================

SIZE = 520
CENTER = SIZE // 2
RADIUS = 200

SETTINGS_FILE = "settings.json"

COLOR_IDLE = "#dddddd"
COLOR_WORK = "#ffd7b0"      # светло-оранжевый
COLOR_BREAK = "#cfefff"     # светло-голубой

BTN_WORK_ACTIVE = "#ff9800"
BTN_WORK_IDLE = "#ffd7b0"
BTN_BREAK_ACTIVE = "#4fc3f7"
BTN_BREAK_IDLE = "#cfefff"
BTN_STOP = "#8b5a2b"
BTN_EXIT = "#c62828"

TEXT_COLOR = "black"

# ================== ЗАГРУЗКА НАСТРОЕК ==================

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"work": 25, "break": 5}

def save_settings():
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f)

settings = load_settings()

# ================== СОСТОЯНИЕ ==================

mode = None
running = False
remaining_seconds = 0
timer_id = None
tray_icon = None

# ================== ОСНОВНОЕ ОКНО ==================

root = tk.Tk()
root.overrideredirect(True)
root.geometry(f"{SIZE}x{SIZE}+300+150")
root.configure(bg=COLOR_IDLE)

canvas = tk.Canvas(root, width=SIZE, height=SIZE, bg=COLOR_IDLE, highlightthickness=0)
canvas.pack()

# ================== ПЕРЕТАСКИВАНИЕ ==================

def start_move(e):
    root.x = e.x
    root.y = e.y

def do_move(e):
    x = root.winfo_x() + e.x - root.x
    y = root.winfo_y() + e.y - root.y
    root.geometry(f"+{x}+{y}")

canvas.bind("<ButtonPress-1>", start_move)
canvas.bind("<B1-Motion>", do_move)

# ================== ИНФОРМАЦИОННОЕ КОЛЬЦО ==================

def draw_time_ring():
    canvas.delete("ring")

    canvas.create_oval(
        CENTER - RADIUS, CENTER - RADIUS,
        CENTER + RADIUS, CENTER + RADIUS,
        outline="white", width=18, tags="ring"
    )

    start_angle = -90
    for hour in range(8, 20):
        angle = math.radians(start_angle + (hour - 8) * 30)
        x = CENTER + math.cos(angle) * (RADIUS + 22)
        y = CENTER + math.sin(angle) * (RADIUS + 22)
        canvas.create_text(x, y, text=str(hour), fill="white", font=("Arial", 12), tags="ring")

draw_time_ring()

# ================== ТАЙМЕР ==================

timer_text = canvas.create_text(
    CENTER, CENTER,
    text="00:00",
    fill=TEXT_COLOR,
    font=("Arial", 42, "bold")
)

def update_timer_label():
    m = remaining_seconds // 60
    s = remaining_seconds % 60
    canvas.itemconfig(timer_text, text=f"{m:02}:{s:02}")

def tick():
    global remaining_seconds, timer_id
    if running and remaining_seconds > 0:
        remaining_seconds -= 1
        update_timer_label()
        update_tray_icon()
        timer_id = root.after(1000, tick)
    else:
        stop_timer()

# ================== УПРАВЛЕНИЕ РЕЖИМАМИ ==================

def start_mode(new_mode):
    global mode, running, remaining_seconds

    stop_timer(cancel_only=True)

    if mode != new_mode:
        if new_mode == "work":
            remaining_seconds = settings["work"] * 60
        else:
            remaining_seconds = settings["break"] * 60

    mode = new_mode
    running = True
    update_ui()
    tick()

def stop_timer(cancel_only=False):
    global running, timer_id
    running = False
    if timer_id:
        root.after_cancel(timer_id)
        timer_id = None
    if not cancel_only:
        update_ui()

# ================== UI ==================

def update_ui():
    if mode == "work" and running:
        root.configure(bg=COLOR_WORK)
        canvas.configure(bg=COLOR_WORK)
        btn_work.config(bg=BTN_WORK_ACTIVE)
        btn_break.config(bg=BTN_BREAK_IDLE)
    elif mode == "break" and running:
        root.configure(bg=COLOR_BREAK)
        canvas.configure(bg=COLOR_BREAK)
        btn_work.config(bg=BTN_WORK_IDLE)
        btn_break.config(bg=BTN_BREAK_ACTIVE)
    else:
        root.configure(bg=COLOR_IDLE)
        canvas.configure(bg=COLOR_IDLE)
        btn_work.config(bg=BTN_WORK_IDLE)
        btn_break.config(bg=BTN_BREAK_IDLE)

# ================== КНОПКИ ==================

btn_work = tk.Button(root, text="Работа", command=lambda: start_mode("work"), bg=BTN_WORK_IDLE)
btn_break = tk.Button(root, text="Перерыв", command=lambda: start_mode("break"), bg=BTN_BREAK_IDLE)
btn_stop = tk.Button(root, text="Останов", command=stop_timer, bg=BTN_STOP, fg="white")
btn_exit = tk.Button(root, text="Выход", command=lambda: exit_app(), bg=BTN_EXIT, fg="white")

canvas.create_window(CENTER - 110, SIZE - 45, window=btn_work)
canvas.create_window(CENTER, SIZE - 45, window=btn_break)
canvas.create_window(CENTER + 110, SIZE - 45, window=btn_stop)
canvas.create_window(CENTER, SIZE - 15, window=btn_exit)

# ================== НАСТРОЙКИ МИНУТ ==================

def open_settings(kind):
    win = tk.Toplevel(root)
    win.title("Настройка")
    win.geometry("200x120")
    tk.Label(win, text=f"{kind.capitalize()} (мин):").pack(pady=10)
    entry = tk.Entry(win)
    entry.insert(0, settings[kind])
    entry.pack()

    def save():
        settings[kind] = int(entry.get())
        save_settings()
        win.destroy()

    tk.Button(win, text="OK", command=save).pack(pady=10)

btn_set_work = tk.Button(root, text="⚙", command=lambda: open_settings("work"))
btn_set_break = tk.Button(root, text="⚙", command=lambda: open_settings("break"))

canvas.create_window(CENTER - 180, CENTER + 80, window=btn_set_work)
canvas.create_window(CENTER + 180, CENTER + 80, window=btn_set_break)

# ================== TRAY ==================

def create_tray_image():
    img = Image.new("RGB", (64, 64), COLOR_IDLE)
    draw = ImageDraw.Draw(img)

    if mode == "work":
        img.paste(Image.new("RGB", (64, 64), BTN_WORK_ACTIVE))
    elif mode == "break":
        img.paste(Image.new("RGB", (64, 64), BTN_BREAK_ACTIVE))

    minutes = remaining_seconds // 60

    try:
        font = ImageFont.truetype("arialbd.ttf", 28)
    except:
        font = ImageFont.load_default()

    text = str(minutes)
    w, h = draw.textsize(text, font=font)
    draw.text(
        ((64 - w) / 2, (64 - h) / 2),
        text,
        fill="black",
        font=font
    )
    return img

def update_tray_icon():
    if tray_icon:
        tray_icon.icon = create_tray_image()

def show_window(icon=None, item=None):
    root.after(0, root.deiconify)

def hide_window():
    root.withdraw()

def exit_app(icon=None, item=None):
    if tray_icon:
        tray_icon.stop()
    root.destroy()

menu = pystray.Menu(
    pystray.MenuItem("Открыть", show_window),
    pystray.MenuItem("Выход", exit_app)
)

def setup_tray():
    global tray_icon
    tray_icon = pystray.Icon("Pomodoro", create_tray_image(), "Pomodoro", menu)
    tray_icon.run_detached()

setup_tray()

# ================== КРЕСТИК ==================

close_btn = tk.Button(root, text="✕", command=hide_window, bg="#bbbbbb")
canvas.create_window(SIZE - 15, 15, window=close_btn)

update_timer_label()
root.mainloop()
