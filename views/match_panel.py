"""
Панель режима соотношения слов (сопоставление)
"""

import tkinter as tk
import random
from config import config
from utils.animations import animate_success, animate_error

class MatchPanel:
    """Класс панели режима соотношения слов"""
    
    def __init__(self, parent, controller):
        """
        Инициализация панели соотношения слов
        
        Args:
            parent: Родительский виджет
            controller: Контроллер (MainWindow)
        """
        self.parent = parent
        self.controller = controller
        self.current_word_obj = None
        self.left_words = []  # Слова слева (обычно иностранные)
        self.right_words = []  # Слова справа (обычно переводы)
        self.selected_left = None
        self.selected_right = None
        self.matched_pairs = []  # Список сопоставленных пар (индекс слева, индекс справа)
        self.left_buttons = []
        self.right_buttons = []
        self.current_correct_word = None
        self.current_correct_translation = None
        
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
        native_flag = config.LANGUAGES[self.controller.native_language]['flag']
        self.mode_label = tk.Label(
            self.mode_frame,
            text=f"{study_flag} ↔ {native_flag}",
            font=('Segoe UI', 20, 'bold'),
            bg=config.COLORS['bg_card'],
            fg=config.COLORS['text']
        )
        self.mode_label.pack()
        
        # Подсказка
        self.hint_label = tk.Label(
            self.main_frame,
            text="Сопоставьте слова, нажимая на пары",
            font=('Segoe UI', 12),
            bg=config.COLORS['bg_card'],
            fg=config.COLORS['text_secondary'],
            pady=10
        )
        self.hint_label.pack()
        
        # Фрейм для двух колонок
        self.columns_frame = tk.Frame(self.main_frame, bg=config.COLORS['bg_dark'], padx=20, pady=20)
        self.columns_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Левая колонка
        self.left_frame = tk.Frame(self.columns_frame, bg=config.COLORS['bg_dark'], width=250)
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Заголовок левой колонки
        study_lang_name = config.LANGUAGES[self.controller.language]['name']
        tk.Label(
            self.left_frame,
            text=f"{study_lang_name}:",
            font=('Segoe UI', 14, 'bold'),
            bg=config.COLORS['bg_dark'],
            fg=config.COLORS['primary']
        ).pack(pady=(0, 10))
        
        # Контейнер для кнопок левой колонки
        self.left_buttons_frame = tk.Frame(self.left_frame, bg=config.COLORS['bg_dark'])
        self.left_buttons_frame.pack(fill=tk.BOTH, expand=True)
        
        # Правая колонка
        self.right_frame = tk.Frame(self.columns_frame, bg=config.COLORS['bg_dark'], width=250)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        # Заголовок правой колонки
        native_lang_name = config.LANGUAGES[self.controller.native_language]['name']
        tk.Label(
            self.right_frame,
            text=f"{native_lang_name}:",
            font=('Segoe UI', 14, 'bold'),
            bg=config.COLORS['bg_dark'],
            fg=config.COLORS['accent']
        ).pack(pady=(0, 10))
        
        # Контейнер для кнопок правой колонки
        self.right_buttons_frame = tk.Frame(self.right_frame, bg=config.COLORS['bg_dark'])
        self.right_buttons_frame.pack(fill=tk.BOTH, expand=True)
        
        # Прогресс
        self.progress_frame = tk.Frame(self.main_frame, bg=config.COLORS['bg_card'])
        self.progress_frame.pack(fill=tk.X, pady=10)
        
        self.progress_label = tk.Label(
            self.progress_frame,
            text="Сопоставлено: 0/3",
            font=('Segoe UI', 12),
            bg=config.COLORS['bg_card'],
            fg=config.COLORS['text']
        )
        self.progress_label.pack()
        
        # Кнопка проверки
        self.check_button = tk.Button(
            self.main_frame,
            text="✅ Проверить все",
            font=('Segoe UI', 14, 'bold'),
            bg=config.COLORS['primary'],
            fg=config.COLORS['text'],
            bd=0,
            padx=30,
            pady=12,
            cursor='hand2',
            command=self.check_all_matches
        )
        self.check_button.pack(pady=15)
    
    def set_question(self, words_data):
        """
        Устанавливает вопрос для соотношения
        
        Args:
            words_data: Список из 3 словарей с парами слов
        """
        self.words_data = words_data
        self.matched_pairs = []
        self.selected_left = None
        self.selected_right = None
        self.current_correct_word = None
        self.current_correct_translation = None
        
        # Очищаем контейнеры
        for widget in self.left_buttons_frame.winfo_children():
            widget.destroy()
        for widget in self.right_buttons_frame.winfo_children():
            widget.destroy()
        
        self.left_buttons = []
        self.right_buttons = []
        
        # Определяем, в каком направлении показывать слова
        study_lang = self.controller.language
        native_lang = self.controller.native_language
        
        # Подготавливаем слова для левой и правой колонки
        self.left_words = []
        self.right_words = []
        self.correct_pairs = []  # (индекс слева, индекс справа)
        
        # Перемешиваем слова, чтобы они были в случайном порядке
        shuffled_data = words_data.copy()
        random.shuffle(shuffled_data)
        
        for word_data in shuffled_data:
            if word_data['language'] == study_lang and word_data['native_language'] == native_lang:
                # Прямое направление
                left_word = word_data['foreign']
                right_word = word_data['translation']
            else:
                # Обратное направление
                left_word = word_data['translation']
                right_word = word_data['foreign']
            
            self.left_words.append(left_word)
            self.right_words.append(right_word)
        
        # Перемешиваем правую колонку отдельно для сложности
        right_indices = list(range(len(self.right_words)))
        random.shuffle(right_indices)
        self.right_words = [self.right_words[i] for i in right_indices]
        
        # Создаем словарь правильных соответствий
        self.correct_mapping = {}
        for i, left_word in enumerate(self.left_words):
            for word_data in words_data:
                if word_data['language'] == study_lang and word_data['native_language'] == native_lang:
                    if left_word == word_data['foreign']:
                        self.correct_mapping[i] = word_data['translation']
                        break
                    elif left_word == word_data['translation']:
                        self.correct_mapping[i] = word_data['foreign']
                        break
                else:
                    if left_word == word_data['translation']:
                        self.correct_mapping[i] = word_data['foreign']
                        break
                    elif left_word == word_data['foreign']:
                        self.correct_mapping[i] = word_data['translation']
                        break
        
        # Создаем кнопки для левой колонки
        for i, word in enumerate(self.left_words):
            btn = tk.Button(
                self.left_buttons_frame,
                text=word,
                font=('Segoe UI', 14),
                bg=config.COLORS['bg_card'],
                fg=config.COLORS['text'],
                bd=2,
                relief=tk.RAISED,
                padx=15,
                pady=12,
                cursor='hand2',
                command=lambda idx=i: self.select_left(idx)
            )
            btn.pack(fill=tk.X, pady=5)
            self.left_buttons.append(btn)
        
        # Создаем кнопки для правой колонки
        for i, word in enumerate(self.right_words):
            btn = tk.Button(
                self.right_buttons_frame,
                text=word,
                font=('Segoe UI', 14),
                bg=config.COLORS['bg_card'],
                fg=config.COLORS['text'],
                bd=2,
                relief=tk.RAISED,
                padx=15,
                pady=12,
                cursor='hand2',
                command=lambda idx=i: self.select_right(idx)
            )
            btn.pack(fill=tk.X, pady=5)
            self.right_buttons.append(btn)
        
        self.update_progress()
    
    def select_left(self, index):
        """Выбирает слово из левой колонки"""
        # Если уже сопоставлено, игнорируем
        for left_idx, right_idx in self.matched_pairs:
            if left_idx == index:
                return
        
        # Снимаем выделение с предыдущего
        if self.selected_left is not None:
            self.left_buttons[self.selected_left].config(bg=config.COLORS['bg_card'], relief=tk.RAISED)
        
        # Выделяем новое
        self.selected_left = index
        self.left_buttons[index].config(bg=config.COLORS['primary'], relief=tk.SUNKEN)
        
        # Если уже выбрано правое слово, пытаемся сопоставить
        if self.selected_right is not None:
            self.make_match()
    
    def select_right(self, index):
        """Выбирает слово из правой колонки"""
        # Если уже сопоставлено, игнорируем
        for left_idx, right_idx in self.matched_pairs:
            if right_idx == index:
                return
        
        # Снимаем выделение с предыдущего
        if self.selected_right is not None:
            self.right_buttons[self.selected_right].config(bg=config.COLORS['bg_card'], relief=tk.RAISED)
        
        # Выделяем новое
        self.selected_right = index
        self.right_buttons[index].config(bg=config.COLORS['accent'], relief=tk.SUNKEN)
        
        # Если уже выбрано левое слово, пытаемся сопоставить
        if self.selected_left is not None:
            self.make_match()
    
    def make_match(self):
        """Сопоставляет выбранные слова"""
        left_idx = self.selected_left
        right_idx = self.selected_right
        
        # Проверяем, правильное ли сопоставление
        left_word = self.left_words[left_idx]
        right_word = self.right_words[right_idx]
        
        is_correct = (self.correct_mapping[left_idx] == right_word)
        
        if is_correct:
            # Правильное сопоставление
            self.matched_pairs.append((left_idx, right_idx))
            
            # Блокируем кнопки
            self.left_buttons[left_idx].config(state='disabled', bg=config.COLORS['success'], relief=tk.RAISED)
            self.right_buttons[right_idx].config(state='disabled', bg=config.COLORS['success'], relief=tk.RAISED)
            
            # Снимаем выделение
            self.selected_left = None
            self.selected_right = None
            
            self.update_progress()
            
            # Если все сопоставлено, показываем успех
            if len(self.matched_pairs) == 3:
                self.all_matched()
        else:
            # Неправильное сопоставление
            animate_error(self.columns_frame)
            
            # Подсвечиваем красным
            self.left_buttons[left_idx].config(bg=config.COLORS['danger'])
            self.right_buttons[right_idx].config(bg=config.COLORS['danger'])
            
            # Возвращаем нормальный цвет через секунду
            self.controller.root.after(500, lambda: self.reset_selection(left_idx, right_idx))
    
    def reset_selection(self, left_idx, right_idx):
        """Сбрасывает выделение после ошибки"""
        self.left_buttons[left_idx].config(bg=config.COLORS['bg_card'])
        self.right_buttons[right_idx].config(bg=config.COLORS['bg_card'])
        
        self.selected_left = None
        self.selected_right = None
    
    def update_progress(self):
        """Обновляет прогресс"""
        count = len(self.matched_pairs)
        self.progress_label.config(text=f"Сопоставлено: {count}/3")
    
    def all_matched(self):
        """Все слова сопоставлены правильно"""
        animate_success(self.columns_frame)
        self.progress_label.config(text="✅ Отлично! Все верно!", fg=config.COLORS['success'])
        self.hint_label.config(text="Молодец! Следующее задание...")
        
        if self.controller.settings['auto_advance']:
            self.controller.root.after(1500, self.controller.next_word)
    
    def check_all_matches(self):
        """Проверяет все сопоставления (кнопка проверки)"""
        if len(self.matched_pairs) == 3:
            # Уже все сопоставлено
            self.all_matched()
            return
        
        # Подсвечиваем правильные ответы
        for left_idx, right_idx in self.matched_pairs:
            self.left_buttons[left_idx].config(bg=config.COLORS['success'])
            self.right_buttons[right_idx].config(bg=config.COLORS['success'])
        
        # Ищем неправильные
        has_errors = False
        for left_idx, left_word in enumerate(self.left_words):
            # Пропускаем уже сопоставленные
            matched = False
            for l_idx, r_idx in self.matched_pairs:
                if l_idx == left_idx:
                    matched = True
                    break
            if matched:
                continue
            
            # Ищем правильное правое слово
            correct_right = self.correct_mapping[left_idx]
            for right_idx, right_word in enumerate(self.right_words):
                if right_word == correct_right:
                    # Проверяем, не сопоставлено ли оно уже с другим
                    already_matched = False
                    for l, r in self.matched_pairs:
                        if r == right_idx:
                            already_matched = True
                            break
                    
                    if not already_matched:
                        # Это правильная пара, подсвечиваем зеленым
                        self.left_buttons[left_idx].config(bg=config.COLORS['warning'])
                        self.right_buttons[right_idx].config(bg=config.COLORS['warning'])
                        has_errors = True
                    break
        
        if has_errors:
            self.hint_label.config(text="Желтым подсвечены правильные пары, которые еще не сопоставлены")
        else:
            self.hint_label.config(text="Сопоставьте оставшиеся слова")
    
    def show_message(self, message):
        """Показывает сообщение (например, нет слов)"""
        # Очищаем контейнеры
        for widget in self.left_buttons_frame.winfo_children():
            widget.destroy()
        for widget in self.right_buttons_frame.winfo_children():
            widget.destroy()
        
        self.hint_label.config(text=message)
        self.progress_label.config(text="")
        self.check_button.config(state='disabled')
    
    def show_no_words_message(self):
        """Показывает сообщение об отсутствии слов"""
        self.show_message("Недостаточно слов для режима соотношения. Нужно минимум 3 слова.")
    
    def update_mode_icon(self, lang_code):
        """Обновляет иконку режима"""
        study_flag = config.LANGUAGES[self.controller.language]['flag']
        native_flag = config.LANGUAGES[self.controller.native_language]['flag']
        self.mode_label.config(text=f"{study_flag} ↔ {native_flag}")
        
        # Обновляем заголовки колонок
        study_lang_name = config.LANGUAGES[self.controller.language]['name']
        native_lang_name = config.LANGUAGES[self.controller.native_language]['name']
        
        # Обновляем заголовки, если они есть
        if hasattr(self, 'left_frame') and self.left_frame.winfo_children():
            for child in self.left_frame.winfo_children():
                if isinstance(child, tk.Label) and child.cget('fg') == config.COLORS['primary']:
                    child.config(text=f"{study_lang_name}:")
                    break
        
        if hasattr(self, 'right_frame') and self.right_frame.winfo_children():
            for child in self.right_frame.winfo_children():
                if isinstance(child, tk.Label) and child.cget('fg') == config.COLORS['accent']:
                    child.config(text=f"{native_lang_name}:")
                    break
    
    def pack(self, **kwargs):
        """Упаковка панели"""
        self.main_frame.pack(**kwargs)
