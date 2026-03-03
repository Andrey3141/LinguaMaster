"""
Основные диалоговые окна: добавление слов, настройки, смена языка
"""

import tkinter as tk
from tkinter import ttk, filedialog
import os
import shutil
from PIL import Image, ImageTk
from config import config
from utils.notifications import show_notification
from utils.speech import speech_synth
from .voice_settings_dialog import VoiceSettingsDialog

class DialogHandlers:
    """Класс для обработки основных диалоговых окон"""
    
    @staticmethod
    def add_word_dialog(controller):
        """Показывает диалог добавления слова"""
        # Проверяем, не открыт ли уже диалог
        if controller.is_dialog_open('add_word'):
            controller.dialogs['add_word'].lift()
            controller.dialogs['add_word'].focus_set()
            return
        
        dialog = tk.Toplevel(controller.root)
        dialog.title("Добавить слово")
        dialog.geometry("600x700")
        dialog.configure(bg=config.COLORS['bg_dark'])
        dialog.transient(controller.root)
        
        # Регистрируем диалог
        controller.register_dialog('add_word', dialog)
        
        # Папка для картинок
        pictures_dir = os.path.join(config.PATHS['data'], 'pictures')
        os.makedirs(pictures_dir, exist_ok=True)
        
        def on_closing():
            controller.unregister_dialog('add_word')
            dialog.destroy()
        
        dialog.protocol("WM_DELETE_WINDOW", on_closing)
        
        try:
            dialog.grab_set()
        except:
            pass
        
        controller._center_dialog(dialog)
        
        # Создаем скроллируемую область
        canvas = tk.Canvas(dialog, bg=config.COLORS['bg_dark'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(dialog, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=config.COLORS['bg_dark'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Основной контейнер внутри скролла
        main_frame = tk.Frame(scrollable_frame, bg=config.COLORS['bg_dark'], padx=25, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Заголовок
        tk.Label(
            main_frame,
            text="➕ Добавить новое слово",
            font=('Segoe UI', 16, 'bold'),
            bg=config.COLORS['bg_dark'],
            fg=config.COLORS['text']
        ).pack(pady=(0, 20))
        
        # Информация о языках с указанием направления
        lang_info = tk.Label(
            main_frame,
            text=f"{config.LANGUAGES[controller.language]['flag']} {config.LANGUAGES[controller.language]['name']} → {config.LANGUAGES[controller.native_language]['flag']} {config.LANGUAGES[controller.native_language]['name']}",
            font=('Segoe UI', 11),
            bg=config.COLORS['bg_card'],
            fg=config.COLORS['primary'],
            pady=8
        )
        lang_info.pack(fill=tk.X, pady=(0, 20))
        
        # Поле для иностранного слова с указанием языка
        foreign_label_frame = tk.Frame(main_frame, bg=config.COLORS['bg_dark'])
        foreign_label_frame.pack(fill=tk.X, pady=(0, 5))
        
        tk.Label(
            foreign_label_frame,
            text="Иностранное слово",
            font=('Segoe UI', 10),
            bg=config.COLORS['bg_dark'],
            fg=config.COLORS['text_secondary'],
            anchor='w'
        ).pack(side=tk.LEFT)
        
        tk.Label(
            foreign_label_frame,
            text=f"({config.LANGUAGES[controller.language]['flag']} {config.LANGUAGES[controller.language]['name']})",
            font=('Segoe UI', 10, 'italic'),
            bg=config.COLORS['bg_dark'],
            fg=config.COLORS['primary'],
            anchor='w'
        ).pack(side=tk.LEFT, padx=(5, 0))
        
        foreign_entry = tk.Entry(
            main_frame,
            font=config.FONTS['input'],
            bg=config.COLORS['bg_card'],
            fg=config.COLORS['text'],
            insertbackground=config.COLORS['text']
        )
        foreign_entry.pack(fill=tk.X, pady=(0, 15), ipady=8)
        
        # Поле для перевода с указанием языка
        translation_label_frame = tk.Frame(main_frame, bg=config.COLORS['bg_dark'])
        translation_label_frame.pack(fill=tk.X, pady=(0, 5))
        
        tk.Label(
            translation_label_frame,
            text="Перевод",
            font=('Segoe UI', 10),
            bg=config.COLORS['bg_dark'],
            fg=config.COLORS['text_secondary'],
            anchor='w'
        ).pack(side=tk.LEFT)
        
        tk.Label(
            translation_label_frame,
            text=f"({config.LANGUAGES[controller.native_language]['flag']} {config.LANGUAGES[controller.native_language]['name']})",
            font=('Segoe UI', 10, 'italic'),
            bg=config.COLORS['bg_dark'],
            fg=config.COLORS['accent'],
            anchor='w'
        ).pack(side=tk.LEFT, padx=(5, 0))
        
        translation_entry = tk.Entry(
            main_frame,
            font=config.FONTS['input'],
            bg=config.COLORS['bg_card'],
            fg=config.COLORS['text'],
            insertbackground=config.COLORS['text']
        )
        translation_entry.pack(fill=tk.X, pady=(0, 15), ipady=8)
        
        # Блок выбора категории
        tk.Label(
            main_frame,
            text="Категория:",
            font=('Segoe UI', 10),
            bg=config.COLORS['bg_dark'],
            fg=config.COLORS['text_secondary'],
            anchor='w'
        ).pack(fill=tk.X, pady=(0, 5))
        
        # Фрейм для категории с кнопкой создания
        category_frame = tk.Frame(main_frame, bg=config.COLORS['bg_dark'])
        category_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Получаем список существующих категорий
        categories = controller.model.get_all_categories()
        if "Основные" not in categories:
            categories.insert(0, "Основные")
        
        category_var = tk.StringVar(value="Основные")
        
        category_combo = ttk.Combobox(
            category_frame,
            textvariable=category_var,
            values=categories,
            font=('Segoe UI', 10),
            state='readonly'
        )
        category_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=5)
        
        # Кнопка создания новой категории
        def create_new_category():
            from tkinter import simpledialog
            new_cat = simpledialog.askstring("Новая категория", "Введите название новой категории:", parent=dialog)
            if new_cat and new_cat.strip():
                category_name = new_cat.strip()
                current_values = list(category_combo['values'])
                if category_name not in current_values:
                    current_values.append(category_name)
                    category_combo['values'] = current_values
                    category_var.set(category_name)
                    show_notification(dialog, "Успех", f"Категория '{category_name}' создана", "success")
        
        tk.Button(
            category_frame,
            text="➕",
            font=('Segoe UI', 12),
            bg=config.COLORS['primary'],
            fg=config.COLORS['text'],
            bd=0,
            padx=12,
            pady=5,
            cursor='hand2',
            command=create_new_category
        ).pack(side=tk.RIGHT, padx=(5, 0))
        
        # ===== НОВЫЙ БЛОК: Добавление картинки =====
        image_frame = tk.Frame(main_frame, bg=config.COLORS['bg_dark'])
        image_frame.pack(fill=tk.X, pady=15)
        
        tk.Label(
            image_frame,
            text="🖼️ Картинка для слова:",
            font=('Segoe UI', 11, 'bold'),
            bg=config.COLORS['bg_dark'],
            fg=config.COLORS['text']
        ).pack(anchor='w', pady=(0, 5))
        
        # Фрейм для предпросмотра
        preview_frame = tk.Frame(
            image_frame,
            bg=config.COLORS['bg_card'],
            width=200,
            height=200,
            relief=tk.SUNKEN,
            bd=2
        )
        preview_frame.pack(pady=10)
        preview_frame.pack_propagate(False)
        
        # Метка для предпросмотра
        preview_label = tk.Label(
            preview_frame,
            text="Нет картинки",
            font=('Segoe UI', 10),
            bg=config.COLORS['bg_card'],
            fg=config.COLORS['text_secondary']
        )
        preview_label.pack(expand=True, fill=tk.BOTH)
        
        # Переменная для хранения временного пути к выбранной картинке
        temp_image_path = tk.StringVar()
        temp_image_name = tk.StringVar()
        
        def select_image():
            foreign = foreign_entry.get().strip()
            translation = translation_entry.get().strip()
            if not foreign or not translation:
                show_notification(dialog, "Ошибка", "Сначала заполните оба поля", "error")
                return
            
            file_path = filedialog.askopenfilename(
                title="Выберите картинку",
                filetypes=[
                    ("Изображения", "*.png *.jpg *.jpeg *.gif *.bmp"),
                    ("Все файлы", "*.*")
                ],
                parent=dialog
            )
            
            if file_path:
                try:
                    # Просто показываем предпросмотр, не копируем
                    img = Image.open(file_path)
                    img.thumbnail((180, 180), Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(img)
                    
                    preview_label.config(image=photo, text="")
                    preview_label.image = photo
                    
                    # Сохраняем путь к временному файлу
                    temp_image_path.set(file_path)
                    
                    # Обновляем текст кнопки
                    image_button.config(text=f"✅ Картинка выбрана")
                    
                    show_notification(dialog, "Успех", "Картинка выбрана", "success")
                    
                except Exception as e:
                    show_notification(dialog, "Ошибка", f"Не удалось загрузить картинку: {e}", "error")
        
        # Кнопка выбора картинки
        image_button = tk.Button(
            image_frame,
            text="📁 Выбрать картинку",
            font=('Segoe UI', 11),
            bg=config.COLORS['primary'],
            fg=config.COLORS['text'],
            bd=0,
            padx=20,
            pady=10,
            cursor='hand2',
            command=select_image
        )
        image_button.pack()
        
        # Информация
        tk.Label(
            image_frame,
            text="Картинка будет скопирована в папку data/pictures после добавления слова",
            font=('Segoe UI', 8),
            bg=config.COLORS['bg_dark'],
            fg=config.COLORS['text_secondary'],
            wraplength=500
        ).pack(pady=(5, 0))
        # ===== КОНЕЦ НОВОГО БЛОКА =====
        
        # Кнопки
        button_frame = tk.Frame(main_frame, bg=config.COLORS['bg_dark'])
        button_frame.pack(fill=tk.X, pady=20)
        
        def add_word():
            foreign = foreign_entry.get().strip()
            translation = translation_entry.get().strip()
            category = category_var.get().strip()
            
            if not foreign or not translation:
                show_notification(dialog, "Ошибка", "Заполните оба поля", "error")
                return
            
            if not category:
                category = "Основные"
            
            # Копируем картинку, если она была выбрана
            image_filename = None
            if temp_image_path.get():
                try:
                    # Создаем имя файла на основе иностранного слова
                    clean_name = foreign.lower().replace(' ', '_').replace('-', '_')
                    ext = os.path.splitext(temp_image_path.get())[1].lower()
                    new_filename = f"{clean_name}{ext}"
                    
                    # Копируем картинку в папку pictures
                    dest_path = os.path.join(pictures_dir, new_filename)
                    
                    # Если файл уже существует, добавляем число
                    counter = 1
                    while os.path.exists(dest_path):
                        new_filename = f"{clean_name}_{counter}{ext}"
                        dest_path = os.path.join(pictures_dir, new_filename)
                        counter += 1
                    
                    # Копируем файл
                    shutil.copy2(temp_image_path.get(), dest_path)
                    image_filename = new_filename
                    
                except Exception as e:
                    show_notification(dialog, "Ошибка", f"Не удалось скопировать картинку: {e}", "error")
                    return
            
            # Добавляем слово с указанием картинки (если есть)
            success = controller.add_word(foreign, translation, category, image_filename)
            
            if success:
                show_notification(dialog, "Успех", "Слово добавлено", "success")
                on_closing()
                controller.next_word()
            else:
                show_notification(dialog, "Ошибка", "Такое слово уже существует", "error")
        
        # Кнопка добавления
        tk.Button(
            button_frame,
            text="✅ Добавить",
            font=('Segoe UI', 12, 'bold'),
            bg=config.COLORS['primary'],
            fg=config.COLORS['text'],
            bd=0,
            padx=30,
            pady=10,
            cursor='hand2',
            command=add_word
        ).pack(side=tk.LEFT)
        
        # Кнопка отмены
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
        
        # Привязываем Enter к добавлению
        foreign_entry.bind('<Return>', lambda e: translation_entry.focus())
        translation_entry.bind('<Return>', lambda e: add_word())
        
        # Фокус на первое поле
        foreign_entry.focus()
    
    @staticmethod
    def refresh_words(controller):
        """Обновляет список слов"""
        controller.next_word()
        show_notification(
            controller.root,
            "Список обновлен",
            "Выбрано новое слово",
            "info"
        )
    
    @staticmethod
    def quick_training(controller):
        """Быстрая тренировка"""
        controller.settings['quick_training_words'] = 10
        show_notification(
            controller.root,
            "Быстрая тренировка",
            f"Будет показано {controller.settings['quick_training_words']} слов",
            "info"
        )
        controller.next_word()
    
    @staticmethod
    def show_settings_dialog(controller):
        """Показывает диалог настроек"""
        # Проверяем, не открыт ли уже диалог
        if controller.is_dialog_open('settings'):
            controller.dialogs['settings'].lift()
            controller.dialogs['settings'].focus_set()
            return
        
        dialog = tk.Toplevel(controller.root)
        dialog.title("⚙️ Настройки")
        dialog.geometry(config.WINDOW_SIZES['settings'])
        dialog.configure(bg=config.COLORS['bg_dark'])
        dialog.transient(controller.root)
        
        # Регистрируем диалог
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
        
        # Создаем Notebook для вкладок
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Вкладка основных настроек
        main_tab = tk.Frame(notebook, bg=config.COLORS['bg_dark'])
        notebook.add(main_tab, text="Основные")
        
        # Вкладка настроек озвучки
        speech_tab = tk.Frame(notebook, bg=config.COLORS['bg_dark'])
        notebook.add(speech_tab, text="Озвучка")
        
        # === ОСНОВНЫЕ НАСТРОЙКИ ===
        tk.Label(
            main_tab,
            text="⚙️ Основные настройки",
            font=('Segoe UI', 14, 'bold'),
            bg=config.COLORS['bg_dark'],
            fg=config.COLORS['text']
        ).pack(pady=(0, 20), anchor='w')
        
        # Автопереход
        auto_var = tk.BooleanVar(value=controller.settings['auto_advance'])
        
        def toggle_auto():
            controller.settings['auto_advance'] = auto_var.get()
        
        auto_frame = tk.Frame(main_tab, bg=config.COLORS['bg_dark'])
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
            if hints_var.get():
                hint_slider.config(state='normal')
                hint_label.config(state='normal')
                hint_value_label.config(state='normal')
            else:
                hint_slider.config(state='disabled')
                hint_label.config(state='disabled')
                hint_value_label.config(state='disabled')
        
        hints_frame = tk.Frame(main_tab, bg=config.COLORS['bg_dark'])
        hints_frame.pack(fill=tk.X, pady=10)
        
        hints_check = tk.Checkbutton(
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
        )
        hints_check.pack(anchor='w')
        
        slider_frame = tk.Frame(main_tab, bg=config.COLORS['bg_dark'])
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
            main_tab,
            text="Порог сложных слов (%):",
            font=('Segoe UI', 10),
            bg=config.COLORS['bg_dark'],
            fg=config.COLORS['text_secondary'],
            anchor='w'
        ).pack(fill=tk.X, pady=(20, 5))
        
        hard_slider = tk.Scale(
            main_tab,
            from_=0, to=100,
            orient=tk.HORIZONTAL,
            length=300,
            bg=config.COLORS['bg_dark'],
            fg=config.COLORS['text'],
            highlightthickness=0,
            troughcolor=config.COLORS['bg_card']
        )
        hard_slider.set(controller.settings['hard_word_threshold'])
        hard_slider.pack(anchor='w')
        
        def update_hard_threshold(val):
            controller.settings['hard_word_threshold'] = int(val)
        
        hard_slider.config(command=update_hard_threshold)
        
        # === НАСТРОЙКИ ОЗВУЧКИ ===
        tk.Label(
            speech_tab,
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
        
        speech_enabled_frame = tk.Frame(speech_tab, bg=config.COLORS['bg_dark'])
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
        
        auto_speak_frame = tk.Frame(speech_tab, bg=config.COLORS['bg_dark'])
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
            speech_tab,
            text="Громкость:",
            font=('Segoe UI', 10),
            bg=config.COLORS['bg_dark'],
            fg=config.COLORS['text_secondary'],
            anchor='w'
        ).pack(fill=tk.X, pady=(20, 5))
        
        volume_frame = tk.Frame(speech_tab, bg=config.COLORS['bg_dark'])
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
            speech_tab,
            text="Скорость речи:",
            font=('Segoe UI', 10),
            bg=config.COLORS['bg_dark'],
            fg=config.COLORS['text_secondary'],
            anchor='w'
        ).pack(fill=tk.X, pady=(20, 5))
        
        speed_frame = tk.Frame(speech_tab, bg=config.COLORS['bg_dark'])
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
            speech_tab,
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
    def change_language_dialog(controller):
        """Показывает диалог смены языка"""
        # Проверяем, не открыт ли уже диалог
        if controller.is_dialog_open('language'):
            controller.dialogs['language'].lift()
            controller.dialogs['language'].focus_set()
            return
        
        dialog = tk.Toplevel(controller.root)
        dialog.title("🌐 Сменить язык")
        dialog.geometry("700x500")
        dialog.configure(bg=config.COLORS['bg_dark'])
        dialog.transient(controller.root)
        
        # Регистрируем диалог
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
        
        # Основной контейнер
        main_frame = tk.Frame(dialog, bg=config.COLORS['bg_dark'], padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(
            main_frame,
            text="🌐 Выбор языков",
            font=('Segoe UI', 16, 'bold'),
            bg=config.COLORS['bg_dark'],
            fg=config.COLORS['text']
        ).pack(pady=(0, 20))
        
        # Фрейм для двух колонок
        columns_frame = tk.Frame(main_frame, bg=config.COLORS['bg_dark'])
        columns_frame.pack(fill=tk.BOTH, expand=True)
        
        # ЛЕВАЯ КОЛОНКА - Изучаемый язык
        left_frame = tk.Frame(columns_frame, bg=config.COLORS['bg_dark'], width=300)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        tk.Label(
            left_frame,
            text="Изучаемый язык:",
            font=('Segoe UI', 12, 'bold'),
            bg=config.COLORS['bg_dark'],
            fg=config.COLORS['primary']
        ).pack(anchor='w', pady=(0, 10))
        
        # Canvas для прокрутки изучаемых языков
        left_canvas = tk.Canvas(left_frame, bg=config.COLORS['bg_dark'], highlightthickness=0, height=300)
        left_scrollbar = ttk.Scrollbar(left_frame, orient="vertical", command=left_canvas.yview)
        
        left_content = tk.Frame(left_canvas, bg=config.COLORS['bg_dark'])
        
        left_canvas.configure(yscrollcommand=left_scrollbar.set)
        
        left_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        left_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        left_canvas_window = left_canvas.create_window((0, 0), window=left_content, anchor="nw", width=280)
        
        # Переменная для выбора изучаемого языка
        language_var = tk.StringVar(value=controller.language)
        
        # Добавляем языки вертикально
        for code, lang_info in config.LANGUAGES.items():
            lang_frame = tk.Frame(left_content, bg=config.COLORS['bg_card'], padx=10, pady=8)
            lang_frame.pack(fill=tk.X, pady=3)
            
            radio = tk.Radiobutton(
                lang_frame,
                text=f"  {lang_info['flag']} {lang_info['name']}",
                variable=language_var,
                value=code,
                font=('Segoe UI', 11),
                bg=config.COLORS['bg_card'],
                fg=config.COLORS['text'],
                selectcolor=config.COLORS['primary'],
                activebackground=config.COLORS['bg_card'],
                activeforeground=config.COLORS['text'],
                indicatoron=1,
                width=25,
                anchor='w'
            )
            radio.pack(side=tk.LEFT)
            
            if code == controller.language:
                check_label = tk.Label(
                    lang_frame,
                    text="✓",
                    font=('Segoe UI', 14, 'bold'),
                    bg=config.COLORS['bg_card'],
                    fg=config.COLORS['success']
                )
                check_label.pack(side=tk.RIGHT, padx=(0, 10))
        
        # ПРАВАЯ КОЛОНКА - Родной язык
        right_frame = tk.Frame(columns_frame, bg=config.COLORS['bg_dark'], width=300)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        tk.Label(
            right_frame,
            text="Родной язык:",
            font=('Segoe UI', 12, 'bold'),
            bg=config.COLORS['bg_dark'],
            fg=config.COLORS['accent']
        ).pack(anchor='w', pady=(0, 10))
        
        # Canvas для прокрутки родных языков
        right_canvas = tk.Canvas(right_frame, bg=config.COLORS['bg_dark'], highlightthickness=0, height=300)
        right_scrollbar = ttk.Scrollbar(right_frame, orient="vertical", command=right_canvas.yview)
        
        right_content = tk.Frame(right_canvas, bg=config.COLORS['bg_dark'])
        
        right_canvas.configure(yscrollcommand=right_scrollbar.set)
        
        right_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        right_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        right_canvas_window = right_canvas.create_window((0, 0), window=right_content, anchor="nw", width=280)
        
        # Переменная для выбора родного языка
        native_var = tk.StringVar(value=controller.native_language)
        
        # Добавляем языки вертикально
        for code, lang_info in config.LANGUAGES.items():
            lang_frame = tk.Frame(right_content, bg=config.COLORS['bg_card'], padx=10, pady=8)
            lang_frame.pack(fill=tk.X, pady=3)
            
            radio = tk.Radiobutton(
                lang_frame,
                text=f"  {lang_info['flag']} {lang_info['name']}",
                variable=native_var,
                value=code,
                font=('Segoe UI', 11),
                bg=config.COLORS['bg_card'],
                fg=config.COLORS['text'],
                selectcolor=config.COLORS['accent'],
                activebackground=config.COLORS['bg_card'],
                activeforeground=config.COLORS['text'],
                indicatoron=1,
                width=25,
                anchor='w'
            )
            radio.pack(side=tk.LEFT)
            
            if code == controller.native_language:
                check_label = tk.Label(
                    lang_frame,
                    text="✓",
                    font=('Segoe UI', 14, 'bold'),
                    bg=config.COLORS['bg_card'],
                    fg=config.COLORS['success']
                )
                check_label.pack(side=tk.RIGHT, padx=(0, 10))
        
        # Кнопки внизу
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
        
        def configure_left_scroll(event):
            left_content.update_idletasks()
            left_canvas.configure(scrollregion=left_canvas.bbox("all"))
            left_canvas.itemconfig(left_canvas_window, width=event.width)
        
        def configure_right_scroll(event):
            right_content.update_idletasks()
            right_canvas.configure(scrollregion=right_canvas.bbox("all"))
            right_canvas.itemconfig(right_canvas_window, width=event.width)
        
        left_content.bind("<Configure>", configure_left_scroll)
        right_content.bind("<Configure>", configure_right_scroll)
        
        def on_left_mousewheel(event):
            left_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        
        def on_right_mousewheel(event):
            right_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        
        left_canvas.bind_all("<MouseWheel>", on_left_mousewheel)
        right_canvas.bind_all("<MouseWheel>", on_right_mousewheel)
    
    @staticmethod
    def set_difficulty(controller, difficulty):
        """Устанавливает сложность слов"""
        controller.difficulty = difficulty
        controller.next_word()
        
        difficulty_names = {
            'all': 'все слова',
            'easy': 'легкие слова',
            'medium': 'средние слова',
            'hard': 'сложные слова'
        }
        
        show_notification(
            controller.root,
            "Сложность изменена",
            f"Теперь показываются {difficulty_names.get(difficulty, difficulty)}",
            "info"
        )
    
    @staticmethod
    def add_word(controller, foreign, translation):
        """Добавляет слово через контроллер"""
        return controller.model.add_word(foreign, translation, controller.language, controller.native_language)
