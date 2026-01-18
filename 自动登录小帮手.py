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
            "btn_capture": "📸 截取验证码界面",
            "btn_test": "🔍 测试截图",

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

            # 截图相关
            "screenshot_title": "自动截取验证码界面",
            "screenshot_prepare": "📍 准备验证码界面\n\n"
                                  "请先打开登录界面，确保验证码输入框可见。\n\n"
                                  "点击确定后，将自动打开截图工具。\n\n"
                                  "请用鼠标框选验证码界面区域，\n"
                                  "截图完成后，点击下方\"已完成截图\"按钮。",
            "screenshot_waiting": "📍 正在等待截图...\n\n"
                                  "程序已自动调用截图工具（Windows+Shift+S）。\n\n"
                                  "请用鼠标框选验证码界面区域。\n\n"
                                  "截图完成后，点击下方\"✅ 已完成截图\"按钮",
            "screenshot_cancel": "取消",
            "screenshot_done": "✅ 已完成截图",

            # 截图错误提示
            "error_no_clipboard": "未能从剪贴板获取到截图！\n\n"
                                  "请确保：\n"
                                  "1. 您已经使用截图工具截图\n"
                                  "2. 截图成功保存到剪贴板\n"
                                  "3. 没有复制其他内容到剪贴板",
            "error_capture_failed": "截图获取失败",
            "error_verify_failed": "截图验证失败，请检查截图内容。\n\n"
                                   "建议：\n"
                                   "1. 确保截图包含完整的验证码界面\n"
                                   "2. 截图宽度建议在 800-1920 像素之间\n"
                                   "3. 重新截图，框选更大的区域",
            "error_screenshot_saved": "截图已保存：{filename}",
            "error_screenshot_loaded": "✅ 验证码界面截图已加载：{filename}",

            # 成功提示
            "success_captured": "验证码界面截图已成功截取并加载！\n\n"
                                "文件：{filename}\n"
                                "保存位置：{path}\n\n"
                                "现在可以按F3开始自动登录了。",

            # 测试截图
            "test_no_screenshot": "❌ 当前目录下没有找到验证码界面截图。\n\n"
                                  "是否现在截取验证码界面？\n\n"
                                  "截取后程序会自动识别是否可用。",
            "test_no_screenshot_title": "未检测到截图",
            "test_capture_cancel": "截图已取消",
            "test_capture_failed": "❌ 未成功截取截图",
            "test_not_captured": "❌ 请先截取验证码界面",
            "test_check_failed": "截图检查失败",
            "test_checking": "正在检查截图文件...",
            "test_checking_file": "正在尝试在屏幕上识别截图...",
            "test_checking_path": "使用的截图路径：{path}",
            "test_checking_size": "文件大小：{size} 字节",
            "test_image_size": "图片尺寸：{width} x {height}",
            "test_no_chinese": "❌ 检测到中文路径，建议将截图文件放在程序目录下",
            "test_res_small": "❌ 截图分辨率过小：{w}x{h}",
            "test_res_large": "❌ 截图分辨率过大：{w}x{h}",
            "test_res_ok": "✅ 截图分辨率合适：{w}x{h}",
            "test_res_info": "ℹ️ 截图分辨率：{w}x{h}（建议 800-1920 x 600-1080）",
            "test_success": "截图可用",
            "test_recognized": "✅ 截图识别成功！\n\n"
                               "截图文件：{filename}\n"
                               "匹配位置：{location}\n\n"
                               "🚀 现在可以按 F3 开始自动登录了！",
            "test_recognized_low_conf": "✅ 截图识别成功！（较低置信度）\n\n"
                                         "截图文件：{filename}\n"
                                         "匹配位置：{location}\n\n"
                                         "🚀 现在可以按 F3 开始自动登录了！",
            "test_failed": "截图识别失败",
            "test_failed_msg": "❌ 在屏幕上未找到与截图匹配的区域。\n\n"
                               "可能原因：\n"
                               "1. 截图与当前屏幕界面不一致\n"
                               "2. 截图包含动态内容（如时间）\n"
                               "3. 验证码界面未打开或被遮挡\n\n"
                               "是否重新截取验证码界面？",

            # 中文路径警告
            "warning_chinese_path": "⚠️ 检测到中文路径：{path}",
            "warning_chinese_path_dir": "⚠️ 警告：程序所在文件夹路径包含中文字符",
            "warning_chinese_path_current": "当前路径：{path}",
            "warning_chinese_path_advice": "建议：将程序文件夹放在不含中文的路径下",
            "warning_chinese_path_result": "这可能导致 OpenCV 无法读取截图文件",
            "warning_chinese_path_screenshot": "建议：将截图文件放在程序目录下",

            # 状态消息
            "status_trigger_screenshot": "已打开截图工具，请框选验证码界面",
            "status_screenshot_cancelled": "截图已取消",
            "status_getting_screenshot": "正在从剪贴板获取截图...",
            "status_screenshot_saved": "截图已保存：{filename}",
            "status_screenshot_verify_failed": "截图验证失败",
            "status_error_log_saved": "错误信息已保存到：{file}",

            # 错误处理
            "error_loading_screenshot": "无法加载截图文件：{error}",
            "error_screenshot_advice": "建议：使用 Windows 自带的画图工具重新保存截图为 PNG 格式",
            "error_screen_timeout": "❌ 超时：未检测到界面 {filename}",
            "error_screen_attempts": "检测次数：{count}次，用时：{timeout}秒",
            "error_screen_advice": "建议：点击\"测试截图\"按钮检查截图是否正确",
            "error_opencv": "❌ 截图识别失败\n\n"
                            "可能原因：\n"
                            "1. Telegram 窗口太小\n"
                            "2. 截图分辨率过低或格式不正确\n"
                            "3. 文件路径包含中文字符\n\n"
                            "解决方法：\n"
                            "1. 将 Telegram 窗口拉大，确保窗口尺寸足够\n"
                            "2. 重新截图，框选更大的区域\n"
                            "3. 将程序文件夹和截图文件放在不含中文的路径下\n"
                            "4. 确保截图文件为 PNG 格式\n\n"
                            "详细错误信息已保存到：\n{file}",

            # 登录流程
            "login_press_1": "[账号 {current}/{total}] 按键: 1",
            "login_press_enter": "[账号 {current}/{total}] 等待响应...",
            "login_skip_plus_one": "[账号 {current}/{total}] 跳过+1输入，直接提取手机号",
            "login_paste_phone": "[账号 {current}/{total}] 粘贴手机号: {phone}",
            "login_submit_phone": "[账号 {current}/{total}] 提交手机号，等待验证码界面...",
            "login_no_screenshot": "[账号 {current}] ❌ 未截取验证码界面",
            "login_capture_hint": "请点击\"截取验证码界面\"按钮先截取验证码界面",
            "login_timeout": "[账号 {current}] ❌ 等待验证码界面超时",
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
            "extract_failed": "提取失败：{error}",

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
            "btn_capture": "📸 Capture Screen",
            "btn_test": "🔍 Test Screenshot",

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

            # Screenshot
            "screenshot_title": "Capture Verification Screen",
            "screenshot_prepare": "📍 Prepare Verification Screen\n\n"
                                  "Please open the login interface first.\n\n"
                                  "Click OK to start screenshot tool.\n\n"
                                  "Select the verification screen area.\n"
                                  "After capturing, click \"Done\" button.",
            "screenshot_waiting": "📍 Waiting for screenshot...\n\n"
                                  "Screenshot tool activated (Windows+Shift+S).\n\n"
                                  "Please select the verification screen area.\n\n"
                                  "After capturing, click \"✅ Done\" button",
            "screenshot_cancel": "Cancel",
            "screenshot_done": "✅ Done",

            # Screenshot Errors
            "error_no_clipboard": "Could not get screenshot from clipboard!\n\n"
                                  "Please ensure:\n"
                                  "1. You have captured the screen\n"
                                  "2. Screenshot saved to clipboard\n"
                                  "3. No other content copied to clipboard",
            "error_capture_failed": "Screenshot capture failed",
            "error_verify_failed": "Screenshot verification failed.\n\n"
                                   "Suggestions:\n"
                                   "1. Ensure screenshot includes complete verification screen\n"
                                   "2. Recommended width: 800-1920 pixels\n"
                                   "3. Recapture, select larger area",
            "error_screenshot_saved": "Screenshot saved: {filename}",
            "error_screenshot_loaded": "✅ Screenshot loaded: {filename}",

            # Success
            "success_captured": "Screenshot captured and loaded successfully!\n\n"
                                "File: {filename}\n"
                                "Location: {path}\n\n"
                                "Press F3 to start auto login.",

            # Test Screenshot
            "test_no_screenshot": "❌ Screenshot file not found.\n\n"
                                  "Capture verification screen now?\n\n"
                                  "Program will verify after capture.",
            "test_no_screenshot_title": "No Screenshot Found",
            "test_capture_cancel": "Screenshot cancelled",
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
            "warning_chinese_path_current": "Current path: {path}",
            "warning_chinese_path_advice": "Suggestion: Place program in English path",
            "warning_chinese_path_result": "May cause OpenCV reading errors",
            "warning_chinese_path_screenshot": "Suggestion: Place screenshot in program directory",

            # Status Messages
            "status_trigger_screenshot": "Screenshot tool opened, select verification screen",
            "status_screenshot_cancelled": "Screenshot cancelled",
            "status_getting_screenshot": "Getting screenshot from clipboard...",
            "status_screenshot_saved": "Screenshot saved: {filename}",
            "status_screenshot_verify_failed": "Screenshot verification failed",
            "status_error_log_saved": "Error log saved to: {file}",

            # Error Handling
            "error_loading_screenshot": "Cannot load screenshot: {error}",
            "error_screenshot_advice": "Suggestion: Use Paint to save as PNG format",
            "error_screen_timeout": "❌ Timeout: Screen {filename} not detected",
            "error_screen_attempts": "Attempts: {count}, Time: {timeout}s",
            "error_screen_advice": "Suggestion: Click \"Test Screenshot\" to verify",
            "error_opencv": "❌ Screenshot recognition failed\n\n"
                            "Possible causes:\n"
                            "1. Telegram window too small\n"
                            "2. Screenshot resolution too low or format incorrect\n"
                            "3. File path contains Chinese characters\n\n"
                            "Solutions:\n"
                            "1. Maximize Telegram window\n"
                            "2. Recapture, select larger area\n"
                            "3. Place program and screenshots in English path\n"
                            "4. Ensure screenshot is PNG format\n\n"
                            "Detailed error saved to:\n{file}",

            # Login Process
            "login_press_1": "[Account {current}/{total}] Press: 1",
            "login_press_enter": "[Account {current}/{total}] Waiting...",
            "login_skip_plus_one": "[Account {current}/{total}] Skip +1, extract phone",
            "login_paste_phone": "[Account {current}/{total}] Paste phone: {phone}",
            "login_submit_phone": "[Account {current}/{total}] Submit phone, waiting...",
            "login_no_screenshot": "[Account {current}] ❌ No screenshot",
            "login_capture_hint": "Please click \"Capture Screen\" first",
            "login_timeout": "[Account {current}] ❌ Timeout waiting for screen",
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
            "extract_failed": "Extraction failed: {error}",

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

    def run(self):
        keyboard.add_hotkey("F4", self.extract_url)
        keyboard.add_hotkey("F3", self.extract_number)
        keyboard.wait()


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
        self.setFixedSize(750, 600)

        # 检查程序目录是否包含中文
        if self.contains_chinese(self.script_dir):
            self.update_status(f"⚠️ 警告：程序所在文件夹路径包含中文字符")
            self.update_status(f"   当前路径：{self.script_dir}")
            self.update_status(f"   建议：将程序文件夹放在不含中文的路径下")
            self.update_status(f"   这可能导致 OpenCV 无法读取截图文件")

        # 配置文件路径
        self.config_file = os.path.join(self.script_dir, "config.json")

        # 错误日志文件路径
        self.error_log_file = os.path.join(self.script_dir, "error_log.txt")

        # 失败账号导出文件路径
        self.failed_file = os.path.join(self.script_dir, "failed_accounts.txt")

        # 用户截取的验证码界面截图路径
        self.user_screenshot_path = ""

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

    def contains_chinese(self, text):
        """检测文本中是否包含中文字符"""
        return any('\u4e00' <= char <= '\u9fff' for char in text)

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
        self.capture_btn.setText(self.get_text("btn_capture"))
        self.test_screenshot_btn.setText(self.get_text("btn_test"))

        # 更新语言选择器文本
        self.language_label.setText(self.get_text("language") + ":")
        self.language_combo.setItemText(0, self.get_text("chinese"))
        self.language_combo.setItemText(1, self.get_text("english"))

    def setup_ui(self):
        """设置UI布局"""
        # 主布局
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # 标题和语言选择行
        title_row = QHBoxLayout()

        self.title_label = QLabel("🚀 " + self.get_text("window_title"))
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setFont(QFont("Microsoft YaHei", 16, QFont.Bold))

        # 语言选择器
        self.language_label = QLabel(self.get_text("language") + ":")
        self.language_label.setFont(QFont("Microsoft YaHei", 10))

        self.language_combo = QComboBox()
        self.language_combo.addItems([self.get_text("chinese"), self.get_text("english")])
        self.language_combo.setCurrentIndex(0 if self.current_language == Translations.ZH else 1)
        self.language_combo.currentIndexChanged.connect(self.switch_language)
        self.language_combo.setStyleSheet("""
            QComboBox {
                padding: 5px 10px;
                border: 1px solid #4CAF50;
                border-radius: 3px;
                background-color: white;
                font-size: 10px;
            }
            QComboBox::drop-down {
                border: none;
            }
        """)

        title_row.addWidget(self.title_label)
        title_row.addStretch()
        title_row.addWidget(self.language_label)
        title_row.addWidget(self.language_combo)

        main_layout.addLayout(title_row)

        # 状态统计面板
        self.stats_group = QGroupBox(self.get_text("stats_title"))
        stats_layout = QHBoxLayout()

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
        self.text_edit.setMaximumHeight(200)
        input_layout.addWidget(self.text_edit)

        self.input_group.setLayout(input_layout)
        main_layout.addWidget(self.input_group)

        # 当前操作状态
        self.status_group = QGroupBox(self.get_text("status_title"))
        status_layout = QVBoxLayout()
        self.status_label = QLabel(self.get_text("status_waiting"))
        self.status_label.setAlignment(Qt.AlignLeft)
        self.status_label.setWordWrap(True)
        self.status_label.setFont(QFont("Microsoft YaHei", 10))
        status_layout.addWidget(self.status_label)
        self.status_group.setLayout(status_layout)
        main_layout.addWidget(self.status_group)

        # 按钮和选项区域
        control_layout = QVBoxLayout()

        # 第一行：提示和复选框
        control_row1 = QHBoxLayout()

        self.start_label = QLabel(self.get_text("lbl_start"))
        self.start_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #4CAF50;
                padding: 10px 15px;
                background-color: #E8F5E9;
                border: 2px solid #4CAF50;
                border-radius: 5px;
            }
        """)

        self.input_plus_one = QCheckBox(self.get_text("chk_input_plus_one"))
        self.input_plus_one.setChecked(False)
        self.input_plus_one.setFont(QFont("Microsoft YaHei", 12, QFont.Bold))
        self.input_plus_one.setStyleSheet("""
            QCheckBox {
                color: #333;
                padding: 10px 15px;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
                border: 2px solid #4CAF50;
                border-radius: 3px;
                background-color: white;
            }
            QCheckBox::indicator:checked {
                background-color: #4CAF50;
                border: 2px solid #4CAF50;
            }
            QCheckBox::indicator:hover {
                border: 2px solid #45a049;
            }
        """)

        control_row1.addWidget(self.start_label)
        control_row1.addWidget(self.input_plus_one)
        control_row1.addStretch()

        # 第二行：操作按钮
        control_row2 = QHBoxLayout()

        self.clear_btn = QPushButton(self.get_text("btn_clear"))
        self.clear_btn.clicked.connect(self.clear_text)
        self.clear_btn.setMinimumWidth(150)

        self.retry_btn = QPushButton(self.get_text("btn_retry"))
        self.retry_btn.clicked.connect(self.retry_failed_accounts)
        self.retry_btn.setEnabled(False)
        self.retry_btn.setMinimumWidth(170)

        self.export_btn = QPushButton(self.get_text("btn_export"))
        self.export_btn.clicked.connect(self.export_failed_accounts)
        self.export_btn.setEnabled(False)
        self.export_btn.setMinimumWidth(150)

        self.capture_btn = QPushButton(self.get_text("btn_capture"))
        self.capture_btn.clicked.connect(self.capture_screenshot)
        self.capture_btn.setMinimumWidth(160)
        self.capture_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 15px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
        """)

        self.test_screenshot_btn = QPushButton(self.get_text("btn_test"))
        self.test_screenshot_btn.clicked.connect(self.test_screenshot)
        self.test_screenshot_btn.setMinimumWidth(120)

        control_row2.addWidget(self.clear_btn)
        control_row2.addWidget(self.retry_btn)
        control_row2.addWidget(self.export_btn)
        control_row2.addWidget(self.capture_btn)
        control_row2.addWidget(self.test_screenshot_btn)

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

    def capture_screenshot(self):
        """
        自动截取验证码界面
        1. 提示用户打开登录界面
        2. 自动调用系统截图工具
        3. 用户框选验证码界面
        4. 从剪贴板获取截图
        5. 自动保存到程序目录
        6. 自动验证并加载
        """
        # 第一步：提示用户准备
        msg_box = QMessageBox()
        msg_box.setWindowTitle(self.get_text("screenshot_title"))
        msg_box.setText(self.get_text("screenshot_prepare"))
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)

        # 记录第一个弹窗的位置
        first_dialog_pos = None

        if msg_box.exec_() == QMessageBox.Cancel:
            return

        # 记录第一个弹窗的位置
        first_dialog_pos = msg_box.pos()

        # 第二步：等待用户截图
        self.update_status("等待用户截图...")

        instruction_box = QMessageBox()
        instruction_box.setWindowTitle(self.get_text("screenshot_title"))
        instruction_box.setText(self.get_text("screenshot_waiting"))
        instruction_box.setIcon(QMessageBox.Information)
        instruction_box.setStandardButtons(QMessageBox.Cancel)

        # 如果第一个弹窗的位置被记录，将第二个弹窗移动到相同位置
        if first_dialog_pos:
            instruction_box.move(first_dialog_pos)

        # 添加自定义按钮
        done_button = instruction_box.addButton(self.get_text("screenshot_done"), QMessageBox.ActionRole)
        cancel_button = instruction_box.button(QMessageBox.Cancel)
        cancel_button.setText(self.get_text("screenshot_cancel"))

        # 延迟0.5秒后自动调用截图工具
        QTimer.singleShot(500, self.trigger_screenshot)

        instruction_box.exec_()

        if instruction_box.clickedButton() != done_button:
            self.update_status("截图已取消")
            return

        # 第三步：从剪贴板获取截图
        self.update_status("正在从剪贴板获取截图...")

        try:
            from PIL import ImageGrab

            # 获取剪贴板中的图片
            img = ImageGrab.grabclipboard()

            if img is None:
                QMessageBox.warning(self, "错误",
                                  "未能从剪贴板获取到截图！\n\n"
                                  "请确保：\n"
                                  "1. 您已经使用截图工具截图\n"
                                  "2. 截图成功保存到剪贴板\n"
                                  "3. 没有复制其他内容到剪贴板")
                self.update_status("截图获取失败")
                return

            # 第四步：自动保存到程序目录
            screenshot_filename = "verification_code_screenshot.png"
            screenshot_path = os.path.join(self.script_dir, screenshot_filename)

            img.save(screenshot_path, "PNG")
            self.update_status(f"截图已保存：{screenshot_filename}")

            # 第五步：验证并加载截图
            check_result, valid_path = self.check_image_file(screenshot_path)
            if check_result:
                self.user_screenshot_path = screenshot_path
                self.update_status(f"✅ 验证码界面截图已加载：{screenshot_filename}")

                QMessageBox.information(self, "成功",
                                      f"验证码界面截图已成功截取并加载！\n\n"
                                      f"文件：{screenshot_filename}\n"
                                      f"保存位置：{self.script_dir}\n\n"
                                      f"现在可以按F3开始自动登录了。")
            else:
                QMessageBox.warning(self, "错误",
                                  "截图验证失败，请检查截图内容。\n\n"
                                  "建议：\n"
                                  "1. 确保截图包含完整的验证码界面\n"
                                  "2. 截图宽度建议在 800-1920 像素之间\n"
                                  "3. 重新截图，框选更大的区域")
                self.update_status("截图验证失败")

        except Exception as e:
            import traceback
            error_detail = traceback.format_exc()

            # 保存错误日志
            log_content = f"""错误类型: {type(e).__name__}
错误信息: {str(e)}
截图保存路径: {screenshot_path if 'screenshot_path' in locals() else '未知'}
目录: {self.script_dir}

完整堆栈跟踪:
{error_detail}
"""
            self.save_error_log("截图处理错误", log_content)

            self.update_status(f"截图处理失败：{str(e)}")
            self.update_status(f"   详细错误已保存到：{self.error_log_file}")

            QMessageBox.critical(self, "错误",
                              f"截图处理失败：{str(e)}\n\n"
                              f"详细错误信息已保存到：\n{self.error_log_file}\n\n"
                              "请打开该文件查看完整错误信息。\n\n"
                              "请重试或联系开发者。")

    def trigger_screenshot(self):
        """触发系统截图工具"""
        try:
            # 模拟按下 Windows+Shift+S
            pyautogui.hotkey('win', 'shift', 's')
            self.update_status("已打开截图工具，请框选验证码界面")
        except Exception as e:
            self.update_status(f"调用截图工具失败：{str(e)}")

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
                "user_screenshot_path": self.user_screenshot_path,
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
            self.user_screenshot_path = config.get("user_screenshot_path", "")

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

            # 检查截图路径是否有效
            if self.user_screenshot_path:
                # 检查路径是否存在
                if not os.path.exists(self.user_screenshot_path):
                    self.update_status(f"⚠️ 上次保存的截图文件不存在：{self.user_screenshot_path}")
                    # 尝试在当前目录查找默认截图
                    default_screenshot = os.path.join(self.script_dir, "verification_code_screenshot.png")
                    if os.path.exists(default_screenshot):
                        self.user_screenshot_path = default_screenshot
                        self.update_status(f"✅ 已找到当前目录的截图：verification_code_screenshot.png")
                    else:
                        # 清空无效路径
                        self.user_screenshot_path = ""
                        self.update_status(f"⚠️ 未找到截图文件，请重新截取")
                # 如果路径包含中文，提示用户
                elif self.contains_chinese(self.user_screenshot_path):
                    self.update_status(f"⚠️ 检测到中文路径，建议将截图文件放在程序目录下")
                    self.update_status(f"   当前路径：{self.user_screenshot_path}")

            # 恢复文本框内容
            self.text_edit.setText(text_content)

            # 更新统计信息
            self.update_stats()

            # 更新按钮状态
            if self.failed_accounts:
                self.retry_btn.setEnabled(True)
                self.export_btn.setEnabled(True)

            if self.user_screenshot_path:
                self.update_status(f"✅ 已加载上次保存的验证码截图")

            return True

        except Exception as e:
            print(f"加载配置失败: {e}")
            return False

    def test_screenshot(self):
        """
        测试截图文件是否可以被正确识别
        1. 检测当前目录下有没有截图
        2. 没有截图提示用户进行截取验证码界面的图片
        3. 有的话尝试识别
        4. 识别失败提示用户重新截取
        5. 识别成功则提示截图可用，请开始登录
        """
        # 检查当前目录下是否有验证码界面截图
        default_screenshot_name = "verification_code_screenshot.png"
        default_screenshot_path = os.path.join(self.script_dir, default_screenshot_name)

        # 如果已加载的截图路径存在且文件存在
        if self.user_screenshot_path and os.path.exists(self.user_screenshot_path):
            image_path = self.user_screenshot_path
            self.update_status(f"✅ 检测到已加载的截图")
        # 否则检查默认路径
        elif os.path.exists(default_screenshot_path):
            image_path = default_screenshot_path
            self.update_status(f"✅ 检测到当前目录的截图文件")
        else:
            # 没有截图，提示用户截取
            reply = QMessageBox.question(
                self,
                "未检测到截图",
                "❌ 当前目录下没有找到验证码界面截图。\n\n"
                "是否现在截取验证码界面？\n\n"
                "截取后程序会自动识别是否可用。",
                QMessageBox.Yes | QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                self.capture_screenshot()
                # 检查是否成功截取
                if self.user_screenshot_path and os.path.exists(self.user_screenshot_path):
                    image_path = self.user_screenshot_path
                elif os.path.exists(default_screenshot_path):
                    image_path = default_screenshot_path
                else:
                    self.update_status("❌ 未成功截取截图")
                    return
            else:
                self.update_status("❌ 请先截取验证码界面")
                return

        # 检查文件
        self.update_status(f"正在检查截图文件...")
        check_result, abs_image_path = self.check_image_file(image_path)

        if not check_result:
            # 文件检查失败，提示重新截取
            reply = QMessageBox.question(
                self,
                "截图检查失败",
                "❌ 截图文件检查失败。\n\n"
                "是否重新截取验证码界面？",
                QMessageBox.Yes | QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                self.capture_screenshot()
                if self.user_screenshot_path and os.path.exists(self.user_screenshot_path):
                    image_path = self.user_screenshot_path
                elif os.path.exists(default_screenshot_path):
                    image_path = default_screenshot_path
                else:
                    self.update_status("❌ 重新截取失败")
                    return

                # 再次检查
                check_result, abs_image_path = self.check_image_file(image_path)
                if not check_result:
                    self.update_status("❌ 重新截取后仍然检查失败")
                    return
            else:
                self.update_status("❌ 截图不可用")
                return

        # 文件检查通过，尝试识别
        try:
            self.update_status(f"正在尝试在屏幕上识别截图...")
            self.update_status(f"   使用的截图路径：{abs_image_path}")
            self.update_status(f"   文件大小：{os.path.getsize(abs_image_path)} 字节")

            # 读取图片尺寸
            from PIL import Image
            with Image.open(abs_image_path) as img:
                width, height = img.size
                self.update_status(f"   图片尺寸：{width} x {height}")

            # 尝试识别（confidence 从 0.8 开始，如果失败可以尝试更低的值）
            location = pyautogui.locateOnScreen(abs_image_path, confidence=0.8)

            if location:
                # 识别成功
                # 如果还没加载，自动加载截图
                if not self.user_screenshot_path:
                    self.user_screenshot_path = image_path  # 保存原始路径
                    self.save_config()

                self.update_status(f"✅ 截图识别成功！")
                self.update_status(f"   截图文件：{os.path.basename(image_path)}")
                self.update_status(f"   匹配位置：{location}")

                # 显示成功提示
                QMessageBox.information(
                    self,
                    "截图可用",
                    "✅ 截图识别成功！\n\n"
                    f"截图文件：{os.path.basename(image_path)}\n"
                    f"匹配位置：{location}\n\n"
                    "🚀 现在可以按 F3 开始自动登录了！"
                )
            else:
                # 识别失败，尝试降低置信度
                self.update_status(f"⚠️ 第一次识别失败，尝试降低置信度...")
                try:
                    location = pyautogui.locateOnScreen(abs_image_path, confidence=0.6)
                    if location:
                        self.update_status(f"✅ 降低置信度后识别成功！")
                        if not self.user_screenshot_path:
                            self.user_screenshot_path = image_path  # 保存原始路径
                            self.save_config()
                        QMessageBox.information(
                            self,
                            "截图可用",
                            "✅ 截图识别成功！（较低置信度）\n\n"
                            f"截图文件：{os.path.basename(image_path)}\n"
                            f"匹配位置：{location}\n\n"
                            "🚀 现在可以按 F3 开始自动登录了！"
                        )
                        return
                except:
                    pass

                # 识别失败
                self.update_status(f"❌ 截图识别失败")
                self.update_status(f"   原因：屏幕上未找到与截图匹配的区域")
                self.update_status(f"   建议：请打开验证码界面后再试")

                reply = QMessageBox.question(
                    self,
                    "截图识别失败",
                    "❌ 在屏幕上未找到与截图匹配的区域。\n\n"
                    "可能原因：\n"
                    "1. 截图与当前屏幕界面不一致\n"
                    "2. 截图包含动态内容（如时间）\n"
                    "3. 验证码界面未打开或被遮挡\n\n"
                    "是否重新截取验证码界面？",
                    QMessageBox.Yes | QMessageBox.No
                )

                if reply == QMessageBox.Yes:
                    self.capture_screenshot()
                    if self.user_screenshot_path and os.path.exists(self.user_screenshot_path):
                        image_path = self.user_screenshot_path
                    elif os.path.exists(default_screenshot_path):
                        image_path = default_screenshot_path
                    else:
                        self.update_status("❌ 重新截取失败")
                        return

                    # 再次尝试识别
                    self.update_status(f"正在重新尝试识别...")
                    check_result, abs_image_path = self.check_image_file(image_path)
                    if not check_result:
                        self.update_status("❌ 重新截图后检查失败")
                        return

                    try:
                        location = pyautogui.locateOnScreen(abs_image_path, confidence=0.8)
                    except Exception as retry_e:
                        self.update_status(f"❌ 重新识别时出错：{str(retry_e)}")
                        QMessageBox.warning(
                            self,
                            "识别出错",
                            f"❌ 重新识别时出错：\n\n{str(retry_e)}\n\n"
                            "请尝试重新截图或联系开发者。"
                        )
                        return

                    if location:
                        # 重新识别成功
                        if not self.user_screenshot_path:
                            self.user_screenshot_path = image_path  # 保存原始路径
                            self.save_config()

                        self.update_status(f"✅ 重新截图后识别成功！")
                        self.update_status(f"   截图文件：{os.path.basename(image_path)}")

                        QMessageBox.information(
                            self,
                            "截图可用",
                            "✅ 重新截图后识别成功！\n\n"
                            f"截图文件：{os.path.basename(image_path)}\n"
                            f"匹配位置：{location}\n\n"
                            "🚀 现在可以按 F3 开始自动登录了！"
                        )
                    else:
                        self.update_status(f"❌ 重新截图后仍然识别失败")
                        QMessageBox.warning(
                            self,
                            "识别失败",
                            "❌ 重新截图后仍然无法识别。\n\n"
                            "请确保：\n"
                            "1. 验证码界面已打开\n"
                            "2. 截图包含完整的验证码界面\n"
                            "3. 截图内容与当前界面一致"
                        )
                else:
                    self.update_status("❌ 截图不可用")

        except Exception as e:
            import traceback
            error_detail = traceback.format_exc()

            # 检查是否是 OpenCV 读取错误（OSError）
            if isinstance(e, OSError) and "Failed to read" in str(e):
                # 保存详细错误到日志文件
                log_content = f"""错误类型: {type(e).__name__}
错误信息: {str(e)}
截图路径: {abs_image_path}
文件是否存在: {os.path.exists(abs_image_path) if 'abs_image_path' in locals() else '未知'}
文件大小: {os.path.getsize(abs_image_path) if 'abs_image_path' in locals() and os.path.exists(abs_image_path) else '未知'}

完整堆栈跟踪:
{error_detail}

环境信息:
- Python版本: {sys.version}
- 当前目录: {self.script_dir}
- 已保存的截图路径: {self.user_screenshot_path}
"""
                self.save_error_log("截图识别错误", log_content)

                self.update_status(f"❌ 截图识别出错")
                self.update_status(f"   错误：无法读取截图文件")

                # 显示友好的错误提示
                QMessageBox.warning(
                    self,
                    "截图识别失败",
                    "❌ 截图识别失败\n\n"
                    "可能原因：\n"
                    "1. Telegram 窗口太小\n"
                    "2. 截图分辨率过低或格式不正确\n"
                    "3. 文件路径包含中文字符\n\n"
                    "解决方法：\n"
                    "1. 将 Telegram 窗口拉大，确保窗口尺寸足够\n"
                    "2. 重新截图，框选更大的区域\n"
                    "3. 将程序文件夹和截图文件放在不含中文的路径下\n"
                    "4. 确保截图文件为 PNG 格式\n\n"
                    f"详细错误信息已保存到：\n{self.error_log_file}"
                )
                return

            # 其他错误处理
            # 保存详细错误到日志文件
            log_content = f"""错误类型: {type(e).__name__}
错误信息: {str(e)}
截图路径: {abs_image_path}
文件是否存在: {os.path.exists(abs_image_path) if 'abs_image_path' in locals() else '未知'}
文件大小: {os.path.getsize(abs_image_path) if 'abs_image_path' in locals() and os.path.exists(abs_image_path) else '未知'}

完整堆栈跟踪:
{error_detail}

环境信息:
- Python版本: {sys.version}
- 当前目录: {self.script_dir}
- 已保存的截图路径: {self.user_screenshot_path}
"""
            self.save_error_log("截图识别错误", log_content)

            self.update_status(f"❌ 截图识别过程出错：{str(e)}")
            self.update_status(f"   详细错误已保存到：{self.error_log_file}")

            # 显示简化的错误信息
            reply = QMessageBox.question(
                self,
                "识别出错",
                f"❌ 截图识别过程出错：\n\n"
                f"错误：{str(e)}\n\n"
                f"详细错误信息已保存到：\n{self.error_log_file}\n\n"
                "请打开该文件查看完整错误信息。\n\n"
                "是否重新截取验证码界面？",
                QMessageBox.Yes | QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                self.capture_screenshot()

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

    def check_image_file(self, image_path):
        """
        检查截图文件是否存在且可读

        Args:
            image_path: 截图文件路径（相对路径或绝对路径）

        Returns:
            tuple: (bool: 是否存在且可读, str: 可读取的文件路径)
        """
        # 支持绝对路径和相对路径
        if os.path.isabs(image_path):
            abs_image_path = image_path
        else:
            abs_image_path = os.path.join(self.script_dir, image_path)

        # 检查文件是否存在
        if not os.path.exists(abs_image_path):
            self.update_status(f"❌ 截图文件不存在：{image_path}")
            self.update_status(f"   完整路径：{abs_image_path}")
            return False, ""

        # 检查是否包含中文路径
        if self.contains_chinese(abs_image_path):
            self.update_status(f"⚠️ 检测到中文路径：{abs_image_path}")
            self.update_status(f"   建议：将程序文件夹和截图文件放在不含中文的路径下")
            self.update_status(f"   这可能导致 OpenCV 无法读取文件")

        # 检查文件大小
        file_size = os.path.getsize(abs_image_path)
        if file_size == 0:
            self.update_status(f"❌ 截图文件为空：{image_path}")
            self.update_status(f"   文件大小：0 字节")
            return False, ""

        # 检查文件是否可读
        if not os.access(abs_image_path, os.R_OK):
            self.update_status(f"❌ 截图文件无读取权限：{image_path}")
            self.update_status(f"   完整路径：{abs_image_path}")
            return False, ""

        # 检查截图分辨率
        try:
            from PIL import Image
            with Image.open(abs_image_path) as img:
                width, height = img.size

                self.update_status(f"📊 截图分辨率：{width}x{height}")

                # 检查分辨率是否过大或过小
                if width < 400 or height < 300:
                    self.update_status(f"❌ 截图分辨率过小：{width}x{height}")
                    self.update_status(f"   最小要求：宽400px × 高300px")
                    self.update_status(f"   当前尺寸：宽{width}px × 高{height}px")
                    self.update_status(f"   差距：还需要宽度{400-width}px 或 高度{300-height}px")
                    self.update_status(f"   解决方法：")
                    self.update_status(f"   1. 重新截图，确保截取更完整的界面")
                    self.update_status(f"   2. 不要只截取一个小区域，要包含整个窗口")
                    self.update_status(f"   3. 使用 Windows+Shift+S 进行全屏或窗口截图")
                    return False, ""

                if width > 4000 or height > 3000:
                    self.update_status(f"❌ 截图分辨率过大：{width}x{height}")
                    self.update_status(f"   最大要求：宽4000px × 高3000px")
                    self.update_status(f"   当前尺寸：宽{width}px × 高{height}px")
                    self.update_status(f"   解决方法：")
                    self.update_status(f"   1. 使用画图工具打开截图")
                    self.update_status(f"   2. 选择\"重新调整大小\"功能")
                    self.update_status(f"   3. 将宽度设置为 1000-1920 之间")
                    self.update_status(f"   4. 保存为 PNG 格式")
                    return False, ""

                # 推荐分辨率范围
                if 800 <= width <= 1920 and 600 <= height <= 1080:
                    self.update_status(f"✅ 截图分辨率合适：{width}x{height}")
                else:
                    self.update_status(f"ℹ️ 截图分辨率：{width}x{height}（建议 800-1920 x 600-1080）")

        except Exception as e:
            import traceback
            error_detail = traceback.format_exc()

            # 保存错误日志
            log_content = f"""错误类型: {type(e).__name__}
错误信息: {str(e)}
截图路径: {abs_image_path}
文件是否存在: {os.path.exists(abs_image_path)}
文件大小: {os.path.getsize(abs_image_path) if os.path.exists(abs_image_path) else '未知'}

完整堆栈跟踪:
{error_detail}
"""
            self.save_error_log("截图文件检查错误", log_content)

            self.update_status(f"❌ 无法读取截图分辨率：{str(e)}")
            self.update_status(f"   原因：文件可能损坏或格式不正确")
            self.update_status(f"   详细错误已保存到：{self.error_log_file}")
            self.update_status(f"   解决方法：")
            self.update_status(f"   1. 用画图工具打开截图")
            self.update_status(f"   2. 另存为 PNG 格式")
            return False, ""

        return True, abs_image_path

    def wait_for_screen(self, image_path, timeout=30, check_interval=0.5):
        """
        等待指定的界面出现

        Args:
            image_path: 界面截图路径（相对路径或绝对路径）
            timeout: 超时时间（秒）
            check_interval: 检测间隔（秒）

        Returns:
            bool: 是否检测到界面
        """
        # 先检查文件是否存在
        check_result, abs_image_path = self.check_image_file(image_path)
        if not check_result:
            return False

        # 首次读取截图以验证文件格式
        try:
            from PIL import Image
            img = Image.open(abs_image_path)
            width, height = img.size
            self.update_status(f"加载截图：{os.path.basename(image_path)} ({width}x{height})")
        except Exception as e:
            self.update_status(f"❌ 无法加载截图文件：{str(e)}")
            self.update_status(f"   建议：使用 Windows 自带的画图工具重新保存截图为 PNG 格式")
            return False

        start_time = time.time()
        attempt_count = 0
        while time.time() - start_time < timeout:
            attempt_count += 1
            try:
                location = pyautogui.locateOnScreen(abs_image_path, confidence=0.8)
                if location:
                    self.update_status(f"✅ 检测到界面: {os.path.basename(image_path)} (第{attempt_count}次尝试)")
                    return True
            except OSError as oe:
                # OpenCV 读取错误，记录到日志
                if attempt_count % 10 == 1:  # 每隔几次记录一次
                    self.update_status(f"⚠️ 等待界面时出现读取错误: {str(oe)}")
                    self.update_status(f"   可能原因：窗口太小或截图文件有问题")
            except Exception as e:
                if attempt_count % 10 == 1:  # 每隔几次打印一次错误
                    pass  # 静默处理，避免刷屏

            time.sleep(check_interval)

        self.update_status(f"❌ 超时：未检测到界面 {os.path.basename(image_path)}")
        self.update_status(f"   检测次数：{attempt_count}次，用时：{timeout}秒")
        self.update_status(f"   建议：点击\"测试截图\"按钮检查截图是否正确")
        return False

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

            # 6. 检查用户是否已截取验证码界面
            if not self.user_screenshot_path:
                self.update_status("login_no_screenshot",
                                 current=self.current_index + 1)
                self.update_status("login_capture_hint")
                self.record_failed_account(line)
                return

            # 7. 等待验证码界面出现（优化检测间隔）
            if not self.wait_for_screen(self.user_screenshot_path, timeout=30, check_interval=0.2):  # 优化：减少检测间隔
                self.update_status("login_timeout",
                                 current=self.current_index + 1)
                self.record_failed_account(line)
                return

            # 8. 后台提取验证码和密码
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

            # 2. 延迟1秒（优化：减少延迟）
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

                # 5. 再按一次回车
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
        注意：不删除临时截图文件，因为它们可能在下次启动时被使用
        """
        # 临时文件由系统自动管理，不手动删除
        # 这样可以保证重新打开程序时能够正常加载之前的截图配置
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = ExtractorApp()
    win.show()
    sys.exit(app.exec_())
