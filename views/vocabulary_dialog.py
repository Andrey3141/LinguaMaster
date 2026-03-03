"""
Диалоговое окно словаря с сортировкой и фильтрацией
"""

import tkinter as tk
from tkinter import ttk
from config import config

class VocabularyDialog:
    """Класс для отображения словаря"""
    
    @staticmethod
    def show_vocabulary(controller):
        """Показывает окно со словарем с фильтрацией и сортировкой"""
        # Проверяем, не открыт ли уже диалог
        if controller.is_dialog_open('vocabulary'):
            controller.dialogs['vocabulary'].lift()
            controller.dialogs['vocabulary'].focus_set()
            return
        
        dialog = tk.Toplevel(controller.root)
        dialog.title("📖 Словарь")
        dialog.geometry("1000x650")
        dialog.configure(bg=config.COLORS['bg_dark'])
        dialog.transient(controller.root)
        
        # Регистрируем диалог
        controller.register_dialog('vocabulary', dialog)
        
        def on_closing():
            controller.unregister_dialog('vocabulary')
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
        
        # Заголовок
        tk.Label(
            main_frame,
            text="📖 Словарь",
            font=('Segoe UI', 16, 'bold'),
            bg=config.COLORS['bg_dark'],
            fg=config.COLORS['text']
        ).pack(pady=(0, 20))
        
        # Фрейм для фильтров
        filter_frame = tk.Frame(main_frame, bg=config.COLORS['bg_dark'])
        filter_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Левая часть - фильтр по языкам
        lang_frame = tk.Frame(filter_frame, bg=config.COLORS['bg_dark'])
        lang_frame.pack(side=tk.LEFT)
        
        # Чекбокс "Показать все слова"
        show_all_var = tk.BooleanVar(value=False)
        
        def on_checkbox_change():
            load_data()
        
        show_all_check = tk.Checkbutton(
            lang_frame,
            text="Показать все слова",
            variable=show_all_var,
            command=on_checkbox_change,
            font=('Segoe UI', 10),
            bg=config.COLORS['bg_dark'],
            fg=config.COLORS['text'],
            selectcolor=config.COLORS['bg_dark'],
            activebackground=config.COLORS['bg_dark'],
            activeforeground=config.COLORS['text']
        )
        show_all_check.pack(side=tk.LEFT, padx=(0, 20))
        
        # Правая часть - фильтр по категориям
        category_frame = tk.Frame(filter_frame, bg=config.COLORS['bg_dark'])
        category_frame.pack(side=tk.RIGHT)
        
        tk.Label(
            category_frame,
            text="Категория:",
            font=('Segoe UI', 10),
            bg=config.COLORS['bg_dark'],
            fg=config.COLORS['text_secondary']
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        # Получаем список категорий
        categories = ["Все категории"] + controller.model.get_all_categories()
        category_var = tk.StringVar(value="Все категории")
        
        category_combo = ttk.Combobox(
            category_frame,
            textvariable=category_var,
            values=categories,
            font=('Segoe UI', 10),
            state='readonly',
            width=20
        )
        category_combo.pack(side=tk.LEFT)
        category_combo.bind('<<ComboboxSelected>>', lambda e: load_data())
        
        # Фрейм для Treeview
        tree_frame = tk.Frame(main_frame, bg=config.COLORS['bg_dark'])
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Создаем скроллбар
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Определяем столбцы
        columns = ('foreign', 'translation', 'study_language', 'native_language', 'category', 'difficulty')
        
        # Создаем таблицу
        tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show='headings',
            yscrollcommand=scrollbar.set,
            height=20
        )
        
        # Настраиваем скроллбар
        scrollbar.config(command=tree.yview)
        
        # Настраиваем колонки с сортировкой
        columns_config = [
            ('foreign', 'Иностранное слово', 200),
            ('translation', 'Перевод', 200),
            ('study_language', 'Изучаемый язык', 150),
            ('native_language', 'Родной язык', 150),
            ('category', 'Категория', 150),
            ('difficulty', 'Сложность', 100)
        ]
        
        # Словарь для направления сортировки
        sort_directions = {col: False for col, _, _ in columns_config}
        
        def treeview_sort_column(col, reverse):
            data = [(tree.set(child, col), child) for child in tree.get_children('')]
            
            if col == 'difficulty':
                data.sort(key=lambda x: int(x[0].replace('%', '')), reverse=reverse)
            else:
                data.sort(key=lambda x: x[0].lower(), reverse=reverse)
            
            for index, (_, child) in enumerate(data):
                tree.move(child, '', index)
            
            sort_directions[col] = not reverse
            update_sort_indicators()
        
        def on_header_click(col):
            reverse = sort_directions[col]
            treeview_sort_column(col, reverse)
        
        def update_sort_indicators():
            for col, name, _ in columns_config:
                direction = sort_directions[col]
                arrow = " ↑" if direction else " ↓"
                tree.heading(col, text=name + arrow)
        
        # Настраиваем колонки с обработчиками сортировки
        for col, name, width in columns_config:
            tree.heading(col, text=name, command=lambda c=col: on_header_click(c))
            tree.column(col, width=width)
        
        tree.pack(fill=tk.BOTH, expand=True)
        
        # Информация о количестве найденных слов
        filter_info = tk.Label(
            lang_frame,
            text="",
            font=('Segoe UI', 10),
            bg=config.COLORS['bg_dark'],
            fg=config.COLORS['text_secondary']
        )
        filter_info.pack(side=tk.LEFT, padx=(10, 0))
        
        def load_data():
            """Загружает данные в Treeview"""
            # Очищаем таблицу
            for item in tree.get_children():
                tree.delete(item)
            
            # Получаем все слова из модели
            all_words = controller.model.get_all_words()
            
            # ЭТАП 1: ФИЛЬТРАЦИЯ ПО ЯЗЫКАМ
            if not show_all_var.get():
                filtered_by_lang = []
                for word in all_words:
                    if ((word['language'] == controller.language and 
                         word['native_language'] == controller.native_language) or
                        (word['language'] == controller.native_language and 
                         word['native_language'] == controller.language)):
                        filtered_by_lang.append(word)
                current_words = filtered_by_lang
            else:
                current_words = all_words
            
            # ЭТАП 2: ФИЛЬТРАЦИЯ ПО КАТЕГОРИИ
            selected_category = category_var.get()
            if selected_category != "Все категории":
                filtered_by_category = []
                for word in current_words:
                    if word.get('category', "Основные") == selected_category:
                        filtered_by_category.append(word)
                current_words = filtered_by_category
            
            # Добавляем данные в таблицу
            for word in current_words:
                study_lang_name = config.LANGUAGES.get(word['language'], {}).get('name', word['language'])
                native_lang_name = config.LANGUAGES.get(word['native_language'], {}).get('name', word['native_language'])
                category = word.get('category', "Основные")
                difficulty = f"{word['difficulty']}%"
                
                tree.insert('', 'end', values=(
                    word['foreign'],
                    word['translation'],
                    study_lang_name,
                    native_lang_name,
                    category,
                    difficulty
                ))
            
            # Обновляем информацию о количестве
            count = len(current_words)
            filter_info.config(text=f"Найдено: {count} слов")
        
        # Первоначальная загрузка данных
        load_data()
        
        # ===== ИСПРАВЛЕНО: Кнопка закрытия большая по вертикали =====
        button_frame = tk.Frame(main_frame, bg=config.COLORS['bg_dark'])
        button_frame.pack(fill=tk.X, pady=20)
        
        # Создаем кнопку с явным указанием размера
        close_button = tk.Button(
            button_frame,
            text="Закрыть",
            font=('Segoe UI', 14, 'bold'),
            bg=config.COLORS['primary'],
            fg=config.COLORS['text'],
            bd=2,
            relief=tk.RAISED,
            padx=30,
            pady=20,        # увеличенный вертикальный отступ
            cursor='hand2',
            command=on_closing
        )
        close_button.pack()
        
        # Принудительно устанавливаем высоту кнопки
        close_button.config(height=3)  # высота в текстовых строках
