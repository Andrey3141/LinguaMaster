"""
Панель тестового режима с выбором вариантов
"""

import tkinter as tk
from config import config
from utils.animations import animate_success, animate_error
from utils.speech import speech_synth

class TestPanel:
    """Класс панели тестового режима"""
    
    def __init__(self, parent, controller):
        """
        Инициализация панели тестового режима
        
        Args:
            parent: Родительский виджет
            controller: Контроллер (MainWindow)
        """
        self.parent = parent
        self.controller = controller
        self.current_word_obj = None
        self.correct_answer = ""
        self.options = []
        self.option_buttons = []
        self.current_display_word = ""
        
        self.create_widgets()
    
    def create_widgets(self):
        """Создание виджетов панели"""
        # Основной фрейм
        self.main_frame = tk.Frame(
            self.parent, 
            bg=config.COLORS['bg_card'],
            padx=30,
            pady=30
        )
        
        # Верхняя часть - иконка режима
        self.mode_frame = tk.Frame(self.main_frame, bg=config.COLORS['bg_card'])
        self.mode_frame.pack(fill=tk.X, pady=20)
        
        # Иконка языка
        study_flag = config.LANGUAGES[self.controller.language]['flag']
        native_flag = config.LANGUAGES[self.controller.native_language]['flag']
        self.mode_label = tk.Label(
            self.mode_frame,
            text=f"{study_flag} → {native_flag}",
            font=('Segoe UI', 24),
            bg=config.COLORS['bg_card'],
            fg=config.COLORS['text']
        )
        self.mode_label.pack()
        
        # Карточка слова
        self.word_card = tk.Frame(
            self.main_frame,
            bg=config.COLORS['bg_dark'],
            padx=40,
            pady=40
        )
        self.word_card.pack(fill=tk.BOTH, expand=True, pady=20)
        
        # Фрейм для слова и кнопки динамика
        self.word_frame = tk.Frame(self.word_card, bg=config.COLORS['bg_dark'])
        self.word_frame.pack(expand=True)
        
        # Слово для перевода
        self.word_label = tk.Label(
            self.word_frame,
            text="",
            font=config.FONTS['word_display'],
            bg=config.COLORS['bg_dark'],
            fg=config.COLORS['text'],
            wraplength=500,
            justify='center'
        )
        self.word_label.pack(side=tk.LEFT, padx=(0, 10))
        
        # ===== НОВОЕ: Кнопка динамика для озвучки в тестовом режиме =====
        self.speaker_button = tk.Button(
            self.word_frame,
            text="🔊",
            font=config.FONTS['speaker_icon'],
            bg=config.COLORS['speaker'],
            fg=config.COLORS['text'],
            bd=0,
            padx=10,
            pady=5,
            cursor='hand2',
            command=self.speak_current_word,
            state='normal' if speech_synth.enabled else 'disabled'
        )
        self.speaker_button.pack(side=tk.LEFT)
        
        # Эффект при наведении
        self.speaker_button.bind('<Enter>', self._on_speaker_hover)
        self.speaker_button.bind('<Leave>', self._on_speaker_leave)
        self.speaker_normal_bg = config.COLORS['speaker']
        # ===== КОНЕЦ НОВОГО КОДА =====
        
        # Подсказка
        self.hint_label = tk.Label(
            self.word_card,
            text="Выберите правильный перевод:",
            font=config.FONTS['body_small'],
            bg=config.COLORS['bg_dark'],
            fg=config.COLORS['text_secondary'],
            pady=20
        )
        self.hint_label.pack()
        
        # Фрейм для кнопок с вариантами
        self.options_frame = tk.Frame(self.main_frame, bg=config.COLORS['bg_card'])
        self.options_frame.pack(fill=tk.BOTH, expand=True, pady=20)
        
        # Создаем 3 кнопки для вариантов (максимум)
        for i in range(3):
            btn = tk.Button(
                self.options_frame,
                text="",
                font=('Segoe UI', 14),
                bg=config.COLORS['bg_dark'],
                fg=config.COLORS['text'],
                bd=0,
                padx=20,
                pady=15,
                cursor='hand2',
                command=lambda idx=i: self.check_answer(idx)
            )
            btn.pack(fill=tk.X, pady=5)
            
            # Эффект при наведении
            btn.bind('<Enter>', lambda e, b=btn: b.config(bg=config.COLORS['primary']))
            btn.bind('<Leave>', lambda e, b=btn: b.config(bg=config.COLORS['bg_dark']))
            
            self.option_buttons.append(btn)
    
    def _on_speaker_hover(self, event):
        """Эффект при наведении на кнопку динамика"""
        if self.speaker_button['state'] == 'normal':
            self.speaker_button.config(bg=config.COLORS['speaker_hover'])
    
    def _on_speaker_leave(self, event):
        """Эффект при уходе с кнопки динамика"""
        if self.speaker_button['state'] == 'normal':
            self.speaker_button.config(bg=self.speaker_normal_bg)
        else:
            self.speaker_button.config(bg=config.COLORS['speaker_disabled'])
    
    def set_question(self, word, options, correct_answer, word_obj):
        """Устанавливает вопрос и варианты ответов"""
        self.current_display_word = word
        self.word_label.config(text=word)
        self.correct_answer = correct_answer
        self.current_word_obj = word_obj
        self.options = options
        
        # Сначала скрываем все кнопки
        for btn in self.option_buttons:
            btn.pack_forget()
        
        # Показываем нужное количество кнопок
        for i in range(len(options)):
            btn = self.option_buttons[i]
            btn.config(
                text=options[i],
                state='normal',
                bg=config.COLORS['bg_dark']
            )
            btn.pack(fill=tk.X, pady=5)
        
        # Обновляем подсказку
        if len(options) == 1:
            self.hint_label.config(text="Нажмите кнопку для продолжения:")
        else:
            self.hint_label.config(text="Выберите правильный перевод:")
        
        # ===== НОВОЕ: Автоматическая озвучка, если включена =====
        if (word and "Нет слов" not in word and 
            word_obj and 
            speech_synth.enabled and 
            self.controller.settings.get('auto_speak', False)):
            # Небольшая задержка, чтобы интерфейс обновился
            self.controller.root.after(100, self.speak_current_word)
        # ===== КОНЕЦ НОВОГО КОДА =====
    
    def check_answer(self, option_index):
        """Проверяет выбранный вариант"""
        if option_index >= len(self.options):
            return
        
        selected = self.options[option_index]
        
        # Блокируем все кнопки
        for btn in self.option_buttons:
            btn.config(state='disabled')
        self.speaker_button.config(state='disabled')
        
        # Проверяем ответ через контроллер
        self.controller.check_test_answer(selected)
    
    def show_result(self, is_correct, correct_answer):
        """Показывает результат ответа"""
        if is_correct:
            animate_success(self.word_card)
            # Подсвечиваем правильный ответ зеленым
            for btn in self.option_buttons:
                if btn['text'] == correct_answer:
                    btn.config(bg=config.COLORS['success'])
        else:
            animate_error(self.word_card)
            # Подсвечиваем правильный ответ зеленым, а неправильные красным
            for btn in self.option_buttons:
                if btn['text'] == correct_answer:
                    btn.config(bg=config.COLORS['success'])
                elif btn['text'] in self.options and btn['state'] != 'disabled':
                    btn.config(bg=config.COLORS['danger'])
    
    def show_message(self, message):
        """Показывает сообщение (например, нет слов)"""
        self.word_label.config(text=message, font=('Segoe UI', 24, 'bold'))
        self.hint_label.config(text="")
        for btn in self.option_buttons:
            btn.pack_forget()
        self.speaker_button.config(state='disabled')
    
    def show_no_words_message(self):
        """Показывает сообщение об отсутствии слов"""
        self.show_message("Нет слов для изучения")
    
    def update_mode_icon(self, lang_code):
        """Обновляет иконку режима"""
        study_flag = config.LANGUAGES[self.controller.language]['flag']
        native_flag = config.LANGUAGES[self.controller.native_language]['flag']
        self.mode_label.config(text=f"{study_flag} → {native_flag}")
    
    # ===== НОВЫЙ МЕТОД: Озвучка текущего слова =====
    def speak_current_word(self):
        """Озвучивает текущее слово"""
        if not speech_synth.enabled:
            return
        
        if not self.current_display_word or not self.current_word_obj:
            return
        
        # Определяем язык отображаемого слова
        if self.current_display_word == self.current_word_obj['foreign']:
            lang = self.current_word_obj['language']
        else:
            lang = self.current_word_obj['native_language']
        
        # Временно делаем кнопку неактивной во время озвучки
        self.speaker_button.config(state='disabled', bg=config.COLORS['speaker_disabled'])
        
        def on_speech_complete(success):
            # Возвращаем кнопке нормальное состояние после озвучки
            if (self.current_display_word and 
                "Нет слов" not in self.current_display_word and 
                self.current_word_obj and 
                speech_synth.enabled):
                self.speaker_button.config(state='normal', bg=self.speaker_normal_bg)
            else:
                # Если условия не выполняются, оставляем disabled
                self.speaker_button.config(state='disabled', bg=config.COLORS['speaker_disabled'])
        
        speech_synth.speak_async(self.current_display_word, lang, callback=on_speech_complete)
    # ===== КОНЕЦ НОВОГО МЕТОДА =====
    
    def pack(self, **kwargs):
        """Упаковка панели"""
        self.main_frame.pack(**kwargs)
