import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QDesktopWidget, QLineEdit
from PyQt5.QtGui import QIcon
from main import Ui_MainWindow
from PyQt5.QtCore import QStringListModel
from time import sleep
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QIcon, QTransform
from PyQt5.QtCore import QSize
import pytesseract
import easygui
from PIL import Image
import docx
import os
import arabic_reshaper
from bidi.algorithm import get_display
import io
import fitz  # PyMuPDF
import tkinter as tk
from tkinter import filedialog
import requests
from googletrans import Translator
import webbrowser

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.center()
        self.setFixedSize(self.size())

        self.collapse_top.clicked.connect(self.toggle_top_table_visibility)  # type: ignore
        self.cleartext.clicked.connect(self.translate_show.clear)  # type: ignore
        self.bottom_table.itemClicked['QTableWidgetItem*'].connect(self.third_language_down.update)  # type: ignore
        self.collapse_down.clicked.connect(self.toggle_down_table_visibility)  # type: ignore
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        # اتصال سیگنال کلیک جدول به تابع
        self.top_table.cellClicked.connect(self.select_source_language)
        self.bottom_table.cellClicked.connect(self.select_target_language)

        # انتخاب یکی از دو حالت برای زبان مرجع
        self.first_language_top.clicked.connect(self.toggle_button_first_top)
        self.Detected_language_button.clicked.connect(self.toggle_button_detected)

        self.reverse_button.clicked.connect(self.reverse_language)

        self.first_language_down.clicked.connect(self.update_selected_la_dict)
        self.second_language_down.clicked.connect(self.update_selected_la_dict)
        self.third_language_down.clicked.connect(self.update_selected_la_dict)

        # انتخاب عکس و استخراج متن
        # self.import_image.clicked.connect(self.read_image_and_update_text)

        self.import_file.clicked.connect(self.extract_text_from_file)

        self.import_pdf.clicked.connect(self.import_and_read_pdf_file)

        self.openurl.clicked.connect(self.open_and_translate)

        # زبان‌های انتخاب شده برای ترجمه
        self.selected_languages = {}

        # functions

    # انتخاب زبان هدف
    def select_target_language(self, row, column):
        selected_language = self.bottom_table.item(row, column).text()
        self.bottom_table.hide()
        if selected_language.lower() not in [self.second_language_down.text(), self.third_language_down.text(),
                                             self.first_language_down.text()]:
            sbt = self.second_language_down.text()
            self.second_language_down.setText(self.first_language_down.text())
            self.third_language_down.setText(sbt)
            self.first_language_down.setText(selected_language.lower())
            self.first_language_down.setChecked(True)
            self.selected_languages["target"] = self.first_language_down.text()
            self.collapse_down.setIcon(QIcon(':/newPrefix/icons8-expand-arrow-64.png'))

    def open_file_dialog(self, filetypes=[('PDF files', "*.pdf")]):
        file_path = filedialog.askopenfilename(filetypes=filetypes)
        if file_path:
            return file_path

    # انتخاب زبان مرجع
    def select_source_language(self, row, column):
        selected_language = self.top_table.item(row, column).text()
        self.top_table.hide()
        self.first_language_top.setText(selected_language)
        self.collapse_top.setIcon(QIcon(':/newPrefix/icons8-expand-arrow-64.png'))

    # پنهان کردن جدول زبان‌های بالایی
    def toggle_top_table_visibility(self):
        if self.top_table.isVisible():
            self.top_table.hide()  # پنهان کردن جدول
            sleep(0.10)
            self.collapse_top.setIcon(QIcon(':/newPrefix/icons8-expand-arrow-64.png'))
        else:
            self.top_table.show()  # ظاهر کردن جدول
            sleep(0.10)
            self.collapse_top.setIcon(QIcon(':/newPrefix/icons8-collapse-arrow-64.png'))

            # پنهان کردن جدول زبان‌های پایینی

    def toggle_down_table_visibility(self):
        if self.bottom_table.isVisible():
            self.bottom_table.hide()  # پنهان کردن جدول
            sleep(0.10)
            self.collapse_down.setIcon(QIcon(':/newPrefix/icons8-expand-arrow-64.png'))
        else:
            self.bottom_table.show()  # ظاهر کردن جدول
            sleep(0.10)
            self.collapse_down.setIcon(QIcon(':/newPrefix/icons8-collapse-arrow-64.png'))

    # تغییر وضعیت متناوب فعال بودن دکمه‌های زبان بالایی
    def toggle_button_first_top(self):
        self.Detected_language_button.setChecked(False)
        self.first_language_top.setChecked(True)
        self.selected_languages["source"] = self.first_language_top.text()
        print(self.selected_languages)

    def toggle_button_detected(self):
        self.Detected_language_button.setChecked(True)
        self.first_language_top.setChecked(False)

    def reverse_language(self):
        # در صورتی که دکمه تشخیص زبان خودکار فعال نیست
        if not self.Detected_language_button.isChecked():
            result = ""
            if self.first_language_down.isChecked():
                result = self.first_language_down
            elif self.second_language_down.isChecked():
                result = self.second_language_down
            elif self.third_language_down.isChecked():
                result = self.third_language_down
            if result != "":
                i = result.text()
                result.setText(self.first_language_top.text())
                self.first_language_top.setText(i)
                self.selected_languages["target"], self.selected_languages["source"] = \
                    self.selected_languages["source"], self.selected_languages["target"]

    # بروزرسانی زبان هدف
    def update_selected_la_dict(self):
        if self.first_language_down.isChecked():
            self.selected_languages["target"] = self.first_language_down.text()
        elif self.second_language_down.isChecked():
            self.selected_languages["target"] = self.second_language_down
        elif self.third_language_down.isChecked():
            self.selected_languages["target"] = self.third_language_down

    # بروزرسانی متن ترجمه
    def read_image_and_update_text(self):
        newtext = self.select_image_and_read()
        self.input_text_box.setText(newtext)

    # انتخاب عکس و استخراج متن
    def select_image_and_read(self):
        languages = {
            "english": "eng",
            "arabic": "ara",
            "french": "fra",
            "german": "deu",
            "spanish": "spa",
            "russian": "rus",
            "chinese": "chi_sim",  # Simplified Chinese
            "japanese": "jpn",
            "korean": "kor",
            "italian": "ita",
            "portuguese": "por",
            "dutch": "nld",
            "turkish": "tur",
            "hindi": "hin",
            "urdu": "urd",
            "swedish": "swe",
            "persian": "fas",
            "czech": "ces"
        }
        # انتخاب فایل تصویر
        image_path = self.open_file_dialog()
        lang_choice = easygui.choicebox("لطفاً زبان متن را انتخاب کنید:", "انتخاب زبان",
                                        list(languages.keys()))
        lang_code = languages[lang_choice]
        # استخراج متن
        img = Image.open(image_path)
        custom_config = r'--oem 3 --psm 6 -l ' + f"{lang_code}"
        text = pytesseract.image_to_string(img, config=custom_config)
        return text

    def show_message_box(self, text, title):
        """تبدیل متن فارسی برای نمایش صحیح از راست به چپ"""
        reshaped_text = arabic_reshaper.reshape(text)
        formatted_message = get_display(reshaped_text)
        formatted_title = get_display(arabic_reshaper.reshape(title))
        easygui.msgbox(formatted_message, formatted_title, ok_button=get_display(arabic_reshaper.reshape("تایید")))

    # استخراج متن از فایل
    def extract_text_from_file(self):
        text_to_translate = ""
        """
        این تابع متن را از فایل‌های Word (.docx) و متنی (.txt) استخراج می‌کند.
        :return: متن استخراج شده از فایل
        """
        # ایجاد پنجره پیام
        file_path = self.open_file_dialog(filetypes=[("text files", "*.docx", "*.doc", "*.txt")])

        # مسیر و پسوند فایل
        file_extension = os.path.splitext(file_path)
        if file_extension[1].lower() in ['.docx', ".doc"]:
            doc = docx.Document(file_path)
            full_text = []
            for para in doc.paragraphs:
                full_text.append(para.text)
            text_to_translate += '\n'.join(full_text)
        elif file_extension[1].lower() == '.txt':
            # استخراج متن از فایل متنی
            with open(file_path, 'r', encoding='utf-8') as file:
                text_to_translate = file.read()
        else:
            self.show_message_box("مشکلی متاسفانه رخ داده است", "خطا!")
        if text_to_translate:
            self.input_text_box.setText(text_to_translate)

    def import_and_read_pdf_file(self):
        pdfText = ""
        # مسیر فایل PDF خود را اینجا قرار دهید
        pdf_path = self.open_file_dialog()
        if pdf_path:
            # باز کردن فایل PDF
            pdf_document = fitz.open(pdf_path)
            # تعداد صفحات PDF را دریافت کنید
            num_pages = pdf_document.page_count
            # استخراج متن از هر صفحه
            for page_num in range(num_pages):
                page = pdf_document.load_page(page_num)
                text = page.get_text()
                pdfText += text
            self.input_text_box.setText(pdfText)
            # بستن فایل PDF
            pdf_document.close()

    def open_and_translate(self, target_language='fa'):
        url = easygui.enterbox("لطفاً آدرس وب‌سایت را وارد کنید:")
        languages = {
            "english": "eng",
            "arabic": "ara",
            "french": "fra",
            "german": "deu",
            "spanish": "spa",
            "russian": "rus",
            "chinese": "chi_sim",  # Simplified Chinese
            "japanese": "jpn",
            "korean": "kor",
            "italian": "ita",
            "portuguese": "por",
            "dutch": "nld",
            "turkish": "tur",
            "hindi": "hin",
            "urdu": "urd",
            "swedish": "swe",
            "persian": "fas",
            "czech": "ces"}
        lang_choice = easygui.choicebox("لطفاً زبان متن را انتخاب کنید:", "انتخاب زبان",
                                        list(languages.keys()))
        target_language = languages[lang_choice]

        if url:
            # آدرس ترجمه شده توسط Google Translate
            translate_url = f'https://translate.google.com/translate?sl=auto&tl={target_language}&u={url}'
            # باز کردن آدرس در یک تب جدید مرورگر پیش‌فرض
            webbrowser.open_new_tab(translate_url)
        else:
            easygui.msgbox("آدرسی وارد نشده است.", "خطا")


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
