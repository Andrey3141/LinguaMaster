#!/usr/bin/env python3
"""
Точка входа в приложение тренажера иностранных слов
"""

import tkinter as tk
from views.main_window import MainWindow

def main():
    """Запуск приложения"""
    root = tk.Tk()
    app = MainWindow(root)
    
    # Центрируем окно
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    root.mainloop()

if __name__ == "__main__":
    main()
