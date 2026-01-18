import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import subprocess
import platform
from pathlib import Path
from typing import List


class FileHelper:
    """文件号直登小帮手 - 批量复制和打开文件工具"""

    def __init__(self, root):
        self.root = root
        self.root.title("文件号直登小帮手 v2.0")
        self.root.geometry("1200x850")
        # 设置窗口最小尺寸
        self.root.minsize(1000, 700)

        # 设置窗口图标（如果有的话）
        try:
            # 可以设置自定义图标
            pass
        except:
            pass

        # 语言设置
        self.current_lang = "zh"  # zh: 中文, en: 英文

        # 双语文本字典
        self.i18n = {
            "zh": {
                "window_title": "文件号直登小帮手 v2.0",
                "title": "📁 文件号直登小帮手",
                "source_file": "📄 选择要复制的文件",
                "select_file": "🔍 浏览文件",
                "target_folder": "📂 选择目标文件夹",
                "select_folder": "🔍 浏览文件夹",
                "options": "⚙️ 选项设置",
                "open_after_copy": "✓ 复制后自动打开文件",
                "overwrite": "✓ 覆盖已存在的文件",
                "start_copy": "🚀 开始复制到所有子文件夹",
                "operation_log": "📋 操作日志",
                "find_settings": "🔎 查找设置",
                "find_filename": "要查找的文件名:",
                "find_file": "🔍 查找文件",
                "find_results": "📊 查找结果",
                "filename": "文件名",
                "path": "路径",
                "found_files": "找到 {count} 个文件",
                "open_all": "📖 打开所有找到的文件",
                "clear_list": "🗑️ 清空列表",
                "ready": "✨ 就绪",
                "error": "❌ 错误",
                "warning": "⚠️ 警告",
                "confirm": "📌 确认",
                "complete": "✅ 完成",
                "switch_lang": "🌐 English",
                "select_source_title": "选择要复制的文件",
                "select_target_title": "选择目标文件夹",
                "all_files": "所有文件",
                "selected_source": "✓ 已选择源文件: {name}",
                "source_file": "源文件: {name}",
                "selected_target": "✓ 已选择目标文件夹: {path}",
                "target_folder": "目标文件夹: {path}",
                "no_source": "请先选择要复制的文件！",
                "no_target": "请先选择目标文件夹！",
                "target_not_exist": "目标文件夹不存在！",
                "no_subfolders": "目标文件夹中没有第一层子文件夹！",
                "no_subfolders_log": "⚠ 目标文件夹中没有子文件夹",
                "confirm_copy": "确认将文件复制到 {count} 个第一层子文件夹吗？",
                "start_copying": "📋 开始复制文件到 {count} 个子文件夹...",
                "skip_existing": "⏭  [{i}/{total}] 跳过（已存在）: {name}",
                "copy_success": "✓  [{i}/{total}] 复制成功: {name}",
                "copy_failed": "✗  [{i}/{total}] 复制失败 {name}: {error}",
                "copy_complete": "✅ 复制完成！\n\n成功: {success} 个\n跳过: {skip} 个\n失败: {fail} 个",
                "copy_complete_msg": "复制完成",
                "copy_complete_status": "复制完成 - 成功: {success}, 跳过: {skip}, 失败: {fail}",
                "open_failed": "✗ 打开文件失败 {path}: {error}",
                "no_target_find": "请先选择目标文件夹！",
                "enter_filename": "请输入要查找的文件名！",
                "start_finding": "🔍 开始查找文件...",
                "no_subfolders_find": "目标文件夹中没有第一层子文件夹！",
                "no_subfolders_find_log": "⚠ 没有子文件夹可查找",
                "found": "✓ 找到: {name}",
                "not_found": "未在 {count} 个子文件夹中找到 {name}",
                "not_found_log": "⚠ 未找到文件",
                "found_status": "找到 {count} 个文件",
                "found_msg": "查找结果",
                "found_count_msg": "找到 {count} 个 {name}",
                "no_files_found": "没有找到任何文件！",
                "confirm_open": "确定要打开 {count} 个文件吗？",
                "start_opening": "📖 开始打开文件...",
                "opened": "✓ [{i}/{total}] 已打开: {name}",
                "open_failed_log": "✗ [{i}/{total}] 打开失败: {error}",
                "open_complete": "打开完成！成功: {success} 个，失败: {fail} 个",
                "open_complete_status": "打开完成 - 成功: {success}, 失败: {fail}",
                "read_failed": "✗ 读取文件夹失败: {error}",
                "cleared": "🗑️ 已清空查找结果",
                "cleared_status": "已清空"
            },
            "en": {
                "window_title": "File Helper v2.0",
                "title": "📁 File Helper",
                "source_file": "📄 Select File to Copy",
                "select_file": "🔍 Browse File",
                "target_folder": "📂 Select Target Folder",
                "select_folder": "🔍 Browse Folder",
                "options": "⚙️ Options",
                "open_after_copy": "✓ Auto-open after copy",
                "overwrite": "✓ Overwrite existing files",
                "start_copy": "🚀 Copy to all subfolders",
                "operation_log": "📋 Operation Log",
                "find_settings": "🔎 Find Settings",
                "find_filename": "Filename to find:",
                "find_file": "🔍 Find File",
                "find_results": "📊 Search Results",
                "filename": "Filename",
                "path": "Path",
                "found_files": "Found {count} files",
                "open_all": "📖 Open All Found Files",
                "clear_list": "🗑️ Clear List",
                "ready": "✨ Ready",
                "error": "❌ Error",
                "warning": "⚠️ Warning",
                "confirm": "📌 Confirm",
                "complete": "✅ Complete",
                "switch_lang": "🌐 中文",
                "select_source_title": "Select file to copy",
                "select_target_title": "Select target folder",
                "all_files": "All Files",
                "selected_source": "✓ Selected source file: {name}",
                "source_file": "Source file: {name}",
                "selected_target": "✓ Selected target folder: {path}",
                "target_folder": "Target folder: {path}",
                "no_source": "Please select a file to copy first!",
                "no_target": "Please select a target folder first!",
                "target_not_exist": "Target folder does not exist!",
                "no_subfolders": "No first-level subfolders in target folder!",
                "no_subfolders_log": "⚠ No subfolders",
                "confirm_copy": "Confirm to copy file to {count} first-level subfolders?",
                "start_copying": "📋 Starting copy to {count} subfolders...",
                "skip_existing": "⏭  [{i}/{total}] Skip (exists): {name}",
                "copy_success": "✓  [{i}/{total}] Copy success: {name}",
                "copy_failed": "✗  [{i}/{total}] Copy failed {name}: {error}",
                "copy_complete": "✅ Copy Complete!\n\nSuccess: {success}\nSkipped: {skip}\nFailed: {fail}",
                "copy_complete_msg": "Copy Complete",
                "copy_complete_status": "Copy Complete - Success: {success}, Skipped: {skip}, Failed: {fail}",
                "open_failed": "✗ Failed to open {path}: {error}",
                "no_target_find": "Please select a target folder first!",
                "enter_filename": "Please enter a filename to find!",
                "start_finding": "🔍 Starting file search...",
                "no_subfolders_find": "No first-level subfolders in target folder!",
                "no_subfolders_find_log": "⚠ No subfolders to search",
                "found": "✓ Found: {name}",
                "not_found": "Not found in {count} subfolders: {name}",
                "not_found_log": "⚠ File not found",
                "found_status": "Found {count} files",
                "found_msg": "Search Results",
                "found_count_msg": "Found {count} {name}",
                "no_files_found": "No files found!",
                "confirm_open": "Confirm to open {count} files?",
                "start_opening": "📖 Opening files...",
                "opened": "✓ [{i}/{total}] Opened: {name}",
                "open_failed_log": "✗ [{i}/{total}] Open failed: {error}",
                "open_complete": "Open Complete! Success: {success}, Failed: {fail}",
                "open_complete_status": "Open Complete - Success: {success}, Failed: {fail}",
                "read_failed": "✗ Failed to read folder: {error}",
                "cleared": "🗑️ Results cleared",
                "cleared_status": "Cleared"
            }
        }

        # 当前系统
        self.current_system = platform.system().lower()

        # 跨平台字体配置
        self.font_family = self.get_system_font()

        # 设置样式
        self.setup_styles()

        # 创建UI元素
        self.create_widgets()

        # 存储选择的文件路径和目标文件夹路径
        self.source_file_path = ""
        self.target_folder_path = ""
        self.found_files = []

    def get_system_font(self):
        """获取系统字体，支持跨平台"""
        system = platform.system()
        if system == "Windows":
            return "微软雅黑"
        elif system == "Darwin":  # macOS
            return "PingFang SC"  # 苹方（简体中文）
        else:  # Linux
            return "DejaVu Sans"  # Linux常见字体

    def get_text(self, key, **kwargs):
        """获取当前语言的文本"""
        text = self.i18n[self.current_lang].get(key, key)
        if kwargs:
            return text.format(**kwargs)
        return text

    def switch_language(self):
        """切换语言"""
        self.current_lang = "en" if self.current_lang == "zh" else "zh"
        self.update_all_texts()

    def update_all_texts(self):
        """更新所有界面文本"""
        # 更新窗口标题
        self.root.title(self.get_text("window_title"))
        self.title_label.config(text=self.get_text("title"))
        self.lang_btn.config(text=self.get_text("switch_lang"))

        # 更新左侧控件
        self.source_frame_label.config(text=self.get_text("source_file"))
        self.source_btn.config(text=self.get_text("select_file"))
        self.target_frame_label.config(text=self.get_text("target_folder"))
        self.target_btn.config(text=self.get_text("select_folder"))
        self.options_frame_label.config(text=self.get_text("options"))
        self.open_check.config(text=self.get_text("open_after_copy"))
        self.overwrite_check.config(text=self.get_text("overwrite"))
        self.copy_btn.config(text=self.get_text("start_copy"))
        self.log_frame_label.config(text=self.get_text("operation_log"))

        # 更新右侧控件
        self.find_frame_label.config(text=self.get_text("find_settings"))
        self.find_filename_label.config(text=self.get_text("find_filename"))
        self.find_btn.config(text=self.get_text("find_file"))
        self.result_frame_label.config(text=self.get_text("find_results"))
        self.result_tree.heading("文件名", text=self.get_text("filename"))
        self.result_tree.heading("路径", text=self.get_text("path"))
        self.open_all_btn.config(text=self.get_text("open_all"))
        self.clear_btn.config(text=self.get_text("clear_list"))

        # 更新状态栏
        self.update_status(self.get_text("ready"))

    def setup_styles(self):
        """设置控件样式"""
        style = ttk.Style()
        style.theme_use('clam')

        # 配色方案 - 现代化配色
        colors = {
            'primary': '#4F46E5',        # 主色调 - 靛蓝色
            'primary_hover': '#4338CA',   # 主色调悬停
            'success': '#10B981',         # 成功 - 翠绿色
            'success_hover': '#059669',   # 成功悬停
            'info': '#3B82F6',            # 信息 - 蓝色
            'info_hover': '#2563EB',      # 信息悬停
            'warning': '#F59E0B',         # 警告 - 琥珀色
            'dark': '#1E293B',            # 深色
            'dark_lighter': '#334155',    # 深色较浅
            'light': '#F8FAFC',           # 浅色
            'light_darker': '#E2E8F0',    # 浅色较深
            'text': '#1E293B',            # 文字颜色
            'text_light': '#64748B',      # 文字浅色
        }

        # ===== 标题样式 =====
        style.configure("Title.TLabel",
                       font=(self.font_family, 14, "bold"),
                       background=colors['dark'],
                       foreground="white",
                       padding=6)

        # ===== 按钮样式 =====
        # 主按钮（蓝色）
        style.configure("Primary.TButton",
                       font=(self.font_family, 9, "bold"),
                       foreground="white",
                       background=colors['info'],
                       borderwidth=0,
                       focuscolor='none',
                       padding=6)
        style.map("Primary.TButton",
                 background=[('active', colors['info_hover']),
                           ('pressed', colors['info_hover'])])

        # 成功按钮（绿色）
        style.configure("Success.TButton",
                       font=(self.font_family, 9, "bold"),
                       foreground="white",
                       background=colors['success'],
                       borderwidth=0,
                       focuscolor='none',
                       padding=6)
        style.map("Success.TButton",
                 background=[('active', colors['success_hover']),
                           ('pressed', colors['success_hover'])])

        # 语言切换按钮（紫色）
        style.configure("Lang.TButton",
                       font=(self.font_family, 8, "bold"),
                       foreground="white",
                       background="#8B5CF6",
                       borderwidth=0,
                       focuscolor='none',
                       padding=5)
        style.map("Lang.TButton",
                 background=[('active', '#7C3AED'),
                           ('pressed', '#7C3AED')])

        # 清空按钮（灰色）
        style.configure("Clear.TButton",
                       font=(self.font_family, 8),
                       foreground=colors['text_light'],
                       background=colors['light_darker'],
                       borderwidth=0,
                       focuscolor='none',
                       padding=5)
        style.map("Clear.TButton",
                 background=[('active', '#CBD5E1'),
                           ('pressed', '#CBD5E1')])

        # ===== LabelFrame 样式 - 圆角卡片效果 =====
        style.configure("Card.TLabelframe",
                       background=colors['light'],
                       borderwidth=0,
                       relief="flat")

        style.configure("Card.TLabelframe.Label",
                       font=(self.font_family, 9, "bold"),
                       background=colors['light'],
                       foreground=colors['text'],
                       padding=(8, 3))

        # ===== Treeview 样式 =====
        style.configure("Treeview",
                       font=(self.font_family, 8),
                       background="white",
                       foreground=colors['text'],
                       rowheight=26,
                       fieldbackground="white",
                       borderwidth=0)
        style.map("Treeview",
                 background=[('selected', colors['info'])],
                 foreground=[('selected', 'white')])

        style.configure("Treeview.Heading",
                       font=(self.font_family, 9, "bold"),
                       background=colors['light_darker'],
                       foreground=colors['text'],
                       borderwidth=0,
                       relief="flat")
        style.map("Treeview.Heading",
                 background=[('active', colors['primary'])])

        # ===== Checkbox 样式 =====
        style.configure("Custom.TCheckbutton",
                       font=(self.font_family, 8),
                       background=colors['light'],
                       foreground=colors['text'],
                       padding=4)

        # ===== Entry 样式 =====
        style.configure("Custom.TEntry",
                       font=(self.font_family, 8),
                       fieldbackground="white",
                       borderwidth=1,
                       relief="solid",
                       padding=5)

    def create_widgets(self):
        """创建所有界面控件"""

        # ===== 顶部装饰栏 =====
        header_frame = tk.Frame(self.root, bg=self.get_gradient_color('#4F46E5', '#7C3AED'), height=60)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)

        # 标题和语言切换
        header_content = tk.Frame(header_frame, bg=self.get_gradient_color('#4F46E5', '#7C3AED'))
        header_content.pack(fill="both", expand=True, padx=15, pady=10)

        # 左侧：标题
        self.title_label = ttk.Label(header_content, text=self.get_text("title"), style="Title.TLabel")
        self.title_label.pack(side="left", expand=True)

        # 右侧：语言切换按钮
        self.lang_btn = ttk.Button(header_content, text=self.get_text("switch_lang"),
                                   command=self.switch_language, style="Lang.TButton")
        self.lang_btn.pack(side="right", padx=6)

        # ===== 主内容区域 - 渐变背景 =====
        main_bg = tk.Frame(self.root, bg="#F1F5F9")
        main_bg.pack(fill="both", expand=True)

        main_frame = tk.Frame(main_bg, bg="#F1F5F9")
        main_frame.pack(fill="both", expand=True, padx=12, pady=12)

        # 左侧：操作区域 - 自适应宽度
        left_frame = tk.Frame(main_frame, bg="#F1F5F9")
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 6))

        # 右侧：查找区域 - 自适应宽度
        right_frame = tk.Frame(main_frame, bg="#F1F5F9")
        right_frame.pack(side="right", fill="both", expand=True, padx=(6, 0))

        # ===== 左侧：卡片式布局 =====
        # 源文件选择卡片
        source_card = self.create_card(left_frame, self.get_text("source_file"))
        source_card['card'].pack(fill="x", pady=(0, 8))
        self.source_frame = source_card['inner']
        self.source_frame_label = source_card['card']

        self.source_path_var = tk.StringVar()
        source_entry = ttk.Entry(self.source_frame, textvariable=self.source_path_var, style="Custom.TEntry")
        source_entry.pack(fill="x", pady=(5, 5))

        self.source_btn = ttk.Button(self.source_frame, text=self.get_text("select_file"),
                                   command=self.select_source_file, style="Primary.TButton")
        self.source_btn.pack(fill="x", pady=(0, 5))

        # 目标文件夹选择卡片
        target_card = self.create_card(left_frame, self.get_text("target_folder"))
        target_card['card'].pack(fill="x", pady=8)
        self.target_frame = target_card['inner']
        self.target_frame_label = target_card['card']

        self.target_path_var = tk.StringVar()
        target_entry = ttk.Entry(self.target_frame, textvariable=self.target_path_var, style="Custom.TEntry")
        target_entry.pack(fill="x", pady=(5, 5))

        self.target_btn = ttk.Button(self.target_frame, text=self.get_text("select_folder"),
                                    command=self.select_target_folder, style="Primary.TButton")
        self.target_btn.pack(fill="x", pady=(0, 5))

        # 选项卡片
        options_card = self.create_card(left_frame, self.get_text("options"))
        options_card['card'].pack(fill="x", pady=8)
        self.options_frame = options_card['inner']
        self.options_frame_label = options_card['card']

        self.open_after_copy_var = tk.BooleanVar(value=True)
        self.open_check = ttk.Checkbutton(self.options_frame, text=self.get_text("open_after_copy"),
                                         variable=self.open_after_copy_var, style="Custom.TCheckbutton")
        self.open_check.pack(anchor="w", pady=4)

        self.overwrite_var = tk.BooleanVar(value=False)
        self.overwrite_check = ttk.Checkbutton(self.options_frame, text=self.get_text("overwrite"),
                                              variable=self.overwrite_var, style="Custom.TCheckbutton")
        self.overwrite_check.pack(anchor="w", pady=(0, 4))

        # 开始复制按钮卡片
        action_card = self.create_card(left_frame, "")
        action_card['card'].pack(fill="x", pady=8)
        action_frame = action_card['inner']

        self.copy_btn = ttk.Button(action_frame, text=self.get_text("start_copy"),
                                 command=self.start_copying, style="Success.TButton")
        self.copy_btn.pack(fill="x", pady=5)

        # 日志输出卡片 - 自动占据剩余空间
        log_card = self.create_card(left_frame, self.get_text("operation_log"))
        log_card['card'].pack(fill="both", expand=True, pady=(8, 0))
        self.log_frame = log_card['inner']
        self.log_frame_label = log_card['card']

        log_scrollbar = ttk.Scrollbar(self.log_frame)
        log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.log_text = tk.Text(self.log_frame, yscrollcommand=log_scrollbar.set,
                               wrap=tk.WORD, font=("Consolas", 8),
                               bg="#1E293B", fg="#10B981", insertbackground="white",
                               relief="flat", padx=8, pady=8)
        self.log_text.pack(fill="both", expand=True)
        log_scrollbar.config(command=self.log_text.yview)

        # ===== 右侧：查找和打开 =====
        # 查找设置卡片
        find_card = self.create_card(right_frame, self.get_text("find_settings"))
        find_card['card'].pack(fill="x", pady=(0, 8))
        self.find_frame = find_card['inner']
        self.find_frame_label = find_card['card']

        self.find_filename_label = tk.Label(self.find_frame, text=self.get_text("find_filename"),
                                            font=(self.font_family, 8, "bold"), bg="#F8FAFC", fg="#64748B")
        self.find_filename_label.pack(anchor="w", pady=(5, 4))
        self.find_filename_var = tk.StringVar()
        find_entry = ttk.Entry(self.find_frame, textvariable=self.find_filename_var, style="Custom.TEntry")
        find_entry.pack(fill="x", pady=(0, 5))

        self.find_btn = ttk.Button(self.find_frame, text=self.get_text("find_file"),
                                  command=self.find_files, style="Primary.TButton")
        self.find_btn.pack(fill="x", pady=(0, 5))

        # 查找结果卡片 - 自动占据剩余空间，包含表格和按钮
        result_card = self.create_card(right_frame, self.get_text("find_results"))
        result_card['card'].pack(fill="both", expand=True, pady=8)
        self.result_frame = result_card['inner']
        self.result_frame_label = result_card['card']

        # Treeview表格容器 - 使用expand占据主要空间
        result_container = tk.Frame(self.result_frame, bg="white")
        result_container.pack(fill="both", expand=True, pady=(5, 8), padx=5)

        result_scrollbar = ttk.Scrollbar(result_container)
        result_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        columns = ("文件名", "路径")
        self.result_tree = ttk.Treeview(result_container, columns=columns, show="headings",
                                       yscrollcommand=result_scrollbar.set, style="Treeview")

        self.result_tree.heading("文件名", text=self.get_text("filename"))
        self.result_tree.heading("路径", text=self.get_text("path"))

        # 列宽使用比例分配，文件名35%，路径65%
        self.result_tree.column("文件名", width=0, minwidth=150, stretch=True)
        self.result_tree.column("路径", width=0, minwidth=200, stretch=True)

        self.result_tree.pack(fill="both", expand=True)
        result_scrollbar.config(command=self.result_tree.yview)

        # 结果统计
        self.result_count_label = tk.Label(self.result_frame, text=self.get_text("found_files", count=0),
                                           font=(self.font_family, 8, "bold"), bg="#F8FAFC", fg="#4F46E5")
        self.result_count_label.pack(fill="x", pady=(0, 5))

        # 打开按钮区域 - 始终可见
        self.open_all_btn = ttk.Button(self.result_frame, text=self.get_text("open_all"),
                                     command=self.open_all_found_files, style="Success.TButton")
        self.open_all_btn.pack(fill="x", pady=5)

        # 清空按钮
        self.clear_btn = ttk.Button(self.result_frame, text=self.get_text("clear_list"),
                                   command=self.clear_results, style="Clear.TButton")
        self.clear_btn.pack(fill="x", pady=(3, 0))

        # ===== 底部状态栏 - 现代化设计 =====
        status_bar = tk.Frame(self.root, bg="#1E293B", height=26)
        status_bar.pack(fill="x")
        status_bar.pack_propagate(False)

        status_content = tk.Frame(status_bar, bg="#1E293B")
        status_content.pack(fill="both", expand=True, padx=12, pady=4)

        # 状态图标
        status_icon_font = "Segoe UI Emoji" if self.current_system == "windows" else "Apple Color Emoji" if self.current_system == "darwin" else "DejaVu Sans"
        status_icon = tk.Label(status_content, text="ℹ", font=(status_icon_font, 10),
                              bg="#1E293B", fg="#3B82F6")
        status_icon.pack(side="left", padx=(0, 6))

        self.status_label = tk.Label(status_content, text=self.get_text("ready"),
                                    bg="#1E293B", fg="#94A3B8",
                                    font=(self.font_family, 8), anchor="w")
        self.status_label.pack(side="left", expand=True, fill="x")

        # 分隔线
        separator = tk.Frame(status_content, width=1, bg="#334155")
        separator.pack(side="right", padx=10, fill="y")

        # 系统信息
        system_info = tk.Label(status_content, text=f"{platform.system()}",
                              bg="#1E293B", fg="#64748B",
                              font=(self.font_family, 7))
        system_info.pack(side="right", padx=(0, 3))

    def create_card(self, parent, title):
        """创建卡片式容器，返回包含 LabelFrame 和内部 Frame 的字典"""
        card = ttk.LabelFrame(parent, text=title, style="Card.TLabelframe", padding=0)
        inner = tk.Frame(card, bg="#F8FAFC")
        inner.pack(fill="both", expand=True, padx=10, pady=8)
        return {'card': card, 'inner': inner}

    def get_gradient_color(self, start_color, end_color):
        """获取渐变颜色（简化版）"""
        return start_color  # tkinter不支持真正的渐变，这里返回起始色

    def select_source_file(self):
        """选择源文件"""
        file_path = filedialog.askopenfilename(
            title=self.get_text("select_source_title"),
            filetypes=[(self.get_text("all_files"), "*.*")]
        )

        if file_path:
            # 确保使用绝对路径
            file_path = os.path.abspath(file_path)
            self.source_file_path = file_path
            self.source_path_var.set(file_path)
            file_name = os.path.basename(file_path)

            # 自动填充查找文件名
            self.find_filename_var.set(file_name)

            self.log_message(self.get_text("selected_source", name=file_name))
            self.update_status(self.get_text("source_file", name=file_name))

    def select_target_folder(self):
        """选择目标文件夹"""
        folder_path = filedialog.askdirectory(title=self.get_text("select_target_title"))

        if folder_path:
            # 确保使用绝对路径
            folder_path = os.path.abspath(folder_path)
            self.target_folder_path = folder_path
            self.target_path_var.set(folder_path)
            self.log_message(self.get_text("selected_target", path=folder_path))
            self.update_status(self.get_text("target_folder", path=folder_path))

    def get_first_level_subfolders(self, folder_path):
        """获取第一层子文件夹列表"""
        subfolders = []
        try:
            for item in os.listdir(folder_path):
                item_path = os.path.join(folder_path, item)
                if os.path.isdir(item_path):
                    subfolders.append(item_path)
        except Exception as e:
            self.log_message(self.get_text("read_failed", error=str(e)))

        return subfolders

    def start_copying(self):
        """开始复制文件到所有子文件夹"""
        if not self.source_file_path:
            messagebox.showerror(self.get_text("error"), self.get_text("no_source"))
            return

        if not self.target_folder_path:
            messagebox.showerror(self.get_text("error"), self.get_text("no_target"))
            return

        if not os.path.exists(self.target_folder_path):
            messagebox.showerror(self.get_text("error"), self.get_text("target_not_exist"))
            return

        # 获取所有第一层子文件夹
        subfolders = self.get_first_level_subfolders(self.target_folder_path)

        if not subfolders:
            messagebox.showwarning(self.get_text("warning"), self.get_text("no_subfolders"))
            self.log_message(self.get_text("no_subfolders_log"))
            return

        # 确认操作
        confirm_msg = self.get_text("confirm_copy", count=len(subfolders))
        if not messagebox.askyesno(self.get_text("confirm"), confirm_msg):
            return

        # 开始复制
        self.copy_btn.config(state="disabled")
        self.log_message("=" * 60)
        self.log_message(self.get_text("start_copying", count=len(subfolders)))
        self.log_message("=" * 60)

        success_count = 0
        fail_count = 0
        skip_count = 0

        file_name = os.path.basename(self.source_file_path)

        for i, folder in enumerate(subfolders, 1):
            try:
                # 构建目标路径
                dest_path = os.path.join(folder, file_name)

                # 检查文件是否已存在
                if os.path.exists(dest_path) and not self.overwrite_var.get():
                    self.log_message(self.get_text("skip_existing", i=i, total=len(subfolders),
                                                   name=os.path.basename(folder)))
                    skip_count += 1
                    continue

                # 复制文件
                shutil.copy2(self.source_file_path, dest_path)
                success_count += 1
                self.log_message(self.get_text("copy_success", i=i, total=len(subfolders),
                                              name=os.path.basename(folder)))

                # 如果需要，打开文件
                if self.open_after_copy_var.get():
                    self.open_file(dest_path)

            except Exception as e:
                fail_count += 1
                self.log_message(self.get_text("copy_failed", i=i, total=len(subfolders),
                                              name=os.path.basename(folder), error=str(e)))

        # 显示结果
        self.log_message("=" * 60)
        result_msg = self.get_text("copy_complete", success=success_count, skip=skip_count, fail=fail_count)
        self.log_message(result_msg.replace("\n", " | "))
        messagebox.showinfo(self.get_text("copy_complete_msg"), result_msg)
        self.log_message("=" * 60)

        self.copy_btn.config(state="normal")
        self.update_status(self.get_text("copy_complete_status", success=success_count,
                                       skip=skip_count, fail=fail_count))

    def open_file(self, file_path):
        """使用系统默认程序打开文件"""
        try:
            # 规范化路径，确保使用正确的路径分隔符
            file_path = os.path.normpath(file_path)

            # 检查文件是否存在
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")

            system = platform.system()
            if system == "Windows":
                os.startfile(file_path)
            elif system == "Darwin":  # macOS
                # 使用 Popen 并传递列表参数，避免路径中的空格和特殊字符问题
                # 使用 start_new_session=True 确保在 macOS 上正确打开
                subprocess.Popen(["open", file_path],
                               stdout=subprocess.DEVNULL,
                               stderr=subprocess.DEVNULL,
                               start_new_session=True)
            else:  # Linux
                # 使用 Popen 并传递列表参数，避免路径中的空格和特殊字符问题
                subprocess.Popen(["xdg-open", file_path],
                               stdout=subprocess.DEVNULL,
                               stderr=subprocess.DEVNULL,
                               start_new_session=True)
        except FileNotFoundError as e:
            self.log_message(f"✗ 文件不存在: {file_path}")
        except Exception as e:
            self.log_message(self.get_text("open_failed", path=file_path, error=str(e)))

    def find_files(self):
        """查找目标文件夹下所有第一层子文件夹中的指定文件"""
        if not self.target_folder_path:
            messagebox.showerror(self.get_text("error"), self.get_text("no_target_find"))
            return

        file_name = self.find_filename_var.get().strip()
        if not file_name:
            messagebox.showerror(self.get_text("error"), self.get_text("enter_filename"))
            return

        self.clear_results()
        self.log_message(self.get_text("start_finding"))

        # 获取所有第一层子文件夹
        subfolders = self.get_first_level_subfolders(self.target_folder_path)

        if not subfolders:
            messagebox.showwarning(self.get_text("warning"), self.get_text("no_subfolders_find"))
            self.log_message(self.get_text("no_subfolders_find_log"))
            return

        # 在子文件夹中查找文件
        found_count = 0
        self.found_files = []

        for folder in subfolders:
            # 确保使用绝对路径
            target_path = os.path.join(folder, file_name)
            target_path = os.path.abspath(target_path)
            if os.path.exists(target_path):
                self.found_files.append(target_path)
                self.result_tree.insert("", "end", values=(file_name, folder))
                found_count += 1
                self.log_message(self.get_text("found", name=f"{os.path.basename(folder)}/{file_name}"))

        self.result_count_label.config(text=self.get_text("found_files", count=found_count))

        if found_count == 0:
            messagebox.showinfo(self.get_text("found_msg"),
                              self.get_text("not_found", count=len(subfolders), name=file_name))
            self.log_message(self.get_text("not_found_log"))
        else:
            self.update_status(self.get_text("found_status", count=found_count))
            messagebox.showinfo(self.get_text("found_msg"),
                              self.get_text("found_count_msg", count=found_count, name=file_name))

    def open_all_found_files(self):
        """打开所有查找到的文件"""
        if not self.found_files:
            messagebox.showwarning(self.get_text("warning"), self.get_text("no_files_found"))
            return

        confirm_msg = self.get_text("confirm_open", count=len(self.found_files))
        if not messagebox.askyesno(self.get_text("confirm"), confirm_msg):
            return

        self.log_message(self.get_text("start_opening"))
        success_count = 0
        fail_count = 0

        for i, file_path in enumerate(self.found_files, 1):
            try:
                self.open_file(file_path)
                success_count += 1
                self.log_message(self.get_text("opened", i=i, total=len(self.found_files),
                                              name=os.path.basename(file_path)))
            except Exception as e:
                fail_count += 1
                self.log_message(self.get_text("open_failed_log", i=i, total=len(self.found_files),
                                              error=str(e)))

        result_msg = self.get_text("open_complete", success=success_count, fail=fail_count)
        messagebox.showinfo(self.get_text("complete"), result_msg)
        self.update_status(self.get_text("open_complete_status", success=success_count, fail=fail_count))

    def clear_results(self):
        """清空查找结果"""
        for item in self.result_tree.get_children():
            self.result_tree.delete(item)
        self.found_files = []
        self.result_count_label.config(text=self.get_text("found_files", count=0))
        self.log_message(self.get_text("cleared"))
        self.update_status(self.get_text("cleared_status"))

    def log_message(self, message):
        """添加消息到日志"""
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.root.update()

    def update_status(self, message):
        """更新状态栏"""
        self.status_label.config(text=message)
        self.root.update()


def main():
    root = tk.Tk()
    app = FileHelper(root)

    # 居中显示窗口
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')

    root.mainloop()


if __name__ == "__main__":
    main()
