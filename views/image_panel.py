"""
Панель режима перевода картинки
"""

import tkinter as tk
from tkinter import ttk
import os
from PIL import Image, ImageTk
from config import config
from utils.animations import animate_success, animate_error
from utils.speech import speech_synth

class ImagePanel:
    """Класс панели перевода картинки"""
    
    def __init__(self, parent, controller):
        """
        Инициализация панели перевода картинки
        
        Args:
            parent: Родительский виджет
            controller: Контроллер (MainWindow)
        """
        self.parent = parent
        self.controller = controller
        self.current_word_obj = None
        self.current_image_path = None
        self.photo_image = None
        self.incorrect_attempts = 0
        self.hint_active = False
        self.hint_text = ""
        self.user_typing = False
        self.original_entry_bg = None
        self.original_entry_fg = None
        self.has_image = False
        
        # Папка с картинками
        self.images_dir = os.path.join(config.PATHS['data'], 'pictures')
        os.makedirs(self.images_dir, exist_ok=True)
        
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
        self.mode_frame.pack(fill=tk.X, pady=10)
        
        # Иконка языка
        study_flag = config.LANGUAGES[self.controller.language]['flag']
        self.mode_label = tk.Label(
            self.mode_frame,
            text=f"Переведи на {config.LANGUAGES[self.controller.language]['name']} ({study_flag})",
            font=('Segoe UI', 18, 'bold'),
            bg=config.COLORS['bg_card'],
            fg=config.COLORS['text']
        )
        self.mode_label.pack()
        
        # Карточка с картинкой на полуночном синем фоне
        self.image_card = tk.Frame(
            self.main_frame,
            bg='#2d304a',
            width=900,
            height=400
        )
        self.image_card.pack(fill=tk.BOTH, expand=True, pady=20)
        self.image_card.pack_propagate(False)
        
        # Место для картинки
        self.image_label = tk.Label(
            self.image_card,
            text="🖼️",
            font=('Segoe UI', 48),
            bg='#2d304a',
            fg=config.COLORS['text_secondary']
        )
        self.image_label.pack(expand=True, fill=tk.BOTH)
        
        # Подсказка
        self.hint_label = tk.Label(
            self.main_frame,
            text="Что изображено на картинке?",
            font=config.FONTS['body_small'],
            bg=config.COLORS['bg_card'],
            fg=config.COLORS['text_secondary'],
            pady=10
        )
        self.hint_label.pack()
        
        # Фрейм для поля ввода и кнопки динамика
        input_frame = tk.Frame(self.main_frame, bg=config.COLORS['bg_card'])
        input_frame.pack(fill=tk.X, pady=10)
        
        # Поле ввода
        self.answer_entry = tk.Entry(
            input_frame,
            font=config.FONTS['input'],
            bg=config.COLORS['bg_card'],
            fg=config.COLORS['text'],
            insertbackground=config.COLORS['text'],
            bd=0,
            justify='center'
        )
        self.answer_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=10, padx=(0, 10))
        
        # Кнопка динамика для озвучки
        self.speaker_button = tk.Button(
            input_frame,
            text="🔊",
            font=config.FONTS['speaker_icon'],
            bg=config.COLORS['speaker'],
            fg=config.COLORS['text'],
            bd=0,
            padx=15,
            pady=8,
            cursor='hand2',
            command=self.speak_current_word,
            state='normal' if speech_synth.enabled else 'disabled'
        )
        self.speaker_button.pack(side=tk.RIGHT)
        
        # Сохраняем оригинальные цвета для восстановления
        self.original_entry_bg = config.COLORS['bg_card']
        self.original_entry_fg = config.COLORS['text']
        
        # Привязываем события для поля ввода
        self.answer_entry.bind('<FocusIn>', self._on_entry_focus_in)
        self.answer_entry.bind('<FocusOut>', self._on_entry_focus_out)
        self.answer_entry.bind('<KeyPress>', self._on_key_press)
        self.answer_entry.bind('<KeyRelease>', self._on_key_release)
        
        # Эффект при наведении на кнопку динамика
        self.speaker_button.bind('<Enter>', self._on_speaker_hover)
        self.speaker_button.bind('<Leave>', self._on_speaker_leave)
        
        # Подчеркивание поля ввода
        self.entry_underline = tk.Frame(
            self.main_frame,
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
            command=self.controller.check_image_answer
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
            self.speaker_button.config(bg=config.COLORS['speaker'])
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
    
    def set_image_word(self, word_obj):
        """
        Устанавливает слово с картинкой для тренировки
        
        Args:
            word_obj: Объект слова из модели
        """
        self.current_word_obj = word_obj
        self.incorrect_attempts = 0
        self.hint_active = False
        self.hint_text = ""
        self.user_typing = False
        self.has_image = False
        
        # Сбрасываем картинку
        self.image_label.config(image="", text="🖼️", font=('Segoe UI', 48))
        
        # Проверяем, есть ли картинка для слова
        image_filename = word_obj.get('image', '')
        if image_filename:
            image_path = os.path.join(self.images_dir, image_filename)
            if os.path.exists(image_path):
                try:
                    # Загружаем и отображаем картинку
                    image = Image.open(image_path)
                    
                    # Изменяем размер под контейнер
                    max_width = 880
                    max_height = 480
                    image.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
                    
                    self.photo_image = ImageTk.PhotoImage(image)
                    self.image_label.config(image=self.photo_image, text="")
                    self.has_image = True
                except Exception as e:
                    print(f"Ошибка загрузки картинки: {e}")
        
        # Очищаем поле ввода
        self.answer_entry.delete(0, tk.END)
        self.answer_entry.config(
            bg=self.original_entry_bg,
            fg=self.original_entry_fg
        )
        
        # Обновляем подсказку
        self.update_hint_display()
        
        # Обновляем состояние кнопки динамика и поля ввода
        self.update_speaker_button_state()
        
        if not self.has_image:
            self.answer_entry.config(state='disabled')
            self.check_button.config(state='disabled')
            self.hint_label.config(text="Для этого слова нет картинки")
        else:
            self.answer_entry.config(state='normal')
            self.check_button.config(state='normal')
            # Включаем Enter
            self.answer_entry.bind('<Return>', lambda e: self.controller.check_image_answer())
            
            # Автоматическая озвучка
            if speech_synth.enabled and self.controller.settings.get('auto_speak', False):
                self.controller.root.after(100, self.speak_current_word)
    
    def update_hint_display(self):
        """Обновляет отображение подсказки"""
        if not self.has_image:
            return
            
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
            self.hint_label.config(
                text="Что изображено на картинке?",
                fg=config.COLORS['text_secondary']
            )
    
    def show_hint(self):
        """Показывает подсказку (правильный ответ серым цветом)"""
        if not self.current_word_obj or self.hint_active or not self.has_image:
            return
        
        # Определяем правильный ответ (слово на изучаемом языке)
        if self.current_word_obj['language'] == self.controller.language:
            correct_answer = self.current_word_obj['foreign']
        else:
            correct_answer = self.current_word_obj['translation']
        
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
        if self.hint_active and self.has_image:
            self.answer_entry.delete(0, tk.END)
            self.answer_entry.config(
                bg=self.original_entry_bg,
                fg=self.original_entry_fg
            )
            self.hint_active = False
            self.update_hint_display()
    
    def restore_hint(self):
        """Восстанавливает подсказку, если поле пустое и пользователь не печатает"""
        if self.hint_text and not self.user_typing and not self.hint_active and self.has_image:
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
        if self.has_image and self.controller.settings.get('show_hints', False):
            self.incorrect_attempts += 1
            threshold = self.controller.settings.get('hint_threshold', 3)
            
            if self.incorrect_attempts >= threshold and not self.hint_active and not self.user_typing:
                self.show_hint()
            else:
                self.update_hint_display()
    
    def reset_incorrect(self):
        """Сбрасывает счетчик неправильных ответов"""
        self.incorrect_attempts = 0
        if self.hint_active and self.has_image:
            self.clear_hint()
        else:
            self.update_hint_display()
    
    def update_speaker_button_state(self):
        """Обновляет состояние кнопки динамика"""
        if (self.has_image and self.current_word_obj and 
            speech_synth.enabled and
            speech_synth.is_available()):
            self.speaker_button.config(
                state='normal',
                bg=config.COLORS['speaker'],
                fg=config.COLORS['text']
            )
        else:
            self.speaker_button.config(
                state='disabled',
                bg=config.COLORS['speaker_disabled'],
                fg=config.COLORS['text_secondary']
            )
    
    def speak_current_word(self):
        """Озвучивает текущее слово (правильный ответ)"""
        if not speech_synth.enabled or not self.current_word_obj or not self.has_image:
            return
        
        # Определяем правильный ответ для озвучки
        if self.current_word_obj['language'] == self.controller.language:
            word_to_speak = self.current_word_obj['foreign']
            lang = self.current_word_obj['language']
        else:
            word_to_speak = self.current_word_obj['translation']
            lang = self.current_word_obj['native_language']
        
        # Временно делаем кнопку неактивной
        self.speaker_button.config(state='disabled', bg=config.COLORS['speaker_disabled'])
        
        def on_speech_complete(success):
            if (self.has_image and self.current_word_obj and speech_synth.enabled):
                self.speaker_button.config(state='normal', bg=config.COLORS['speaker'])
            else:
                self.speaker_button.config(state='disabled', bg=config.COLORS['speaker_disabled'])
        
        speech_synth.speak_async(word_to_speak, lang, callback=on_speech_complete)
    
    def get_user_answer(self):
        """Получает ответ пользователя"""
        return self.answer_entry.get().strip()
    
    def focus_entry(self):
        """Устанавливает фокус"""
        if self.has_image:
            self.answer_entry.focus()
    
    def show_success_animation(self):
        """Анимация успеха"""
        if self.has_image:
            animate_success(self.image_card)
            self.reset_incorrect()
    
    def show_error_animation(self):
        """Анимация ошибки"""
        if self.has_image:
            animate_error(self.image_card)
            self.increment_incorrect()
    
    def show_no_image_message(self):
        """Показывает сообщение об отсутствии картинок"""
        self.image_label.config(image="", text="🖼️❌", font=('Segoe UI', 64))
        self.hint_label.config(text="Нет слов с картинками в этой категории")
        self.answer_entry.config(state='disabled')
        self.check_button.config(state='disabled')
        self.speaker_button.config(state='disabled')
        self.has_image = False
        self.current_word_obj = None
    
    def show_no_words_message(self):
        """Показывает сообщение об отсутствии слов (для совместимости)"""
        self.show_no_image_message()
    
    def update_mode_icon(self, lang_code):
        """Обновляет иконку режима"""
        study_flag = config.LANGUAGES[self.controller.language]['flag']
        self.mode_label.config(
            text=f"Переведи на {config.LANGUAGES[self.controller.language]['name']} ({study_flag})"
        )
    
    def pack(self, **kwargs):
        """Упаковка панели"""
        self.main_frame.pack(**kwargs)
