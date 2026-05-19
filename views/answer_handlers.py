"""
Обработчики проверки ответов пользователя
"""

import time
from utils.notifications import show_notification

class AnswerHandlers:
    """Класс для обработки проверки ответов пользователя"""
    
    def __init__(self, controller):
        """
        Инициализация обработчика ответов
        
        Args:
            controller: Главный контроллер (MainWindow)
        """
        self.controller = controller
    
    def check_answer(self):
        """Проверяет ответ пользователя в режиме ручного ввода"""
        current_time = time.time() * 1000
        if self.controller.check_in_progress or (current_time - self.controller.last_check_time < 500):
            return
        
        if not self.controller.has_words_for_current_language():
            show_notification(
                self.controller.root,
                "Нет слов для изучения",
                f"Добавьте слова для пары {self.controller.language} → {self.controller.native_language}",
                "warning"
            )
            return
        
        if self.controller.model.current_word is None:
            show_notification(
                self.controller.root,
                "Нет слова для проверки",
                "Выберите слово или добавьте новые",
                "warning"
            )
            return
        
        self.controller.check_in_progress = True
        self.controller.last_check_time = current_time
        
        try:
            user_answer = self.controller.training_panel.get_user_answer()
            
            if not user_answer:
                show_notification(
                    self.controller.root,
                    "Пустой ответ",
                    "Введите перевод слова",
                    "warning"
                )
                return
            
            study_lang = self.controller.language
            native_lang = self.controller.native_language
            current_word = self.controller.model.current_word
            
            # Определяем правильный ответ с поддержкой множественных переводов
            if current_word['language'] == study_lang and current_word['native_language'] == native_lang:
                # Прямое направление - проверяем по списку переводов
                if 'translations' in current_word and current_word['translations']:
                    correct_translations = [t.lower() for t in current_word['translations']]
                    correct_display = ', '.join(current_word['translations'])
                    is_correct = user_answer.lower() in correct_translations
                else:
                    correct_answer = current_word.get('translation', '').lower()
                    correct_display = current_word.get('translation', '')
                    is_correct = user_answer.lower() == correct_answer
            else:
                # Обратное направление - проверяем иностранное слово
                correct_answer = current_word['foreign'].lower()
                correct_display = current_word['foreign']
                is_correct = user_answer.lower() == correct_answer
            
            if is_correct:
                self.controller.training_panel.show_success_animation()
                show_notification(
                    self.controller.root,
                    "Правильно! 🎉",
                    f"Правильный ответ: {correct_display}",
                    "success"
                )
                if self.controller.settings['auto_advance']:
                    self.controller.root.after(800, self._safe_next_word)
            else:
                self.controller.training_panel.show_error_animation()
                show_notification(
                    self.controller.root,
                    "Неправильно 😕",
                    f"Правильно: {correct_display}",
                    "error"
                )
            
            # Обновляем статистику
            self.controller.model.check_answer(user_answer, self.controller.mode)
            self.controller.update_stats()
            
        finally:
            self.controller.root.after(500, lambda: setattr(self.controller, 'check_in_progress', False))
    
    def check_test_answer(self, selected_answer):
        """Проверяет ответ в тестовом режиме"""
        if not self.controller.model.current_word:
            return
        
        study_lang = self.controller.language
        native_lang = self.controller.native_language
        current_word = self.controller.model.current_word
        
        # Определяем правильный ответ с поддержкой множественных переводов
        if current_word['language'] == study_lang and current_word['native_language'] == native_lang:
            if 'translations' in current_word and current_word['translations']:
                correct_answer = current_word['translations'][0]
            else:
                correct_answer = current_word.get('translation', '')
        else:
            correct_answer = current_word['foreign']
        
        is_correct = (selected_answer == correct_answer)
        
        if is_correct:
            self.controller.test_panel.show_result(True, correct_answer)
            show_notification(self.controller.root, "✅ Правильно!", "Отличная работа!", "success")
            if self.controller.settings['auto_advance']:
                self.controller.root.after(800, self._safe_next_word)
        else:
            self.controller.test_panel.show_result(False, correct_answer)
            show_notification(self.controller.root, "❌ Ошибка", f"Правильно: {correct_answer}", "error")
        
        self.controller.model.check_answer(selected_answer if is_correct else "", self.controller.mode)
        self.controller.update_stats()
    
    def check_image_answer(self):
        """Проверяет ответ пользователя в режиме картинок"""
        current_time = time.time() * 1000
        if self.controller.check_in_progress or (current_time - self.controller.last_check_time < 500):
            return
        
        if not self.controller.has_words_for_current_language():
            show_notification(
                self.controller.root,
                "Нет слов для изучения",
                f"Добавьте слова для пары {self.controller.language} → {self.controller.native_language}",
                "warning"
            )
            return
        
        if self.controller.model.current_word is None:
            show_notification(
                self.controller.root,
                "Нет слова для проверки",
                "Выберите слово или добавьте новые",
                "warning"
            )
            return
        
        self.controller.check_in_progress = True
        self.controller.last_check_time = current_time
        
        try:
            user_answer = self.controller.image_panel.get_user_answer()
            
            if not user_answer:
                show_notification(
                    self.controller.root,
                    "Пустой ответ",
                    "Введите перевод слова",
                    "warning"
                )
                return
            
            current_word = self.controller.model.current_word
            
            if current_word['language'] == self.controller.language:
                correct_answer = current_word['foreign']
            else:
                if 'translations' in current_word and current_word['translations']:
                    correct_answer = current_word['translations'][0]
                else:
                    correct_answer = current_word.get('translation', '')
            
            is_correct = user_answer.lower() == correct_answer.lower()
            
            if is_correct:
                self.controller.image_panel.show_success_animation()
                show_notification(
                    self.controller.root,
                    "Правильно! 🎉",
                    f"Правильный ответ: {correct_answer}",
                    "success"
                )
                if self.controller.settings['auto_advance']:
                    self.controller.root.after(800, self._safe_next_word)
            else:
                self.controller.image_panel.show_error_animation()
                show_notification(
                    self.controller.root,
                    "Неправильно 😕",
                    f"Правильно: {correct_answer}",
                    "error"
                )
            
            self.controller.model.check_answer(user_answer, self.controller.mode)
            self.controller.update_stats()
            
        finally:
            self.controller.root.after(500, lambda: setattr(self.controller, 'check_in_progress', False))
    
    def _safe_next_word(self):
        """Безопасный вызов next_word"""
        try:
            success = self.controller.next_word()
            if not success:
                show_notification(
                    self.controller.root,
                    "Словарь пуст",
                    "Добавьте новые слова для продолжения",
                    "info"
                )
        except Exception:
            pass
