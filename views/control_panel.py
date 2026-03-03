"""
Панель управления
"""

import tkinter as tk
from config import config

class ControlPanel:
    """Класс панели управления"""
    
    def __init__(self, parent, controller):
        """
        Инициализация панели управления
        
        Args:
            parent: Родительский виджет
            controller: Контроллер (MainWindow)
        """
        self.parent = parent
        self.controller = controller
        self.button_active = {}  # Словарь для отслеживания состояния кнопок
        
        self.create_widgets()
    
    def create_widgets(self):
        """Создание виджетов панели"""
        # Основной фрейм
        self.main_frame = tk.Frame(
            self.parent, 
            bg=config.COLORS['bg_card'],
            width=280
        )
        self.main_frame.pack_propagate(False)
        
        # Заголовок
        tk.Label(
            self.main_frame,
            text="⚙️ Управление",
            font=('Segoe UI', 16, 'bold'),
            bg=config.COLORS['bg_card'],
            fg=config.COLORS['text']
        ).pack(fill=tk.X, pady=20)
        
        # Кнопки действий
        self.create_action_buttons()
    
    def create_action_buttons(self):
        """Создание кнопок действий"""
        actions = [
            {"text": "Добавить слово", "icon": "➕", "command": self.controller.add_word_dialog, "color": config.COLORS['primary']},
            {"text": "Показать словарь", "icon": "📖", "command": self.controller.show_vocabulary, "color": config.COLORS['accent']},
            {"text": "Настройки", "icon": "⚙️", "command": self.controller.show_settings_dialog, "color": config.COLORS['warning']},
            {"text": "Обновить список", "icon": "🔄", "command": self.controller.refresh_words, "color": config.COLORS['success']},
            {"text": "Задания для тренировки", "icon": "🎓", "command": self.controller.show_learning_method, "color": config.COLORS['secondary']},  # ← НОВАЯ КНОПКА
            {"text": "Сложные слова", "icon": "🎯", "command": self.controller.show_hard_words, "color": config.COLORS['warning']},
            {"text": "Статистика", "icon": "📊", "command": self.controller.show_detailed_stats, "color": config.COLORS['text_secondary']},
            {"text": "Быстрая тренировка", "icon": "⚡", "command": self.controller.quick_training, "color": config.COLORS['danger']},
            {"text": "Сменить язык", "icon": "🌐", "command": self.controller.change_language_dialog, "color": config.COLORS['primary']}
        ]
        
        for i, action in enumerate(actions):
            btn = tk.Button(
                self.main_frame,
                text=f"{action['icon']} {action['text']}",
                font=('Segoe UI', 11),
                bg=config.COLORS['bg_dark'],
                fg=action['color'],
                bd=0,
                padx=15,
                pady=10,
                cursor='hand2',
                command=self.create_button_handler(action['command'], f"btn_{i}"),
                wraplength=250,
                justify='left'
            )
            btn.pack(fill=tk.X, pady=5)
            
            # Простая привязка событий
            original_bg = config.COLORS['bg_dark']
            original_fg = action['color']
            
            btn.bind('<Enter>', lambda e, b=btn: b.config(bg=config.COLORS['primary'], fg=config.COLORS['text']))
            btn.bind('<Leave>', lambda e, b=btn: b.config(bg=original_bg, fg=original_fg))
            
            # Инициализируем состояние кнопки
            self.button_active[f"btn_{i}"] = False
    
    def create_button_handler(self, command, btn_id):
        """Создает обработчик для кнопки с защитой от двойного нажатия"""
        def handler():
            # Проверяем, активна ли уже кнопка
            if self.button_active.get(btn_id, False):
                return  # Игнорируем повторное нажатие
            
            # Устанавливаем флаг активности
            self.button_active[btn_id] = True
            
            try:
                # Выполняем команду
                command()
            finally:
                # Сбрасываем флаг активности через небольшой таймаут
                self.controller.root.after(500, lambda: self.reset_button(btn_id))
        
        return handler
    
    def reset_button(self, btn_id):
        """Сбрасывает флаг активности кнопки"""
        self.button_active[btn_id] = False
    
    def pack(self, **kwargs):
        """Упаковка панели"""
        self.main_frame.pack(**kwargs)
