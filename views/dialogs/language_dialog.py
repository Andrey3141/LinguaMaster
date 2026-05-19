"""
Диалог смены языка
"""

import tkinter as tk
from tkinter import ttk
from config import config
from utils.notifications import show_notification

class LanguageDialog:
    """Класс диалога смены языка"""
    
    @staticmethod
    def show(controller):
        """Показывает диалог смены языка"""
        if controller.is_dialog_open('language'):
            controller.dialogs['language'].lift()
            controller.dialogs['language'].focus_set()
            return
        
        dialog = tk.Toplevel(controller.root)
        dialog.title("🌐 Сменить язык")
        dialog.geometry("700x500")
        dialog.configure(bg=config.COLORS['bg_dark'])
        dialog.transient(controller.root)
        
        controller.register_dialog('language', dialog)
        
        def on_closing():
            controller.unregister_dialog('language')
            dialog.destroy()
        
        dialog.protocol("WM_DELETE_WINDOW", on_closing)
        
        try:
            dialog.grab_set()
        except:
            pass
        
        controller._center_dialog(dialog)
        
        main_frame = tk.Frame(dialog, bg=config.COLORS['bg_dark'], padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(
            main_frame,
            text="🌐 Выбор языков",
            font=('Segoe UI', 16, 'bold'),
            bg=config.COLORS['bg_dark'],
            fg=config.COLORS['text']
        ).pack(pady=(0, 20))
        
        columns_frame = tk.Frame(main_frame, bg=config.COLORS['bg_dark'])
        columns_frame.pack(fill=tk.BOTH, expand=True)
        
        # Левая колонка - изучаемый язык
        language_var = LanguageDialog._create_language_column(
            columns_frame, "Изучаемый язык:", controller.language, config.COLORS['primary']
        )
        
        # Правая колонка - родной язык
        native_var = LanguageDialog._create_language_column(
            columns_frame, "Родной язык:", controller.native_language, config.COLORS['accent']
        )
        
        # Кнопки
        button_frame = tk.Frame(main_frame, bg=config.COLORS['bg_dark'])
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        def validate_and_apply():
            study_lang = language_var.get()
            native_lang = native_var.get()
            
            if study_lang == native_lang:
                show_notification(
                    dialog,
                    "Ошибка выбора языка",
                    "Изучаемый и родной языки не могут быть одинаковыми!",
                    "error"
                )
                return False
            return True
        
        def apply_languages():
            if not validate_and_apply():
                return
            
            study_lang = language_var.get()
            native_lang = native_var.get()
            
            controller.language = study_lang
            controller.native_language = native_lang
            controller.mode = f'{study_lang}-{native_lang}'
            
            controller.top_bar.refresh_mode_buttons()
            
            if controller.training_panel:
                controller.training_panel.update_mode_icon(study_lang)
            if controller.test_panel:
                controller.test_panel.update_mode_icon(study_lang)
            if controller.match_panel:
                controller.match_panel.update_mode_icon(study_lang)
            if controller.image_panel:
                controller.image_panel.update_mode_icon(study_lang)
            
            words_for_mode = controller.model.get_words_for_mode(controller.mode)
            
            if not words_for_mode:
                show_notification(
                    controller.root,
                    "Словарь пуст",
                    f"Для языка {config.LANGUAGES[study_lang]['name']} ↔ {config.LANGUAGES[native_lang]['name']} нет слов. Добавьте слова для обучения.",
                    "warning"
                )
            else:
                show_notification(
                    controller.root,
                    "Язык изменен",
                    f"Режим: {config.LANGUAGES[study_lang]['flag']} → {config.LANGUAGES[native_lang]['flag']}",
                    "success"
                )
            
            controller.next_word()
        
        def save_and_close():
            if not validate_and_apply():
                return
            apply_languages()
            on_closing()
        
        tk.Button(
            button_frame,
            text="💾 Сохранить",
            font=('Segoe UI', 12, 'bold'),
            bg=config.COLORS['primary'],
            fg=config.COLORS['text'],
            bd=0,
            padx=30,
            pady=10,
            cursor='hand2',
            command=save_and_close
        ).pack(side=tk.LEFT)
        
        tk.Button(
            button_frame,
            text="✅ Применить",
            font=('Segoe UI', 12),
            bg=config.COLORS['success'],
            fg=config.COLORS['text'],
            bd=0,
            padx=30,
            pady=10,
            cursor='hand2',
            command=apply_languages
        ).pack(side=tk.LEFT, padx=(10, 0))
        
        tk.Button(
            button_frame,
            text="❌ Отмена",
            font=('Segoe UI', 12),
            bg=config.COLORS['bg_card'],
            fg=config.COLORS['text_secondary'],
            bd=0,
            padx=30,
            pady=10,
            cursor='hand2',
            command=on_closing
        ).pack(side=tk.RIGHT)
    
    @staticmethod
    def _create_language_column(parent, title, current_language, color):
        """Создает колонку со списком языков"""
        frame = tk.Frame(parent, bg=config.COLORS['bg_dark'], width=300)
        frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        tk.Label(
            frame,
            text=title,
            font=('Segoe UI', 12, 'bold'),
            bg=config.COLORS['bg_dark'],
            fg=color
        ).pack(anchor='w', pady=(0, 10))
        
        canvas = tk.Canvas(frame, bg=config.COLORS['bg_dark'], highlightthickness=0, height=300)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        content = tk.Frame(canvas, bg=config.COLORS['bg_dark'])
        
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        canvas.create_window((0, 0), window=content, anchor="nw")
        
        lang_var = tk.StringVar(value=current_language)
        
        for code, lang_info in config.LANGUAGES.items():
            lang_frame = tk.Frame(content, bg=config.COLORS['bg_card'], padx=10, pady=8)
            lang_frame.pack(fill=tk.X, pady=3)
            
            radio = tk.Radiobutton(
                lang_frame,
                text=f"  {lang_info['flag']} {lang_info['name']}",
                variable=lang_var,
                value=code,
                font=('Segoe UI', 11),
                bg=config.COLORS['bg_card'],
                fg=config.COLORS['text'],
                selectcolor=color,
                activebackground=config.COLORS['bg_card'],
                activeforeground=config.COLORS['text'],
                indicatoron=1,
                width=25,
                anchor='w'
            )
            radio.pack(side=tk.LEFT)
            
            if code == current_language:
                tk.Label(
                    lang_frame,
                    text="✓",
                    font=('Segoe UI', 14, 'bold'),
                    bg=config.COLORS['bg_card'],
                    fg=config.COLORS['success']
                ).pack(side=tk.RIGHT, padx=(0, 10))
        
        def configure_scroll(event):
            content.update_idletasks()
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.itemconfig(canvas.create_window((0, 0), window=content, anchor="nw"), width=event.width)
        
        content.bind("<Configure>", configure_scroll)
        
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        
        canvas.bind_all("<MouseWheel>", on_mousewheel)
        
        return lang_var
