"""
Уведомления приложения
"""

import tkinter as tk
from config import config

def show_notification(root, title, message, type_="info", duration=2000):
    """
    Показывает всплывающее уведомление
    
    Args:
        root: Корневое окно
        title: Заголовок уведомления
        message: Текст сообщения
        type_: Тип уведомления ('info', 'success', 'warning', 'error')
        duration: Длительность показа в миллисекундах
    """
    # Цвета для разных типов уведомлений
    colors = {
        'info': config.COLORS['primary'],
        'success': config.COLORS['success'],
        'warning': config.COLORS['warning'],
        'error': config.COLORS['danger']
    }
    
    bg_color = colors.get(type_, config.COLORS['primary'])
    
    # Создаем окно уведомления
    notification = tk.Toplevel(root)
    notification.title("")
    notification.geometry("350x120")
    notification.configure(bg=bg_color)
    notification.overrideredirect(True)
    
    # Иконка для типа уведомления
    icons = {
        'info': 'ℹ️',
        'success': '✅',
        'warning': '⚠️',
        'error': '❌'
    }
    
    icon = icons.get(type_, 'ℹ️')
    
    # Позиционируем по центру
    center_window(notification, root)
    
    # Создаем содержимое уведомления
    create_notification_content(notification, icon, title, message, bg_color)
    
    # Автоматическое закрытие через указанное время
    notification.after(duration, notification.destroy)
    
    # Возможность закрытия по клику
    notification.bind('<Button-1>', lambda e: notification.destroy())

def center_window(window, parent):
    """
    Центрирует окно относительно родительского
    
    Args:
        window: Окно для центрирования
        parent: Родительское окно
    """
    window.update_idletasks()
    
    width = window.winfo_width()
    height = window.winfo_height()
    
    x = parent.winfo_rootx() + (parent.winfo_width() // 2) - (width // 2)
    y = parent.winfo_rooty() + (parent.winfo_height() // 2) - (height // 2)
    
    window.geometry(f'+{x}+{y}')

def create_notification_content(window, icon, title, message, bg_color):
    """
    Создает содержимое уведомления
    
    Args:
        window: Окно уведомления
        icon: Иконка
        title: Заголовок
        message: Сообщение
        bg_color: Цвет фона
    """
    # Фрейм для содержимого
    content_frame = tk.Frame(window, bg=bg_color)
    content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    # Иконка и заголовок в одной строке
    header_frame = tk.Frame(content_frame, bg=bg_color)
    header_frame.pack(anchor='w', pady=(0, 10))
    
    # Иконка
    icon_label = tk.Label(
        header_frame,
        text=icon,
        font=('Segoe UI', 24),
        bg=bg_color,
        fg=config.COLORS['text']
    )
    icon_label.pack(side=tk.LEFT, padx=(0, 10))
    
    # Заголовок
    title_label = tk.Label(
        header_frame,
        text=title,
        font=('Segoe UI', 14, 'bold'),
        bg=bg_color,
        fg=config.COLORS['text']
    )
    title_label.pack(side=tk.LEFT)
    
    # Сообщение
    message_label = tk.Label(
        content_frame,
        text=message,
        font=('Segoe UI', 11),
        bg=bg_color,
        fg=config.COLORS['text'],
        wraplength=300,
        justify='left'
    )
    message_label.pack(anchor='w')

def show_toast(root, message, position="bottom", duration=1500):
    """
    Показывает тост-уведомление
    
    Args:
        root: Корневое окно
        message: Сообщение
        position: Позиция ('top', 'bottom', 'center')
        duration: Длительность показа
    """
    toast = tk.Toplevel(root)
    toast.title("")
    toast.configure(bg=config.COLORS['bg_card'])
    toast.overrideredirect(True)
    
    # Настраиваем прозрачность (если поддерживается)
    try:
        toast.attributes('-alpha', 0.9)
    except:
        pass
    
    # Создаем содержимое тоста
    label = tk.Label(
        toast,
        text=message,
        font=('Segoe UI', 10),
        bg=config.COLORS['bg_card'],
        fg=config.COLORS['text'],
        padx=20,
        pady=10
    )
    label.pack()
    
    # Позиционируем тост
    position_toast(toast, root, position)
    
    # Анимация появления
    toast.attributes('-alpha', 0)
    fade_in(toast, 300)
    
    # Автоматическое закрытие
    toast.after(duration, lambda: fade_out(toast, 300))

def position_toast(toast, parent, position):
    """
    Позиционирует тост-уведомление
    
    Args:
        toast: Окно тоста
        parent: Родительское окно
        position: Позиция
    """
    toast.update_idletasks()
    
    width = toast.winfo_width()
    height = toast.winfo_height()
    parent_width = parent.winfo_width()
    parent_height = parent.winfo_height()
    
    x = parent.winfo_rootx() + (parent_width // 2) - (width // 2)
    
    if position == "top":
        y = parent.winfo_rooty() + 50
    elif position == "bottom":
        y = parent.winfo_rooty() + parent_height - height - 50
    else:  # center
        y = parent.winfo_rooty() + (parent_height // 2) - (height // 2)
    
    toast.geometry(f'+{x}+{y}')

def fade_in(window, duration=300):
    """
    Плавное появление окна
    
    Args:
        window: Окно
        duration: Длительность анимации
    """
    steps = 10
    delay = duration // steps
    
    def increase_opacity(step):
        if step <= steps:
            try:
                alpha = step / steps
                window.attributes('-alpha', alpha)
                window.after(delay, lambda: increase_opacity(step + 1))
            except:
                pass
    
    increase_opacity(1)

def fade_out(window, duration=300):
    """
    Плавное исчезновение окна
    
    Args:
        window: Окно
        duration: Длительность анимации
    """
    steps = 10
    delay = duration // steps
    
    def decrease_opacity(step):
        if step >= 0:
            try:
                alpha = step / steps
                window.attributes('-alpha', alpha)
                window.after(delay, lambda: decrease_opacity(step - 1))
            except:
                pass
        else:
            window.destroy()
    
    decrease_opacity(steps)

def show_confirmation_dialog(root, title, message, on_confirm, on_cancel=None):
    """
    Показывает диалог подтверждения
    
    Args:
        root: Корневое окно
        title: Заголовок диалога
        message: Сообщение
        on_confirm: Функция при подтверждении
        on_cancel: Функция при отмене (опционально)
    """
    dialog = tk.Toplevel(root)
    dialog.title(title)
    dialog.geometry("400x200")
    dialog.configure(bg=config.COLORS['bg_dark'])
    dialog.resizable(False, False)
    
    # Центрируем
    center_window(dialog, root)
    
    # Заголовок
    tk.Label(
        dialog,
        text=title,
        font=('Segoe UI', 16, 'bold'),
        bg=config.COLORS['bg_dark'],
        fg=config.COLORS['text']
    ).pack(pady=(30, 10))
    
    # Сообщение
    tk.Label(
        dialog,
        text=message,
        font=config.FONTS['body'],
        bg=config.COLORS['bg_dark'],
        fg=config.COLORS['text_secondary'],
        wraplength=350
    ).pack(pady=10, padx=20)
    
    # Кнопки
    button_frame = tk.Frame(dialog, bg=config.COLORS['bg_dark'])
    button_frame.pack(pady=30)
    
    # Кнопка подтверждения
    tk.Button(
        button_frame,
        text="Подтвердить",
        font=config.FONTS['body'],
        bg=config.COLORS['success'],
        fg=config.COLORS['text'],
        bd=0,
        padx=25,
        pady=8,
        cursor='hand2',
        command=lambda: [on_confirm(), dialog.destroy()]
    ).pack(side=tk.LEFT, padx=(0, 10))
    
    # Кнопка отмены
    tk.Button(
        button_frame,
        text="Отмена",
        font=config.FONTS['body'],
        bg=config.COLORS['bg_card'],
        fg=config.COLORS['text_secondary'],
        bd=0,
        padx=25,
        pady=8,
        cursor='hand2',
        command=lambda: [on_cancel() if on_cancel else None, dialog.destroy()]
    ).pack(side=tk.LEFT)
    
    dialog.transient(root)
    dialog.grab_set()
    dialog.wait_window()
