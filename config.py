"""
Конфигурация приложения: цвета, стили, настройки
"""

class Config:
    """Класс конфигурации приложения"""
    
    # Цветовая схема (темная тема)
    COLORS = {
        'bg_dark': '#0f172a',           # Темно-синий фон
        'bg_card': '#1e293b',           # Карточки
        'primary': '#3b82f6',           # Основной акцент (синий)
        'secondary': '#10b981',         # Второстепенный (зеленый)
        'accent': '#8b5cf6',           # Акцент (фиолетовый)
        'text': '#f1f5f9',              # Основной текст
        'text_secondary': '#94a3b8',    # Вторичный текст
        'danger': '#ef4444',            # Ошибки (красный)
        'warning': '#f59e0b',           # Предупреждения (оранжевый)
        'success': '#10b981',           # Успех (зеленый)
        'border': '#334155',            # Границы
        'speaker': '#8b5cf6',           # Цвет кнопки динамика (фиолетовый)
        'speaker_hover': '#7c3aed',      # Цвет при наведении
        'speaker_disabled': '#4a4a4a',   # Цвет отключенного динамика
    }
    
    # Размеры окон
    WINDOW_SIZES = {
        'main': '1920x1080',
        'add_word': '500x350',
        'view_vocabulary': '900x600',
        'hard_words': '500x400',
        'stats': '600x600',
        'settings': '700x550',         # Увеличено для настроек голосов
        'language': '700x500',
        'voice_settings': '500x600'     # Новое окно для выбора голосов
    }
    
    # Шрифты
    FONTS = {
        'title': ('Segoe UI', 20, 'bold'),
        'subtitle': ('Segoe UI', 10),
        'heading': ('Segoe UI', 13, 'bold'),
        'body': ('Segoe UI', 10),
        'body_small': ('Segoe UI', 9),
        'word_display': ('Segoe UI', 36, 'bold'),
        'input': ('Segoe UI', 16),
        'speaker_icon': ('Segoe UI', 14),
    }
    
    # Поддерживаемые языки
    LANGUAGES = {
        'en': {'name': 'Английский', 'flag': '🇺🇸', 'code': 'en'},
        'ru': {'name': 'Русский', 'flag': '🇷🇺', 'code': 'ru'},
        'es': {'name': 'Испанский', 'flag': '🇪🇸', 'code': 'es'},
        'fr': {'name': 'Французский', 'flag': '🇫🇷', 'code': 'fr'},
        'de': {'name': 'Немецкий', 'flag': '🇩🇪', 'code': 'de'},
        'zh': {'name': 'Китайский', 'flag': '🇨🇳', 'code': 'zh'},
        'ja': {'name': 'Японский', 'flag': '🇯🇵', 'code': 'ja'},
        'ko': {'name': 'Корейский', 'flag': '🇰🇷', 'code': 'ko'},
        'pt': {'name': 'Португальский', 'flag': '🇵🇹', 'code': 'pt'},
        'it': {'name': 'Итальянский', 'flag': '🇮🇹', 'code': 'it'},
        'ar': {'name': 'Арабский', 'flag': '🇸🇦', 'code': 'ar'}
    }
    
    # Настройки тренировки
    TRAINING_SETTINGS = {
        'default_language': 'en',
        'native_language': 'ru',
        'quick_training_words': 10,
        'hard_word_threshold': 50,
        'easy_word_threshold': 80,
        'auto_advance': True,
        'show_hints': True,
        'prevent_repeats': True
    }
    
    # Настройки озвучки
    SPEECH_SETTINGS = {
        'enabled': True,
        'auto_speak': False,
        'volume': 100,
        'speed': 1.0,
        'selected_voices': {  # Выбранные голоса для каждого языка
            'ru': 'anna',
            'en': 'slt',
            'es': 'elena',
            'fr': 'celia',
            'de': 'yuriy',
            'zh': 'mikhail',
            'ja': 'mikhail',
            'ko': 'mikhail',
            'pt': 'maria',
            'it': 'aleksandr',
            'ar': 'anna'
        }
    }
    
    # Файлы
    FILES = {
        'vocabulary': 'vocabulary.json',
        'user_settings': 'settings.json'
    }
    
    # Пути к ресурсам
    PATHS = {
        'data': 'data/',
        'backups': 'backups/'
    }
    
    # Тексты
    TEXTS = {
        'app_name': 'LinguaMaster',
        'app_subtitle': 'Тренажер иностранных слов',
        'version': 'v1.13.1',
        'year': '2026'
    }

# Глобальный экземпляр конфигурации
config = Config()
