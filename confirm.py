import tkinter as tk

import ttkbootstrap as ttk
from ttkbootstrap.constants import *

from constants import ICON_PATH, resource_path


class ConfirmDialog(ttk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.set_icon()
        self.title("Подтверждение очистки")
        self.geometry("400x200")
        self.result = False

        # Основной фрейм
        main_frame = ttk.Frame(self)
        main_frame.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)

        # Сообщение
        lbl_text = "Все предыдущие PDF файлы будут удалены!\nПродолжить?"
        ttk.Label(main_frame, text=lbl_text, justify=tk.CENTER).pack(pady=10)

        # Кнопки
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=20)

        ttk.Button(
            btn_frame,
            text="Да, очистить",
            command=self.on_confirm,
            bootstyle=SUCCESS
        ).pack(side=tk.LEFT, padx=10)

        ttk.Button(
            btn_frame,
            text="Отмена",
            command=self.on_cancel,
            bootstyle=DANGER
        ).pack(side=tk.LEFT)

        self.center_window()

    def set_icon(self):
        try:
            self.iconbitmap(resource_path(ICON_PATH))
        except Exception as e:
            print(f"Ошибка загрузки иконки подтверждения: {str(e)}")

    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'+{x}+{y}')

    def on_confirm(self):
        self.result = True
        self.destroy()

    def on_cancel(self):
        self.result = False
        self.destroy()

    def show(self):
        self.grab_set()
        self.wait_window()
        return self.result
