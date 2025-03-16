import json
import logging
import os

from constants import SETTINGS_FILE, resource_path

DEFAULT_SETTINGS = {
    'extensions': ['java', 'html'],
    'specific_files': ['application.properties'],
    'exclusions': ['problems-report.html']
}


def parse_input(text):
    """Анализирует ввод пользователя и разделяет на расширения и конкретные файлы"""
    extensions = []
    specific_files = []

    # Нормализация ввода: удаление переносов строк и лишних пробелов
    items = [item.strip() for item in text.replace('\n', ',').split(',') if item.strip()]

    for item in items:
        if '.' in item:
            # Если содержит точку - считаем конкретным файлом
            if item.count('.') > 1:
                # Игнорируем некорректные записи вроде "file.name.txt"
                continue
            specific_files.append(item)
        else:
            # Без точки - расширение (приводим к нижнему регистру)
            extensions.append(item.lower())

    # Удаляем дубликаты
    return list(set(extensions)), list(set(specific_files))


def save_settings(settings):
    try:
        with open(resource_path(SETTINGS_FILE), 'w', encoding='utf-8') as f:
            json.dump(settings, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        logging.error(f"Ошибка сохранения настроек: {str(e)}")
        return False


def load_settings():
    try:
        if os.path.exists(resource_path(SETTINGS_FILE)):
            with open(resource_path(SETTINGS_FILE), 'r', encoding='utf-8') as f:
                return json.load(f)
        return DEFAULT_SETTINGS.copy()
    except Exception as e:
        logging.error(f"Ошибка загрузки настроек: {str(e)}")
        return DEFAULT_SETTINGS.copy()
