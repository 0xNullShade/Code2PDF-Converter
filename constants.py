import os
import sys


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


ICON_PATH = resource_path('img/app_icon.ico')
FONT_DIR = resource_path('fonts/')
SETTINGS_FILE = resource_path('json/code2pdf_settings.json')
