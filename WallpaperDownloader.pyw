import os
import sys
import shutil
import atexit
import platform
import traceback
import threading
import subprocess
import tkinter as tk

import re
import json
import time
import base64
import locale
import ctypes

from pathlib import Path
from urllib.parse import unquote
from types import SimpleNamespace
from collections import defaultdict
from tkinter import ttk, scrolledtext, filedialog, messagebox

import psutil
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

        # 配置模板 (Key 是調用值, Value 是輸出值)
        self.cfg_key = {
            "Save": "Sava_Path",
            "Acc": "Account", "App": "Application",
            "X": "window_x", "Y": "window_y",
            "W": "window_width", "H": "window_height",
            "Task": "Tasks"
        }

        # 依賴載入路徑
        self.id_json = self.current_dir / "APPID/ID.json"
        self.config_json = self.current_dir / "Config.json"
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

        self.cfg_data = {}
        self.CK = SimpleNamespace(**self.cfg_key) # 方便簡短調用

        if self.config_json.exists():
            try:
                config_dict = json.loads(self.config_json.read_text(encoding="utf-8"))

                self.cfg_data = {val: config_dict[val] for val in self.cfg_key.values() if val in config_dict} # 解構數據
                record_path = Path(self.cfg_data.get(self.CK.Save, ""))

                if record_path.is_absolute():
                    self.save_path = record_path if record_path.name == self.output_folder else record_path / self.output_folder
            except Exception as e:
                print(f"{self.transl('讀取配置文件時出錯')}: {e}") # 除錯用

    def save_config(self, data):
        old_data = {}
        cache_data = ""

        if self.config_json.exists():
            old_data = json.loads(self.config_json.read_text(encoding="utf-8"))
            cache_data = old_data.copy()

        old_data.update(data)
        self.final_config = {val: old_data.get(val, "") for val in self.cfg_key.values() if val in old_data}  

        if cache_data != self.final_config:
            self.config_json.write_text(
                json.dumps(old_data, indent=4, separators=(',',':')),
                encoding="utf-8"
            )

class GUI:
    def __init__(self):
        self.title(f"Wallpaper Engine {self.transl('創意工坊下載器')}")

        x = self.cfg_data.get(self.CK.X, 200)
        y = self.cfg_data.get(self.CK.Y, 200)
        width = self.cfg_data.get(self.CK.W, 600)
        height = self.cfg_data.get(self.CK.H, 700)

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
        self.username.set(f"{self.transl('帳號')}->{self.cfg_data.get(self.CK.Acc, self.acc_list[0])}") # 下面取用數據時, 會進行判斷是否存在, 這邊直接填充
        self.username_menu = ttk.Combobox(self.select_frame, textvariable=self.username, font=("Microsoft JhengHei", 10), width=15, cursor="hand2", justify="center", state="readonly", values=self.acc_list)
        self.username_menu.grid(row=0, column=1, sticky="w", padx=(0, 20))

        self.serverid = tk.StringVar(self)
        self.serverid.set(f"{self.transl('應用')}->{self.cfg_data.get(self.CK.App, self.app_list[0])}")
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
        threading.Thread(target=self.listen_clipboard, daemon=True).start()

        for task in self.cfg_data.get(self.CK.Task, []): # 添加舊任務數據
            self.input_text.insert("end", f"{task}\n")

        self.run_button = tk.Button(self.operate_frame, text=self.transl('下載'), font=("Microsoft JhengHei", 14, "bold"), borderwidth=2, cursor="hand2", relief="raised", bg=self.secondary_color, fg=self.text_color, command=lambda: threading.Thread(target=self.download_trigger, daemon=True).start())
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

        # 緩存任務數據 用於未完成恢復
        self.task_cache = {}

        # 除重用
        self.capture_record = set()
        self.complete_record = set()

        self.app_list = list(self.appid_dict.keys())
        self.acc_list = list(self.account_dict.keys())

        self.illegal_regular = re.compile(r'[<>:"/\\|?*\x00-\x1F]')
        self.parse_regular = re.compile(r'(\d{8,10})(?:&searchtext=(.*))?')
        self.link_regular = re.compile(r'^https://steamcommunity\.com/sharedfiles/filedetails/\?id=\d+.*$')

        self.token = True # 可強制停止所有任務
        self.error_rule = {
            "Microsoft.NETCore.App": self.transl("下載失敗: 請先安裝 .NET 9 執行庫"),
            "Unable to locate manifest ID for published file": self.transl("下載失敗: 該項目可能已被刪除，或應用設置錯誤"),
            "STEAM GUARD": [self.transl("下載失敗: 請嘗試變更帳號後在下載")], # 列表為可觸發強制停止任務
        }
        self.error_rule["AccountDisabled"] = self.error_rule["STEAM GUARD"] # 重用
        atexit.register(self.process_cleanup) # 關閉清理

    """ ====== 關閉清理 ====== """
    def Closure(self):
        username, app = self.get_config(True)
        undone = list({cache['url'] for cache in self.task_cache.values()} | set(self.input_stream()))

        self.save_config({
            "Account": username,
            "Application": app,
            "window_x": self.winfo_x(),
            "window_y": self.winfo_y(),
            "window_width": self.winfo_width(),
            "window_height": self.winfo_height(),
            "Tasks": undone
        })

        self.destroy()

    def process_cleanup(self):
        pids = []
        processName = "DepotDownloaderMod.exe"
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if proc.info['name'].lower() == processName.lower():
                    pids.append(proc.pid)
                    proc.kill()
            except:continue
        self.del_error_file(pids)

    def del_error_file(self, pids):
        for task in self.task_cache.values():
            path = task['path']

            if Path(path).exists():
                for _ in range(10): # 最多等待10秒
                    if not any(psutil.pid_exists(pid) for pid in pids):
                        try:
                            shutil.rmtree(path)
                            break
                        except:continue
                    time.sleep(1)

    """ ====== 設定配置 ====== """
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

    """ ====== 檔案整合 ====== """
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

    """ ====== 下載處理 ====== """
    def console_analysis(self, text):
        for Key, message in self.error_rule.items():
            if Key in text:
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
            end_message = self.transl('下載完成')
            process_name = self.illegal_regular.sub("-", searchText if searchText else pubId).strip()

            self.console_update(f"\n> {self.transl('開始下載')} [{process_name}]\n", "important")

            if not self.save_path.exists():
                self.save_path.mkdir(parents=True, exist_ok=True)

            task_path = self.get_unique_path(self.save_path / process_name)
            self.task_cache[taskId]['path'] = task_path # 再添加下載路徑

            # 避免 Command Injection
            command = [
                self.depot_exe, "-app", str(appId), "-pubfile", str(pubId),
                "-verify-all", "-username", Username, "-password", Password,
                "-dir", task_path
            ]

            process = subprocess.Popen(
                command, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, 
                creationflags=subprocess.CREATE_NO_WINDOW
            )

            for line in process.stdout:
                self.console_update(line)
                err_message = self.console_analysis(line)

                # 消息是列表狀態, 代表需要強制中止
                if isinstance(err_message, list):
                    self.token = False
                    process.terminate()
                    end_message = err_message[0]
                    return

                elif err_message: end_message = err_message

            process.stdout.close()
            process.wait()

            if end_message == self.transl('下載完成') and Path(task_path).exists():
                self.task_cache.pop(taskId, None) # 刪除已下載緩存
                self.complete_record.add(taskId) # 添加下載完成紀錄
            else:
                # 這邊因為進程可能還需要繼續, 而不刪除錯誤的文件
                end_message = end_message if end_message != self.transl('下載完成') else self.transl('下載失敗') # 用於顯示不在 console_analysis 中的錯誤

            self.console_update(f"> [{process_name}] {end_message}\n", "important")
        except:
            self.console_update(f"> {self.transl('例外中止')}\n", "important")
            messagebox.showerror(self.transl('例外'), traceback.format_exc(), parent=self)

    """ ====== 觸發與 UI 操作 ====== """
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
        pyperclip.copy("") # 避免開啟直接貼上

        while True:
            clipboard = unquote(pyperclip.paste()) # unquote 是沒必要的, 方便觀看而已, 但會有額外性能開銷

            if self.link_regular.match(clipboard) and clipboard not in self.capture_record:
                self.capture_record.add(clipboard)
                self.input_text.insert("end", f"{clipboard}\n")
                self.input_text.yview("end")

            time.sleep(0.3)

    def status_switch(self, state):
        if state == "disabled":
            self.merge_button.config(state="disabled", cursor="no")
            self.run_button.config(state="disabled", cursor="no")
        else:
            self.merge_button.config(state="normal", cursor="hand2")
            self.run_button.config(state="normal", cursor="hand2")

            pyperclip.copy("") # 重設剪貼簿 避免 record 清除後再次擷取

            for task in self.task_cache.values():
                self.input_text.insert("end", f"{task['url']}\n")

            self.token = True # 重設令牌
            self.task_cache.clear() # 重設任務緩存
            self.capture_record.clear() # 重設擷取紀錄

    def input_stream(self):
        while True:
            lines = self.input_text.get("1.0", "end").splitlines()
            if not lines or not lines[0].strip(): break # 避免空數據
            self.input_text.delete("1.0", "2.0")
            yield unquote(lines[0]).strip()

    def download_trigger(self):
        self.status_switch("disabled")

        for link in self.input_stream():
            if link:
                match = self.parse_regular.search(link)
                if match:
                    appid, username, password = self.get_config() # 允許臨時變更, 所以每次重獲取
                    self.capture_record.add(link)

                    match_gp1 = match.group(1)
                    task_id = f"{appid}-{match_gp1}"

                    if task_id not in self.complete_record:
                        self.task_cache[task_id] = {'url': link}
                        self.download(task_id, appid, match_gp1, match.group(2), username, password)
                else:
                    self.console_update(f"{self.transl('無效連結')}：{link}\n")

        self.status_switch("normal")

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
                "已複製": "已复制",
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
                "下載失敗": "下载失败",
                "下載失敗: 請先安裝 .NET 9 執行庫": "下载失败: 请先安装 .NET 9 运行库",
                "下載失敗: 該項目可能已被刪除，或應用設置錯誤": "下载失败: 该项目可能已被删除，或应用设置错误",
                "下載失敗: 請嘗試變更帳號後在下載": "下载失败: 请尝试变更帐号后再下载",
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
                "下載失敗": "Download Failed",
                "下載失敗: 請先安裝 .NET 9 執行庫": "Download Failed: Please install .NET 9 Runtime first",
                "下載失敗: 該項目可能已被刪除，或應用設置錯誤": "Download Failed: The project may have been deleted, or the application settings are incorrect",
                "下載失敗: 請嘗試變更帳號後在下載": "Download Failed: Please try changing the account and then download",
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
            ML = Word.get(Locale.get(lang, 'en_US'), lang)
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