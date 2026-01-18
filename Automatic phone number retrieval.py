import sys
import os
import json
import time
import keyboard

from PyQt5.QtWidgets import (
    QApplication, QWidget, QFileDialog,
    QLabel, QPushButton, QSpinBox,
    QTextEdit, QVBoxLayout, QHBoxLayout,
    QMessageBox, QCheckBox, QInputDialog
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QTimer


PROGRESS_FILE = "progress.json"


class TextExtractor(QWidget):
    def __init__(self):
        super().__init__()

        # ===== 基础窗口 =====
        self.setWindowTitle("Automatic text extraction · Global paste")
        self.resize(420, 280)
        self.setAcceptDrops(True)

        # ===== 核心状态 =====
        self.file_path = None
        self.lines = []
        self.current_line = 0

        self.hotkey_copy = "ctrl+alt+v"
        self.auto_send = False

        self._is_running = False
        self._finished_notified = False

        # ===== 启动流程 =====
        self._load_progress()
        self._build_ui()
        self._load_file_if_exists()
        self.bind_global_hotkey()

    # ================= UI =================

    def _build_ui(self):
        font_title = QFont("微软雅黑", 11, QFont.Bold)
        font_normal = QFont("微软雅黑", 9)

        title = QLabel("📄 Automatic text extraction tool")
        title.setFont(font_title)

        self.file_label = QLabel("Current file: Not selected")
        self.file_label.setFont(font_normal)

        self.line_label = QLabel("Currently copied to: row 0")
        self.line_label.setFont(font_normal)

        # 行数
        row_box = QHBoxLayout()
        row_box.addWidget(QLabel("Number of rows extracted each time:"))
        self.spin_lines = QSpinBox()
        self.spin_lines.setRange(1, 1000)
        self.spin_lines.setValue(5)
        row_box.addWidget(self.spin_lines)
        row_box.addStretch()

        # 按钮
        btn_box = QHBoxLayout()
        self.btn_open = QPushButton("📂 Open file")
        self.btn_copy = QPushButton("📋 Extract and copy")
        self.btn_hotkey = QPushButton("⌨ Set shortcut keys")

        btn_box.addWidget(self.btn_open)
        btn_box.addWidget(self.btn_copy)
        btn_box.addWidget(self.btn_hotkey)

        # 自动发送
        self.chk_auto_send = QCheckBox("Send automatically after pasting（Enter）")
        self.chk_auto_send.setChecked(self.auto_send)
        self.chk_auto_send.stateChanged.connect(self._on_auto_send_changed)

        # 预览
        self.preview = QTextEdit()
        self.preview.setReadOnly(True)
        self.preview.setFixedHeight(90)

        # 绑定
        self.btn_open.clicked.connect(self.open_file)
        self.btn_copy.clicked.connect(self.extract_and_copy)
        self.btn_hotkey.clicked.connect(self.set_hotkey)

        # 布局
        layout = QVBoxLayout()
        layout.addWidget(title)
        layout.addWidget(self.file_label)
        layout.addWidget(self.line_label)
        layout.addLayout(row_box)
        layout.addLayout(btn_box)
        layout.addWidget(self.chk_auto_send)
        layout.addWidget(self.preview)

        self.setLayout(layout)
        self._apply_style()

    def _apply_style(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;
                color: #dddddd;
            }
            QPushButton {
                background-color: #2d89ef;
                border-radius: 5px;
                padding: 5px 10px;
                color: white;
            }
            QPushButton:hover {
                background-color: #1b5fbd;
            }
            QTextEdit {
                background-color: #2a2a2a;
                border-radius: 5px;
                padding: 6px;
            }
        """)

    # ================= 文件 =================

    def open_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select text file", "", "Text Files (*.txt)"
        )
        if path:
            self.load_file(path)

    def load_file(self, path, reset_position=True):
        if not os.path.exists(path):
            return

        self.file_path = path
        if reset_position:
            self.current_line = 0
        self._finished_notified = False

        with open(path, "r", encoding="utf-8") as f:
            self.lines = f.readlines()

        self.file_label.setText(f"Current file：{os.path.basename(path)}")
        self._update_line_label()
        self.preview.clear()
        self._save_progress()

    def _load_file_if_exists(self):
        if self.file_path and os.path.exists(self.file_path):
            self.load_file(self.file_path, reset_position=False)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        if not urls:
            return

        # 只取第一个文件
        path = urls[0].toLocalFile()

        # 只允许 txt
        if not path.lower().endswith(".txt"):
            QMessageBox.warning(self, "不支持的文件", "目前仅支持 .txt 文件")
            return

        # 拖入新文件，重置位置
        self.load_file(path, reset_position=True)

    # ================= 核心功能 =================

    def extract_and_copy(self):
        if not self.lines:
            return

        n = self.spin_lines.value()
        start = self.current_line
        end = min(start + n, len(self.lines))

        if start >= len(self.lines):
            return

        text = "".join(self.lines[start:end])
        QApplication.clipboard().setText(text)
        self.preview.setPlainText(text)

        self.current_line = end
        self._update_line_label()
        self._save_progress()

        # ⭐ 提取完成提示（只提示一次）
        if self.current_line >= len(self.lines) and not self._finished_notified:
            self._finished_notified = True
            QMessageBox.information(
                self,
                "Extraction complete",
                "📌 The entire contents of the current file have been extracted.。"
            )

    def extract_copy_and_paste(self):
        self.extract_and_copy()

        QApplication.processEvents()
        time.sleep(0.05)

        keyboard.press_and_release("ctrl+v")

        if self.auto_send:
            time.sleep(0.05)
            keyboard.press_and_release("enter")

    # ================= 全局热键（关键） =================

    def bind_global_hotkey(self):
        try:
            keyboard.unhook_all_hotkeys()
        except:
            pass

        keyboard.add_hotkey(
            self.hotkey_copy,
            self._on_global_hotkey,
            suppress=True
        )

    def _on_global_hotkey(self):
        if self._is_running:
            return

        self._is_running = True
        keyboard.unhook_all_hotkeys()
        QTimer.singleShot(0, self._safe_run)

    def _safe_run(self):
        try:
            self.extract_copy_and_paste()
        finally:
            QTimer.singleShot(300, self._restore_hotkey)

    def _restore_hotkey(self):
        self._is_running = False
        self.bind_global_hotkey()

    # ================= 设置 =================

    def set_hotkey(self):
        text, ok = QInputDialog.getText(
            self,
            "Set shortcut keys",
            "示例：ctrl+alt+v / ctrl+shift+v / ctrl+f2",
            text=self.hotkey_copy
        )
        if ok and text.strip():
            self.hotkey_copy = text.strip().lower()
            self._save_progress()
            self.bind_global_hotkey()

    def _on_auto_send_changed(self, state):
        self.auto_send = (state == Qt.Checked)
        self._save_progress()

    # ================= 状态 =================

    def _update_line_label(self):
        self.line_label.setText(f"Currently copied to：{self.current_line} row")

    def _save_progress(self):
        data = {
            "file_path": self.file_path,
            "current_line": self.current_line,
            "hotkey_copy": self.hotkey_copy,
            "auto_send": self.auto_send
        }
        with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _load_progress(self):
        if os.path.exists(PROGRESS_FILE):
            with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.file_path = data.get("file_path")
                self.current_line = data.get("current_line", 0)
                self.hotkey_copy = data.get("hotkey_copy", "ctrl+alt+v")
                self.auto_send = data.get("auto_send", False)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = TextExtractor()
    win.show()
    sys.exit(app.exec_())
