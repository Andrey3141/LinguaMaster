"""
Менеджер настроек приложения
"""

import json
import os
from config import config

class SettingsManager:
    """Класс для управления настройками приложения"""
    
    def __init__(self):
        """Инициализация менеджера настроек"""
        data_dir = config.PATHS['data']
        os.makedirs(data_dir, exist_ok=True)
        self.settings_file = os.path.join(data_dir, 'app_settings.json')
        self.settings = {}
        self.load_settings()
    
    def load_settings(self):
        """Загружает настройки из файла"""
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    self.settings = json.load(f)
                print(f"✅ Загружены настройки из {self.settings_file}")
            except Exception as e:
                print(f"Ошибка загрузки настроек: {e}")
                self.settings = {}
        else:
            self.settings = {}
    
    def save_settings(self, settings):
        """Сохраняет настройки в файл"""
        try:
            os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
            self.settings = settings.copy()
            print(f"✅ Сохранены настройки в {self.settings_file}")
            return True
        except Exception as e:
            print(f"Ошибка сохранения настроек: {e}")
            return False
    
    def get(self, key, default=None):
        """Получает значение настройки по ключу"""
        return self.settings.get(key, default)
    
    def get_all(self):
        """Возвращает все настройки"""
        return self.settings.copy()

# Глобальный экземпляр менеджера настроек
settings_manager = SettingsManager()
