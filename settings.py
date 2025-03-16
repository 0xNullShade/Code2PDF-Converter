import tkinter as tk
from tkinter import ttk, messagebox

import ttkbootstrap as ttk
from ttkbootstrap.constants import *

from constants import ICON_PATH, resource_path
from utils import parse_input, save_settings


class SettingsWindow(ttk.Toplevel):
    def __init__(self, parent, settings, callback):
        super().__init__(parent)
        self.set_icon()
        self.settings = settings
        self.callback = callback
        self.title("Настройки конвертации")
        self.geometry("700x600")
        self.resizable(False, False)
        self.create_widgets()
        self.center_window()

    def set_icon(self):
        try:
            self.iconbitmap(resource_path(ICON_PATH))
        except Exception as e:
            print(f"Ошибка загрузки иконки настроек: {str(e)}")

    def create_widgets(self):
        main_frame = ttk.Frame(self)
        main_frame.pack(pady=15, padx=20, fill=tk.BOTH, expand=True)

        # Включаемые элементы
        incl_frame = ttk.LabelFrame(main_frame, text="Включаемые элементы", padding=10)
        incl_frame.pack(fill=tk.X, pady=5)

        ttk.Label(incl_frame, text="Укажите через запятую:").pack(anchor=tk.W)
        self.incl_entry = ttk.Text(incl_frame, height=5, wrap=tk.WORD)
        initial_incl = ', '.join(self.settings['extensions'] + self.settings['specific_files'])
        self.incl_entry.insert('1.0', initial_incl)
        self.incl_entry.pack(fill=tk.X, pady=5)

        # Исключения
        excl_frame = ttk.LabelFrame(main_frame, text="Исключения", padding=10)
        excl_frame.pack(fill=tk.X, pady=5)

        ttk.Label(excl_frame, text="Укажите через запятую:").pack(anchor=tk.W)
        self.excl_entry = ttk.Text(excl_frame, height=4, wrap=tk.WORD)
        initial_excl = ', '.join(self.settings['exclusions'])
        self.excl_entry.insert('1.0', initial_excl)
        self.excl_entry.pack(fill=tk.X, pady=5)

        # Инструкция
        help_frame = ttk.LabelFrame(main_frame, text="Инструкция", padding=10)
        help_frame.pack(fill=tk.X, pady=10)

        help_text = (
            "Формат ввода:\n"
            "• Для расширений: java, html, xml\n"
            "• Для конкретных файлов: config.xml, README.md\n"
            "• В исключении только файлы: file.txt, temp.html\n\n"
            "Пример:\n"
            "java, xml, application.properties, .gitignore"
        )
        ttk.Label(help_frame, text=help_text, justify=tk.LEFT).pack(anchor=tk.W)

        # Кнопки
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=15)

        ttk.Button(
            btn_frame,
            text="Сохранить",
            command=self.save,
            width=12,
            bootstyle=(SUCCESS, OUTLINE)
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            btn_frame,
            text="Отмена",
            command=self.destroy,
            width=12,
            bootstyle=(DANGER, OUTLINE)
        ).pack(side=tk.LEFT, padx=5)

    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'+{x}+{y}')

    def save(self):
        try:
            # Парсим введенные данные
            incl_text = self.incl_entry.get('1.0', tk.END).strip()
            excl_text = self.excl_entry.get('1.0', tk.END).strip()

            extensions, specific_files = parse_input(incl_text)
            exclusions = [x.strip() for x in excl_text.split(',') if x.strip()]

            new_settings = {
                'extensions': extensions,
                'specific_files': specific_files,
                'exclusions': exclusions
            }

            # Сохраняем в файл
            save_settings(new_settings)

            # Обновляем основной интерфейс
            self.callback(new_settings)
            self.destroy()

        except Exception as e:
            messagebox.showerror(
                "Ошибка сохранения",
                f"Не удалось сохранить настройки:\n{str(e)}",
                parent=self
            )

    def show(self):
        self.grab_set()
        self.wait_window()
        return self.settings
