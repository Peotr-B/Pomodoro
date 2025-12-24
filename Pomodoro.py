# -*- coding: utf-8 -*-
"""
Created on Mon Dec 24 11:38:43 2025
Pomodoro.py
С использованием DeepSeek
D:\ИИ\Нейросети\Программирование с нейросетью\Помодоро с нейросетью
Scriptor
@author: рс
"""

import tkinter as tk
from tkinter import font
import time
import winsound

class PomodoroTimer:
    def __init__(self, root):
        self.root = root
        self.root.title("Таймер помодоро – эффективность в работе")
        self.root.geometry("450x450")
        self.root.configure(bg='#C8FF96')  # жёлто-зелёный цвет
        
        # Настройки по умолчанию
        self.work_time = 25 * 60  # 25 минут в секундах
        self.break_time = 5 * 60  # 5 минут в секундах
        self.current_time = self.work_time
        self.is_work_mode = True
        self.is_running = False
        self.timer_id = None
        
        # Цвета
        self.work_active_color = '#FFC864'      # ярко-оранжевый
        self.work_inactive_color = '#FFEBC8'    # бледный оранжевый
        self.break_active_color = '#64C8FF'     # ярко-голубой
        self.break_inactive_color = '#C8EBFF'   # бледный голубой
        self.work_bg_color = '#FFC896'          # оранжевый фон
        self.break_bg_color = '#96C8FF'         # голубой фон
        self.form_color = '#C8FF96'             # жёлто-зелёный
        self.reset_button_color = '#E0E0E0'     # цвет кнопки сброса
        
        self.setup_ui()
        self.update_display()
    
    def setup_ui(self):
        # Заголовок
        title_font = font.Font(family='Arial', size=16, weight='bold')
        title_label = tk.Label(
            self.root, 
            text="ТАЙМЕР ПОМОДОРО",
            font=title_font,
            bg=self.form_color,
            fg='black'
        )
        title_label.pack(pady=20)
        
        # Фрейм для настроек времени
        settings_frame = tk.Frame(self.root, bg=self.form_color)
        settings_frame.pack(pady=10)
        
        # Поле для времени работы
        work_label = tk.Label(
            settings_frame,
            text="Работа (минуты):",
            font=('Arial', 10),
            bg=self.form_color,
            fg='black'
        )
        work_label.grid(row=0, column=0, padx=10, pady=5)
        
        self.work_entry = tk.Entry(
            settings_frame,
            width=10,
            font=('Arial', 12),
            bg=self.work_bg_color,
            fg='black',
            justify='center'
        )
        self.work_entry.insert(0, "25")
        self.work_entry.grid(row=0, column=1, padx=10, pady=5)
        
        # Поле для времени перерыва
        break_label = tk.Label(
            settings_frame,
            text="Перерыв (минуты):",
            font=('Arial', 10),
            bg=self.form_color,
            fg='black'
        )
        break_label.grid(row=1, column=0, padx=10, pady=5)
        
        self.break_entry = tk.Entry(
            settings_frame,
            width=10,
            font=('Arial', 12),
            bg=self.break_bg_color,
            fg='black',
            justify='center'
        )
        self.break_entry.insert(0, "5")
        self.break_entry.grid(row=1, column=1, padx=10, pady=5)
        
        # Отображение таймера
        self.timer_font = font.Font(family='Arial', size=48, weight='bold')
        self.timer_label = tk.Label(
            self.root,
            text="25:00",
            font=self.timer_font,
            bg=self.form_color,
            fg='black'
        )
        self.timer_label.pack(pady=30)
        
        # Фрейм для кнопок управления
        control_frame = tk.Frame(self.root, bg=self.form_color)
        control_frame.pack(pady=10)
        
        # Кнопка "Работа"
        self.work_button = tk.Button(
            control_frame,
            text="РАБОТА",
            font=('Arial', 12, 'bold'),
            width=12,
            height=2,
            bg=self.work_inactive_color,
            fg='black',
            command=self.work_button_click
        )
        self.work_button.grid(row=0, column=0, padx=5)
        
        # Кнопка "Перерыв"
        self.break_button = tk.Button(
            control_frame,
            text="ПЕРЕРЫВ",
            font=('Arial', 12, 'bold'),
            width=12,
            height=2,
            bg=self.break_inactive_color,
            fg='black',
            command=self.break_button_click
        )
        self.break_button.grid(row=0, column=1, padx=5)
        
        # Фрейм для кнопки сброса
        reset_frame = tk.Frame(self.root, bg=self.form_color)
        reset_frame.pack(pady=10)
        
        # Кнопка "Сброс"
        self.reset_button = tk.Button(
            reset_frame,
            text="СБРОС",
            font=('Arial', 10, 'bold'),
            width=10,
            height=1,
            bg=self.reset_button_color,
            fg='black',
            command=self.reset_timer
        )
        self.reset_button.pack()
        
        # Индикатор текущего режима
        self.mode_label = tk.Label(
            self.root,
            text="Режим: РАБОТА",
            font=('Arial', 10),
            bg=self.form_color,
            fg='black'
        )
        self.mode_label.pack(pady=5)
    
    def work_button_click(self):
        """Обработчик клика по кнопке РАБОТА"""
        if self.is_running:
            # Если таймер запущен
            if self.is_work_mode:
                # Если уже в режиме работы - останавливаем
                self.stop_timer()
                self.work_button.config(bg=self.work_inactive_color)
            else:
                # Если в режиме перерыва - переключаемся на работу
                self.switch_to_work()
        else:
            # Если таймер остановлен
            if self.is_work_mode:
                # Если уже в режиме работы - запускаем
                self.start_work_mode()
            else:
                # Если в режиме перерыва - переключаемся на работу и запускаем
                self.switch_to_work()
    
    def break_button_click(self):
        """Обработчик клика по кнопке ПЕРЕРЫВ"""
        if self.is_running:
            # Если таймер запущен
            if not self.is_work_mode:
                # Если уже в режиме перерыва - останавливаем
                self.stop_timer()
                self.break_button.config(bg=self.break_inactive_color)
            else:
                # Если в режиме работы - переключаемся на перерыв
                self.switch_to_break()
        else:
            # Если таймер остановлен
            if not self.is_work_mode:
                # Если уже в режиме перерыва - запускаем
                self.start_break_mode()
            else:
                # Если в режиме работы - переключаемся на перерыв и запускаем
                self.switch_to_break()
    
    def switch_to_work(self):
        """Переключение в режим работы"""
        # Останавливаем текущий таймер
        self.stop_timer()
        
        # Устанавливаем время работы
        try:
            minutes = int(self.work_entry.get())
            if minutes < 1:
                minutes = 1
            self.work_time = minutes * 60
            self.current_time = self.work_time
        except ValueError:
            self.work_time = 25 * 60
            self.current_time = self.work_time
            self.work_entry.delete(0, tk.END)
            self.work_entry.insert(0, "25")
        
        # Устанавливаем режим и запускаем
        self.is_work_mode = True
        self.start_timer()
        
        # Обновляем кнопки
        self.work_button.config(bg=self.work_active_color)
        self.break_button.config(bg=self.break_inactive_color)
        self.mode_label.config(text="Режим: РАБОТА")
    
    def switch_to_break(self):
        """Переключение в режим перерыва"""
        # Останавливаем текущий таймер
        self.stop_timer()
        
        # Устанавливаем время перерыва
        try:
            minutes = int(self.break_entry.get())
            if minutes < 1:
                minutes = 1
            self.break_time = minutes * 60
            self.current_time = self.break_time
        except ValueError:
            self.break_time = 5 * 60
            self.current_time = self.break_time
            self.break_entry.delete(0, tk.END)
            self.break_entry.insert(0, "5")
        
        # Устанавливаем режим и запускаем
        self.is_work_mode = False
        self.start_timer()
        
        # Обновляем кнопки
        self.break_button.config(bg=self.break_active_color)
        self.work_button.config(bg=self.work_inactive_color)
        self.mode_label.config(text="Режим: ПЕРЕРЫВ")
    
    def start_work_mode(self):
        """Запуск режима работы (если уже в этом режиме)"""
        # Обновляем время работы
        try:
            minutes = int(self.work_entry.get())
            if minutes < 1:
                minutes = 1
            self.work_time = minutes * 60
            self.current_time = self.work_time
        except ValueError:
            self.work_time = 25 * 60
            self.current_time = self.work_time
            self.work_entry.delete(0, tk.END)
            self.work_entry.insert(0, "25")
        
        # Устанавливаем режим
        self.is_work_mode = True
        self.start_timer()
        
        # Обновляем кнопки
        self.work_button.config(bg=self.work_active_color)
        self.break_button.config(bg=self.break_inactive_color)
        self.mode_label.config(text="Режим: РАБОТА")
    
    def start_break_mode(self):
        """Запуск режима перерыва (если уже в этом режиме)"""
        # Обновляем время перерыва
        try:
            minutes = int(self.break_entry.get())
            if minutes < 1:
                minutes = 1
            self.break_time = minutes * 60
            self.current_time = self.break_time
        except ValueError:
            self.break_time = 5 * 60
            self.current_time = self.break_time
            self.break_entry.delete(0, tk.END)
            self.break_entry.insert(0, "5")
        
        # Устанавливаем режим
        self.is_work_mode = False
        self.start_timer()
        
        # Обновляем кнопки
        self.break_button.config(bg=self.break_active_color)
        self.work_button.config(bg=self.work_inactive_color)
        self.mode_label.config(text="Режим: ПЕРЕРЫВ")
    
    def start_timer(self):
        """Запуск таймера"""
        if not self.is_running:
            self.is_running = True
            self.update_timer()
    
    def stop_timer(self):
        """Остановка таймера"""
        self.is_running = False
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None
    
    def update_timer(self):
        """Обновление таймера"""
        if not self.is_running:
            return
        
        self.current_time -= 1
        
        if self.current_time <= 0:
            self.stop_timer()
            # Воспроизводим звуковой сигнал
            winsound.Beep(1000, 1000)
            
            # Сбрасываем цвета кнопок
            self.work_button.config(bg=self.work_inactive_color)
            self.break_button.config(bg=self.break_inactive_color)
            
            # Обновляем индикатор режима
            if self.is_work_mode:
                self.mode_label.config(text="Работа завершена!")
            else:
                self.mode_label.config(text="Перерыв завершён!")
            
            # Возвращаем значения по умолчанию
            if self.is_work_mode:
                self.current_time = self.work_time
            else:
                self.current_time = self.break_time
        
        self.update_display()
        
        if self.is_running:
            # Запланировать следующее обновление через 1 секунду
            self.timer_id = self.root.after(1000, self.update_timer)
    
    def update_display(self):
        """Обновление отображения таймера"""
        minutes = self.current_time // 60
        seconds = self.current_time % 60
        self.timer_label.config(text=f"{minutes:02d}:{seconds:02d}")
    
    def reset_timer(self):
        """Сброс таймера"""
        self.stop_timer()
        
        # Восстанавливаем значения по умолчанию из полей ввода
        try:
            work_minutes = int(self.work_entry.get())
            if work_minutes < 1:
                work_minutes = 1
            self.work_time = work_minutes * 60
        except ValueError:
            self.work_time = 25 * 60
            self.work_entry.delete(0, tk.END)
            self.work_entry.insert(0, "25")
        
        try:
            break_minutes = int(self.break_entry.get())
            if break_minutes < 1:
                break_minutes = 1
            self.break_time = break_minutes * 60
        except ValueError:
            self.break_time = 5 * 60
            self.break_entry.delete(0, tk.END)
            self.break_entry.insert(0, "5")
        
        # Устанавливаем режим работы
        self.is_work_mode = True
        self.current_time = self.work_time
        
        # Сбрасываем кнопки
        self.work_button.config(bg=self.work_inactive_color)
        self.break_button.config(bg=self.break_inactive_color)
        self.mode_label.config(text="Режим: РАБОТА")
        
        # Обновляем отображение
        self.update_display()

def main():
    root = tk.Tk()
    app = PomodoroTimer(root)
    root.mainloop()

if __name__ == "__main__":
    main()
