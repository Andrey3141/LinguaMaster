"""
Диалоговые окна приложения
"""

from .add_word_dialog import AddWordDialog
from .settings_dialog import SettingsDialog
from .language_dialog import LanguageDialog

class DialogHandlers:
    """Класс-обертка для обратной совместимости"""
    
    @staticmethod
    def add_word_dialog(controller):
        AddWordDialog.show(controller)
    
    @staticmethod
    def show_settings_dialog(controller):
        SettingsDialog.show(controller)
    
    @staticmethod
    def change_language_dialog(controller):
        LanguageDialog.show(controller)
    
    @staticmethod
    def refresh_words(controller):
        """Обновляет список слов"""
        controller.next_word()
        from utils.notifications import show_notification
        show_notification(
            controller.root,
            "Список обновлен",
            "Выбрано новое слово",
            "info"
        )
    
    @staticmethod
    def quick_training(controller):
        """Быстрая тренировка"""
        controller.settings['quick_training_words'] = 10
        from utils.notifications import show_notification
        show_notification(
            controller.root,
            "Быстрая тренировка",
            f"Будет показано {controller.settings['quick_training_words']} слов",
            "info"
        )
        controller.next_word()
    
    @staticmethod
    def set_difficulty(controller, difficulty):
        """Устанавливает сложность слов"""
        controller.difficulty = difficulty
        controller.next_word()
        
        from utils.notifications import show_notification
        difficulty_names = {
            'all': 'все слова',
            'easy': 'легкие слова',
            'medium': 'средние слова',
            'hard': 'сложные слова'
        }
        
        show_notification(
            controller.root,
            "Сложность изменена",
            f"Теперь показываются {difficulty_names.get(difficulty, difficulty)}",
            "info"
        )
