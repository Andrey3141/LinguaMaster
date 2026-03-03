"""
Диалоговые окна статистики и сложных слов
"""

import tkinter as tk
from tkinter import ttk
from config import config
from utils.notifications import show_notification

class StatsDialog:
    """Класс для отображения статистики"""
    
    @staticmethod
    def show_hard_words(controller):
        """Показывает окно со сложными словами"""
        # Проверяем, не открыт ли уже диалог
        if controller.is_dialog_open('hard_words'):
            controller.dialogs['hard_words'].lift()
            controller.dialogs['hard_words'].focus_set()
            return
        
        hard_words = controller.model.get_hard_words()
        
        if not hard_words:
            show_notification(
                controller.root,
                "Сложные слова",
                "У вас пока нет сложных слов!",
                "info"
            )
            return
        
        dialog = tk.Toplevel(controller.root)
        dialog.title("🎯 Сложные слова")
        dialog.geometry(config.WINDOW_SIZES['hard_words'])
        dialog.configure(bg=config.COLORS['bg_dark'])
        dialog.transient(controller.root)
        
        # Регистрируем диалог
        controller.register_dialog('hard_words', dialog)
        
        def on_closing():
            controller.unregister_dialog('hard_words')
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
            text=f"🎯 Сложные слова ({len(hard_words)})",
            font=('Segoe UI', 16, 'bold'),
            bg=config.COLORS['bg_dark'],
            fg=config.COLORS['text']
        ).pack(pady=(0, 20))
        
        # Показываем список сложных слов
        for i, word in enumerate(hard_words[:10]):
            word_frame = tk.Frame(main_frame, bg=config.COLORS['bg_card'], padx=15, pady=10)
            word_frame.pack(fill=tk.X, pady=5)
            
            tk.Label(
                word_frame,
                text=f"{word['foreign']} → {word['translation']}",
                font=('Segoe UI', 11),
                bg=config.COLORS['bg_card'],
                fg=config.COLORS['text']
            ).pack(side=tk.LEFT)
            
            tk.Label(
                word_frame,
                text=f"{word['difficulty']}%",
                font=('Segoe UI', 10),
                bg=config.COLORS['bg_card'],
                fg=config.COLORS['warning']
            ).pack(side=tk.RIGHT)
        
        if len(hard_words) > 10:
            tk.Label(
                main_frame,
                text=f"... и еще {len(hard_words) - 10} слов",
                font=('Segoe UI', 10),
                bg=config.COLORS['bg_dark'],
                fg=config.COLORS['text_secondary']
            ).pack(pady=10)
        
        # Кнопка тренировки
        def train_hard_words():
            controller.difficulty = 'hard'
            controller.next_word()
            on_closing()
        
        tk.Button(
            main_frame,
            text="🎯 Тренировать эти слова",
            font=('Segoe UI', 12, 'bold'),
            bg=config.COLORS['warning'],
            fg=config.COLORS['text'],
            bd=0,
            padx=30,
            pady=10,
            cursor='hand2',
            command=train_hard_words
        ).pack(pady=20)
    
    @staticmethod
    def show_detailed_stats(controller):
        """Показывает подробную статистику с прокруткой"""
        # Проверяем, не открыт ли уже диалог
        if controller.is_dialog_open('stats'):
            controller.dialogs['stats'].lift()
            controller.dialogs['stats'].focus_set()
            return
        
        stats = controller.model.get_stats()
        
        dialog = tk.Toplevel(controller.root)
        dialog.title("📊 Подробная статистика")
        dialog.geometry("600x600")
        dialog.configure(bg=config.COLORS['bg_dark'])
        dialog.transient(controller.root)
        
        # Регистрируем диалог
        controller.register_dialog('stats', dialog)
        
        def on_closing():
            controller.unregister_dialog('stats')
            dialog.destroy()
        
        dialog.protocol("WM_DELETE_WINDOW", on_closing)
        
        try:
            dialog.grab_set()
        except:
            pass
        
        controller._center_dialog(dialog)
        
        # Основной контейнер с Canvas для прокрутки
        canvas = tk.Canvas(dialog, bg=config.COLORS['bg_dark'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(dialog, orient="vertical", command=canvas.yview)
        
        # Фрейм для контента внутри Canvas
        content_frame = tk.Frame(canvas, bg=config.COLORS['bg_dark'])
        
        # Настраиваем Canvas для прокрутки
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Упаковываем элементы
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Создаем окно в Canvas для контента
        canvas_window = canvas.create_window((0, 0), window=content_frame, anchor="nw")
        
        # Заголовок
        tk.Label(
            content_frame,
            text="📊 Подробная статистика",
            font=('Segoe UI', 16, 'bold'),
            bg=config.COLORS['bg_dark'],
            fg=config.COLORS['text']
        ).pack(pady=(20, 20), padx=20)
        
        # Статистические карточки
        stats_data = [
            ("Всего слов", str(stats['total_words']), "📚", config.COLORS['primary']),
            ("Изучено слов", str(stats['learned_words']), "🎓", config.COLORS['success']),
            ("Сложных слов", str(stats['hard_words']), "🎯", config.COLORS['warning']),
            ("Слов сегодня", str(stats['daily_words']), "📅", config.COLORS['accent']),
            ("Правильно сегодня", f"{stats['correct_today']}/{stats['daily_words']}", "✅", config.COLORS['success']),
            ("Точность сегодня", f"{stats['accuracy_today']:.1f}%", "🎯", config.COLORS['primary']),
            ("Процент изучения", f"{stats['progress']:.1f}%", "📈", config.COLORS['accent']),
        ]
        
        for title, value, icon, color in stats_data:
            card_frame = tk.Frame(content_frame, bg=config.COLORS['bg_card'], padx=15, pady=15)
            card_frame.pack(fill=tk.X, pady=5, padx=20)
            
            tk.Label(
                card_frame,
                text=icon,
                font=('Segoe UI', 20),
                bg=config.COLORS['bg_card'],
                fg=color
            ).pack(side=tk.LEFT, padx=(0, 15))
            
            text_frame = tk.Frame(card_frame, bg=config.COLORS['bg_card'])
            text_frame.pack(side=tk.LEFT, fill=tk.Y)
            
            tk.Label(
                text_frame,
                text=title,
                font=('Segoe UI', 10),
                bg=config.COLORS['bg_card'],
                fg=config.COLORS['text_secondary']
            ).pack(anchor='w')
            
            tk.Label(
                text_frame,
                text=value,
                font=('Segoe UI', 18, 'bold'),
                bg=config.COLORS['bg_card'],
                fg=config.COLORS['text']
            ).pack(anchor='w')
        
        # Дополнительная статистика (если есть)
        if stats['total_words'] > 0:
            accuracy = (stats['learned_words'] / stats['total_words'] * 100) if stats['total_words'] > 0 else 0
            extra_stats = [
                (f"Средняя точность: {accuracy:.1f}%", "📊"),
                (f"Слов в работе: {stats['total_words'] - stats['learned_words']}", "🔄"),
                ("Текущий язык обучения: " + config.LANGUAGES.get(controller.language, {}).get('name', controller.language), "🌐"),
            ]
            
            for text, icon in extra_stats:
                extra_frame = tk.Frame(content_frame, bg=config.COLORS['bg_dark'], padx=20, pady=5)
                extra_frame.pack(fill=tk.X, pady=5)
                
                tk.Label(
                    extra_frame,
                    text=f"{icon} {text}",
                    font=('Segoe UI', 10),
                    bg=config.COLORS['bg_dark'],
                    fg=config.COLORS['text_secondary'],
                    justify='left'
                ).pack(anchor='w')
        
        # Кнопка закрытия
        close_frame = tk.Frame(content_frame, bg=config.COLORS['bg_dark'])
        close_frame.pack(pady=20, padx=20)
        
        tk.Button(
            close_frame,
            text="Закрыть",
            font=('Segoe UI', 12),
            bg=config.COLORS['primary'],
            fg=config.COLORS['text'],
            bd=0,
            padx=30,
            pady=10,
            cursor='hand2',
            command=on_closing
        ).pack()
        
        # Настраиваем прокрутку
        def configure_scroll(event):
            content_frame.update_idletasks()
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.itemconfig(canvas_window, width=event.width)
        
        content_frame.bind("<Configure>", configure_scroll)
        canvas.bind("<Configure>", configure_scroll)
        
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        
        canvas.bind_all("<MouseWheel>", on_mousewheel)
