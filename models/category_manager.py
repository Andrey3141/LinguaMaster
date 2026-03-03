"""
Модель словаря
"""

import json
import os
import random
from datetime import datetime, date
from config import config

class VocabularyModel:
    """Модель для работы со словарем"""
    
    def __init__(self):
        """Инициализация модели"""
        self.vocabulary = []
        self.current_word = None
        self.load_vocabulary()
        
        # Статистика
        self.daily_stats = {
            'date': str(date.today()),
            'words_today': 0,
            'correct_today': 0
        }
        self.load_stats()
    
    def load_vocabulary(self):
        """Загружает словарь из JSON файла"""
        file_path = os.path.join(config.PATHS['data'], config.FILES['vocabulary'])
        
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.vocabulary = json.load(f)
                print(f"Загружено {len(self.vocabulary)} слов")
            except Exception as e:
                print(f"Ошибка загрузки словаря: {e}")
                self.vocabulary = []
        else:
            print(f"Файл словаря не найден: {file_path}")
            self.vocabulary = []
    
    def save_vocabulary(self):
        """Сохраняет словарь в JSON файл"""
        file_path = os.path.join(config.PATHS['data'], config.FILES['vocabulary'])
        
        # Создаем директорию если ее нет
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.vocabulary, f, ensure_ascii=False, indent=2)
            print(f"Словарь сохранен: {len(self.vocabulary)} слов")
        except Exception as e:
            print(f"Ошибка сохранения словаря: {e}")
    
    def load_stats(self):
        """Загружает статистику"""
        try:
            file_path = os.path.join(config.PATHS['data'], 'stats.json')
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    stats = json.load(f)
                
                # Проверяем дату
                if stats.get('date') == str(date.today()):
                    self.daily_stats = stats
                else:
                    # Новый день - сбрасываем статистику
                    self.daily_stats = {
                        'date': str(date.today()),
                        'words_today': 0,
                        'correct_today': 0
                    }
        except Exception as e:
            print(f"Ошибка загрузки статистики: {e}")
    
    def save_stats(self):
        """Сохраняет статистику"""
        try:
            file_path = os.path.join(config.PATHS['data'], 'stats.json')
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.daily_stats, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Ошибка сохранения статистики: {e}")
    
    def add_word(self, foreign, translation, language='en', native_language='ru'):
        """
        Добавляет новое слово в словарь
        
        Args:
            foreign: Иностранное слово
            translation: Перевод
            language: Язык иностранного слова
            native_language: Родной язык
            
        Returns:
            bool: Успешно ли добавлено
        """
        # Сохраняем оригинальный регистр
        foreign = foreign.strip()
        translation = translation.strip()
        
        # Проверяем, нет ли уже такого слова
        for word in self.vocabulary:
            if (word['foreign'].lower() == foreign.lower() and 
                word['language'] == language and
                word['native_language'] == native_language):
                return False
        
        # Создаем новую запись
        new_word = {
            'foreign': foreign,
            'translation': translation,
            'language': language,
            'native_language': native_language,
            'added_date': str(date.today()),
            'last_review': None,
            'review_count': 0,
            'correct_count': 0,
            'incorrect_count': 0,
            'difficulty': 50  # Средняя сложность (0-100)
        }
        
        self.vocabulary.append(new_word)
        self.save_vocabulary()
        return True
    
    def get_random_word(self, difficulty='all', language='en', native_language='ru', prevent_repeats=True):
        """
        Получает случайное слово
        
        Args:
            difficulty: Уровень сложности ('all', 'easy', 'medium', 'hard')
            language: Язык слова
            native_language: Родной язык
            prevent_repeats: Предотвращать повторения
            
        Returns:
            dict: Случайное слово или None
        """
        # Фильтруем слова по языку - ИСПРАВЛЕНО: учитываем оба направления
        filtered_words = [
            word for word in self.vocabulary 
            if word['language'] == language and word['native_language'] == native_language
        ]
        
        if not filtered_words:
            return None
        
        # Фильтрация по сложности
        if difficulty == 'easy':
            filtered_words = [w for w in filtered_words if w['difficulty'] >= config.TRAINING_SETTINGS['easy_word_threshold']]
        elif difficulty == 'hard':
            filtered_words = [w for w in filtered_words if w['difficulty'] <= config.TRAINING_SETTINGS['hard_word_threshold']]
        elif difficulty == 'medium':
            filtered_words = [w for w in filtered_words if 
                             w['difficulty'] > config.TRAINING_SETTINGS['hard_word_threshold'] and 
                             w['difficulty'] < config.TRAINING_SETTINGS['easy_word_threshold']]
        
        if not filtered_words:
            # Если после фильтрации по сложности слов нет, возвращаем любые слова для этой языковой пары
            filtered_words = [
                word for word in self.vocabulary 
                if word['language'] == language and word['native_language'] == native_language
            ]
        
        if not filtered_words:
            return None
        
        # Если нужно предотвратить повторения, убираем текущее слово
        if prevent_repeats and self.current_word:
            # Создаем новый список без текущего слова
            temp_words = [w for w in filtered_words if w != self.current_word]
            # Если после удаления текущего слова остались другие слова, используем их
            if temp_words:
                filtered_words = temp_words
            # Иначе используем все слова (включая текущее)
            # чтобы не было пустого списка
        
        # Выбираем случайное слово
        try:
            self.current_word = random.choice(filtered_words)
            return self.current_word
        except IndexError:
            # Если список пуст (что не должно происходить после проверок)
            return None
    
    def check_answer(self, user_answer, mode='en-ru'):
        """
        Проверяет ответ пользователя
        
        Args:
            user_answer: Ответ пользователя
            mode: Режим тренировки ('en-ru' или 'ru-en')
            
        Returns:
            tuple: (is_correct, correct_answer)
        """
        if not self.current_word:
            return False, ""
        
        # Обновляем статистику дня
        self.daily_stats['words_today'] += 1
        
        # Определяем правильный ответ в зависимости от режима
        if '-' in mode:
            study_lang, native_lang = mode.split('-')
        else:
            study_lang, native_lang = 'en', 'ru'
        
        # Если режим совпадает с направлением слова в словаре
        if study_lang == self.current_word['language'] and native_lang == self.current_word['native_language']:
            # Правильный ответ - перевод
            correct = self.current_word['translation'].lower()
        else:
            # Правильный ответ - иностранное слово
            correct = self.current_word['foreign'].lower()
        
        user = user_answer.lower()
        
        # Проверяем правильность
        is_correct = user == correct
        
        # Обновляем статистику слова
        if is_correct:
            self.current_word['correct_count'] += 1
            self.current_word['difficulty'] = min(100, self.current_word['difficulty'] + 5)
            self.daily_stats['correct_today'] += 1
        else:
            self.current_word['incorrect_count'] += 1
            self.current_word['difficulty'] = max(0, self.current_word['difficulty'] - 10)
        
        self.current_word['review_count'] += 1
        self.current_word['last_review'] = str(datetime.now())
        
        # Сохраняем изменения
        self.save_vocabulary()
        self.save_stats()
        
        return is_correct, correct
    
    def get_stats(self):
        """
        Возвращает статистику
        
        Returns:
            dict: Статистика
        """
        total_words = len(self.vocabulary)
        
        # Подсчитываем изученные слова (сложность > 80)
        learned_words = len([w for w in self.vocabulary if w['difficulty'] >= 80])
        
        # Подсчитываем сложные слова (сложность < 50)
        hard_words = len([w for w in self.vocabulary if w['difficulty'] <= 50])
        
        # Прогресс (процент изученных слов)
        progress = (learned_words / total_words * 100) if total_words > 0 else 0
        
        return {
            'total_words': total_words,
            'learned_words': learned_words,
            'hard_words': hard_words,
            'progress': progress,
            'daily_words': self.daily_stats['words_today'],
            'correct_today': self.daily_stats['correct_today'],
            'accuracy_today': (self.daily_stats['correct_today'] / self.daily_stats['words_today'] * 100) if self.daily_stats['words_today'] > 0 else 0
        }
    
    def get_word_display(self, word, mode='en-ru', display_language=None):
        """
        Возвращает слово для отображения
    
        Args:
            word: Слово из словаря
            mode: Режим тренировки
            display_language: Язык для отображения (если None, определяется из режима)
        
        Returns:
            str: Слово для отображения
        """
        if '-' in mode:
            study_lang, native_lang = mode.split('-')
        else:
            study_lang, native_lang = 'en', 'ru'
    
        # Если задан язык отображения, используем его
        if display_language:
            if word['language'] == display_language:
                return word['foreign']
            elif word['native_language'] == display_language:
                return word['translation']
    
        # Старая логика для обратной совместимости
        # Если режим совпадает с направлением слова в словаре
        if study_lang == word['language'] and native_lang == word['native_language']:
            return word['foreign']  # Показываем иностранное слово
        # Если режим обратный направлению слова в словаре
        elif study_lang == word['native_language'] and native_lang == word['language']:
            return word['translation']  # Показываем перевод
        else:
            # По умолчанию показываем иностранное слово
            return word['foreign']
    
    def get_display_word(self, word):
        """
        Возвращает отображаемое слово
        
        Args:
            word: Слово из словаря
            
        Returns:
            str: Слово для отображения
        """
        return word['foreign']
    
    def get_display_translation(self, word):
        """
        Возвращает отображаемый перевод
        
        Args:
            word: Слово из словаря
            
        Returns:
            str: Перевод для отображения
        """
        return word['translation']
    
    def get_all_words(self):
        """
        Возвращает все слова
        
        Returns:
            list: Все слова словаря
        """
        return self.vocabulary.copy()
    
    def get_words_by_language(self, language, native_language):
        """
        Возвращает слова по языку
        
        Args:
            language: Язык слова
            native_language: Родной язык
            
        Returns:
            list: Слова указанного языка
        """
        return [word for word in self.vocabulary 
                if word['language'] == language and word['native_language'] == native_language]
    
    def get_words_for_mode(self, mode):
        """
        Возвращает слова для режима тренировки
        
        Args:
            mode: Режим тренировки ('en-ru', 'ru-en', etc.)
            
        Returns:
            list: Слова для режима
        """
        if '-' in mode:
            study_lang, native_lang = mode.split('-')
            # Ищем слова в обеих комбинациях языков
            return [
                word for word in self.vocabulary 
                if (word['language'] == study_lang and word['native_language'] == native_lang) or
                   (word['language'] == native_lang and word['native_language'] == study_lang)
            ]
        return []
    
    def get_hard_words(self, threshold=50):
        """
        Возвращает сложные слова
        
        Args:
            threshold: Порог сложности
            
        Returns:
            list: Сложные слова
        """
        return [word for word in self.vocabulary if word['difficulty'] <= threshold]
