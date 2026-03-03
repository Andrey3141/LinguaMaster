"""
Верхняя панель
"""

import tkinter as tk
from config import config

class TopBar:
    """Класс верхней панели"""
    
    def __init__(self, parent, controller):
        """
        Инициализация верхней панели
        
        Args:
            parent: Родительский виджет
            controller: Контроллер (MainWindow)
        """
        self.parent = parent
        self.controller = controller
        self.fullscreen = False
        
        self.create_widgets()
    
    def create_widgets(self):
        """Создание виджетов панели"""
        # Основной фрейм
        self.main_frame = tk.Frame(
            self.parent, 
            bg=config.COLORS['bg_dark'],
            height=60
        )
        self.main_frame.pack_propagate(False)
        
        # Левый блок - логотип
        logo_frame = tk.Frame(self.main_frame, bg=config.COLORS['bg_dark'])
        logo_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        # Логотип
        tk.Label(
            logo_frame,
            text="🎓",
            font=('Segoe UI', 28),
            bg=config.COLORS['bg_dark'],
            fg=config.COLORS['primary']
        ).pack(side=tk.LEFT)
        
        # Название приложения
        tk.Label(
            logo_frame,
            text=config.TEXTS['app_name'],
            font=('Segoe UI', 20, 'bold'),
            bg=config.COLORS['bg_dark'],
            fg=config.COLORS['text']
        ).pack(side=tk.LEFT, padx=(10, 0))
        
        tk.Label(
            logo_frame,
            text=config.TEXTS['app_subtitle'],
            font=config.FONTS['subtitle'],
            bg=config.COLORS['bg_dark'],
            fg=config.COLORS['text_secondary']
        ).pack(side=tk.LEFT, padx=(10, 0))
        
        # Центральный блок - кнопка полноэкранного режима
        center_frame = tk.Frame(self.main_frame, bg=config.COLORS['bg_dark'])
        center_frame.pack(side=tk.LEFT, fill=tk.Y, expand=True)
        
        # Кнопка полноэкранного режима
        self.fullscreen_btn = tk.Button(
            center_frame,
            text="⛶ Полный экран",
            font=('Segoe UI', 10),
            bg=config.COLORS['bg_card'],
            fg=config.COLORS['text'],
            bd=0,
            padx=15,
            pady=5,
            cursor='hand2',
            command=self.toggle_fullscreen,
            relief='flat'
        )
        self.fullscreen_btn.pack(anchor='center')
        
        # Привязываем события для кнопки полноэкранного режима
        self.fullscreen_btn.bind('<Enter>', lambda e: self.fullscreen_btn.config(
            bg=config.COLORS['primary'], 
            fg=config.COLORS['text']
        ))
        self.fullscreen_btn.bind('<Leave>', lambda e: self.fullscreen_btn.config(
            bg=config.COLORS['bg_card'], 
            fg=config.COLORS['text']
        ))
        
        # Правый блок - статистика и режимы
        right_frame = tk.Frame(self.main_frame, bg=config.COLORS['bg_dark'])
        right_frame.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Статистика
        self.stats_label = tk.Label(
            right_frame,
            text="Слов: 0 | Изучено: 0 | Прогресс: 0%",
            font=('Segoe UI', 10),
            bg=config.COLORS['bg_dark'],
            fg=config.COLORS['text_secondary']
        )
        self.stats_label.pack(side=tk.RIGHT, padx=(20, 0))
        
        # Кнопки выбора режима
        self.mode_frame = tk.Frame(right_frame, bg=config.COLORS['bg_dark'])
        self.mode_frame.pack(side=tk.RIGHT)
        
        # Создаем кнопки режимов
        self.create_mode_buttons()
    
    def toggle_fullscreen(self):
        """Переключает полноэкранный режим"""
        self.fullscreen = not self.fullscreen
        self.controller.root.attributes('-fullscreen', self.fullscreen)
        
        if self.fullscreen:
            self.fullscreen_btn.config(text="🗗 Выйти из полного экрана")
        else:
            self.fullscreen_btn.config(text="⛶ Полный экран")
    
    def create_mode_buttons(self):
        """Создает кнопки выбора режима - динамически на основе текущих языков"""
        # Получаем текущие языки из контроллера
        study_lang = self.controller.language
        native_lang = self.controller.native_language
        
        # Удаляем старые кнопки если есть
        for widget in self.mode_frame.winfo_children():
            widget.destroy()
        
        # Сбрасываем словарь кнопок
        self.mode_buttons = {}
        
        # Режимы тренировки
        modes = [
            {'code': f'{study_lang}-{native_lang}', 
             'label': f'{config.LANGUAGES[study_lang]["flag"]} → {config.LANGUAGES[native_lang]["flag"]}'},
            {'code': f'{native_lang}-{study_lang}', 
             'label': f'{config.LANGUAGES[native_lang]["flag"]} → {config.LANGUAGES[study_lang]["flag"]}'},
        ]
        
        for mode in modes:
            btn = tk.Button(
                self.mode_frame,
                text=mode['label'],
                font=('Segoe UI', 12),
                bg=config.COLORS['bg_card'],
                fg=config.COLORS['text_secondary'],
                bd=0,
                padx=10,
                pady=5,
                cursor='hand2',
                command=lambda m=mode['code']: self.controller.set_mode(m),
                relief='flat'
            )
            btn.pack(side=tk.LEFT, padx=(0, 5))
            
            # Привязываем события для кнопок режима
            btn.bind('<Enter>', lambda e, b=btn: b.config(
                bg=config.COLORS['primary'], 
                fg=config.COLORS['text']
            ))
            btn.bind('<Leave>', lambda e, b=btn, m=mode['code']: 
                b.config(
                    bg=config.COLORS['primary'] if m == self.controller.mode else config.COLORS['bg_card'],
                    fg=config.COLORS['text'] if m == self.controller.mode else config.COLORS['text_secondary']
                )
            )
            
            # Сохраняем ссылку на кнопку
            self.mode_buttons[mode['code']] = btn
        
        # Сразу обновляем активную кнопку
        self.update_mode_buttons(self.controller.mode)
    
    def update_mode_buttons(self, active_mode):
        """
        Обновляет состояние кнопок режима
        
        Args:
            active_mode: Активный режим
        """
        if hasattr(self, 'mode_buttons'):
            for mode_code, button in self.mode_buttons.items():
                if mode_code == active_mode:
                    button.config(bg=config.COLORS['primary'], fg=config.COLORS['text'])
                else:
                    button.config(bg=config.COLORS['bg_card'], fg=config.COLORS['text_secondary'])
    
    def update_stats(self, stats):
        """
        Обновляет статистику в верхней панели
        
        Args:
            stats: Словарь со статистиками
        """
        total_words = stats.get('total_words', 0)
        learned_words = stats.get('learned_words', 0)
        progress = stats.get('progress', 0)
        
        self.stats_label.config(
            text=f"Слов: {total_words} | Изучено: {learned_words} | Прогресс: {progress:.0f}%"
        )
    
    def refresh_mode_buttons(self):
        """Обновляет кнопки режима при смене языка"""
        self.create_mode_buttons()
    
    def pack(self, **kwargs):
        """Упаковка панели"""
        self.main_frame.pack(**kwargs)

