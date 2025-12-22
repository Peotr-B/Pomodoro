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

# ---------- Цвета ----------
BG_COLOR = "#d6e86c"

WORK_BG = "#f4a742"
BREAK_BG = "#6ec6ff"

WORK_BTN = "#ff8c00"
BREAK_BTN = "#00a2ff"

STOP_BTN = "#8b5a2b"    # коричневый
EXIT_BTN = "#cc0000"    # красный

TEXT_COLOR = "black"

# ---------- Состояние ----------
mode = None
running = False
timer_id = None
time_left = 0

# ---------- Звук ----------
def play_sound():
    winsound.PlaySound("SystemExclamation", winsound.SND_ALIAS)

# ---------- Логика ----------
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
    global running, timer_id
    running = False
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

def start_work():
    global mode, running, time_left
    stop_timer()
    mode = "work"
    time_left = minutes_to_seconds(work_entry)
    running = True
    update_display()
    tick()

def start_break():
    global mode, running, time_left
    stop_timer()
    mode = "break"
    time_left = minutes_to_seconds(break_entry)
    running = True
    update_display()
    tick()

def stop_only():
    stop_timer()

def exit_app():
    stop_timer()
    root.destroy()

# ---------- UI ----------
root = tk.Tk()
root.title("Таймер помодоро – эффективность в работе")
root.geometry("420x360")
root.configure(bg=BG_COLOR)
root.resizable(False, False)

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
    font=("Arial", 40, "bold"),
    bg=BG_COLOR,
    fg=TEXT_COLOR
)
timer_label.pack(pady=10)

frame = tk.Frame(root, bg=BG_COLOR)
frame.pack()

tk.Label(frame, text="Работа (мин)", bg=WORK_BG).grid(row=0, column=0, padx=10)
work_entry = tk.Entry(frame, width=5, justify="center", fg=TEXT_COLOR)
work_entry.insert(0, "25")
work_entry.grid(row=1, column=0)

tk.Label(frame, text="Перерыв (мин)", bg=BREAK_BG).grid(row=0, column=1, padx=10)
break_entry = tk.Entry(frame, width=5, justify="center", fg=TEXT_COLOR)
break_entry.insert(0, "5")
break_entry.grid(row=1, column=1)

btn_frame = tk.Frame(root, bg=BG_COLOR)
btn_frame.pack(pady=25)

tk.Button(
    btn_frame,
    text="Работа",
    width=12,
    bg=WORK_BTN,
    command=start_work
).grid(row=0, column=0, padx=5)

tk.Button(
    btn_frame,
    text="Перерыв",
    width=12,
    bg=BREAK_BTN,
    command=start_break
).grid(row=0, column=1, padx=5)

tk.Button(
    btn_frame,
    text="Останов",
    width=12,
    bg=STOP_BTN,
    fg="white",
    command=stop_only
).grid(row=1, column=0, padx=5, pady=10)

tk.Button(
    btn_frame,
    text="Выход",
    width=12,
    bg=EXIT_BTN,
    fg="white",
    command=exit_app
).grid(row=1, column=1, padx=5, pady=10)

root.mainloop()
