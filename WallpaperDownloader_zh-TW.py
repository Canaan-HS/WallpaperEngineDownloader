import os
import re
import time
import base64
import threading
import pyperclip
import subprocess
import tkinter as tk

from tkinter import ttk
from pathlib import Path
from tkinter import scrolledtext, filedialog, messagebox

class DLL:
    def __init__(self):
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

        self.folder = "Wallpaper_Output"
        self.current_dir = Path(__file__).parent

        self.add_record_url = set()
        self.complete_record_id = set()
        self.pattern = re.compile(r"^https://steamcommunity\.com/sharedfiles/filedetails/\?id=\d+.*$")

        self.depot_exe = Path(self.current_dir) / "DepotdownloaderMod/DepotDownloadermod.exe"
        self.config_cfg = Path(self.current_dir) / "lastsavelocation.cfg"
        self.save_path = Path(self.current_dir) / self.folder

        if not self.depot_exe.exists():
            messagebox.showerror("依賴錯誤", f"找不到 {self.depot_exe}")
            os._exit(0)

        if self.config_cfg.exists():
            try:
                record_str = self.config_cfg.read_text().strip()
                record_path = Path(record_str)

                if record_path.is_absolute():
                    self.save_path = record_path if record_path.name == self.folder else record_path / self.folder
            except Exception as e:
                print(f"讀取配置文件時出錯: {e}")

class GUI(DLL, tk.Tk):
    def __init__(self):
        DLL.__init__(self)
        tk.Tk.__init__(self, className="Wallpaper Engine 創意工坊下載器")

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
        username_label = tk.Label(self.top_frame, text="選擇帳號:", font=("Microsoft JhengHei", 14, "bold"), bg=self.primary_color, fg=self.text_color)
        username_label.grid(row=0, column=0, sticky="w", padx=(0, 10), pady=(10, 10))

        self.username = tk.StringVar(self)
        self.username.set(self.acclist[0])
        self.sername_menu = ttk.Combobox(self.top_frame, textvariable=self.username, font=("Microsoft JhengHei", 10), cursor="hand2", justify="center", state="readonly", values=self.acclist)
        self.sername_menu.grid(row=0, column=1, sticky="ew", padx=(0, 350))

        self.path_button = tk.Button(self.top_frame, text="修改路徑", font=("Microsoft JhengHei", 10, "bold"), cursor="hand2", relief="flat", bg=self.secondary_color, fg=self.primary_color, command=self.save_settings)
        self.path_button.grid(row=1, column=0, sticky="w")

        self.save_path_label = tk.Label(self.top_frame, text=self.save_path, font=("Microsoft JhengHei", 14, "bold"), bg=self.primary_color, fg=self.text_color)
        self.save_path_label.grid(row=1, column=1, sticky="w")

    def display_element(self):
        console_label = tk.Label(self.middle_frame, text="控制台輸出：", font=("Microsoft JhengHei", 10, "bold"), bg=self.primary_color, fg=self.text_color)
        console_label.grid(row=0, column=0, sticky="nsew")

        self.console = scrolledtext.ScrolledText(self.middle_frame, font=("Microsoft JhengHei", 12, "bold"), height=14, borderwidth=1, cursor="arrow", relief="sunken", state="disabled")
        self.console.grid(row=1, column=0, sticky="nsew")

    def input_element(self):
        input_label = tk.Label(self.bottom_frame, text="輸入創意工坊專案（每行一個，支援連結和檔案ID）:", font=("Microsoft JhengHei", 10, "bold"), bg=self.primary_color, fg=self.text_color)
        input_label.grid(row=0, column=0, sticky="nsew")

        self.input_text = scrolledtext.ScrolledText(self.bottom_frame, font=("Microsoft JhengHei", 10, "bold"), height=7, borderwidth=1, relief="sunken")
        self.input_text.grid(row=1, column=0, sticky="nsew", pady=8)
        threading.Thread(target=self.listen_clipboard).start()

        self.run_button = tk.Button(self.bottom_frame, text="下載", font=("Microsoft JhengHei", 10, "bold"), borderwidth=2, cursor="hand2", relief="flat", bg=self.secondary_color, fg=self.primary_color, command=self.download_trigger)
        self.run_button.grid(row=2, column=0, sticky="ew")

    def listen_clipboard(self):
        pyperclip.copy('')

        while True:
            clipboard = pyperclip.paste()

            if self.pattern.match(clipboard) and clipboard not in self.add_record_url:
                self.add_record_url.add(clipboard)

                self.input_text.insert(tk.END, f"{clipboard}\n")
                pyperclip.copy('')
            time.sleep(0.3)
        
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
        path = filedialog.askdirectory(title="選擇資料夾")

        if path:
            self.save_path = Path(path) / self.folder
            self.save_path_label.config(text=self.save_path)
            self.config_cfg.write_text(str(self.save_path), encoding="utf-8")

    def console_update(self, message):
        self.console.config(state="normal")
        self.console.insert(tk.END, message)
        self.console.yview(tk.END)
        self.console.config(state="disabled")

    def download(self, taskId):
        self.console_update(f"----- 開始下載 [{taskId}] -----\n")
        if not self.save_path.exists():
            self.console_update(f"錯誤：儲存位置不存在。\n")
            return

        dir_option = f"-dir \"{self.save_path / taskId}\""
        command = f"{self.depot_exe} -app 431960 -pubfile {taskId} -verify-all -username {self.username.get()} -password {self.passwords[self.username.get()]} {dir_option}"

        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,creationflags=subprocess.CREATE_NO_WINDOW)
        for line in process.stdout:
            self.console_update(line)
        process.stdout.close()
        process.wait()

        self.console_update(f"----- [{taskId}] 下載完成 -----\n\n")
        self.complete_record_id.add(taskId)
        
    def download_trigger(self):
        self.status_switch("disabled")
        self.save_path.mkdir(parents=True, exist_ok=True)

        def lines():
            while True:
                lines = self.input_text.get("1.0", "end").splitlines()
                if not lines or not lines[0].strip():
                    break
                self.input_text.delete("1.0", "2.0")
                yield lines[0].strip()

        def trigger():
            for link in lines():
                if link:
                    match = re.search(r'\b\d{8,10}\b', link)
                    if match:
                        self.add_record_url.add(link)
                        if match.group(0) not in self.complete_record_id:
                            self.download(match.group(0))
                    else:
                        self.console_update(f"無效連結：{link}\n")

            self.status_switch("normal")

        threading.Thread(target=trigger).start()

    def Main(self):
        self.protocol("WM_DELETE_WINDOW", lambda: (subprocess.Popen("taskkill /f /im DepotDownloadermod.exe", creationflags=subprocess.CREATE_NO_WINDOW), os._exit(0)))
        self.mainloop()

if __name__ == "__main__":
    GUI().Main()