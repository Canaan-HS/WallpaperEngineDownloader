import os
import re
import sys
import time
import locale
import base64
import threading
import subprocess
import tkinter as tk

from tkinter import ttk
from pathlib import Path
from urllib.parse import unquote
from collections import defaultdict
from tkinter import scrolledtext, filedialog, messagebox

import pyperclip

def language(lang):
        Word = {
            '950': {"": ""},
            '936': {
                "依賴錯誤": "依赖错误",
                "找不到": "找不到",
                "讀取配置文件時出錯": "读取配置文件时出错",
                "創意工坊下載器": "创意工坊下载器",
                "選擇帳號": "选择账号",
                "修改路徑": "修改路径",
                "檔案整合": "文件整合",
                "控制台輸出": "控制台输出",
                "輸入創意工坊專案（每行一個，支援連結和檔案ID）": "输入创意工坊项目（每行一个，支持链接和文件ID）",
                "下載": "下载",
                "選擇資料夾": "选择文件夹",
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
                "下載完成": "下载完成",
                "無效連結": "无效链接"
            },
            '1252': {
                "依賴錯誤": "Dependency Error",
                "找不到": "Not Found",
                "讀取配置文件時出錯": "Error Reading Configuration File",
                "創意工坊下載器": "Workshop Downloader",
                "選擇帳號": "Select Account",
                "修改路徑": "Modify Path",
                "檔案整合": "File Integration",
                "控制台輸出": "Console Output",
                "輸入創意工坊專案（每行一個，支援連結和檔案ID）": "Enter Workshop Projects (One per Line, Supports Links and File IDs)",
                "下載": "Download",
                "選擇資料夾": "Select Folder",
                "選擇整合的類型": "Select the types to integrate",
                "檔案類型": "File Type",
                "檔案數量": "File Count",
                "操作提示": "Operation Tips",
                "請選擇要整合的類型": "Please select the types to integrate",
                "操作確認": "Operation Confirmation",
                "整合以下類型的檔案": "Integrate the following types of files",
                "操作完成": "Operation Completed",
                "檔案整合完成": "File Integration Completed",
                "整合輸出": "Integration Output",
                "獲取失敗": "Failed to Retrieve",
                "沒有可整合的檔案": "No Files to Integrate",
                "下載完成": "Download Completed",
                "無效連結": "Invalid Link"
            }
        }

        lang = str(lang).replace('cp', '')
        ML = Word.get(lang) or Word.get('1252')
        return lambda text: ML.get(text) or text

class DLL:
    def __init__(self):
        self.integrate_folder = "Integrate"
        self.output_folder = "Wallpaper_Output"
        self.current_dir = Path(sys.executable).parent if getattr(sys, 'frozen', False) else Path(__file__).parent

        self.save_path = Path(self.current_dir) / self.output_folder
        self.config_cfg = Path(self.current_dir) / "lastsavelocation.cfg"
        self.icon_ico = Path(self.current_dir) / "Icon/DepotDownloader.ico"
        self.depot_exe = Path(self.current_dir) / "DepotdownloaderMod/DepotDownloadermod.exe"

        self.transl = language(locale.getlocale()[1])

        if not self.depot_exe.exists():
            messagebox.showerror(self.transl('依賴錯誤'), f"{self.transl('找不到')} {self.depot_exe}", parent=self)
            os._exit(0)

        if self.config_cfg.exists():
            try:
                record_str = self.config_cfg.read_text().strip()
                record_path = Path(record_str)

                if record_path.is_absolute():
                    self.save_path = record_path if record_path.name == self.output_folder else record_path / self.output_folder
            except Exception as e:
                print(f"{self.transl('讀取配置文件時出錯')}: {e}")

        self.add_record_url = set()
        self.complete_record_id = set()

        self.illegal_regular = re.compile(r'[<>:"/\\|?*\x00-\x1F]')
        self.parse_regular = re.compile(r'id=(\d{8,10})(?:&searchtext=(.*))?')
        self.link_regular = re.compile(r'^https://steamcommunity\.com/sharedfiles/filedetails/\?id=\d+.*$')
        
        self.accounts = {
            'ruiiixx': 'UzY3R0JUQjgzRDNZ',
            'premexilmenledgconis': 'M3BYYkhaSmxEYg==',
            'vAbuDy': 'Qm9vbHE4dmlw',
            'adgjl1182': 'UUVUVU85OTk5OQ==',
            'gobjj16182': 'enVvYmlhbzgyMjI=',
            '787109690': 'SHVjVXhZTVFpZzE1'
        }

        self.acclist = list(self.accounts.keys())
        self.passwords = {account: base64.b64decode(self.accounts[account]).decode('utf-8') for account in self.accounts}

    def get_save_data(self):
        file_data = defaultdict(list)
        [file_data[file.suffix].append(file) for file in self.save_path.rglob("*") if file.is_file() and self.integrate_folder not in str(file)]
        return { # 數量多到少排序, 相同數量按字母排序, 組合 key 為副檔名, value 為檔案列表 回傳字典
            suffix: files for suffix, files in sorted(file_data.items(), key=lambda item: (-len(item[1]), item[0]))
        }

class GUI(DLL, tk.Tk):
    def __init__(self):
        DLL.__init__(self)
        tk.Tk.__init__(self, className=f"Wallpaper Engine {self.transl('創意工坊下載器')}")

        self.geometry("600x650")
        self.minsize(500, 550)

        try:
            self.iconbitmap(self.icon_ico)
        except: pass

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.primary_color = "#383d48"
        self.consolo_color = "#272727"
        self.secondary_color = "#afd4ff"
        self.text_color = "#ffffff"
        self.configure(bg=self.primary_color)

        self.select_frame = tk.Frame(self, bg=self.primary_color)
        self.select_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        self.select_frame.columnconfigure(1, weight=0)
        self.settings_element()

        self.console_frame = tk.Frame(self, bg=self.primary_color)
        self.console_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        self.console_frame.rowconfigure(1, weight=1)
        self.console_frame.columnconfigure(0, weight=1)
        self.display_element()

        self.operate_frame = tk.Frame(self, bg=self.primary_color)
        self.operate_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=5)
        self.operate_frame.columnconfigure(0, weight=1)
        self.input_element()

    def settings_element(self):
        username_label = tk.Label(self.select_frame, text=f"{self.transl('選擇帳號')}：", font=("Microsoft JhengHei", 14, "bold"), bg=self.primary_color, fg=self.text_color)
        username_label.grid(row=0, column=0, sticky="w", pady=(10, 10))

        self.username = tk.StringVar(self)
        self.username.set(self.acclist[0])
        self.sername_menu = ttk.Combobox(self.select_frame, textvariable=self.username, font=("Microsoft JhengHei", 10), cursor="hand2", justify="center", state="readonly", values=self.acclist)
        self.sername_menu.grid(row=0, column=1, sticky="w")

        self.path_button = tk.Button(self.select_frame, text=self.transl('修改路徑'), font=("Microsoft JhengHei", 10, "bold"), cursor="hand2", relief="raised", bg=self.secondary_color, fg=self.text_color, command=self.save_settings)
        self.path_button.grid(row=1, column=0, sticky="w")

        self.save_path_label = tk.Label(self.select_frame, text=self.save_path, font=("Microsoft JhengHei", 14, "bold"), bg=self.primary_color, fg=self.text_color)
        self.save_path_label.grid(row=1, column=1, sticky="w")

        self.merge_button = tk.Button(self.select_frame, text=self.transl('檔案整合'), font=("Microsoft JhengHei", 10, "bold"), cursor="hand2", relief="raised", bg=self.secondary_color, fg=self.text_color, command=self.file_merge)
        self.merge_button.grid(row=2, column=0, sticky="w", pady=(15, 0))

    def display_element(self):
        console_label = tk.Label(self.console_frame, text=f"{self.transl('控制台輸出')}：", font=("Microsoft JhengHei", 10, "bold"), bg=self.primary_color, fg=self.text_color)
        console_label.grid(row=0, column=0, sticky="nsew")

        self.console = scrolledtext.ScrolledText(self.console_frame, font=("Consolas", 12), height=14, borderwidth=4, cursor="arrow", relief="sunken", state="disabled", bg=self.consolo_color, fg=self.text_color)
        self.console.tag_configure("important", foreground="#00DB00", font=("Consolas", 12, "bold"))
        self.console.grid(row=1, column=0, sticky="nsew")

    def input_element(self):
        input_label = tk.Label(self.operate_frame, text=f"{self.transl('輸入創意工坊專案（每行一個，支援連結和檔案ID）')}：", font=("Microsoft JhengHei", 10, "bold"), bg=self.primary_color, fg=self.text_color)
        input_label.grid(row=0, column=0, sticky="nsew")

        self.input_text = scrolledtext.ScrolledText(self.operate_frame, font=("Microsoft JhengHei", 10, "bold"), height=7, borderwidth=2, relief="sunken", wrap="none")
        self.input_text.grid(row=1, column=0, sticky="nsew")
        threading.Thread(target=self.listen_clipboard).start()

        self.run_button = tk.Button(self.operate_frame, text=self.transl('下載'), font=("Microsoft JhengHei", 14, "bold"), borderwidth=2, cursor="hand2", relief="raised", bg=self.secondary_color, fg=self.text_color, command=self.download_trigger)
        self.run_button.grid(row=2, column=0, sticky="ew", pady=(12, 5))

    def save_settings(self):
        path = filedialog.askdirectory(title=self.transl('選擇資料夾'))

        if path:
            self.save_path = Path(path) / self.output_folder
            self.save_path_label.config(text=self.save_path)
            self.config_cfg.write_text(str(self.save_path), encoding="utf-8")

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
                            file.rename(merge_path / f"[{file.parent.name}] {file.name}")

                    messagebox.showinfo(title=self.transl('操作完成'), message=f"{self.transl('檔案整合完成')}\n{merge_path}", parent=merge_window)

            print_button = tk.Button(output_frame, text=self.transl('整合輸出'), font=("Microsoft JhengHei", 12, "bold"), borderwidth=2, cursor="hand2", relief="raised", bg=self.secondary_color, fg=self.text_color, command=move_save_file)
            print_button.pack(pady=(5, 15))
        else:
            messagebox.showwarning(title=self.transl('獲取失敗'), message=self.transl('沒有可整合的檔案'), parent=self)

    def status_switch(self, state):
        if state == "disabled":
            self.sername_menu.config(state="disabled", cursor="no")
            self.path_button.config(state="disabled", cursor="no")
            self.merge_button.config(state="disabled", cursor="no")
            self.run_button.config(state="disabled", cursor="no")
        else:
            self.sername_menu.config(state="readonly", cursor="hand2")
            self.path_button.config(state="normal", cursor="hand2")
            self.merge_button.config(state="normal", cursor="hand2")
            self.run_button.config(state="normal", cursor="hand2")

    def console_update(self, message, *args):
        self.console.config(state="normal")
        self.console.insert(tk.END, message, *args)
        self.console.yview(tk.END)
        self.console.config(state="disabled")

    def listen_clipboard(self):
        pyperclip.copy('')

        while True:
            clipboard = pyperclip.paste()

            if self.link_regular.match(clipboard) and clipboard not in self.add_record_url:
                self.add_record_url.add(clipboard)

                self.input_text.insert(tk.END, f"{clipboard}\n")
                pyperclip.copy('')
            time.sleep(0.3)

    def download(self, taskId, searchtext):
        process_name = self.illegal_regular.sub("-", searchtext if searchtext else taskId).strip()

        self.console_update(f"> {self.transl('開始下載')} [{process_name}]\n", "important")
        if not self.save_path.exists():
            self.save_path.mkdir(parents=True, exist_ok=True)

        dir_option = f"-dir \"{self.save_path / process_name}\""
        command = f"{self.depot_exe} -app 431960 -pubfile {taskId} -verify-all -username {self.username.get()} -password {self.passwords[self.username.get()]} {dir_option}"

        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,creationflags=subprocess.CREATE_NO_WINDOW)
        for line in process.stdout:
            self.console_update(line)
        process.stdout.close()
        process.wait()

        self.console_update(f"> [{process_name}] {self.transl('下載完成')} \n\n", "important")
        self.complete_record_id.add(taskId)

    def download_trigger(self):
        self.status_switch("disabled")

        def lines():
            while True:
                lines = self.input_text.get("1.0", "end").splitlines()
                if not lines or not lines[0].strip():
                    break
                self.input_text.delete("1.0", "2.0")
                yield unquote(lines[0]).strip()

        def trigger():
            for link in lines():
                if link:
                    match = self.parse_regular.search(link)
                    if match:
                        self.add_record_url.add(link)
                        if match.group(1) not in self.complete_record_id:
                            self.download(match.group(1), match.group(2))
                    else:
                        self.console_update(f"{self.transl('無效連結')}：{link}\n")

            self.status_switch("normal")

        threading.Thread(target=trigger).start()

    def Main(self):
        self.protocol("WM_DELETE_WINDOW", lambda: (subprocess.Popen("taskkill /f /im DepotDownloadermod.exe", creationflags=subprocess.CREATE_NO_WINDOW), os._exit(0)))
        self.mainloop()

if __name__ == "__main__":
    GUI().Main()