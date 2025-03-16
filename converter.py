import os
import shutil
import tkinter as tk
from queue import Queue
from threading import Thread, Event
from tkinter import filedialog, messagebox

import ttkbootstrap as ttk
from PyPDF2 import PdfMerger
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from ttkbootstrap.constants import *

from confirm import ConfirmDialog
from constants import ICON_PATH, FONT_DIR, resource_path
from settings import SettingsWindow
from utils import load_settings


class PDFConverter:
    def __init__(self, root):
        self.set_icon()
        self.root = root
        self.stop_event = Event()
        self.queue = Queue()
        self.settings = load_settings()
        self.setup_gui()
        self.check_queue()
        pdfmetrics.registerFont(TTFont('DejaVuSansMono', resource_path(FONT_DIR + '/DejaVuSansMono.ttf')))
        pdfmetrics.registerFont(TTFont('DejaVuSansMono-Bold', resource_path(FONT_DIR + '/DejaVuSansMono-Bold.ttf')))

    def set_icon(self):
        try:
            self.root.iconbitmap(resource_path(ICON_PATH))
        except Exception as e:
            print(f"Ошибка загрузки иконки: {str(e)}")

    def setup_gui(self):
        self.root.title("Code2PDF Converter")
        self.root.geometry("700x560")

        style = ttk.Style()
        style.configure('TLabel', font=('Helvetica', 10))
        style.configure('TButton', font=('Helvetica', 10))
        style.configure('TCheckbutton', font=('Helvetica', 10))

        # Project Directory Frame
        frame_project = ttk.Frame(self.root)
        frame_project.pack(pady=10, padx=20, fill=tk.X)

        ttk.Label(frame_project, text="Директория проекта:").pack(anchor=tk.W)
        self.entry_project = ttk.Entry(frame_project)
        self.entry_project.pack(fill=tk.X, pady=5)
        ttk.Button(
            frame_project,
            text="Обзор...",
            command=lambda: self.select_directory(self.entry_project),
            bootstyle=INFO
        ).pack(pady=5)

        # Output Directory Frame
        frame_output = ttk.Frame(self.root)
        frame_output.pack(pady=10, padx=20, fill=tk.X)

        ttk.Label(frame_output, text="Выходная директория:").pack(anchor=tk.W)
        self.entry_output = ttk.Entry(frame_output)
        self.entry_output.pack(fill=tk.X, pady=5)
        ttk.Button(
            frame_output,
            text="Обзор...",
            command=lambda: self.select_directory(self.entry_output),
            bootstyle=INFO
        ).pack(pady=5)

        # Options Frame
        frame_options = ttk.Frame(self.root)
        frame_options.pack(pady=10, padx=20, fill=tk.X)

        self.var_individual = tk.BooleanVar(value=True)
        self.var_combined = tk.BooleanVar(value=True)

        ttk.Checkbutton(
            frame_options,
            text="Создать отдельные PDF файлы",
            variable=self.var_individual,
            bootstyle=TOOLBUTTON
        ).pack(anchor=tk.W, pady=5)

        ttk.Checkbutton(
            frame_options,
            text="Объединить в один PDF файл",
            variable=self.var_combined,
            bootstyle=TOOLBUTTON
        ).pack(anchor=tk.W, pady=5)

        # Clean Frame
        frame_clean = ttk.Frame(self.root)
        frame_clean.pack(pady=5, padx=20, fill=tk.X)

        self.var_clean = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            frame_clean,
            text="Очистить выходную директорию перед конвертацией",
            variable=self.var_clean,
            bootstyle=TOOLBUTTON
        ).pack(anchor=tk.W)

        # Progress Frame
        frame_progress = ttk.Frame(self.root)
        frame_progress.pack(pady=10, padx=20, fill=tk.X)

        ttk.Label(frame_progress, text="Прогресс:").pack(anchor=tk.W)
        self.progress = ttk.Progressbar(frame_progress, maximum=100, bootstyle=SUCCESS)
        self.progress.pack(fill=tk.X, pady=5)

        # Settings Button
        ttk.Button(
            self.root,
            text="Настройки файлов",
            command=self.show_settings,
            bootstyle=WARNING
        ).pack(pady=10)

        # Start Button
        ttk.Button(
            self.root,
            text="Сгенерировать PDF",
            command=self.start_processing,
            bootstyle=SUCCESS
        ).pack(pady=20)

    def check_queue(self):
        while not self.queue.empty():
            msg = self.queue.get()
            if msg == "update_progress":
                self.progress['value'] += 1
                self.root.update_idletasks()
            elif msg == "complete":
                messagebox.showinfo("Готово", "PDF файлы успешно созданы!")
                self.progress['value'] = 0
                self.stop_event.set()
            elif isinstance(msg, Exception):
                messagebox.showerror("Ошибка", f"Произошла ошибка:\n{str(msg)}")
                self.progress['value'] = 0
                self.stop_event.set()
        self.root.after(100, self.check_queue)

    def create_pdf_from_file(self, filepath, output_dir):
        """Создание PDF из одного файла с заголовком"""
        try:
            filename = os.path.basename(filepath)
            parts_dir = os.path.join(output_dir, "parts")
            os.makedirs(parts_dir, exist_ok=True)
            pdf_path = os.path.join(parts_dir, f"{filename}.pdf")

            with open(filepath, 'r', encoding='utf-8') as file:
                content = file.read()

            c = canvas.Canvas(pdf_path, pagesize=letter)
            width, height = letter
            y_position = height - 40
            page_number = 1

            # Добавляем заголовок
            c.setFont("DejaVuSansMono-Bold", 12)
            header = f"{filename}:"
            c.drawString(40, y_position, header)
            y_position -= 20

            # Основной текст
            c.setFont("DejaVuSansMono", 10)
            text = c.beginText(40, y_position)

            for line in content.split('\n'):
                text.textLine(line.strip('\r'))
                y_position -= 15
                if y_position < 40:
                    # Завершаем текущую страницу
                    c.drawText(text)
                    c.showPage()
                    page_number += 1
                    y_position = height - 40

                    # Добавляем заголовок на новой странице
                    if page_number > 1:
                        c.setFont("DejaVuSansMono-Bold", 12)
                        c.drawString(40, y_position, f"{filename} (продолжение):")
                        y_position -= 20
                        c.setFont("DejaVuSansMono", 10)

                    text = c.beginText(40, y_position)

            c.drawText(text)
            c.save()
            return pdf_path
        except Exception as e:
            return None

    def process_files(self):
        try:
            project_dir = self.entry_project.get()
            output_dir = self.entry_output.get()

            if not project_dir or not output_dir:
                self.queue.put(ValueError("Выберите все директории!"))
                return

            os.makedirs(output_dir, exist_ok=True)

            all_files = []
            for root, _, files in os.walk(project_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    if self.should_convert(file_path):
                        all_files.append(file_path)

            self.progress['maximum'] = len(all_files) if all_files else 1
            pdf_files = []

            if self.var_individual.get() and all_files:
                for file in all_files:
                    if self.stop_event.is_set():
                        return
                    pdf_path = self.create_pdf_from_file(file, output_dir)
                    if pdf_path:
                        pdf_files.append(pdf_path)
                        self.queue.put("update_progress")

            if self.var_combined.get() and pdf_files:
                combined_dir = os.path.join(output_dir, "combined-parts")
                os.makedirs(combined_dir, exist_ok=True)

                extensions = {}
                for pdf in pdf_files:
                    ext = os.path.splitext(os.path.basename(pdf))[0].split('.')[-1]
                    if ext not in extensions:
                        extensions[ext] = []
                    extensions[ext].append(pdf)

                for ext, files in extensions.items():
                    merger = PdfMerger()
                    for pdf in files:
                        merger.append(pdf)
                    merger.write(os.path.join(combined_dir, f"combined-{ext}.pdf"))
                    merger.close()

            self.queue.put("complete")

        except Exception as e:
            self.queue.put(e)

    def should_convert(self, file_path):
        filename = os.path.basename(file_path)
        file_ext = os.path.splitext(filename)[1][1:].lower()

        if filename in self.settings['exclusions']:
            return False

        if filename in self.settings['specific_files']:
            return True

        return file_ext in self.settings['extensions']

    def clean_output_directory(self, output_dir):
        try:
            if not os.path.exists(output_dir):
                return True

            dirs_to_remove = ["parts", "combined-parts"]
            files_to_remove = ["combined.pdf"]

            for dir_name in dirs_to_remove:
                dir_path = os.path.join(output_dir, dir_name)
                if os.path.exists(dir_path):
                    shutil.rmtree(dir_path)

            for file_name in files_to_remove:
                file_path = os.path.join(output_dir, file_name)
                if os.path.exists(file_path):
                    os.remove(file_path)

            return True
        except Exception as e:
            self.queue.put(e)
            return False

    def start_processing(self):
        if self.var_clean.get():
            output_dir = self.entry_output.get()

            if not output_dir:
                messagebox.showerror("Ошибка", "Сначала укажите выходную директорию!")
                return

            if not ConfirmDialog(self.root).show():
                return

            if not self.clean_output_directory(output_dir):
                return

        self.stop_event.clear()
        self.progress['value'] = 0
        Thread(target=self.process_files, daemon=True).start()

    def select_directory(self, entry):
        path = filedialog.askdirectory()
        if path:
            entry.delete(0, tk.END)
            entry.insert(0, path)

    def show_settings(self):
        SettingsWindow(self.root, self.settings, self.update_settings)

    def update_settings(self, new_settings):
        self.settings = new_settings


if __name__ == "__main__":
    root = ttk.Window(themename="morph")
    app = PDFConverter(root)
    root.mainloop()
