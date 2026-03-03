"""
Модель словаря
"""

import json
import os
import random
import time
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
        self.stats_history = []  # История всех дней
        self.daily_stats = {
            'date': str(date.today()),
            'words_today': 0,
            'correct_today': 0,
            'time_spent': 0  # Время в секундах
        }
        self.session_start_time = time.time()  # Время начала сессии
        self.load_stats()
    
    def load_vocabulary(self):
        """Загружает словарь из JSON файла"""
        file_path = os.path.join(config.PATHS['data'], config.FILES['vocabulary'])
        
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.vocabulary = json.load(f)
                
                # Добавляем поле category для старых слов, если его нет
                for word in self.vocabulary:
                    if 'category' not in word:
                        word['category'] = "Основные"
                    # Добавляем поле image для старых слов, если его нет
                    if 'image' not in word:
                        word['image'] = None
                
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
                    data = json.load(f)
                
                # Новая структура: словарь с историей
                if isinstance(data, dict) and 'history' in data:
                    self.stats_history = data.get('history', [])
                    
                    # Находим статистику за сегодня
                    today = str(date.today())
                    today_stats = None
                    for day in self.stats_history:
                        if day.get('date') == today:
                            today_stats = day
                            break
                    
                    if today_stats:
                        self.daily_stats = today_stats
                    else:
                        # Новый день - создаем запись
                        self.daily_stats = {
                            'date': today,
                            'words_today': 0,
                            'correct_today': 0,
                            'time_spent': 0
                        }
                else:
                    # Старая структура (один объект) - конвертируем
                    if data.get('date') == str(date.today()):
                        self.daily_stats = {
                            'date': data['date'],
                            'words_today': data.get('words_today', 0),
                            'correct_today': data.get('correct_today', 0),
                            'time_spent': 0
                        }
                        self.stats_history = [self.daily_stats.copy()]
                    else:
                        # Другой день - создаем новую запись
                        self.daily_stats = {
                            'date': str(date.today()),
                            'words_today': 0,
                            'correct_today': 0,
                            'time_spent': 0
                        }
                        # Сохраняем старую запись в историю
                        if data:
                            old_stats = {
                                'date': data['date'],
                                'words_today': data.get('words_today', 0),
                                'correct_today': data.get('correct_today', 0),
                                'time_spent': 0
                            }
                            self.stats_history = [old_stats, self.daily_stats.copy()]
            else:
                # Файла нет - создаем новую статистику
                self.stats_history = []
                self.daily_stats = {
                    'date': str(date.today()),
                    'words_today': 0,
                    'correct_today': 0,
                    'time_spent': 0
                }
        except Exception as e:
            print(f"Ошибка загрузки статистики: {e}")
            self.stats_history = []
            self.daily_stats = {
                'date': str(date.today()),
                'words_today': 0,
                'correct_today': 0,
                'time_spent': 0
            }
    
    def save_stats(self):
        """Сохраняет статистику"""
        try:
            file_path = os.path.join(config.PATHS['data'], 'stats.json')
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Обновляем время в текущей сессии
            current_time = time.time()
            session_duration = int(current_time - self.session_start_time)
            self.daily_stats['time_spent'] += session_duration
            self.session_start_time = current_time  # Сбрасываем для следующего замера
            
            # Обновляем или добавляем запись за сегодня в истории
            today = str(date.today())
            found = False
            for i, day in enumerate(self.stats_history):
                if day.get('date') == today:
                    self.stats_history[i] = self.daily_stats.copy()
                    found = True
                    break
            
            if not found:
                self.stats_history.append(self.daily_stats.copy())
            
            # Сортируем историю по дате (от новых к старым)
            self.stats_history.sort(key=lambda x: x.get('date', ''), reverse=True)
            
            # Сохраняем всю историю
            data = {
                'history': self.stats_history,
                'current': self.daily_stats
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            print(f"Статистика сохранена: {len(self.stats_history)} дней")
        except Exception as e:
            print(f"Ошибка сохранения статистики: {e}")
    
    # ========== ИЗМЕНЕНИЕ: добавлен параметр image ==========
    def add_word(self, foreign, translation, language='en', native_language='ru', category="Основные", image=None):
        """
        Добавляет новое слово в словарь
        
        Args:
            foreign: Иностранное слово
            translation: Перевод
            language: Язык иностранного слова
            native_language: Родной язык
            category: Категория слова
            image: Имя файла картинки (опционально)
            
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
            'category': category,
            'image': image,  # ← НОВОЕ ПОЛЕ
            'added_date': str(date.today()),
            'last_review': None,
            'review_count': 0,
            'correct_count': 0,
            'incorrect_count': 0,
            'difficulty': 50
        }
        
        self.vocabulary.append(new_word)
        self.save_vocabulary()
        return True
    # ========== КОНЕЦ ИЗМЕНЕНИЯ ==========
    
    def get_random_word(self, difficulty='all', language='en', native_language='ru', prevent_repeats=True, category=None):
        """
        Получает случайное слово
        
        Args:
            difficulty: Уровень сложности ('all', 'easy', 'medium', 'hard')
            language: Язык слова
            native_language: Родной язык
            prevent_repeats: Предотвращать повторения
            category: Категория (если None - все категории)
            
        Returns:
            dict: Случайное слово или None
        """
        # Фильтруем слова по языку - учитываем оба направления
        filtered_words = [
            word for word in self.vocabulary 
            if word['language'] == language and word['native_language'] == native_language
        ]
        
        if not filtered_words:
            return None
        
        # Фильтр по категории (если указана)
        if category:
            filtered_words = [w for w in filtered_words if w.get('category', "Основные") == category]
        
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
            if category:
                filtered_words = [w for w in filtered_words if w.get('category', "Основные") == category]
        
        if not filtered_words:
            return None
        
        # Если нужно предотвратить повторения, убираем текущее слово
        if prevent_repeats and self.current_word:
            # Создаем новый список без текущего слова
            temp_words = [w for w in filtered_words if w != self.current_word]
            if temp_words:
                filtered_words = temp_words
        
        try:
            self.current_word = random.choice(filtered_words)
            return self.current_word
        except IndexError:
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
        
        self.daily_stats['words_today'] += 1
        
        if '-' in mode:
            study_lang, native_lang = mode.split('-')
        else:
            study_lang, native_lang = 'en', 'ru'
        
        if study_lang == self.current_word['language'] and native_lang == self.current_word['native_language']:
            correct = self.current_word['translation'].lower()
        else:
            correct = self.current_word['foreign'].lower()
        
        user = user_answer.lower()
        is_correct = user == correct
        
        if is_correct:
            self.current_word['correct_count'] += 1
            self.current_word['difficulty'] = min(100, self.current_word['difficulty'] + 5)
            self.daily_stats['correct_today'] += 1
        else:
            self.current_word['incorrect_count'] += 1
            self.current_word['difficulty'] = max(0, self.current_word['difficulty'] - 10)
        
        self.current_word['review_count'] += 1
        self.current_word['last_review'] = str(datetime.now())
        
        self.save_vocabulary()
        self.save_stats()
        
        return is_correct, correct
    
    def get_stats(self):
        """
        Возвращает статистику для текущего дня
        
        Returns:
            dict: Статистика
        """
        total_words = len(self.vocabulary)
        learned_words = len([w for w in self.vocabulary if w['difficulty'] >= 80])
        hard_words = len([w for w in self.vocabulary if w['difficulty'] <= 50])
        progress = (learned_words / total_words * 100) if total_words > 0 else 0
        
        # Форматируем время
        hours = self.daily_stats['time_spent'] // 3600
        minutes = (self.daily_stats['time_spent'] % 3600) // 60
        seconds = self.daily_stats['time_spent'] % 60
        
        if hours > 0:
            time_str = f"{hours}ч {minutes}м"
        elif minutes > 0:
            time_str = f"{minutes}м {seconds}с"
        else:
            time_str = f"{seconds}с"
        
        return {
            'total_words': total_words,
            'learned_words': learned_words,
            'hard_words': hard_words,
            'progress': progress,
            'daily_words': self.daily_stats['words_today'],
            'correct_today': self.daily_stats['correct_today'],
            'accuracy_today': (self.daily_stats['correct_today'] / self.daily_stats['words_today'] * 100) if self.daily_stats['words_today'] > 0 else 0,
            'time_spent': self.daily_stats['time_spent'],
            'time_spent_str': time_str
        }
    
    def get_stats_history(self):
        """
        Возвращает всю историю статистики
        
        Returns:
            list: История статистики по дням
        """
        return self.stats_history.copy()
    
    def get_total_stats(self):
        """
        Возвращает суммарную статистику за все время
        
        Returns:
            dict: Суммарная статистика
        """
        total_words_all_time = 0
        total_correct_all_time = 0
        total_time_all_time = 0
        
        for day in self.stats_history:
            total_words_all_time += day.get('words_today', 0)
            total_correct_all_time += day.get('correct_today', 0)
            total_time_all_time += day.get('time_spent', 0)
        
        # Добавляем текущий день
        total_words_all_time += self.daily_stats['words_today']
        total_correct_all_time += self.daily_stats['correct_today']
        total_time_all_time += self.daily_stats['time_spent']
        
        accuracy = (total_correct_all_time / total_words_all_time * 100) if total_words_all_time > 0 else 0
        
        # Форматируем время
        hours = total_time_all_time // 3600
        minutes = (total_time_all_time % 3600) // 60
        
        return {
            'total_words': total_words_all_time,
            'total_correct': total_correct_all_time,
            'accuracy': accuracy,
            'total_time': total_time_all_time,
            'total_time_str': f"{hours}ч {minutes}м",
            'days_count': len(self.stats_history) + (1 if self.daily_stats['words_today'] > 0 else 0)
        }
    
    def get_word_display(self, word, mode='en-ru', display_language=None):
        if '-' in mode:
            study_lang, native_lang = mode.split('-')
        else:
            study_lang, native_lang = 'en', 'ru'
    
        if display_language:
            if word['language'] == display_language:
                return word['foreign']
            elif word['native_language'] == display_language:
                return word['translation']
    
        if study_lang == word['language'] and native_lang == word['native_language']:
            return word['foreign']
        elif study_lang == word['native_language'] and native_lang == word['language']:
            return word['translation']
        else:
            return word['foreign']
    
    def get_display_word(self, word):
        return word['foreign']
    
    def get_display_translation(self, word):
        return word['translation']
    
    def get_all_words(self):
        """
        Возвращает все слова
        
        Returns:
            list: Все слова словаря
        """
        return self.vocabulary.copy()
    
    def get_words_by_language(self, language, native_language):
        return [word for word in self.vocabulary 
                if word['language'] == language and word['native_language'] == native_language]
    
    def get_words_for_mode(self, mode):
        if '-' in mode:
            study_lang, native_lang = mode.split('-')
            return [
                word for word in self.vocabulary 
                if (word['language'] == study_lang and word['native_language'] == native_lang) or
                   (word['language'] == native_lang and word['native_language'] == study_lang)
            ]
        return []
    
    def get_hard_words(self, threshold=50):
        return [word for word in self.vocabulary if word['difficulty'] <= threshold]
    
    def get_all_categories(self):
        """Возвращает список всех уникальных категорий"""
        categories = set()
        for word in self.vocabulary:
            cat = word.get('category', "Основные")
            categories.add(cat)
        return sorted(list(categories))
