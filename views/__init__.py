"""
Пакет views - содержит все классы представлений (интерфейса)
"""

from .widgets import *
from .main_window import MainWindow
from .top_bar import TopBar
from .stats_panel import StatsPanel
from .training_panel import TrainingPanel
from .control_panel import ControlPanel
from .dialog_handlers import DialogHandlers
from .vocabulary_dialog import VocabularyDialog
from .stats_dialog import StatsDialog

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
