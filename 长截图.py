"""
自动滚动长截图工具 - 增强版
功能：
1. 拖拽选择屏幕上的截图区域
2. 自动滚动并连续截取该区域（支持全局热键）
3. 简单拼接（无重叠检测）
4. 自动拼接成完整长图
5. 支持中英文切换
6. 支持自定义全局快捷键
7. 自动检查更新
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import pyautogui
import threading
import time
import os
import sys
import json
from datetime import datetime
import pyperclip
import keyboard
import io
try:
    import requests
except ImportError:
    requests = None


def get_app_dir():
    """获取应用目录（开发环境和打包环境通用）"""
    if getattr(sys, 'frozen', False):
        # 打包后的 EXE
        return os.path.dirname(sys.executable)
    else:
        # 开发环境
        return os.path.dirname(os.path.abspath(__file__))

# ========================================
# 版本和更新配置（每次发布新版本时修改）
# ========================================

# 当前版本号
CURRENT_VERSION = "v10.0.0"

# 更新检查 API（自动获取最新版本）
UPDATE_CHECK_API = "https://api.github.com/repos/suzheng6/AutoUpdate/releases/latest"

# GitHub Releases 下载页面
RELEASES_PAGE_URL = "https://github.com/suzheng6/AutoUpdate/releases"

# 是否启用自动更新检查（True: 启用, False: 禁用）
ENABLE_AUTO_UPDATE = True

# 每次启动都检查更新（True: 每次都检查, False: 每天只检查一次）
CHECK_UPDATE_EVERY_START = True

# ========================================


class UpdateManager:
    """更新管理器 - 负责检查程序更新"""

    def __init__(self, current_version, api_url, releases_url):
        self.current_version = current_version
        self.api_url = api_url
        self.releases_url = releases_url
        self.latest_version = None
        self.new_version_available = False
        self.download_url = None
        self.release_notes = ""

    def check_for_updates(self):
        """
        检查是否有新版本
        返回: (是否更新, 最新版本, 下载链接, 更新说明)
        """
        if requests is None:
            print("[更新检查] requests 库未安装，跳过更新检查")
            return False, None, None, ""

        try:
            print(f"[更新检查] 检查更新: {self.api_url}")
            response = requests.get(self.api_url, timeout=10)
            response.raise_for_status()

            data = response.json()
            latest_version = data.get('tag_name', '')
            release_notes = data.get('body', '')
            html_url = data.get('html_url', self.releases_url)

            print(f"[更新检查] 当前版本: {self.current_version}")
            print(f"[更新检查] 最新版本: {latest_version}")

            # 比较版本号
            if self._compare_versions(self.current_version, latest_version) < 0:
                print(f"[更新检查] 发现新版本！")
                self.latest_version = latest_version
                self.new_version_available = True
                self.download_url = html_url
                self.release_notes = release_notes
                return True, latest_version, html_url, release_notes
            else:
                print(f"[更新检查] 当前已是最新版本")
                return False, latest_version, html_url, release_notes

        except Exception as e:
            print(f"[更新检查] 检查失败: {e}")
            return False, None, None, ""

    def _compare_versions(self, v1, v2):
        """
        比较版本号
        返回: -1 (v1 < v2), 0 (v1 == v2), 1 (v1 > v2)
        """
        # 移除版本号前缀 'v'
        v1 = v1.lstrip('v')
        v2 = v2.lstrip('v')

        # 分割版本号
        parts1 = v1.split('.')
        parts2 = v2.split('.')

        # 补齐长度
        max_len = max(len(parts1), len(parts2))
        parts1.extend(['0'] * (max_len - len(parts1)))
        parts2.extend(['0'] * (max_len - len(parts2)))

        # 逐位比较
        for p1, p2 in zip(parts1, parts2):
            try:
                n1 = int(p1)
                n2 = int(p2)
            except ValueError:
                # 如果不是数字，按字符串比较
                n1 = p1
                n2 = p2

            if n1 < n2:
                return -1
            elif n1 > n2:
                return 1

        return 0


class LanguageManager:
    """语言管理器"""

    def __init__(self, config_path='language_config.json'):
        # 获取应用目录（兼容开发和打包环境）
        script_dir = get_app_dir()
        self.config_path = os.path.join(script_dir, config_path)
        self.current_lang = 'zh'

        # 确保目录存在
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)

        self.translations = self.load_translations()

    def get_default_translations(self):
        """获取默认翻译配置"""
        return {
            "zh": {
                "app_title": "自动滚动长截图工具",
                "menu_file": "文件",
                "menu_edit": "编辑",
                "menu_help": "帮助",
                "menu_save": "保存截图",
                "menu_copy": "复制到剪贴板",
                "menu_clear": "清空所有",
                "menu_settings": "快捷键设置",
                "menu_language": "切换语言",
                "menu_about": "关于",
                "menu_exit": "退出",
                "btn_select_region": "选择区域",
                "btn_start": "开始自动滚动",
                "btn_stop": "停止",
                "btn_save": "保存图片",
                "btn_clear": "清空",
                "status_ready": "就绪",
                "status_recording": "录制中...",
                "label_scroll_speed": "滚动速度:",
                "label_scroll_distance": "滚动距离:",
                "settings_title": "快捷键设置",
                "settings_header_action": "操作",
                "settings_header_shortcut": "快捷键",
                "settings_header_record": "录制",
                "settings_save": "保存",
                "settings_cancel": "取消",
                "settings_default": "恢复默认",
                "action_select_region": "选择区域",
                "action_start_stop": "开始/停止录制",
                "action_stop": "停止录制",
                "action_save": "保存结果",
                "action_copy": "复制到剪贴板",
                "action_clear": "清空所有",
                "action_cancel": "取消操作",
                "action_language": "切换语言",
                "record_press": "按键...",
                "hint_region": "请先选择截图区域",
                "hint_recording": "滚动并截图中...",
                "success_saved": "截图已保存: {}",
                "success_copied": "截图已复制到剪贴板",
                "error_no_image": "没有可保存的截图",
                "error_region": "请先选择截图区域",
                "about_title": "关于",
                "about_content": "自动滚动长截图工具 v1.0\n\n功能:\n1. 拖拽选择屏幕区域\n2. 自动滚动截图\n3. 智能拼接\n4. 全局快捷键",
                "update_available_title": "发现新版本",
                "current_version": "当前版本: {}",
                "new_version": "最新版本: {}",
                "release_notes": "更新说明:",
                "download_now": "立即下载",
                "remind_later": "稍后提醒",
                "skip_this_version": "跳过此版本",
                "msg_success_saved": "截图已保存\n\n路径: {path}\n尺寸: {width}x{height}\n截图数量: {count}",
                "msg_error_save": "保存失败: {error}",
                "msg_success_copied": "截图已复制到剪贴板",
                "msg_error_copy": "复制失败: {error}",
                "msg_warning_no_screenshot": "没有可保存的截图",
                "msg_warning_no_copy": "没有可复制的截图",
                "count_value": "已截图: {count} 张",
                "status_stitching": "拼接中 ({width}x{height})",
                "status_title": "状态",
                "region_label": "选择区域",
                "count_label": "截图数量",
                "preview_title": "预览",
                "select_region_hint": "拖拽鼠标选择截图区域",
                "region_selected": "已选择区域: {}",
                "msg_warning_select": "请先选择截图区域",
                "msg_success_stitched": "拼接完成！\n\n截图数量: {count}\n最终尺寸: {width}x{height}px",
                "msg_error_stitch": "拼接失败: {error}",
                "msg_settings_saved": "快捷键设置已保存！",
                "btn_save_settings": "保存设置",
                "btn_reset_settings": "恢复默认",
                "no_release_notes": "暂无更新说明",
                "hotkey_select_region": "选择区域",
                "hotkey_start_stop_recording": "开始/停止录制",
                "hotkey_stop_recording": "停止录制",
                "hotkey_save_result": "保存结果",
                "hotkey_copy_to_clipboard": "复制到剪贴板",
                "hotkey_clear_all": "清空所有",
                "hotkey_switch_language": "切换语言",
                "btn_record": "录制",
                "record_press_hint": "请按键...",
                "hotkeys_config_title": "快捷键配置",
                "btn_language": "切换语言",
                "btn_shortcuts": "快捷键设置",
                "usage_title": "使用说明",
                "usage_instructions": "1. 点击「选择区域」或使用快捷键 (Ctrl+Shift+S) 选择截图区域\n2. 点击「开始自动滚动」或使用快捷键 (Ctrl+Shift+R) 开始自动滚动截图\n3. 程序会自动滚动并连续截取该区域，检测到页面底部时自动停止\n4. 点击「停止」或使用快捷键 (Ctrl+Shift+E) 手动停止\n5. 程序会自动拼接所有截图为完整长图\n6. 点击「保存图片」或使用快捷键 (Ctrl+Shift+W) 保存结果\n7. 点击「复制到剪贴板」或使用快捷键 (Ctrl+Shift+C) 复制到剪贴板",
                "btn_select_region": "选择区域",
                "btn_start_recording": "开始自动滚动",
                "btn_stop_recording": "停止",
                "btn_save": "保存图片",
                "btn_copy": "复制到剪贴板",
                "btn_clear": "清空",
                "stitch_mode_title": "拼接模式",
                "stitch_mode_vertical": "垂直拼接（长图）",
                "stitch_mode_grid": "网格拼接（多列）",
                "stitch_mode_desc_vertical": "所有图片垂直拼接成一张长图，适合连续内容（如长网页、聊天记录）",
                "stitch_mode_desc_grid": "图片按网格布局拼接，从上到下、从左到右排列，适合多张独立截图"
            },
            "en": {
                "app_title": "Auto Scroll Screenshot Tool",
                "menu_file": "File",
                "menu_edit": "Edit",
                "menu_help": "Help",
                "menu_save": "Save Screenshot",
                "menu_copy": "Copy to Clipboard",
                "menu_clear": "Clear All",
                "menu_settings": "Hotkey Settings",
                "menu_language": "Switch Language",
                "menu_about": "About",
                "menu_exit": "Exit",
                "btn_select_region": "Select Region",
                "btn_start": "Start Auto Scroll",
                "btn_stop": "Stop",
                "btn_save": "Save Image",
                "btn_clear": "Clear",
                "status_ready": "Ready",
                "status_recording": "Recording...",
                "label_scroll_speed": "Scroll Speed:",
                "label_scroll_distance": "Scroll Distance:",
                "settings_title": "Hotkey Settings",
                "settings_header_action": "Action",
                "settings_header_shortcut": "Shortcut",
                "settings_header_record": "Record",
                "settings_save": "Save",
                "settings_cancel": "Cancel",
                "settings_default": "Reset to Default",
                "action_select_region": "Select Region",
                "action_start_stop": "Start/Stop Recording",
                "action_stop": "Stop Recording",
                "action_save": "Save Result",
                "action_copy": "Copy to Clipboard",
                "action_clear": "Clear All",
                "action_cancel": "Cancel Operation",
                "action_language": "Switch Language",
                "record_press": "Press key...",
                "hint_region": "Please select screenshot region first",
                "hint_recording": "Scrolling and capturing...",
                "success_saved": "Screenshot saved: {}",
                "success_copied": "Screenshot copied to clipboard",
                "error_no_image": "No screenshot to save",
                "error_region": "Please select screenshot region first",
                "about_title": "About",
                "about_content": "Auto Scroll Screenshot Tool v1.0\n\nFeatures:\n1. Drag to select screen region\n2. Auto scroll capture\n3. Smart stitch\n4. Global hotkeys",
                "update_available_title": "New Version Available",
                "current_version": "Current Version: {}",
                "new_version": "Latest Version: {}",
                "release_notes": "Release Notes:",
                "download_now": "Download Now",
                "remind_later": "Remind Later",
                "skip_this_version": "Skip This Version",
                "msg_success_saved": "Screenshot saved\n\nPath: {path}\nSize: {width}x{height}\nCount: {count}",
                "msg_error_save": "Save failed: {error}",
                "msg_success_copied": "Screenshot copied to clipboard",
                "msg_error_copy": "Copy failed: {error}",
                "msg_warning_no_screenshot": "No screenshot to save",
                "msg_warning_no_copy": "No screenshot to copy",
                "count_value": "Screenshots: {count}",
                "status_stitching": "Stitching ({width}x{height})",
                "status_title": "Status",
                "region_label": "Selected Region",
                "count_label": "Screenshot Count",
                "preview_title": "Preview",
                "select_region_hint": "Drag to select screenshot region",
                "region_selected": "Region selected: {}",
                "msg_warning_select": "Please select screenshot region first",
                "msg_success_stitched": "Stitching complete!\n\nCount: {count}\nFinal size: {width}x{height}px",
                "msg_error_stitch": "Stitching failed: {error}",
                "msg_settings_saved": "Hotkey settings saved!",
                "btn_save_settings": "Save Settings",
                "btn_reset_settings": "Reset to Default",
                "no_release_notes": "No release notes",
                "hotkey_select_region": "Select Region",
                "hotkey_start_stop_recording": "Start/Stop Recording",
                "hotkey_stop_recording": "Stop Recording",
                "hotkey_save_result": "Save Result",
                "hotkey_copy_to_clipboard": "Copy to Clipboard",
                "hotkey_clear_all": "Clear All",
                "hotkey_switch_language": "Switch Language",
                "btn_record": "Record",
                "record_press_hint": "Press key...",
                "hotkeys_config_title": "Hotkey Configuration",
                "btn_language": "Switch Language",
                "btn_shortcuts": "Hotkey Settings",
                "usage_title": "Instructions",
                "usage_instructions": "1. Click 'Select Region' or use shortcut (Ctrl+Shift+S) to select screenshot area\n2. Click 'Start Auto Scroll' or use shortcut (Ctrl+Shift+R) to start auto-scrolling screenshot\n3. The program will automatically scroll and continuously capture the area, stopping when it detects the page bottom\n4. Click 'Stop' or use shortcut (Ctrl+Shift+E) to manually stop\n5. The program will automatically stitch all screenshots into a complete long image\n6. Click 'Save Image' or use shortcut (Ctrl+Shift+W) to save the result\n7. Click 'Copy to Clipboard' or use shortcut (Ctrl+Shift+C) to copy to clipboard",
                "btn_select_region": "Select Region",
                "btn_start_recording": "Start Auto Scroll",
                "btn_stop_recording": "Stop",
                "btn_save": "Save Image",
                "btn_copy": "Copy to Clipboard",
                "btn_clear": "Clear",
                "stitch_mode_title": "Stitch Mode",
                "stitch_mode_vertical": "Vertical Stitch (Long Image)",
                "stitch_mode_grid": "Grid Stitch (Multi-Column)",
                "stitch_mode_desc_vertical": "All images stitched vertically into one long image, suitable for continuous content (e.g., long web pages, chat records)",
                "stitch_mode_desc_grid": "Images arranged in grid layout, from top to bottom, left to right, suitable for multiple independent screenshots"
            }
        }

    def load_translations(self):
        """加载翻译配置，不存在则自动生成，存在则合并默认配置"""
        try:
            default_translations = self.get_default_translations()

            if os.path.exists(self.config_path):
                # 读取现有配置
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    existing_translations = json.load(f)

                # 深度合并：优先使用现有配置，但会添加默认配置中新增的键
                merged_translations = {}
                for lang in ['zh', 'en']:
                    merged_translations[lang] = {}
                    # 先复制默认配置（确保所有键都存在）
                    merged_translations[lang].update(default_translations[lang])
                    # 然后用现有配置覆盖（保留用户自定义）
                    if lang in existing_translations:
                        merged_translations[lang].update(existing_translations[lang])

                # 保存合并后的配置（确保配置文件包含所有最新的键）
                self.save_translations(merged_translations)
                print(f"语言配置已合并并更新: {self.config_path}")
                return merged_translations
            else:
                # 自动生成默认配置
                print(f"语言配置文件不存在，自动生成: {self.config_path}")
                self.save_translations(default_translations)
                return default_translations
        except Exception as e:
            print(f"加载语言配置失败: {e}，使用默认配置")
            return self.get_default_translations()

    def save_translations(self, translations):
        """保存翻译配置"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(translations, f, indent=2, ensure_ascii=False)
            self.translations = translations
            return True
        except Exception as e:
            print(f"保存语言配置失败: {e}")
            return False

    def get(self, key, **kwargs):
        """获取翻译文本"""
        try:
            text = self.translations.get(self.current_lang, {}).get(key, key)
            # 支持格式化
            if kwargs:
                return text.format(**kwargs)
            return text
        except Exception:
            return key

    def switch_language(self):
        """切换语言"""
        self.current_lang = 'en' if self.current_lang == 'zh' else 'zh'
        return self.current_lang


class HotkeyManager:
    """快捷键管理器"""

    def __init__(self, config_path='hotkey_config.json'):
        # 获取应用目录（兼容开发和打包环境）
        script_dir = get_app_dir()
        self.config_path = os.path.join(script_dir, config_path)

        # 确保目录存在
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)

        self.hotkeys = self.load_hotkeys()
        self.active_hotkeys = {}

    def load_hotkeys(self):
        """加载快捷键配置，不存在则自动生成，存在则合并默认配置"""
        try:
            default_hotkeys = self.get_default_hotkeys()

            if os.path.exists(self.config_path):
                # 读取现有配置
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    existing_hotkeys = json.load(f)

                # 合并配置：优先使用现有配置，但会添加默认配置中新增的键
                merged_hotkeys = {}
                # 先复制默认配置（确保所有键都存在）
                merged_hotkeys.update(default_hotkeys)
                # 然后用现有配置覆盖（保留用户自定义）
                merged_hotkeys.update(existing_hotkeys)

                # 保存合并后的配置（确保配置文件包含所有最新的键）
                self.save_hotkeys(merged_hotkeys)
                print(f"快捷键配置已合并并更新: {self.config_path}")
                return merged_hotkeys
            else:
                # 自动生成默认配置
                print(f"快捷键配置文件不存在，自动生成: {self.config_path}")
                self.save_hotkeys(default_hotkeys)
                return default_hotkeys
        except Exception as e:
            print(f"加载快捷键配置失败: {e}，使用默认配置")
            return self.get_default_hotkeys()

    def save_hotkeys(self, hotkeys):
        """保存快捷键配置"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(hotkeys, f, indent=2, ensure_ascii=False)
            self.hotkeys = hotkeys
            return True
        except Exception as e:
            print(f"保存快捷键配置失败: {e}")
            return False

    def get_hotkey(self, action):
        """获取快捷键"""
        return self.hotkeys.get(action, '')

    def set_hotkey(self, action, hotkey):
        """设置快捷键"""
        self.hotkeys[action] = hotkey

    def get_default_hotkeys(self):
        """获取默认快捷键"""
        return {
            "select_region": "ctrl+shift+s",
            "start_stop_recording": "ctrl+shift+r",
            "stop_recording": "ctrl+shift+e",
            "save_result": "ctrl+shift+w",
            "copy_to_clipboard": "ctrl+shift+c",
            "clear_all": "ctrl+shift+d",
            "cancel_operation": "escape",
            "switch_language": "ctrl+shift+l"
        }

    def register_global_hotkey(self, action, callback):
        """注册全局热键"""
        try:
            hotkey = self.get_hotkey(action)
            if hotkey:
                keyboard.add_hotkey(hotkey, callback)
                self.active_hotkeys[action] = hotkey
                return True
        except Exception as e:
            print(f"注册热键失败 {action}: {e}")
        return False

    def unregister_all_hotkeys(self):
        """取消所有热键"""
        keyboard.unhook_all_hotkeys()
        self.active_hotkeys.clear()


class AutoScrollScreenshotTool:
    """自动滚动长截图工具"""

    @staticmethod
    def stitch_simple(images):
        """
        简单拼接算法：直接垂直拼接所有图片
        不需要任何重叠检测，因为每张图片的滚动距离是固定的
        """
        if not images:
            return None

        # 计算总尺寸
        total_width = images[0].width
        total_height = sum(img.height for img in images)

        # 创建空白画布
        result = Image.new('RGB', (total_width, total_height))

        # 拼接所有图片
        y_offset = 0
        for img in images:
            result.paste(img, (0, y_offset))
            y_offset += img.height

        return result

    @staticmethod
    def stitch_grid(images, max_columns=2, gap=10, bg_color=(255, 255, 255)):
        """
        网格拼接算法：将图片按网格布局拼接
        :param images: 图片列表
        :param max_columns: 最大列数（默认2列）
        :param gap: 图片之间的间距（像素）
        :param bg_color: 背景颜色
        :return: 拼接后的图片
        """
        if not images:
            return None

        # 根据图片数量和尺寸计算最佳列数，使拼接结果接近正方形
        num_images = len(images)

        # 获取图片尺寸（假设所有图片尺寸相同）
        img_width = images[0].width
        img_height = images[0].height

        # 智能计算最佳列数：遍历可能的列数，选择使结果最接近正方形的
        def calculate_aspect_ratio(cols):
            """计算使用cols列时的长宽比（接近1.0为最佳）"""
            rows = (num_images + cols - 1) // cols
            total_width = img_width * cols
            total_height = img_height * rows

            # 避免除零
            if total_height == 0:
                return float('inf')

            ratio = total_width / total_height
            # 返回偏离1.0的距离（越小越好）
            return abs(ratio - 1.0)

        # 少量图片固定最少2列
        if num_images <= 2:
            columns = 2
        else:
            # 遍历可能的列数（2到max_columns），选择使长宽比最接近1的
            best_columns = 2
            best_ratio_diff = float('inf')

            for cols in range(2, max_columns + 1):
                ratio_diff = calculate_aspect_ratio(cols)
                if ratio_diff < best_ratio_diff:
                    best_ratio_diff = ratio_diff
                    best_columns = cols

            columns = best_columns

        print(f"[网格拼接] 图片数量: {num_images}, 尺寸: {img_width}x{img_height}")

        # 计算行数
        rows = (num_images + columns - 1) // columns

        print(f"[网格拼接] 图片数量: {num_images}, 尺寸: {img_width}x{img_height}")
        print(f"[网格拼接] 使用 {columns}列 x {rows}行 布局")

        # 计算总尺寸
        total_width = img_width * columns + gap * (columns + 1)
        total_height = img_height * rows + gap * (rows + 1)

        print(f"[网格拼接] 最终尺寸: {total_width}x{total_height}, 长宽比: {total_width/total_height:.2f}")

        # 创建空白画布
        result = Image.new('RGB', (total_width, total_height), bg_color)

        # 填充背景
        result.paste(bg_color, [0, 0, total_width, total_height])

        # 拼接所有图片
        for i, img in enumerate(images):
            row = i // columns
            col = i % columns

            x_offset = gap + col * (img_width + gap)
            y_offset = gap + row * (img_height + gap)

            result.paste(img, (x_offset, y_offset))

        return result

    def __init__(self, root):
        self.root = root
        self.lang_manager = LanguageManager()
        self.hotkey_manager = HotkeyManager()

        # 初始化更新管理器
        self.update_manager = UpdateManager(
            CURRENT_VERSION,
            UPDATE_CHECK_API,
            RELEASES_PAGE_URL
        )

        # 初始化UI
        self.setup_window()

        # 状态变量
        self.screenshots = []
        self.is_recording = False
        self.selection_start = None
        self.selection_rect = None
        self.selection_rect_coords = None
        self.region_height = 0  # 截图区域高度

        # 自动滚动参数
        self.scroll_delay = 0.5  # 滚动后等待时间（秒），让内容加载
        self.auto_scroll_enabled = True  # 是否自动滚动

        # 拼接模式：'vertical'（垂直长图）或 'grid'（网格布局）
        self.stitch_mode = 'vertical'

        # 创建界面
        self.create_widgets()

        # 注册全局热键
        self.register_global_hotkeys()

        # 检查更新（异步）
        if ENABLE_AUTO_UPDATE:
            self.check_for_updates_async()

    def setup_window(self):
        """设置窗口"""
        self.root.title(self.lang_manager.get('app_title'))
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)
        self.root.attributes('-topmost', True)

        # 设置背景颜色
        self.root.configure(bg='#f5f5f5')

        # 配置主题样式
        self.setup_theme()

        # 窗口关闭时清理
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_theme(self):
        """配置主题样式"""
        style = ttk.Style()

        # 使用 clam 主题作为基础
        style.theme_use('clam')

        # 定义颜色方案
        colors = {
            'bg': '#f5f5f5',           # 背景色
            'fg': '#333333',           # 前景色
            'primary': '#4a90e2',      # 主色
            'primary_dark': '#357abd', # 深主色
            'success': '#52c41a',      # 成功色
            'warning': '#faad14',      # 警告色
            'danger': '#ff4d4f',       # 危险色
            'border': '#d9d9d9',       # 边框色
            'header': '#ffffff',       # 标题背景
            'header_fg': '#1890ff',    # 标题文字
        }

        # 配置 Frame 样式
        style.configure('TFrame', background=colors['bg'])

        # 配置 Label 样式
        style.configure('TLabel',
                       background=colors['bg'],
                       foreground=colors['fg'],
                       font=('Microsoft YaHei UI', 10))
        style.configure('Header.TLabel',
                       background=colors['header'],
                       foreground=colors['header_fg'],
                       font=('Microsoft YaHei UI', 24, 'bold'))
        style.configure('Title.TLabel',
                       background=colors['bg'],
                       foreground=colors['primary'],
                       font=('Microsoft YaHei UI', 12, 'bold'))
        style.configure('Info.TLabel',
                       background=colors['bg'],
                       foreground='#666666',
                       font=('Microsoft YaHei UI', 9))

        # 配置 Button 样式
        style.configure('TButton',
                       font=('Microsoft YaHei UI', 10),
                       padding=8,
                       relief='flat')
        style.map('TButton',
                 background=[('active', colors['primary_dark']),
                           ('pressed', colors['primary_dark'])],
                 foreground=[('active', 'white'),
                           ('pressed', 'white')])

        # 配置各功能按钮颜色
        style.configure('Primary.TButton',
                       background=colors['primary'],
                       foreground='white',
                       font=('Microsoft YaHei UI', 10, 'bold'))
        style.configure('Success.TButton',
                       background=colors['success'],
                       foreground='white',
                       font=('Microsoft YaHei UI', 10))
        style.configure('Warning.TButton',
                       background=colors['warning'],
                       foreground='white',
                       font=('Microsoft YaHei UI', 10))
        style.configure('Danger.TButton',
                       background=colors['danger'],
                       foreground='white',
                       font=('Microsoft YaHei UI', 10))

        # 配置 LabelFrame 样式
        style.configure('TLabelframe',
                       background=colors['bg'],
                       borderwidth=2,
                       relief='flat')
        style.configure('TLabelframe.Label',
                       background=colors['bg'],
                       foreground=colors['primary'],
                       font=('Microsoft YaHei UI', 10, 'bold'))

        # 配置 Canvas 样式
        style.configure('TCanvas', background=colors['bg'])

        # 配置 Treeview 样式
        style.configure('Treeview',
                       background='white',
                       foreground=colors['fg'],
                       rowheight=25)
        style.map('Treeview',
                 background=[('selected', colors['primary'])],
                 foreground=[('selected', 'white')])

    def create_widgets(self):
        """创建界面组件"""
        # 创建主容器
        main_container = ttk.Frame(self.root, style='TFrame')
        main_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        # ============ 顶部标题栏 ============
        header_frame = tk.Frame(main_container, bg='#ffffff', padx=20, pady=15)
        header_frame.pack(fill=tk.X, pady=(0, 15))

        # 标题
        title_label = tk.Label(
            header_frame,
            text=self.lang_manager.get('app_title'),
            bg='#ffffff',
            fg='#1890ff',
            font=('Microsoft YaHei UI', 24, 'bold')
        )
        title_label.pack(side=tk.LEFT, padx=5)

        # 右侧按钮容器
        right_buttons = tk.Frame(header_frame, bg='#ffffff')
        right_buttons.pack(side=tk.RIGHT)

        # 语言切换按钮
        lang_btn = ttk.Button(
            right_buttons,
            text=f"🌐 {self.lang_manager.get('btn_language')}",
            command=self.switch_language,
            width=12
        )
        lang_btn.pack(side=tk.LEFT, padx=5)

        # 快捷键设置按钮
        settings_btn = ttk.Button(
            right_buttons,
            text=f"⚙️ {self.lang_manager.get('btn_shortcuts')}",
            command=self.open_shortcut_settings,
            width=12
        )
        settings_btn.pack(side=tk.LEFT, padx=5)

        # ============ 操作说明区域 ============
        info_frame = ttk.LabelFrame(
            main_container,
            text=f"  📋 {self.lang_manager.get('usage_title')}  ",
            padding="15",
            style='TLabelframe'
        )
        info_frame.pack(fill=tk.X, pady=(0, 15))

        instructions = self.lang_manager.get('usage_instructions')
        info_label = ttk.Label(
            info_frame,
            text=instructions,
            style='Info.TLabel',
            justify=tk.LEFT,
            wraplength=1100
        )
        info_label.pack(anchor=tk.W, padx=5)

        # ============ 按钮区域 ============
        button_container = ttk.Frame(main_container, style='TFrame')
        button_container.pack(fill=tk.X, pady=(0, 15))

        # 按钮分组
        main_actions = ttk.Frame(button_container, style='TFrame')
        main_actions.pack(side=tk.LEFT, padx=5)

        # 选择区域按钮
        ttk.Button(
            main_actions,
            text=f"🎯 {self.lang_manager.get('btn_select_region')}",
            command=self.select_region,
            style='Primary.TButton',
            width=18
        ).pack(side=tk.LEFT, padx=5)

        # 开始录制按钮
        self.start_btn = ttk.Button(
            main_actions,
            text=f"🔴 {self.lang_manager.get('btn_start_recording')}",
            command=self.start_recording,
            style='Success.TButton',
            width=18
        )
        self.start_btn.pack(side=tk.LEFT, padx=5)

        # 停止录制按钮
        self.stop_btn = ttk.Button(
            main_actions,
            text=f"⏹️ {self.lang_manager.get('btn_stop_recording')}",
            command=self.stop_recording,
            style='Danger.TButton',
            width=18,
            state='disabled'
        )
        self.stop_btn.pack(side=tk.LEFT, padx=5)

        # 文件操作按钮
        file_actions = ttk.Frame(button_container, style='TFrame')
        file_actions.pack(side=tk.LEFT, padx=20)

        ttk.Button(
            file_actions,
            text=f"💾 {self.lang_manager.get('btn_save')}",
            command=self.save_result,
            width=14
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            file_actions,
            text=f"📋 {self.lang_manager.get('btn_copy')}",
            command=self.copy_to_clipboard,
            width=14
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            file_actions,
            text=f"🗑️ {self.lang_manager.get('btn_clear')}",
            command=self.clear_all,
            style='Warning.TButton',
            width=14
        ).pack(side=tk.LEFT, padx=5)

        # ============ 拼接模式选择区域 ============
        stitch_mode_frame = ttk.LabelFrame(
            main_container,
            text=f"  🧩 {self.lang_manager.get('stitch_mode_title')}  ",
            padding="15",
            style='TLabelframe'
        )
        stitch_mode_frame.pack(fill=tk.X, pady=(0, 15))

        # 拼接模式选项
        mode_container = ttk.Frame(stitch_mode_frame, style='TFrame')
        mode_container.pack(fill=tk.X)

        # 垂直拼接（长图）
        self.stitch_mode_var = tk.StringVar(value='vertical')
        vertical_radio = tk.Radiobutton(
            mode_container,
            text=f"📏 {self.lang_manager.get('stitch_mode_vertical')}",
            variable=self.stitch_mode_var,
            value='vertical',
            bg='#f5f5f5',
            fg='#333333',
            font=('Microsoft YaHei UI', 10),
            selectcolor='#e6f7ff',
            activebackground='#1890ff',
            activeforeground='white',
            indicatoron=0,  # 禁用圆点，使用全选样式
            width=25,
            pady=8,
            cursor='hand2'
        )
        vertical_radio.pack(side=tk.LEFT, padx=10)

        # 网格拼接
        grid_radio = tk.Radiobutton(
            mode_container,
            text=f"📐 {self.lang_manager.get('stitch_mode_grid')}",
            variable=self.stitch_mode_var,
            value='grid',
            bg='#f5f5f5',
            fg='#333333',
            font=('Microsoft YaHei UI', 10),
            selectcolor='#e6f7ff',
            activebackground='#1890ff',
            activeforeground='white',
            indicatoron=0,  # 禁用圆点，使用全选样式
            width=25,
            pady=8,
            cursor='hand2'
        )
        grid_radio.pack(side=tk.LEFT, padx=10)

        # 说明标签
        mode_desc = tk.Label(
            mode_container,
            text=self.lang_manager.get('stitch_mode_desc_vertical'),
            bg='#f5f5f5',
            fg='#666666',
            font=('Microsoft YaHei UI', 9),
            justify=tk.LEFT,
            wraplength=500
        )
        mode_desc.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)

        # 绑定选择事件，更新说明
        def on_stitch_mode_change():
            mode = self.stitch_mode_var.get()
            if mode == 'vertical':
                mode_desc.config(text=self.lang_manager.get('stitch_mode_desc_vertical'))
            else:
                mode_desc.config(text=self.lang_manager.get('stitch_mode_desc_grid'))

        self.stitch_mode_var.trace('w', lambda *args: on_stitch_mode_change())

        # ============ 状态显示区域 ============
        status_container = ttk.LabelFrame(
            main_container,
            text=f"  📊 {self.lang_manager.get('status_title')}  ",
            padding="15",
            style='TLabelframe'
        )
        status_container.pack(fill=tk.X, pady=(0, 15))

        # 状态标签网格
        status_grid = ttk.Frame(status_container, style='TFrame')
        status_grid.pack(fill=tk.X)

        # 状态行1
        row1 = ttk.Frame(status_grid, style='TFrame')
        row1.pack(fill=tk.X, pady=2)

        ttk.Label(
            row1,
            text=f"🔹 {self.lang_manager.get('status_ready')}",
            style='Info.TLabel'
        ).pack(side=tk.LEFT, padx=5)

        self.status_indicator = tk.Label(
            row1,
            text="●",
            fg='gray',
            bg='#f5f5f5',
            font=('Arial', 12)
        )
        self.status_indicator.pack(side=tk.LEFT, padx=5)

        # 状态行2
        row2 = ttk.Frame(status_grid, style='TFrame')
        row2.pack(fill=tk.X, pady=2)

        ttk.Label(
            row2,
            text=f"📍 {self.lang_manager.get('region_label')}",
            style='Info.TLabel'
        ).pack(side=tk.LEFT, padx=5)

        self.region_info = ttk.Label(
            row2,
            text="",
            style='Title.TLabel',
            foreground='#666666'
        )
        self.region_info.pack(side=tk.LEFT, padx=10)

        # 状态行3
        row3 = ttk.Frame(status_grid, style='TFrame')
        row3.pack(fill=tk.X, pady=2)

        ttk.Label(
            row3,
            text=f"📷 {self.lang_manager.get('count_label')}",
            style='Info.TLabel'
        ).pack(side=tk.LEFT, padx=5)

        self.count_info = ttk.Label(
            row3,
            text="0",
            style='Title.TLabel',
            foreground='#4a90e2',
            font=('Microsoft YaHei UI', 12, 'bold'))
        self.count_info.pack(side=tk.LEFT, padx=10)

        # ============ 预览区域 ============
        preview_frame = ttk.LabelFrame(
            main_container,
            text=f"  🖼️ {self.lang_manager.get('preview_title')}  ",
            padding="10",
            style='TLabelframe'
        )
        preview_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # 创建可滚动的画布
        canvas_frame = ttk.Frame(preview_frame, style='TFrame')
        canvas_frame.pack(fill=tk.BOTH, expand=True)

        # 画布
        self.preview_canvas = tk.Canvas(
            canvas_frame,
            bg="#2c2c2c",
            highlightthickness=0
        )

        # 滚动条
        scrollbar_y = ttk.Scrollbar(
            canvas_frame,
            orient=tk.VERTICAL,
            command=self.preview_canvas.yview
        )
        scrollbar_x = ttk.Scrollbar(
            canvas_frame,
            orient=tk.HORIZONTAL,
            command=self.preview_canvas.xview
        )

        self.preview_canvas.configure(
            yscrollcommand=scrollbar_y.set,
            xscrollcommand=scrollbar_x.set
        )

        self.preview_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)

        # 更新状态标签引用
        self.status_label = ttk.Label(status_container, text=self.lang_manager.get('status_ready'))
        self.region_label = ttk.Label(status_container, text=self.lang_manager.get('region_label'))
        self.count_label = ttk.Label(status_container, text=self.lang_manager.get('count_label'))

    def register_global_hotkeys(self):
        """注册全局热键"""
        # 使用线程避免阻塞主界面
        def register_thread():
            self.hotkey_manager.register_global_hotkey('select_region', self.select_region)
            self.hotkey_manager.register_global_hotkey('start_stop_recording', self.toggle_recording)
            self.hotkey_manager.register_global_hotkey('stop_recording', self.stop_recording)
            self.hotkey_manager.register_global_hotkey('save_result', self.save_result)
            self.hotkey_manager.register_global_hotkey('copy_to_clipboard', self.copy_to_clipboard)
            self.hotkey_manager.register_global_hotkey('clear_all', self.clear_all)
            self.hotkey_manager.register_global_hotkey('switch_language', self.switch_language)

        thread = threading.Thread(target=register_thread, daemon=True)
        thread.start()

    def toggle_recording(self):
        """切换录制状态"""
        if self.is_recording:
            self.stop_recording()
        else:
            self.start_recording()

    def switch_language(self):
        """切换语言"""
        lang = self.lang_manager.switch_language()

        # 更新窗口标题
        self.root.title(self.lang_manager.get('app_title'))

        # 重建界面以更新所有文本
        for widget in self.root.winfo_children():
            widget.destroy()
        self.create_widgets()

        messagebox.showinfo(
            "Language / 语言",
            f"Language switched to {lang}\n语言已切换到 {lang}"
        )

    def check_for_updates_async(self):
        """异步检查更新"""
        def check_thread():
            has_update, latest_version, download_url, release_notes = \
                self.update_manager.check_for_updates()

            if has_update:
                # 在主线程显示更新提示
                self.root.after(0, self.show_update_dialog,
                              latest_version, download_url, release_notes)

        thread = threading.Thread(target=check_thread, daemon=True)
        thread.start()

    def show_update_dialog(self, new_version, download_url, release_notes):
        """显示更新提示对话框"""
        update_window = tk.Toplevel(self.root)
        update_window.title(self.lang_manager.get('update_available_title'))
        update_window.geometry("600x500")
        update_window.attributes('-topmost', True)
        update_window.configure(bg='#f5f5f5')
        update_window.resizable(False, False)

        # 居中显示
        update_window.transient(self.root)
        update_window.grab_set()

        main_frame = ttk.Frame(update_window, style='TFrame', padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 标题
        title_label = ttk.Label(
            main_frame,
            text=f"🚀 {self.lang_manager.get('update_available_title')}",
            style='Header.TLabel',
            font=('Microsoft YaHei UI', 20, 'bold')
        )
        title_label.pack(pady=(0, 20))

        # 版本信息
        version_frame = ttk.Frame(main_frame, style='TFrame')
        version_frame.pack(fill=tk.X, pady=(0, 15))

        ttk.Label(
            version_frame,
            text=f"{self.lang_manager.get('current_version')}: {CURRENT_VERSION}",
            style='Info.TLabel',
            font=('Microsoft YaHei UI', 12)
        ).pack(side=tk.LEFT, padx=5)

        ttk.Label(
            version_frame,
            text=f"→",
            style='Title.TLabel',
            font=('Arial', 16, 'bold'),
            foreground='#4CAF50'
        ).pack(side=tk.LEFT, padx=10)

        ttk.Label(
            version_frame,
            text=f"{self.lang_manager.get('new_version')}: {new_version}",
            style='Title.TLabel',
            font=('Microsoft YaHei UI', 14, 'bold'),
            foreground='#4CAF50'
        ).pack(side=tk.LEFT, padx=5)

        # 分隔线
        ttk.Separator(main_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=(0, 15))

        # 更新说明
        ttk.Label(
            main_frame,
            text=self.lang_manager.get('release_notes'),
            style='Title.TLabel',
            font=('Microsoft YaHei UI', 12, 'bold')
        ).pack(anchor=tk.W, pady=(0, 10))

        # 更新说明文本框
        notes_text = tk.Text(
            main_frame,
            height=10,
            wrap=tk.WORD,
            font=('Consolas', 10),
            bg='#f9f9f9',
            fg='#333333',
            padx=10,
            pady=10
        )
        notes_text.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        # 插入更新说明
        if release_notes:
            notes_text.insert(tk.END, release_notes)
        else:
            notes_text.insert(tk.END, self.lang_manager.get('no_release_notes'))

        notes_text.config(state=tk.DISABLED)

        # 按钮区域
        button_frame = ttk.Frame(main_frame, style='TFrame')
        button_frame.pack(fill=tk.X, pady=(15, 0))

        ttk.Button(
            button_frame,
            text=f"⬇️ {self.lang_manager.get('download_now')}",
            style='Success.TButton',
            width=20,
            command=lambda: self.open_download_page(download_url)
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            button_frame,
            text=f"⏭️ {self.lang_manager.get('remind_later')}",
            width=20,
            command=update_window.destroy
        ).pack(side=tk.RIGHT, padx=5)

        ttk.Button(
            button_frame,
            text=f"❌ {self.lang_manager.get('skip_this_version')}",
            width=20,
            command=lambda: self.skip_this_version(new_version, update_window)
        ).pack(side=tk.RIGHT, padx=5)

    def open_download_page(self, url):
        """打开下载页面"""
        import webbrowser
        webbrowser.open(url)

    def skip_this_version(self, version, window):
        """跳过此版本的更新"""
        # 记录跳过的版本到配置文件
        script_dir = os.path.dirname(os.path.abspath(__file__))
        skip_config_path = os.path.join(script_dir, 'skip_version.json')

        try:
            skip_config = {}
            if os.path.exists(skip_config_path):
                with open(skip_config_path, 'r', encoding='utf-8') as f:
                    skip_config = json.load(f)

            skip_config['skip_version'] = version

            with open(skip_config_path, 'w', encoding='utf-8') as f:
                json.dump(skip_config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[警告] 保存跳过版本失败: {e}")

        window.destroy()


    def select_region(self):
        """选择截图区域"""
        self.root.withdraw()

        # 创建全屏选择窗口
        self.selection_window = tk.Toplevel(self.root)
        self.selection_window.attributes('-fullscreen', True)
        self.selection_window.attributes('-alpha', 0.3)
        self.selection_window.attributes('-topmost', True)
        self.selection_window.configure(bg='black')

        # 创建选择框画布
        self.selection_canvas = tk.Canvas(self.selection_window,
                                        highlightthickness=0, bg='black')
        self.selection_canvas.pack(fill=tk.BOTH, expand=True)

        # 绑定鼠标事件
        self.selection_canvas.bind('<ButtonPress-1>', self.on_selection_start)
        self.selection_canvas.bind('<B1-Motion>', self.on_selection_drag)
        self.selection_canvas.bind('<ButtonRelease-1>', self.on_selection_end)
        self.selection_window.bind('<Escape>', self.cancel_selection)

        # 显示提示
        hint_text = self.lang_manager.get('select_region_hint')
        self.selection_canvas.create_text(
            self.selection_window.winfo_screenwidth() // 2,
            self.selection_window.winfo_screenheight() // 2,
            text=hint_text,
            fill='white', font=('Arial', 20)
        )

    def on_selection_start(self, event):
        """开始选择"""
        self.selection_start = (event.x, event.y)
        if self.selection_rect:
            self.selection_canvas.delete(self.selection_rect)

    def on_selection_drag(self, event):
        """拖拽选择"""
        if self.selection_start:
            x, y = self.selection_start
            if self.selection_rect:
                self.selection_canvas.delete(self.selection_rect)

            self.selection_rect = self.selection_canvas.create_rectangle(
                x, y, event.x, event.y,
                outline='red', width=2, fill='white', stipple='gray25'
            )

    def on_selection_end(self, event):
        """完成选择"""
        if self.selection_start:
            x1, y1 = self.selection_start
            x2, y2 = event.x, event.y

            self.selection_rect_coords = (
                min(x1, x2), min(y1, y2),
                max(x1, x2), max(y1, y2)
            )

            coords_str = f"({self.selection_rect_coords[0]}, {self.selection_rect_coords[1]}) - ({self.selection_rect_coords[2]}, {self.selection_rect_coords[3]})"
            self.region_label.config(text=self.lang_manager.get('region_selected', coords=coords_str))

            # 更新新的 region_info 组件
            width = self.selection_rect_coords[2] - self.selection_rect_coords[0]
            height = self.selection_rect_coords[3] - self.selection_rect_coords[1]
            self.region_info.config(
                text=f"位置: ({self.selection_rect_coords[0]}, {self.selection_rect_coords[1]}) | 尺寸: {width}x{height}px",
                foreground='#52c41a'
            )

            # 关闭选择窗口
            self.selection_window.destroy()
            self.root.deiconify()

            self.status_indicator.config(fg='#4a90e2')

    def cancel_selection(self, event=None):
        """取消选择"""
        self.selection_window.destroy()
        self.root.deiconify()
        self.region_info.config(text="", foreground='#666666')
        self.status_indicator.config(fg='gray')

    def start_recording(self):
        """开始录制"""
        if not self.selection_rect_coords:
            messagebox.showwarning("Warning", self.lang_manager.get('msg_warning_select'))
            return

        if self.is_recording:
            return

        self.is_recording = True
        self.screenshots = []

        # 更新UI状态
        self.start_btn.config(state='disabled')
        self.stop_btn.config(state='normal')
        self.status_indicator.config(fg='#52c41a')  # 绿色

        # 立即截取第一张
        self.take_screenshot()

        # 启动自动截图线程
        self.recording_thread = threading.Thread(target=self.auto_screenshot_loop, daemon=True)
        self.recording_thread.start()

    def stop_recording(self):
        """停止录制"""
        if not self.is_recording:
            return

        self.is_recording = False

        # 更新UI状态
        self.start_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
        self.status_indicator.config(fg='#4a90e2')  # 蓝色

        # 拼接所有截图
        if self.screenshots:
            self.stitch_images()

    def auto_screenshot_loop(self):
        """自动截图循环（带自动滚动和到底检测）"""
        screenshot_count = 0
        prev_screenshot = None
        no_change_count = 0  # 连续未变化次数
        max_no_change = 3  # 最大连续未变化次数后停止（增加到3次，减少误判）

        while self.is_recording:
            # 1. 截取当前区域
            current_screenshot = self.take_screenshot()

            if current_screenshot:
                # 记录第一次截图的高度作为区域高度
                if screenshot_count == 0:
                    self.region_height = current_screenshot.height
                    print(f"[记录] 截图区域高度: {self.region_height}px")

                # 检测是否滚动到底（对比前后截图）
                if prev_screenshot is not None and self.auto_scroll_enabled:
                    is_bottom = self.is_scroll_to_bottom(prev_screenshot, current_screenshot)
                    if is_bottom:
                        no_change_count += 1
                        print(f"[检测] 检测到滚动到底 (第{no_change_count}次)")

                        if no_change_count >= max_no_change:
                            print(f"[完成] 检测到页面底部，停止录制")
                            self.root.after(0, self.stop_recording)
                            break
                    else:
                        no_change_count = 0  # 有变化，重置计数

                # 保存截图
                self.screenshots.append(current_screenshot)
                prev_screenshot = current_screenshot
                screenshot_count += 1

                # 更新计数
                self.root.after(0, self.update_count)

                # 2. 如果启用了自动滚动，模拟滚动一个区域高度
                if self.auto_scroll_enabled and self.region_height > 0:
                    try:
                        # 使用鼠标滚轮滚动（向上滚动，正值向下）
                        pyautogui.scroll(-self.region_height)
                        print(f"[滚动] 滚动 {self.region_height}px")

                        # 等待内容加载
                        time.sleep(self.scroll_delay)

                    except Exception as e:
                        print(f"[滚动失败] {e}")
                else:
                    # 不自动滚动，只是定时截图
                    time.sleep(0.2)

            else:
                # 截图失败，等待一下再重试
                time.sleep(0.2)

        print(f"[完成] 共截取 {screenshot_count} 张图片")

    def is_scroll_to_bottom(self, img1, img2, threshold=0.90):
        """
        判断是否滚动到底（对比两张图片是否相似）
        :param img1: 前一张图片
        :param img2: 当前图片
        :param threshold: 相似度阈值（0-1），超过此值认为已经到底（默认90%）
        :return: True 表示已经滚动到底，False 表示还可以继续滚动
        """
        try:
            # 确保图片尺寸相同
            if img1.size != img2.size:
                return False

            # 转换为RGB模式
            if img1.mode != 'RGB':
                img1 = img1.convert('RGB')
            if img2.mode != 'RGB':
                img2 = img2.convert('RGB')

            # 获取像素数据（使用 get_flattened_data 替代已弃用的 getdata）
            data1 = list(img1.get_flattened_data())
            data2 = list(img2.get_flattened_data())

            # 计算相同像素的数量
            same_pixels = sum(1 for p1, p2 in zip(data1, data2) if p1 == p2)

            # 计算相似度
            similarity = same_pixels / len(data1)

            print(f"[相似度] {similarity:.3f} (阈值: {threshold})")

            return similarity >= threshold

        except Exception as e:
            print(f"[对比错误] {e}")
            return False

    def take_screenshot(self):
        """截取指定区域"""
        try:
            # 检查是否已选择区域
            if self.selection_rect_coords is None:
                return None

            x1, y1, x2, y2 = self.selection_rect_coords
            width = x2 - x1
            height = y2 - y1

            if width <= 0 or height <= 0:
                return None

            # 截取指定区域
            screenshot = pyautogui.screenshot(region=(x1, y1, width, height))
            return screenshot

        except Exception as e:
            print(f"截图错误: {e}")
            return None

    def update_count(self):
        """更新截图数量显示"""
        count = len(self.screenshots)
        self.count_label.config(text=self.lang_manager.get('count_value', count=count))
        self.count_info.config(text=str(count))

    def stitch_images(self):
        """拼接所有截图（根据选择的拼接模式）"""
        if not self.screenshots:
            return

        try:
            # 获取选择的拼接模式
            stitch_mode = self.stitch_mode_var.get()
            print(f"[拼接] 开始拼接 {len(self.screenshots)} 张图片... 拼接模式: {stitch_mode}")
            start_time = time.time()

            # 根据拼接模式选择不同的拼接算法
            if stitch_mode == 'grid':
                # 网格拼接
                self.result_image = AutoScrollScreenshotTool.stitch_grid(
                    self.screenshots,
                    max_columns=6,  # 最多6列，使拼接结果更接近方形
                    gap=20,  # 间距20像素
                    bg_color=(255, 255, 255)  # 白色背景
                )
                print(f"[拼接] 网格拼接完成")
            else:
                # 垂直拼接（默认）
                self.result_image = AutoScrollScreenshotTool.stitch_simple(self.screenshots)
                print(f"[拼接] 垂直拼接完成")

            end_time = time.time()
            print(f"[拼接] 总耗时 {(end_time - start_time) * 1000:.1f}ms")
            print(f"[拼接] 最终尺寸: {self.result_image.width}x{self.result_image.height}")

            # 更新预览
            self.update_preview()

            # 显示成功消息
            mode_text = self.lang_manager.get('stitch_mode_vertical') if stitch_mode == 'vertical' else self.lang_manager.get('stitch_mode_grid')
            messagebox.showinfo(
                "Success",
                f"{self.lang_manager.get('msg_success_stitched', count=len(self.screenshots), width=self.result_image.width, height=self.result_image.height)}\n\n拼接模式: {mode_text}"
            )

        except Exception as e:
            print(f"[拼接错误] {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Error", self.lang_manager.get('msg_error_stitch', error=str(e)))

    def update_preview(self):
        """更新预览显示"""
        if not hasattr(self, 'result_image'):
            return

        # 缩放图片以适应预览
        canvas_width = 800
        scale = min(canvas_width / self.result_image.width, 1.0)

        display_width = int(self.result_image.width * scale)
        display_height = int(self.result_image.height * scale)

        # 使用 Resampling.LANCZOS（兼容 Pillow 9.0+）
        try:
            resampling_filter = Image.Resampling.LANCZOS
        except AttributeError:
            # 旧版本 Pillow 使用 Image.LANCZOS
            resampling_filter = Image.LANCZOS

        display_image = self.result_image.resize(
            (display_width, display_height),
            resampling_filter
        )

        self.preview_photo = ImageTk.PhotoImage(display_image)

        # 在画布上显示
        self.preview_canvas.delete("all")
        self.preview_canvas.create_image(
            0, 0,
            anchor=tk.NW,
            image=self.preview_photo
        )

        # 设置滚动区域
        self.preview_canvas.config(
            scrollregion=(0, 0, display_width, display_height)
        )

    def save_result(self):
        """保存结果"""
        if not hasattr(self, 'result_image'):
            messagebox.showwarning("Warning", self.lang_manager.get('msg_warning_no_screenshot'))
            return

        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"long_screenshot_{timestamp}.png"

        # 选择保存路径
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            initialfile=default_filename,
            filetypes=[
                ("PNG Image", "*.png"),
                ("JPEG Image", "*.jpg"),
                ("All Files", "*.*")
            ]
        )

        if file_path:
            try:
                # 根据文件扩展名使用最优保存参数
                file_ext = os.path.splitext(file_path)[1].lower()

                if file_ext == '.png':
                    # PNG: 无损压缩，最高质量
                    self.result_image.save(
                        file_path,
                        format='PNG',
                        compress_level=0,  # 0 = 无压缩（最高质量），9 = 最大压缩
                        optimize=False    # 不优化，保持原始质量
                    )
                elif file_ext in ['.jpg', '.jpeg']:
                    # JPEG: 最高质量
                    self.result_image.save(
                        file_path,
                        format='JPEG',
                        quality=100,        # 1-100，100 = 最高质量
                        subsampling=0,      # 0 = 无子采样（最高质量），2 = 标准子采样
                        optimize=False
                    )
                else:
                    # 其他格式默认使用 PNG
                    self.result_image.save(
                        file_path,
                        format='PNG',
                        compress_level=0,
                        optimize=False
                    )

                messagebox.showinfo(
                    "Success",
                    self.lang_manager.get('msg_success_saved',
                                        path=file_path,
                                        width=self.result_image.width,
                                        height=self.result_image.height,
                                        count=len(self.screenshots))
                )
            except Exception as e:
                messagebox.showerror("Error", self.lang_manager.get('msg_error_save', error=str(e)))

    def copy_to_clipboard(self):
        """复制图片到剪贴板（最高质量）- 确保在主线程执行"""
        # 检查是否有结果图片
        if not hasattr(self, 'result_image'):
            messagebox.showwarning("Warning", self.lang_manager.get('msg_warning_no_copy'))
            return

        # 确保在主线程中执行剪贴板操作
        # 如果从快捷键调用，可能在后台线程，需要调度到主线程
        if threading.current_thread() is threading.main_thread():
            # 已在主线程，直接执行
            self._copy_to_clipboard_impl()
        else:
            # 在后台线程，调度到主线程执行
            self.root.after(0, self._copy_to_clipboard_impl)

    def _copy_to_clipboard_impl(self):
        """复制图片到剪贴板的实际实现（必须在主线程调用）"""
        import platform

        # Windows 平台
        if platform.system() == 'Windows':
            try:
                import win32clipboard
                import win32con

                # 保存为最高质量 PNG 到内存
                png_bytes = io.BytesIO()
                self.result_image.save(
                    png_bytes,
                    format='PNG',
                    compress_level=0,  # 无压缩，最高质量
                    optimize=False
                )
                png_bytes.seek(0)

                # 打开剪贴板（必须在主线程）
                win32clipboard.OpenClipboard()
                try:
                    win32clipboard.EmptyClipboard()

                    # 方法1: 使用 CF_DIBV5（现代应用，支持更多颜色）
                    try:
                        win32clipboard.SetClipboardData(win32con.CF_DIBV5, self.result_image.tobytes())
                        print("[成功] 使用 CF_DIBV5 格式复制图片（最高质量）")
                    except:
                        pass

                    # 方法2: 使用 CF_DIB（兼容旧应用）
                    win32clipboard.SetClipboardData(win32con.CF_DIB, self.result_image.tobytes())
                    print("[成功] 使用 CF_DIB 格式复制图片（兼容）")

                finally:
                    win32clipboard.CloseClipboard()

                png_bytes.close()

                messagebox.showinfo(
                    "Success",
                    f"图片已复制到剪贴板（最高质量）！\n\n尺寸: {self.result_image.width}x{self.result_image.height}px\n格式: PNG 无损 + CF_DIBV5/CF_DIB 双格式\n\n可以直接粘贴到画图、Word、微信等应用中。"
                )
                return

            except ImportError:
                print("[警告] win32clipboard 未安装，尝试使用其他方法...")
            except Exception as e:
                print(f"[错误] 复制图片失败: {e}")
                import traceback
                traceback.print_exc()

        # 备选方案：保存临时文件
        try:
            import tempfile

            # 保存到临时文件（使用最高质量 PNG）
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                temp_path = tmp.name

            # 使用最高质量保存
            self.result_image.save(
                temp_path,
                format='PNG',
                compress_level=0,  # 无压缩
                optimize=False
            )

            # macOS/Linux 处理
            if platform.system() == 'Darwin':
                # macOS
                import subprocess
                subprocess.run(['osascript', '-e',
                    f'set the clipboard to (read file "{temp_path}" as «class PNGf»)'],
                    check=True)
            elif platform.system() == 'Linux':
                # Linux: 使用 xclip
                try:
                    import subprocess
                    with open(temp_path, 'rb') as f:
                        png_data = f.read()
                    subprocess.run(['xclip', '-selection', 'clipboard', '-t', 'image/png'],
                                 input=png_data, check=True)
                except:
                    # 回退方案：复制文件路径
                    pyperclip.copy(f"file://{temp_path}")

            messagebox.showinfo(
                "Success",
                self.lang_manager.get('msg_success_copied')
            )

        except Exception as e:
            messagebox.showerror("Error", self.lang_manager.get('msg_error_copy', error=str(e)))
            import traceback
            traceback.print_exc()

        except Exception as e:
            print(f"[错误] 复制失败: {e}")
            messagebox.showerror("Error", self.lang_manager.get('msg_error_copy', error=str(e)))

    def clear_all(self):
        """清空所有内容"""
        self.screenshots = []
        self.preview_canvas.delete("all")
        if hasattr(self, 'result_image'):
            del self.result_image
        self.count_label.config(text=self.lang_manager.get('count_label'))
        self.count_info.config(text="0")
        self.status_indicator.config(fg='gray')

    def open_shortcut_settings(self):
        """打开快捷键设置窗口"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title(self.lang_manager.get('settings_title'))
        settings_window.geometry("700x650")  # 增加窗口高度
        settings_window.attributes('-topmost', True)
        settings_window.configure(bg='#f5f5f5')

        # 创建设置界面
        main_frame = ttk.Frame(settings_window, style='TFrame', padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 标题
        title_label = ttk.Label(
            main_frame,
            text=f"⚙️ {self.lang_manager.get('settings_title')}",
            style='Header.TLabel',
            font=('Microsoft YaHei UI', 18, 'bold')
        )
        title_label.pack(pady=(0, 15))

        # 快捷键设置（使用 Canvas 和 Scrollbar 实现滚动）
        scroll_frame = ttk.Frame(main_frame, style='TFrame')
        scroll_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        # 创建 Canvas 和滚动条
        canvas = tk.Canvas(scroll_frame, bg='#f5f5f5', highlightthickness=0)
        scrollbar = ttk.Scrollbar(scroll_frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, style='TFrame')

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=660)
        canvas.configure(yscrollcommand=scrollbar.set)

        # 快捷键 LabelFrame
        hotkeys_frame = ttk.LabelFrame(
            scrollable_frame,
            text=f"  🔑 {self.lang_manager.get('hotkeys_config_title')}  ",
            padding="15",
            style='TLabelframe'
        )
        hotkeys_frame.pack(fill=tk.X, pady=5)

        # 快捷键列表
        hotkey_actions = [
            'select_region',
            'start_stop_recording',
            'stop_recording',
            'save_result',
            'copy_to_clipboard',
            'clear_all',
            'switch_language'
        ]

        entries = {}

        # 添加表头
        header_frame = ttk.Frame(hotkeys_frame, style='TFrame')
        header_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(
            header_frame,
            text=self.lang_manager.get('settings_header_action'),
            style='Title.TLabel',
            width=25
        ).pack(side=tk.LEFT, padx=5)

        ttk.Label(
            header_frame,
            text=self.lang_manager.get('settings_header_shortcut'),
            style='Title.TLabel',
            width=25
        ).pack(side=tk.LEFT, padx=5)

        ttk.Label(
            header_frame,
            text=self.lang_manager.get('settings_header_record'),
            style='Title.TLabel',
            width=10
        ).pack(side=tk.LEFT, padx=5)

        # 分隔线
        ttk.Separator(hotkeys_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=5)

        for i, action in enumerate(hotkey_actions):
            row_frame = ttk.Frame(hotkeys_frame, style='TFrame')
            row_frame.pack(fill=tk.X, pady=5)

            label_text = self.lang_manager.get(f'hotkey_{action}')
            ttk.Label(row_frame, text=label_text, style='TLabel', width=25).pack(side=tk.LEFT, padx=5)

            entry = ttk.Entry(row_frame, width=25, font=('Consolas', 10))
            entry.insert(0, self.hotkey_manager.get_hotkey(action))
            entry.pack(side=tk.LEFT, padx=5)
            entries[action] = entry

            # 记录按钮
            record_btn = ttk.Button(
                row_frame,
                text=f"🎤 {self.lang_manager.get('btn_record')}",
                width=12,
                command=lambda a=action, e=entry: self.record_hotkey(a, e)
            )
            record_btn.pack(side=tk.LEFT, padx=5)

        # 打包滚动组件
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 鼠标滚轮支持（解绑函数定义在后面）
        def _on_mousewheel(event):
            try:
                # 检查 canvas 是否仍然有效
                if canvas.winfo_exists():
                    canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            except tk.TclError:
                # 窗口已关闭，忽略错误
                pass

        # 绑定鼠标滚轮事件到当前窗口，而不是全局
        canvas.bind("<MouseWheel>", _on_mousewheel)

        # 窗口关闭时解绑事件
        def unbind_on_close():
            try:
                canvas.unbind("<MouseWheel>", _on_mousewheel)
            except:
                pass
            settings_window.destroy()

        settings_window.protocol("WM_DELETE_WINDOW", unbind_on_close)

        # 按钮区域（固定在底部）
        button_frame = ttk.Frame(main_frame, style='TFrame')
        button_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Button(
            button_frame,
            text=f"💾 {self.lang_manager.get('btn_save_settings')}",
            style='Success.TButton',
            width=15,
            command=lambda: self.save_shortcuts(entries, settings_window)
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            button_frame,
            text=f"🔄 {self.lang_manager.get('btn_reset_settings')}",
            width=15,
            command=lambda: self.reset_shortcuts(entries)
        ).pack(side=tk.LEFT, padx=5)

    def record_hotkey(self, action, entry):
        """录制快捷键"""
        entry.delete(0, tk.END)
        entry.insert(0, self.lang_manager.get('record_press_hint'))
        entry.config(state='readonly')
        
        def on_key_press(event):
            if event.name == 'esc':
                # 取消录制
                entry.config(state='normal')
                entry.delete(0, tk.END)
                entry.insert(0, self.hotkey_manager.get_hotkey(action))
                keyboard.unhook_all()
            else:
                # 保存快捷键
                hotkey_str = event.name
                if event.event_type == keyboard.KEY_DOWN:
                    # 处理组合键
                    modifiers = []
                    if keyboard.is_pressed('ctrl'):
                        modifiers.append('ctrl')
                    if keyboard.is_pressed('alt'):
                        modifiers.append('alt')
                    if keyboard.is_pressed('shift'):
                        modifiers.append('shift')
                    if keyboard.is_pressed('windows'):
                        modifiers.append('windows')
                    
                    if modifiers:
                        hotkey_str = '+'.join(modifiers + [event.name])
                
                entry.config(state='normal')
                entry.delete(0, tk.END)
                entry.insert(0, hotkey_str)
                keyboard.unhook_all()
        
        keyboard.hook(on_key_press)
        
    def save_shortcuts(self, entries, window):
        """保存快捷键设置"""
        new_hotkeys = {}
        for action, entry in entries.items():
            hotkey = entry.get().strip().lower()
            if hotkey:
                new_hotkeys[action] = hotkey
        
        if self.hotkey_manager.save_hotkeys(new_hotkeys):
            messagebox.showinfo("Success", self.lang_manager.get('msg_settings_saved'))
            # 重新注册热键
            self.hotkey_manager.unregister_all_hotkeys()
            self.register_global_hotkeys()
            window.destroy()
        else:
            messagebox.showerror("Error", "Failed to save settings")
            
    def reset_shortcuts(self, entries):
        """重置为默认快捷键"""
        defaults = self.hotkey_manager.get_default_hotkeys()
        for action, entry in entries.items():
            entry.delete(0, tk.END)
            entry.insert(0, defaults.get(action, ''))
            
    def on_closing(self):
        """窗口关闭事件"""
        self.hotkey_manager.unregister_all_hotkeys()
        self.root.destroy()


def main():
    """主函数"""
    root = tk.Tk()
    app = AutoScrollScreenshotTool(root)
    root.mainloop()


if __name__ == "__main__":
    main()
