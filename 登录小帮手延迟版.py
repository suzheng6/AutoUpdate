import sys
import re
import time
import keyboard
import pyperclip
import pyautogui
import requests
import webbrowser
import os
import json
from datetime import datetime
from bs4 import BeautifulSoup
from PyQt5.QtWidgets import (
    QApplication, QWidget, QTextEdit, QLabel, QVBoxLayout,
    QPushButton, QHBoxLayout, QGroupBox, QFileDialog, QMessageBox, QCheckBox, QComboBox
)
from PyQt5.QtCore import Qt, QThread, QTimer
from PyQt5.QtGui import QFont, QColor, QPalette


# 多语言配置
class Translations:
    """多语言配置类"""
    ZH = "zh"
    EN = "en"

    STRINGS = {
        ZH: {
            # 窗口标题
            "window_title": "自动登录小助手 · Pro",

            # 统计
            "stats_title": "📊 登录统计",
            "total_accounts": "总账号数: {count}",
            "current_account": "当前账号: {count}",
            "success_count": "✓ 成功: {count}",
            "fail_count": "✗ 失败: {count}",

            # 输入区域
            "input_title": "📝 账号列表",
            "input_placeholder": "粘贴文本，每行格式：\n"
                                "+14582185432|https://xxx.xxx\n\n"
                                "快捷键：\n"
                                "F4 - 打开网址\n"
                                "F3 - 自动登录流程",

            # 状态
            "status_title": "⚡ 当前操作",
            "status_waiting": "等待操作...",

            # 按钮
            "btn_clear": "🗑️ 清空列表",
            "btn_retry": "🔄 重新登录失败账号",
            "btn_export": "📥 导出失败账号",

            # 复选框和标签
            "chk_input_plus_one": "输入+1",
            "lbl_start": "🚀 按F3开始登录",

            # 消息提示
            "msg_no_failed_accounts": "没有失败账号需要导出",
            "msg_export_success": "已将{count}个失败账号保存到 {file}",
            "msg_no_failed_retry": "没有失败账号需要重新登录",
            "msg_retry_loaded": "失败账号已加载到列表中，请按F3重新登录",
            "msg_url_extracted": "已打开网址：{url}",
            "msg_url_complete": "网址提取完毕",
            "msg_login_complete": "所有账号登录完成！",
            "msg_login_complete_with_fail": "登录完成！成功: {success}, 失败: {fail}",
            "msg_login_all_success": "登录完成！所有账号成功登录",

            # 登录流程
            "login_press_1": "[账号 {current}/{total}] 按键: 1",
            "login_press_enter": "[账号 {current}/{total}] 等待响应...",
            "login_skip_plus_one": "[账号 {current}/{total}] 跳过+1输入，直接提取手机号",
            "login_paste_phone": "[账号 {current}/{total}] 粘贴手机号: {phone}",
            "login_submit_phone": "[账号 {current}/{total}] 提交手机号，等待验证码界面...",
            "login_no_url": "[账号 {current}] ❌ 未提供URL",
            "login_error": "[账号 {current}] ❌ 登录异常：{error}",
            "login_extracting": "[账号 {current}/{total}] 正在提取验证码...",
            "login_paste_code": "[账号 {current}/{total}] 粘贴验证码: {code}",
            "login_submit_code": "[账号 {current}/{total}] 提交验证码，等待2fa密码...",
            "login_paste_2fa": "[账号 {current}/{total}] 粘贴2fa密码: {pass_2fa}",
            "login_success": "[账号 {current}] ✅ 登录成功！",
            "login_no_2fa": "[账号 {current}] ⚠️ 未找到2fa密码",
            "login_no_code": "[账号 {current}] ❌ 未能提取到验证码",
            "login_retry_hint": "💡 提示：按F3继续下一个账户登录",

            # 提取验证码
            "extract_retry": "未提取到验证码，2秒后重试... (第{attempt}次)",
            "extract_failed": "提取失败：{error}" + "2秒后重试",

            # 语言切换
            "language": "语言",
            "chinese": "中文",
            "english": "English",

            # 日志提示
            "log_location": "提示：所有错误信息会自动保存到：{file}",
        },
        EN: {
            # Window Title
            "window_title": "Auto Login Assistant · Pro",

            # Stats
            "stats_title": "📊 Login Statistics",
            "total_accounts": "Total: {count}",
            "current_account": "Current: {count}",
            "success_count": "✓ Success: {count}",
            "fail_count": "✗ Failed: {count}",

            # Input Area
            "input_title": "📝 Account List",
            "input_placeholder": "Paste text, one per line:\n"
                                "+14582185432|https://xxx.xxx\n\n"
                                "Hotkeys:\n"
                                "F4 - Open URL\n"
                                "F3 - Auto Login",

            # Status
            "status_title": "⚡ Current Operation",
            "status_waiting": "Waiting...",

            # Buttons
            "btn_clear": "🗑️ Clear List",
            "btn_retry": "🔄 Retry Failed Accounts",
            "btn_export": "📥 Export Failed",

            # Checkbox and Label
            "chk_input_plus_one": "Input +1",
            "lbl_start": "🚀 Press F3 to Start",

            # Messages
            "msg_no_failed_accounts": "No failed accounts to export",
            "msg_export_success": "Exported {count} failed accounts to {file}",
            "msg_no_failed_retry": "No failed accounts to retry",
            "msg_retry_loaded": "Failed accounts loaded, press F3 to retry",
            "msg_url_extracted": "Opened URL: {url}",
            "msg_url_complete": "URL extraction complete",
            "msg_login_complete": "All accounts login complete!",
            "msg_login_complete_with_fail": "Login complete! Success: {success}, Failed: {fail}",
            "msg_login_all_success": "Login complete! All accounts successful",
            "test_capture_failed": "❌ Screenshot capture failed",
            "test_not_captured": "❌ Please capture verification screen first",
            "test_check_failed": "Screenshot check failed",
            "test_checking": "Checking screenshot file...",
            "test_checking_file": "Trying to recognize screenshot on screen...",
            "test_checking_path": "Screenshot path: {path}",
            "test_checking_size": "File size: {size} bytes",
            "test_image_size": "Image size: {width} x {height}",
            "test_no_chinese": "❌ Chinese path detected, use English path",
            "test_res_small": "❌ Resolution too small: {w}x{h}",
            "test_res_large": "❌ Resolution too large: {w}x{h}",
            "test_res_ok": "✅ Resolution good: {w}x{h}",
            "test_res_info": "ℹ️ Resolution: {w}x{h} (recommended 800-1920 x 600-1080)",
            "test_success": "Screenshot Valid",
            "test_recognized": "✅ Screenshot recognized successfully!\n\n"
                               "File: {filename}\n"
                               "Location: {location}\n\n"
                               "🚀 Press F3 to start auto login!",
            "test_recognized_low_conf": "✅ Screenshot recognized! (low confidence)\n\n"
                                         "File: {filename}\n"
                                         "Location: {location}\n\n"
                                         "🚀 Press F3 to start auto login!",
            "test_failed": "Recognition Failed",
            "test_failed_msg": "❌ Could not find matching area on screen.\n\n"
                               "Possible reasons:\n"
                               "1. Screenshot doesn't match current screen\n"
                               "2. Screenshot contains dynamic content (e.g., time)\n"
                               "3. Verification screen not open or blocked\n\n"
                               "Recapture verification screen?",

            # Chinese Path Warning
            "warning_chinese_path": "⚠️ Chinese path detected: {path}",
            "warning_chinese_path_dir": "⚠️ Warning: Program folder contains Chinese characters",
            "status_error_log_saved": "Error log saved to: {file}",

            # Login Process
            "login_press_1": "[Account {current}/{total}] Press: 1",
            "login_press_enter": "[Account {current}/{total}] Waiting...",
            "login_skip_plus_one": "[Account {current}/{total}] Skip +1, extract phone",
            "login_paste_phone": "[Account {current}/{total}] Paste phone: {phone}",
            "login_submit_phone": "[Account {current}/{total}] Submit phone, waiting...",
            "login_no_url": "[Account {current}] ❌ No URL provided",
            "login_error": "[Account {current}] ❌ Login error: {error}",
            "login_extracting": "[Account {current}/{total}] Extracting code...",
            "login_paste_code": "[Account {current}/{total}] Paste code: {code}",
            "login_submit_code": "[Account {current}/{total}] Submit code, waiting...",
            "login_paste_2fa": "[Account {current}/{total}] Paste 2FA: {pass_2fa}",
            "login_success": "[Account {current}] ✅ Login successful!",
            "login_no_2fa": "[Account {current}] ⚠️ No 2FA found",
            "login_no_code": "[Account {current}] ❌ Could not extract code",
            "login_retry_hint": "💡 Hint: Press F3 to continue with next account",

            # Extract Code
            "extract_retry": "No code extracted, retrying in 2s... (attempt {attempt})",
            "extract_failed": "Extraction failed: {error}" + "2s later retry",

            # Language Switch
            "language": "Language",
            "chinese": "中文",
            "english": "English",

            # Log
            "log_location": "Hint: All errors will be saved to: {file}",
        }
    }


class HotkeyListener(QThread):
    def __init__(self, extract_url, extract_number):
        super().__init__()
        self.extract_url = extract_url
        self.extract_number = extract_number
        self._running = True

    def run(self):
        """使用全局热键监听F3和F4"""
        try:
            # 使用全局热键，这样可以优先响应
            keyboard.add_hotkey('f3', self.extract_number, suppress=True)
            keyboard.add_hotkey('f4', self.extract_url, suppress=True)
            print("[热键] F3和F4快捷键已注册（全局优先）")
        except Exception as e:
            print(f"[错误] 注册热键失败: {e}")
            # 如果suppress不支持，回退到普通模式
            try:
                keyboard.add_hotkey('f3', self.extract_number)
                keyboard.add_hotkey('f4', self.extract_url)
                print("[热键] F3和F4快捷键已注册（普通模式）")
            except Exception as e2:
                print(f"[错误] 注册热键失败（回退）: {e2}")

        # 保持线程运行
        while self._running:
            try:
                keyboard.wait(0.1)  # 等待0.1秒，这样可以定期检查_running标志
            except:
                break

    def stop(self):
        """停止监听"""
        self._running = False
        try:
            keyboard.unhook_all_hotkeys()
        except:
            pass


class ExtractorApp(QWidget):
    def __init__(self):
        super().__init__()
        self.current_language = Translations.ZH  # 默认语言：中文

        # 获取程序所在目录（支持Python脚本和打包后的EXE）
        if getattr(sys, 'frozen', False):
            # 如果是打包后的EXE
            self.script_dir = os.path.dirname(sys.executable)
            print(f"[启动] 运行模式: 打包的EXE")
            print(f"[启动] EXE路径: {sys.executable}")
        else:
            # 如果是Python脚本
            self.script_dir = os.path.dirname(os.path.abspath(__file__))
            print(f"[启动] 运行模式: Python脚本")
            print(f"[启动] 脚本路径: {__file__}")

        print(f"[启动] 程序目录: {self.script_dir}")

        # 设置窗口标题
        self.setWindowTitle(self.get_text("window_title"))
        self.setFixedSize(700, 600)  # 增加高度以确保所有元素可见
        self.setWindowFlags(Qt.WindowStaysOnTopHint)  # 窗口保持在最上层

        # 配置文件路径
        self.config_file = os.path.join(self.script_dir, "config.json")

        # 错误日志文件路径
        self.error_log_file = os.path.join(self.script_dir, "error_log.txt")

        # 失败账号导出文件路径
        self.failed_file = os.path.join(self.script_dir, "failed_accounts.txt")

        # 状态统计变量
        self.total_accounts = 0
        self.success_count = 0
        self.fail_count = 0
        self.current_index = 0
        self.failed_accounts = []

        # 设置UI样式
        self.setup_ui()
        self.setup_styles()

        # 数据
        self.lines = []
        self.url_index = 0
        self.num_index = 0

        # 清空错误日志（仅保留最后100行，避免文件过大）
        try:
            if os.path.exists(self.error_log_file):
                with open(self.error_log_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                if len(lines) > 100:
                    with open(self.error_log_file, 'w', encoding='utf-8') as f:
                        f.writelines(lines[-100:])
        except:
            pass

        # 加载上次保存的配置
        self.load_config()

        # 显示错误日志位置提示
        self.update_status(self.get_text("log_location", file=os.path.basename(self.error_log_file)))

        # 启动热键监听
        self.listener = HotkeyListener(
            self.extract_next_url,
            self.extract_next_number
        )
        self.listener.start()

    def get_program_directory(self):
        """
        获取程序所在目录（支持Python脚本和打包后的EXE）

        Returns:
            str: 程序所在目录的绝对路径
        """
        if getattr(sys, 'frozen', False):
            # 如果是打包后的EXE
            return os.path.dirname(sys.executable)
        else:
            # 如果是Python脚本
            return os.path.dirname(os.path.abspath(__file__))

    def get_text(self, key, **kwargs):
        """
        获取当前语言的文本

        Args:
            key: 文本键名
            **kwargs: 用于格式化字符串的参数

        Returns:
            str: 格式化后的文本
        """
        text = Translations.STRINGS[self.current_language].get(key, key)
        if kwargs:
            return text.format(**kwargs)
        return text

    def switch_language(self, index):
        """
        切换语言

        Args:
            index: 语言选择框的索引（0=中文，1=英文）
        """
        new_lang = Translations.ZH if index == 0 else Translations.EN
        if new_lang != self.current_language:
            self.current_language = new_lang
            self.update_ui_language()
            self.save_config()

    def update_ui_language(self):
        """更新所有UI元素的语言"""
        # 更新窗口标题
        self.setWindowTitle(self.get_text("window_title"))

        # 更新标题标签
        self.title_label.setText("🚀 " + self.get_text("window_title"))

        # 更新统计面板
        self.stats_group.setTitle(self.get_text("stats_title"))
        self.update_stats()

        # 更新输入区域
        self.input_group.setTitle(self.get_text("input_title"))
        self.text_edit.setPlaceholderText(self.get_text("input_placeholder"))

        # 更新状态区域
        self.status_group.setTitle(self.get_text("status_title"))
        if self.status_label.text() == "等待操作...":
            self.status_label.setText(self.get_text("status_waiting"))

        # 更新按钮和复选框
        self.start_label.setText(self.get_text("lbl_start"))
        self.input_plus_one.setText(self.get_text("chk_input_plus_one"))
        self.clear_btn.setText(self.get_text("btn_clear"))
        self.retry_btn.setText(self.get_text("btn_retry"))
        self.export_btn.setText(self.get_text("btn_export"))

        # 更新语言选择器文本
        self.language_label.setText(self.get_text("language") + ":")
        self.language_combo.setItemText(0, self.get_text("chinese"))
        self.language_combo.setItemText(1, self.get_text("english"))

    def setup_ui(self):
        """设置UI布局"""
        # 主布局
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(25, 25, 25, 25)

        # 标题和语言选择行
        title_row = QHBoxLayout()

        self.title_label = QLabel("🚀 " + self.get_text("window_title"))
        self.title_label.setAlignment(Qt.AlignLeft)
        self.title_label.setFont(QFont("Microsoft YaHei", 18, QFont.Bold))
        self.title_label.setStyleSheet("color: #2E7D32;")

        # 语言选择器
        self.language_label = QLabel(self.get_text("language") + ":")
        self.language_label.setFont(QFont("Microsoft YaHei", 10))

        self.language_combo = QComboBox()
        self.language_combo.addItems([self.get_text("chinese"), self.get_text("english")])
        self.language_combo.setCurrentIndex(0 if self.current_language == Translations.ZH else 1)
        self.language_combo.currentIndexChanged.connect(self.switch_language)
        self.language_combo.setStyleSheet("""
            QComboBox {
                padding: 6px 12px;
                border: 2px solid #4CAF50;
                border-radius: 5px;
                background-color: white;
                font-size: 11px;
                min-width: 80px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                border: 2px solid #4CAF50;
                selection-background-color: #E8F5E9;
            }
        """)

        title_row.addWidget(self.title_label, 1)
        title_row.addStretch()
        title_row.addWidget(self.language_label)
        title_row.addWidget(self.language_combo)

        main_layout.addLayout(title_row)

        # 状态统计面板
        self.stats_group = QGroupBox(self.get_text("stats_title"))
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(15)

        self.total_label = self.create_stat_label(self.get_text("total_accounts", count=0), "#4CAF50")
        self.current_label = self.create_stat_label(self.get_text("current_account", count=0), "#2196F3")
        self.success_label = self.create_stat_label(self.get_text("success_count", count=0), "#4CAF50")
        self.fail_label = self.create_stat_label(self.get_text("fail_count", count=0), "#F44336")

        stats_layout.addWidget(self.total_label)
        stats_layout.addWidget(self.current_label)
        stats_layout.addWidget(self.success_label)
        stats_layout.addWidget(self.fail_label)
        self.stats_group.setLayout(stats_layout)
        main_layout.addWidget(self.stats_group)

        # 输入区域
        self.input_group = QGroupBox(self.get_text("input_title"))
        input_layout = QVBoxLayout()

        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText(self.get_text("input_placeholder"))
        self.text_edit.setMinimumHeight(120)
        self.text_edit.setMaximumHeight(180)
        self.text_edit.setStyleSheet("""
            QTextEdit {
                border: 2px solid #BDBDBD;
                border-radius: 5px;
                padding: 10px;
                font-size: 12px;
                background-color: #FAFAFA;
            }
            QTextEdit:focus {
                border: 2px solid #4CAF50;
            }
        """)
        input_layout.addWidget(self.text_edit)

        self.input_group.setLayout(input_layout)
        main_layout.addWidget(self.input_group, 2)

        # 当前操作状态
        self.status_group = QGroupBox(self.get_text("status_title"))
        status_layout = QVBoxLayout()
        self.status_label = QLabel(self.get_text("status_waiting"))
        self.status_label.setAlignment(Qt.AlignLeft)
        self.status_label.setWordWrap(True)
        self.status_label.setFont(QFont("Microsoft YaHei", 11))
        self.status_label.setStyleSheet("""
            QLabel {
                color: #333;
                padding: 8px;
                background-color: #F5F5F5;
                border-radius: 3px;
            }
        """)
        status_layout.addWidget(self.status_label)
        self.status_group.setLayout(status_layout)
        main_layout.addWidget(self.status_group, 1)

        # 按钮和选项区域
        control_layout = QVBoxLayout()
        control_layout.setSpacing(12)

        # 第一行：提示和复选框
        control_row1 = QHBoxLayout()
        control_row1.setSpacing(15)

        # F3快捷键提示标签 - 使用更醒目的样式
        self.start_label = QLabel(self.get_text("lbl_start"))
        self.start_label.setAlignment(Qt.AlignCenter)
        self.start_label.setMinimumHeight(45)
        self.start_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #FFFFFF;
                padding: 15px 25px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #4CAF50, stop:1 #2E7D32);
                border: 2px solid #1B5E20;
                border-radius: 8px;
            }
        """)

        self.input_plus_one = QCheckBox(self.get_text("chk_input_plus_one"))
        self.input_plus_one.setChecked(False)
        self.input_plus_one.setFont(QFont("Microsoft YaHei", 12, QFont.Bold))
        self.input_plus_one.setStyleSheet("""
            QCheckBox {
                color: #333;
                padding: 12px 18px;
            }
            QCheckBox::indicator {
                width: 22px;
                height: 22px;
                border: 2px solid #4CAF50;
                border-radius: 4px;
                background-color: white;
            }
            QCheckBox::indicator:checked {
                background-color: #4CAF50;
                border: 2px solid #4CAF50;
            }
            QCheckBox::indicator:hover {
                border: 2px solid #66BB6A;
            }
        """)

        control_row1.addWidget(self.start_label, 2)  # 给F3标签更多空间
        control_row1.addWidget(self.input_plus_one, 1)
        control_row1.addStretch(1)

        # 第二行：操作按钮
        control_row2 = QHBoxLayout()
        control_row2.setSpacing(15)

        self.clear_btn = QPushButton(self.get_text("btn_clear"))
        self.clear_btn.clicked.connect(self.clear_text)
        self.clear_btn.setMinimumWidth(140)
        self.clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF5722;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 12px 18px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #F44336;
            }
            QPushButton:pressed {
                background-color: #E64A19;
            }
            QPushButton:disabled {
                background-color: #BDBDBD;
            }
        """)

        self.retry_btn = QPushButton(self.get_text("btn_retry"))
        self.retry_btn.clicked.connect(self.retry_failed_accounts)
        self.retry_btn.setEnabled(False)
        self.retry_btn.setMinimumWidth(160)
        self.retry_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 12px 18px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #FB8C00;
            }
            QPushButton:pressed {
                background-color: #EF6C00;
            }
            QPushButton:disabled {
                background-color: #BDBDBD;
            }
        """)

        self.export_btn = QPushButton(self.get_text("btn_export"))
        self.export_btn.clicked.connect(self.export_failed_accounts)
        self.export_btn.setEnabled(False)
        self.export_btn.setMinimumWidth(140)
        self.export_btn.setStyleSheet("""
            QPushButton {
                background-color: #9C27B0;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 12px 18px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #AB47BC;
            }
            QPushButton:pressed {
                background-color: #8E24AA;
            }
            QPushButton:disabled {
                background-color: #BDBDBD;
            }
        """)

        control_row2.addWidget(self.clear_btn)
        control_row2.addWidget(self.retry_btn)
        control_row2.addWidget(self.export_btn)
        control_row2.addStretch()

        control_layout.addLayout(control_row1)
        control_layout.addLayout(control_row2)

        main_layout.addLayout(control_layout)

        self.setLayout(main_layout)

    def create_stat_label(self, text, color):
        """创建统计标签"""
        label = QLabel(text)
        label.setFont(QFont("Microsoft YaHei", 10, QFont.Bold))
        label.setStyleSheet(f"color: {color}; padding: 5px; border: 1px solid {color}; border-radius: 5px;")
        label.setAlignment(Qt.AlignCenter)
        return label

    def setup_styles(self):
        """设置样式"""
        self.setStyleSheet("""
            QWidget {
                background-color: #f5f5f5;
                font-family: "Microsoft YaHei";
            }
            QGroupBox {
                font-weight: bold;
                font-size: 12px;
                border: 2px solid #ddd;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QTextEdit {
                border: 2px solid #ddd;
                border-radius: 8px;
                padding: 8px;
                font-family: "Consolas", 10px;
                background-color: #fafafa;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 15px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)

    def update_stats(self):
        """更新统计信息"""
        self.total_label.setText(self.get_text("total_accounts", count=self.total_accounts))
        self.current_label.setText(self.get_text("current_account", count=self.current_index + 1))
        self.success_label.setText(self.get_text("success_count", count=self.success_count))
        self.fail_label.setText(self.get_text("fail_count", count=self.fail_count))

    def update_status(self, message, **kwargs):
        """
        更新状态显示

        Args:
            message: 消息内容（可以是文本键或直接文本）
            **kwargs: 用于格式化的参数
        """
        # 检查是否是文本键
        if message in Translations.STRINGS[self.current_language]:
            display_message = self.get_text(message, **kwargs)
        else:
            # 直接使用传入的文本
            if kwargs:
                display_message = message.format(**kwargs)
            else:
                display_message = message

        self.status_label.setText(f"📌 {display_message}")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #1976D2;
                font-weight: bold;
                padding: 10px;
                background-color: #E3F2FD;
                border-radius: 5px;
            }
        """)

    def save_error_log(self, title, error_message):
        """保存错误日志到文件"""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_content = f"""
{'='*60}
时间: {timestamp}
标题: {title}
{'='*60}
{error_message}
{'='*60}

"""
            with open(self.error_log_file, 'a', encoding='utf-8') as f:
                f.write(log_content)

            self.update_status(f"❌ 错误信息已保存到：{self.error_log_file}")
            return True
        except Exception as e:
            self.update_status(f"保存错误日志失败: {str(e)}")
            return False

    def save_config(self):
        """保存当前状态到配置文件"""
        try:
            config = {
                "lines": self.lines,
                "url_index": self.url_index,
                "num_index": self.num_index,
                "current_index": self.current_index,
                "total_accounts": self.total_accounts,
                "success_count": self.success_count,
                "fail_count": self.fail_count,
                "failed_accounts": self.failed_accounts,
                "text_content": self.text_edit.toPlainText(),
                "language": self.current_language
            }

            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)

            # print("配置已保存")  # 调试用
        except Exception as e:
            print(f"保存配置失败: {e}")

    def load_config(self):
        """从配置文件加载上次的状态"""
        try:
            if not os.path.exists(self.config_file):
                return False

            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)

            # 恢复状态
            self.lines = config.get("lines", [])
            self.url_index = config.get("url_index", 0)
            self.num_index = config.get("num_index", 0)
            self.current_index = config.get("current_index", 0)
            self.total_accounts = config.get("total_accounts", 0)
            self.success_count = config.get("success_count", 0)
            self.fail_count = config.get("fail_count", 0)
            self.failed_accounts = config.get("failed_accounts", [])
            text_content = config.get("text_content", "")

            # 恢复语言设置
            saved_language = config.get("language", Translations.ZH)
            if saved_language in [Translations.ZH, Translations.EN]:
                self.current_language = saved_language
                # 更新语言选择器的选中项
                self.language_combo.blockSignals(True)
                self.language_combo.setCurrentIndex(0 if self.current_language == Translations.ZH else 1)
                self.language_combo.blockSignals(False)
                # 更新UI语言
                self.update_ui_language()

            # 恢复文本框内容
            self.text_edit.setText(text_content)

            # 更新统计信息
            self.update_stats()

            # 更新按钮状态
            if self.failed_accounts:
                self.retry_btn.setEnabled(True)
                self.export_btn.setEnabled(True)

            return True

        except Exception as e:
            print(f"加载配置失败: {e}")
            return False

    def clear_text(self):
        """清空文本"""
        self.text_edit.clear()
        self.lines = []
        self.url_index = 0
        self.num_index = 0
        self.total_accounts = 0
        self.current_index = 0
        self.success_count = 0
        self.fail_count = 0
        self.failed_accounts = []
        self.update_stats()
        self.status_label.setText("等待操作...")
        self.status_label.setStyleSheet("")
        self.retry_btn.setEnabled(False)
        self.export_btn.setEnabled(False)
        self.save_config()  # 自动保存配置

    def load_lines(self):
        """加载账号列表"""
        text = self.text_edit.toPlainText().strip()
        self.lines = [line for line in text.splitlines() if "|" in line]
        self.total_accounts = len(self.lines)
        self.update_stats()
        self.save_config()  # 自动保存配置

    def record_failed_account(self, line):
        """记录失败账号"""
        self.failed_accounts.append(line)
        self.fail_count += 1
        self.update_stats()
        self.retry_btn.setEnabled(True)
        self.export_btn.setEnabled(True)
        self.save_config()  # 自动保存配置

    def export_failed_accounts(self):
        """导出失败账号"""
        if not self.failed_accounts:
            QMessageBox.information(self, self.get_text("msg_no_failed_accounts"), "")
            return

        # 保存到文件
        with open(self.failed_file, 'w', encoding='utf-8') as f:
            for account in self.failed_accounts:
                f.write(account + '\n')

        QMessageBox.information(self, "成功", self.get_text("msg_export_success",
                                                             count=len(self.failed_accounts),
                                                             file=os.path.basename(self.failed_file)))

    def retry_failed_accounts(self):
        """重新登录失败账号"""
        if not self.failed_accounts:
            QMessageBox.information(self, "提示", "没有失败账号需要重新登录")
            return

        # 将失败账号放回文本框
        self.text_edit.setText('\n'.join(self.failed_accounts))

        # 重置索引和统计
        self.failed_accounts = []
        self.fail_count = 0
        self.url_index = 0
        self.num_index = 0
        self.current_index = 0

        self.update_stats()
        self.retry_btn.setEnabled(False)
        self.export_btn.setEnabled(False)
        self.save_config()  # 自动保存配置

        QMessageBox.information(self, "提示", "失败账号已加载到列表中，请按F3重新登录")

    def extract_next_url(self):
        """提取并打开URL"""
        self.load_lines()
        if self.url_index >= len(self.lines):
            self.update_status("网址提取完毕")
            return

        line = self.lines[self.url_index]
        self.url_index += 1

        match = re.search(r"https?://\S+", line)
        if match:
            url = match.group()
            webbrowser.open(url)
            self.update_status(f"已打开网址：{url}")

        self.save_config()  # 自动保存配置

    def extract_code_from_html(self, url, max_retries=4):
        """从URL提取设备验证码和2fa密码，支持自动重试"""
        for attempt in range(max_retries):
            try:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                response = requests.get(url, headers=headers, timeout=10)
                response.raise_for_status()

                soup = BeautifulSoup(response.text, 'html.parser')

                # 提取设备验证码 (id="code")
                code_input = soup.find('input', {'id': 'code'})
                device_code = code_input.get('value', '').strip() if code_input else ''

                # 提取2fa/密码 (id="pass2fa")
                pass_input = soup.find('input', {'id': 'pass2fa'})
                pass_2fa = pass_input.get('value', '').strip() if pass_input else ''

                if device_code:  # 如果成功提取到验证码，立即返回
                    return device_code, pass_2fa

                # 如果没有提取到验证码，等待2秒后重试
                if attempt < max_retries - 1:
                    self.update_status("extract_retry", attempt=attempt + 1)
                    time.sleep(2)

            except Exception as e:
                self.update_status("extract_failed", error=str(e))
                if attempt < max_retries - 1:
                    time.sleep(2)

        return '', ''  # 所有尝试都失败

    def extract_next_number(self):
        """完整的自动登录流程"""
        self.load_lines()
        if self.num_index >= len(self.lines):
            self.update_status("msg_login_complete")
            if self.failed_accounts:
                self.update_status("msg_login_complete_with_fail",
                                 success=self.success_count,
                                 fail=self.fail_count)
            else:
                self.update_status("msg_login_all_success")
            return

        line = self.lines[self.num_index]
        self.num_index += 1
        self.current_index = self.num_index - 1
        self.update_stats()

        # 提取URL和手机号
        parts = line.split("|")
        phone = parts[0]
        url = parts[1] if len(parts) > 1 else ''

        # 开始登录流程
        try:
            # 检查是否需要输入+1
            if self.input_plus_one.isChecked():
                # 1. 先按1
                self.update_status("login_press_1",
                                 current=self.current_index + 1,
                                 total=self.total_accounts)
                pyautogui.press("1")

                # 2. 按回车
                time.sleep(0.2)  # 优化：减少延迟
                pyautogui.press("enter")
                self.update_status("login_press_enter",
                                 current=self.current_index + 1,
                                 total=self.total_accounts)

                # 按完回车后延迟
                time.sleep(0.8)  # 优化：减少延迟
            else:
                self.update_status("login_skip_plus_one",
                                 current=self.current_index + 1,
                                 total=self.total_accounts)

            # 3. 提取手机号（去掉+1或+91）
            digits = re.sub(r"\D", "", phone)
            phone_10_digits = digits[1:] if len(digits) > 1 else digits

            if len(phone_10_digits) < 10:
                self.update_status(f"[账号 {self.current_index + 1}] ❌ 手机号格式错误：{phone_10_digits}")
                self.record_failed_account(line)
                return

            # 4. 粘贴手机号
            pyperclip.copy(phone_10_digits)
            pyautogui.hotkey("ctrl", "v")
            self.update_status("login_paste_phone",
                             current=self.current_index + 1,
                             total=self.total_accounts,
                             phone=phone_10_digits)

            # 5. 直接按回车（不延迟）
            pyautogui.press("enter")
            self.update_status("login_submit_phone",
                             current=self.current_index + 1,
                             total=self.total_accounts)

            # 6. 延迟5秒等待验证码界面出现
            time.sleep(5)

            # 7. 后台提取验证码和密码
            if url:
                self._process_verification_code(url, line)
            else:
                self.update_status("login_no_url",
                                 current=self.current_index + 1)
                self.record_failed_account(line)

        except Exception as e:
            self.update_status("login_error",
                             current=self.current_index + 1,
                             error=str(e))
            self.record_failed_account(line)

    def _process_verification_code(self, url=None, line=None):
        """处理验证码提取和粘贴的通用方法"""
        self.update_status("login_extracting",
                         current=self.current_index + 1,
                         total=self.total_accounts)

        device_code, pass_2fa = self.extract_code_from_html(url)

        if device_code:
            # 1. 粘贴设备验证码
            pyperclip.copy(device_code)
            pyautogui.hotkey("ctrl", "v")
            self.update_status("login_paste_code",
                             current=self.current_index + 1,
                             total=self.total_accounts,
                             code=device_code)

            # 2. 延迟1秒
            time.sleep(1)

            # 3. 按回车
            pyautogui.press("enter")
            self.update_status("login_submit_code",
                             current=self.current_index + 1,
                             total=self.total_accounts)

            # 4. 粘贴2fa密码
            if pass_2fa:
                time.sleep(0.3)
                pyperclip.copy(pass_2fa)
                pyautogui.hotkey("ctrl", "v")
                self.update_status("login_paste_2fa",
                                 current=self.current_index + 1,
                                 total=self.total_accounts,
                                 pass_2fa=pass_2fa)

                # 延迟0.3秒后按回车
                time.sleep(0.3)
                pyautogui.press("enter")

                # 登录成功
                self.success_count += 1
                self.update_stats()
                self.update_status("login_success", current=self.current_index + 1)
                self.save_config()  # 保存配置
            else:
                self.update_status("login_no_2fa", current=self.current_index + 1)
                self.record_failed_account(line)
        else:
            self.update_status("login_no_code", current=self.current_index + 1)
            self.update_status("login_retry_hint")
            if line:
                self.record_failed_account(line)

    def closeEvent(self, event):
        """
        程序关闭时的清理工作
        """
        # 停止快捷键监听线程
        if hasattr(self, 'listener'):
            self.listener.stop()
            self.listener.quit()
            self.listener.wait()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = ExtractorApp()
    # 确保窗口显示在最上层
    win.show()
    win.activateWindow()
    win.raise_()
    sys.exit(app.exec_())
