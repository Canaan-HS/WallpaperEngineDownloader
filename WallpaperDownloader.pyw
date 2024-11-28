# 標準庫 - 系統 & 平台
import os
import sys
import atexit
import platform
import traceback
import threading
import subprocess

# 標準庫 - 數據處理
import re
import json
import time
import base64
import locale
import ctypes

# 標準庫 - 文件 & 解析
from pathlib import Path
from urllib.parse import unquote
from collections import OrderedDict, defaultdict

# GUI (Tkinter)
import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox

# 第三方庫
import pyperclip

SysPlat = platform.system()

class DLL:
    def __init__(self):
        # 打包的 exe 執行路徑 與 原碼執行要抓不同路徑
        self.current_dir = Path(sys.executable).parent if getattr(sys, 'frozen', False) else Path(__file__).parent

        # 預設輸出的文件名稱
        self.integrate_folder = "!【Integrate】!"
        self.output_folder = "Wallpaper_Output"

        # 配置預設值
        self.transl = language()
        self.account = "ruiiixx"
        self.appid_dict = {"Wallpaper Engine": "431960"}
        # 保存數據的模板, 目前取索引值的方式, 不能隨意變動順序, 只能變動名稱
        self.template = ["Sava_Path", "Account", "Application", "window_x", "window_y", "window_width", "window_height", "Tasks"]

        # 依賴載入路徑
        self.id_json = self.current_dir / "APPID/ID.json"
        self.config_cfg = self.current_dir / "Config.json"
        self.save_path = self.current_dir / self.output_folder
        self.icon_ico = self.current_dir / "Icon/DepotDownloader.ico"
        self.depot_exe = self.current_dir / "DepotdownloaderMod/DepotDownloadermod.exe"

        if not self.depot_exe.exists():
            messagebox.showerror(self.transl('依賴錯誤'), f"{self.transl('找不到')} {self.depot_exe}")
            os._exit(0)

        if self.id_json.exists():
            try:
                id_dict = json.loads(self.id_json.read_text(encoding="utf-8"))
                self.appid_dict.update(id_dict)
            except Exception as e:
                print(f"{self.transl('讀取配置文件時出錯')}: {e}")

        self.config_data = {} # 空數據宣告
        if self.config_cfg.exists():
            try:
                config_dict = json.loads(self.config_cfg.read_text(encoding="utf-8"))

                self.config_data = {key: config_dict[key] for key in self.template if key in config_dict} # 解構數據
                record_path = Path(self.config_data.get(self.template[0], ""))

                if record_path.is_absolute():
                    self.save_path = record_path if record_path.name == self.output_folder else record_path / self.output_folder
            except Exception as e:
                print(f"{self.transl('讀取配置文件時出錯')}: {e}") # 除錯用

    def save_config(self, data):
        old_data = {}
        cache_data = ""

        if self.config_cfg.exists():
            old_data = json.loads(self.config_cfg.read_text(encoding="utf-8"))
            cache_data = old_data.copy()

        old_data.update(data)
        self.final_config = {key: old_data.get(key, "") for key in self.template if key in old_data}  

        if cache_data != self.final_config:
            self.config_cfg.write_text(
                json.dumps(old_data, indent=4, separators=(',',':')),
                encoding="utf-8"
            )

class GUI:
    def __init__(self):
        self.title(f"Wallpaper Engine {self.transl('創意工坊下載器')}")

        x = self.config_data.get(self.template[3], 200)
        y = self.config_data.get(self.template[4], 200)
        width = self.config_data.get(self.template[5], 600)
        height = self.config_data.get(self.template[6], 700)

        self.geometry(f"{width}x{height}+{x}+{y}")
        self.minsize(350, 250)

        try:
            self.iconbitmap(self.icon_ico)
        except: pass

        self.primary_color = "#383d48"
        self.consolo_color = "#272727"
        self.secondary_color = "#afd4ff"
        self.text_color = "#ffffff"
        self.configure(bg=self.primary_color)

        self.rowconfigure(0, weight=0)  # select_frame
        self.rowconfigure(1, weight=0)  # console_frame
        self.rowconfigure(2, weight=1)  # operate_frame
        self.columnconfigure(0, weight=1)  # 水平拉伸

        self.select_frame = tk.Frame(self, bg=self.primary_color)
        self.select_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        self.select_frame.columnconfigure(1, weight=0)
        self.select_frame.columnconfigure(2, weight=1)
        self.settings_element()

        self.console_frame = tk.Frame(self, bg=self.primary_color)
        self.console_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        self.console_frame.rowconfigure(1, weight=1)
        self.console_frame.columnconfigure(0, weight=1)
        self.display_element()

        self.operate_frame = tk.Frame(self, bg=self.primary_color)
        self.operate_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=5)
        self.operate_frame.rowconfigure(1, weight=1)
        self.operate_frame.rowconfigure(2, weight=0)
        self.operate_frame.columnconfigure(0, weight=1)
        self.input_element()

    def settings_element(self):
        username_label = tk.Label(self.select_frame, text=f"{self.transl('選擇配置')}：", font=("Microsoft JhengHei", 14, "bold"), bg=self.primary_color, fg=self.text_color)
        username_label.grid(row=0, column=0, sticky="w", padx=(0, 10), pady=(10, 10))

        self.username = tk.StringVar(self)
        self.username.set(f"{self.transl('帳號')}->{self.config_data.get(self.template[1], self.acc_list[0])}") # 下面取用數據時, 會進行判斷是否存在, 這邊直接填充
        self.username_menu = ttk.Combobox(self.select_frame, textvariable=self.username, font=("Microsoft JhengHei", 10), width=15, cursor="hand2", justify="center", state="readonly", values=self.acc_list)
        self.username_menu.grid(row=0, column=1, sticky="w", padx=(0, 20))

        self.serverid = tk.StringVar(self)
        self.serverid.set(f"{self.transl('應用')}->{self.config_data.get(self.template[2], self.app_list[0])}")
        self.serverid_menu = ttk.Combobox(self.select_frame, textvariable=self.serverid, font=("Microsoft JhengHei", 10),  cursor="hand2", justify="center", values=self.app_list)
        self.serverid_menu.grid(row=0, column=2, sticky="we")
        self.server_search()

        self.path_button = tk.Button(self.select_frame, text=self.transl('修改路徑'), font=("Microsoft JhengHei", 10, "bold"), cursor="hand2", relief="raised", bg=self.secondary_color, fg=self.text_color, command=self.save_settings)
        self.path_button.grid(row=1, column=0, sticky="w")

        self.save_path_label = tk.Label(self.select_frame, text=self.save_path, font=("Microsoft JhengHei", 14, "bold"), cursor="hand2", anchor="w", justify="left", bg=self.primary_color, fg=self.text_color)
        self.save_path_label.grid(row=1, column=1, columnspan=3, sticky="w")
        self.save_path_label.bind("<Button-1>", self.copy_save_path)

        self.merge_button = tk.Button(self.select_frame, text=self.transl('檔案整合'), font=("Microsoft JhengHei", 10, "bold"), cursor="hand2", relief="raised", bg=self.secondary_color, fg=self.text_color, command=self.file_merge)
        self.merge_button.grid(row=2, column=0, sticky="w", pady=(15, 0))

    def display_element(self):
        console_label = tk.Label(self.console_frame, text=f"{self.transl('控制台輸出')}：", font=("Microsoft JhengHei", 10, "bold"), bg=self.primary_color, fg=self.text_color)
        console_label.grid(row=0, column=0, sticky="nsew")

        self.console = scrolledtext.ScrolledText(self.console_frame, font=("Consolas", 12), height=16, borderwidth=4, cursor="arrow", relief="sunken", state="disabled", bg=self.consolo_color, fg=self.text_color)
        self.console.tag_configure("important", foreground="#00DB00", font=("Consolas", 12, "bold"))
        self.console.grid(row=1, column=0, sticky="nsew")

    def input_element(self):
        input_label = tk.Label(self.operate_frame, text=f"{self.transl('輸入創意工坊專案（每行一個，支援連結和檔案ID）')}：", font=("Microsoft JhengHei", 10, "bold"), bg=self.primary_color, fg=self.text_color)
        input_label.grid(row=0, column=0, sticky="nsew")

        self.input_text = scrolledtext.ScrolledText(self.operate_frame, font=("Microsoft JhengHei", 10, "bold"), borderwidth=2, relief="sunken", wrap="none")
        self.input_text.grid(row=1, column=0, sticky="nsew")
        threading.Thread(target=self.listen_clipboard).start()

        for task in self.config_data.get(self.template[7], []): # 添加舊任務數據
            self.input_text.insert("end", f"{task}\n")

        self.run_button = tk.Button(self.operate_frame, text=self.transl('下載'), font=("Microsoft JhengHei", 14, "bold"), borderwidth=2, cursor="hand2", relief="raised", bg=self.secondary_color, fg=self.text_color, command=lambda: threading.Thread(target=self.download_trigger).start())
        self.run_button.grid(row=2, column=0, sticky="ew", pady=(12, 5))

class Backend:
    def __init__(self):
        self.account_dict = {
            key: {**value, key: base64.b64decode(value[key]).decode('utf-8')}
            for key, value in {
                'ruiiixx': {'ruiiixx': 'UzY3R0JUQjgzRDNZ'},
                'vAbuDy': {'vAbuDy': 'Qm9vbHE4dmlw'},
                'adgjl1182': {'adgjl1182': 'UUVUVU85OTk5OQ=='},
                '787109690': {'787109690': 'SHVjVXhZTVFpZzE1'}
            }.items()
        }

        # 除重用
        self.capture_record = set()
        self.complete_record = set()

        # 緩存任務數據 用於未完成恢復
        self.task_cache = OrderedDict()

        self.app_list = list(self.appid_dict.keys())
        self.acc_list = list(self.account_dict.keys())

        self.illegal_regular = re.compile(r'[<>:"/\\|?*\x00-\x1F]')
        self.parse_regular = re.compile(r'(\d{8,10})(?:&searchtext=(.*))?')
        self.link_regular = re.compile(r'^https://steamcommunity\.com/sharedfiles/filedetails/\?id=\d+.*$')

        self.token = True
        self.error_rule = {
            "Microsoft.NETCore.App": self.transl("下載失敗 請先安裝 .NET 9 執行庫"),
            "Unable to locate manifest ID for published file": self.transl("下載失敗 請設置正確的應用"),
            "STEAM GUARD": [self.transl("下載失敗 請嘗試變更帳號後在下載")],
        }
        # 重用
        self.error_rule["AccountDisabled"] = self.error_rule["STEAM GUARD"]

    def Closure(self):
        username, app = self.get_config(True)
        undone = list(set(self.task_cache.values()) | set(self.input_stream()))

        self.save_config({
            "Account": username,
            "Application": app,
            "window_x": self.winfo_x(),
            "window_y": self.winfo_y(),
            "window_width": self.winfo_width(),
            "window_height": self.winfo_height(),
            "Tasks": undone
        })

        processName = "DepotDownloadermod.exe"

        if SysPlat == "Windows":
            subprocess.Popen(f"taskkill /f /im {processName}", creationflags=subprocess.CREATE_NO_WINDOW)
        elif SysPlat in ["Linux", "Darwin"]:
            subprocess.Popen(f"pkill -f {processName}", shell=True)

        os._exit(0)

    def save_settings(self):
        path = filedialog.askdirectory(title=self.transl('選擇資料夾'))

        if path:
            self.save_path = Path(path) / self.output_folder
            self.save_path_label.config(text=self.save_path)
            self.save_config({"Sava_Path": str(self.save_path)})

    def copy_save_path(self, event):
        pyperclip.copy(self.save_path)
        popup = tk.Toplevel(self)
        popup.overrideredirect(True)
        popup.attributes("-topmost", True)

        label = tk.Label(popup, text=self.transl('已複製'), font=("Microsoft JhengHei", 10), bg="#333333", fg="#FFFFFF", padx=5, pady=5)
        label.pack()

        popup.update_idletasks() # 更新窗口以計算 label 的大小
        popup.geometry(f"{label.winfo_reqwidth()}x{label.winfo_reqheight()}+{event.x_root - 25}+{event.y_root - 35}")
        popup.grab_set()
        popup.after(800, popup.destroy)

    def server_search(self):
        # 編譯前綴樹函數
        def build_trie(data_list):
            trie = {}
            for appid in data_list:
                current = trie
                for char in appid.lower():
                    if char not in current:
                        current[char] = {}
                    current = current[char]
                current["$"] = appid
            return trie
        # 搜尋前綴樹函數
        def search_trie(trie, prefix):
            current = trie
            for char in prefix:
                if char not in current:
                    return iter([])
                current = current[char]

            def match_generator():
                stack = [current]
                while stack:
                    node = stack.pop()
                    if "$" in node:
                        yield node["$"]
                    for char, subtree in node.items():
                        if char != "$":
                            stack.append(subtree)
            return match_generator()

        # 編譯前綴樹
        appid_trie = build_trie(self.app_list)

        def on_input(event):
            prefix = event.widget.get().lower()
            matches = search_trie(appid_trie, prefix) if prefix else self.app_list
            self.serverid_menu.configure(values=list(matches))

        def on_click(event):
            x = event.x
            widget = event.widget
            text = self.serverid.get()
            if x < widget.winfo_width() - 20 and "->" in text:
                self.serverid.set("")
                self.serverid_menu.unbind("<Button-1>")

        def on_select(event):
            self.serverid_menu.configure(values=self.app_list)

        self.serverid_menu.bind("<KeyRelease>", on_input)
        self.serverid_menu.bind("<Button-1>", on_click)
        self.serverid_menu.bind("<<ComboboxSelected>>", on_select)

    """ ====== 檔案整合區塊 ====== """
    def get_save_data(self):
        file_data = defaultdict(list)
        for file in self.save_path.rglob("*"):
            if file.is_file() and self.integrate_folder not in file.parts:
                file_data[file.suffix].append(file)
        return dict( # 數量多到少排序, 相同數量按字母排序, 組合 key 為副檔名, value 為檔案列表 回傳字典
            sorted(file_data.items(), key=lambda item: (-len(item[1]), item[0]))
        )

    def file_merge(self):
        data_table = self.get_save_data()

        if data_table:
            merge_window = tk.Toplevel(self)
            merge_window.title(self.transl('檔案整合'))
            merge_window.configure(bg=self.primary_color)

            try:
                merge_window.iconbitmap(self.icon_ico)
            except: pass

            width = 500
            height = 550

            merge_window.geometry(f"{width}x{height}+{int((self.winfo_screenwidth() - width) / 2)}+{int((self.winfo_screenheight() - height) / 2)}")
            merge_window.minsize(400, 450)

            tip_frame = tk.Frame(merge_window, bg=self.primary_color)
            tip_frame.pack(fill="x", padx=10, pady=10)
            tip = tk.Label(tip_frame, text=self.transl('選擇整合的類型'), font=("Microsoft JhengHei", 18, "bold"), bg=self.primary_color, fg=self.text_color)
            tip.pack()

            display_frame = tk.Frame(merge_window, bg=self.primary_color)
            display_frame.pack(fill="both", expand=True, padx=10, pady=10)

            output_frame = tk.Frame(merge_window, bg=self.primary_color)
            output_frame.pack(fill="x")

            scroll_y = tk.Scrollbar(display_frame, orient="vertical")
            scroll_y.pack(side="right", fill="y")

            style = ttk.Style()
            style.configure("Custom.Treeview", font=("Microsoft JhengHei", 14, "bold"), foreground=self.text_color, background=self.consolo_color, rowheight=30)
            style.configure("Custom.Treeview.Heading", font=("Microsoft JhengHei", 16, "bold"), foreground="#0066CC")

            treeview = ttk.Treeview(display_frame, columns=("Type", "Count"), show="headings", yscrollcommand=scroll_y.set, cursor="hand2", style="Custom.Treeview")
            treeview.heading("Type", text=self.transl('檔案類型'))
            treeview.heading("Count", text=self.transl('檔案數量'))
            treeview.column("Type", anchor="center")
            treeview.column("Count", anchor="center")

            for key, value in data_table.items():
                treeview.insert("", "end", values=(key.replace(".", ""), len(value)))

            scroll_y.config(command=treeview.yview)
            treeview.pack(fill="both", expand=True)

            def move_save_file():
                if len(treeview.selection()) == 0:
                    messagebox.showwarning(title=self.transl('操作提示'), message=self.transl('請選擇要整合的類型'), parent=merge_window)
                    return

                selected = []
                selected_items = treeview.selection()

                for item in selected_items:
                    values = treeview.item(item, "values")  # 取得對應的數據
                    selected.append(values[0])

                confirm = messagebox.askquestion(self.transl('操作確認'), f"{self.transl('整合以下類型的檔案')}?\n\n{selected}", parent=merge_window)
                if confirm == "yes":
                    for item in selected_items: # 移除選中的項目
                        treeview.delete(item)

                    merge_path = self.save_path / self.integrate_folder
                    merge_path.mkdir(parents=True, exist_ok=True)
                    move_file = [data_table[f".{select}"] for select in selected]

                    for files in move_file:
                        for file in files:
                            relative_path = file.relative_to(self.save_path) # 獲取 file 在 self.save_path 下的相對路徑
                            top_folder = relative_path.parts[0] # 取得最上層資料夾名稱

                            file.rename(merge_path / f"[{top_folder}] {file.name}")

                    messagebox.showinfo(title=self.transl('操作完成'), message=f"{self.transl('檔案整合完成')}\n{merge_path}", parent=merge_window)

            print_button = tk.Button(output_frame, text=self.transl('整合輸出'), font=("Microsoft JhengHei", 12, "bold"), borderwidth=2, cursor="hand2", relief="raised", bg=self.secondary_color, fg=self.text_color, command=move_save_file)
            print_button.pack(pady=(5, 15))
        else:
            messagebox.showwarning(title=self.transl('獲取失敗'), message=self.transl('沒有可整合的檔案'), parent=self)
    """ ====== 檔案整合區塊 ====== """

    """ ====== 下載處理區塊 ====== """
    def console_analysis(self, text):
        for Key, message in self.error_rule.items():
            if Key in text:
                self.token = False
                return message

    def get_unique_path(self, path):
        index = 1
        [parent, stem, suffix] = path.parent, path.stem, path.suffix
        while path.exists():
            path = parent / f"{stem} ({index}){suffix}"
            index += 1
        return path

    def console_update(self, message, *args):
        self.console.config(state="normal")
        self.console.insert("end", message, *args)
        self.console.yview("end")
        self.console.config(state="disabled")

    def download(self, taskId, appId, pubId, searchText, Username, Password):
        if not self.token: return

        try:
            process_name = self.illegal_regular.sub("-", searchText if searchText else pubId).strip()

            self.console_update(f"\n> {self.transl('開始下載')} [{process_name}]\n", "important")

            if not self.save_path.exists():
                self.save_path.mkdir(parents=True, exist_ok=True)

            dir_option = f"-dir \"{self.get_unique_path(self.save_path / process_name)}\""
            command = f"{self.depot_exe} -app {appId} -pubfile {pubId} -verify-all -username {Username} -password {Password} {dir_option}"

            end_message = self.transl('下載完成')
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,creationflags=subprocess.CREATE_NO_WINDOW)

            for line in process.stdout:
                self.console_update(line)
                state = self.console_analysis(line)

                # 錯誤時更改消息
                if isinstance(state, list):
                    end_message = state[0]
                    process.terminate()
                    break

                elif state: end_message = state

            process.stdout.close()
            process.wait()

            self.console_update(f"> [{process_name}] {end_message}\n", "important")
            if self.token:
                del self.task_cache[taskId] # 刪除已下載緩存
                self.complete_record.add(taskId) # 添加下載完成紀錄
        except:
            self.console_update(f"> {self.transl('例外中止')}\n", "important")
            messagebox.showerror(self.transl('例外'), traceback.format_exc(), parent=self)
    """ ====== 下載處理區塊 ====== """

    """ ====== 觸發與UI處理區塊 ====== """
    def get_config(self, original=False):
        username, password = next(iter(
                self.account_dict.get(self.username.get().split("->")[-1], self.account_dict.get(self.account)).items()
            )
        )

        if original:
            for app in [self.serverid.get().split("->")[-1], self.app_list[0]]:
                if app in self.appid_dict:
                    return username, app
        else:
            appid = self.appid_dict.get(self.serverid.get(), next(iter(self.appid_dict.values())))
            return appid, username, password

    def listen_clipboard(self):
        while True:
            clipboard = unquote(pyperclip.paste()) # unquote 是沒必要的, 方便觀看而已, 但會有額外性能開銷

            if self.link_regular.match(clipboard) and clipboard not in self.capture_record:
                self.capture_record.add(clipboard)
                self.input_text.insert("end", f"{clipboard}\n")
                self.input_text.yview("end")

            time.sleep(0.3)

    def status_switch(self, state):
        if state == "disabled":
            self.username_menu.config(state="disabled", cursor="no")
            self.serverid_menu.config(state="disabled", cursor="no")
            self.path_button.config(state="disabled", cursor="no")
            self.merge_button.config(state="disabled", cursor="no")
            self.run_button.config(state="disabled", cursor="no")
        else:
            self.username_menu.config(state="readonly", cursor="hand2")
            self.serverid_menu.config(state="normal", cursor="hand2")
            self.path_button.config(state="normal", cursor="hand2")
            self.merge_button.config(state="normal", cursor="hand2")
            self.run_button.config(state="normal", cursor="hand2")

            pyperclip.copy("") # 重設剪貼簿 避免 record 清除後再次擷取

            for task in self.task_cache.values():
                self.input_text.insert("end", f"{task}\n")

            self.token = True # 重設令牌
            self.capture_record.clear() # 重設擷取紀錄

    def input_stream(self):
        while True:
            lines = self.input_text.get("1.0", "end").splitlines()
            if not lines or not lines[0].strip(): break # 避免空數據
            self.input_text.delete("1.0", "2.0")
            yield unquote(lines[0]).strip()

    def download_trigger(self):
        self.status_switch("disabled")
        appid, username, password = self.get_config()

        for link in self.input_stream():
            if link:
                match = self.parse_regular.search(link)
                if match:
                    self.capture_record.add(link)

                    match_gp1 = match.group(1)
                    task_id = f"{appid}-{match_gp1}"

                    if task_id not in self.complete_record:
                        self.task_cache[task_id] = link
                        self.download(task_id, appid, match_gp1, match.group(2), username, password)
                else:
                    self.console_update(f"{self.transl('無效連結')}：{link}\n")

        self.status_switch("normal")
    """ ====== 觸發與UI處理區塊 ====== """

def language(lang=None):
        Word = {
            'zh_TW': {"": ""},
            'zh_CN': {
                "創意工坊下載器": "创意工坊下载器",
                "選擇配置": "选择配置",
                "修改路徑": "修改路径",
                "檔案整合": "文件整合",
                "帳號": "账号",
                "應用": "应用",
                "已複製": "",
                "選擇資料夾": "选择文件夹",
                "控制台輸出": "控制台输出",
                "輸入創意工坊專案（每行一個，支援連結和檔案ID）": "输入创意工坊项目（每行一个，支持链接和文件ID）",
                "選擇整合的類型": "选择整合的类型",
                "檔案類型": "文件类型",
                "檔案數量": "文件数量",
                "操作提示": "操作提示",
                "請選擇要整合的類型": "请选择要整合的类型",
                "操作確認": "操作确认",
                "整合以下類型的檔案": "整合以下类型的文件",
                "操作完成": "操作完成",
                "檔案整合完成": "文件整合完成",
                "整合輸出": "整合输出",
                "獲取失敗": "获取失败",
                "沒有可整合的檔案": "没有可整合的文件",
                "下載": "下载",
                "例外": "例外",
                "開始下載": "开始下载",
                "下載完成": "下载完成",
                "例外中止": "例外中止",
                "無效連結": "无效链接",
                "下載失敗 請先安裝 .NET 9 執行庫": "",
                "下載失敗 請設置正確的應用": "",
                "下載失敗 請嘗試變更帳號後在下載": "",
                "找不到": "找不到",
                "依賴錯誤": "依赖错误",
                "讀取配置文件時出錯": "读取配置文件时出错"
            },
            'en_US': {
                "創意工坊下載器": "Workshop Downloader",
                "選擇配置": "Select",
                "修改路徑": "Modify Path",
                "檔案整合": "File Integration",
                "帳號": "Acc",
                "應用": "App",
                "已複製": "Copied",
                "選擇資料夾": "Select Folder",
                "控制台輸出": "Console Output",
                "輸入創意工坊專案（每行一個，支援連結和檔案ID）": "Enter Workshop Project (one per line, supports link and file ID)",
                "選擇整合的類型": "Select Type of Integration",
                "檔案類型": "File Type",
                "檔案數量": "File Count",
                "操作提示": "Operation Tips",
                "請選擇要整合的類型": "Please select the type of integration",
                "操作確認": "Operation Confirmation",
                "整合以下類型的檔案": "Integrate the following types of files",
                "操作完成": "Operation Completed",
                "檔案整合完成": "File Integration Completed",
                "整合輸出": "Integration Output",
                "獲取失敗": "Failed to Retrieve",
                "沒有可整合的檔案": "No Files to Integrate",
                "下載": "Download",
                "例外": "Exception",
                "開始下載": "Start Download",
                "下載完成": "Download Completed",
                "例外中止": "Exception Aborted",
                "無效連結": "Invalid Link",
                "下載失敗 請先安裝 .NET 9 執行庫": "Download Failed. Please install .NET 9 runtime first",
                "下載失敗 請設置正確的應用": "Download Failed. Please set the correct application",
                "下載失敗 請嘗試變更帳號後在下載": "Download Failed. Please try changing the account and retry",
                "找不到": "Not Found",
                "依賴錯誤": "Dependency Error",
                "讀取配置文件時出錯": "Error Reading Configuration File"
            }
        }

        Locale = {
            '950': 'zh_TW', '936': 'zh_CN', '1252': 'en_US'
        }

        # 總是有人系統怪怪的
        if lang is None:
            if SysPlat == 'Windows':
                buffer = ctypes.create_unicode_buffer(85)
                ctypes.windll.kernel32.GetUserDefaultLocaleName(buffer, len(buffer))
                lang = buffer.value.replace('-', '_')
            elif SysPlat == 'Linux' or SysPlat == 'Darwin':
                lang = os.environ.get("LANG").split('.')[0]
            else:
                locale.setlocale(locale.LC_ALL, '')
                lang = locale.getlocale()[1].replace('cp', '')

        if lang.isdigit():
            lang = Locale.get(lang, 'en_US')
            ML = Word.get(lang)
        else:
            ML = Word.get(lang, 'en_US') 

        return lambda text: ML.get(text, text)

class Controller(DLL, tk.Tk, Backend, GUI):
    def __init__(self):
        DLL.__init__(self)
        tk.Tk.__init__(self)
        Backend.__init__(self)
        GUI.__init__(self)

        self.protocol("WM_DELETE_WINDOW", self.Closure)
        self.mainloop()

if __name__ == "__main__":
    Controller()