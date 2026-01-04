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
from tkinter import messagebox
import json
import os

class PomodoroTimer:
    def __init__(self, root):
        self.root = root
        self.root.title("Таймер помодоро – эффективность в работе")
        self.root.geometry("450x500")  # Вернули обычную высоту
        self.root.configure(bg='#C8FF96')
        
        # Обычное закрытие окна крестиком
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Файл для сохранения настроек
        self.settings_file = "pomodoro_settings.json"
        
        # Загружаем сохраненные настройки
        self.saved_settings = self.load_settings()
        
        # Настройки таймера
        self.work_time = self.saved_settings.get("work_time", 25) * 60
        self.break_time = self.saved_settings.get("break_time", 5) * 60
        self.original_work_minutes = self.saved_settings.get("work_time", 25)
        self.original_break_minutes = self.saved_settings.get("break_time", 5)
        
        # Текущее состояние
        self.current_time = self.work_time
        self.is_work_mode = True
        self.is_running = False
        self.timer_id = None
        self.paused_time = None
        
        # Цвета
        self.idle_color = '#C8FF96'  # жёлто-зелёный (бездействие)
        self.work_active_color = '#FFC864'      # ярко-оранжевый
        self.work_inactive_color = '#FFEBC8'    # светло-оранжевый (фон для работы)
        self.break_active_color = '#64C8FF'     # ярко-голубой
        self.break_inactive_color = '#C8EBFF'   # светло-голубой (фон для перерыва)
        self.work_bg_color = '#FFC896'          # оранжевый фон поля ввода
        self.break_bg_color = '#96C8FF'         # голубой фон поля ввода
        self.reset_button_color = '#E0E0E0'
        self.exit_button_color = '#FFAAAA'
        self.minimize_button_color = '#CCCCCC'
        self.save_button_color = '#90EE90'
        
        # Текущий цвет фона
        self.current_bg_color = self.idle_color
        
        self.setup_ui()
        self.update_display()
    
    def load_settings(self):
        """Загрузка сохраненных настроек из файла"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Ошибка загрузки настроек: {e}")
        return {"work_time": 25, "break_time": 5}
    
    def save_settings(self):
        """Сохранение настроек в файл"""
        try:
            settings = {
                "work_time": self.original_work_minutes,
                "break_time": self.original_break_minutes
            }
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Ошибка сохранения настроек: {e}")
    
    def setup_ui(self):
        # Заголовок
        title_font = font.Font(family='Arial', size=16, weight='bold')
        self.title_label = tk.Label(
            self.root, 
            text="ТАЙМЕР ПОМОДОРО",
            font=title_font,
            bg=self.current_bg_color,
            fg='black'
        )
        self.title_label.pack(pady=20)
        
        # Фрейм для настроек
        self.settings_frame = tk.Frame(self.root, bg=self.current_bg_color)
        self.settings_frame.pack(pady=10)
        
        # Поле для работы
        self.work_label = tk.Label(
            self.settings_frame,
            text="Работа (минуты):",
            font=('Arial', 10),
            bg=self.current_bg_color,
            fg='black'
        )
        self.work_label.grid(row=0, column=0, padx=10, pady=5)
        
        self.work_entry = tk.Entry(
            self.settings_frame,
            width=10,
            font=('Arial', 12),
            bg=self.work_bg_color,
            fg='black',
            justify='center'
        )
        self.work_entry.insert(0, str(self.original_work_minutes))
        self.work_entry.grid(row=0, column=1, padx=10, pady=5)
        
        # Кнопка сохранения для работы
        self.save_work_button = tk.Button(
            self.settings_frame,
            text="✓",
            font=('Arial', 10, 'bold'),
            width=3,
            bg=self.save_button_color,
            fg='black',
            command=self.save_work_time
        )
        self.save_work_button.grid(row=0, column=2, padx=5)
        
        # Поле для перерыва
        self.break_label = tk.Label(
            self.settings_frame,
            text="Перерыв (минуты):",
            font=('Arial', 10),
            bg=self.current_bg_color,
            fg='black'
        )
        self.break_label.grid(row=1, column=0, padx=10, pady=5)
        
        self.break_entry = tk.Entry(
            self.settings_frame,
            width=10,
            font=('Arial', 12),
            bg=self.break_bg_color,
            fg='black',
            justify='center'
        )
        self.break_entry.insert(0, str(self.original_break_minutes))
        self.break_entry.grid(row=1, column=1, padx=10, pady=5)
        
        # Кнопка сохранения для перерыва
        self.save_break_button = tk.Button(
            self.settings_frame,
            text="✓",
            font=('Arial', 10, 'bold'),
            width=3,
            bg=self.save_button_color,
            fg='black',
            command=self.save_break_time
        )
        self.save_break_button.grid(row=1, column=2, padx=5)
        
        # Таймер
        self.timer_font = font.Font(family='Arial', size=48, weight='bold')
        self.timer_label = tk.Label(
            self.root,
            text=self.format_time(self.current_time),
            font=self.timer_font,
            bg=self.current_bg_color,
            fg='black'
        )
        self.timer_label.pack(pady=30)
        
        # Кнопки управления
        self.control_frame = tk.Frame(self.root, bg=self.current_bg_color)
        self.control_frame.pack(pady=10)
        
        # Кнопка Работа
        self.work_button = tk.Button(
            self.control_frame,
            text="РАБОТА",
            font=('Arial', 12, 'bold'),
            width=12,
            height=2,
            bg=self.work_inactive_color,
            fg='black',
            command=self.work_button_click
        )
        self.work_button.grid(row=0, column=0, padx=5)
        
        # Кнопка Перерыв
        self.break_button = tk.Button(
            self.control_frame,
            text="ПЕРЕРЫВ",
            font=('Arial', 12, 'bold'),
            width=12,
            height=2,
            bg=self.break_inactive_color,
            fg='black',
            command=self.break_button_click
        )
        self.break_button.grid(row=0, column=1, padx=5)
        
        # Нижние кнопки
        self.bottom_frame = tk.Frame(self.root, bg=self.current_bg_color)
        self.bottom_frame.pack(pady=20)
        
        # Кнопка Сброс
        self.reset_button = tk.Button(
            self.bottom_frame,
            text="СБРОС",
            font=('Arial', 10, 'bold'),
            width=10,
            height=1,
            bg=self.reset_button_color,
            fg='black',
            command=self.reset_timer
        )
        self.reset_button.grid(row=0, column=0, padx=5)
        
        # Кнопка Выход
        self.exit_button = tk.Button(
            self.bottom_frame,
            text="ВЫХОД",
            font=('Arial', 10, 'bold'),
            width=10,
            height=1,
            bg=self.exit_button_color,
            fg='black',
            command=self.quit_application
        )
        self.exit_button.grid(row=0, column=1, padx=5)
        
        # Кнопка Свернуть
        self.minimize_button = tk.Button(
            self.bottom_frame,
            text="СВЕРНУТЬ",
            font=('Arial', 10, 'bold'),
            width=10,
            height=1,
            bg=self.minimize_button_color,
            fg='black',
            command=self.minimize_window
        )
        self.minimize_button.grid(row=0, column=2, padx=5)
        
        # Индикатор режима
        self.mode_label = tk.Label(
            self.root,
            text="Режим: РАБОТА",
            font=('Arial', 10),
            bg=self.current_bg_color,
            fg='black'
        )
        self.mode_label.pack(pady=5)
        
        # Статус таймера
        self.status_label = tk.Label(
            self.root,
            text="Таймер остановлен",
            font=('Arial', 9),
            bg=self.current_bg_color,
            fg='#666666'
        )
        self.status_label.pack(pady=2)
        
        # Простая подсказка внизу (без упоминания цвета)
        self.info_label = tk.Label(
            self.root,
            text="✓ - сохранить значение | ✗ - свернуть | СБРОС - к сохранённым значениям",
            font=('Arial', 8),
            bg=self.current_bg_color,
            fg='#666666'
        )
        self.info_label.pack(pady=5)
    
    def format_time(self, seconds):
        """Форматирование времени в MM:SS"""
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:02d}:{seconds:02d}"
    
    def update_background_color(self):
        """Обновляем цвет фона приложения"""
        if not self.is_running:
            # Таймер не работает - жёлто-зелёный
            new_color = self.idle_color
        elif self.is_work_mode:
            # Активный режим работы - светло-оранжевый
            new_color = self.work_inactive_color
        else:
            # Активный режим перерыва - светло-голубой
            new_color = self.break_inactive_color
        
        if new_color != self.current_bg_color:
            self.current_bg_color = new_color
            self.root.configure(bg=new_color)
            
            # Обновляем цвет всех виджетов
            self.update_all_widgets_color()
    
    def update_all_widgets_color(self):
        """Обновляем цвет всех виджетов при изменении цвета фона"""
        # Обновляем цвет всех меток и фреймов
        widgets_to_update = [
            self.title_label, self.settings_frame, self.work_label, 
            self.break_label, self.timer_label, self.control_frame,
            self.bottom_frame, self.mode_label, self.status_label,
            self.info_label
        ]
        
        for widget in widgets_to_update:
            try:
                widget.configure(bg=self.current_bg_color)
            except:
                pass
    
    def save_work_time(self):
        """Сохранение времени работы"""
        try:
            minutes = int(self.work_entry.get())
            if minutes < 1:
                minutes = 1
            self.original_work_minutes = minutes
            self.work_time = minutes * 60
            
            if not self.is_running and self.is_work_mode:
                self.current_time = self.work_time
                self.update_display()
            
            self.save_settings()
            
            self.save_work_button.config(bg='#00FF00')
            self.root.after(500, lambda: self.save_work_button.config(bg=self.save_button_color))
            
        except ValueError:
            self.work_entry.delete(0, tk.END)
            self.work_entry.insert(0, str(self.original_work_minutes))
    
    def save_break_time(self):
        """Сохранение времени перерыва"""
        try:
            minutes = int(self.break_entry.get())
            if minutes < 1:
                minutes = 1
            self.original_break_minutes = minutes
            self.break_time = minutes * 60
            
            if not self.is_running and not self.is_work_mode:
                self.current_time = self.break_time
                self.update_display()
            
            self.save_settings()
            
            self.save_break_button.config(bg='#00FF00')
            self.root.after(500, lambda: self.save_break_button.config(bg=self.save_button_color))
            
        except ValueError:
            self.break_entry.delete(0, tk.END)
            self.break_entry.insert(0, str(self.original_break_minutes))
    
    def work_button_click(self):
        """Обработчик клика по кнопке РАБОТА"""
        if self.is_running:
            if self.is_work_mode:
                # Останавливаем таймер работы
                self.stop_timer()
                self.paused_time = self.current_time
                self.status_label.config(text="Таймер работы остановлен")
                self.update_background_color()
            else:
                # Переключаемся с перерыва на работу
                self.stop_timer()
                self.switch_to_work()
        else:
            if self.is_work_mode:
                # Продолжаем или начинаем работу
                if self.paused_time is not None:
                    self.current_time = self.paused_time
                    self.paused_time = None
                else:
                    self.current_time = self.work_time
                
                self.start_work_mode()
            else:
                # Переключаемся с перерыва на работу
                self.switch_to_work()
    
    def break_button_click(self):
        """Обработчик клика по кнопке ПЕРЕРЫВ"""
        if self.is_running:
            if not self.is_work_mode:
                # Останавливаем таймер перерыва
                self.stop_timer()
                self.paused_time = self.current_time
                self.status_label.config(text="Таймер перерыва остановлен")
                self.update_background_color()
            else:
                # Переключаемся с работы на перерыв
                self.stop_timer()
                self.switch_to_break()
        else:
            if not self.is_work_mode:
                # Продолжаем или начинаем перерыв
                if self.paused_time is not None:
                    self.current_time = self.paused_time
                    self.paused_time = None
                else:
                    self.current_time = self.break_time
                
                self.start_break_mode()
            else:
                # Переключаемся с работы на перерыв
                self.switch_to_break()
    
    def switch_to_work(self):
        """Переключение в режим работы"""
        self.paused_time = None
        self.is_work_mode = True
        self.current_time = self.work_time
        self.start_work_mode()
        self.status_label.config(text="Таймер работы запущен")
    
    def switch_to_break(self):
        """Переключение в режим перерыва"""
        self.paused_time = None
        self.is_work_mode = False
        self.current_time = self.break_time
        self.start_break_mode()
        self.status_label.config(text="Таймер перерыва запущен")
    
    def start_work_mode(self):
        """Запуск режима работы"""
        self.is_work_mode = True
        self.is_running = True
        self.work_button.config(bg=self.work_active_color)
        self.break_button.config(bg=self.break_inactive_color)
        self.mode_label.config(text="Режим: РАБОТА")
        self.status_label.config(text="Таймер работы запущен")
        self.update_background_color()
        self.start_timer()
    
    def start_break_mode(self):
        """Запуск режима перерыва"""
        self.is_work_mode = False
        self.is_running = True
        self.break_button.config(bg=self.break_active_color)
        self.work_button.config(bg=self.work_inactive_color)
        self.mode_label.config(text="Режим: ПЕРЕРЫВ")
        self.status_label.config(text="Таймер перерыва запущен")
        self.update_background_color()
        self.start_timer()
    
    def start_timer(self):
        """Запуск таймера"""
        if not self.timer_id:
            self.update_timer()
    
    def stop_timer(self):
        """Остановка таймера"""
        self.is_running = False
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None
        
        if self.is_work_mode:
            self.work_button.config(bg=self.work_inactive_color)
        else:
            self.break_button.config(bg=self.break_inactive_color)
        
        self.update_background_color()
    
    def update_timer(self):
        """Обновление таймера"""
        if not self.is_running:
            return
        
        self.current_time -= 1
        
        if self.current_time <= 0:
            self.stop_timer()
            winsound.Beep(1000, 1000)
            
            self.paused_time = None
            
            if self.is_work_mode:
                self.current_time = self.work_time
                self.mode_label.config(text="Работа завершена!")
                self.status_label.config(text="Работа завершена. Нажмите РАБОТА для повтора или ПЕРЕРЫВ для отдыха")
            else:
                self.current_time = self.break_time
                self.mode_label.config(text="Перерыв завершён!")
                self.status_label.config(text="Перерыв завершён. Нажмите ПЕРЕРЫВ для повтора или РАБОТА для работы")
            
            self.update_background_color()
        
        self.update_display()
        
        if self.is_running:
            self.timer_id = self.root.after(1000, self.update_timer)
    
    def update_display(self):
        """Обновление отображения таймера"""
        self.timer_label.config(text=self.format_time(self.current_time))
    
    def reset_timer(self):
        """Сброс таймера к сохранённым значениям"""
        self.stop_timer()
        self.paused_time = None
        
        self.work_time = self.original_work_minutes * 60
        self.break_time = self.original_break_minutes * 60
        
        self.is_work_mode = True
        self.current_time = self.work_time
        
        self.work_entry.delete(0, tk.END)
        self.work_entry.insert(0, str(self.original_work_minutes))
        self.break_entry.delete(0, tk.END)
        self.break_entry.insert(0, str(self.original_break_minutes))
        
        self.work_button.config(bg=self.work_inactive_color)
        self.break_button.config(bg=self.break_inactive_color)
        self.mode_label.config(text="Режим: РАБОТА")
        self.status_label.config(text="Таймер сброшен к сохранённым значениям")
        
        self.update_background_color()
        self.update_display()
    
    def on_close(self):
        """Обработка закрытия окна крестиком"""
        self.save_settings()
        self.root.iconify()
    
    def minimize_window(self):
        """Сворачивание окна по кнопке"""
        self.root.iconify()
    
    def quit_application(self):
        """Выход из приложения"""
        if messagebox.askyesno("Выход", "Вы уверены, что хотите выйти?"):
            self.save_settings()
            self.stop_timer()
            self.root.quit()
            self.root.destroy()

def main():
    root = tk.Tk()
    app = PomodoroTimer(root)
    
    # Центрируем окно
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    # Устанавливаем минимальный размер окна
    root.minsize(450, 500)
    
    root.mainloop()

if __name__ == "__main__":
    main()