# -*- coding: utf-8 -*-
"""
Created on Mon Dec 22 11:38:43 2025
pomodoro_circle.py
С использованием ChatGPT
D:\ИИ\Нейросети\Программирование с нейросетью\Помодоро с нейросетью
Scriptor
@author: рс
"""

import tkinter as tk
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

paused = False

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
    global mode, running, time_left, paused

    stop_timer()

    if mode != "work":
        time_left = work_minutes * 60

    mode = "work"
    running = True
    paused = False

    update_ui()
    tick()

def start_break():
    global mode, running, time_left, paused

    stop_timer()

    if mode != "break":
        time_left = break_minutes * 60

    mode = "break"
    running = True
    paused = False

    update_ui()
    tick()

def stop_mode():
    global mode, paused
    stop_timer()
    paused = True
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
#root.overrideredirect(True)  #Для скрытия окна
root.title("Помодоро")
#root.geometry("260x340")
#root.geometry("300x300")
#root.geometry("280x280")
root.geometry("240x210")
root.resizable(False, False)

"""root = tk.Tk()
root.title("Помодоро")
root.geometry("280x280")
root.resizable(False, False)
root.overrideredirect(True)
"""

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
""" 
def minimize_to_tray():
    root.withdraw()   # скрываем окно
"""
 
def on_close():
    root.iconify()   # сворачивает в панель задач

# -------------------- layout --------------------

#tk.Label(root, text="Помодоро", font=("Arial", 14, "bold")).pack(pady=5)

timer_label = tk.Label(root, text="00:00", font=("Arial", 32))
#timer_label.pack(pady=10)
timer_label.pack(pady=5)

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
#frame_buttons.pack(pady=15)
frame_buttons.pack(pady=8)

work_btn = tk.Button(frame_buttons, text="Работа", width=10, command=wrapped_start_work)
work_btn.grid(row=0, column=0, padx=5)

stop_btn = tk.Button(frame_buttons, text="Останов", width=10, bg=COLOR_STOP, command=stop_mode)
stop_btn.grid(row=0, column=1, padx=5)

break_btn = tk.Button(frame_buttons, text="Перерыв", width=10, command=wrapped_start_break)
break_btn.grid(row=1, column=0, padx=5, pady=5)

exit_btn = tk.Button(
    frame_buttons,
    text="Выход",
    command=quit_app
)
exit_btn.grid(row=1, column=1, padx=5, pady=5)

update_ui()
update_timer_label()

root.protocol("WM_DELETE_WINDOW", on_close)
root.mainloop()
