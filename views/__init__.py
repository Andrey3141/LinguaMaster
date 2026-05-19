"""
Пакет views - содержит все классы представлений (интерфейса)
"""

from .main_window import MainWindow
from .dialogs import DialogHandlers
from .training_panel import TrainingPanel
from .test_panel import TestPanel
from .match_panel import MatchPanel
from .image_panel import ImagePanel
from .top_bar import TopBar
from .stats_panel import StatsPanel
from .control_panel import ControlPanel
from .vocabulary_dialog import VocabularyDialog
from .stats_dialog import StatsDialog
from .voice_settings_dialog import VoiceSettingsDialog
from .navigation import NavigationHandler
from .answer_handlers import AnswerHandlers
from .learning_methods import LearningMethodHandler

__all__ = [
    'MainWindow',
    'TopBar',
    'StatsPanel',
    'TrainingPanel',
    'ControlPanel',
    'DialogHandlers',
    'VocabularyDialog',
    'StatsDialog'
]
