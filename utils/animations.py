"""
Анимации приложения
"""

import tkinter as tk
from config import config

def animate_welcome(word_label, hint_label):
    """
    Анимация приветствия
    
    Args:
        word_label: Метка для отображения слова
        hint_label: Метка для отображения подсказки
    """
    # Устанавливаем приветственный текст
    word_label.config(text="Добро пожаловать!")
    hint_label.config(text="Готовы начать обучение?")
    
    # Можно добавить дополнительные эффекты:
    # - Мерцание текста
    # - Плавное появление
    # - Изменение цвета

def animate_success(widget, callback=None):
    """
    Анимация успешного ответа
    
    Args:
        widget: Виджет для анимации
        callback: Функция обратного вызова после анимации
    """
    original_bg = widget.cget('bg')
    
    # Первая фаза: зеленый фон
    widget.config(bg=config.COLORS['success'])
    widget.after(150, lambda: phase2(widget, original_bg, callback))

def phase2(widget, original_bg, callback):
    """Вторая фаза анимации успеха"""
    # Вторая фаза: возврат к исходному цвету
    widget.config(bg=original_bg)
    
    if callback:
        widget.after(150, callback)

def animate_error(widget, callback=None):
    """
    Анимация ошибки
    
    Args:
        widget: Виджет для анимации
        callback: Функция обратного вызова после анимации
    """
    original_bg = widget.cget('bg')
    
    # Первая фаза: красный фон
    widget.config(bg=config.COLORS['danger'])
    widget.after(150, lambda: phase2(widget, original_bg, callback))

def fade_in(widget, duration=500, callback=None):
    """
    Плавное появление виджета
    
    Args:
        widget: Виджет для анимации
        duration: Длительность анимации в мс
        callback: Функция обратного вызова после анимации
    """
    widget.place_forget() if widget.winfo_ismapped() else None
    
    # Начинаем с прозрачности
    widget.place(relx=0.5, rely=0.5, anchor='center')
    widget.update()
    
    steps = 20
    delay = duration // steps
    
    for i in range(steps + 1):
        alpha = i / steps
        widget.after(i * delay, lambda a=alpha: set_widget_alpha(widget, a))
    
    if callback:
        widget.after(duration, callback)

def set_widget_alpha(widget, alpha):
    """
    Устанавливает прозрачность виджета
    
    Args:
        widget: Виджет
        alpha: Значение прозрачности (0.0-1.0)
    """
    # Эта функция требует дополнительной реализации
    # в зависимости от платформы и возможностей tkinter
    pass

def shake_widget(widget, intensity=5, duration=300, callback=None):
    """
    Анимация тряски виджета (для ошибок)
    
    Args:
        widget: Виджет для анимации
        intensity: Интенсивность тряски
        duration: Длительность анимации в мс
        callback: Функция обратного вызова после анимации
    """
    original_x = widget.winfo_x()
    original_y = widget.winfo_y()
    
    steps = 10
    delay = duration // steps
    
    for i in range(steps):
        offset = intensity * (1 - i / steps)
        x_offset = offset if i % 2 == 0 else -offset
        
        widget.after(i * delay, lambda x=original_x + x_offset: widget.place(x=x, y=original_y))
    
    # Возвращаем в исходное положение
    widget.after(duration, lambda: widget.place(x=original_x, y=original_y))
    
    if callback:
        widget.after(duration, callback)

def pulse_animation(widget, color, duration=1000, callback=None):
    """
    Пульсирующая анимация
    
    Args:
        widget: Виджет для анимации
        color: Цвет пульсации
        duration: Длительность анимации в мс
        callback: Функция обратного вызова после анимации
    """
    original_bg = widget.cget('bg')
    steps = 10
    delay = duration // (steps * 2)
    
    def pulse_in(step):
        if step <= steps:
            alpha = step / steps
            # Смешиваем цвета
            widget.config(bg=blend_colors(original_bg, color, alpha))
            widget.after(delay, lambda: pulse_in(step + 1))
        else:
            pulse_out(steps)
    
    def pulse_out(step):
        if step >= 0:
            alpha = step / steps
            widget.config(bg=blend_colors(original_bg, color, alpha))
            widget.after(delay, lambda: pulse_out(step - 1))
        elif callback:
            widget.config(bg=original_bg)
            callback()
    
    pulse_in(1)

def blend_colors(color1, color2, alpha):
    """
    Смешивает два цвета
    
    Args:
        color1: Первый цвет в формате hex
        color2: Второй цвет в формате hex
        alpha: Коэффициент смешивания (0.0-1.0)
        
    Returns:
        str: Смешанный цвет в формате hex
    """
    # Простая реализация смешивания цветов
    # Для полноценной реализации нужно конвертировать hex в RGB
    return color2 if alpha > 0.5 else color1

def typewriter_effect(label, text, delay=50, callback=None):
    """
    Эффект печатной машинки
    
    Args:
        label: Метка для текста
        text: Текст для отображения
        delay: Задержка между символами в мс
        callback: Функция обратного вызова после анимации
    """
    label.config(text="")
    current_text = []
    
    def type_char(i):
        if i < len(text):
            current_text.append(text[i])
            label.config(text="".join(current_text))
            label.after(delay, lambda: type_char(i + 1))
        elif callback:
            callback()
    
    type_char(0)

def count_up_animation(label, start_value, end_value, duration=1000, callback=None):
    """
    Анимация счетчика с увеличением значения
    
    Args:
        label: Метка для отображения значения
        start_value: Начальное значение
        end_value: Конечное значение
        duration: Длительность анимации в мс
        callback: Функция обратного вызова после анимации
    """
    steps = 30
    delay = duration // steps
    increment = (end_value - start_value) / steps
    
    def update_value(step):
        if step <= steps:
            current_value = start_value + increment * step
            label.config(text=f"{current_value:.0f}")
            label.after(delay, lambda: update_value(step + 1))
        elif callback:
            callback()
    
    update_value(1)
