"""
Диалог настроек приложения
"""

import tkinter as tk
from tkinter import ttk
from config import config
from utils.speech import speech_synth
from utils.notifications import show_notification
from ..voice_settings_dialog import VoiceSettingsDialog

class SettingsDialog:
    """Класс диалога настроек"""
    
    @staticmethod
    def show(controller):
        """Показывает диалог настроек"""
        if controller.is_dialog_open('settings'):
            controller.dialogs['settings'].lift()
            controller.dialogs['settings'].focus_set()
            return
        
        dialog = tk.Toplevel(controller.root)
        dialog.title("⚙️ Настройки")
        dialog.geometry(config.WINDOW_SIZES['settings'])
        dialog.configure(bg=config.COLORS['bg_dark'])
        dialog.transient(controller.root)
        
        controller.register_dialog('settings', dialog)
        
        def on_closing():
            controller.unregister_dialog('settings')
            dialog.destroy()
        
        dialog.protocol("WM_DELETE_WINDOW", on_closing)
        
        try:
            dialog.grab_set()
        except:
            pass
        
        controller._center_dialog(dialog)
        
        main_frame = tk.Frame(dialog, bg=config.COLORS['bg_dark'], padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Вкладки
        main_tab = tk.Frame(notebook, bg=config.COLORS['bg_dark'])
        notebook.add(main_tab, text="Основные")
        
        speech_tab = tk.Frame(notebook, bg=config.COLORS['bg_dark'])
        notebook.add(speech_tab, text="Озвучка")
        
        # Настройки основной вкладки
        SettingsDialog._setup_main_tab(main_tab, controller)
        
        # Настройки озвучки
        SettingsDialog._setup_speech_tab(speech_tab, controller)
        
        # Кнопка сохранения
        tk.Button(
            main_frame,
            text="Сохранить и закрыть",
            font=('Segoe UI', 12, 'bold'),
            bg=config.COLORS['primary'],
            fg=config.COLORS['text'],
            bd=0,
            padx=30,
            pady=12,
            cursor='hand2',
            command=on_closing
        ).pack(pady=20)
    
    @staticmethod
    def _setup_main_tab(parent, controller):
        """Настройки основной вкладки"""
        tk.Label(
            parent,
            text="⚙️ Основные настройки",
            font=('Segoe UI', 14, 'bold'),
            bg=config.COLORS['bg_dark'],
            fg=config.COLORS['text']
        ).pack(pady=(0, 20), anchor='w')
        
        # Автопереход
        auto_var = tk.BooleanVar(value=controller.settings.get('auto_advance', True))
        
        def toggle_auto():
            controller.settings['auto_advance'] = auto_var.get()
        
        auto_frame = tk.Frame(parent, bg=config.COLORS['bg_dark'])
        auto_frame.pack(fill=tk.X, pady=10)
        
        tk.Checkbutton(
            auto_frame,
            text="Автопереход к следующему слову после правильного ответа",
            variable=auto_var,
            command=toggle_auto,
            font=('Segoe UI', 10),
            bg=config.COLORS['bg_dark'],
            fg=config.COLORS['text'],
            selectcolor=config.COLORS['bg_dark'],
            activebackground=config.COLORS['bg_dark'],
            activeforeground=config.COLORS['text']
        ).pack(anchor='w')
        
        # Подсказки со слайдером
        hints_var = tk.BooleanVar(value=controller.settings.get('show_hints', False))
        hint_threshold_var = tk.IntVar(value=controller.settings.get('hint_threshold', 3))
        
        def toggle_hints():
            controller.settings['show_hints'] = hints_var.get()
            state = 'normal' if hints_var.get() else 'disabled'
            hint_slider.config(state=state)
            hint_label.config(state=state)
            hint_value_label.config(state=state)
        
        hints_frame = tk.Frame(parent, bg=config.COLORS['bg_dark'])
        hints_frame.pack(fill=tk.X, pady=10)
        
        tk.Checkbutton(
            hints_frame,
            text="Показывать подсказки",
            variable=hints_var,
            command=toggle_hints,
            font=('Segoe UI', 10),
            bg=config.COLORS['bg_dark'],
            fg=config.COLORS['text'],
            selectcolor=config.COLORS['bg_dark'],
            activebackground=config.COLORS['bg_dark'],
            activeforeground=config.COLORS['text']
        ).pack(anchor='w')
        
        slider_frame = tk.Frame(parent, bg=config.COLORS['bg_dark'])
        slider_frame.pack(fill=tk.X, pady=(5, 10), padx=(20, 0))
        
        hint_label = tk.Label(
            slider_frame,
            text="Показывать правильный ответ после ошибок:",
            font=('Segoe UI', 9),
            bg=config.COLORS['bg_dark'],
            fg=config.COLORS['text_secondary']
        )
        hint_label.pack(anchor='w')
        
        slider_control_frame = tk.Frame(slider_frame, bg=config.COLORS['bg_dark'])
        slider_control_frame.pack(fill=tk.X, pady=(5, 0))
        
        hint_slider = tk.Scale(
            slider_control_frame,
            from_=1, to=10,
            orient=tk.HORIZONTAL,
            length=200,
            bg=config.COLORS['bg_dark'],
            fg=config.COLORS['text'],
            highlightthickness=0,
            troughcolor=config.COLORS['bg_card'],
            variable=hint_threshold_var,
            state='normal' if hints_var.get() else 'disabled'
        )
        hint_slider.pack(side=tk.LEFT)
        
        hint_value_label = tk.Label(
            slider_control_frame,
            text=f"{hint_threshold_var.get()}",
            font=('Segoe UI', 10, 'bold'),
            bg=config.COLORS['bg_dark'],
            fg=config.COLORS['primary'],
            width=3
        )
        hint_value_label.pack(side=tk.LEFT, padx=(10, 0))
        
        def update_hint_threshold(val):
            hint_value_label.config(text=str(int(val)))
            controller.settings['hint_threshold'] = int(val)
        
        hint_slider.config(command=update_hint_threshold)
        
        # Порог сложных слов
        tk.Label(
            parent,
            text="Порог сложных слов (%):",
            font=('Segoe UI', 10),
            bg=config.COLORS['bg_dark'],
            fg=config.COLORS['text_secondary'],
            anchor='w'
        ).pack(fill=tk.X, pady=(20, 5))
        
        hard_slider = tk.Scale(
            parent,
            from_=0, to=100,
            orient=tk.HORIZONTAL,
            length=300,
            bg=config.COLORS['bg_dark'],
            fg=config.COLORS['text'],
            highlightthickness=0,
            troughcolor=config.COLORS['bg_card']
        )
        hard_slider.set(controller.settings.get('hard_word_threshold', 50))
        hard_slider.pack(anchor='w')
        
        def update_hard_threshold(val):
            controller.settings['hard_word_threshold'] = int(val)
        
        hard_slider.config(command=update_hard_threshold)
    
    @staticmethod
    def _setup_speech_tab(parent, controller):
        """Настройки озвучки"""
        tk.Label(
            parent,
            text="🔊 Настройки озвучки",
            font=('Segoe UI', 14, 'bold'),
            bg=config.COLORS['bg_dark'],
            fg=config.COLORS['text']
        ).pack(pady=(0, 20), anchor='w')
        
        speech_enabled_var = tk.BooleanVar(value=speech_synth.enabled)
        
        def toggle_speech_enabled():
            speech_synth.set_enabled(speech_enabled_var.get())
            controller.settings['enabled'] = speech_enabled_var.get()
            if controller.training_panel:
                controller.training_panel.update_speaker_button_state()
            if controller.test_panel:
                controller.test_panel.update_speaker_button_state()
            if controller.image_panel:
                controller.image_panel.update_speaker_button_state()
            controller.update_stats()
        
        speech_enabled_frame = tk.Frame(parent, bg=config.COLORS['bg_dark'])
        speech_enabled_frame.pack(fill=tk.X, pady=10)
        
        tk.Checkbutton(
            speech_enabled_frame,
            text="Включить озвучку",
            variable=speech_enabled_var,
            command=toggle_speech_enabled,
            font=('Segoe UI', 10),
            bg=config.COLORS['bg_dark'],
            fg=config.COLORS['text'],
            selectcolor=config.COLORS['bg_dark'],
            activebackground=config.COLORS['bg_dark'],
            activeforeground=config.COLORS['text']
        ).pack(anchor='w')
        
        auto_speak_var = tk.BooleanVar(value=controller.settings.get('auto_speak', False))
        
        def toggle_auto_speak():
            controller.settings['auto_speak'] = auto_speak_var.get()
        
        auto_speak_frame = tk.Frame(parent, bg=config.COLORS['bg_dark'])
        auto_speak_frame.pack(fill=tk.X, pady=10)
        
        tk.Checkbutton(
            auto_speak_frame,
            text="Автоматически озвучивать новые слова",
            variable=auto_speak_var,
            command=toggle_auto_speak,
            font=('Segoe UI', 10),
            bg=config.COLORS['bg_dark'],
            fg=config.COLORS['text'],
            selectcolor=config.COLORS['bg_dark'],
            activebackground=config.COLORS['bg_dark'],
            activeforeground=config.COLORS['text']
        ).pack(anchor='w')
        
        # Громкость
        tk.Label(
            parent,
            text="Громкость:",
            font=('Segoe UI', 10),
            bg=config.COLORS['bg_dark'],
            fg=config.COLORS['text_secondary'],
            anchor='w'
        ).pack(fill=tk.X, pady=(20, 5))
        
        volume_frame = tk.Frame(parent, bg=config.COLORS['bg_dark'])
        volume_frame.pack(fill=tk.X)
        
        volume_slider = tk.Scale(
            volume_frame,
            from_=0, to=100,
            orient=tk.HORIZONTAL,
            length=200,
            bg=config.COLORS['bg_dark'],
            fg=config.COLORS['text'],
            highlightthickness=0,
            troughcolor=config.COLORS['bg_card']
        )
        volume_slider.set(speech_synth.volume)
        volume_slider.pack(side=tk.LEFT)
        
        volume_label = tk.Label(
            volume_frame,
            text=f"{speech_synth.volume}%",
            font=('Segoe UI', 10),
            bg=config.COLORS['bg_dark'],
            fg=config.COLORS['text']
        )
        volume_label.pack(side=tk.LEFT, padx=10)
        
        def update_volume(val):
            volume = int(val)
            speech_synth.set_volume(volume)
            controller.settings['volume'] = volume
            volume_label.config(text=f"{volume}%")
        
        volume_slider.config(command=update_volume)
        
        # Скорость
        tk.Label(
            parent,
            text="Скорость речи:",
            font=('Segoe UI', 10),
            bg=config.COLORS['bg_dark'],
            fg=config.COLORS['text_secondary'],
            anchor='w'
        ).pack(fill=tk.X, pady=(20, 5))
        
        speed_frame = tk.Frame(parent, bg=config.COLORS['bg_dark'])
        speed_frame.pack(fill=tk.X)
        
        speed_slider = tk.Scale(
            speed_frame,
            from_=50, to=200,
            orient=tk.HORIZONTAL,
            length=200,
            bg=config.COLORS['bg_dark'],
            fg=config.COLORS['text'],
            highlightthickness=0,
            troughcolor=config.COLORS['bg_card']
        )
        speed_slider.set(int(speech_synth.speed * 100))
        speed_slider.pack(side=tk.LEFT)
        
        speed_label = tk.Label(
            speed_frame,
            text=f"{speech_synth.speed:.1f}x",
            font=('Segoe UI', 10),
            bg=config.COLORS['bg_dark'],
            fg=config.COLORS['text']
        )
        speed_label.pack(side=tk.LEFT, padx=10)
        
        def update_speed(val):
            speed = int(val) / 100.0
            speech_synth.set_speed(speed)
            controller.settings['speed'] = speed
            speed_label.config(text=f"{speed:.1f}x")
        
        speed_slider.config(command=update_speed)
        
        tk.Button(
            parent,
            text="🎤 Выбрать голоса для языков",
            font=('Segoe UI', 12),
            bg=config.COLORS['accent'],
            fg=config.COLORS['text'],
            bd=0,
            padx=20,
            pady=10,
            cursor='hand2',
            command=lambda: VoiceSettingsDialog.show_dialog(controller)
        ).pack(pady=30)
