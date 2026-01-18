import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import psutil
import os
import re
import sys
import subprocess


class TelegramAPI提取器:
    def __init__(self, root):
        self.root = root
        self.root.title("Telegram API ID & Hash 提取工具")
        self.root.geometry("750x600")
        self.root.resizable(True, True)

        # 设置应用程序图标（可选）
        try:
            self.root.iconbitmap('telegram.ico')  # 如果有图标文件的话
        except:
            pass

        # 设置样式
        self.设置样式()

        # 创建主界面
        self.创建主界面()

        # 初始化变量
        self.telegram路径 = None
        self.日志("应用程序已启动。点击'扫描Telegram'开始。")

    def 设置样式(self):
        """设置界面样式"""
        style = ttk.Style()
        style.theme_use('clam')

        # 自定义颜色
        self.root.configure(bg='#f0f0f0')

        # 自定义按钮样式
        style.configure('成功.TButton', foreground='green')
        style.configure('警告.TButton', foreground='orange')
        style.configure('危险.TButton', foreground='red')

    def 创建主界面(self):
        """创建主界面组件"""
        # 创建主框架
        主框架 = ttk.Frame(self.root, padding="15")
        主框架.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 标题
        标题标签 = tk.Label(
            主框架,
            text="Telegram API ID & Hash 提取工具",
            font=("微软雅黑", 18, "bold"),
            bg='#f0f0f0',
            fg='#2c3e50'
        )
        标题标签.grid(row=0, column=0, columnspan=2, pady=(0, 20))

        # 状态显示
        self.状态标签 = tk.Label(
            主框架,
            text="准备扫描Telegram进程...",
            font=("微软雅黑", 10),
            bg='#f0f0f0',
            fg='#3498db'
        )
        self.状态标签.grid(row=1, column=0, columnspan=2, pady=(0, 15), sticky=tk.W)

        # 按钮框架
        按钮框架 = ttk.Frame(主框架)
        按钮框架.grid(row=2, column=0, columnspan=2, pady=(0, 20))

        # 扫描按钮
        self.扫描按钮 = ttk.Button(
            按钮框架,
            text="🔍 扫描Telegram进程",
            command=self.扫描Telegram进程,
            width=25
        )
        self.扫描按钮.pack(side=tk.LEFT, padx=5)

        # 提取按钮
        self.提取按钮 = ttk.Button(
            按钮框架,
            text="📥 提取API凭证",
            command=self.提取API凭证,
            width=25,
            state="disabled"
        )
        self.提取按钮.pack(side=tk.LEFT, padx=5)

        # 清理按钮
        self.清理按钮 = ttk.Button(
            按钮框架,
            text="🗑️ 清理日志",
            command=self.清理日志,
            width=20
        )
        self.清理按钮.pack(side=tk.LEFT, padx=5)

        # API凭证显示框架
        凭证框架 = ttk.LabelFrame(主框架, text="提取的API凭证", padding="15")
        凭证框架.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))

        # API ID
        tk.Label(
            凭证框架,
            text="API ID:",
            font=("微软雅黑", 11, "bold"),
            bg='#f0f0f0'
        ).grid(row=0, column=0, sticky=tk.W, pady=8)

        self.api_id变量 = tk.StringVar()
        api_id输入框 = ttk.Entry(
            凭证框架,
            textvariable=self.api_id变量,
            width=50,
            font=("Consolas", 10),
            state="readonly"
        )
        api_id输入框.grid(row=0, column=1, padx=(15, 0), pady=8)

        # API Hash
        tk.Label(
            凭证框架,
            text="API Hash:",
            font=("微软雅黑", 11, "bold"),
            bg='#f0f0f0'
        ).grid(row=1, column=0, sticky=tk.W, pady=8)

        self.api_hash变量 = tk.StringVar()
        api_hash输入框 = ttk.Entry(
            凭证框架,
            textvariable=self.api_hash变量,
            width=50,
            font=("Consolas", 10),
            state="readonly"
        )
        api_hash输入框.grid(row=1, column=1, padx=(15, 0), pady=8)

        # 复制按钮框架
        复制按钮框架 = ttk.Frame(凭证框架)
        复制按钮框架.grid(row=2, column=0, columnspan=2, pady=(15, 5))

        ttk.Button(
            复制按钮框架,
            text="📋 复制API ID",
            command=self.复制API_ID
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            复制按钮框架,
            text="📋 复制API Hash",
            command=self.复制API_Hash
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            复制按钮框架,
            text="📋 复制全部",
            command=self.复制全部
        ).pack(side=tk.LEFT, padx=5)

        # 手动输入按钮
        ttk.Button(
            复制按钮框架,
            text="✏️ 手动输入",
            command=self.手动输入凭证
        ).pack(side=tk.LEFT, padx=5)

        # 日志框架
        日志框架 = ttk.LabelFrame(主框架, text="操作日志", padding="10")
        日志框架.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 15))

        self.日志文本框 = scrolledtext.ScrolledText(
            日志框架,
            height=12,
            width=85,
            font=("微软雅黑", 9),
            bg='#2c3e50',
            fg='#ecf0f1'
        )
        self.日志文本框.pack(fill=tk.BOTH, expand=True)

        # 信息提示
        信息标签 = tk.Label(
            主框架,
            text="提示：请确保Telegram桌面版正在运行后再进行提取操作。\n如果自动提取失败，可以使用手动输入功能。",
            font=("微软雅黑", 9),
            bg='#f0f0f0',
            fg='#7f8c8d',
            justify=tk.LEFT
        )
        信息标签.grid(row=5, column=0, columnspan=2, pady=(10, 0), sticky=tk.W)

        # 版本信息
        版本标签 = tk.Label(
            主框架,
            text="版本 1.0 | 基于Python 3.x",
            font=("微软雅黑", 8),
            bg='#f0f0f0',
            fg='#95a5a6'
        )
        版本标签.grid(row=6, column=1, sticky=tk.E, pady=(10, 0))

        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        主框架.columnconfigure(0, weight=1)
        主框架.columnconfigure(1, weight=1)
        主框架.rowconfigure(4, weight=1)

    def 日志(self, 消息):
        """添加日志消息"""
        时间戳 = self.获取时间戳()
        self.日志文本框.insert(tk.END, f"[{时间戳}] {消息}\n")
        self.日志文本框.see(tk.END)
        self.root.update()

    def 获取时间戳(self):
        """获取当前时间戳"""
        from datetime import datetime
        return datetime.now().strftime("%H:%M:%S")

    def 扫描Telegram进程(self):
        """扫描系统中正在运行的Telegram进程"""
        self.日志("\n" + "=" * 60)
        self.日志("开始扫描Telegram进程...")

        telegram进程列表 = []

        try:
            for 进程 in psutil.process_iter(['pid', 'name', 'exe']):
                try:
                    进程名称 = 进程.info['name'].lower() if 进程.info['name'] else ""
                    进程路径 = 进程.info['exe'] if 进程.info['exe'] else ""

                    # 检查是否是Telegram进程
                    if 'telegram' in 进程名称 or 'telegram' in 进程路径.lower():
                        telegram进程列表.append(进程)
                        self.日志(f"发现Telegram进程: PID={进程.pid}, 名称={进程名称}")

                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            if not telegram进程列表:
                self.日志("❌ 未发现正在运行的Telegram进程！")
                self.状态标签.config(text="未找到Telegram进程", fg='#e74c3c')
                self.提取按钮.config(state="disabled")

                # 提供启动Telegram的选项
                回答 = messagebox.askyesno(
                    "未找到Telegram",
                    "未检测到正在运行的Telegram进程！\n\n是否要启动Telegram？"
                )

                if 回答:
                    self.启动Telegram()
                return

            # 获取Telegram安装路径
            for 进程 in telegram进程列表:
                try:
                    执行路径 = 进程.exe()
                    if 执行路径:
                        self.telegram路径 = os.path.dirname(执行路径)
                        self.日志(f"Telegram执行路径: {执行路径}")
                        self.日志(f"Telegram目录: {self.telegram路径}")
                        break
                except:
                    continue

            self.状态标签.config(text=f"发现 {len(telegram进程列表)} 个Telegram进程", fg='#27ae60')
            self.提取按钮.config(state="normal")
            self.日志(f"✅ 扫描完成，发现 {len(telegram进程列表)} 个进程")

        except Exception as 错误:
            self.日志(f"❌ 扫描过程中发生错误: {str(错误)}")
            messagebox.showerror("错误", f"扫描过程中发生错误:\n{str(错误)}")

    def 启动Telegram(self):
        """尝试启动Telegram"""
        self.日志("尝试启动Telegram...")

        # 常见Telegram安装路径
        可能路径 = [
            # Windows
            r"C:\Program Files\Telegram Desktop\Telegram.exe",
            r"C:\Program Files (x86)\Telegram Desktop\Telegram.exe",
            os.path.join(os.environ.get('APPDATA', ''), 'Telegram Desktop', 'Telegram.exe'),
            # Linux
            "/usr/bin/telegram-desktop",
            "/snap/bin/telegram-desktop",
            # macOS
            "/Applications/Telegram.app/Contents/MacOS/Telegram",
        ]

        for 路径 in 可能路径:
            if os.path.exists(路径):
                try:
                    subprocess.Popen([路径])
                    self.日志(f"✅ 已启动Telegram: {路径}")
                    messagebox.showinfo("成功", f"Telegram已启动:\n{路径}")
                    return
                except Exception as 错误:
                    self.日志(f"启动失败 {路径}: {错误}")

        self.日志("❌ 无法找到或启动Telegram")
        messagebox.showwarning("警告", "无法自动启动Telegram。请手动启动后重试。")

    def 提取API凭证(self):
        """从Telegram配置文件中提取API凭证"""
        if not self.telegram路径:
            messagebox.showerror("错误", "无法确定Telegram安装路径！")
            return

        self.日志("\n" + "=" * 60)
        self.日志("开始提取API凭证...")

        # 尝试在不同平台查找配置文件
        配置路径列表 = self.获取可能配置路径()

        tdata路径 = None
        for 路径 in 配置路径列表:
            if os.path.exists(路径):
                tdata路径 = 路径
                self.日志(f"✅ 找到tdata目录: {路径}")
                break

        if not tdata路径:
            # 尝试在安装目录下查找
            安装目录tdata = os.path.join(self.telegram路径, 'tdata')
            if os.path.exists(安装目录tdata):
                tdata路径 = 安装目录tdata
                self.日志(f"✅ 在安装目录找到tdata: {安装目录tdata}")
            else:
                self.日志("❌ 无法找到tdata目录！")
                messagebox.showerror("错误",
                                     "无法找到Telegram数据目录 (tdata)！\n"
                                     "可能的原因：\n"
                                     "1. Telegram版本不同\n"
                                     "2. 配置文件被加密\n"
                                     "3. 权限不足"
                                     )
                return

        # 搜索配置文件
        api_id, api_hash = self.搜索API凭证(tdata路径)

        if api_id and api_hash:
            self.api_id变量.set(api_id)
            self.api_hash变量.set(api_hash)

            self.状态标签.config(text="✅ API凭证提取成功！", fg='#27ae60')
            self.日志("✅ API凭证提取成功！")
            self.日志(f"API ID: {api_id}")
            self.日志(f"API Hash: {api_hash}")

            messagebox.showinfo("成功", "API凭证提取成功！\n\n已自动填充到上方输入框。")
        else:
            self.状态标签.config(text="⚠ 需要手动提取", fg='#f39c12')
            self.日志("❌ 无法自动提取API凭证")

            回答 = messagebox.askyesno(
                "需要手动提取",
                "无法自动提取API凭证。\n\n"
                "请按照以下步骤手动获取：\n"
                "1. 访问 https://my.telegram.org\n"
                "2. 使用手机号登录\n"
                "3. 进入 'API Development Tools'\n"
                "4. 创建新应用\n\n"
                "是否要现在手动输入API凭证？"
            )

            if 回答:
                self.手动输入凭证()

    def 获取可能配置路径(self):
        """获取不同平台的Telegram配置路径"""
        return [
            # Windows
            os.path.join(os.environ.get('APPDATA', ''), 'Telegram Desktop', 'tdata'),
            os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Telegram Desktop', 'tdata'),
            # Linux
            os.path.expanduser('~/.local/share/TelegramDesktop/tdata'),
            os.path.expanduser('~/.TelegramDesktop/tdata'),
            # macOS
            os.path.expanduser('~/Library/Application Support/Telegram Desktop/tdata'),
            # 便携版
            os.path.join(os.path.dirname(self.telegram路径), 'tdata'),
        ]

    def 搜索API凭证(self, tdata路径):
        """在配置文件中搜索API凭证"""
        api_id = None
        api_hash = None

        配置文件模式 = ['config', 'config1', 'configs', 'key_datas']

        for 模式 in 配置文件模式:
            配置文件 = os.path.join(tdata路径, 模式)
            if os.path.exists(配置文件):
                self.日志(f"找到配置文件: {配置文件}")

                try:
                    with open(配置文件, 'rb') as 文件:
                        内容 = 文件.read()

                    # 尝试多种匹配模式
                    匹配结果 = self.多种匹配模式(内容)

                    if 匹配结果['api_id']:
                        api_id = 匹配结果['api_id']
                    if 匹配结果['api_hash']:
                        api_hash = 匹配结果['api_hash']

                    if api_id and api_hash:
                        break

                except Exception as 错误:
                    self.日志(f"读取配置文件错误: {错误}")
                    continue

        return api_id, api_hash

    def 多种匹配模式(self, 内容):
        """使用多种正则表达式匹配API凭证"""
        结果 = {'api_id': None, 'api_hash': None}

        # 匹配API ID的模式
        id模式列表 = [
            rb'api_id[^\d]*(\d+)',
            rb'"api_id"\s*:\s*(\d+)',
            rb'apiId[^\d]*(\d+)',
            rb'\x00api_id\x00[^\d]*(\d+)',
        ]

        # 匹配API Hash的模式
        hash模式列表 = [
            rb'api_hash[^\w]*([a-fA-F0-9]{32})',
            rb'"api_hash"\s*:\s*"([a-fA-F0-9]{32})"',
            rb'apiHash[^\w]*([a-fA-F0-9]{32})',
            rb'\x00api_hash\x00[^\w]*([a-fA-F0-9]{32})',
        ]

        # 尝试匹配API ID
        for 模式 in id模式列表:
            匹配 = re.search(模式, 内容, re.IGNORECASE)
            if 匹配:
                结果['api_id'] = 匹配.group(1).decode()
                self.日志(f"匹配到API ID: {结果['api_id']}")
                break

        # 尝试匹配API Hash
        for 模式 in hash模式列表:
            匹配 = re.search(模式, 内容, re.IGNORECASE)
            if 匹配:
                结果['api_hash'] = 匹配.group(1).decode()
                self.日志(f"匹配到API Hash: {结果['api_hash']}")
                break

        return 结果

    def 手动输入凭证(self):
        """打开手动输入凭证的窗口"""
        手动窗口 = tk.Toplevel(self.root)
        手动窗口.title("手动输入API凭证")
        手动窗口.geometry("500x350")
        手动窗口.transient(self.root)
        手动窗口.grab_set()

        # 居中显示
        手动窗口.update_idletasks()
        宽度 = 手动窗口.winfo_width()
        高度 = 手动窗口.winfo_height()
        x坐标 = (手动窗口.winfo_screenwidth() // 2) - (宽度 // 2)
        y坐标 = (手动窗口.winfo_screenheight() // 2) - (高度 // 2)
        手动窗口.geometry(f'{宽度}x{高度}+{x坐标}+{y坐标}')

        # 主框架
        主框架 = ttk.Frame(手动窗口, padding="20")
        主框架.pack(fill=tk.BOTH, expand=True)

        tk.Label(
            主框架,
            text="手动输入API凭证",
            font=("微软雅黑", 14, "bold")
        ).pack(pady=(0, 20))

        # API ID输入
        id框架 = ttk.Frame(主框架)
        id框架.pack(fill=tk.X, pady=10)

        tk.Label(id框架, text="API ID:", font=("微软雅黑", 11)).pack(side=tk.LEFT)
        id输入框 = ttk.Entry(id框架, font=("Consolas", 11))
        id输入框.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(10, 0))
        id输入框.focus()

        # API Hash输入
        hash框架 = ttk.Frame(主框架)
        hash框架.pack(fill=tk.X, pady=10)

        tk.Label(hash框架, text="API Hash:", font=("微软雅黑", 11)).pack(side=tk.LEFT)
        hash输入框 = ttk.Entry(hash框架, font=("Consolas", 11))
        hash输入框.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(10, 0))

        # 帮助文本
        帮助文本 = tk.Text(
            主框架,
            height=5,
            font=("微软雅黑", 9),
            bg='#f8f9fa',
            relief=tk.FLAT
        )
        帮助文本.pack(fill=tk.X, pady=(20, 10))
        帮助文本.insert(tk.END, "如何获取API凭证：\n")
        帮助文本.insert(tk.END, "1. 访问 https://my.telegram.org\n")
        帮助文本.insert(tk.END, "2. 使用手机号登录\n")
        帮助文本.insert(tk.END, "3. 进入 'API Development Tools'\n")
        帮助文本.insert(tk.END, "4. 创建应用并复制API ID和Hash")
        帮助文本.config(state=tk.DISABLED)

        def 保存凭证():
            api_id = id输入框.get().strip()
            api_hash = hash输入框.get().strip()

            if not api_id or not api_hash:
                messagebox.showerror("错误", "请输入完整的API ID和Hash！")
                return

            if not api_id.isdigit():
                messagebox.showerror("错误", "API ID必须是数字！")
                return

            self.api_id变量.set(api_id)
            self.api_hash变量.set(api_hash)
            self.状态标签.config(text="✅ 手动输入凭证已保存！", fg='#27ae60')
            self.日志(f"\n✅ 手动输入凭证已保存")
            self.日志(f"API ID: {api_id}")
            self.日志(f"API Hash: {api_hash}")

            手动窗口.destroy()

        # 按钮框架
        按钮框架 = ttk.Frame(主框架)
        按钮框架.pack(pady=20)

        ttk.Button(
            按钮框架,
            text="保存",
            command=保存凭证
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            按钮框架,
            text="取消",
            command=手动窗口.destroy
        ).pack(side=tk.LEFT, padx=5)

    def 复制API_ID(self):
        """复制API ID到剪贴板"""
        if self.api_id变量.get():
            self.root.clipboard_clear()
            self.root.clipboard_append(self.api_id变量.get())
            self.状态标签.config(text="✅ API ID已复制到剪贴板", fg='#3498db')
            self.日志("API ID已复制到剪贴板")

    def 复制API_Hash(self):
        """复制API Hash到剪贴板"""
        if self.api_hash变量.get():
            self.root.clipboard_clear()
            self.root.clipboard_append(self.api_hash变量.get())
            self.状态标签.config(text="✅ API Hash已复制到剪贴板", fg='#3498db')
            self.日志("API Hash已复制到剪贴板")

    def 复制全部(self):
        """复制全部凭证到剪贴板"""
        if self.api_id变量.get() and self.api_hash变量.get():
            文本 = f"API ID: {self.api_id变量.get()}\nAPI Hash: {self.api_hash变量.get()}"
            self.root.clipboard_clear()
            self.root.clipboard_append(文本)
            self.状态标签.config(text="✅ 全部凭证已复制到剪贴板", fg='#3498db')
            self.日志("全部凭证已复制到剪贴板")

    def 清理日志(self):
        """清理日志文本框"""
        self.日志文本框.delete(1.0, tk.END)
        self.日志("日志已清理")


def 检查依赖():
    """检查并安装必要的依赖"""
    try:
        import psutil
        return True
    except ImportError:
        print("正在安装必要的依赖包...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "psutil"])
            import psutil
            print("✅ 依赖安装成功！")
            return True
        except Exception as 错误:
            print(f"❌ 依赖安装失败: {错误}")
            return False


def 主程序():
    """主程序入口"""
    # 检查依赖
    if not 检查依赖():
        print("请手动安装依赖：pip install psutil")
        input("按Enter键退出...")
        return

    # 创建主窗口
    主窗口 = tk.Tk()

    # 设置窗口图标（可选）
    try:
        主窗口.iconbitmap('telegram.ico')
    except:
        pass

    # 创建应用程序实例
    应用 = TelegramAPI提取器(主窗口)

    # 运行主循环
    主窗口.mainloop()


if __name__ == "__main__":
    主程序()