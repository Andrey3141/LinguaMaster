"""
Обработчик методов обучения
"""

import tkinter as tk
from config import config
from utils.notifications import show_notification

class LearningMethodHandler:
    """Класс для обработки методов обучения"""
    
    def __init__(self, controller):
        """
        Инициализация обработчика методов обучения
        
        Args:
            controller: Главный контроллер (MainWindow)
        """
        self.controller = controller
    
    def show_learning_method(self):
        """Показывает диалог выбора метода обучения"""
        dialog = tk.Toplevel(self.controller.root)
        dialog.title("Задания для тренировки слов")
        dialog.geometry("750x350")
        dialog.configure(bg=config.COLORS['bg_dark'])
        dialog.transient(self.controller.root)
        dialog.grab_set()
        
        self.controller._center_dialog(dialog)
        
        # Заголовок
        tk.Label(
            dialog,
            text="Выберите задание для тренировки слов",
            font=('Segoe UI', 16, 'bold'),
            bg=config.COLORS['bg_dark'],
            fg=config.COLORS['text']
        ).pack(pady=(20, 10))
        
        # Описание
        tk.Label(
            dialog,
            text="Как вы хотите тренироваться?",
            font=('Segoe UI', 11),
            bg=config.COLORS['bg_dark'],
            fg=config.COLORS['text_secondary']
        ).pack(pady=(0, 20))
        
        # Кнопка "Ручной перевод"
        self._create_method_button(
            dialog, "✍️ Перевод слова", config.COLORS['primary'], 'manual'
        )
        
        # Кнопка "Тест"
        self._create_method_button(
            dialog, "📝 Тест (выбор варианта)", config.COLORS['secondary'], 'test'
        )
        
        # Кнопка "Соотношение"
        self._create_method_button(
            dialog, "🔄 Сопоставление слов", config.COLORS['accent'], 'match'
        )
        
        # Кнопка "Перевод картинки"
        self._create_method_button(
            dialog, "🖼️ Назови изображенное слово", config.COLORS['warning'], 'image'
        )
    
    def _create_method_button(self, dialog, text, color, method):
        """Создает кнопку выбора метода обучения"""
        btn = tk.Button(
            dialog,
            text=text,
            font=('Segoe UI', 12, 'bold'),
            bg=color,
            fg=config.COLORS['text'],
            bd=0,
            padx=30,
            pady=10,
            cursor='hand2',
            command=lambda: self.set_learning_method(method, dialog)
        )
        btn.pack(pady=5, padx=40, fill=tk.X)
        
        btn.bind('<Enter>', lambda e, b=btn, c=color: self._on_button_hover(b, c))
        btn.bind('<Leave>', lambda e, b=btn, c=color: self._on_button_leave(b, c))
    
    def _on_button_hover(self, button, color):
        """Эффект при наведении на кнопку"""
        if color == config.COLORS['primary']:
            button.config(bg='#2563eb')
        elif color == config.COLORS['secondary']:
            button.config(bg='#059669')
        elif color == config.COLORS['accent']:
            button.config(bg='#7c3aed')
        elif color == config.COLORS['warning']:
            button.config(bg='#f97316')
    
    def _on_button_leave(self, button, color):
        """Эффект при уходе с кнопки"""
        button.config(bg=color)
    
    def set_learning_method(self, method, dialog):
        """Устанавливает метод обучения"""
        self.controller.learning_method = method
        self.controller.switch_training_panel(method)
        dialog.destroy()
        self.controller.next_word()
        
        self.controller.update_interface_colors()
        
        method_names = {
            'manual': 'ручной перевод',
            'test': 'тест',
            'match': 'соотношение',
            'image': 'перевод картинки'
        }
        
        show_notification(
            self.controller.root,
            "Метод изменен",
            f"Выбран метод: {method_names.get(method, method)}",
            "success"
        )
