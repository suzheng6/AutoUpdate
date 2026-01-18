import sys
import re
import keyboard
import pyperclip
import pyautogui
import webbrowser
from PyQt5.QtWidgets import (
    QApplication, QWidget, QTextEdit, QLabel, QVBoxLayout, QPushButton
)
from PyQt5.QtCore import Qt, QThread


class HotkeyListener(QThread):
    def __init__(self, extract_url, extract_number):
        super().__init__()
        self.extract_url = extract_url
        self.extract_number = extract_number

    def run(self):
        keyboard.add_hotkey("F4", self.extract_url)
        keyboard.add_hotkey("F3", self.extract_number)
        keyboard.wait()


class ExtractorApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("文本提取工具 · Pro")
        self.setFixedSize(520, 420)

        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText(
            "粘贴文本，每行格式：\n"
            "+919411611324|https://xxx.xxx\n\n"
            "F4 打开网址\nF3 提取数字"
        )

        self.status_label = QLabel("状态：等待操作")
        self.status_label.setAlignment(Qt.AlignCenter)

        self.clear_btn = QPushButton("清空文本")
        self.clear_btn.clicked.connect(self.text_edit.clear)

        layout = QVBoxLayout()
        layout.addWidget(self.text_edit)
        layout.addWidget(self.status_label)
        layout.addWidget(self.clear_btn)

        self.setLayout(layout)

        self.lines = []
        self.url_index = 0
        self.num_index = 0

        self.listener = HotkeyListener(
            self.extract_next_url,
            self.extract_next_number
        )
        self.listener.start()

    def load_lines(self):
        text = self.text_edit.toPlainText().strip()
        self.lines = [line for line in text.splitlines() if "|" in line]

    def extract_next_url(self):
        self.load_lines()
        if self.url_index >= len(self.lines):
            self.status_label.setText("网址提取完毕")
            return

        line = self.lines[self.url_index]
        self.url_index += 1

        match = re.search(r"https?://\S+", line)
        if match:
            url = match.group()
            webbrowser.open(url)  # 🚀 直接打开网址
            self.status_label.setText(f"已打开网址：{url}")

    def extract_next_number(self):
        self.load_lines()
        if self.num_index >= len(self.lines):
            self.status_label.setText("数字提取完毕")
            return

        line = self.lines[self.num_index]
        self.num_index += 1

        phone = line.split("|")[0]
        digits = re.sub(r"\D", "", phone)

        if len(digits) > 2:
            result = digits[2:]
            self.copy_and_paste(result)
            self.status_label.setText(f"已提取数字：{result}")

    def copy_and_paste(self, text):
        pyperclip.copy(text)
        pyautogui.hotkey("ctrl", "v")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = ExtractorApp()
    win.show()
    sys.exit(app.exec_())
