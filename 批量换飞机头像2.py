import sys
import os
import json
import time
import random
import threading
from datetime import datetime
from pathlib import Path

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


# 先检查并安装依赖
def install_dependencies():
    """检查并安装依赖"""
    import subprocess
    import importlib

    dependencies = [
        "PyQt5",
        "telethon",
        "pillow"  # 用于图片处理
    ]

    missing = []
    for dep in dependencies:
        try:
            importlib.import_module(dep if dep != "pillow" else "PIL")
        except ImportError:
            missing.append(dep)

    if missing:
        print("正在安装缺少的依赖包...")
        for dep in missing:
            try:
                if dep == "pillow":
                    dep = "Pillow"
                subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
                print(f"✓ 已安装 {dep}")
            except Exception as e:
                print(f"✗ 安装 {dep} 失败: {e}")
                return False

        print("\n所有依赖安装完成！请重新运行程序。")
        input("按回车键退出...")
        sys.exit(0)

    return True


# 安装依赖
if install_dependencies():

    # 现在导入telethon
    from telethon import TelegramClient
    from telethon.errors import FloodWaitError, SessionPasswordNeededError
    from telethon.sessions import StringSession


    class TelegramAvatarChanger(QMainWindow):
        def __init__(self):
            super().__init__()
            self.client = None
            self.is_authenticated = False
            self.avatars_queue = []
            self.current_avatar_index = 0
            self.change_interval = 10
            self.is_changing = False
            self.is_paused = False

            # 会话目录
            self.session_dir = "telegram_sessions"
            os.makedirs(self.session_dir, exist_ok=True)

            # 配置
            self.config_file = "telegram_config.json"
            self.load_config()

            self.init_ui()

        def load_config(self):
            """加载配置"""
            if os.path.exists(self.config_file):
                try:
                    with open(self.config_file, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                        self.api_id = str(config.get('api_id', ''))
                        self.api_hash = config.get('api_hash', '')
                        self.phone_number = config.get('phone_number', '')
                        self.session_string = config.get('session_string', '')
                except:
                    self.api_id = ''
                    self.api_hash = ''
                    self.phone_number = ''
                    self.session_string = ''
            else:
                self.api_id = ''
                self.api_hash = ''
                self.phone_number = ''
                self.session_string = ''

        def save_config(self):
            """保存配置"""
            config = {
                'api_id': self.api_id,
                'api_hash': self.api_hash,
                'phone_number': self.phone_number,
                'session_string': self.session_string
            }
            try:
                with open(self.config_file, 'w', encoding='utf-8') as f:
                    json.dump(config, f, ensure_ascii=False, indent=2)
            except:
                pass

        def init_ui(self):
            self.setWindowTitle("Telegram头像批量更换工具")
            self.setGeometry(100, 100, 900, 700)

            # 创建中心窗口部件
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            main_layout = QVBoxLayout(central_widget)

            # 1. 连接区域
            conn_group = QGroupBox("🔗 Telegram连接设置")
            conn_layout = QVBoxLayout()

            # API设置
            api_layout = QGridLayout()
            api_layout.addWidget(QLabel("API ID:"), 0, 0)
            self.api_id_input = QLineEdit(self.api_id)
            self.api_id_input.setPlaceholderText("从 my.telegram.org 获取")
            api_layout.addWidget(self.api_id_input, 0, 1)

            api_layout.addWidget(QLabel("API Hash:"), 1, 0)
            self.api_hash_input = QLineEdit(self.api_hash)
            self.api_hash_input.setPlaceholderText("从 my.telegram.org 获取")
            self.api_hash_input.setEchoMode(QLineEdit.Password)
            api_layout.addWidget(self.api_hash_input, 1, 1)

            api_layout.addWidget(QLabel("手机号:"), 2, 0)
            self.phone_input = QLineEdit(self.phone_number)
            self.phone_input.setPlaceholderText("+8612345678900")
            api_layout.addWidget(self.phone_input, 2, 1)

            conn_layout.addLayout(api_layout)

            # 连接按钮
            btn_layout = QHBoxLayout()
            self.connect_btn = QPushButton("连接到Telegram")
            self.connect_btn.clicked.connect(self.connect_to_telegram)
            self.connect_btn.setStyleSheet("""
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    padding: 10px;
                    font-weight: bold;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: #45a049;
                }
            """)
            btn_layout.addWidget(self.connect_btn)

            self.disconnect_btn = QPushButton("断开连接")
            self.disconnect_btn.clicked.connect(self.disconnect_from_telegram)
            self.disconnect_btn.setEnabled(False)
            btn_layout.addWidget(self.disconnect_btn)

            conn_layout.addLayout(btn_layout)

            # 状态显示
            self.status_label = QLabel("状态: 未连接")
            self.status_label.setStyleSheet("font-weight: bold; font-size: 14px;")
            conn_layout.addWidget(self.status_label)

            self.user_label = QLabel("")
            conn_layout.addWidget(self.user_label)

            conn_group.setLayout(conn_layout)
            main_layout.addWidget(conn_group)

            # 2. 文件管理区域
            file_group = QGroupBox("📁 头像文件管理")
            file_layout = QVBoxLayout()

            # 文件列表
            self.file_list = QListWidget()
            self.file_list.setSelectionMode(QListWidget.ExtendedSelection)
            file_layout.addWidget(self.file_list)

            # 文件操作按钮
            file_btn_layout = QHBoxLayout()

            self.add_btn = QPushButton("添加文件")
            self.add_btn.clicked.connect(self.add_files)
            self.add_btn.setIcon(self.style().standardIcon(QStyle.SP_FileIcon))
            file_btn_layout.addWidget(self.add_btn)

            self.add_folder_btn = QPushButton("添加文件夹")
            self.add_folder_btn.clicked.connect(self.add_folder)
            self.add_folder_btn.setIcon(self.style().standardIcon(QStyle.SP_DirIcon))
            file_btn_layout.addWidget(self.add_folder_btn)

            self.clear_btn = QPushButton("清空列表")
            self.clear_btn.clicked.connect(self.clear_files)
            self.clear_btn.setIcon(self.style().standardIcon(QStyle.SP_DialogCancelButton))
            file_btn_layout.addWidget(self.clear_btn)

            file_layout.addLayout(file_btn_layout)

            # 文件统计
            self.file_count_label = QLabel("已选择 0 个文件")
            file_layout.addWidget(self.file_count_label)

            file_group.setLayout(file_layout)
            main_layout.addWidget(file_group)

            # 3. 预览区域
            preview_group = QGroupBox("🖼️ 图片预览")
            preview_layout = QHBoxLayout()

            self.preview_label = QLabel()
            self.preview_label.setAlignment(Qt.AlignCenter)
            self.preview_label.setMinimumSize(250, 250)
            self.preview_label.setStyleSheet("""
                QLabel {
                    border: 2px solid #cccccc;
                    border-radius: 10px;
                    background-color: white;
                }
            """)
            preview_layout.addWidget(self.preview_label)

            # 预览信息和控制
            info_layout = QVBoxLayout()

            self.preview_info = QTextEdit()
            self.preview_info.setReadOnly(True)
            self.preview_info.setMaximumHeight(100)
            info_layout.addWidget(self.preview_info)

            # 预览控制
            preview_ctrl = QHBoxLayout()
            self.prev_btn = QPushButton("◀ 上一个")
            self.prev_btn.clicked.connect(self.prev_image)
            preview_ctrl.addWidget(self.prev_btn)

            self.next_btn = QPushButton("下一个 ▶")
            self.next_btn.clicked.connect(self.next_image)
            preview_ctrl.addWidget(self.next_btn)
            info_layout.addLayout(preview_ctrl)

            # 单次更换按钮
            self.single_set_btn = QPushButton("🔄 设置当前头像")
            self.single_set_btn.clicked.connect(self.set_current_avatar)
            self.single_set_btn.setEnabled(False)
            self.single_set_btn.setStyleSheet("""
                QPushButton {
                    background-color: #2196F3;
                    color: white;
                    padding: 8px;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #1976D2;
                }
                QPushButton:disabled {
                    background-color: #cccccc;
                }
            """)
            info_layout.addWidget(self.single_set_btn)

            info_layout.addStretch()
            preview_layout.addLayout(info_layout)

            preview_group.setLayout(preview_layout)
            main_layout.addWidget(preview_group)

            # 4. 设置区域
            settings_group = QGroupBox("⚙️ 更换设置")
            settings_layout = QGridLayout()

            settings_layout.addWidget(QLabel("更换间隔(秒):"), 0, 0)
            self.interval_spin = QSpinBox()
            self.interval_spin.setRange(5, 3600)
            self.interval_spin.setValue(10)
            self.interval_spin.setSuffix(" 秒")
            settings_layout.addWidget(self.interval_spin, 0, 1)

            settings_layout.addWidget(QLabel("循环模式:"), 1, 0)
            self.loop_cb = QCheckBox("循环更换")
            self.loop_cb.setChecked(True)
            settings_layout.addWidget(self.loop_cb, 1, 1)

            settings_layout.addWidget(QLabel("随机顺序:"), 2, 0)
            self.random_cb = QCheckBox("随机顺序")
            settings_layout.addWidget(self.random_cb, 2, 1)

            settings_group.setLayout(settings_layout)
            main_layout.addWidget(settings_group)

            # 5. 控制区域
            control_group = QGroupBox("🎮 操作控制")
            control_layout = QHBoxLayout()

            self.start_btn = QPushButton("▶ 开始批量更换")
            self.start_btn.clicked.connect(self.start_changing)
            self.start_btn.setEnabled(False)
            self.start_btn.setStyleSheet("""
                QPushButton {
                    background-color: #e74c3c;
                    color: white;
                    padding: 12px;
                    font-weight: bold;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: #c0392b;
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

            control_group.setLayout(control_layout)
            main_layout.addWidget(control_group)

            # 6. 进度和日志
            # 进度条
            self.progress_bar = QProgressBar()
            self.progress_bar.setTextVisible(True)
            self.progress_bar.setStyleSheet("""
                QProgressBar {
                    border: 1px solid #cccccc;
                    border-radius: 3px;
                    text-align: center;
                }
                QProgressBar::chunk {
                    background-color: #2ecc71;
                    border-radius: 3px;
                }
            """)
            main_layout.addWidget(self.progress_bar)

            # 日志区域
            log_group = QGroupBox("📝 操作日志")
            log_layout = QVBoxLayout()

            self.log_text = QTextEdit()
            self.log_text.setReadOnly(True)
            self.log_text.setMaximumHeight(120)
            self.log_text.setStyleSheet("""
                QTextEdit {
                    background-color: #f8f8f8;
                    border: 1px solid #dddddd;
                    font-family: Consolas, monospace;
                    font-size: 10px;
                }
            """)
            log_layout.addWidget(self.log_text)

            log_group.setLayout(log_layout)
            main_layout.addWidget(log_group)

            # 连接事件
            self.file_list.currentRowChanged.connect(self.update_preview)

            # 初始化日志
            self.log("程序已启动")
            self.log("首次使用需要API凭证，请访问: https://my.telegram.org")

        def log(self, message):
            """记录日志"""
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.log_text.append(f"[{timestamp}] {message}")
            # 滚动到底部
            scrollbar = self.log_text.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())

        def connect_to_telegram(self):
            """连接到Telegram"""
            # 获取输入值
            api_id = self.api_id_input.text().strip()
            api_hash = self.api_hash_input.text().strip()
            phone = self.phone_input.text().strip()

            if not api_id or not api_hash:
                QMessageBox.warning(self, "错误", "请输入API ID和API Hash")
                return

            if not phone:
                QMessageBox.warning(self, "错误", "请输入手机号（包含国家代码，如：+8612345678900）")
                return

            # 保存配置
            self.api_id = api_id
            self.api_hash = api_hash
            self.phone_number = phone
            self.save_config()

            # 更新UI
            self.connect_btn.setEnabled(False)
            self.connect_btn.setText("连接中...")
            self.status_label.setText("状态: 连接中...")
            self.log(f"正在连接到Telegram...")

            # 在新线程中连接
            threading.Thread(target=self._connect_thread, daemon=True).start()

        def _connect_thread(self):
            """连接线程"""
            try:
                # 创建客户端
                session_name = f"session_{self.phone_number}"
                session_path = os.path.join(self.session_dir, session_name)

                # 如果有保存的会话字符串，使用它
                if self.session_string:
                    self.client = TelegramClient(
                        StringSession(self.session_string),
                        int(self.api_id),
                        self.api_hash
                    )
                else:
                    self.client = TelegramClient(
                        session_path,
                        int(self.api_id),
                        self.api_hash
                    )

                # 启动客户端
                self.client.start(phone=self.phone_number)

                # 保存会话字符串供下次使用
                if not self.session_string:
                    self.session_string = self.client.session.save()
                    self.save_config()

                # 获取用户信息
                me = self.client.loop.run_until_complete(self.client.get_me())

                # 连接成功
                self._on_connect_success(me)

            except SessionPasswordNeededError:
                self._ask_for_password()
            except Exception as e:
                self._on_connect_error(str(e))

        def _ask_for_password(self):
            """请求两步验证密码"""
            QMetaObject.invokeMethod(self, "_show_password_dialog",
                                     Qt.QueuedConnection)

        def _show_password_dialog(self):
            """显示密码输入对话框"""
            password, ok = QInputDialog.getText(
                self,
                "两步验证",
                "请输入两步验证密码:",
                QLineEdit.Password
            )

            if ok and password:
                self.log("正在验证两步验证密码...")
                threading.Thread(target=self._verify_password_thread,
                                 args=(password,), daemon=True).start()
            else:
                self._on_connect_error("需要两步验证密码")

        def _verify_password_thread(self, password):
            """验证密码线程"""
            try:
                self.client.sign_in(password=password)
                me = self.client.loop.run_until_complete(self.client.get_me())
                self._on_connect_success(me)
            except Exception as e:
                self._on_connect_error(f"密码错误: {str(e)}")

        def _on_connect_success(self, me):
            """连接成功"""
            self.is_authenticated = True

            user_info = f"{me.first_name or ''} {me.last_name or ''}".strip()
            if me.username:
                user_info += f" (@{me.username})"

            # 更新UI
            QMetaObject.invokeMethod(self.connect_btn, "setText",
                                     Qt.QueuedConnection,
                                     Q_ARG(str, "已连接"))
            QMetaObject.invokeMethod(self.connect_btn, "setEnabled",
                                     Qt.QueuedConnection,
                                     Q_ARG(bool, False))
            QMetaObject.invokeMethod(self.disconnect_btn, "setEnabled",
                                     Qt.QueuedConnection,
                                     Q_ARG(bool, True))
            QMetaObject.invokeMethod(self.start_btn, "setEnabled",
                                     Qt.QueuedConnection,
                                     Q_ARG(bool, True))
            QMetaObject.invokeMethod(self.single_set_btn, "setEnabled",
                                     Qt.QueuedConnection,
                                     Q_ARG(bool, True))

            QMetaObject.invokeMethod(self.status_label, "setText",
                                     Qt.QueuedConnection,
                                     Q_ARG(str, "状态: ✅ 已连接"))
            QMetaObject.invokeMethod(self.status_label, "setStyleSheet",
                                     Qt.QueuedConnection,
                                     Q_ARG(str, "color: green; font-weight: bold;"))

            QMetaObject.invokeMethod(self.user_label, "setText",
                                     Qt.QueuedConnection,
                                     Q_ARG(str, f"用户: {user_info}"))

            QMetaObject.invokeMethod(self, "log",
                                     Qt.QueuedConnection,
                                     Q_ARG(str, f"✅ 连接成功！用户: {user_info}"))

            # 获取当前头像
            threading.Thread(target=self._get_current_photos, daemon=True).start()

        def _get_current_photos(self):
            """获取当前头像"""
            try:
                me = self.client.loop.run_until_complete(self.client.get_me())
                photos = self.client.loop.run_until_complete(
                    self.client.get_profile_photos(me)
                )
                QMetaObject.invokeMethod(self, "log",
                                         Qt.QueuedConnection,
                                         Q_ARG(str, f"当前有 {len(photos)} 个头像"))
            except Exception as e:
                pass

        def _on_connect_error(self, error_msg):
            """连接失败"""
            # 更新UI
            QMetaObject.invokeMethod(self.connect_btn, "setText",
                                     Qt.QueuedConnection,
                                     Q_ARG(str, "连接到Telegram"))
            QMetaObject.invokeMethod(self.connect_btn, "setEnabled",
                                     Qt.QueuedConnection,
                                     Q_ARG(bool, True))

            QMetaObject.invokeMethod(self.status_label, "setText",
                                     Qt.QueuedConnection,
                                     Q_ARG(str, "状态: ❌ 连接失败"))
            QMetaObject.invokeMethod(self.status_label, "setStyleSheet",
                                     Qt.QueuedConnection,
                                     Q_ARG(str, "color: red; font-weight: bold;"))

            # 显示详细错误
            error_display = str(error_msg)

            QMetaObject.invokeMethod(self, "log",
                                     Qt.QueuedConnection,
                                     Q_ARG(str, f"❌ 连接失败: {error_display}"))

            # 显示对话框
            QMetaObject.invokeMethod(self, "_show_error_dialog",
                                     Qt.QueuedConnection,
                                     Q_ARG(str, error_display))

        def _show_error_dialog(self, error_msg):
            """显示错误对话框"""
            QMessageBox.critical(self, "连接失败",
                                 f"连接失败: {error_msg}\n\n"
                                 "请确保：\n"
                                 "1. API ID和API Hash正确（从 my.telegram.org 获取）\n"
                                 "2. 手机号格式正确（包含国家代码，如：+8612345678900）\n"
                                 "3. 网络连接正常\n"
                                 "4. 如果启用了两步验证，需要输入密码")

        def disconnect_from_telegram(self):
            """断开连接"""
            if self.client:
                try:
                    self.client.disconnect()
                except:
                    pass
                self.client = None

            self.is_authenticated = False

            # 更新UI
            self.connect_btn.setText("连接到Telegram")
            self.connect_btn.setEnabled(True)
            self.disconnect_btn.setEnabled(False)
            self.start_btn.setEnabled(False)
            self.single_set_btn.setEnabled(False)

            self.status_label.setText("状态: 未连接")
            self.status_label.setStyleSheet("")
            self.user_label.setText("")

            self.log("已断开连接")

        def add_files(self):
            """添加文件"""
            files, _ = QFileDialog.getOpenFileNames(
                self,
                "选择头像图片",
                "",
                "图片文件 (*.jpg *.jpeg *.png *.bmp *.gif *.webp);;所有文件 (*.*)"
            )

            added = 0
            for file in files:
                if file not in self.avatars_queue:
                    self.avatars_queue.append(file)
                    self.file_list.addItem(os.path.basename(file))
                    added += 1

            if added > 0:
                self.log(f"添加了 {added} 个图片文件")
                self.update_file_count()
                self.update_progress()

                # 自动选择第一个
                if self.file_list.count() > 0 and self.file_list.currentRow() < 0:
                    self.file_list.setCurrentRow(0)

        def add_folder(self):
            """添加文件夹"""
            folder = QFileDialog.getExistingDirectory(self, "选择文件夹")
            if folder:
                image_exts = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp'}
                added = 0

                for file_path in Path(folder).rglob('*'):
                    if file_path.suffix.lower() in image_exts:
                        file_str = str(file_path)
                        if file_str not in self.avatars_queue:
                            self.avatars_queue.append(file_str)
                            self.file_list.addItem(file_path.name)
                            added += 1

                if added > 0:
                    self.log(f"从文件夹添加了 {added} 个图片文件")
                    self.update_file_count()
                    self.update_progress()

                    if self.file_list.count() > 0 and self.file_list.currentRow() < 0:
                        self.file_list.setCurrentRow(0)

        def clear_files(self):
            """清空文件列表"""
            self.avatars_queue.clear()
            self.file_list.clear()
            self.preview_label.clear()
            self.preview_info.clear()
            self.update_file_count()
            self.update_progress()
            self.log("已清空所有文件")

        def update_file_count(self):
            """更新文件计数"""
            count = len(self.avatars_queue)
            self.file_count_label.setText(f"已选择 {count} 个文件")

        def update_preview(self, row):
            """更新预览"""
            if 0 <= row < len(self.avatars_queue):
                file_path = self.avatars_queue[row]

                # 加载图片
                pixmap = QPixmap(file_path)
                if not pixmap.isNull():
                    # 缩放
                    scaled = pixmap.scaled(self.preview_label.size(),
                                           Qt.KeepAspectRatio,
                                           Qt.SmoothTransformation)
                    self.preview_label.setPixmap(scaled)

                    # 显示信息
                    info = f"📄 文件: {os.path.basename(file_path)}\n"
                    info += f"📊 大小: {os.path.getsize(file_path) / 1024:.1f} KB\n"
                    info += f"📐 尺寸: {pixmap.width()} × {pixmap.height()}\n"
                    info += f"📍 位置: {row + 1}/{len(self.avatars_queue)}"
                    self.preview_info.setText(info)
                else:
                    self.preview_label.setText("无法加载图片")
                    self.preview_info.setText(f"文件: {os.path.basename(file_path)}\n(无法加载)")

        def prev_image(self):
            """上一个图片"""
            current = self.file_list.currentRow()
            if current > 0:
                self.file_list.setCurrentRow(current - 1)

        def next_image(self):
            """下一个图片"""
            current = self.file_list.currentRow()
            if current < self.file_list.count() - 1:
                self.file_list.setCurrentRow(current + 1)

        def set_current_avatar(self):
            """设置当前头像"""
            if not self.is_authenticated:
                QMessageBox.warning(self, "错误", "请先连接到Telegram")
                return

            current_row = self.file_list.currentRow()
            if current_row < 0:
                QMessageBox.warning(self, "错误", "请先选择一个图片")
                return

            file_path = self.avatars_queue[current_row]
            self.log(f"正在设置头像: {os.path.basename(file_path)}")

            # 在新线程中设置
            threading.Thread(target=self._set_avatar_thread,
                             args=(file_path,),
                             daemon=True).start()

        def _set_avatar_thread(self, file_path):
            """设置头像线程"""
            try:
                # 使用telethon上传头像
                self.client.loop.run_until_complete(
                    self.client.upload_profile_photo(file_path)
                )

                QMetaObject.invokeMethod(self, "log",
                                         Qt.QueuedConnection,
                                         Q_ARG(str, f"✅ 头像设置成功: {os.path.basename(file_path)}"))

            except FloodWaitError as e:
                QMetaObject.invokeMethod(self, "log",
                                         Qt.QueuedConnection,
                                         Q_ARG(str, f"⏳ 需要等待 {e.seconds} 秒"))
            except Exception as e:
                QMetaObject.invokeMethod(self, "log",
                                         Qt.QueuedConnection,
                                         Q_ARG(str, f"❌ 设置失败: {str(e)}"))

        def update_progress(self):
            """更新进度条"""
            total = len(self.avatars_queue)
            self.progress_bar.setMaximum(total if total > 0 else 1)
            self.progress_bar.setValue(0)
            self.progress_bar.setFormat(f"准备就绪 ({total} 个头像)")

        def start_changing(self):
            """开始批量更换"""
            if not self.is_authenticated:
                QMessageBox.warning(self, "错误", "请先连接到Telegram")
                return

            if not self.avatars_queue:
                QMessageBox.warning(self, "错误", "请先添加头像文件")
                return

            self.is_changing = True
            self.is_paused = False
            self.current_avatar_index = 0
            self.change_interval = self.interval_spin.value()

            # 随机顺序
            if self.random_cb.isChecked():
                random.shuffle(self.avatars_queue)
                self.file_list.clear()
                for file in self.avatars_queue:
                    self.file_list.addItem(os.path.basename(file))

            # 更新按钮状态
            self.start_btn.setEnabled(False)
            self.pause_btn.setEnabled(True)
            self.stop_btn.setEnabled(True)
            self.connect_btn.setEnabled(False)
            self.single_set_btn.setEnabled(False)

            self.log(f"🚀 开始批量更换头像 (间隔: {self.change_interval}秒)")
            self.progress_bar.setFormat("更换中: %p% (%v/%m)")

            # 开始线程
            threading.Thread(target=self._change_avatars_thread, daemon=True).start()

        def pause_changing(self):
            """暂停/继续"""
            if self.is_paused:
                self.is_paused = False
                self.pause_btn.setText("⏸️ 暂停")
                self.log("继续更换")
            else:
                self.is_paused = True
                self.pause_btn.setText("▶ 继续")
                self.log("已暂停")

        def stop_changing(self):
            """停止"""
            self.is_changing = False
            self.is_paused = False

            self.start_btn.setEnabled(True)
            self.pause_btn.setEnabled(False)
            self.stop_btn.setEnabled(False)
            self.connect_btn.setEnabled(True)
            self.single_set_btn.setEnabled(True)

            self.pause_btn.setText("⏸️ 暂停")
            self.log("已停止更换")
            self.progress_bar.setFormat("已停止 (%v/%m 个完成)")

        def _change_avatars_thread(self):
            """批量更换线程"""
            while self.is_changing and self.current_avatar_index < len(self.avatars_queue):
                # 检查暂停
                while self.is_paused and self.is_changing:
                    time.sleep(0.5)

                if not self.is_changing:
                    break

                file_path = self.avatars_queue[self.current_avatar_index]
                filename = os.path.basename(file_path)

                try:
                    # 更新进度
                    QMetaObject.invokeMethod(self.progress_bar, "setValue",
                                             Qt.QueuedConnection,
                                             Q_ARG(int, self.current_avatar_index + 1))

                    # 记录开始
                    QMetaObject.invokeMethod(self, "log",
                                             Qt.QueuedConnection,
                                             Q_ARG(str, f"正在设置: {filename} "
                                                        f"({self.current_avatar_index + 1}/{len(self.avatars_queue)})"))

                    # 设置头像
                    self.client.loop.run_until_complete(
                        self.client.upload_profile_photo(file_path)
                    )

                    # 记录成功
                    QMetaObject.invokeMethod(self, "log",
                                             Qt.QueuedConnection,
                                             Q_ARG(str, f"  ✅ 完成: {filename}"))

                    self.current_avatar_index += 1

                    # 等待
                    if self.is_changing and self.current_avatar_index < len(self.avatars_queue):
                        wait_time = self.change_interval
                        while wait_time > 0 and self.is_changing and not self.is_paused:
                            time.sleep(1)
                            wait_time -= 1

                except FloodWaitError as e:
                    wait_time = e.seconds
                    QMetaObject.invokeMethod(self, "log",
                                             Qt.QueuedConnection,
                                             Q_ARG(str, f"⏳ 需要等待 {wait_time} 秒"))
                    time.sleep(wait_time)
                    continue

                except Exception as e:
                    QMetaObject.invokeMethod(self, "log",
                                             Qt.QueuedConnection,
                                             Q_ARG(str, f"❌ 失败: {filename} - {str(e)}"))
                    self.current_avatar_index += 1
                    time.sleep(2)
                    continue

            # 循环模式
            if self.is_changing and self.loop_cb.isChecked():
                self.current_avatar_index = 0
                self.log("开始新一轮更换...")
                # 重新开始
                time.sleep(2)
                if self.is_changing:
                    self._change_avatars_thread()
                    return

            # 完成
            QMetaObject.invokeMethod(self, "stop_changing", Qt.QueuedConnection)
            QMetaObject.invokeMethod(self, "log", Qt.QueuedConnection,
                                     Q_ARG(str, "✅ 批量更换完成！"))

        def closeEvent(self, event):
            """关闭事件"""
            if self.is_changing:
                self.stop_changing()

            if self.client:
                try:
                    self.client.disconnect()
                except:
                    pass

            self.save_config()
            self.log("程序已退出")
            event.accept()


    def main():
        app = QApplication(sys.argv)
        app.setApplicationName("Telegram头像批量更换工具")

        # 设置样式
        app.setStyle("Fusion")

        # 设置默认样式
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(240, 240, 240))
        palette.setColor(QPalette.WindowText, QColor(0, 0, 0))
        palette.setColor(QPalette.Base, QColor(255, 255, 255))
        palette.setColor(QPalette.AlternateBase, QColor(245, 245, 245))
        palette.setColor(QPalette.ToolTipBase, QColor(255, 255, 255))
        palette.setColor(QPalette.ToolTipText, QColor(0, 0, 0))
        palette.setColor(QPalette.Text, QColor(0, 0, 0))
        palette.setColor(QPalette.Button, QColor(240, 240, 240))
        palette.setColor(QPalette.ButtonText, QColor(0, 0, 0))
        palette.setColor(QPalette.BrightText, QColor(255, 0, 0))
        palette.setColor(QPalette.Link, QColor(42, 130, 218))
        palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
        app.setPalette(palette)

        window = TelegramAvatarChanger()
        window.show()

        sys.exit(app.exec_())


    if __name__ == "__main__":
        main()