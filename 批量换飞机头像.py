import sys
import asyncio
import os
import json
import time
from datetime import datetime
from pathlib import Path

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

# Telegram相关库
from telethon import TelegramClient, errors
from telethon.sessions import StringSession
import psutil


class TelegramAvatarChanger(QMainWindow):
    def __init__(self):
        super().__init__()
        self.client = None
        self.is_authenticated = False
        self.avatars_queue = []
        self.current_avatar_index = 0
        self.change_interval = 5  # 默认5秒
        self.is_changing = False
        self.config_file = "telegram_avatar_changer.json"
        self.load_config()
        self.init_ui()

    def load_config(self):
        """加载配置"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.last_session = config.get('last_session', '')
                    self.last_api_id = config.get('last_api_id', '')
                    self.last_api_hash = config.get('last_api_hash', '')
            except:
                self.last_session = ''
                self.last_api_id = ''
                self.last_api_hash = ''
        else:
            self.last_session = ''
            self.last_api_id = ''
            self.last_api_hash = ''

    def save_config(self):
        """保存配置"""
        config = {
            'last_session': self.last_session,
            'last_api_id': self.last_api_id,
            'last_api_hash': self.last_api_hash
        }
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        except:
            pass

    def init_ui(self):
        self.setWindowTitle("Telegram 批量头像更换工具 (使用现有会话)")
        self.setGeometry(100, 100, 800, 600)

        # 创建中心窗口部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # 连接状态区域
        status_group = QGroupBox("连接状态")
        status_layout = QVBoxLayout()

        self.status_label = QLabel("状态: 未连接")
        self.status_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        status_layout.addWidget(self.status_label)

        self.user_info_label = QLabel("用户: 未登录")
        status_layout.addWidget(self.user_info_label)

        # 自动检测按钮
        auto_detect_btn = QPushButton("🎯 自动检测Telegram会话")
        auto_detect_btn.clicked.connect(self.auto_detect_session)
        auto_detect_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 10px;
                font-size: 14px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        status_layout.addWidget(auto_detect_btn)

        status_group.setLayout(status_layout)
        layout.addWidget(status_group)

        # API凭证区域（可选）
        api_group = QGroupBox("API凭证 (备用方式)")
        api_layout = QGridLayout()

        api_layout.addWidget(QLabel("API ID:"), 0, 0)
        self.api_id_input = QLineEdit()
        self.api_id_input.setText(self.last_api_id)
        api_layout.addWidget(self.api_id_input, 0, 1)

        api_layout.addWidget(QLabel("API Hash:"), 1, 0)
        self.api_hash_input = QLineEdit()
        self.api_hash_input.setText(self.last_api_hash)
        self.api_hash_input.setEchoMode(QLineEdit.Password)
        api_layout.addWidget(self.api_hash_input, 1, 1)

        # 手动连接按钮
        manual_connect_btn = QPushButton("手动连接")
        manual_connect_btn.clicked.connect(self.manual_connect)
        api_layout.addWidget(manual_connect_btn, 2, 0, 1, 2)

        api_group.setLayout(api_layout)
        layout.addWidget(api_group)

        # 头像文件区域
        avatar_group = QGroupBox("头像文件管理")
        avatar_layout = QVBoxLayout()

        # 文件列表
        self.file_list = QListWidget()
        self.file_list.setSelectionMode(QListWidget.ExtendedSelection)
        self.file_list.setDragDropMode(QListWidget.InternalMove)
        avatar_layout.addWidget(QLabel("选择的头像文件:"))
        avatar_layout.addWidget(self.file_list)

        # 文件操作按钮
        file_buttons_layout = QHBoxLayout()

        self.add_files_btn = QPushButton("📁 添加图片文件")
        self.add_files_btn.clicked.connect(self.add_avatar_files)
        self.add_files_btn.setStyleSheet("padding: 5px;")
        file_buttons_layout.addWidget(self.add_files_btn)

        self.add_folder_btn = QPushButton("📂 添加文件夹")
        self.add_folder_btn.clicked.connect(self.add_avatar_folder)
        self.add_folder_btn.setStyleSheet("padding: 5px;")
        file_buttons_layout.addWidget(self.add_folder_btn)

        self.clear_files_btn = QPushButton("🗑️ 清空列表")
        self.clear_files_btn.clicked.connect(self.clear_avatar_files)
        self.clear_files_btn.setStyleSheet("padding: 5px;")
        file_buttons_layout.addWidget(self.clear_files_btn)

        avatar_layout.addLayout(file_buttons_layout)
        avatar_group.setLayout(avatar_layout)
        layout.addWidget(avatar_group)

        # 预览区域
        preview_group = QGroupBox("头像预览")
        preview_layout = QHBoxLayout()

        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setMinimumSize(200, 200)
        self.preview_label.setStyleSheet("""
            QLabel {
                border: 2px solid #ddd;
                border-radius: 10px;
                background-color: #f5f5f5;
            }
        """)
        preview_layout.addWidget(self.preview_label)

        preview_info_layout = QVBoxLayout()
        self.preview_info = QLabel("未选择图片")
        self.preview_info.setWordWrap(True)
        preview_info_layout.addWidget(self.preview_info)

        # 预览控制按钮
        preview_btns_layout = QHBoxLayout()
        self.prev_preview_btn = QPushButton("◀ 上一个")
        self.prev_preview_btn.clicked.connect(self.show_previous_preview)
        preview_btns_layout.addWidget(self.prev_preview_btn)

        self.next_preview_btn = QPushButton("下一个 ▶")
        self.next_preview_btn.clicked.connect(self.show_next_preview)
        preview_btns_layout.addWidget(self.next_preview_btn)

        preview_info_layout.addLayout(preview_btns_layout)
        preview_info_layout.addStretch()
        preview_layout.addLayout(preview_info_layout)

        preview_group.setLayout(preview_layout)
        layout.addWidget(preview_group)

        # 设置区域
        settings_group = QGroupBox("更换设置")
        settings_layout = QGridLayout()

        settings_layout.addWidget(QLabel("更换间隔(秒):"), 0, 0)
        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(1, 3600)
        self.interval_spin.setValue(5)
        settings_layout.addWidget(self.interval_spin, 0, 1)

        settings_layout.addWidget(QLabel("循环模式:"), 1, 0)
        self.loop_checkbox = QCheckBox("完成后重新开始")
        self.loop_checkbox.setChecked(True)
        settings_layout.addWidget(self.loop_checkbox, 1, 1)

        settings_layout.addWidget(QLabel("随机顺序:"), 2, 0)
        self.random_checkbox = QCheckBox("随机选择头像")
        settings_layout.addWidget(self.random_checkbox, 2, 1)

        settings_group.setLayout(settings_layout)
        layout.addWidget(settings_group)

        # 控制区域
        control_group = QGroupBox("操作控制")
        control_layout = QHBoxLayout()

        self.start_btn = QPushButton("▶ 开始更换")
        self.start_btn.clicked.connect(self.start_changing)
        self.start_btn.setEnabled(False)
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                padding: 10px;
                font-size: 14px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        control_layout.addWidget(self.start_btn)

        self.pause_btn = QPushButton("⏸️ 暂停")
        self.pause_btn.clicked.connect(self.pause_changing)
        self.pause_btn.setEnabled(False)
        control_layout.addWidget(self.pause_btn)

        self.stop_btn = QPushButton("⏹️ 停止")
        self.stop_btn.clicked.connect(self.stop_changing)
        self.stop_btn.setEnabled(False)
        control_layout.addWidget(self.stop_btn)

        # 单次更换按钮
        self.single_change_btn = QPushButton("🔄 更换当前头像")
        self.single_change_btn.clicked.connect(self.single_change)
        self.single_change_btn.setEnabled(False)
        control_layout.addWidget(self.single_change_btn)

        control_group.setLayout(control_layout)
        layout.addWidget(control_group)

        # 日志区域
        log_group = QGroupBox("操作日志")
        log_layout = QVBoxLayout()

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(150)
        self.log_text.setStyleSheet("""
            QTextEdit {
                background-color: #f8f8f8;
                font-family: Consolas, monospace;
                font-size: 11px;
            }
        """)
        log_layout.addWidget(self.log_text)

        log_group.setLayout(log_layout)
        layout.addWidget(log_group)

        # 进度区域
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #ccc;
                border-radius: 3px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 3px;
            }
        """)
        layout.addWidget(self.progress_bar)

        # 连接文件列表的选择事件
        self.file_list.itemSelectionChanged.connect(self.update_preview)
        self.file_list.currentRowChanged.connect(self.update_preview)

        # 初始化
        self.log_message("等待连接...")

        # 尝试自动连接
        if self.last_session and self.last_api_id and self.last_api_hash:
            QTimer.singleShot(1000, self.try_auto_connect)

    def try_auto_connect(self):
        """尝试自动连接"""
        self.log_message("正在尝试自动连接...")
        asyncio.create_task(self.connect_with_session(
            self.last_session,
            self.last_api_id,
            self.last_api_hash
        ))

    def find_telegram_process(self):
        """查找运行的Telegram进程"""
        telegram_processes = []
        for proc in psutil.process_iter(['name', 'exe']):
            try:
                name = proc.info['name'].lower()
                if 'telegram' in name:
                    telegram_processes.append(proc)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        return telegram_processes

    def auto_detect_session(self):
        """自动检测Telegram会话"""
        self.log_message("正在检测Telegram进程...")

        # 查找Telegram进程
        processes = self.find_telegram_process()
        if not processes:
            self.log_message("未找到运行的Telegram进程")
            QMessageBox.information(self, "提示",
                                    "未检测到正在运行的Telegram进程。\n\n请确保Telegram已经登录并正在运行。")
            return

        self.log_message(f"找到 {len(processes)} 个Telegram进程")

        # 尝试使用标准会话路径
        session_paths = self.get_telegram_session_paths()

        if session_paths:
            self.log_message(f"找到会话文件: {session_paths}")
            QMessageBox.information(self, "信息",
                                    "已检测到Telegram会话。\n\n请使用备用方式手动输入API凭证连接。")
        else:
            self.log_message("未找到标准会话文件")
            QMessageBox.information(self, "信息",
                                    "已检测到Telegram正在运行。\n\n请使用备用方式连接：\n"
                                    "1. 访问 https://my.telegram.org\n"
                                    "2. 获取API ID和API Hash\n"
                                    "3. 在下方输入凭证连接")

    def get_telegram_session_paths(self):
        """获取可能的Telegram会话路径"""
        paths = []
        base_dirs = [
            os.path.expanduser("~/.local/share/TelegramDesktop"),
            os.path.expanduser("~/AppData/Roaming/Telegram Desktop"),
            os.path.expanduser("~/Library/Application Support/Telegram Desktop"),
        ]

        for base_dir in base_dirs:
            if os.path.exists(base_dir):
                for file in os.listdir(base_dir):
                    if file.endswith(('.map', '.key')):
                        paths.append(os.path.join(base_dir, file))

        return paths

    def manual_connect(self):
        """手动连接"""
        api_id = self.api_id_input.text()
        api_hash = self.api_hash_input.text()

        if not api_id or not api_hash:
            QMessageBox.warning(self, "错误", "请输入API ID和API Hash")
            return

        # 保存凭证
        self.last_api_id = api_id
        self.last_api_hash = api_hash
        self.save_config()

        # 尝试连接现有会话
        if self.last_session:
            asyncio.create_task(self.connect_with_session(
                self.last_session, api_id, api_hash
            ))
        else:
            # 如果没有保存的会话，需要创建新会话
            self.create_new_session(api_id, api_hash)

    async def connect_with_session(self, session_string, api_id, api_hash):
        """使用会话字符串连接"""
        try:
            self.log_message("正在连接Telegram...")
            self.status_label.setText("状态: 连接中...")

            self.client = TelegramClient(
                StringSession(session_string),
                int(api_id),
                api_hash
            )

            await self.client.connect()

            if await self.client.is_user_authorized():
                self.is_authenticated = True
                await self.on_connect_success()
            else:
                self.log_message("会话已过期")
                self.status_label.setText("状态: 会话过期")

        except Exception as e:
            self.log_message(f"连接失败: {str(e)}")
            self.status_label.setText("状态: 连接失败")

    def create_new_session(self, api_id, api_hash):
        """创建新会话"""
        from telethon.sessions import MemorySession

        try:
            self.log_message("创建新会话...")
            self.client = TelegramClient(
                MemorySession(),
                int(api_id),
                api_hash
            )

            # 在新线程中启动客户端
            asyncio.create_task(self.start_new_session())

        except Exception as e:
            self.log_message(f"创建会话失败: {str(e)}")

    async def start_new_session(self):
        """启动新会话"""
        try:
            await self.client.start()

            # 保存会话
            session_string = self.client.session.save()
            self.last_session = session_string
            self.save_config()

            self.is_authenticated = True
            await self.on_connect_success()

        except Exception as e:
            self.log_message(f"启动失败: {str(e)}")

    async def on_connect_success(self):
        """连接成功后的处理"""
        try:
            me = await self.client.get_me()
            user_info = f"{me.first_name} {me.last_name or ''} (@{me.username or '无用户名'})"

            # 更新UI
            self.status_label.setText("状态: 已连接 ✓")
            self.status_label.setStyleSheet("color: green; font-weight: bold; font-size: 14px;")
            self.user_info_label.setText(f"用户: {user_info}")

            self.start_btn.setEnabled(True)
            self.single_change_btn.setEnabled(True)

            self.log_message(f"连接成功！欢迎 {user_info}")

            # 获取当前头像
            await self.get_current_avatar()

        except Exception as e:
            self.log_message(f"获取用户信息失败: {str(e)}")

    async def get_current_avatar(self):
        """获取当前头像"""
        try:
            me = await self.client.get_me()
            photos = await self.client.get_profile_photos(me)
            if photos:
                self.log_message(f"当前有 {len(photos)} 个头像")
            else:
                self.log_message("当前没有设置头像")
        except Exception as e:
            self.log_message(f"获取头像信息失败: {str(e)}")

    def add_avatar_files(self):
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "选择头像图片",
            "",
            "图片文件 (*.jpg *.jpeg *.png *.bmp *.gif *.webp)"
        )

        for file in files:
            if file not in self.avatars_queue:
                self.avatars_queue.append(file)
                item = QListWidgetItem(file)
                self.file_list.addItem(item)

        self.log_message(f"添加了 {len(files)} 个文件")
        self.update_progress()

        if self.avatars_queue and not self.file_list.currentItem():
            self.file_list.setCurrentRow(0)

    def add_avatar_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "选择头像文件夹")
        if folder:
            image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp'}
            added_count = 0

            for file in Path(folder).rglob('*'):
                if file.suffix.lower() in image_extensions:
                    file_str = str(file)
                    if file_str not in self.avatars_queue:
                        self.avatars_queue.append(file_str)
                        item = QListWidgetItem(file_str)
                        self.file_list.addItem(item)
                        added_count += 1

            self.log_message(f"从文件夹添加了 {added_count} 个文件")
            self.update_progress()

            if added_count > 0 and not self.file_list.currentItem():
                self.file_list.setCurrentRow(0)

    def clear_avatar_files(self):
        self.avatars_queue.clear()
        self.file_list.clear()
        self.preview_label.clear()
        self.preview_info.setText("未选择图片")
        self.update_progress()
        self.log_message("已清空头像列表")

    def update_preview(self):
        """更新预览"""
        current_row = self.file_list.currentRow()
        if 0 <= current_row < len(self.avatars_queue):
            file_path = self.avatars_queue[current_row]

            # 显示文件信息
            file_name = Path(file_path).name
            file_size = os.path.getsize(file_path) / 1024  # KB
            self.preview_info.setText(
                f"文件名: {file_name}\n大小: {file_size:.1f} KB\n位置: {current_row + 1}/{len(self.avatars_queue)}")

            # 加载并显示图片
            pixmap = QPixmap(file_path)
            if not pixmap.isNull():
                # 缩放以适应预览区域
                scaled_pixmap = pixmap.scaled(
                    self.preview_label.size() - QSize(20, 20),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                self.preview_label.setPixmap(scaled_pixmap)
            else:
                self.preview_label.setText("无法加载图片")
                self.preview_label.setAlignment(Qt.AlignCenter)

    def show_previous_preview(self):
        current = self.file_list.currentRow()
        if current > 0:
            self.file_list.setCurrentRow(current - 1)

    def show_next_preview(self):
        current = self.file_list.currentRow()
        if current < self.file_list.count() - 1:
            self.file_list.setCurrentRow(current + 1)

    def update_progress(self):
        total = len(self.avatars_queue)
        self.progress_bar.setMaximum(total if total > 0 else 1)
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat(f"准备就绪 - {total} 个头像")

    def start_changing(self):
        if not self.is_authenticated:
            QMessageBox.warning(self, "警告", "请先连接Telegram")
            return

        if not self.avatars_queue:
            QMessageBox.warning(self, "警告", "请先添加头像文件")
            return

        self.is_changing = True
        self.is_paused = False
        self.start_btn.setEnabled(False)
        self.pause_btn.setEnabled(True)
        self.stop_btn.setEnabled(True)
        self.single_change_btn.setEnabled(False)
        self.change_interval = self.interval_spin.value()
        self.current_avatar_index = 0

        # 如果需要随机顺序，打乱列表
        if self.random_checkbox.isChecked():
            import random
            random.shuffle(self.avatars_queue)
            self.file_list.clear()
            for file in self.avatars_queue:
                self.file_list.addItem(QListWidgetItem(file))

        self.log_message("开始批量更换头像...")
        self.progress_bar.setFormat("更换中: %p% (%v/%m)")

        # 启动更换任务
        self.change_task = asyncio.create_task(self.change_avatars_loop())

    def pause_changing(self):
        if self.is_paused:
            self.is_paused = False
            self.pause_btn.setText("⏸️ 暂停")
            self.log_message("继续更换头像")
        else:
            self.is_paused = True
            self.pause_btn.setText("▶ 继续")
            self.log_message("已暂停")

    def stop_changing(self):
        self.is_changing = False
        self.is_paused = False
        self.start_btn.setEnabled(True)
        self.pause_btn.setEnabled(False)
        self.stop_btn.setEnabled(False)
        self.single_change_btn.setEnabled(True)
        self.log_message("已停止更换头像")
        self.progress_bar.setFormat("已停止 - %v/%m 个已完成")

    async def change_avatars_loop(self):
        while self.is_changing and self.avatars_queue:
            # 检查是否暂停
            while self.is_paused and self.is_changing:
                await asyncio.sleep(0.5)

            if self.current_avatar_index >= len(self.avatars_queue):
                if self.loop_checkbox.isChecked():
                    self.current_avatar_index = 0
                    self.log_message("开始新一轮更换...")
                else:
                    self.stop_changing()
                    self.log_message("所有头像已更换完成！")
                    break

            current_file = self.avatars_queue[self.current_avatar_index]
            file_name = Path(current_file).name

            try:
                # 更新状态
                self.log_message(
                    f"正在设置头像: {file_name} ({self.current_avatar_index + 1}/{len(self.avatars_queue)})")

                # 设置头像
                await self.client.upload_profile_photo(current_file)

                # 更新进度
                self.progress_bar.setValue(self.current_avatar_index + 1)

                self.current_avatar_index += 1

                # 等待间隔
                if self.is_changing and not self.is_paused and self.current_avatar_index < len(self.avatars_queue):
                    for i in range(self.change_interval):
                        if not self.is_changing or self.is_paused:
                            break
                        await asyncio.sleep(1)

            except errors.FloodWaitError as e:
                wait_time = e.seconds
                self.log_message(f"需要等待 {wait_time} 秒才能继续操作")
                await asyncio.sleep(wait_time)
                continue
            except Exception as e:
                self.log_message(f"设置头像失败 {file_name}: {str(e)}")
                self.current_avatar_index += 1
                await asyncio.sleep(1)

    async def single_change(self):
        """单次更换当前选中的头像"""
        if not self.is_authenticated:
            QMessageBox.warning(self, "警告", "请先连接Telegram")
            return

        current_row = self.file_list.currentRow()
        if current_row < 0 or current_row >= len(self.avatars_queue):
            QMessageBox.warning(self, "警告", "请先选择一个头像文件")
            return

        current_file = self.avatars_queue[current_row]
        file_name = Path(current_file).name

        try:
            self.log_message(f"正在设置单个头像: {file_name}")

            # 禁用按钮防止重复点击
            self.single_change_btn.setEnabled(False)

            # 设置头像
            await self.client.upload_profile_photo(current_file)

            self.log_message(f"头像设置成功: {file_name}")
            QMessageBox.information(self, "成功", f"头像已更换为: {file_name}")

        except errors.FloodWaitError as e:
            wait_time = e.seconds
            self.log_message(f"需要等待 {wait_time} 秒才能继续操作")
            QMessageBox.warning(self, "等待", f"请等待 {wait_time} 秒后再试")
        except Exception as e:
            self.log_message(f"设置头像失败: {str(e)}")
            QMessageBox.critical(self, "错误", f"设置头像失败: {str(e)}")
        finally:
            self.single_change_btn.setEnabled(True)

    def log_message(self, message):
        """记录日志消息（修复了方法名不一致的问题）"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")
        # 自动滚动到底部
        self.log_text.verticalScrollBar().setValue(
            self.log_text.verticalScrollBar().maximum()
        )

    def closeEvent(self, event):
        if self.is_changing:
            self.stop_changing()

        if self.client:
            asyncio.create_task(self.client.disconnect())

        self.save_config()
        event.accept()


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # 使用Fusion样式

    # 创建窗口
    window = TelegramAvatarChanger()
    window.show()

    # 运行应用
    sys.exit(app.exec_())


if __name__ == '__main__':
    # 检查是否需要安装依赖
    try:
        import PyQt5
        import telethon
        import psutil
    except ImportError as e:
        print(f"缺少依赖包: {e}")
        print("请安装所需的依赖包：")
        print("pip install PyQt5 telethon psutil")
        sys.exit(1)

    # 在单独的线程中运行asyncio事件循环
    import threading


    def start_asyncio_loop():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_forever()


    # 启动asyncio事件循环线程
    asyncio_thread = threading.Thread(target=start_asyncio_loop, daemon=True)
    asyncio_thread.start()

    # 运行Qt应用
    main()