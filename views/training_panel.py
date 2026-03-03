"""
Панель тренировки
"""

import tkinter as tk
from config import config
from utils.animations import animate_success, animate_error
from utils.speech import speech_synth

class TrainingPanel:
    """Класс панели тренировки"""
    
    def __init__(self, parent, controller):
        """
        Инициализация панели тренировки
        
        Args:
            parent: Родительский виджет
            controller: Контроллер (MainWindow)
        """
        self.parent = parent
        self.controller = controller
        self.current_display_word = ""
        self.current_word_obj = None
        self.speaker_normal_bg = config.COLORS['speaker']
        self.incorrect_attempts = 0
        self.hint_active = False
        self.original_entry_bg = None
        self.original_entry_fg = None
        self.hint_text = ""
        self.user_typing = False
        
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
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
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
        
        # Кнопка динамика для озвучки
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
        
        # Подсказка
        self.hint_label = tk.Label(
            self.word_card,
            text="Введите перевод:",
            font=config.FONTS['body_small'],
            bg=config.COLORS['bg_dark'],
            fg=config.COLORS['text_secondary'],
            pady=20
        )
        self.hint_label.pack()
        
        # Поле ввода
        self.answer_entry = tk.Entry(
            self.word_card,
            font=config.FONTS['input'],
            bg=config.COLORS['bg_card'],
            fg=config.COLORS['text'],
            insertbackground=config.COLORS['text'],
            bd=0,
            justify='center'
        )
        self.answer_entry.pack(fill=tk.X, pady=20, ipady=10)
        
        # Сохраняем оригинальные цвета для восстановления
        self.original_entry_bg = config.COLORS['bg_card']
        self.original_entry_fg = config.COLORS['text']
        
        # Привязываем события для поля ввода
        self.answer_entry.bind('<FocusIn>', self._on_entry_focus_in)
        self.answer_entry.bind('<FocusOut>', self._on_entry_focus_out)
        self.answer_entry.bind('<KeyPress>', self._on_key_press)
        self.answer_entry.bind('<KeyRelease>', self._on_key_release)
        
        # Подчеркивание поля ввода
        self.entry_underline = tk.Frame(
            self.word_card,
            height=2,
            bg=config.COLORS['border']
        )
        self.entry_underline.pack(fill=tk.X)
        
        # Кнопка проверки
        self.check_button = tk.Button(
            self.main_frame,
            text="✅ Проверить",
            font=('Segoe UI', 14, 'bold'),
            bg=config.COLORS['primary'],
            fg=config.COLORS['text'],
            bd=0,
            padx=40,
            pady=15,
            cursor='hand2',
            command=self.controller.check_answer
        )
        self.check_button.pack(pady=20)
        
        self.answer_entry.unbind('<Return>')
    
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
    
    def _on_entry_focus_in(self, event):
        """При получении фокуса полем ввода"""
        pass
    
    def _on_entry_focus_out(self, event):
        """При потере фокуса полем ввода"""
        pass
    
    def _on_key_press(self, event):
        """При нажатии клавиши в поле ввода"""
        if self.hint_active:
            self.user_typing = True
            self.clear_hint()
    
    def _on_key_release(self, event):
        """При отпускании клавиши в поле ввода"""
        if not self.answer_entry.get():
            self.user_typing = False
            if self.hint_text and self.incorrect_attempts >= self.controller.settings.get('hint_threshold', 3):
                self.restore_hint()
    
    def set_word(self, word, hint, word_obj=None):
        """
        Устанавливает слово для тренировки
        
        Args:
            word: Слово для перевода
            hint: Подсказка
            word_obj: Объект слова из модели
        """
        self.current_display_word = word
        self.current_word_obj = word_obj
        self.word_label.config(text=word)
        self.incorrect_attempts = 0
        self.hint_active = False
        self.hint_text = ""
        self.user_typing = False
        
        # Очищаем поле ввода и восстанавливаем цвета
        self.answer_entry.delete(0, tk.END)
        self.answer_entry.config(
            bg=self.original_entry_bg,
            fg=self.original_entry_fg
        )
        
        # Обновляем подсказку
        self.update_hint_display()
        
        # Обновляем состояние кнопки динамика
        self.update_speaker_button_state()
        
        # Включаем Enter
        if word and "Нет слов" not in word:
            self.answer_entry.bind('<Return>', lambda e: self.controller.check_answer())
        else:
            self.answer_entry.unbind('<Return>')
        
        # Автоматическая озвучка, если включена
        if (word and "Нет слов" not in word and 
            word_obj and 
            speech_synth.enabled and 
            self.controller.settings.get('auto_speak', False)):
            self.controller.root.after(100, self.speak_current_word)
    
    def update_hint_display(self):
        """Обновляет отображение подсказки"""
        if self.controller.settings.get('show_hints', False):
            threshold = self.controller.settings.get('hint_threshold', 3)
            remaining = max(0, threshold - self.incorrect_attempts)
            
            if remaining > 0:
                self.hint_label.config(
                    text=f"Подсказка через {remaining} ошибок",
                    fg=config.COLORS['text_secondary']
                )
            else:
                if self.hint_active:
                    self.hint_label.config(
                        text="Подсказка активирована",
                        fg=config.COLORS['warning']
                    )
                else:
                    self.hint_label.config(
                        text="Подсказка готова",
                        fg=config.COLORS['warning']
                    )
        else:
            # Возвращаем стандартную подсказку
            self.hint_label.config(
                text="Введите перевод:",
                fg=config.COLORS['text_secondary']
            )
    
    def show_hint(self):
        """Показывает подсказку (правильный ответ серым цветом)"""
        if not self.current_word_obj or self.hint_active:
            return
        
        # Определяем правильный ответ
        study_lang = self.controller.language
        native_lang = self.controller.native_language
        
        if self.current_word_obj['language'] == study_lang and self.current_word_obj['native_language'] == native_lang:
            correct_answer = self.current_word_obj['translation']
        else:
            correct_answer = self.current_word_obj['foreign']
        
        # Сохраняем текст подсказки
        self.hint_text = correct_answer
        
        # Показываем подсказку в поле ввода
        self.answer_entry.delete(0, tk.END)
        self.answer_entry.insert(0, correct_answer)
        self.answer_entry.config(
            bg=self.original_entry_bg,
            fg=config.COLORS['text_secondary']
        )
        self.hint_active = True
        
        self.update_hint_display()
    
    def clear_hint(self):
        """Убирает подсказку, если пользователь начал вводить текст"""
        if self.hint_active:
            self.answer_entry.delete(0, tk.END)
            self.answer_entry.config(
                bg=self.original_entry_bg,
                fg=self.original_entry_fg
            )
            self.hint_active = False
            self.update_hint_display()
    
    def restore_hint(self):
        """Восстанавливает подсказку, если поле пустое и пользователь не печатает"""
        if self.hint_text and not self.user_typing and not self.hint_active:
            self.answer_entry.delete(0, tk.END)
            self.answer_entry.insert(0, self.hint_text)
            self.answer_entry.config(
                bg=self.original_entry_bg,
                fg=config.COLORS['text_secondary']
            )
            self.hint_active = True
            self.update_hint_display()
    
    def increment_incorrect(self):
        """Увеличивает счетчик неправильных ответов"""
        if self.controller.settings.get('show_hints', False):
            self.incorrect_attempts += 1
            threshold = self.controller.settings.get('hint_threshold', 3)
            
            if self.incorrect_attempts >= threshold and not self.hint_active and not self.user_typing:
                self.show_hint()
            else:
                self.update_hint_display()
    
    def reset_incorrect(self):
        """Сбрасывает счетчик неправильных ответов"""
        self.incorrect_attempts = 0
        if self.hint_active:
            self.clear_hint()
        else:
            self.update_hint_display()
    
    def update_speaker_button_state(self):
        """Обновляет состояние кнопки динамика"""
        if (self.current_display_word and 
            "Нет слов" not in self.current_display_word and 
            self.current_word_obj and 
            speech_synth.enabled and
            speech_synth.is_available()):
            self.speaker_button.config(
                state='normal',
                bg=config.COLORS['speaker'],
                fg=config.COLORS['text']
            )
            self.speaker_normal_bg = config.COLORS['speaker']
        else:
            self.speaker_button.config(
                state='disabled',
                bg=config.COLORS['speaker_disabled'],
                fg=config.COLORS['text_secondary']
            )
            self.speaker_normal_bg = config.COLORS['speaker_disabled']
    
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
                self.speaker_button.config(state='disabled', bg=config.COLORS['speaker_disabled'])
        
        speech_synth.speak_async(self.current_display_word, lang, callback=on_speech_complete)
    
    def get_user_answer(self):
        """Получает ответ пользователя"""
        return self.answer_entry.get().strip()
    
    def focus_entry(self):
        """Устанавливает фокус"""
        self.answer_entry.focus()
    
    def show_success_animation(self):
        """Анимация успеха"""
        animate_success(self.word_card)
        self.reset_incorrect()
    
    def show_error_animation(self):
        """Анимация ошибки"""
        animate_error(self.word_card)
        self.increment_incorrect()
    
    def update_mode_icon(self, lang_code):
        """Обновляет иконку режима"""
        study_flag = config.LANGUAGES[self.controller.language]['flag']
        native_flag = config.LANGUAGES[self.controller.native_language]['flag']
        self.mode_label.config(text=f"{study_flag} → {native_flag}")
    
    def pack(self, **kwargs):
        """Упаковка панели"""
        self.main_frame.pack(**kwargs)
