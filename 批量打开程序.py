import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path
import subprocess
import platform
import sys
from typing import List
import re


class BatchExeOpener:
    def __init__(self, root):
        self.root = root
        self.root.title("批量可执行程序启动工具")
        self.root.geometry("850x650")

        # 设置样式
        self.root.configure(bg='#f0f0f0')

        # 变量
        self.folder_path = tk.StringVar()
        self.file_name_pattern = tk.StringVar()
        self.search_depth = tk.StringVar(value="all")  # all: 所有子文件夹, first: 仅第一层
        self.search_type = tk.StringVar(value="all")
        self.sort_order = tk.StringVar(value="name")

        # 当前系统的默认设置
        self.current_system = platform.system().lower()
        if self.current_system == "windows":
            self.search_type.set("windows")
        elif self.current_system == "darwin":
            self.search_type.set("mac")
        else:
            self.search_type.set("linux")

        self.found_files = []
        self.last_selected_item = None  # 用于Shift多选

        # 支持的扩展名（按系统分类）
        self.executable_extensions = {
            "all": [".exe", ".bat", ".cmd", ".sh", ".app", ".bin", ".msi", ".jar", ".py", ".ps1", ".run", ".command"],
            "windows": [".exe", ".bat", ".cmd", ".msi", ".ps1"],
            "linux": [".sh", ".bin", ".run", ".py"],
            "mac": [".app", ".sh", ".bin", ".command", ".py"]
        }

        # 创建界面
        self.create_widgets()

    def create_widgets(self):
        # 标题
        title_label = tk.Label(
            self.root,
            text="批量可执行程序启动工具",
            font=('微软雅黑', 14, 'bold'),
            bg='#2c3e50',
            fg='white',
            pady=6
        )
        title_label.pack(fill='x', padx=0)

        # 主内容区域
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(fill='both', expand=True, padx=10, pady=8)

        # 左侧控制面板
        control_frame = tk.Frame(main_frame, bg='#ecf0f1', relief='ridge', bd=1)
        control_frame.pack(side='left', fill='y', padx=(0, 8))

        # 使用网格布局使控制面板更紧凑
        row = 0

        # 文件夹选择区域
        folder_label = tk.Label(
            control_frame,
            text="目录设置",
            font=('微软雅黑', 10, 'bold'),
            bg='#ecf0f1',
            anchor='w'
        )
        folder_label.grid(row=row, column=0, columnspan=3, sticky='w', padx=10, pady=(8, 4))
        row += 1

        tk.Label(
            control_frame,
            text="选择目录:",
            font=('微软雅黑', 9),
            bg='#ecf0f1'
        ).grid(row=row, column=0, sticky='w', padx=(10, 5), pady=2)

        folder_entry = tk.Entry(
            control_frame,
            textvariable=self.folder_path,
            font=('微软雅黑', 9),
            relief='groove',
            width=25
        )
        folder_entry.grid(row=row, column=1, sticky='ew', padx=(0, 5), pady=2)

        browse_btn = tk.Button(
            control_frame,
            text="浏览",
            font=('微软雅黑', 9),
            bg='#3498db',
            fg='white',
            relief='flat',
            width=6,
            command=self.browse_folder
        )
        browse_btn.grid(row=row, column=2, padx=(0, 10), pady=2)
        row += 1

        # 文件名搜索区域
        name_label = tk.Label(
            control_frame,
            text="文件名搜索",
            font=('微软雅黑', 10, 'bold'),
            bg='#ecf0f1',
            anchor='w'
        )
        name_label.grid(row=row, column=0, columnspan=3, sticky='w', padx=10, pady=(8, 4))
        row += 1

        tk.Label(
            control_frame,
            text="文件名(*?):",
            font=('微软雅黑', 9),
            bg='#ecf0f1'
        ).grid(row=row, column=0, sticky='w', padx=(10, 5), pady=2)

        name_entry = tk.Entry(
            control_frame,
            textvariable=self.file_name_pattern,
            font=('微软雅黑', 9),
            relief='groove',
            width=25
        )
        name_entry.grid(row=row, column=1, columnspan=2, sticky='ew', padx=(0, 10), pady=2)
        row += 1

        # 快速文件名按钮
        tk.Label(
            control_frame,
            text="快速选择:",
            font=('微软雅黑', 9),
            bg='#ecf0f1'
        ).grid(row=row, column=0, sticky='w', padx=(10, 5), pady=2)

        quick_frame = tk.Frame(control_frame, bg='#ecf0f1')
        quick_frame.grid(row=row, column=1, columnspan=2, sticky='ew', padx=(0, 10), pady=2)

        quick_names = [("所有", "*"), ("EXE", "*.exe"), ("BAT", "*.bat"), ("SH", "*.sh")]
        for i, (text, pattern) in enumerate(quick_names):
            btn = tk.Button(
                quick_frame,
                text=text,
                font=('微软雅黑', 8),
                bg='#7f8c8d',
                fg='white',
                relief='flat',
                width=4,
                command=lambda p=pattern: self.file_name_pattern.set(p)
            )
            btn.pack(side='left', padx=1, fill='x', expand=True)
        row += 1

        # 搜索选项区域
        options_label = tk.Label(
            control_frame,
            text="搜索选项",
            font=('微软雅黑', 10, 'bold'),
            bg='#ecf0f1',
            anchor='w'
        )
        options_label.grid(row=row, column=0, columnspan=3, sticky='w', padx=10, pady=(8, 4))
        row += 1

        # 搜索深度选项（两个单选按钮）
        tk.Label(
            control_frame,
            text="搜索范围:",
            font=('微软雅黑', 9),
            bg='#ecf0f1'
        ).grid(row=row, column=0, sticky='w', padx=(10, 5), pady=2)

        depth_frame = tk.Frame(control_frame, bg='#ecf0f1')
        depth_frame.grid(row=row, column=1, columnspan=2, sticky='ew', padx=(0, 10), pady=2)

        depth_options = [
            ("所有子文件夹", "all"),
            ("仅第一层", "first")
        ]

        for i, (text, value) in enumerate(depth_options):
            rb = tk.Radiobutton(
                depth_frame,
                text=text,
                variable=self.search_depth,
                value=value,
                font=('微软雅黑', 8),
                bg='#ecf0f1',
                selectcolor='#ecf0f1'
            )
            rb.pack(side='left', padx=5)
        row += 1

        # 系统类型选择
        tk.Label(
            control_frame,
            text="系统类型:",
            font=('微软雅黑', 9),
            bg='#ecf0f1'
        ).grid(row=row, column=0, sticky='w', padx=(10, 5), pady=2)

        system_frame = tk.Frame(control_frame, bg='#ecf0f1')
        system_frame.grid(row=row, column=1, columnspan=2, sticky='ew', padx=(0, 10), pady=2)

        system_types = ["all", "windows", "linux", "mac"]
        for i, system_type in enumerate(system_types):
            rb = tk.Radiobutton(
                system_frame,
                text=system_type.capitalize(),
                variable=self.search_type,
                value=system_type,
                font=('微软雅黑', 8),
                bg='#ecf0f1',
                selectcolor='#ecf0f1'
            )
            rb.pack(side='left', padx=2)
        row += 1

        # 排序方式选择
        tk.Label(
            control_frame,
            text="排序方式:",
            font=('微软雅黑', 9),
            bg='#ecf0f1'
        ).grid(row=row, column=0, sticky='w', padx=(10, 5), pady=2)

        sort_frame = tk.Frame(control_frame, bg='#ecf0f1')
        sort_frame.grid(row=row, column=1, columnspan=2, sticky='ew', padx=(0, 10), pady=2)

        sort_options = [("名称", "name"), ("大小", "size"), ("日期", "date")]
        for i, (text, value) in enumerate(sort_options):
            rb = tk.Radiobutton(
                sort_frame,
                text=text,
                variable=self.sort_order,
                value=value,
                font=('微软雅黑', 8),
                bg='#ecf0f1',
                selectcolor='#ecf0f1'
            )
            rb.pack(side='left', padx=6)
        row += 1

        # 操作按钮区域
        buttons_frame = tk.Frame(control_frame, bg='#ecf0f1')
        buttons_frame.grid(row=row, column=0, columnspan=3, sticky='ew', padx=10, pady=(15, 8))

        button_configs = [
            ("🔍 查找", '#2ecc71', self.find_executables),
            ("✓ 勾选", '#3498db', self.select_all),  # 将"全选"改为"勾选"
            ("🚀 启动选中", '#e74c3c', self.open_selected),
            ("🗑️ 清空", '#95a5a6', self.clear_list)
        ]

        for i, (text, color, command) in enumerate(button_configs):
            btn = tk.Button(
                buttons_frame,
                text=text,
                font=('微软雅黑', 10),
                bg=color,
                fg='white',
                relief='flat',
                height=1,
                command=command
            )
            btn.grid(row=0, column=i, padx=2, sticky='ew')
            buttons_frame.columnconfigure(i, weight=1)
        row += 1

        # 启动所有按钮
        launch_all_btn = tk.Button(
            control_frame,
            text="🚀 启动所有程序",
            font=('微软雅黑', 10, 'bold'),
            bg='#e74c3c',
            fg='white',
            relief='flat',
            height=1,
            command=self.open_all_files
        )
        launch_all_btn.grid(row=row, column=0, columnspan=3, sticky='ew', padx=10, pady=(5, 10))
        row += 1

        # 右侧文件列表区域
        list_frame = tk.Frame(main_frame, bg='#f0f0f0')
        list_frame.pack(side='right', fill='both', expand=True)

        # 列表标题和统计
        header_frame = tk.Frame(list_frame, bg='#f0f0f0')
        header_frame.pack(fill='x', pady=(0, 8))

        tk.Label(
            header_frame,
            text="找到的可执行程序:",
            font=('微软雅黑', 11, 'bold'),
            bg='#f0f0f0'
        ).pack(side='left')

        self.count_label = tk.Label(
            header_frame,
            text="(0)",
            font=('微软雅黑', 9),
            bg='#f0f0f0',
            fg='#7f8c8d'
        )
        self.count_label.pack(side='left', padx=8)

        # 反选按钮
        invert_btn = tk.Button(
            header_frame,
            text="反选",
            font=('微软雅黑', 9),
            bg='#9b59b6',
            fg='white',
            relief='flat',
            height=1,
            command=self.invert_selection
        )
        invert_btn.pack(side='right', padx=2)

        # 列表容器
        list_container = tk.Frame(list_frame, bg='white', relief='sunken', bd=1)
        list_container.pack(fill='both', expand=True)

        # 创建Treeview
        columns = ('#', '✓', '文件名', '类型', '大小', '日期', '路径')
        self.tree = ttk.Treeview(list_container, columns=columns, show='headings', height=22)

        # 设置列
        self.tree.heading('#', text='#', command=lambda: self.sort_by_column('#'))
        self.tree.heading('✓', text='✓')
        self.tree.heading('文件名', text='文件名', command=lambda: self.sort_by_column('文件名'))
        self.tree.heading('类型', text='类型')
        self.tree.heading('大小', text='大小', command=lambda: self.sort_by_column('大小'))
        self.tree.heading('日期', text='日期', command=lambda: self.sort_by_column('日期'))
        self.tree.heading('路径', text='路径')

        self.tree.column('#', width=35, anchor='center', minwidth=35)
        self.tree.column('✓', width=30, anchor='center', minwidth=30)
        self.tree.column('文件名', width=140, minwidth=100)
        self.tree.column('类型', width=70, minwidth=50)
        self.tree.column('大小', width=70, minwidth=50)
        self.tree.column('日期', width=110, minwidth=80)
        self.tree.column('路径', width=220, minwidth=150)

        # 创建复选框事件绑定
        self.tree.tag_bind('checked', '<Button-1>', self.on_checkbox_click)
        self.tree.tag_bind('unchecked', '<Button-1>', self.on_checkbox_click)

        # 添加Shift多选事件绑定
        self.tree.bind('<Shift-Button-1>', self.on_shift_click)

        # 滚动条
        scrollbar_y = ttk.Scrollbar(list_container, orient='vertical', command=self.tree.yview)
        scrollbar_x = ttk.Scrollbar(list_container, orient='horizontal', command=self.tree.xview)
        self.tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

        # 网格布局
        self.tree.grid(row=0, column=0, sticky='nsew')
        scrollbar_y.grid(row=0, column=1, sticky='ns')
        scrollbar_x.grid(row=1, column=0, sticky='ew')

        list_container.grid_rowconfigure(0, weight=1)
        list_container.grid_columnconfigure(0, weight=1)

        # 绑定事件
        self.tree.bind('<Double-1>', self.on_item_double_click)

        # 状态栏
        self.status_bar = tk.Label(
            self.root,
            text="就绪 | 当前系统: {} | 选中: 0".format(self.current_system.capitalize()),
            font=('微软雅黑', 8),
            bg='#34495e',
            fg='white',
            relief='sunken',
            anchor='w',
            padx=8,
            pady=3
        )
        self.status_bar.pack(side='bottom', fill='x', padx=0)

    def browse_folder(self):
        """浏览选择文件夹"""
        folder_selected = filedialog.askdirectory(title="选择目录")
        if folder_selected:
            self.folder_path.set(folder_selected)
            self.update_status(f"已选择目录: {os.path.basename(folder_selected)}...")

    def pattern_match(self, filename: str, pattern: str) -> bool:
        """检查文件名是否匹配模式（支持通配符*和?）"""
        if not pattern or pattern == "*":
            return True

        pattern = pattern.strip()
        if not pattern:
            return True

        patterns = [p.strip() for p in pattern.split(';') if p.strip()]

        for pat in patterns:
            regex_pat = re.escape(pat)
            regex_pat = regex_pat.replace(r'\*', '.*').replace(r'\?', '.')

            if not regex_pat.startswith('.*'):
                regex_pat = '^' + regex_pat
            if not regex_pat.endswith('.*'):
                regex_pat = regex_pat + '$'

            try:
                if re.match(regex_pat, filename, re.IGNORECASE):
                    return True
            except re.error:
                if pat == "*" or pat in filename:
                    return True

        return False

    def get_executable_extensions(self):
        """获取当前选择的扩展名列表"""
        return self.executable_extensions[self.search_type.get()]

    def is_executable_file(self, file_path):
        """检查文件是否为可执行程序"""
        ext = file_path.suffix.lower()
        if ext in self.get_executable_extensions():
            return True

        if platform.system() != "Windows" and os.access(file_path, os.X_OK):
            return True

        return False

    def get_file_info(self, file_path: Path):
        """获取文件的详细信息"""
        try:
            stat = file_path.stat()
            size = stat.st_size

            if size < 1024:
                size_str = f"{size}B"
            elif size < 1024 * 1024:
                size_str = f"{size / 1024:.0f}K"
            elif size < 1024 * 1024 * 1024:
                size_str = f"{size / (1024 * 1024):.1f}M"
            else:
                size_str = f"{size / (1024 * 1024 * 1024):.1f}G"

            from datetime import datetime
            date_str = datetime.fromtimestamp(stat.st_mtime).strftime("%m-%d %H:%M")

            ext = file_path.suffix.lower()
            file_type = {
                '.exe': 'EXE', '.bat': 'BAT', '.cmd': 'CMD', '.sh': 'SH',
                '.app': 'APP', '.bin': 'BIN', '.msi': 'MSI', '.jar': 'JAR',
                '.py': 'PY', '.ps1': 'PS1', '.run': 'RUN', '.command': 'CMD'
            }.get(ext, ext.upper() if ext else '?')

            return size_str, date_str, file_type

        except Exception:
            return "?", "?", "?"

    def find_executables(self):
        """查找可执行程序"""
        folder_path = self.folder_path.get()
        name_pattern = self.file_name_pattern.get()

        if not folder_path:
            messagebox.showwarning("警告", "请先选择目录！")
            return

        if not os.path.exists(folder_path):
            messagebox.showerror("错误", "目录不存在！")
            return

        self.clear_list()
        self.found_files = []
        self.last_selected_item = None

        try:
            folder_path = Path(folder_path)
            self.update_status("搜索中...")

            # 根据搜索深度选择搜索模式
            if self.search_depth.get() == "all":
                search_pattern = "**/*"  # 所有子文件夹
            else:
                search_pattern = "*"  # 仅当前目录

            all_files = []
            for file_path in folder_path.glob(search_pattern):
                if file_path.is_file():
                    # 如果是仅第一层子文件夹，检查深度
                    if self.search_depth.get() == "first":
                        # 计算相对路径的深度
                        relative_path = file_path.relative_to(folder_path)
                        if len(relative_path.parts) > 1:
                            # 跳过深度大于1的文件
                            continue
                    all_files.append(file_path)

            executables = []
            for file_path in all_files:
                if self.is_executable_file(file_path):
                    if self.pattern_match(file_path.name, name_pattern):
                        executables.append(file_path)

            # 排序
            sort_by = self.sort_order.get()
            if sort_by == "name":
                executables.sort(key=lambda x: x.name.lower())
            elif sort_by == "size":
                executables.sort(key=lambda x: x.stat().st_size)
            elif sort_by == "date":
                executables.sort(key=lambda x: x.stat().st_mtime, reverse=True)

            # 显示文件
            for i, file_path in enumerate(executables, 1):
                self.found_files.append(file_path)

                size_str, date_str, file_type = self.get_file_info(file_path)
                relative_path = file_path.relative_to(folder_path)

                item_id = self.tree.insert('', 'end', values=(
                    i,
                    "□",
                    file_path.name,
                    file_type,
                    size_str,
                    date_str,
                    str(relative_path)
                ))
                self.tree.item(item_id, tags=('unchecked',))

            self.update_selection_count()
            self.count_label.config(text=f"({len(self.found_files)})")

            if self.found_files:
                self.update_status(f"找到 {len(self.found_files)} 个程序")
            else:
                self.update_status("未找到程序")

        except Exception as e:
            messagebox.showerror("错误", f"搜索出错:\n{str(e)}")
            self.update_status("搜索出错")

    def sort_by_column(self, column):
        """按列排序"""
        if not self.found_files:
            return

        selected_items = self.get_checked_items()

        if column == '#':
            self.sort_files_by_order()
        elif column == '文件名':
            self.found_files.sort(key=lambda x: x.name.lower())
            self.sort_files_by_order()
        elif column == '大小':
            self.found_files.sort(key=lambda x: x.stat().st_size)
            self.sort_files_by_order()
        elif column == '日期':
            self.found_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            self.sort_files_by_order()

        self.restore_selection(selected_items)

    def sort_files_by_order(self):
        """按当前顺序显示文件"""
        self.tree.delete(*self.tree.get_children())
        for i, file_path in enumerate(self.found_files, 1):
            size_str, date_str, file_type = self.get_file_info(file_path)
            relative_path = file_path.relative_to(Path(self.folder_path.get()))

            item_id = self.tree.insert('', 'end', values=(
                i,
                "□",
                file_path.name,
                file_type,
                size_str,
                date_str,
                str(relative_path)
            ))
            self.tree.item(item_id, tags=('unchecked',))

    def on_checkbox_click(self, event):
        """处理复选框点击（普通点击）"""
        row_id = self.tree.identify_row(event.y)
        column = self.tree.identify_column(event.x)

        if row_id and column == '#2':  # 第二列是复选框列
            self.toggle_checkbox(row_id)
            self.last_selected_item = row_id

    def on_shift_click(self, event):
        """处理Shift+点击（多选）"""
        row_id = self.tree.identify_row(event.y)
        column = self.tree.identify_column(event.x)

        if row_id and column == '#2':
            if self.last_selected_item:
                # 获取所有项目ID
                all_items = list(self.tree.get_children())

                # 获取开始和结束位置
                start_idx = all_items.index(self.last_selected_item)
                end_idx = all_items.index(row_id)

                # 确保start_idx <= end_idx
                if start_idx > end_idx:
                    start_idx, end_idx = end_idx, start_idx

                # 选中范围内的所有项目
                for i in range(start_idx, end_idx + 1):
                    item_id = all_items[i]
                    values = list(self.tree.item(item_id, 'values'))
                    values[1] = "✓"
                    self.tree.item(item_id, values=values)
                    self.tree.item(item_id, tags=('checked',))

                # 更新最后一个选中的项目
                self.last_selected_item = row_id
            else:
                # 如果没有上一次选中的项目，只选中当前项目
                self.toggle_checkbox(row_id)
                self.last_selected_item = row_id

            self.update_selection_count()

    def toggle_checkbox(self, item_id):
        """切换复选框状态"""
        current_value = self.tree.item(item_id, 'values')[1]
        if current_value == "□":
            new_value = "✓"
            self.tree.item(item_id, tags=('checked',))
        else:
            new_value = "□"
            self.tree.item(item_id, tags=('unchecked',))

        values = list(self.tree.item(item_id, 'values'))
        values[1] = new_value
        self.tree.item(item_id, values=values)
        self.update_selection_count()

    def get_checked_items(self) -> List[int]:
        """获取当前选中的项目索引"""
        checked_items = []
        for item_id in self.tree.get_children():
            values = self.tree.item(item_id, 'values')
            if values[1] == "✓":
                index = int(values[0]) - 1
                checked_items.append(index)
        return checked_items

    def restore_selection(self, selected_indices: List[int]):
        """恢复选中状态"""
        for item_id in self.tree.get_children():
            values = list(self.tree.item(item_id, 'values'))
            index = int(values[0]) - 1

            if index in selected_indices:
                values[1] = "✓"
                self.tree.item(item_id, tags=('checked',))
            else:
                values[1] = "□"
                self.tree.item(item_id, tags=('unchecked',))

            self.tree.item(item_id, values=values)

        self.update_selection_count()

    def update_selection_count(self):
        """更新选中计数"""
        checked_count = 0
        for item_id in self.tree.get_children():
            values = self.tree.item(item_id, 'values')
            if values[1] == "✓":
                checked_count += 1

        status_parts = self.status_bar.cget("text").split("|")
        if len(status_parts) >= 3:
            status_parts[2] = f" 选中: {checked_count}"
            self.status_bar.config(text="|".join(status_parts))

    def select_all(self):
        """勾选所有项目（全选）"""
        for item_id in self.tree.get_children():
            values = list(self.tree.item(item_id, 'values'))
            values[1] = "✓"
            self.tree.item(item_id, values=values)
            self.tree.item(item_id, tags=('checked',))
            self.tree.item(item_id,
                           )

        self.update_selection_count()

    def invert_selection(self):
        """反选"""
        for item_id in self.tree.get_children():
            values = list(self.tree.item(item_id, 'values'))
            if values[1] == "✓":
                values[1] = "□"
                self.tree.item(item_id, tags=('unchecked',))
            else:
                values[1] = "✓"
                self.tree.item(item_id, tags=('checked',))
            self.tree.item(item_id, values=values)

        self.update_selection_count()

    def open_all_files(self):
        """打开所有找到的程序"""
        if not self.found_files:
            messagebox.showinfo("提示", "没有要运行的程序，请先查找程序")
            return

        confirm = messagebox.askyesno("确认", f"确定要运行 {len(self.found_files)} 个程序吗？\n注意：请确保程序安全！")

        if not confirm:
            return

        self.run_executables(self.found_files)

    def open_selected(self):
        """打开选中的程序"""
        selected_indices = self.get_checked_items()

        if not selected_indices:
            messagebox.showinfo("提示", "请先选择一个或多个程序")
            return

        selected_files = [self.found_files[i] for i in selected_indices]

        confirm = messagebox.askyesno("确认", f"确定要运行选中的 {len(selected_files)} 个程序吗？")

        if confirm:
            self.run_executables(selected_files)

    def on_item_double_click(self, event):
        """双击运行程序"""
        item = self.tree.identify_row(event.y)
        if item:
            index = int(self.tree.item(item, 'values')[0]) - 1
            if 0 <= index < len(self.found_files):
                file_path = self.found_files[index]
                confirm = messagebox.askyesno("确认", f"确定要运行程序吗？\n\n{file_path.name}")
                if confirm:
                    self.run_executable(file_path)

    def run_executables(self, file_list):
        """批量运行可执行程序"""
        success_count = 0
        failed_files = []

        progress_window = tk.Toplevel(self.root)
        progress_window.title("正在运行程序")
        progress_window.geometry("350x120")
        progress_window.transient(self.root)
        progress_window.grab_set()

        tk.Label(progress_window, text="正在批量运行程序...", font=('微软雅黑', 11)).pack(pady=8)

        progress_var = tk.DoubleVar()
        progress_bar = ttk.Progressbar(progress_window, variable=progress_var, maximum=len(file_list))
        progress_bar.pack(fill='x', padx=15, pady=5)

        status_label = tk.Label(progress_window, text="准备开始...", font=('微软雅黑', 9))
        status_label.pack()

        progress_window.update()

        for i, file_path in enumerate(file_list, 1):
            try:
                status_label.config(text=f"正在运行: {file_path.name[:20]}...")
                progress_var.set(i)
                progress_window.update()

                self.run_executable(file_path)
                success_count += 1

                self.root.after(100)

            except Exception as e:
                failed_files.append((file_path.name, str(e)))

        progress_window.destroy()

        result_message = f"成功启动 {success_count}/{len(file_list)} 个程序"

        if failed_files:
            result_message += "\n\n以下程序启动失败:"
            for file_name, error in failed_files[:5]:
                result_message += f"\n  • {file_name}: {error}"
            if len(failed_files) > 5:
                result_message += f"\n  还有{len(failed_files) - 5}个..."

        messagebox.showinfo("运行结果", result_message)
        self.update_status(f"成功启动 {success_count}/{len(file_list)} 个程序")

    def run_executable(self, file_path):
        """运行单个可执行程序"""
        try:
            file_path = Path(file_path)

            if file_path.suffix.lower() == '.jar':
                subprocess.Popen(['java', '-jar', str(file_path)],
                                 shell=True,
                                 creationflags=subprocess.CREATE_NEW_CONSOLE if platform.system() == "Windows" else 0)
            elif file_path.suffix.lower() == '.py':
                subprocess.Popen([sys.executable, str(file_path)],
                                 shell=True,
                                 creationflags=subprocess.CREATE_NEW_CONSOLE if platform.system() == "Windows" else 0)
            elif file_path.suffix.lower() == '.sh' and platform.system() != "Windows":
                subprocess.Popen(['bash', str(file_path)], shell=False)
            elif file_path.suffix.lower() == '.ps1' and platform.system() == "Windows":
                subprocess.Popen(['powershell', '-File', str(file_path)],
                                 shell=True,
                                 creationflags=subprocess.CREATE_NEW_CONSOLE)
            else:
                if platform.system() == "Windows":
                    os.startfile(str(file_path))
                else:
                    subprocess.Popen([str(file_path)], shell=False)

            return True

        except Exception as e:
            raise Exception(f"运行失败: {str(e)}")

    def clear_list(self):
        """清空文件列表"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.found_files = []
        self.last_selected_item = None
        self.count_label.config(text="(0)")
        self.update_status("已清空列表")
        self.update_selection_count()

    def update_status(self, message):
        """更新状态栏"""
        system_info = f"当前系统: {self.current_system.capitalize()}"
        selected_info = self.status_bar.cget("text").split("|")[-1] if "选中:" in self.status_bar.cget(
            "text") else " 选中: 0"
        self.status_bar.config(text=f"状态: {message} | {system_info} |{selected_info}")
        self.root.update()


def main():
    root = tk.Tk()
    app = BatchExeOpener(root)

    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')

    root.mainloop()


if __name__ == "__main__":
    main()