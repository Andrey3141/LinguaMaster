"""
Модуль для озвучки слов через Edge-TTS (Microsoft Neural TTS)
с возможностью выбора альтернативных голосов из RHVoice
"""

import asyncio
import threading
import os
import tempfile
import subprocess
import pygame
import edge_tts
import json
from config import config
from utils.settings_manager import settings_manager  # Добавляем импорт

class SpeechSynthesizer:
    """Класс для синтеза речи через Edge-TTS с поддержкой RHVoice как альтернативы"""
    
    # Все голоса Edge-TTS для всех языков (Microsoft Neural Voices)
    EDGE_VOICES = {
        'ru': 'ru-RU-DariyaNeural',      # Русский (Дарья) - женский
        'en': 'en-US-JennyNeural',        # Английский (Дженни) - женский
        'es': 'es-ES-ElviraNeural',       # Испанский (Эльвира) - женский
        'fr': 'fr-FR-DeniseNeural',       # Французский (Дениз) - женский
        'de': 'de-DE-KatjaNeural',        # Немецкий (Катя) - женский
        'zh': 'zh-CN-XiaoxiaoNeural',     # Китайский (Сяосяо) - женский
        'ja': 'ja-JP-NanamiNeural',       # Японский (Нанами) - женский
        'ko': 'ko-KR-SunHiNeural',        # Корейский (Сон Хи) - женский
        'pt': 'pt-BR-FranciscaNeural',    # Португальский (Франсиска) - женский
        'it': 'it-IT-ElsaNeural',         # Итальянский (Эльза) - женский
        'ar': 'ar-EG-SalmaNeural',        # Арабский (Сальма) - женский
    }
    
    # Мужские голоса Edge-TTS
    EDGE_VOICES_MALE = {
        'ru': 'ru-RU-MikhailNeural',      # Русский (Михаил) - мужской
        'en': 'en-US-GuyNeural',           # Английский (Гай) - мужской
        'es': 'es-ES-AlvaroNeural',        # Испанский (Альваро) - мужской
        'fr': 'fr-FR-HenriNeural',         # Французский (Анри) - мужской
        'de': 'de-DE-ConradNeural',        # Немецкий (Конрад) - мужской
        'zh': 'zh-CN-YunxiNeural',         # Китайский (Юньси) - мужской
        'ja': 'ja-JP-KeitaNeural',         # Японский (Кейта) - мужской
        'ko': 'ko-KR-InJoonNeural',        # Корейский (Ин Джун) - мужской
        'pt': 'pt-BR-AntonioNeural',       # Португальский (Антонио) - мужской
        'it': 'it-IT-DiegoNeural',         # Итальянский (Диего) - мужской
        'ar': 'ar-EG-ShakirNeural',        # Арабский (Шакир) - мужской
    }
    
    def __init__(self):
        """Инициализация синтезатора"""
        self.is_speaking = False
        self.volume = config.SPEECH_SETTINGS['volume']
        self.speed = config.SPEECH_SETTINGS['speed']
        self.enabled = config.SPEECH_SETTINGS['enabled']
        self.current_process = None
        self.lock = threading.Lock()
        self.cache_dir = os.path.expanduser('~/.cache/edge-tts')
        
        # Создаем папку для данных, если её нет
        os.makedirs(config.PATHS['data'], exist_ok=True)
        
        # Загружаем настройки голосов из app_settings.json
        self.selected_voices = self._load_voice_settings()
        
        # Создаем папку для кэша Edge-TTS
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Инициализация pygame для воспроизведения
        try:
            pygame.mixer.init()
            self.audio_available = True
        except Exception as e:
            print(f"Ошибка инициализации аудио: {e}")
            self.audio_available = False
        
        # Проверяем доступность Edge-TTS
        self.edge_available = self._check_edge_tts()
        
        # Проверяем доступность RHVoice (как альтернатива)
        self.rhvoice_available = self._check_rhvoice()
        if self.rhvoice_available:
            self._get_available_rhvoice_voices()
        
        if self.edge_available:
            print("✅ Edge-TTS доступен")
        
        if self.rhvoice_available:
            print("✅ RHVoice доступен")
    
    def _load_voice_settings(self):
        """Загружает настройки голосов из app_settings.json"""
        # Значения по умолчанию
        default_voices = {
            'ru': 'anna',  # RHVoice для русского
            'en': self.EDGE_VOICES['en'],
            'es': self.EDGE_VOICES['es'],
            'fr': self.EDGE_VOICES['fr'],
            'de': self.EDGE_VOICES['de'],
            'zh': self.EDGE_VOICES['zh'],
            'ja': self.EDGE_VOICES['ja'],
            'ko': self.EDGE_VOICES['ko'],
            'pt': self.EDGE_VOICES['pt'],
            'it': self.EDGE_VOICES['it'],
            'ar': self.EDGE_VOICES['ar'],
        }
        
        try:
            # Загружаем из общего менеджера настроек
            all_settings = settings_manager.get_all()
            app_settings = all_settings.get('app_settings', {})
            saved_voices = app_settings.get('selected_voices', {})
            
            if saved_voices:
                print(f"✅ Загружены настройки голосов из app_settings.json")
                # Обновляем значения по умолчанию сохраненными
                for lang, voice in saved_voices.items():
                    if lang in default_voices:
                        default_voices[lang] = voice
            else:
                print(f"ℹ️ Настройки голосов не найдены, используются значения по умолчанию")
        except Exception as e:
            print(f"❌ Ошибка загрузки настроек голосов: {e}")
        
        return default_voices
    
    def _save_voice_settings(self):
        """Сохраняет настройки голосов в app_settings.json"""
        try:
            # Получаем текущие настройки
            all_settings = settings_manager.get_all()
            
            # Обновляем или создаем app_settings
            if 'app_settings' not in all_settings:
                all_settings['app_settings'] = {}
            
            all_settings['app_settings']['selected_voices'] = self.selected_voices.copy()
            
            # Сохраняем через менеджер настроек
            settings_manager.save_settings(all_settings)
            return True
        except Exception as e:
            print(f"❌ Ошибка сохранения настроек голосов: {e}")
            return False
    
    def _check_edge_tts(self):
        """Проверяет доступность edge-tts"""
        try:
            import edge_tts
            return True
        except ImportError:
            return False
    
    def _check_rhvoice(self):
        """Проверяет доступность RHVoice"""
        try:
            result = subprocess.run(
                ['which', 'RHVoice-test'],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except:
            return False
    
    def _get_available_rhvoice_voices(self):
        """Получает список доступных голосов RHVoice"""
        self.available_rhvoice_voices = []
        try:
            voice_paths = [
                '/usr/share/RHVoice/voices',
                '/usr/local/share/RHVoice/voices',
                os.path.expanduser('~/.local/share/RHVoice/voices')
            ]
            
            for path in voice_paths:
                if os.path.exists(path):
                    for item in os.listdir(path):
                        if not item.startswith('.'):
                            self.available_rhvoice_voices.append(item)
            
            # Если не нашли, используем список из системы
            if not self.available_rhvoice_voices:
                self.available_rhvoice_voices = [
                    'anna', 'irina', 'elena', 'aleksandr', 'mikhail', 'yuriy',
                    'victoria', 'bdl', 'slt', 'evgeniy-eng', 'alan', 'maria', 'celia'
                ]
        except Exception as e:
            print(f"Ошибка получения голосов RHVoice: {e}")
            self.available_rhvoice_voices = []
    
    def is_available(self):
        """Проверяет доступность TTS"""
        return (self.edge_available or self.rhvoice_available) and self.audio_available
    
    def is_rhvoice_voice(self, voice_name):
        """Проверяет, является ли голос голосом RHVoice"""
        return voice_name in self.available_rhvoice_voices
    
    def get_all_voices_for_language(self, language_code):
        """Возвращает ВСЕ доступные голоса для языка (Edge + RHVoice)"""
        voices = []
        
        # Добавляем Edge-TTS голоса
        female = self.EDGE_VOICES.get(language_code)
        male = self.EDGE_VOICES_MALE.get(language_code)
        if female:
            voices.append(f"🌐 {female}")
        if male:
            voices.append(f"🌐 {male}")
        
        # Добавляем RHVoice голоса, если они доступны
        if self.rhvoice_available:
            # Маппинг языков для RHVoice
            rhvoice_map = {
                'ru': ['anna', 'irina', 'elena', 'aleksandr', 'mikhail', 'yuriy'],
                'en': ['slt', 'bdl', 'clb', 'evgeniy-eng', 'alan'],
                'es': ['maria', 'elena', 'anna'],
                'fr': ['celia', 'maria', 'anna'],
                'de': ['yuriy', 'anna', 'mikhail'],
                'pt': ['maria', 'elena'],
                'it': ['aleksandr', 'anna'],
                'zh': [],
                'ja': [],
                'ko': [],
                'ar': [],
            }
            
            candidates = rhvoice_map.get(language_code, [])
            for voice in candidates:
                if voice in self.available_rhvoice_voices:
                    voices.append(f"🎤 {voice}")
        
        return voices
    
    def get_default_voice_for_language(self, language_code):
        """Возвращает голос по умолчанию для языка"""
        # Проверяем сохраненные настройки
        if language_code in self.selected_voices:
            return self.selected_voices[language_code]
        
        # Иначе возвращаем предустановленный по умолчанию
        if language_code == 'ru':
            return 'anna'
        else:
            return self.EDGE_VOICES.get(language_code)
    
    def set_voice_for_language(self, language_code, voice_name):
        """Устанавливает голос для языка"""
        # Убираем префикс, если он есть
        clean_voice = voice_name
        if voice_name.startswith("🌐 "):
            clean_voice = voice_name[2:]
        elif voice_name.startswith("🎤 "):
            clean_voice = voice_name[2:]
        
        self.selected_voices[language_code] = clean_voice
        # Сохраняем в app_settings.json
        self._save_voice_settings()
        return True
    
    def stop_current(self):
        """Останавливает текущее произношение"""
        with self.lock:
            if self.audio_available:
                pygame.mixer.music.stop()
            if self.current_process:
                try:
                    self.current_process.terminate()
                except:
                    pass
            self.is_speaking = False
    
    def test_voice(self, voice_name, text=None):
        """Тестирует голос"""
        # Извлекаем чистое имя голоса без префикса
        clean_voice = voice_name
        if voice_name.startswith("🌐 "):
            clean_voice = voice_name[2:]
        elif voice_name.startswith("🎤 "):
            clean_voice = voice_name[2:]
        
        # Определяем язык по голосу
        lang_code = None
        for lang, voice in self.EDGE_VOICES.items():
            if voice == clean_voice:
                lang_code = lang
                break
        if not lang_code:
            for lang, voice in self.EDGE_VOICES_MALE.items():
                if voice == clean_voice:
                    lang_code = lang
                    break
        
        if not lang_code:
            # Если это RHVoice голос
            for lang, voices in {
                'ru': ['anna', 'irina', 'elena', 'aleksandr', 'mikhail', 'yuriy'],
                'en': ['slt', 'bdl', 'clb', 'evgeniy-eng', 'alan'],
                'es': ['maria', 'elena', 'anna'],
                'fr': ['celia', 'maria', 'anna'],
                'de': ['yuriy', 'anna', 'mikhail'],
                'pt': ['maria', 'elena'],
                'it': ['aleksandr', 'anna'],
            }.items():
                if clean_voice in voices:
                    lang_code = lang
                    break
        
        if not lang_code:
            lang_code = 'ru'
        
        if not text:
            # Тестовые тексты для разных языков
            test_texts = {
                'ru': "Это тестовое предложение на русском языке",
                'en': "This is a test sentence in English",
                'es': "Esta es una frase de prueba en español",
                'fr': "Ceci est une phrase de test en français",
                'zh': "这是一个中文测试句子",
                'ja': "これは日本語のテスト文です",
                'ko': "이것은 한국어 테스트 문장입니다",
                'ar': "هذه جملة اختبار باللغة العربية"
            }
            text = test_texts.get(lang_code, "Test sentence")
        
        self.speak(text, lang_code, clean_voice)
        return True
    
    def set_enabled(self, enabled):
        """Включает/отключает озвучку"""
        self.enabled = enabled
        if not enabled:
            self.stop_current()
    
    def speak(self, text, language=None, forced_voice=None, callback=None):
        """Произносит текст"""
        if not self.enabled or not text or not self.audio_available:
            if callback:
                callback(False)
            return
        
        self.stop_current()
        
        if language is None:
            language = 'ru'
        
        thread = threading.Thread(
            target=self._speak_thread,
            args=(text, language, forced_voice, callback),
            daemon=True
        )
        thread.start()
    
    def _speak_edge(self, text, voice, language, callback):
        """Синтез через Edge-TTS"""
        try:
            # Создаем временный файл
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as tmp_file:
                tmp_path = tmp_file.name
            
            # Запускаем асинхронный синтез
            async def generate():
                communicate = edge_tts.Communicate(text, voice)
                await communicate.save(tmp_path)
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(generate())
            loop.close()
            
            # Проверяем, что файл создался и не пустой
            if os.path.exists(tmp_path) and os.path.getsize(tmp_path) > 0:
                # Воспроизводим
                pygame.mixer.music.load(tmp_path)
                pygame.mixer.music.set_volume(self.volume / 100.0)
                pygame.mixer.music.play()
                
                # Ждем окончания
                while pygame.mixer.music.get_busy():
                    threading.Event().wait(0.1)
            else:
                print(f"❌ Ошибка: не удалось создать аудиофайл для голоса {voice}")
                # Пробуем альтернативный голос для русского (RHVoice)
                if language == 'ru' and voice in self.EDGE_VOICES.values():
                    print("🔄 Пробуем использовать RHVoice для русского...")
                    self._speak_rhvoice(text, 'anna', callback)
                    return
            
            # Удаляем временный файл
            try:
                os.unlink(tmp_path)
            except:
                pass
            
            if callback:
                callback(True)
                    
        except Exception as e:
            print(f"❌ Ошибка Edge-TTS: {e}")
            # Если ошибка с русским голосом, пробуем RHVoice
            if language == 'ru' and (voice in self.EDGE_VOICES.values() or voice in self.EDGE_VOICES_MALE.values()):
                print("🔄 Пробуем использовать RHVoice для русского...")
                self._speak_rhvoice(text, 'anna', callback)
            else:
                if callback:
                    callback(False)
    
    def _speak_rhvoice(self, text, voice, callback):
        """Синтез через RHVoice"""
        try:
            speed_percent = int(self.speed * 100)
            volume_percent = self.volume
            
            cmd = [
                'RHVoice-test',
                '-p', voice,
                '-r', str(speed_percent),
                '-v', str(volume_percent),
            ]
            
            self.current_process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            self.current_process.communicate(input=text)
            
            if callback:
                callback(True)
                
        except Exception as e:
            print(f"❌ Ошибка RHVoice: {e}")
            if callback:
                callback(False)
    
    def _speak_thread(self, text, language, forced_voice, callback):
        """Поток для синтеза речи"""
        with self.lock:
            self.is_speaking = True
        
        try:
            # Определяем какой голос использовать
            if forced_voice:
                voice = forced_voice
            else:
                voice = self.get_default_voice_for_language(language)
            
            if not voice:
                if callback:
                    callback(False)
                return
            
            # Определяем движок по голосу
            is_rhvoice = voice in self.available_rhvoice_voices
            
            if is_rhvoice and self.rhvoice_available:
                self._speak_rhvoice(text, voice, callback)
            elif self.edge_available:
                self._speak_edge(text, voice, language, callback)
            else:
                print(f"❌ Нет доступного движка для голоса {voice}")
                if callback:
                    callback(False)
        finally:
            with self.lock:
                self.is_speaking = False
                self.current_process = None
    
    def speak_async(self, text, language=None, callback=None):
        """Асинхронная озвучка с callback (использует голос по умолчанию)"""
        self.speak(text, language, None, callback)
    
    def set_volume(self, volume):
        """Устанавливает громкость"""
        self.volume = max(0, min(100, volume))
        if self.audio_available:
            pygame.mixer.music.set_volume(self.volume / 100.0)
    
    def set_speed(self, speed):
        """Устанавливает скорость речи"""
        self.speed = max(0.5, min(2.0, speed))
        
    # ===== НОВЫЙ МЕТОД: save_settings =====
    def save_settings(self):
        """Сохраняет настройки голосов (для вызова из voice_settings_dialog)"""
        return self._save_voice_settings()
    # ===== КОНЕЦ НОВОГО МЕТОДА =====

# Глобальный экземпляр синтезатора
speech_synth = SpeechSynthesizer()
