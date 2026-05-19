"""
Главное окно приложения
"""

import tkinter as tk
from tkinter import ttk
import webbrowser
import random
import time
from config import config
from models.vocabulary import VocabularyModel
from .top_bar import TopBar
from .stats_panel import StatsPanel
from .training_panel import TrainingPanel
from .test_panel import TestPanel
from .match_panel import MatchPanel
from .image_panel import ImagePanel
from .control_panel import ControlPanel
from .answer_handlers import AnswerHandlers
from .navigation import NavigationHandler
from .learning_methods import LearningMethodHandler
from utils.notifications import show_notification
from utils.speech import speech_synth
from utils.settings_manager import settings_manager

class MainWindow:
    """Класс главного окна приложения"""
    
    def __init__(self, root):
        """
        Инициализация главного окна
        
        Args:
            root: Корневое окно tkinter
        """
        self.root = root
        self.root.title(f"{config.TEXTS['app_name']} - {config.TEXTS['app_subtitle']}")
        
        # Получаем размеры экрана
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Устанавливаем окно на весь экран
        self.root.geometry(f"{screen_width}x{screen_height}+0+0")
        
        # Отключаем изменение размера окна
        self.root.resizable(False, False)
        
        # Устанавливаем цвет фона
        self.root.configure(bg=config.COLORS['bg_dark'])
        
        # Стиль окна
        self.root.option_add('*Font', ('Segoe UI', 10))
        
        # Инициализируем модель
        self.model = VocabularyModel()
        
        # Загружаем сохраненные настройки
        saved_settings = settings_manager.get_all()
        
        # Настройки приложения (сначала из конфига, потом перезаписываем сохраненными)
        self.language = saved_settings.get('language', config.TRAINING_SETTINGS['default_language'])
        self.native_language = saved_settings.get('native_language', config.TRAINING_SETTINGS['native_language'])
        self.mode = f'{self.language}-{self.native_language}'
        self.difficulty = saved_settings.get('difficulty', 'all')
        self.current_category = saved_settings.get('current_category', None)
        self.learning_method = saved_settings.get('learning_method', 'manual')
        
        # Объединяем все настройки
        self.settings = {}
        self.settings.update(config.TRAINING_SETTINGS.copy())
        self.settings.update(config.SPEECH_SETTINGS.copy())
        
        # Добавляем значения по умолчанию для подсказок
        if 'show_hints' not in self.settings:
            self.settings['show_hints'] = False
        if 'hint_threshold' not in self.settings:
            self.settings['hint_threshold'] = 3
        
        # Перезаписываем сохраненными настройками
        saved_app_settings = saved_settings.get('app_settings', {})
        for key, value in saved_app_settings.items():
            if key in self.settings:
                self.settings[key] = value
        
        # Флаг для защиты от DoS-атаки
        self.check_in_progress = False
        self.last_check_time = 0
        
        self.dialogs = {}  # Словарь для отслеживания открытых диалогов
        
        # Список недавно показанных слов
        self.recent_words = []
        self.max_recent_words = 10
        
        # Инициализируем обработчики
        self.answer_handler = AnswerHandlers(self)
        self.navigation_handler = NavigationHandler(self)
        self.learning_method_handler = LearningMethodHandler(self)
        
        # Проверяем доступность RHVoice
        if not speech_synth.is_available():
            self.settings['enabled'] = False
        else:
            speech_synth.set_volume(self.settings['volume'])
            speech_synth.set_speed(self.settings['speed'])
            speech_synth.set_enabled(self.settings['enabled'])
        
        self._setup_styles()
        self._setup_ui()
        
        self.root.after(100, self.show_welcome)
        
        # Добавляем начальные слова, если словарь пуст
        if len(self.model.vocabulary) == 0:
            initial_words = [
                ("hello", ["привет"], "en", "ru"),
                ("world", ["мир"], "en", "ru"),
                ("cat", ["кот"], "en", "ru"),
                ("dog", ["собака"], "en", "ru"),
                ("book", ["книга"], "en", "ru"),
            ]
            for foreign, translations, lang, native in initial_words:
                self.model.add_word(foreign, translations, lang, native)
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def _setup_styles(self):
        """Настройка кастомных стилей"""
        style = ttk.Style()
        style.configure('Custom.Horizontal.TProgressbar',
                       background=config.COLORS['primary'],
                       troughcolor=config.COLORS['bg_card'],
                       bordercolor=config.COLORS['bg_card'],
                       lightcolor=config.COLORS['primary'],
                       darkcolor=config.COLORS['primary'])
        
        style.configure('TButton', 
                       font=config.FONTS['body'],
                       padding=6)
    
    def _setup_ui(self):
        """Создание интерфейса"""
        # Основной контейнер
        self.main_container = tk.Frame(self.root, bg=config.COLORS['bg_dark'])
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=40, pady=20)
        
        # Верхняя панель
        self.top_bar = TopBar(self.main_container, self)
        self.top_bar.pack(fill=tk.X, pady=30)
        
        # Фрейм для выбора категории
        self._create_category_frame(self.main_container)
        
        # Контейнер для всех трех панелей
        self.content_frame = tk.Frame(self.main_container, bg=config.COLORS['bg_dark'])
        self.content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Панель статистики - слева
        self.stats_panel = StatsPanel(self.content_frame, self)
        self.stats_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=False)
        
        # Динамическая загрузка панели тренировки
        self.training_panel = None
        self.test_panel = None
        self.match_panel = None
        self.image_panel = None
        self.current_panel = None
        self.switch_training_panel(self.learning_method)
        
        # Панель управления - справа
        self.control_panel = ControlPanel(self.content_frame, self)
        self.control_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=False)
        
        # Нижняя панель
        self._create_bottom_bar(self.main_container)
    
    def _create_category_frame(self, parent):
        """Создает фрейм выбора категории"""
        category_frame = tk.Frame(parent, bg=config.COLORS['bg_dark'])
        category_frame.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(
            category_frame,
            text="📁 Категория:",
            font=('Segoe UI', 12),
            bg=config.COLORS['bg_dark'],
            fg=config.COLORS['text_secondary']
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        initial_category = "Все категории" if self.current_category is None else self.current_category
        self.category_var = tk.StringVar(value=initial_category)
        
        categories = self.model.get_all_categories()
        self.category_combo = ttk.Combobox(
            category_frame,
            textvariable=self.category_var,
            values=["Все категории"] + categories,
            font=('Segoe UI', 11),
            state='readonly',
            width=30
        )
        self.category_combo.pack(side=tk.LEFT)
        self.category_combo.bind('<<ComboboxSelected>>', self.on_category_change)
    
    def _create_bottom_bar(self, parent):
        """Создание нижней панели"""
        bottom_frame = tk.Frame(parent, bg=config.COLORS['bg_dark'])
        bottom_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=20)
        
        # Фрейм для прогресса дня
        progress_frame = tk.Frame(bottom_frame, bg=config.COLORS['bg_dark'])
        progress_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.progress_label = tk.Label(
            progress_frame,
            text="Прогресс дня: 0%",
            font=('Segoe UI', 9),
            bg=config.COLORS['bg_dark'],
            fg=config.COLORS['text_secondary']
        )
        self.progress_label.pack(side=tk.LEFT)
        
        self.daily_counter_label = tk.Label(
            progress_frame,
            text="• Сегодня: 0 слов",
            font=('Segoe UI', 9),
            bg=config.COLORS['bg_dark'],
            fg=config.COLORS['text_secondary']
        )
        self.daily_counter_label.pack(side=tk.LEFT, padx=10)
        
        speech_text = "🔊 Вкл" if self.settings['enabled'] else "🔇 Выкл"
        self.speech_status_label = tk.Label(
            progress_frame,
            text=speech_text,
            font=('Segoe UI', 9),
            bg=config.COLORS['bg_dark'],
            fg=config.COLORS['text_secondary']
        )
        self.speech_status_label.pack(side=tk.LEFT, padx=10)
        
        self.copyright_label = tk.Label(
            bottom_frame,
            text=f"© {config.TEXTS['year']} {config.TEXTS['app_name']} {config.TEXTS['version']}",
            font=('Segoe UI', 9),
            bg=config.COLORS['bg_dark'],
            fg=config.COLORS['text_secondary'],
            cursor='hand2'
        )
        self.copyright_label.pack(side=tk.RIGHT)
        self.copyright_label.bind('<Button-1>', lambda e: webbrowser.open('https://github.com'))
    
    def switch_training_panel(self, method):
        """Переключает панель тренировки в зависимости от метода"""
        if self.current_panel:
            self.current_panel.main_frame.destroy()
            self.current_panel = None
            self.training_panel = None
            self.test_panel = None
            self.match_panel = None
            self.image_panel = None
        
        if method == 'test':
            self.test_panel = TestPanel(self.content_frame, self)
            self.current_panel = self.test_panel
        elif method == 'match':
            self.match_panel = MatchPanel(self.content_frame, self)
            self.current_panel = self.match_panel
        elif method == 'image':
            self.image_panel = ImagePanel(self.content_frame, self)
            self.current_panel = self.image_panel
        else:
            self.training_panel = TrainingPanel(self.content_frame, self)
            self.current_panel = self.training_panel
        
        self.current_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=40)
    
    def show_welcome(self):
        """Показывает приветствие"""
        from utils.animations import animate_welcome
        if self.training_panel:
            animate_welcome(self.training_panel.word_label, self.training_panel.hint_label)
        self.root.after(1500, self.next_word)
    
    # Делегирование методов обработчикам
    def next_word(self):
        return self.navigation_handler.next_word()
    
    def on_category_change(self, event=None):
        self.navigation_handler.on_category_change(event)
    
    def set_mode(self, mode):
        self.navigation_handler.set_mode(mode)
    
    def check_answer(self):
        self.answer_handler.check_answer()
    
    def check_test_answer(self, selected_answer):
        self.answer_handler.check_test_answer(selected_answer)
    
    def check_image_answer(self):
        self.answer_handler.check_image_answer()
    
    def show_learning_method(self):
        self.learning_method_handler.show_learning_method()
    
    def set_learning_method(self, method, dialog):
        self.learning_method_handler.set_learning_method(method, dialog)
    
    def update_stats(self):
        """Обновляет статистики"""
        stats = self.model.get_stats()
        
        self.stats_panel.update_stats(stats)
        self.progress_label.config(text=f"Прогресс дня: {stats['progress']:.0f}%")
        self.daily_counter_label.config(text=f"• Сегодня: {stats['daily_words']} слов")
        
        speech_text = "🔊 Вкл" if self.settings['enabled'] else "🔇 Выкл"
        self.speech_status_label.config(text=speech_text)
        
        self.top_bar.update_stats(stats)
    
    def has_words_for_current_language(self):
        """Проверяет, есть ли слова для текущей пары языков"""
        words_for_pair = [
            w for w in self.model.vocabulary 
            if (w['language'] == self.language and w['native_language'] == self.native_language) or
               (w['language'] == self.native_language and w['native_language'] == self.language)
        ]
        return len(words_for_pair) > 0
    
    def generate_test_options(self, correct_word, correct_answer, study_lang, native_lang):
        """Генерирует варианты ответов для теста"""
        options = [correct_answer]
        
        other_words = []
        for word in self.model.vocabulary:
            if word != correct_word:
                if word['language'] == study_lang and word['native_language'] == native_lang:
                    if 'translations' in word and word['translations']:
                        other_words.append(word['translations'][0])
                    else:
                        other_words.append(word.get('translation', ''))
                elif word['language'] == native_lang and word['native_language'] == study_lang:
                    other_words.append(word['foreign'])
        
        other_words = list(set([w for w in other_words if w and w.lower() != correct_answer.lower()]))
        
        if len(other_words) >= 1:
            random.shuffle(other_words)
            num_options = min(2, len(other_words))
            options.extend(other_words[:num_options])
            random.shuffle(options)
            return options
        else:
            return [correct_answer]
    
    def add_word(self, foreign, translations, category="Основные", image=None):
        """
        Добавляет слово через контроллер с поддержкой множественных переводов
        
        Args:
            foreign: Иностранное слово
            translations: Список переводов (или строка для обратной совместимости)
            category: Категория
            image: Имя файла картинки
        """
        success = self.model.add_word(foreign, translations, self.language, self.native_language, category, image)
        if success:
            categories = self.model.get_all_categories()
            self.category_combo['values'] = ["Все категории"] + categories
        return success
    
    def apply_settings(self):
        """Применяет настройки после закрытия диалога"""
        if self.training_panel:
            self.training_panel.update_hint_display()
            self.training_panel.reset_incorrect()
        if self.image_panel:
            self.image_panel.update_hint_display()
            self.image_panel.reset_incorrect()
    
    def save_all_settings(self):
        """Сохраняет все настройки приложения"""
        settings_to_save = {
            'language': self.language,
            'native_language': self.native_language,
            'difficulty': self.difficulty,
            'current_category': self.current_category,
            'learning_method': self.learning_method,
            'app_settings': self.settings.copy()
        }
        settings_manager.save_settings(settings_to_save)
    
    def on_closing(self):
        """Обработчик закрытия окна"""
        self.model.save_stats()
        self.save_all_settings()
        
        for dialog in list(self.dialogs.values()):
            try:
                dialog.destroy()
            except:
                pass
        
        self.root.destroy()
    
    # Методы для диалогов
    def add_word_dialog(self):
        from .dialogs import DialogHandlers
        DialogHandlers.add_word_dialog(self)
    
    def show_vocabulary(self):
        from .vocabulary_dialog import VocabularyDialog
        VocabularyDialog.show_vocabulary(self)
    
    def show_hard_words(self):
        from .stats_dialog import StatsDialog
        StatsDialog.show_hard_words(self)
    
    def show_detailed_stats(self):
        from .stats_dialog import StatsDialog
        StatsDialog.show_detailed_stats(self)
    
    def refresh_words(self):
        from .dialogs import DialogHandlers
        DialogHandlers.refresh_words(self)
    
    def quick_training(self):
        from .dialogs import DialogHandlers
        DialogHandlers.quick_training(self)
    
    def show_settings_dialog(self):
        from .dialogs import DialogHandlers
        DialogHandlers.show_settings_dialog(self)
    
    def change_language_dialog(self):
        from .dialogs import DialogHandlers
        DialogHandlers.change_language_dialog(self)
        self.update_interface_colors()
    
    def set_difficulty(self, difficulty):
        from .dialogs import DialogHandlers
        DialogHandlers.set_difficulty(self, difficulty)
    
    def update_interface_colors(self):
        """Обновляет цвета интерфейса"""
        if hasattr(self, 'control_panel') and hasattr(self.control_panel, 'update_button_colors'):
            self.control_panel.update_button_colors()
    
    def _center_dialog(self, dialog):
        """Центрирует диалоговое окна"""
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        
        x = self.root.winfo_rootx() + (self.root.winfo_width() // 2) - (width // 2)
        y = self.root.winfo_rooty() + (self.root.winfo_height() // 2) - (height // 2)
        
        dialog.geometry(f'+{x}+{y}')
    
    def register_dialog(self, dialog_type, dialog):
        """Регистрирует открытый диалог"""
        self.dialogs[dialog_type] = dialog
    
    def unregister_dialog(self, dialog_type):
        """Удаляет диалог из регистрации"""
        if dialog_type in self.dialogs:
            del self.dialogs[dialog_type]
    
    def is_dialog_open(self, dialog_type):
        """Проверяет, открыт ли диалог данного типа"""
        return dialog_type in self.dialogs
    
    def close_dialog(self, dialog_type):
        """Закрывает диалог по типу"""
        if dialog_type in self.dialogs:
            try:
                self.dialogs[dialog_type].destroy()
                del self.dialogs[dialog_type]
            except:
                pass
