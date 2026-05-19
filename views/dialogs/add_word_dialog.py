"""
Диалог добавления слова с поддержкой множественных переводов
"""

import tkinter as tk
from tkinter import ttk, filedialog
import os
import shutil
from PIL import Image, ImageTk
from config import config
from utils.notifications import show_notification

class AddWordDialog:
    """Класс диалога добавления слова"""
    
    @staticmethod
    def show(controller):
        """Показывает диалог добавления слова"""
        # Проверяем, не открыт ли уже диалог
        if controller.is_dialog_open('add_word'):
            controller.dialogs['add_word'].lift()
            controller.dialogs['add_word'].focus_set()
            return
        
        dialog = tk.Toplevel(controller.root)
        dialog.title("Добавить слово")
        dialog.geometry("650x850")
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
        
        # Блок для множественных переводов
        translations_label_frame = tk.Frame(main_frame, bg=config.COLORS['bg_dark'])
        translations_label_frame.pack(fill=tk.X, pady=(0, 5))
        
        tk.Label(
            translations_label_frame,
            text="Перевод(ы)",
            font=('Segoe UI', 10),
            bg=config.COLORS['bg_dark'],
            fg=config.COLORS['text_secondary'],
            anchor='w'
        ).pack(side=tk.LEFT)
        
        tk.Label(
            translations_label_frame,
            text=f"({config.LANGUAGES[controller.native_language]['flag']} {config.LANGUAGES[controller.native_language]['name']})",
            font=('Segoe UI', 10, 'italic'),
            bg=config.COLORS['bg_dark'],
            fg=config.COLORS['accent'],
            anchor='w'
        ).pack(side=tk.LEFT, padx=(5, 0))
        
        tk.Label(
            translations_label_frame,
            text=" (можно несколько через запятую)",
            font=('Segoe UI', 9, 'italic'),
            bg=config.COLORS['bg_dark'],
            fg=config.COLORS['text_secondary'],
            anchor='w'
        ).pack(side=tk.LEFT, padx=(5, 0))
        
        # Фрейм для переводов с кнопками добавления
        translations_frame = tk.Frame(main_frame, bg=config.COLORS['bg_dark'])
        translations_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Список для хранения виджетов переводов
        translation_entries = []
        translation_remove_buttons = []
        
        # Контейнер для списка переводов
        translations_container = tk.Frame(translations_frame, bg=config.COLORS['bg_dark'])
        translations_container.pack(fill=tk.X)
        
        # Первое поле для перевода
        def add_translation_field(initial_text=""):
            frame = tk.Frame(translations_container, bg=config.COLORS['bg_dark'])
            frame.pack(fill=tk.X, pady=2)
            
            entry = tk.Entry(
                frame,
                font=config.FONTS['input'],
                bg=config.COLORS['bg_card'],
                fg=config.COLORS['text'],
                insertbackground=config.COLORS['text']
            )
            entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=8)
            if initial_text:
                entry.insert(0, initial_text)
            
            remove_btn = tk.Button(
                frame,
                text="✖",
                font=('Segoe UI', 10),
                bg=config.COLORS['danger'],
                fg=config.COLORS['text'],
                bd=0,
                padx=8,
                pady=4,
                cursor='hand2',
                state='normal' if len(translation_entries) > 1 else 'disabled'
            )
            remove_btn.pack(side=tk.RIGHT, padx=(5, 0))
            
            translation_entries.append(entry)
            translation_remove_buttons.append(remove_btn)
            
            return frame, entry, remove_btn
        
        # Создаем первое поле
        AddWordDialog._create_first_translation_field(translations_container, translation_entries, translation_remove_buttons)
        
        # Кнопка добавления перевода
        def add_translation():
            AddWordDialog._add_translation_field(translations_container, translation_entries, translation_remove_buttons)
        
        add_translation_btn = tk.Button(
            translations_frame,
            text="➕ Добавить перевод",
            font=('Segoe UI', 10),
            bg=config.COLORS['primary'],
            fg=config.COLORS['text'],
            bd=0,
            padx=10,
            pady=5,
            cursor='hand2',
            command=add_translation
        )
        add_translation_btn.pack(pady=(5, 0))
        
        # Блок выбора категории
        category_frame, category_var, category_combo = AddWordDialog._create_category_section(main_frame, controller)
        
        # Блок добавления картинки
        temp_image_path, image_button, preview_label = AddWordDialog._create_image_section(
            main_frame, foreign_entry, translation_entries, dialog, pictures_dir
        )
        
        # Кнопки
        button_frame = tk.Frame(main_frame, bg=config.COLORS['bg_dark'])
        button_frame.pack(fill=tk.X, pady=20)
        
        def add_word():
            AddWordDialog._add_word(
                controller, dialog, foreign_entry, translation_entries,
                category_var, temp_image_path, pictures_dir, on_closing
            )
        
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
        foreign_entry.bind('<Return>', lambda e: translation_entries[0].focus() if translation_entries else None)
        
        # Фокус на первое поле
        foreign_entry.focus()
    
    @staticmethod
    def _create_first_translation_field(container, entries, remove_buttons):
        """Создает первое поле для перевода"""
        frame = tk.Frame(container, bg=config.COLORS['bg_dark'])
        frame.pack(fill=tk.X, pady=2)
        
        entry = tk.Entry(
            frame,
            font=config.FONTS['input'],
            bg=config.COLORS['bg_card'],
            fg=config.COLORS['text'],
            insertbackground=config.COLORS['text']
        )
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=8)
        
        remove_btn = tk.Button(
            frame,
            text="✖",
            font=('Segoe UI', 10),
            bg=config.COLORS['danger'],
            fg=config.COLORS['text'],
            bd=0,
            padx=8,
            pady=4,
            cursor='hand2',
            state='disabled'
        )
        remove_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        entries.append(entry)
        remove_buttons.append(remove_btn)
    
    @staticmethod
    def _add_translation_field(container, entries, remove_buttons):
        """Добавляет новое поле для перевода"""
        frame = tk.Frame(container, bg=config.COLORS['bg_dark'])
        frame.pack(fill=tk.X, pady=2)
        
        entry = tk.Entry(
            frame,
            font=config.FONTS['input'],
            bg=config.COLORS['bg_card'],
            fg=config.COLORS['text'],
            insertbackground=config.COLORS['text']
        )
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=8)
        
        def remove_field():
            idx = entries.index(entry)
            if len(entries) > 1:
                frame.destroy()
                del entries[idx]
                del remove_buttons[idx]
                # Обновляем состояние кнопок удаления
                for i, btn in enumerate(remove_buttons):
                    btn.config(state='normal' if len(entries) > 1 else 'disabled')
        
        remove_btn = tk.Button(
            frame,
            text="✖",
            font=('Segoe UI', 10),
            bg=config.COLORS['danger'],
            fg=config.COLORS['text'],
            bd=0,
            padx=8,
            pady=4,
            cursor='hand2',
            command=remove_field,
            state='normal'
        )
        remove_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        entries.append(entry)
        remove_buttons.append(remove_btn)
    
    @staticmethod
    def _create_category_section(parent, controller):
        """Создает секцию выбора категории"""
        tk.Label(
            parent,
            text="Категория:",
            font=('Segoe UI', 10),
            bg=config.COLORS['bg_dark'],
            fg=config.COLORS['text_secondary'],
            anchor='w'
        ).pack(fill=tk.X, pady=(0, 5))
        
        category_frame = tk.Frame(parent, bg=config.COLORS['bg_dark'])
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
            new_cat = simpledialog.askstring("Новая категория", "Введите название новой категории:")
            if new_cat and new_cat.strip():
                category_name = new_cat.strip()
                current_values = list(category_combo['values'])
                if category_name not in current_values:
                    current_values.append(category_name)
                    category_combo['values'] = current_values
                    category_var.set(category_name)
                    show_notification(parent, "Успех", f"Категория '{category_name}' создана", "success")
        
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
        
        return category_frame, category_var, category_combo
    
    @staticmethod
    def _create_image_section(parent, foreign_entry, translation_entries, dialog, pictures_dir):
        """Создает секцию выбора картинки"""
        image_frame = tk.Frame(parent, bg=config.COLORS['bg_dark'])
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
        
        def select_image():
            foreign = foreign_entry.get().strip()
            translations = [e.get().strip() for e in translation_entries if e.get().strip()]
            if not foreign or not translations:
                show_notification(dialog, "Ошибка", "Сначала заполните слово и хотя бы один перевод", "error")
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
                    img = Image.open(file_path)
                    img.thumbnail((180, 180), Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(img)
                    
                    preview_label.config(image=photo, text="")
                    preview_label.image = photo
                    
                    temp_image_path.set(file_path)
                    image_button.config(text=f"✅ Картинка выбрана")
                    
                    show_notification(dialog, "Успех", "Картинка выбрана", "success")
                    
                except Exception as e:
                    show_notification(dialog, "Ошибка", f"Не удалось загрузить картинку: {e}", "error")
        
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
        
        tk.Label(
            image_frame,
            text="Картинка будет скопирована в папку data/pictures после добавления слова",
            font=('Segoe UI', 8),
            bg=config.COLORS['bg_dark'],
            fg=config.COLORS['text_secondary'],
            wraplength=500
        ).pack(pady=(5, 0))
        
        return temp_image_path, image_button, preview_label
    
    @staticmethod
    def _add_word(controller, dialog, foreign_entry, translation_entries, category_var, temp_image_path, pictures_dir, on_closing):
        """Добавляет слово в словарь"""
        foreign = foreign_entry.get().strip()
        translations = [e.get().strip() for e in translation_entries if e.get().strip()]
        category = category_var.get().strip()
        
        if not foreign or not translations:
            show_notification(dialog, "Ошибка", "Заполните слово и хотя бы один перевод", "error")
            return
        
        if not category:
            category = "Основные"
        
        # Копируем картинку, если она была выбрана
        image_filename = None
        if temp_image_path.get():
            try:
                clean_name = foreign.lower().replace(' ', '_').replace('-', '_')
                ext = os.path.splitext(temp_image_path.get())[1].lower()
                new_filename = f"{clean_name}{ext}"
                
                dest_path = os.path.join(pictures_dir, new_filename)
                
                counter = 1
                while os.path.exists(dest_path):
                    new_filename = f"{clean_name}_{counter}{ext}"
                    dest_path = os.path.join(pictures_dir, new_filename)
                    counter += 1
                
                shutil.copy2(temp_image_path.get(), dest_path)
                image_filename = new_filename
                
            except Exception as e:
                show_notification(dialog, "Ошибка", f"Не удалось скопировать картинку: {e}", "error")
                return
        
        # Добавляем слово с множественными переводами
        success = controller.add_word(foreign, translations, category, image_filename)
        
        if success:
            show_notification(dialog, "Успех", f"Слово '{foreign}' добавлено с {len(translations)} перевод(ами)", "success")
            on_closing()
            controller.next_word()
        else:
            show_notification(dialog, "Ошибка", "Такое слово уже существует", "error")
