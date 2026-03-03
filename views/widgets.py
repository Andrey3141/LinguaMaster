"""
Кастомные виджеты для приложения
"""

import tkinter as tk
from config import config

class ModernButton(tk.Button):
    """Современная кнопка с эффектами"""
    
    def __init__(self, parent, **kwargs):
        """
        Инициализация современной кнопки
        
        Args:
            parent: Родительский виджет
            **kwargs: Дополнительные параметры
        """
        # Извлекаем кастомные параметры
        self.hover_color = kwargs.pop('hover_color', config.COLORS['primary'])
        self.original_color = kwargs.get('bg', config.COLORS['bg_card'])
        
        # Базовые стили
        kwargs.setdefault('bd', 0)
        kwargs.setdefault('cursor', 'hand2')
        kwargs.setdefault('relief', 'flat')
        
        super().__init__(parent, **kwargs)
        
        # Привязываем события мыши
        self.bind('<Enter>', self.on_enter)
        self.bind('<Leave>', self.on_leave)
        self.bind('<ButtonPress>', self.on_press)
        self.bind('<ButtonRelease>', self.on_release)
    
    def on_enter(self, event):
        """Обработчик наведения мыши"""
        self.config(bg=self.hover_color)
    
    def on_leave(self, event):
        """Обработчик ухода мыши"""
        self.config(bg=self.original_color)
    
    def on_press(self, event):
        """Обработчик нажатия кнопки"""
        # Слегка затемняем цвет при нажатии
        self.config(relief='sunken')
    
    def on_release(self, event):
        """Обработчик отпускания кнопки"""
        self.config(relief='flat')

class CardFrame(tk.Frame):
    """Карточка с тенями и скруглениями"""
    
    def __init__(self, parent, **kwargs):
        """
        Инициализация карточки
        
        Args:
            parent: Родительский виджет
            **kwargs: Дополнительные параметры
        """
        # Стили карточки
        kwargs.setdefault('bg', config.COLORS['bg_card'])
        kwargs.setdefault('relief', 'flat')
        kwargs.setdefault('highlightbackground', config.COLORS['border'])
        kwargs.setdefault('highlightthickness', 1)
        
        super().__init__(parent, **kwargs)

class ModernEntry(tk.Entry):
    """Современное поле ввода с подчеркиванием"""
    
    def __init__(self, parent, **kwargs):
        """
        Инициализация современного поля ввода
        
        Args:
            parent: Родительский виджет
            **kwargs: Дополнительные параметры
        """
        # Стили по умолчанию
        kwargs.setdefault('bg', config.COLORS['bg_dark'])
        kwargs.setdefault('fg', config.COLORS['text'])
        kwargs.setdefault('insertbackground', config.COLORS['text'])
        kwargs.setdefault('bd', 0)
        kwargs.setdefault('relief', 'flat')
        kwargs.setdefault('font', config.FONTS['body'])
        
        super().__init__(parent, **kwargs)
        
        # Создаем подчеркивание
        self.underline = tk.Frame(
            parent,
            height=2,
            bg=config.COLORS['bg_card']
        )
        
        # Привязываем события
        self.bind('<FocusIn>', self.on_focus_in)
        self.bind('<FocusOut>', self.on_focus_out)
    
    def place(self, **kwargs):
        """Переопределение метода размещения"""
        super().place(**kwargs)
        
        # Размещаем подчеркивание под полем ввода
        x = kwargs.get('x', 0)
        y = kwargs.get('y', 0) + self.winfo_reqheight() - 2
        width = kwargs.get('width', self.winfo_reqwidth())
        
        self.underline.place(x=x, y=y, width=width)
    
    def pack(self, **kwargs):
        """Переопределение метода упаковки"""
        super().pack(**kwargs)
        self.underline.pack(fill=tk.X, pady=(2, 0))
    
    def grid(self, **kwargs):
        """Переопределение метода размещения в сетке"""
        super().grid(**kwargs)
        # Для grid нужно специально обрабатывать подчеркивание
    
    def on_focus_in(self, event):
        """Обработчик получения фокуса"""
        self.underline.config(bg=config.COLORS['primary'])
    
    def on_focus_out(self, event):
        """Обработчик потери фокуса"""
        self.underline.config(bg=config.COLORS['bg_card'])

class IconLabel(tk.Label):
    """Метка с иконкой и текстом"""
    
    def __init__(self, parent, icon, text, **kwargs):
        """
        Инициализация метки с иконкой
        
        Args:
            parent: Родительский виджет
            icon: Иконка (эмодзи или символ)
            text: Текст
            **kwargs: Дополнительные параметры
        """
        kwargs.setdefault('compound', 'left')
        kwargs.setdefault('font', config.FONTS['body'])
        kwargs.setdefault('bg', config.COLORS['bg_dark'])
        kwargs.setdefault('fg', config.COLORS['text'])
        
        super().__init__(parent, text=f"{icon}  {text}", **kwargs)

class ProgressCard(tk.Frame):
    """Карточка с прогресс-баром"""
    
    def __init__(self, parent, title, value=0, max_value=100, **kwargs):
        """
        Инициализация карточки прогресса
        
        Args:
            parent: Родительский виджет
            title: Заголовок
            value: Текущее значение
            max_value: Максимальное значение
            **kwargs: Дополнительные параметры
        """
        super().__init__(parent, bg=config.COLORS['bg_card'], **kwargs)
        
        # Заголовок
        title_label = tk.Label(
            self,
            text=title,
            font=config.FONTS['body_small'],
            bg=config.COLORS['bg_card'],
            fg=config.COLORS['text_secondary']
        )
        title_label.pack(anchor='w', pady=(10, 5))
        
        # Прогресс-бар
        self.progress_frame = tk.Frame(self, bg=config.COLORS['bg_card'])
        self.progress_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Фон прогресс-бара
        self.bg_bar = tk.Frame(
            self.progress_frame,
            height=8,
            bg=config.COLORS['bg_dark'],
            relief='flat'
        )
        self.bg_bar.pack(fill=tk.X)
        
        # Передний план прогресс-бара
        self.fg_bar = tk.Frame(
            self.bg_bar,
            height=8,
            bg=config.COLORS['primary']
        )
        
        # Значение
        self.value_label = tk.Label(
            self,
            text=f"{value}/{max_value}",
            font=config.FONTS['body'],
            bg=config.COLORS['bg_card'],
            fg=config.COLORS['text']
        )
        self.value_label.pack(anchor='e', padx=10, pady=(0, 10))
        
        # Устанавливаем начальное значение
        self.set_value(value, max_value)
    
    def set_value(self, value, max_value=100):
        """
        Устанавливает значение прогресс-бара
        
        Args:
            value: Текущее значение
            max_value: Максимальное значение
        """
        percentage = min(value / max_value, 1.0)
        width = self.bg_bar.winfo_width() or 100
        
        # Обновляем передний план
        self.fg_bar.place(x=0, y=0, width=int(width * percentage), height=8)
        
        # Обновляем текстовое значение
        self.value_label.config(text=f"{value}/{max_value}")

class StatsCard(tk.Frame):
    """Карточка статистики"""
    
    def __init__(self, parent, title, value, icon, color, **kwargs):
        """
        Инициализация карточки статистики
        
        Args:
            parent: Родительский виджет
            title: Заголовок
            value: Значение
            icon: Иконка
            color: Цвет иконки
            **kwargs: Дополнительные параметры
        """
        super().__init__(parent, bg=config.COLORS['bg_card'], **kwargs)
        
        # Иконка
        icon_label = tk.Label(
            self,
            text=icon,
            font=('Segoe UI', 24),
            bg=config.COLORS['bg_card'],
            fg=color
        )
        icon_label.pack(side=tk.LEFT, padx=15, pady=15)
        
        # Текст
        text_frame = tk.Frame(self, bg=config.COLORS['bg_card'])
        text_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 15))
        
        # Заголовок
        self.title_label = tk.Label(
            text_frame,
            text=title,
            font=config.FONTS['body_small'],
            bg=config.COLORS['bg_card'],
            fg=config.COLORS['text_secondary']
        )
        self.title_label.pack(anchor='w')
        
        # Значение
        self.value_label = tk.Label(
            text_frame,
            text=value,
            font=('Segoe UI', 20, 'bold'),
            bg=config.COLORS['bg_card'],
            fg=config.COLORS['text']
        )
        self.value_label.pack(anchor='w')
    
    def update_value(self, value):
        """
        Обновляет значение карточки
        
        Args:
            value: Новое значение
        """
        self.value_label.config(text=value)
