import sys
import os
import json
import time
import keyboard
import urllib.request
import subprocess
import sys

APP_VERSION = "1.1.0"

GITHUB_API = "https://api.github.com/repos/suzheng6/AutoUpdate/releases/latest"

from PyQt5.QtWidgets import (
    QApplication, QWidget, QFileDialog,
    QLabel, QPushButton, QSpinBox,
    QTextEdit, QVBoxLayout, QHBoxLayout,
    QMessageBox, QCheckBox, QInputDialog,QComboBox
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QTimer


PROGRESS_FILE = "progress.json"

def is_newer_version(latest, current):
    def normalize(v):
        return [int(x) for x in v.strip("v").split(".")]
    return normalize(latest) > normalize(current)

LANGUAGES = {
    "zh": {
        "title": "自动提取电话工具",
        "key": "⌨设置快捷键",
        "ui_title": "📄自动文本提取工具",
        "open_file": "📂打开文件",
        "extract_copy": "📋提取并复制",
        "auto_send": "粘贴后自动发送（Enter）",
        "extract_complete_title": "提取完成",
        "extract_complete_msg": "📌 当前文件内容已全部提取完成。",
        "current_line": "当前已复制到：{line} 行",
        "current_file": "当前文件：{name}",
        "lines_per_extract": "每次提取行数：",
        "update_title": "发现新版本",
        "update_msg": "发现新版本 {new}\n当前版本 {current}\n\n是否立即更新？",
        "yes": "是",
        "no": "否",
        "language": "语言",
        "chinese": "中文",
        "english": "English"
    },
    "en": {
        "title": "Auto Phone Extractor",
        "key": "⌨Set shortcut keys",
        "ui_title": "📄Auto Text Extraction Tool",
        "open_file": "📂Open File",
        "extract_copy": "📋Extract & Copy",
        "auto_send": "Auto send after paste (Enter)",
        "extract_complete_title": "Extraction Completed",
        "extract_complete_msg": "📌 All content in the file has been extracted.",
        "current_line": "Current position: {line} lines",
        "current_file": "Current file: {name}",
        "lines_per_extract": "Lines per extraction:",
        "update_title": "New Version Found",
        "update_msg": "New version {new} detected\nCurrent version: {current}\n\nUpdate now?",
        "yes": "Yes",
        "no": "No",
        "language": "Language",
        "chinese": "Chinese",
        "english": "English"
    }
}


class TextExtractor(QWidget):
    def __init__(self):
        super().__init__()

        self.language = "zh"   # 当前语言：zh / en

        # ===== 基础窗口 =====
        self.setWindowTitle(self.tr("title"))
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
        self._showing_finish_dialog = False

        # ===== 启动流程 =====
        self._load_progress()
        self._build_ui()
        self._load_file_if_exists()
        self.bind_global_hotkey()

        # ===== 调用更新检测 =====
        QTimer.singleShot(1500, self.check_and_update)

    # ================= UI =================

    def _build_ui(self):
        font_title = QFont("微软雅黑", 11, QFont.Bold)
        font_normal = QFont("微软雅黑", 9)

        self.ui_title_label = QLabel(self.tr("ui_title"))
        self.ui_title_label.setFont(font_title)

        self.file_label = QLabel("当前文件：未选择")
        self.file_label.setFont(font_normal)

        self.line_label = QLabel(self.tr("Currently_copied"))
        self.line_label.setFont(font_normal)

        # 行数
        row_box = QHBoxLayout()
        self.lines_label = QLabel(self.tr("lines_per_extract"))
        row_box.addWidget(self.lines_label)
        self.spin_lines = QSpinBox()
        self.spin_lines.setRange(1, 1000)
        self.spin_lines.setValue(5)
        row_box.addWidget(self.spin_lines)
        row_box.addStretch()

        # 按钮
        btn_box = QHBoxLayout()
        self.btn_open = QPushButton(self.tr("open_file"))
        self.btn_copy = QPushButton(self.tr("extract_copy"))
        self.btn_hotkey = QPushButton(self.tr("key"))

        self.lang_box = QComboBox()
        self.lang_box.addItem(self.tr("chinese"), "zh")
        self.lang_box.addItem(self.tr("english"), "en")

        # 根据当前语言设置默认选中
        self.lang_box.setCurrentIndex(0 if self.language == "zh" else 1)

        btn_box.addWidget(self.btn_open)
        btn_box.addWidget(self.btn_copy)
        btn_box.addWidget(self.btn_hotkey)

        # 自动发送
        self.chk_auto_send = QCheckBox(self.tr("auto_send"))
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
        layout.addWidget(self.ui_title_label)
        layout.addWidget(self.file_label)
        layout.addWidget(self.line_label)
        layout.addLayout(row_box)
        layout.addLayout(btn_box)
        layout.addWidget(self.chk_auto_send)
        layout.addWidget(self.preview)
        layout.addWidget(self.lang_box)

        self.lang_box.currentIndexChanged.connect(self.change_language)

        self.setLayout(layout)
        self._apply_style()

    def tr(self, key):
        return LANGUAGES.get(self.language, LANGUAGES["zh"]).get(key, key)

    def change_language(self):
        self.language = self.lang_box.currentData()
        self._save_progress()
        self.retranslate_ui()

    def retranslate_ui(self):
        # 窗口标题
        self.setWindowTitle(self.tr("title"))

        # 按钮
        self.btn_open.setText(self.tr("open_file"))
        self.btn_copy.setText(self.tr("extract_copy"))
        self.btn_hotkey.setText(self.tr("key"))

        # 复选框
        self.chk_auto_send.setText(self.tr("auto_send"))

        # 刷新动态文本（行数 / 文件名）
        self._update_line_label()

        if self.file_path:
            self.file_label.setText(
                self.tr("current_file").format(
                    name=os.path.basename(self.file_path)
                )
            )

        self.lines_label.setText(self.tr("lines_per_extract"))
        self.ui_title_label.setText(self.tr("ui_title"))

        # 语言下拉框本身的显示文本
        self.lang_box.blockSignals(True)
        self.lang_box.setItemText(0, self.tr("chinese"))
        self.lang_box.setItemText(1, self.tr("english"))
        self.lang_box.blockSignals(False)

    def check_and_update(self):
        try:
            req = urllib.request.Request(
                GITHUB_API,
                headers={"User-Agent": "AutoExtractor-Updater"}
            )
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode("utf-8"))

            latest_version = data["tag_name"].lstrip("v")
            asset = data["assets"][0]
            download_url = asset["browser_download_url"]

            if not is_newer_version(latest_version, APP_VERSION):
                return

            reply = QMessageBox.question(
                self,
                self.tr("update_title"),
                self.tr("update_msg").format(
                    new=latest_version,
                    current=APP_VERSION
                ),
                QMessageBox.Yes | QMessageBox.No
            )

            if reply != QMessageBox.Yes:
                return

            tmp_path = os.path.join(os.getcwd(), "update_tmp.exe")

            urllib.request.urlretrieve(download_url, tmp_path)

            updater_path = os.path.join(os.getcwd(), "updater.exe")

            subprocess.Popen([
                updater_path,
                sys.executable,
                tmp_path
            ])

            QApplication.quit()

        except Exception as e:
            # 更新失败时静默，不影响用户使用
            pass

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
            self, "选择文本文件", "", "Text Files (*.txt)"
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

        self.file_label.setText(
            self.tr("current_file").format(
                name=os.path.basename(path)
            )
        )
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
            self.show_topmost_message(
                self.tr("extract_complete_title"),
                 self.tr("extract_complete_msg")
            )

    def extract_copy_and_paste(self):
        self.extract_and_copy()

        QApplication.processEvents()
        time.sleep(0.05)

        keyboard.press_and_release("ctrl+v")

        if self.auto_send and not self._showing_finish_dialog:
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
            "设置快捷键",
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
        self.line_label.setText(
            self.tr("current_line").format(line=self.current_line)
        )

    def _save_progress(self):
        data = {
            "file_path": self.file_path,
            "current_line": self.current_line,
            "hotkey_copy": self.hotkey_copy,
            "auto_send": self.auto_send,
            "language": self.language
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
                self.language = data.get("language", "zh")  # ✅ 新增

    def show_topmost_message(self, title, message):
        self._showing_finish_dialog = True

        msg = QMessageBox(self)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setIcon(QMessageBox.Information)

        msg.setStandardButtons(QMessageBox.Ok)

        msg.setWindowFlags(
            Qt.Window |
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )

        # 当弹窗真正关闭后，解除锁
        def on_finished(_):
            self._showing_finish_dialog = False

        msg.finished.connect(on_finished)

        msg.show()
        msg.raise_()
        msg.activateWindow()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = TextExtractor()
    win.show()
    sys.exit(app.exec_())
