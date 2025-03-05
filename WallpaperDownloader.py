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
                "控制台輸出": "控制台输出",
                "輸入創意工坊專案（每行一個，支援連結和檔案ID）": "输入创意工坊项目（每行一个，支持链接和文件ID）",
                "下載": "下载",
                "選擇資料夾": "选择文件夹",
                "下載完成": "下载完成",
                "無效連結": "无效链接"
            },
            '1252': {
                "依賴錯誤": "Dependency error",
                "找不到": "Not found",
                "讀取配置文件時出錯": "Error reading configuration file",
                "創意工坊下載器": "Workshop Downloader",
                "選擇帳號": "Select account",
                "修改路徑": "Modify path",
                "控制台輸出": "Console output",
                "輸入創意工坊專案（每行一個，支援連結和檔案ID）": "Enter Workshop projects (one per line, supports links and file IDs)",
                "下載": "Download",
                "選擇資料夾": "Select folder",
                "下載完成": "Download complete",
                "無效連結": "Invalid link"
            }
        }

        lang = str(lang).replace('cp', '')
        ML = Word.get(lang) or Word.get('1252')
        return lambda text: ML.get(text) or text

class DLL:
    def __init__(self):
        self.folder = "Wallpaper_Output"
        self.current_dir = Path(sys.executable).parent if getattr(sys, 'frozen', False) else Path(__file__).parent

        self.save_path = Path(self.current_dir) / self.folder
        self.config_cfg = Path(self.current_dir) / "lastsavelocation.cfg"
        self.depot_exe = Path(self.current_dir) / "DepotdownloaderMod/DepotDownloadermod.exe"

        self.transl = language(locale.getlocale()[1])

        if not self.depot_exe.exists():
            messagebox.showerror(self.transl('依賴錯誤'), f"{self.transl('找不到')} {self.depot_exe}")
            os._exit(0)

        if self.config_cfg.exists():
            try:
                record_str = self.config_cfg.read_text().strip()
                record_path = Path(record_str)

                if record_path.is_absolute():
                    self.save_path = record_path if record_path.name == self.folder else record_path / self.folder
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

class GUI(DLL, tk.Tk):
    def __init__(self):
        DLL.__init__(self)
        tk.Tk.__init__(self, className=f"Wallpaper Engine {self.transl('創意工坊下載器')}")

        self.geometry("600x650")
        self.minsize(500, 550)

        try:
            Icon = Path(self.current_dir) / "Icon/DepotDownloader.ico"
            self.iconbitmap(Icon)
        except: pass

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.primary_color = "#383d48"
        self.secondary_color = "#afd4ff"
        self.text_color = "#ffffff"
        self.configure(bg=self.primary_color)

        self.top_frame = tk.Frame(self, bg=self.primary_color)
        self.top_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        self.top_frame.columnconfigure(1, weight=0)
        self.settings_element()

        self.middle_frame = tk.Frame(self, bg=self.primary_color)
        self.middle_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        self.middle_frame.rowconfigure(1, weight=1)
        self.middle_frame.columnconfigure(0, weight=1)
        self.display_element()

        self.bottom_frame = tk.Frame(self, bg=self.primary_color)
        self.bottom_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=5)
        self.bottom_frame.columnconfigure(0, weight=1)
        self.input_element()

    def settings_element(self):
        username_label = tk.Label(self.top_frame, text=f"{self.transl('選擇帳號')}：", font=("Microsoft JhengHei", 14, "bold"), bg=self.primary_color, fg=self.text_color)
        username_label.grid(row=0, column=0, sticky="w", padx=(0, 10), pady=(10, 10))

        self.username = tk.StringVar(self)
        self.username.set(self.acclist[0])
        self.sername_menu = ttk.Combobox(self.top_frame, textvariable=self.username, font=("Microsoft JhengHei", 10), cursor="hand2", justify="center", state="readonly", values=self.acclist)
        self.sername_menu.grid(row=0, column=1, sticky="ew", padx=(0, 350))

        self.path_button = tk.Button(self.top_frame, text=self.transl('修改路徑'), font=("Microsoft JhengHei", 10, "bold"), cursor="hand2", relief="flat", bg=self.secondary_color, fg=self.text_color, command=self.save_settings)
        self.path_button.grid(row=1, column=0, sticky="w")

        self.save_path_label = tk.Label(self.top_frame, text=self.save_path, font=("Microsoft JhengHei", 14, "bold"), bg=self.primary_color, fg=self.text_color)
        self.save_path_label.grid(row=1, column=1, sticky="w")

    def display_element(self):
        console_label = tk.Label(self.middle_frame, text=f"{self.transl('控制台輸出')}：", font=("Microsoft JhengHei", 10, "bold"), bg=self.primary_color, fg=self.text_color)
        console_label.grid(row=0, column=0, sticky="nsew")

        self.console = scrolledtext.ScrolledText(self.middle_frame, font=("Microsoft JhengHei", 12, "bold"), height=14, borderwidth=1, cursor="arrow", relief="sunken", state="disabled")
        self.console.grid(row=1, column=0, sticky="nsew")

    def input_element(self):
        input_label = tk.Label(self.bottom_frame, text=f"{self.transl('輸入創意工坊專案（每行一個，支援連結和檔案ID）')}：", font=("Microsoft JhengHei", 10, "bold"), bg=self.primary_color, fg=self.text_color)
        input_label.grid(row=0, column=0, sticky="nsew")

        self.input_text = scrolledtext.ScrolledText(self.bottom_frame, font=("Microsoft JhengHei", 10, "bold"), height=7, borderwidth=1, relief="sunken")
        self.input_text.grid(row=1, column=0, sticky="nsew", pady=8)
        threading.Thread(target=self.listen_clipboard).start()

        self.run_button = tk.Button(self.bottom_frame, text=self.transl('下載'), font=("Microsoft JhengHei", 10, "bold"), borderwidth=2, cursor="hand2", relief="flat", bg=self.secondary_color, fg=self.text_color, command=self.download_trigger)
        self.run_button.grid(row=2, column=0, sticky="ew")

    def status_switch(self, state):
        if state == "disabled":
            self.sername_menu.config(state="disabled", cursor="no")
            self.path_button.config(state="disabled", cursor="no")
            self.run_button.config(state="disabled", cursor="no")
        else:
            self.sername_menu.config(state="readonly", cursor="hand2")
            self.path_button.config(state="normal", cursor="hand2")
            self.run_button.config(state="normal", cursor="hand2")

    def save_settings(self):
        path = filedialog.askdirectory(title=self.transl('選擇資料夾'))

        if path:
            self.save_path = Path(path) / self.folder
            self.save_path_label.config(text=self.save_path)
            self.config_cfg.write_text(str(self.save_path), encoding="utf-8")

    def console_update(self, message):
        self.console.config(state="normal")
        self.console.insert(tk.END, message)
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

        self.console_update(f"----- {self.transl('開始下載')} [{process_name}] -----\n")
        if not self.save_path.exists():
            self.save_path.mkdir(parents=True, exist_ok=True)

        dir_option = f"-dir \"{self.save_path / process_name}\""
        command = f"{self.depot_exe} -app 431960 -pubfile {taskId} -verify-all -username {self.username.get()} -password {self.passwords[self.username.get()]} {dir_option}"

        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,creationflags=subprocess.CREATE_NO_WINDOW)
        for line in process.stdout:
            self.console_update(line)
        process.stdout.close()
        process.wait()

        self.console_update(f"----- [{process_name}] {self.transl('下載完成')} -----\n\n")
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
                            self.download(match.group(1).strip(), match.group(2).strip())
                    else:
                        self.console_update(f"{self.transl('無效連結')}：{link}\n")

            self.status_switch("normal")

        threading.Thread(target=trigger).start()

    def Main(self):
        self.protocol("WM_DELETE_WINDOW", lambda: (subprocess.Popen("taskkill /f /im DepotDownloadermod.exe", creationflags=subprocess.CREATE_NO_WINDOW), os._exit(0)))
        self.mainloop()

if __name__ == "__main__":
    GUI().Main()