import ttkbootstrap as ttk

from constants import ICON_PATH, resource_path
from converter import PDFConverter

if __name__ == "__main__":
    root = ttk.Window(themename="morph")
    try:
        root.iconbitmap(resource_path(ICON_PATH))
    except Exception as e:
        print(f"Не удалось загрузить иконку: {str(e)}")
    app = PDFConverter(root)
    root.mainloop()
