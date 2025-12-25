# -*- coding: utf-8 -*-
"""
Created on Mon Dec 22 11:38:43 2025
<<<<<<< Updated upstream
<<<<<<< Updated upstream
<<<<<<< Updated upstream
<<<<<<< Updated upstream
<<<<<<< Updated upstream
Pomodoro.py
=======
pomodoro_circle.py
>>>>>>> Stashed changes
=======
pomodoro_circle.py
>>>>>>> Stashed changes
=======
pomodoro_circle.py
>>>>>>> Stashed changes
=======
pomodoro_circle.py
>>>>>>> Stashed changes
=======
pomodoro_circle.py
>>>>>>> Stashed changes
С использованием ChatGPT
D:\ИИ\Нейросети\Программирование с нейросетью\Помодоро с нейросетью
Scriptor
@author: рс

Created on Mon Dec 24 11:38:43 2025
Создание второго варианта, экзешник под именем:
pomodoro_circle.py


"""

import tkinter as tk
<<<<<<< Updated upstream
<<<<<<< Updated upstream
<<<<<<< Updated upstream
<<<<<<< Updated upstream
<<<<<<< Updated upstream
from tkinter import ttk
import math, time, json, os, threading
from PIL import Image, ImageDraw, ImageFont
import pystray

# ================== КОНСТАНТЫ ==================
APP_SIZE = 480
RING_WIDTH = 24
CONFIG_FILE = "pomodoro_config.json"

COLOR_IDLE = "#e6e6e6"
COLOR_WORK = "#ffd9b3"
COLOR_BREAK = "#d6ecff"

RING_IDLE = "#b0b0b0"
RING_WORK = "#ff9900"
RING_BREAK = "#66b3ff"

START_HOUR = 8
END_HOUR = 20

# ================== СОСТОЯНИЕ ==================
mode = "idle"
remaining = 0
timer_after = None
tray_icon = None
segments = []
current_segment_start = None

work_minutes = 30
break_minutes = 10

# ================== ЗАГРУЗКА ==================
if os.path.exists(CONFIG_FILE):
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            d = json.load(f)
            work_minutes = int(d.get("work", work_minutes))
            break_minutes = int(d.get("break", break_minutes))
    except:
        pass

# ================== TK ==================
root = tk.Tk()
root.title("Помодоро")
root.geometry(f"{APP_SIZE}x{APP_SIZE}")
root.configure(bg=COLOR_IDLE)

canvas = tk.Canvas(root, bg=COLOR_IDLE, highlightthickness=0)
canvas.pack(fill="both", expand=True)

# ================== ПЕРЕТАСКИВАНИЕ (ТОЛЬКО ФОН) ==================
_drag = {"x": 0, "y": 0}

def start_move(e):
    _drag["x"] = e.x_root
    _drag["y"] = e.y_root

def do_move(e):
    dx = e.x_root - _drag["x"]
    dy = e.y_root - _drag["y"]
    x = root.winfo_x() + dx
    y = root.winfo_y() + dy
    root.geometry(f"+{x}+{y}")
    _drag["x"] = e.x_root
    _drag["y"] = e.y_root

canvas.bind("<Button-1>", start_move)
canvas.bind("<B1-Motion>", do_move)

# ================== ФОН ==================
def set_bg():
    bg = COLOR_IDLE if mode=="idle" else COLOR_WORK if mode=="work" else COLOR_BREAK
    root.configure(bg=bg)
    canvas.configure(bg=bg)

# ================== КОЛЬЦО ==================
def time_to_angle(ts):
    lt = time.localtime(ts)
    h = lt.tm_hour + lt.tm_min/60
    return 90 - ((h-START_HOUR)/(END_HOUR-START_HOUR))*360

def draw_ring():
    canvas.delete("ring")
    cx = cy = APP_SIZE//2
    r = APP_SIZE//2 - 40

    canvas.create_oval(cx-r, cy-r, cx+r, cy+r,
                       outline="white", width=RING_WIDTH, tags="ring")

    for s, e, m in segments:
        if e <= s:
            continue
        color = RING_WORK if m=="work" else RING_BREAK
        canvas.create_arc(cx-r, cy-r, cx+r, cy+r,
                          start=time_to_angle(s),
                          extent=time_to_angle(e)-time_to_angle(s),
                          style="arc", width=RING_WIDTH,
                          outline=color, tags="ring")

    for h in range(START_HOUR, END_HOUR):
        a = math.radians(90-(h-START_HOUR)*360/(END_HOUR-START_HOUR))
        tx = cx + (r+18)*math.cos(a)
        ty = cy - (r+18)*math.sin(a)
        canvas.create_text(tx, ty, text=str(h),
                           fill="black", font=("Arial", 10), tags="ring")

# ================== ТАЙМЕР ==================
timer_text = canvas.create_text(APP_SIZE//2, APP_SIZE//2,
                                text="00:00",
                                font=("Arial", 60, "bold"))

def format_time(s): return f"{s//60:02d}:{s%60:02d}"

def tick():
    global remaining, timer_after
    if remaining > 0:
        remaining -= 1
        canvas.itemconfig(timer_text, text=format_time(remaining))
        update_tray_icon()
        timer_after = root.after(1000, tick)
    else:
        stop_timer()

# ================== РЕЖИМЫ ==================
def start_mode(m, minutes):
    global mode, remaining, current_segment_start
    stop_timer()
    mode = m
    remaining = minutes*60
    current_segment_start = time.time()
    set_bg()
    draw_ring()
    canvas.itemconfig(timer_text, text=format_time(remaining))
    tick()

def stop_timer():
    global mode, current_segment_start
    if timer_after:
        root.after_cancel(timer_after)
    if current_segment_start:
        segments.append((current_segment_start, time.time(), mode))
        current_segment_start = None
    mode = "idle"
    set_bg()
    draw_ring()
    update_tray_icon()

# ================== TRAY ==================
def tray_image(text, bg):
    img = Image.new("RGBA", (64,64), bg)
    d = ImageDraw.Draw(img)
    size = 36
    font = ImageFont.truetype("arial.ttf", size) if os.path.exists("arial.ttf") else ImageFont.load_default()
    w, h = d.textsize(text, font)
    d.text(((64-w)//2,(64-h)//2), text, fill="black", font=font)
    return img

def update_tray_icon():
    if tray_icon:
        bg = COLOR_IDLE if mode=="idle" else COLOR_WORK if mode=="work" else COLOR_BREAK
        txt = str(remaining//60) if remaining else ""
        tray_icon.icon = tray_image(txt, bg)

def restore_window(icon=None, item=None):
    root.after(0, lambda: (root.deiconify(), root.lift(), root.focus_force()))

def quit_app(icon=None, item=None):
    save_config()
    if tray_icon:
        tray_icon.stop()
    root.after(0, root.destroy)

def setup_tray():
    global tray_icon
    tray_icon = pystray.Icon(
        "pomodoro",
        tray_image("", COLOR_IDLE),
        "Помодоро",
        pystray.Menu(
            pystray.MenuItem("Открыть", restore_window),
            pystray.MenuItem("Выход", quit_app)
        )
    )
    tray_icon.visible = True
    threading.Thread(target=tray_icon.run, daemon=True).start()

def minimize_to_tray():
    root.withdraw()

# ================== СОХРАНЕНИЕ ==================
def save_config():
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump({"work": work_entry.get(),
                   "break": break_entry.get()}, f)

# ================== UI ВНУТРИ КОЛЬЦА ==================
work_label = ttk.Label(root, text="Работа (мин)")
work_entry = ttk.Entry(root, width=5)
work_entry.insert(0, str(work_minutes))

break_label = ttk.Label(root, text="Перерыв (мин)")
break_entry = ttk.Entry(root, width=5)
break_entry.insert(0, str(break_minutes))

work_label.place(relx=0.4, rely=0.35, anchor="e")
work_entry.place(relx=0.42, rely=0.35, anchor="w")
break_label.place(relx=0.4, rely=0.42, anchor="e")
break_entry.place(relx=0.42, rely=0.42, anchor="w")

btn_work = ttk.Button(root, text="Работа", command=lambda: start_mode("work", int(work_entry.get())))
btn_break = ttk.Button(root, text="Перерыв", command=lambda: start_mode("break", int(break_entry.get())))
btn_stop = ttk.Button(root, text="Останов", command=stop_timer)
btn_exit = ttk.Button(root, text="Выход", command=quit_app)

btn_work.place(relx=0.3, rely=0.7, anchor="center")
btn_stop.place(relx=0.5, rely=0.7, anchor="center")
btn_break.place(relx=0.7, rely=0.7, anchor="center")
btn_exit.place(relx=0.5, rely=0.8, anchor="center")

root.protocol("WM_DELETE_WINDOW", minimize_to_tray)

# ================== СТАРТ ==================
set_bg()
root.after(100, draw_ring)
setup_tray()
=======
=======
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
import sys
import json
from pathlib import Path
import winsound


# -------------------- настройки --------------------

SETTINGS_FILE = Path("pomodoro_settings.json")

DEFAULT_WORK = 25
DEFAULT_BREAK = 5

COLOR_BG_STOP = "#eeeeee"
COLOR_WORK_ACTIVE = "#ff9800"
COLOR_WORK_IDLE = "#ffd6a0"
COLOR_BREAK_ACTIVE = "#4fc3f7"
COLOR_BREAK_IDLE = "#cfefff"
COLOR_STOP = "#8d6e63"
COLOR_EXIT = "#e53935"

# -------------------- состояние --------------------

mode = "stop"          # work / break / stop
running = False

work_minutes = DEFAULT_WORK
break_minutes = DEFAULT_BREAK

time_left = 0           # в секундах
timer_after_id = None   # ВАЖНО: id after()

# -------------------- загрузка / сохранение --------------------

def load_settings():
    global work_minutes, break_minutes
    if SETTINGS_FILE.exists():
        try:
            data = json.loads(SETTINGS_FILE.read_text())
            work_minutes = int(data.get("work", DEFAULT_WORK))
            break_minutes = int(data.get("break", DEFAULT_BREAK))
        except:
            pass

def save_settings():
    SETTINGS_FILE.write_text(json.dumps({
        "work": work_minutes,
        "break": break_minutes
    }))

# -------------------- after-ядро --------------------

def stop_timer():
    """Полная остановка таймера"""
    global running, timer_after_id
    running = False
    if timer_after_id is not None:
        root.after_cancel(timer_after_id)
        timer_after_id = None

def tick():
    """Единственный цикл таймера"""
    global time_left, timer_after_id

    if not running:
        return

    if time_left > 0:
        time_left -= 1
        update_timer_label()
        timer_after_id = root.after(1000, tick)
    else:
        play_end_sound()
        stop_timer()

# -------------------- логика режимов --------------------

def start_work():
    global mode, running, time_left, work_minutes

    stop_timer()
    mode = "work"
    running = True

    if time_left <= 0 or previous_mode != "work":
        time_left = work_minutes * 60

    update_ui()
    tick()

def start_break():
    global mode, running, time_left, break_minutes

    stop_timer()
    mode = "break"
    running = True

    if time_left <= 0 or previous_mode != "break":
        time_left = break_minutes * 60

    update_ui()
    tick()

def stop_mode():
    global mode
    stop_timer()
    mode = "stop"
    update_ui()

def quit_app():
    stop_timer()
    save_settings()
    root.destroy()
    sys.exit(0)

# -------------------- UI --------------------

def update_timer_label():
    m = time_left // 60
    s = time_left % 60
    timer_label.config(text=f"{m:02}:{s:02}")

def update_ui():
    root.config(bg=COLOR_BG_STOP)

    work_btn.config(bg=COLOR_WORK_IDLE)
    break_btn.config(bg=COLOR_BREAK_IDLE)

    if mode == "work":
        root.config(bg=COLOR_WORK_IDLE)
        work_btn.config(bg=COLOR_WORK_ACTIVE)
    elif mode == "break":
        root.config(bg=COLOR_BREAK_IDLE)
        break_btn.config(bg=COLOR_BREAK_ACTIVE)

# -------------------- callbacks значений --------------------

def set_work():
    global work_minutes
    try:
        work_minutes = int(work_entry.get())
        save_settings()
    except:
        pass

def set_break():
    global break_minutes
    try:
        break_minutes = int(break_entry.get())
        save_settings()
    except:
        pass

# -------------------- GUI --------------------

root = tk.Tk()
root.title("Помодоро")
root.geometry("260x340")
root.resizable(False, False)

load_settings()

previous_mode = "stop"

def remember_mode(new_mode):
    global previous_mode
    previous_mode = mode

# intercept
def wrapped_start_work():
    remember_mode("work")
    start_work()

def wrapped_start_break():
    remember_mode("break")
    start_break()

def play_end_sound():
    # "Биг-Бен" — низкий, затем высокий тон
    winsound.Beep(523, 400)   # До
    winsound.Beep(659, 400)   # Ми

# -------------------- layout --------------------

tk.Label(root, text="Помодоро", font=("Arial", 14, "bold")).pack(pady=5)

timer_label = tk.Label(root, text="00:00", font=("Arial", 32))
timer_label.pack(pady=10)

frame_settings = tk.Frame(root)
frame_settings.pack(pady=5)

tk.Label(frame_settings, text="Работа (мин)").grid(row=0, column=0)
work_entry = tk.Entry(frame_settings, width=5)
work_entry.insert(0, str(work_minutes))
work_entry.grid(row=0, column=1)
tk.Button(frame_settings, text="OK", command=set_work).grid(row=0, column=2)

tk.Label(frame_settings, text="Перерыв (мин)").grid(row=1, column=0)
break_entry = tk.Entry(frame_settings, width=5)
break_entry.insert(0, str(break_minutes))
break_entry.grid(row=1, column=1)
tk.Button(frame_settings, text="OK", command=set_break).grid(row=1, column=2)

frame_buttons = tk.Frame(root)
frame_buttons.pack(pady=15)

work_btn = tk.Button(frame_buttons, text="Работа", width=10, command=wrapped_start_work)
work_btn.grid(row=0, column=0, padx=5)

stop_btn = tk.Button(frame_buttons, text="Останов", width=10, bg=COLOR_STOP, command=stop_mode)
stop_btn.grid(row=0, column=1, padx=5)

break_btn = tk.Button(frame_buttons, text="Перерыв", width=10, command=wrapped_start_break)
break_btn.grid(row=1, column=0, padx=5, pady=5)

exit_btn = tk.Button(frame_buttons, text="Выход", width=10, bg=COLOR_EXIT, fg="white", command=quit_app)
exit_btn.grid(row=1, column=1, padx=5, pady=5)

update_ui()
update_timer_label()

root.protocol("WM_DELETE_WINDOW", quit_app)
<<<<<<< Updated upstream
<<<<<<< Updated upstream
<<<<<<< Updated upstream
<<<<<<< Updated upstream
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
root.mainloop()
