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
from .image_panel import ImagePanel  # НОВЫЙ ИМПОРТ
from .control_panel import ControlPanel
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
        self.learning_method = saved_settings.get('learning_method', 'manual')  # 'manual', 'test', 'match', 'image'
        
        # Объединяем все настройки
        self.settings = {}
        self.settings.update(config.TRAINING_SETTINGS.copy())
        self.settings.update(config.SPEECH_SETTINGS.copy())
        
        # Добавляем значения по умолчанию для подсказок, если их нет
        if 'show_hints' not in self.settings:
            self.settings['show_hints'] = False
        if 'hint_threshold' not in self.settings:
            self.settings['hint_threshold'] = 3
        
        # Перезаписываем сохраненными настройками, если они есть
        saved_app_settings = saved_settings.get('app_settings', {})
        for key, value in saved_app_settings.items():
            if key in self.settings:
                self.settings[key] = value
        
        # Флаг для защиты от DoS-атаки
        self.check_in_progress = False
        self.last_check_time = 0
        
        self.dialogs = {}  # Словарь для отслеживания открытых диалогов
        
        # Список недавно показанных слов для предотвращения повторений
        self.recent_words = []
        self.max_recent_words = 10
        
        # Проверяем доступность RHVoice
        if not speech_synth.is_available():
            self.settings['enabled'] = False
        else:
            # Применяем настройки громкости и скорости
            speech_synth.set_volume(self.settings['volume'])
            speech_synth.set_speed(self.settings['speed'])
            # Устанавливаем состояние enabled из настроек
            speech_synth.set_enabled(self.settings['enabled'])
        
        self._setup_styles()
        self._setup_ui()
        
        self.root.after(100, self.show_welcome)
        
        # После загрузки модели проверяем, есть ли слова
        if len(self.model.vocabulary) == 0:
            # Добавляем несколько начальных слов
            initial_words = [
                ("hello", "привет", "en", "ru"),
                ("world", "мир", "en", "ru"),
                ("cat", "кот", "en", "ru"),
                ("dog", "собака", "en", "ru"),
                ("book", "книга", "en", "ru"),
            ]
            
            for foreign, translation, lang, native in initial_words:
                self.model.add_word(foreign, translation, lang, native)
        
        # Привязываем обработчик закрытия
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
        category_frame = tk.Frame(self.main_container, bg=config.COLORS['bg_dark'])
        category_frame.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(
            category_frame,
            text="📁 Категория:",
            font=('Segoe UI', 12),
            bg=config.COLORS['bg_dark'],
            fg=config.COLORS['text_secondary']
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        # Устанавливаем значение комбобокса в зависимости от сохраненной категории
        initial_category = "Все категории" if self.current_category is None else self.current_category
        self.category_var = tk.StringVar(value=initial_category)
        
        # Получаем список категорий
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
        self.image_panel = None  # НОВОЕ
        self.current_panel = None
        self.switch_training_panel(self.learning_method)
        
        # Панель управления - справа
        self.control_panel = ControlPanel(self.content_frame, self)
        self.control_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=False)
        
        # Нижняя панель
        self._create_bottom_bar(self.main_container)
    
    def switch_training_panel(self, method):
        """Переключает панель тренировки в зависимости от метода"""
        # Удаляем текущую панель, если есть
        if self.current_panel:
            self.current_panel.main_frame.destroy()
            self.current_panel = None
            self.training_panel = None
            self.test_panel = None
            self.match_panel = None
            self.image_panel = None
        
        # Создаем новую панель
        if method == 'test':
            self.test_panel = TestPanel(self.content_frame, self)
            self.current_panel = self.test_panel
        elif method == 'match':
            self.match_panel = MatchPanel(self.content_frame, self)
            self.current_panel = self.match_panel
        elif method == 'image':  # НОВОЕ
            self.image_panel = ImagePanel(self.content_frame, self)
            self.current_panel = self.image_panel
        else:  # manual
            self.training_panel = TrainingPanel(self.content_frame, self)
            self.current_panel = self.training_panel
        
        # Упаковываем новую панель
        self.current_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=40)
    
    def on_category_change(self, event=None):
        """Обработчик изменения категории"""
        selected = self.category_var.get()
        if selected == "Все категории":
            self.current_category = None
        else:
            self.current_category = selected
        self.next_word()
    
    def _create_bottom_bar(self, parent):
        """Создание нижней панели"""
        bottom_frame = tk.Frame(parent, bg=config.COLORS['bg_dark'])
        bottom_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=20)
        
        # Фрейм для прогресса дня
        progress_frame = tk.Frame(bottom_frame, bg=config.COLORS['bg_dark'])
        progress_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Простой текст вместо прогресс-бара
        self.progress_label = tk.Label(
            progress_frame,
            text="Прогресс дня: 0%",
            font=('Segoe UI', 9),
            bg=config.COLORS['bg_dark'],
            fg=config.COLORS['text_secondary']
        )
        self.progress_label.pack(side=tk.LEFT)
        
        # Счетчик слов за день
        self.daily_counter_label = tk.Label(
            progress_frame,
            text="• Сегодня: 0 слов",
            font=('Segoe UI', 9),
            bg=config.COLORS['bg_dark'],
            fg=config.COLORS['text_secondary']
        )
        self.daily_counter_label.pack(side=tk.LEFT, padx=10)
        
        # Статус озвучки
        speech_text = "🔊 Вкл" if self.settings['enabled'] else "🔇 Выкл"
        self.speech_status_label = tk.Label(
            progress_frame,
            text=speech_text,
            font=('Segoe UI', 9),
            bg=config.COLORS['bg_dark'],
            fg=config.COLORS['text_secondary']
        )
        self.speech_status_label.pack(side=tk.LEFT, padx=10)
        
        # Авторские права
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
    
    def show_welcome(self):
        """Показывает приветствие"""
        from utils.animations import animate_welcome
        if self.training_panel:
            animate_welcome(self.training_panel.word_label, self.training_panel.hint_label)
        self.root.after(1500, self.next_word)
    
    def set_mode(self, mode):
        """
        Устанавливает режим тренировки
        
        Args:
            mode: Режим в формате 'en-ru' или 'ru-en'
        """
        self.mode = mode
        # Разбираем режим на языки
        if '-' in mode:
            parts = mode.split('-')
            if len(parts) == 2:
                self.language = parts[0]
                self.native_language = parts[1]
        
        # Обновляем иконку в текущей панели
        if self.training_panel:
            self.training_panel.update_mode_icon(self.language)
        if self.test_panel:
            self.test_panel.update_mode_icon(self.language)
        if self.match_panel:
            self.match_panel.update_mode_icon(self.language)
        if self.image_panel:  # НОВОЕ
            self.image_panel.update_mode_icon(self.language)
        
        # Обновляем кнопки режима в top_bar
        self.top_bar.update_mode_buttons(mode)
        
        # Сбрасываем текущее слово и историю
        self.model.current_word = None
        self.recent_words = []
        
        # Проверяем наличие слов для новой пары языков
        self._check_vocabulary_for_current_language()
        
        # Выбираем новое слово
        self.next_word()
    
    def _check_vocabulary_for_current_language(self):
        """Проверяет, есть ли слова для текущей пары языков (в любом направлении)"""
        # Ищем слова в обоих направлениях
        words_for_pair = [
            w for w in self.model.vocabulary 
            if (w['language'] == self.language and w['native_language'] == self.native_language) or
               (w['language'] == self.native_language and w['native_language'] == self.language)
        ]
        
        if not words_for_pair:
            # Нет слов для этой пары языков
            message = f"Добавьте слова для языков {config.LANGUAGES[self.language]['name']} ↔ {config.LANGUAGES[self.native_language]['name']}"
            
            if self.training_panel:
                self.training_panel.word_label.config(
                    text="Нет слов для изучения",
                    font=('Segoe UI', 24, 'bold')
                )
                self.training_panel.hint_label.config(text=message)
                self.training_panel.answer_entry.delete(0, tk.END)
                self.training_panel.answer_entry.config(state='disabled')
                self.training_panel.check_button.config(state='disabled')
                self.training_panel.speaker_button.config(state='disabled')
            
            if self.test_panel:
                self.test_panel.show_no_words_message()
            
            if self.match_panel:
                self.match_panel.show_no_words_message()
            
            if self.image_panel:  # НОВОЕ
                self.image_panel.show_no_words_message()
            
            show_notification(
                self.root,
                "Словарь пуст!",
                f"Нет слов для пары {config.LANGUAGES[self.language]['flag']} ↔ {config.LANGUAGES[self.native_language]['flag']}",
                "warning"
            )
            return False
        
        # Если слова есть, активируем соответствующую панель
        if self.training_panel:
            self.training_panel.answer_entry.config(state='normal')
            self.training_panel.check_button.config(state='normal')
            if self.settings['enabled']:
                self.training_panel.speaker_button.config(state='normal')
        
        return True
    
    def has_words_for_current_language(self):
        """
        Проверяет, есть ли слова для текущей пары языков
        
        Returns:
            bool: True если есть слова
        """
        words_for_pair = [
            w for w in self.model.vocabulary 
            if (w['language'] == self.language and w['native_language'] == self.native_language) or
               (w['language'] == self.native_language and w['native_language'] == self.language)
        ]
        return len(words_for_pair) > 0
    
    def generate_match_words(self):
        """Генерирует 3 слова для режима соотношения"""
        study_lang = self.language
        native_lang = self.native_language
        
        # Ищем все слова для пары языков
        all_words = [
            w for w in self.model.vocabulary 
            if (w['language'] == study_lang and w['native_language'] == native_lang) or
               (w['language'] == native_lang and w['native_language'] == study_lang)
        ]
        
        # Фильтруем по категории, если выбрана
        if self.current_category:
            all_words = [w for w in all_words if w.get('category', "Основные") == self.current_category]
        
        # Если меньше 3 слов, возвращаем None
        if len(all_words) < 3:
            return None
        
        # Выбираем 3 случайных слова
        selected_words = random.sample(all_words, 3)
        return selected_words
    
    def next_word(self):
        """Выбирает следующее слово"""
        # Сначала проверяем, есть ли слова для текущей пары языков
        if not self._check_vocabulary_for_current_language():
            return False
    
        # Получаем языки из режима
        study_lang = self.language
        native_lang = self.native_language
    
        if self.learning_method == 'match':
            # Для режима соотношения нужны 3 слова
            match_words = self.generate_match_words()
            if match_words and self.match_panel:
                self.match_panel.set_question(match_words)
                return True
            else:
                # Недостаточно слов
                if self.match_panel:
                    self.match_panel.show_no_words_message()
                show_notification(
                    self.root,
                    "Недостаточно слов",
                    "Для режима соотношения нужно минимум 3 слова в выбранной категории",
                    "warning"
                )
                return False
    
        elif self.learning_method == 'image' and self.image_panel:
            # Для режима картинок - выбираем слова, у которых есть картинки
            all_words_with_images = [
                w for w in self.model.vocabulary 
                if (w['language'] == study_lang and w['native_language'] == native_lang) or
                   (w['language'] == native_lang and w['native_language'] == study_lang)
            ]
        
            # Фильтруем только те, у которых есть картинка
            words_with_images = [w for w in all_words_with_images if w.get('image')]
        
            # Фильтруем по категории, если выбрана
            if self.current_category:
                words_with_images = [w for w in words_with_images if w.get('category', "Основные") == self.current_category]
        
            if not words_with_images:
                # Нет слов с картинками
                self.image_panel.show_no_image_message()
                show_notification(
                    self.root,
                    "Нет картинок",
                    "В этой категории нет слов с картинками",
                    "info"
                )
                return False
        
            # Удаляем текущее слово из списка, если оно там есть (чтобы не повторяться)
            if self.model.current_word and self.model.current_word in words_with_images and len(words_with_images) > 1:
                words_with_images.remove(self.model.current_word)
        
            # Выбираем случайное слово из доступных
            try:
                word = random.choice(words_with_images)
            except (IndexError, ValueError):
                return False
        
            if word:
                self.model.current_word = word
                self.image_panel.set_image_word(word)
                return True
            return False
    
        else:
            # Для остальных режимов - одно слово
            # Ищем ВСЕ слова для пары языков в любом направлении с учетом категории
            all_words = [
                w for w in self.model.vocabulary 
                if (w['language'] == study_lang and w['native_language'] == native_lang) or
                   (w['language'] == native_lang and w['native_language'] == study_lang)
            ]
        
            # Фильтруем по категории, если выбрана
            if self.current_category:
                all_words = [w for w in all_words if w.get('category', "Основные") == self.current_category]
        
            if not all_words:
                # Нет слов в выбранной категории
                if self.current_category:
                    message = f"Нет слов в категории '{self.current_category}'"
                else:
                    message = "Нет слов для изучения"
            
                if self.training_panel:
                    self.training_panel.word_label.config(text=message, font=('Segoe UI', 24, 'bold'))
                if self.test_panel:
                    self.test_panel.show_message(message)
                return False
        
            # Улучшенная логика предотвращения повторений
            if len(all_words) > 1 and self.settings['prevent_repeats']:
                # Фильтруем слова, исключая недавно показанные
                available_words = [w for w in all_words if w not in self.recent_words]
            
                # Если после фильтрации остались слова, используем их
                if available_words:
                    all_words = available_words
                else:
                    # Если все слова были в recent, очищаем recent и используем все слова
                    self.recent_words = []
        
            # Выбираем случайное слово из доступных
            try:
                word = random.choice(all_words)
            except (IndexError, ValueError):
                return False
        
            if word:
                # Сохраняем текущее слово в модели
                self.model.current_word = word
            
                # Добавляем слово в список недавних
                self.recent_words.append(word)
                if len(self.recent_words) > self.max_recent_words:
                    self.recent_words.pop(0)
            
                # Определяем, какое слово показывать в зависимости от метода обучения
                if self.learning_method == 'test' and self.test_panel:
                    # Для теста - показываем вопрос и генерируем варианты
                    if word['language'] == study_lang and word['native_language'] == native_lang:
                        display_word = word['foreign']
                        correct_answer = word['translation']
                    else:
                        display_word = word['translation']
                        correct_answer = word['foreign']
                
                    options = self.generate_test_options(word, correct_answer, study_lang, native_lang)
                    self.test_panel.set_question(display_word, options, correct_answer, word)
            
                elif self.training_panel:
                    # Для ручного ввода
                    if word['language'] == study_lang and word['native_language'] == native_lang:
                        display_word = word['foreign']
                    else:
                        display_word = word['translation']
                    
                    hint_text = "Введите перевод:" if self.settings['show_hints'] else ""
                    self.training_panel.set_word(display_word, hint_text, word)
                    self.training_panel.focus_entry()
            
                return True
            return False
    
    def generate_test_options(self, correct_word, correct_answer, study_lang, native_lang):
        """Генерирует варианты ответов для теста"""
        options = [correct_answer]
        
        # Получаем другие слова для вариантов
        other_words = []
        for word in self.model.vocabulary:
            if word != correct_word:
                if word['language'] == study_lang and word['native_language'] == native_lang:
                    other_words.append(word['translation'])
                elif word['language'] == native_lang and word['native_language'] == study_lang:
                    other_words.append(word['foreign'])
        
        # Удаляем дубликаты и вариант, совпадающий с правильным ответом
        other_words = list(set([w for w in other_words if w.lower() != correct_answer.lower()]))
        
        # Если есть хотя бы одно другое слово
        if len(other_words) >= 1:
            # Выбираем случайные варианты (до 2 штук)
            random.shuffle(other_words)
            num_options = min(2, len(other_words))
            options.extend(other_words[:num_options])
            random.shuffle(options)
            return options
        else:
            # Если других слов нет, возвращаем только правильный ответ
            return [correct_answer]
    
    def check_answer(self):
        """Проверяет ответ пользователя в режиме ручного ввода"""
        import time
        
        # Защита от DoS-атаки: не проверяем чаще чем раз в 500 мс
        current_time = time.time() * 1000
        if self.check_in_progress or (current_time - self.last_check_time < 500):
            return
        
        # Проверяем, есть ли слова для текущей пары языков
        if not self.has_words_for_current_language():
            show_notification(
                self.root,
                "Нет слов для изучения",
                f"Добавьте слова для пары {config.LANGUAGES[self.language]['flag']} ↔ {config.LANGUAGES[self.native_language]['flag']}",
                "warning"
            )
            return
        
        # Проверяем, есть ли текущее слово
        if self.model.current_word is None:
            show_notification(
                self.root,
                "Нет слова для проверки",
                "Выберите слово или добавьте новые",
                "warning"
            )
            return
        
        # Устанавливаем флаг проверки
        self.check_in_progress = True
        self.last_check_time = current_time
        
        try:
            user_answer = self.training_panel.get_user_answer()
            
            if not user_answer:
                show_notification(
                    self.root,
                    "Пустой ответ",
                    "Введите перевод слова",
                    "warning"
                )
                return
            
            # Получаем языки из режима
            study_lang = self.language
            native_lang = self.native_language
            
            current_word = self.model.current_word
            
            # Определяем правильный ответ
            if current_word['language'] == study_lang and current_word['native_language'] == native_lang:
                # Прямое направление - правильный ответ перевод
                correct_answer = current_word['translation'].lower()
            else:
                # Обратное направление - правильный ответ иностранное слово
                correct_answer = current_word['foreign'].lower()
            
            user_answer_lower = user_answer.lower()
            
            # Проверяем правильность
            is_correct = user_answer_lower == correct_answer
            
            if is_correct:
                self.training_panel.show_success_animation()
                show_notification(
                    self.root,
                    "Правильно! 🎉",
                    f"Правильный ответ: {correct_answer}",
                    "success"
                )
                if self.settings['auto_advance']:
                    self.root.after(800, self._safe_next_word)
            else:
                self.training_panel.show_error_animation()
                show_notification(
                    self.root,
                    f"Неправильно 😕",
                    f"Правильно: {correct_answer}",
                    "error"
                )
            
            # Обновляем статистику
            self.model.check_answer(user_answer, self.mode)
            self.update_stats()
            
        finally:
            self.root.after(500, lambda: setattr(self, 'check_in_progress', False))
    
    def check_test_answer(self, selected_answer):
        """Проверяет ответ в тестовом режиме"""
        if not self.model.current_word:
            return
        
        study_lang = self.language
        native_lang = self.native_language
        current_word = self.model.current_word
        
        # Определяем правильный ответ
        if current_word['language'] == study_lang and current_word['native_language'] == native_lang:
            correct_answer = current_word['translation']
        else:
            correct_answer = current_word['foreign']
        
        is_correct = (selected_answer == correct_answer)
        
        if is_correct:
            self.test_panel.show_result(True, correct_answer)
            show_notification(self.root, "✅ Правильно!", "Отличная работа!", "success")
            if self.settings['auto_advance']:
                self.root.after(800, self._safe_next_word)
        else:
            self.test_panel.show_result(False, correct_answer)
            show_notification(self.root, "❌ Ошибка", f"Правильно: {correct_answer}", "error")
        
        # Обновляем статистику
        self.model.check_answer(selected_answer if is_correct else "", self.mode)
        self.update_stats()
    
    def check_image_answer(self):
        """Проверяет ответ пользователя в режиме картинок"""
        import time
    
        current_time = time.time() * 1000
        if self.check_in_progress or (current_time - self.last_check_time < 500):
            return
    
        if not self.has_words_for_current_language():
            show_notification(
                self.root,
                "Нет слов для изучения",
                f"Добавьте слова для пары {config.LANGUAGES[self.language]['flag']} ↔ {config.LANGUAGES[self.native_language]['flag']}",
                "warning"
            )
            return
    
        if self.model.current_word is None:
            show_notification(
                self.root,
                "Нет слова для проверки",
                "Выберите слово или добавьте новые",
                "warning"
            )
            return
    
        self.check_in_progress = True
        self.last_check_time = current_time
        
        try:
            user_answer = self.image_panel.get_user_answer()
        
            if not user_answer:
                show_notification(
                    self.root,
                    "Пустой ответ",
                    "Введите перевод слова",
                    "warning"
                )
                return
        
            current_word = self.model.current_word
            
            if current_word['language'] == self.language:
                correct_answer = current_word['foreign']
            else:
                correct_answer = current_word['translation']
        
            user_answer_lower = user_answer.lower()
            correct_lower = correct_answer.lower()
        
            is_correct = user_answer_lower == correct_lower
        
            if is_correct:
                self.image_panel.show_success_animation()
                show_notification(
                    self.root,
                    "Правильно! 🎉",
                    f"Правильный ответ: {correct_answer}",
                    "success"
                )
                if self.settings['auto_advance']:
                    self.root.after(800, self._safe_next_word)
            else:
                self.image_panel.show_error_animation()
                show_notification(
                    self.root,
                    f"Неправильно 😕",
                    f"Правильно: {correct_answer}",
                    "error"
                )
        
            self.model.check_answer(user_answer, self.mode)
            self.update_stats()
        
        finally:
            self.root.after(500, lambda: setattr(self, 'check_in_progress', False))
    
    def _safe_next_word(self):
        """Безопасный вызов next_word"""
        try:
            success = self.next_word()
            if not success:
                show_notification(
                    self.root,
                    "Словарь пуст",
                    "Добавьте новые слова для продолжения",
                    "info"
                )
        except Exception as e:
            pass
    
    def update_stats(self):
        """Обновляет статистики"""
        stats = self.model.get_stats()
        
        # Обновляем панель статистики
        self.stats_panel.update_stats(stats)
        
        # Обновляем нижнюю панель
        self.progress_label.config(text=f"Прогресс дня: {stats['progress']:.0f}%")
        self.daily_counter_label.config(text=f"• Сегодня: {stats['daily_words']} слов")
        
        # Обновляем статус озвучки
        speech_text = "🔊 Вкл" if self.settings['enabled'] else "🔇 Выкл"
        self.speech_status_label.config(text=speech_text)
        
        # Обновляем верхнюю панель
        self.top_bar.update_stats(stats)
    
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
    
    def add_word(self, foreign, translation, category="Основные", image=None):
        """Добавляет слово через контроллер с указанием категории и картинки"""
        from .dialog_handlers import DialogHandlers
        success = self.model.add_word(foreign, translation, self.language, self.native_language, category, image)
        if success:
            categories = self.model.get_all_categories()
            self.category_combo['values'] = ["Все категории"] + categories
        return success
    
    def show_learning_method(self):
        """Показывает диалог выбора метода обучения"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Задания для тренировки слов")
        dialog.geometry("750x350")  # Увеличено для 4 кнопок
        dialog.configure(bg=config.COLORS['bg_dark'])
        dialog.transient(self.root)
        dialog.grab_set()
        
        self._center_dialog(dialog)
        
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
        manual_btn = tk.Button(
            dialog,
            text="✍️ Перевод слова",
            font=('Segoe UI', 12, 'bold'),
            bg=config.COLORS['primary'],
            fg=config.COLORS['text'],
            bd=0,
            padx=30,
            pady=10,
            cursor='hand2',
            command=lambda: self.set_learning_method('manual', dialog)
        )
        manual_btn.pack(pady=5, padx=40, fill=tk.X)
        
        # Эффект при наведении
        manual_btn.bind('<Enter>', lambda e: manual_btn.config(bg='#2563eb'))
        manual_btn.bind('<Leave>', lambda e: manual_btn.config(bg=config.COLORS['primary']))
        
        # Кнопка "Тест"
        test_btn = tk.Button(
            dialog,
            text="📝 Тест (выбор варианта)",
            font=('Segoe UI', 12, 'bold'),
            bg=config.COLORS['secondary'],
            fg=config.COLORS['text'],
            bd=0,
            padx=30,
            pady=10,
            cursor='hand2',
            command=lambda: self.set_learning_method('test', dialog)
        )
        test_btn.pack(pady=5, padx=40, fill=tk.X)
        
        # Эффект при наведении
        test_btn.bind('<Enter>', lambda e: test_btn.config(bg='#059669'))
        test_btn.bind('<Leave>', lambda e: test_btn.config(bg=config.COLORS['secondary']))
        
        # Кнопка "Соотношение"
        match_btn = tk.Button(
            dialog,
            text="🔄 Сопоставление слов",
            font=('Segoe UI', 12, 'bold'),
            bg=config.COLORS['accent'],
            fg=config.COLORS['text'],
            bd=0,
            padx=30,
            pady=10,
            cursor='hand2',
            command=lambda: self.set_learning_method('match', dialog)
        )
        match_btn.pack(pady=5, padx=40, fill=tk.X)
        
        # Эффект при наведении
        match_btn.bind('<Enter>', lambda e: match_btn.config(bg='#7c3aed'))
        match_btn.bind('<Leave>', lambda e: match_btn.config(bg=config.COLORS['accent']))
        
        # ===== НОВАЯ КНОПКА: Перевод картинки =====
        image_btn = tk.Button(
            dialog,
            text="🖼️ Назови изображенное слово",
            font=('Segoe UI', 12, 'bold'),
            bg=config.COLORS['warning'],
            fg=config.COLORS['text'],
            bd=0,
            padx=30,
            pady=10,
            cursor='hand2',
            command=lambda: self.set_learning_method('image', dialog)
        )
        image_btn.pack(pady=5, padx=40, fill=tk.X)
        
        # Эффект при наведении
        image_btn.bind('<Enter>', lambda e: image_btn.config(bg='#f97316'))
        image_btn.bind('<Leave>', lambda e: image_btn.config(bg=config.COLORS['warning']))
        # ===== КОНЕЦ НОВОЙ КНОПКИ =====
    
    def set_learning_method(self, method, dialog):
        """Устанавливает метод обучения"""
        self.learning_method = method
        self.switch_training_panel(method)
        dialog.destroy()
        self.next_word()
        
        method_names = {
            'manual': 'ручной перевод',
            'test': 'тест',
            'match': 'соотношение',
            'image': 'перевод картинки'  # НОВОЕ
        }
        
        show_notification(
            self.root,
            "Метод изменен",
            f"Выбран метод: {method_names.get(method, method)}",
            "success"
        )
    
    def apply_settings(self):
        """Применяет настройки после закрытия диалога"""
        # Обновляем состояние подсказок в панели тренировки
        if self.training_panel:
            self.training_panel.update_hint_display()
            self.training_panel.reset_incorrect()
        if self.image_panel:  # НОВОЕ
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
        # Сохраняем статистику перед выходом
        self.model.save_stats()
        
        # Сохраняем все настройки
        self.save_all_settings()
        
        # Закрываем все диалоги
        for dialog in list(self.dialogs.values()):
            try:
                dialog.destroy()
            except:
                pass
        
        self.root.destroy()
    
    # Делегируем методы диалогов
    def add_word_dialog(self):
        from .dialog_handlers import DialogHandlers
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
        from .dialog_handlers import DialogHandlers
        DialogHandlers.refresh_words(self)
    
    def quick_training(self):
        from .dialog_handlers import DialogHandlers
        DialogHandlers.quick_training(self)
    
    def show_settings_dialog(self):
        from .dialog_handlers import DialogHandlers
        DialogHandlers.show_settings_dialog(self)
    
    def change_language_dialog(self):
        from .dialog_handlers import DialogHandlers
        DialogHandlers.change_language_dialog(self)
    
    def set_difficulty(self, difficulty):
        from .dialog_handlers import DialogHandlers
        DialogHandlers.set_difficulty(self, difficulty)
