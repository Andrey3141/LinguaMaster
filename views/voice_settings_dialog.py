"""
Диалог выбора голосов для каждого языка
"""

import tkinter as tk
from tkinter import ttk
from config import config
from utils.speech import speech_synth
from utils.notifications import show_notification

class VoiceSettingsDialog:
    """Класс для выбора голосов для каждого языка"""
    
    @staticmethod
    def show_dialog(controller):
        """Показывает диалог выбора голосов"""
        if controller.is_dialog_open('voice_settings'):
            controller.dialogs['voice_settings'].lift()
            controller.dialogs['voice_settings'].focus_set()
            return
        
        dialog = tk.Toplevel(controller.root)
        dialog.title("🎤 Настройка голосов")
        dialog.geometry("550x600")  # Уменьшена ширина
        dialog.configure(bg=config.COLORS['bg_dark'])
        dialog.transient(controller.root)
        
        dialog.grab_set()
        dialog.focus_set()
        dialog.lift()
        
        controller.register_dialog('voice_settings', dialog)
        
        def on_closing():
            controller.unregister_dialog('voice_settings')
            dialog.grab_release()
            dialog.destroy()
        
        dialog.protocol("WM_DELETE_WINDOW", on_closing)
        controller._center_dialog(dialog)
        
        main_frame = tk.Frame(dialog, bg=config.COLORS['bg_dark'], padx=15, pady=15)  # Уменьшены отступы
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Заголовок
        tk.Label(
            main_frame,
            text="🎤 Выбор голосов",
            font=('Segoe UI', 14, 'bold'),
            bg=config.COLORS['bg_dark'],
            fg=config.COLORS['text']
        ).pack(pady=(0, 10))
        
        # Информация о движках
        info_frame = tk.Frame(main_frame, bg=config.COLORS['bg_card'], padx=8, pady=8)
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(
            info_frame,
            text="🌐 Edge-TTS (основной) | 🎤 RHVoice (альтернатива)",
            font=('Segoe UI', 9),
            bg=config.COLORS['bg_card'],
            fg=config.COLORS['text_secondary']
        ).pack(anchor='w')
        
        # Фрейм для прокрутки
        canvas_frame = tk.Frame(main_frame, bg=config.COLORS['bg_dark'])
        canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        canvas = tk.Canvas(canvas_frame, bg=config.COLORS['bg_dark'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        
        scrollable_frame = tk.Frame(canvas, bg=config.COLORS['bg_dark'])
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Словарь для хранения переменных выбора голосов
        voice_vars = {}
        
        # Тестовые предложения
        test_texts = {
            'ru': "Это тестовое предложение",
            'en': "This is a test sentence",
            'es': "Frase de prueba",
            'fr': "Phrase de test",
            'de': "Testsatz",
            'zh': "测试句子",
            'ja': "テスト文",
            'ko': "테스트 문장",
            'pt': "Frase de teste",
            'it': "Frase di prova",
            'ar': "جملة اختبار"
        }
        
        # Создаем секции для каждого языка
        for lang_code, lang_info in config.LANGUAGES.items():
            # Контейнер для языка
            lang_container = tk.Frame(scrollable_frame, bg=config.COLORS['bg_dark'])
            lang_container.pack(fill=tk.X, pady=2)
            
            # Заголовок языка
            tk.Label(
                lang_container,
                text=f"{lang_info['flag']} {lang_info['name']}",
                font=('Segoe UI', 10, 'bold'),
                bg=config.COLORS['bg_dark'],
                fg=config.COLORS['text']
            ).pack(anchor='w')
            
            # Получаем ВСЕ доступные голоса для языка
            all_voices = speech_synth.get_all_voices_for_language(lang_code)
            default_voice = speech_synth.get_default_voice_for_language(lang_code)
            
            # Форматируем голос по умолчанию
            default_display = None
            if default_voice:
                if default_voice in speech_synth.EDGE_VOICES.values() or default_voice in speech_synth.EDGE_VOICES_MALE.values():
                    default_display = f"🌐 {default_voice}"
                else:
                    default_display = f"🎤 {default_voice}"
            
            if not all_voices:
                tk.Label(
                    lang_container,
                    text="❌ Нет голосов",
                    font=('Segoe UI', 9),
                    bg=config.COLORS['bg_dark'],
                    fg=config.COLORS['danger']
                ).pack(anchor='w')
                continue
            
            # Фрейм для выбора голоса
            voice_frame = tk.Frame(lang_container, bg=config.COLORS['bg_dark'])
            voice_frame.pack(fill=tk.X, pady=2)
            
            # Переменная для выбранного голоса
            voice_var = tk.StringVar(value=default_display if default_display in all_voices else all_voices[0])
            voice_vars[lang_code] = voice_var
            
            # Выпадающий список голосов (уменьшенная ширина)
            voice_combo = ttk.Combobox(
                voice_frame,
                textvariable=voice_var,
                values=all_voices,
                state='readonly',
                width=35  # Уменьшено с 45 до 35
            )
            voice_combo.pack(side=tk.LEFT, padx=(0, 5))
            
            # Кнопка тестирования
            test_text = test_texts.get(lang_code, "Test")
            
            def create_test_callback(v, text):
                return lambda: speech_synth.test_voice(v, text)
            
            test_btn = tk.Button(
                voice_frame,
                text="▶",
                font=('Segoe UI', 9),
                bg=config.COLORS['secondary'],
                fg=config.COLORS['text'],
                bd=0,
                width=3,  # Фиксированная ширина
                cursor='hand2',
                command=create_test_callback(voice_var.get(), test_text)
            )
            test_btn.pack(side=tk.LEFT)
            
            def on_voice_change(*args, btn=test_btn, var=voice_var, txt=test_text):
                btn.config(command=create_test_callback(var.get(), txt))
            
            voice_var.trace_add('write', on_voice_change)
        
        # Кнопки внизу
        button_frame = tk.Frame(main_frame, bg=config.COLORS['bg_dark'])
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        def save_voices():
            """Сохраняет выбранные голоса"""
            for lang_code, var in voice_vars.items():
                speech_synth.set_voice_for_language(lang_code, var.get())
            speech_synth.save_settings()
            show_notification(
                dialog,
                "Настройки сохранены",
                "Выбранные голоса сохранены",
                "success"
            )
        
        def save_and_close():
            save_voices()
            on_closing()
        
        button_center_frame = tk.Frame(button_frame, bg=config.COLORS['bg_dark'])
        button_center_frame.pack()
        
        tk.Button(
            button_center_frame,
            text="💾 Сохранить",
            font=('Segoe UI', 11),
            bg=config.COLORS['primary'],
            fg=config.COLORS['text'],
            bd=0,
            padx=20,
            pady=6,
            cursor='hand2',
            command=save_and_close
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Button(
            button_center_frame,
            text="❌ Отмена",
            font=('Segoe UI', 11),
            bg=config.COLORS['bg_card'],
            fg=config.COLORS['text_secondary'],
            bd=0,
            padx=20,
            pady=6,
            cursor='hand2',
            command=on_closing
        ).pack(side=tk.LEFT)
