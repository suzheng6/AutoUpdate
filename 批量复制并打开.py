import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import subprocess
import platform


class FileBatchCopier:
    def __init__(self, root):
        self.root = root
        self.root.title("批量复制并打开文件工具")
        self.root.geometry("600x800")

        # 设置样式
        self.setup_styles()

        # 创建UI元素
        self.create_widgets()

        # 存储选择的文件路径和目标文件夹路径
        self.source_file_path = ""
        self.target_folder_path = ""

    def setup_styles(self):
        """设置控件样式"""
        style = ttk.Style()
        style.configure("Title.TLabel", font=("Arial", 16, "bold"))
        style.configure("Header.TLabel", font=("Arial", 11, "bold"))
        style.configure("Green.TButton", font=("Arial", 10))

    def create_widgets(self):
        """创建所有界面控件"""

        # 标题
        title_label = ttk.Label(self.root, text="批量复制并打开文件工具", style="Title.TLabel")
        title_label.pack(pady=20)

        # 源文件选择部分
        source_frame = ttk.LabelFrame(self.root, text="选择要复制的文件", padding=10)
        source_frame.pack(fill="x", padx=20, pady=10)

        self.source_label = ttk.Label(source_frame, text="未选择文件", wraplength=500)
        self.source_label.pack(fill="x", pady=(0, 10))

        source_btn = ttk.Button(source_frame, text="选择文件", command=self.select_source_file)
        source_btn.pack()

        # 目标文件夹选择部分
        target_frame = ttk.LabelFrame(self.root, text="选择目标文件夹（将复制到所有子文件夹）", padding=10)
        target_frame.pack(fill="x", padx=20, pady=10)

        self.target_label = ttk.Label(target_frame, text="未选择文件夹", wraplength=500)
        self.target_label.pack(fill="x", pady=(0, 10))

        target_btn = ttk.Button(target_frame, text="选择文件夹", command=self.select_target_folder)
        target_btn.pack()

        # 选项部分
        options_frame = ttk.LabelFrame(self.root, text="选项", padding=10)
        options_frame.pack(fill="x", padx=20, pady=10)

        # 复制后是否打开文件
        self.open_var = tk.BooleanVar(value=True)
        open_check = ttk.Checkbutton(options_frame, text="复制后打开文件", variable=self.open_var)
        open_check.pack(anchor="w")

        # 是否覆盖已存在的文件
        self.overwrite_var = tk.BooleanVar(value=False)
        overwrite_check = ttk.Checkbutton(options_frame, text="覆盖已存在的文件", variable=self.overwrite_var)
        overwrite_check.pack(anchor="w", pady=(5, 0))

        # 日志输出
        log_frame = ttk.LabelFrame(self.root, text="操作日志", padding=10)
        log_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # 添加滚动条
        log_scrollbar = ttk.Scrollbar(log_frame)
        log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.log_text = tk.Text(log_frame, height=8, yscrollcommand=log_scrollbar.set, wrap=tk.WORD)
        self.log_text.pack(fill="both", expand=True)
        log_scrollbar.config(command=self.log_text.yview)

        # 按钮部分
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=15)

        self.copy_btn = ttk.Button(button_frame, text="开始复制", command=self.start_copying, style="Green.TButton")
        self.copy_btn.pack(side=tk.LEFT, padx=10)

        clear_btn = ttk.Button(button_frame, text="清空日志", command=self.clear_log)
        clear_btn.pack(side=tk.LEFT, padx=10)

        exit_btn = ttk.Button(button_frame, text="退出", command=self.root.quit)
        exit_btn.pack(side=tk.LEFT, padx=10)

    def select_source_file(self):
        """选择源文件"""
        file_path = filedialog.askopenfilename(
            title="选择要复制的文件",
            filetypes=[("所有文件", "*.*"), ("文本文件", "*.txt"), ("PDF文件", "*.pdf"),
                       ("Word文档", "*.docx"), ("Excel文件", "*.xlsx")]
        )

        if file_path:
            self.source_file_path = file_path
            file_name = os.path.basename(file_path)
            self.source_label.config(text=f"已选择: {file_name}\n路径: {file_path}")
            self.log_message(f"选择了源文件: {file_path}")

    def select_target_folder(self):
        """选择目标文件夹"""
        folder_path = filedialog.askdirectory(title="选择目标文件夹")

        if folder_path:
            self.target_folder_path = folder_path
            self.target_label.config(text=f"已选择: {folder_path}")
            self.log_message(f"选择了目标文件夹: {folder_path}")

    def start_copying(self):
        """开始复制文件到所有子文件夹"""
        if not self.source_file_path:
            messagebox.showerror("错误", "请先选择要复制的文件！")
            return

        if not self.target_folder_path:
            messagebox.showerror("错误", "请先选择目标文件夹！")
            return

        if not os.path.exists(self.target_folder_path):
            messagebox.showerror("错误", "目标文件夹不存在！")
            return

        # 获取所有子文件夹
        subfolders = []
        for item in os.listdir(self.target_folder_path):
            item_path = os.path.join(self.target_folder_path, item)
            if os.path.isdir(item_path):
                subfolders.append(item_path)

        if not subfolders:
            messagebox.showwarning("警告", "目标文件夹中没有子文件夹！")
            return

        # 确认操作
        confirm_msg = f"确认将文件复制到 {len(subfolders)} 个子文件夹吗？"
        if not messagebox.askyesno("确认", confirm_msg):
            return

        # 开始复制
        self.copy_btn.config(state="disabled")
        self.log_message(f"开始复制文件到 {len(subfolders)} 个子文件夹...")

        success_count = 0
        fail_count = 0

        for folder in subfolders:
            try:
                # 构建目标路径
                file_name = os.path.basename(self.source_file_path)
                dest_path = os.path.join(folder, file_name)

                # 检查文件是否已存在
                if os.path.exists(dest_path) and not self.overwrite_var.get():
                    self.log_message(f"跳过（文件已存在）: {folder}")
                    fail_count += 1
                    continue

                # 复制文件
                shutil.copy2(self.source_file_path, dest_path)
                success_count += 1
                self.log_message(f"复制成功: {folder}")

                # 如果需要，打开文件
                if self.open_var.get():
                    self.open_file(dest_path)

            except Exception as e:
                fail_count += 1
                self.log_message(f"复制失败 {folder}: {str(e)}")

        # 显示结果
        result_msg = f"复制完成！\n成功: {success_count} 个，失败: {fail_count} 个"
        self.log_message(result_msg)
        messagebox.showinfo("完成", result_msg)

        self.copy_btn.config(state="normal")

    def open_file(self, file_path):
        """使用系统默认程序打开文件"""
        try:
            system = platform.system()
            if system == "Windows":
                os.startfile(file_path)
            elif system == "Darwin":  # macOS
                subprocess.call(["open", file_path])
            else:  # Linux
                subprocess.call(["xdg-open", file_path])
            self.log_message(f"已打开: {file_path}")
        except Exception as e:
            self.log_message(f"打开文件失败 {file_path}: {str(e)}")

    def log_message(self, message):
        """添加消息到日志"""
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.root.update()

    def clear_log(self):
        """清空日志"""
        self.log_text.delete(1.0, tk.END)


def main():
    root = tk.Tk()
    app = FileBatchCopier(root)
    root.mainloop()


if __name__ == "__main__":
    main()