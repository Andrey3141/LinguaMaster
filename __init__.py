"""
Пакет тренажера иностранных слов
"""

__version__ = "1.0.0"
__author__ = "Vocabulary Trainer Team"
__description__ = "Современный тренажер для изучения иностранных слов"

# Экспорт основных классов
from .models.vocabulary import VocabularyModel
from .views.main_window import MainWindow
from .config import config
