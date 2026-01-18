# 中文宏录制器（鼠标 + 键盘录制与回放）
# 功能：
# - 录制鼠标移动、点击、滚动
# - 录制键盘按键按下与松开
# - 自动记录每一步延迟
# - 可编辑脚本（修改坐标、键值、延迟）
# - 可保存、加载多个脚本（JSON）
# - 支持循环回放
# - 全中文界面 + 提示

import json
import threading
import time
import tkinter as tk
from tkinter import ttk, filedialog, simpledialog, messagebox

try:
    from pynput import mouse, keyboard
    from pynput.mouse import Button, Controller as MouseController
    from pynput.keyboard import Key, Controller as KeyboardController
except Exception as e:
    raise SystemExit("缺少必要依赖 pynput，请先运行： pip install pynput\n" + str(e))


# 每个动作的数据结构说明：
# {
#     "type": "move" | "click" | "scroll" | "key_down" | "key_up" | "wait",
#     "x": int, "y": int,                       # 鼠标坐标
#     "button": "left"/"right"/"middle",        # 鼠标按键
#     "count": 1,                               # 点击次数
#     "dx": int, "dy": int,                     # 滚轮滚动
#     "key": "a" 或 "Key.enter",                # 键盘按键
#     "delay": float                            # 当前动作之后的延迟
# }


class MacroRecorderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("中文鼠标键盘录制器")
        self.scripts = {}        # 脚本名称 → 动作列表
        self.current_script_name = "未命名脚本"
        self.current_actions = []
        self.recording = False
        self.last_time = None

        self.mouse_controller = MouseController()
        self.keyboard_controller = KeyboardController()

        self.mouse_listener = None
        self.keyboard_listener = None

        self.setup_ui()


    # =======================
    #     构建中文界面
    # =======================
    def setup_ui(self):
        frm = ttk.Frame(self.root, padding=10)
        frm.pack(fill="both", expand=True)

        # 顶部按钮
        top = ttk.Frame(frm)
        top.pack(fill="x", pady=5)

        ttk.Button(top, text="新建脚本", command=self.new_script).pack(side="left")
        ttk.Button(top, text="加载脚本", command=self.load_script).pack(side="left")
        ttk.Button(top, text="保存脚本", command=self.save_script).pack(side="left")

        ttk.Label(top, text="脚本名称：").pack(side="left", padx=(15, 3))
        self.name_var = tk.StringVar(value=self.current_script_name)
        ttk.Entry(top, textvariable=self.name_var, width=25).pack(side="left")

        # 中间录制区
        mid = ttk.Frame(frm)
        mid.pack(fill="x", pady=10)

        rec_frame = ttk.LabelFrame(mid, text="录制 / 播放控制（Recording & Playback）")
        rec_frame.pack(side="left", fill="y", padx=5)

        self.record_btn = ttk.Button(rec_frame, text="开始录制（Start Record）", command=self.start_record)
        self.record_btn.pack(fill="x")

        ttk.Button(rec_frame, text="停止录制（Stop）", command=self.stop_record).pack(fill="x", pady=5)

        # 播放准备时间
        ttk.Label(rec_frame, text="播放前准备秒数：").pack()
        self.prepare_var = tk.DoubleVar(value=1.5)
        ttk.Entry(rec_frame, textvariable=self.prepare_var, width=8).pack()

        ttk.Button(rec_frame, text="播放一次", command=lambda: self.play_script(loop=1)).pack(fill="x", pady=5)

        loop_frame = ttk.Frame(rec_frame)
        loop_frame.pack(fill="x")

        ttk.Label(loop_frame, text="循环次数：").pack(side="left")
        self.loop_var = tk.IntVar(value=3)
        ttk.Entry(loop_frame, textvariable=self.loop_var, width=6).pack(side="left", padx=5)

        ttk.Button(rec_frame, text="循环播放", command=lambda: self.play_script(loop=self.loop_var.get())).pack(fill="x", pady=5)

        # 编辑控制区
        edit_frame = ttk.LabelFrame(mid, text="脚本编辑")
        edit_frame.pack(side="left", fill="both", expand=True, padx=5)

        btns = ttk.Frame(edit_frame)
        btns.pack(fill="x")

        ttk.Button(btns, text="插入等待（秒）", command=self.insert_wait).pack(side="left")
        ttk.Button(btns, text="删除选中动作", command=self.delete_selected).pack(side="left", padx=5)
        ttk.Button(btns, text="编辑选中动作", command=self.edit_selected).pack(side="left", padx=5)

        # 动作列表表格
        cols = ("idx", "type", "desc", "delay")
        self.tree = ttk.Treeview(edit_frame, columns=cols, show="headings", selectmode="browse")

        self.tree.heading("idx", text="编号")
        self.tree.heading("type", text="动作类型")
        self.tree.heading("desc", text="动作说明")
        self.tree.heading("delay", text="延迟（秒）")

        self.tree.column("idx", width=60)
        self.tree.column("type", width=120)
        self.tree.column("desc", width=420)
        self.tree.column("delay", width=100)

        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<Double-1>", lambda e: self.edit_selected())

        # 状态栏
        status_frame = ttk.Frame(frm)
        status_frame.pack(fill="x", pady=(8, 0))

        self.status_var = tk.StringVar(value="就绪")
        ttk.Label(status_frame, textvariable=self.status_var).pack(side="left")

    # =======================
    #     状态显示
    # =======================
    def set_status(self, msg):
        self.status_var.set(msg)
        self.root.update_idletasks()
    # =======================
    #   新建 / 保存 / 加载脚本
    # =======================
    def new_script(self):
        name = simpledialog.askstring("新建脚本", "请输入脚本名称：", initialvalue="未命名脚本")
        if not name:
            return
        self.current_script_name = name
        self.name_var.set(name)
        self.current_actions = []
        self.scripts[name] = self.current_actions
        self.refresh_tree()
        self.set_status("已创建新脚本")

    def save_script(self):
        name = self.name_var.get().strip() or "未命名脚本"
        self.scripts[name] = self.current_actions

        path = filedialog.asksaveasfilename(
            title="保存脚本",
            defaultextension=".json",
            filetypes=[("JSON 文件", "*.json")]
        )
        if not path:
            return

        with open(path, "w", encoding="utf-8") as f:
            json.dump({"name": name, "actions": self.current_actions}, f, ensure_ascii=False, indent=2)

        self.set_status(f"脚本已保存到：{path}")

    def load_script(self):
        path = filedialog.askopenfilename(
            title="加载脚本",
            filetypes=[("JSON 文件", "*.json")]
        )
        if not path:
            return

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        name = data.get("name", "导入脚本")
        actions = data.get("actions", [])

        self.scripts[name] = actions
        self.current_script_name = name
        self.name_var.set(name)
        self.current_actions = actions

        self.refresh_tree()
        self.set_status(f"已加载脚本：{name}")


    # =======================
    #      列表刷新
    # =======================
    def refresh_tree(self):
        for i in self.tree.get_children():
            self.tree.delete(i)

        for idx, act in enumerate(self.current_actions):
            desc = self.action_description(act)
            delay = f"{act.get('delay', 0):.3f}"

            self.tree.insert("", "end", iid=str(idx), values=(
                idx,
                act["type"],
                desc,
                delay
            ))


    # =======================
    #      动作说明中文
    # =======================
    def action_description(self, act):
        t = act["type"]

        if t == "move":
            return f"鼠标移动到 ({act.get('x')}, {act.get('y')})"
        if t == "click":
            return f"鼠标 {act.get('button')} 键点击于 ({act.get('x')}, {act.get('y')}) ×{act.get('count', 1)}"
        if t == "scroll":
            return f"鼠标滚动 dx={act.get('dx')} dy={act.get('dy')}"
        if t == "key_down":
            return f"按下键：{act.get('key')}"
        if t == "key_up":
            return f"松开键：{act.get('key')}"
        if t == "wait":
            return f"等待 {act.get('delay', 0):.3f} 秒"

        return json.dumps(act)


    # =======================
    #        开始录制
    # =======================
    def start_record(self):
        if self.recording:
            return

        self.recording = True
        self.current_actions = []
        self.scripts[self.current_script_name] = self.current_actions

        self.last_time = time.time()
        self.set_status("正在录制… 请执行鼠标与键盘操作")

        # 启动监听器
        self.mouse_listener = mouse.Listener(
            on_move=self.on_move,
            on_click=self.on_click,
            on_scroll=self.on_scroll
        )
        self.keyboard_listener = keyboard.Listener(
            on_press=self.on_key_press,
            on_release=self.on_key_release
        )

        self.mouse_listener.start()
        self.keyboard_listener.start()


    # =======================
    #        停止录制
    # =======================
    def stop_record(self):
        if not self.recording:
            return

        self.recording = False

        if self.mouse_listener:
            self.mouse_listener.stop()
            self.mouse_listener = None

        if self.keyboard_listener:
            self.keyboard_listener.stop()
            self.keyboard_listener = None

        self.set_status("录制已停止")
        self.refresh_tree()
    # =======================
    #   录制动作写入列表
    # =======================
    def record_event(self, act):
        if not self.recording:
            return

        now = time.time()
        delay = now - self.last_time if self.last_time else 0
        self.last_time = now

        # 把延迟记在前一个动作的 delay 上
        if self.current_actions:
            self.current_actions[-1]["delay"] = self.current_actions[-1].get("delay", 0) + delay
        else:
            # 第一个动作前可能存在等待，也记录（可选）
            if delay > 0:
                self.current_actions.append({"type": "wait", "delay": delay})

        act["delay"] = 0
        self.current_actions.append(act)
        self.refresh_tree()


    # =======================
    #    鼠标事件回调
    # =======================
    def on_move(self, x, y):
        if not self.recording:
            return

        # 为减少大量 move 事件：如果前一个是 move，则直接覆盖
        last = self.current_actions[-1] if self.current_actions else None
        if last and last["type"] == "move":
            last["x"], last["y"] = int(x), int(y)
            return

        self.record_event({"type": "move", "x": int(x), "y": int(y)})

    def on_click(self, x, y, button, pressed):
        if not self.recording or not pressed:
            return

        btn = (
            "left" if button == Button.left
            else "right" if button == Button.right
            else "middle"
        )

        self.record_event({
            "type": "click",
            "x": int(x),
            "y": int(y),
            "button": btn,
            "count": 1
        })

    def on_scroll(self, x, y, dx, dy):
        if not self.recording:
            return

        self.record_event({
            "type": "scroll",
            "dx": int(dx),
            "dy": int(dy)
        })


    # =======================
    #    键盘事件回调
    # =======================
    def on_key_press(self, key):
        if not self.recording:
            return
        k = self.key_to_str(key)
        self.record_event({"type": "key_down", "key": k})

    def on_key_release(self, key):
        if not self.recording:
            return
        k = self.key_to_str(key)
        self.record_event({"type": "key_up", "key": k})

    def key_to_str(self, key):
        # 特殊键（如 Key.enter）
        if isinstance(key, Key):
            return f"Key.{key.name}"

        try:
            return key.char
        except:
            return str(key)


    # =======================
    #      脚本播放
    # =======================
    def play_script(self, loop=1):
        if not self.current_actions:
            messagebox.showinfo("提示", "当前脚本为空，无法播放。")
            return

        try:
            prepare = float(self.prepare_var.get())
        except:
            prepare = 1.5

        t = threading.Thread(target=self._play_thread, args=(loop, prepare), daemon=True)
        t.start()

    def _play_thread(self, loop, prepare):
        self.set_status(f"将在 {prepare:.1f} 秒后开始播放，请切换到目标窗口…")
        time.sleep(max(0, prepare))

        self.set_status("正在播放脚本…")

        for r in range(loop):
            for act in self.current_actions:
                atype = act["type"]

                try:
                    if atype == "move":
                        self.mouse_controller.position = (act["x"], act["y"])

                    elif atype == "click":
                        self.mouse_controller.position = (act["x"], act["y"])
                        btn = Button.left if act["button"] == "left" else (
                            Button.right if act["button"] == "right" else Button.middle
                        )
                        for _ in range(act.get("count", 1)):
                            self.mouse_controller.click(btn)

                    elif atype == "scroll":
                        self.mouse_controller.scroll(
                            act.get("dx", 0),
                            act.get("dy", 0)
                        )

                    elif atype == "key_down":
                        self._press_key(act["key"])

                    elif atype == "key_up":
                        self._release_key(act["key"])

                    elif atype == "wait":
                        pass

                except Exception as e:
                    print("播放动作发生错误：", e)

                # 延迟执行
                delay = float(act.get("delay", 0))
                end_time = time.time() + delay
                while time.time() < end_time:
                    time.sleep(min(0.03, end_time - time.time()))

        self.set_status("脚本播放完成。")


    # =======================
    #     键盘操作执行
    # =======================
    def _press_key(self, k):
        if k.startswith("Key."):
            name = k.split(".", 1)[1]
            try:
                keyobj = getattr(Key, name)
                self.keyboard_controller.press(keyobj)
            except:
                pass
        else:
            try:
                self.keyboard_controller.press(k)
            except:
                pass

    def _release_key(self, k):
        if k.startswith("Key."):
            name = k.split(".", 1)[1]
            try:
                keyobj = getattr(Key, name)
                self.keyboard_controller.release(keyobj)
            except:
                pass
        else:
            try:
                self.keyboard_controller.release(k)
            except:
                pass
    # =======================
    #      插入等待动作
    # =======================
    def insert_wait(self):
        idx = self._get_selected_index_or_end()

        val = simpledialog.askfloat("插入等待", "请输入等待秒数：", minvalue=0.0, initialvalue=1.0)
        if val is None:
            return

        act = {"type": "wait", "delay": float(val)}
        self.current_actions.insert(idx, act)
        self.refresh_tree()
        self.set_status("已插入等待动作")


    # =======================
    #      删除动作
    # =======================
    def delete_selected(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("提示", "请先选择一个动作再删除。")
            return

        idx = int(sel[0])
        del self.current_actions[idx]
        self.refresh_tree()
        self.set_status("动作已删除")


    # =======================
    #      编辑动作
    # =======================
    def edit_selected(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("提示", "请先选择一个动作再编辑。")
            return

        idx = int(sel[0])
        act = self.current_actions[idx]

        dialog = ActionEditDialog(self.root, act)
        self.root.wait_window(dialog.top)

        if dialog.updated:
            self.current_actions[idx] = dialog.act
            self.refresh_tree()
            self.set_status("动作已更新")


    # 返回选择的行号，如未选则返回末尾
    def _get_selected_index_or_end(self):
        sel = self.tree.selection()
        if not sel:
            return len(self.current_actions)
        return int(sel[0])



# =======================
#     动作编辑窗口
# =======================
class ActionEditDialog:
    def __init__(self, parent, act):
        self.top = tk.Toplevel(parent)
        self.top.title("编辑动作")
        self.act = dict(act)
        self.updated = False
        self.build()


    def build(self):
        frm = ttk.Frame(self.top, padding=12)
        frm.pack(fill="both", expand=True)

        ttk.Label(frm, text="动作类型（move/click/scroll/key_down/key_up/wait）：").grid(row=0, column=0, sticky="w")
        self.type_var = tk.StringVar(value=self.act.get("type"))
        ttk.Entry(frm, textvariable=self.type_var).grid(row=0, column=1, sticky="we")

        ttk.Label(frm, text="动作字段（以 key=value, key=value 形式填写）：").grid(row=1, column=0, sticky="w", pady=(8,0))
        self.fields_var = tk.StringVar(value=self._fields_to_str(self.act))
        ttk.Entry(frm, textvariable=self.fields_var, width=60).grid(row=2, column=0, columnspan=2, sticky="we")

        ttk.Label(frm, text="延迟（秒）：").grid(row=3, column=0, sticky="w", pady=(8,0))
        self.delay_var = tk.DoubleVar(value=float(self.act.get("delay", 0)))
        ttk.Entry(frm, textvariable=self.delay_var).grid(row=3, column=1, sticky="we")

        btns = ttk.Frame(frm)
        btns.grid(row=4, column=0, columnspan=2, pady=10)

        ttk.Button(btns, text="确定", command=self.on_ok).pack(side="left", padx=4)
        ttk.Button(btns, text="取消", command=self.top.destroy).pack(side="left", padx=4)


    def _fields_to_str(self, act):
        pairs = []
        for k, v in act.items():
            if k not in ("type", "delay"):
                pairs.append(f"{k}={v}")
        return ", ".join(pairs)


    def on_ok(self):
        self.act["type"] = self.type_var.get().strip()

        # 解析字段
        fs = self.fields_var.get().strip()
        if fs:
            parts = [p.strip() for p in fs.split(",") if p.strip()]
            for p in parts:
                if "=" in p:
                    k, v = p.split("=", 1)
                    k = k.strip()
                    v = v.strip()

                    # 自动数值化
                    if v.isdigit():
                        v = int(v)
                    else:
                        try:
                            v = float(v)
                        except:
                            pass

                    self.act[k] = v

        self.act["delay"] = float(self.delay_var.get())

        self.updated = True
        self.top.destroy()



# =======================
#       程序入口
# =======================
def main():
    root = tk.Tk()
    app = MacroRecorderApp(root)
    root.geometry("1000x650")
    root.mainloop()


if __name__ == "__main__":
    main()
