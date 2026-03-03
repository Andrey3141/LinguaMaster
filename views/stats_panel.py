"""
Панель статистики
"""

import tkinter as tk
from config import config

class StatsPanel:
    """Класс панели статистики"""
    
    def __init__(self, parent, controller):
        """
        Инициализация панели статистики
        
        Args:
            parent: Родительский виджет
            controller: Контроллер (MainWindow)
        """
        self.parent = parent
        self.controller = controller
        
        self.create_widgets()
    
    def create_widgets(self):
        """Создание виджетов панели"""
        # Основной фрейм
        self.main_frame = tk.Frame(
            self.parent, 
            bg=config.COLORS['bg_card'],
            width=250
        )
        self.main_frame.pack_propagate(False)
        
        # Заголовок
        tk.Label(
            self.main_frame,
            text="📊 Статистика",
            font=('Segoe UI', 16, 'bold'),
            bg=config.COLORS['bg_card'],
            fg=config.COLORS['text']
        ).pack(fill=tk.X, pady=20)
        
        # Карточки статистики
        self.stats_cards = {}
        
        self.stats_cards['total'] = self.create_stat_card("📚 Всего слов", "0", config.COLORS['primary'])
        self.stats_cards['learned'] = self.create_stat_card("🎓 Изучено", "0", config.COLORS['success'])
        self.stats_cards['hard'] = self.create_stat_card("🎯 Сложные слова", "0", config.COLORS['warning'])
        self.stats_cards['today'] = self.create_stat_card("📅 Сегодня", "0", config.COLORS['accent'])
        
        # Прогресс изучения
        self.create_progress_card()
    
    def create_stat_card(self, title, value, color):
        """Создает карточку статистики"""
        card_frame = tk.Frame(self.main_frame, bg=config.COLORS['bg_card'])
        card_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(
            card_frame,
            text=title,
            font=('Segoe UI', 10),
            bg=config.COLORS['bg_card'],
            fg=config.COLORS['text_secondary']
        ).pack(fill=tk.X)
        
        value_label = tk.Label(
            card_frame,
            text=value,
            font=('Segoe UI', 18, 'bold'),
            bg=config.COLORS['bg_card'],
            fg=color
        )
        value_label.pack(fill=tk.X)
        
        return {'value': value_label}
    
    def create_progress_card(self):
        """Создает карточку с прогрессом"""
        progress_frame = tk.Frame(self.main_frame, bg=config.COLORS['bg_card'])
        progress_frame.pack(fill=tk.X, pady=20)
        
        tk.Label(
            progress_frame,
            text="📈 Общий прогресс",
            font=('Segoe UI', 10),
            bg=config.COLORS['bg_card'],
            fg=config.COLORS['text_secondary']
        ).pack(fill=tk.X)
        
        self.progress_canvas = tk.Canvas(
            progress_frame,
            height=10,
            bg=config.COLORS['bg_card'],
            highlightthickness=0
        )
        self.progress_canvas.pack(fill=tk.X, pady=5)
        
        self.progress_canvas.create_rectangle(0, 0, 100, 10, fill=config.COLORS['bg_dark'], outline='')
        self.progress_fill = self.progress_canvas.create_rectangle(0, 0, 0, 10, fill=config.COLORS['primary'], outline='')
        
        self.progress_text = tk.Label(
            progress_frame,
            text="0%",
            font=('Segoe UI', 9),
            bg=config.COLORS['bg_card'],
            fg=config.COLORS['text_secondary']
        )
        self.progress_text.pack(fill=tk.X)
    
    def update_stats(self, stats):
        """Обновляет статистики"""
        # Защита от отсутствующих ключей
        total_words = stats.get('total_words', 0)
        learned_words = stats.get('learned_words', 0)
        hard_words = stats.get('hard_words', 0)
        daily_words = stats.get('daily_words', 0)
        progress = stats.get('progress', 0)
        
        self.stats_cards['total']['value'].config(text=str(total_words))
        self.stats_cards['learned']['value'].config(text=str(learned_words))
        self.stats_cards['hard']['value'].config(text=str(hard_words))
        self.stats_cards['today']['value'].config(text=str(daily_words))
        
        width = self.progress_canvas.winfo_width() or 100
        fill_width = int(width * (progress / 100))
        
        self.progress_canvas.coords(self.progress_fill, 0, 0, fill_width, 10)
        self.progress_text.config(text=f"{progress:.0f}%")
    
    def pack(self, **kwargs):
        """Упаковка панели"""
        self.main_frame.pack(**kwargs)
