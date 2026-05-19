"""
Обработчик навигации (смена режимов, категорий, получение следующего слова)
"""

import random
from config import config
from utils.notifications import show_notification

class NavigationHandler:
    """Класс для обработки навигации в приложении"""
    
    def __init__(self, controller):
        """
        Инициализация обработчика навигации
        
        Args:
            controller: Главный контроллер (MainWindow)
        """
        self.controller = controller
    
    def set_mode(self, mode):
        """
        Устанавливает режим тренировки
        
        Args:
            mode: Режим в формате 'en-ru' или 'ru-en'
        """
        self.controller.mode = mode
        if '-' in mode:
            parts = mode.split('-')
            if len(parts) == 2:
                self.controller.language = parts[0]
                self.controller.native_language = parts[1]
        
        # Обновляем иконку в текущей панели
        if self.controller.training_panel:
            self.controller.training_panel.update_mode_icon(self.controller.language)
        if self.controller.test_panel:
            self.controller.test_panel.update_mode_icon(self.controller.language)
        if self.controller.match_panel:
            self.controller.match_panel.update_mode_icon(self.controller.language)
        if self.controller.image_panel:
            self.controller.image_panel.update_mode_icon(self.controller.language)
        
        self.controller.top_bar.update_mode_buttons(mode)
        self.controller.update_interface_colors()
        
        self.controller.model.current_word = None
        self.controller.recent_words = []
        
        self._check_vocabulary_for_current_language()
        self.next_word()
    
    def on_category_change(self, event=None):
        """Обработчик изменения категории"""
        selected = self.controller.category_var.get()
        if selected == "Все категории":
            self.controller.current_category = None
        else:
            self.controller.current_category = selected
        self.next_word()
    
    def _check_vocabulary_for_current_language(self):
        """Проверяет, есть ли слова для текущей пары языков"""
        words_for_pair = [
            w for w in self.controller.model.vocabulary 
            if (w['language'] == self.controller.language and w['native_language'] == self.controller.native_language) or
               (w['language'] == self.controller.native_language and w['native_language'] == self.controller.language)
        ]
        
        if not words_for_pair:
            message = f"Добавьте слова для языков {config.LANGUAGES[self.controller.language]['name']} ↔ {config.LANGUAGES[self.controller.native_language]['name']}"
            
            if self.controller.training_panel:
                self.controller.training_panel.word_label.config(
                    text="Нет слов для изучения",
                    font=('Segoe UI', 24, 'bold')
                )
                self.controller.training_panel.hint_label.config(text=message)
                self.controller.training_panel.answer_entry.delete(0, 'end')
                self.controller.training_panel.answer_entry.config(state='disabled')
                self.controller.training_panel.check_button.config(state='disabled')
                self.controller.training_panel.speaker_button.config(state='disabled')
            
            if self.controller.test_panel:
                self.controller.test_panel.show_no_words_message()
            
            if self.controller.match_panel:
                self.controller.match_panel.show_no_words_message()
            
            if self.controller.image_panel:
                self.controller.image_panel.show_no_words_message()
            
            show_notification(
                self.controller.root,
                "Словарь пуст!",
                f"Нет слов для пары {config.LANGUAGES[self.controller.language]['flag']} ↔ {config.LANGUAGES[self.controller.native_language]['flag']}",
                "warning"
            )
            return False
        
        if self.controller.training_panel:
            self.controller.training_panel.answer_entry.config(state='normal')
            self.controller.training_panel.check_button.config(state='normal')
            if self.controller.settings['enabled']:
                self.controller.training_panel.speaker_button.config(state='normal')
        
        return True
    
    def generate_match_words(self):
        """Генерирует 3 слова для режима соотношения"""
        study_lang = self.controller.language
        native_lang = self.controller.native_language
        
        all_words = [
            w for w in self.controller.model.vocabulary 
            if (w['language'] == study_lang and w['native_language'] == native_lang) or
               (w['language'] == native_lang and w['native_language'] == study_lang)
        ]
        
        if self.controller.current_category:
            all_words = [w for w in all_words if w.get('category', "Основные") == self.controller.current_category]
        
        if len(all_words) < 3:
            return None
        
        selected_words = random.sample(all_words, 3)
        return selected_words
    
    def next_word(self):
        """Выбирает следующее слово"""
        if not self._check_vocabulary_for_current_language():
            return False
        
        study_lang = self.controller.language
        native_lang = self.controller.native_language
        
        if self.controller.learning_method == 'match':
            match_words = self.generate_match_words()
            if match_words and self.controller.match_panel:
                self.controller.match_panel.set_question(match_words)
                return True
            else:
                if self.controller.match_panel:
                    self.controller.match_panel.show_no_words_message()
                show_notification(
                    self.controller.root,
                    "Недостаточно слов",
                    "Для режима соотношения нужно минимум 3 слова в выбранной категории",
                    "warning"
                )
                return False
        
        elif self.controller.learning_method == 'image' and self.controller.image_panel:
            all_words_with_images = [
                w for w in self.controller.model.vocabulary 
                if (w['language'] == study_lang and w['native_language'] == native_lang) or
                   (w['language'] == native_lang and w['native_language'] == study_lang)
            ]
            
            words_with_images = [w for w in all_words_with_images if w.get('image')]
            
            if self.controller.current_category:
                words_with_images = [w for w in words_with_images if w.get('category', "Основные") == self.controller.current_category]
            
            if not words_with_images:
                self.controller.image_panel.show_no_image_message()
                show_notification(
                    self.controller.root,
                    "Нет картинок",
                    "В этой категории нет слов с картинками",
                    "info"
                )
                return False
            
            if self.controller.model.current_word and self.controller.model.current_word in words_with_images and len(words_with_images) > 1:
                words_with_images.remove(self.controller.model.current_word)
            
            try:
                word = random.choice(words_with_images)
            except (IndexError, ValueError):
                return False
            
            if word:
                self.controller.model.current_word = word
                self.controller.image_panel.set_image_word(word)
                return True
            return False
        
        else:
            all_words = [
                w for w in self.controller.model.vocabulary 
                if (w['language'] == study_lang and w['native_language'] == native_lang) or
                   (w['language'] == native_lang and w['native_language'] == study_lang)
            ]
            
            if self.controller.current_category:
                all_words = [w for w in all_words if w.get('category', "Основные") == self.controller.current_category]
            
            if not all_words:
                if self.controller.current_category:
                    message = f"Нет слов в категории '{self.controller.current_category}'"
                else:
                    message = "Нет слов для изучения"
                
                if self.controller.training_panel:
                    self.controller.training_panel.word_label.config(text=message, font=('Segoe UI', 24, 'bold'))
                if self.controller.test_panel:
                    self.controller.test_panel.show_message(message)
                return False
            
            if len(all_words) > 1 and self.controller.settings.get('prevent_repeats', True):
                available_words = [w for w in all_words if w not in self.controller.recent_words]
                if available_words:
                    all_words = available_words
                else:
                    self.controller.recent_words = []
            
            try:
                word = random.choice(all_words)
            except (IndexError, ValueError):
                return False
            
            if word:
                self.controller.model.current_word = word
                self.controller.recent_words.append(word)
                if len(self.controller.recent_words) > self.controller.max_recent_words:
                    self.controller.recent_words.pop(0)
                
                if self.controller.learning_method == 'test' and self.controller.test_panel:
                    if word['language'] == study_lang and word['native_language'] == native_lang:
                        display_word = word['foreign']
                        # Для правильного ответа используем первый перевод
                        if 'translations' in word and word['translations']:
                            correct_answer = word['translations'][0]
                        else:
                            correct_answer = word.get('translation', '')
                    else:
                        display_word = self._get_display_translation(word)
                        correct_answer = word['foreign']
                    
                    options = self.controller.generate_test_options(word, correct_answer, study_lang, native_lang)
                    self.controller.test_panel.set_question(display_word, options, correct_answer, word)
                
                elif self.controller.training_panel:
                    if word['language'] == study_lang and word['native_language'] == native_lang:
                        display_word = word['foreign']
                    else:
                        display_word = self._get_display_translation(word)
                    
                    hint_text = "Введите перевод:" if self.controller.settings['show_hints'] else ""
                    self.controller.training_panel.set_word(display_word, hint_text, word)
                    self.controller.training_panel.focus_entry()
                
                return True
            return False
    
    def _get_display_translation(self, word):
        """Возвращает отображаемый перевод для слова"""
        if 'translations' in word and word['translations']:
            return word['translations'][0]
        elif 'translation' in word:
            return word['translation']
        return ""
