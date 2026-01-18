import sys
import os
import io
import requests
import pandas as pd
from PyQt5 import QtWidgets
from difflib import get_close_matches
JATI_TO_VARNA = {
    "brahmin": [
        "brahmin","brahman","iyer","iyengar","smartha","saraswat",
        "gaur","kanyakubja","maithil","bhumihar","joshi","pandey",
        "mishra","tiwari","shukla","upadhyay","acharya",
        "chatterjee","mukherjee","banerjee","bhattacharya"
    ],
    "kshatriya": [
        "kshatriya","rajput","thakur","rana","chauhan","sisodia",
        "rathore","jadeja","solanki","maratha","jat","nair"
    ],
    "vaishya": [
        "vaishya","baniya","agarwal","agrawal","gupta","mahajan",
        "seth","jain","oswal","porwal","khandelwal","maheshwari",
        "marwari","modi","mittal","jindal","chettiar"
    ],
    "obc": [
        "obc","yadav","kurmi","patel","patidar","reddy","vokkaliga",
        "lingayat","gounder","thevar","nadar","mudaliar","naidu"
    ],
    "sc": [
        "sc","scheduled caste","dalit","chamar","jatav","mahar",
        "madiga","mala","pasi","dhobi","bhangi"
    ],
    "st": [
        "st","scheduled tribe","adivasi","gond","santhal","munda",
        "oraon","bhil","meena","koya","irula","toda"
    ]
}
JATI_TO_VARNA = {
    "brahmin": [
        "brahmin","brahman","iyer","iyengar","smartha","saraswat",
        "gaur","kanyakubja","maithil","bhumihar","joshi","pandit",
        "purohit","acharya","upadhyay","trivedi","dwivedi",
        "shukla","mishra","pandey","tiwari","pathak",
        "kulkarni","bhat","bhatt","bhattacharya",
        "chatterjee","mukherjee","banerjee","chakraborty"
    ],
    "kshatriya": [
        "kshatriya","rajput","thakur","rana","rao",
        "chauhan","sisodia","rathore","jadeja","solanki",
        "maratha","kunbi","jat","jaat","nair","menon"
    ],
    "vaishya": [
        "vaishya","baniya","banik","agarwal","agrawal",
        "gupta","goyal","goenka","mahajan","seth",
        "jain","oswal","porwal","khandelwal","maheshwari",
        "marwari","modi","mittal","jindal","singhal",
        "chettiar","komati","arya vysya"
    ],
    "obc": [
        "obc","sebc","backward",
        "yadav","ahir","kurmi","koeri",
        "patel","patidar","kadva","leva",
        "reddy","kapu","telaga",
        "vokkaliga","gowda","lingayat","veerashaiva",
        "gounder","vellalar","thevar","kallar","maravar",
        "nadar","mudaliar","naidu","koli","mali","kumbhar","saini"
    ],
    "sc": [
        "sc","scheduled caste","dalit",
        "chamar","jatav","valmiki","balmiki",
        "mahar","madiga","mala","pasi","dusadh",
        "dhobi","bhangi","mehtar","arunthathiyar","paraiyar"
    ],
    "st": [
        "st","scheduled tribe","adivasi",
        "gond","bhil","meena","santhal","santal",
        "munda","oraon","ho","koya","toda","irula",
        "khasi","garo","jarawa","onge"
    ]
}


def normalize_caste(raw: str) -> str:
    if not raw:
        return ""

    s = raw.lower()
    for x in ["caste","community","(",")","-","_"]:
        s = s.replace(x, " ")
    s = " ".join(s.split())

    for varna, keywords in JATI_TO_VARNA.items():
        for k in keywords:
            if k in s:
                return varna

    return ""



# ===================== 种姓解释库 =====================
CASTE_INFO = {
    "brahmin": {
        "varna": "Brahmin（婆罗门）",
        "tier": "传统知识与教育阶层",
        "identity": [
            "学者 / 教师",
            "宗教人士",
            "行政与文职人员",
            "城市中产 / 上层中产"
        ],
        "summary": "传统上与教育、宗教和知识阶层相关，现代社会中多分布于城市中产及以上阶层。",
        "confidence": "高"
    },
    "kshatriya": {
        "varna": "Kshatriya（刹帝利）",
        "tier": "传统统治与武士阶层",
        "identity": [
            "军警人员",
            "政治与行政领导",
            "土地拥有者"
        ],
        "summary": "历史上负责统治和防卫，现代多进入政治、军警或商业领域。",
        "confidence": "高"
    },
    "vaishya": {
        "varna": "Vaishya（吠舍）",
        "tier": "传统商贸阶层",
        "identity": [
            "商人",
            "贸易与金融",
            "企业经营者"
        ],
        "summary": "以商业和贸易为主，在印度商业和中小企业群体中占比高。",
        "confidence": "高"
    },
    "obc": {
        "varna": "OBC（其他落后阶层）",
        "tier": "政府政策分类阶层",
        "identity": [
            "农业",
            "地方商业",
            "技术与服务行业"
        ],
        "summary": "政府统计分类，涵盖多个传统种姓，社会地位差异较大。",
        "confidence": "中"
    }
}

# ===================== 数据源 =====================
CSV_RAW_URL = "https://raw.githubusercontent.com/merishnaSuwal/indian_surnames_data/master/indian_caste_data.csv"
CACHE_FILE = os.path.join(os.path.expanduser("~"), ".india_caste_db.csv")


def download_dataset():
    if os.path.exists(CACHE_FILE):
        try:
            return pd.read_csv(CACHE_FILE, dtype=str)
        except Exception:
            os.remove(CACHE_FILE)

    r = requests.get(CSV_RAW_URL, timeout=15)
    r.raise_for_status()
    df = pd.read_csv(io.StringIO(r.text), dtype=str)
    df.to_csv(CACHE_FILE, index=False)
    return df


def extract_surname(name: str) -> str:
    parts = name.strip().split()
    return parts[-1] if parts else ""


# ===================== 主窗口 =====================
class CasteLookupApp(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("印度姓氏 → 种姓 / 阶级 查询")
        self.resize(900, 520)

        # ---------- UI ----------
        self.input_line = QtWidgets.QLineEdit()
        self.input_line.setPlaceholderText("输入姓名或姓氏，如：Rahul Sharma")

        self.search_btn = QtWidgets.QPushButton("查询")

        self.result_area = QtWidgets.QTextEdit()
        self.result_area.setReadOnly(True)

        self.explain_area = QtWidgets.QTextEdit()
        self.explain_area.setReadOnly(True)

        self.status_label = QtWidgets.QLabel("正在加载数据库…")

        # ---------- 布局（只用一种 layout） ----------
        self.layout = QtWidgets.QVBoxLayout(self)

        top = QtWidgets.QHBoxLayout()
        top.addWidget(self.input_line)
        top.addWidget(self.search_btn)
        self.layout.addLayout(top)

        mid = QtWidgets.QHBoxLayout()
        mid.addWidget(self.result_area)
        mid.addWidget(self.explain_area)
        self.layout.addLayout(mid)

        self.layout.addWidget(self.status_label)

        # ---------- 事件 ----------
        self.search_btn.clicked.connect(self.on_search)
        self.input_line.returnPressed.connect(self.on_search)

        # ---------- 数据 ----------
        self.df = pd.DataFrame()
        self.load_data()

    def load_data(self):
        try:
            self.df = download_dataset().fillna("")
            self.status_label.setText(f"数据库加载完成（{len(self.df)} 条记录）")
        except Exception as e:
            self.status_label.setText(f"数据库加载失败：{e}")

    def lookup_surname(self, surname):
        if self.df.empty:
            return []

        key = surname.lower()
        concat = self.df.astype(str).agg(" | ".join, axis=1).str.lower()
        idx = concat[concat.str.contains(key, na=False)].index.tolist()

        if idx:
            return self.df.loc[idx].head(20).to_dict(orient="records")

        return []

    def on_search(self):
        try:
            caste_key = ""
            raw_caste = ""
            record = None
            self.result_area.clear()
            self.explain_area.clear()

            text = self.input_line.text().strip()
            if not text:
                self.status_label.setText("请输入姓名或姓氏")
                return

            surname = extract_surname(text)
            results = self.lookup_surname(surname)
            if not results:
                self.result_area.setText(f"未找到与「{surname}」相关的记录")
                self.explain_area.setText("暂无阶级解释信息")
                self.status_label.setText("未找到匹配")
                return

            # ✅ 一定要先定义
            record = results[0]

            raw_caste = (
                    record.get("caste")
                    or record.get("community")
                    or record.get("category")
                    or record.get("varna")
                    or ""
            )

            caste_key = normalize_caste(raw_caste)
            info = CASTE_INFO.get(caste_key)

            # ---------- 左侧 ----------
            self.result_area.setText(
                f"姓氏：{surname}\n"
                f"匹配种姓：{raw_caste or '未知'}\n\n"
                + "\n".join(f"{k}: {v}" for k, v in record.items() if v)
            )

            # ---------- 右侧 ----------
            if info:
                self.explain_area.setText(
                    f"【Varna】\n{info['varna']}\n\n"
                    f"【社会阶层】\n{info['tier']}\n\n"
                    f"【常见身份】\n- " + "\n- ".join(info["identity"]) + "\n\n"
                                                                        f"【概述】\n{info['summary']}\n\n"
                                                                        f"【可信度】{info['confidence']}\n\n"
                                                                        "⚠️ 说明：该信息为社会学参考，存在地区与个体差异。"
                )
            else:
                self.explain_area.setText(
                    "该种姓暂无标准阶级解释\n"
                    "可能为地区性分支或拼写差异"
                )

            self.status_label.setText("查询完成")


        except Exception as e:
            self.result_area.setText("程序内部错误")
            self.explain_area.setText(str(e))
            print("❌ 错误：", e)


def main():
    app = QtWidgets.QApplication(sys.argv)
    w = CasteLookupApp()
    w.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
