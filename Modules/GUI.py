from .__Lib__ import *


class GUI:
    def __init__(self):  # 方便還原
        self.win_title = f"Wallpaper Engine {self.transl('創意工坊下載器')}"

        x = self.cfg_data.get(self.CK.X, 200)
        y = self.cfg_data.get(self.CK.Y, 200)
        width = self.cfg_data.get(self.CK.W, 600)
        height = self.cfg_data.get(self.CK.H, 700)

        self.title(self.win_title)
        self.minsize(350, 250)
        self.geometry(f"{width}x{height}+{x}+{y}")

        try:
            self.iconbitmap(self.icon_ico)
        except Exception as e:
            logging.warning(e)
            pass

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
        username_label = tk.Label(
            self.select_frame,
            text=f"{self.transl('選擇配置')}：",
            font=("Microsoft JhengHei", 14, "bold"),
            bg=self.primary_color,
            fg=self.text_color,
        )
        username_label.grid(row=0, column=0, sticky="w", padx=(0, 10), pady=(10, 10))

        self.username = tk.StringVar(self)
        self.username.set(
            f"{self.transl('帳號')}->{self.cfg_data.get(self.CK.Acc, self.acc_list[0])}"
        )  # 下面取用數據時, 會進行判斷是否存在, 這邊直接填充
        self.username_menu = ttk.Combobox(
            self.select_frame,
            textvariable=self.username,
            font=("Microsoft JhengHei", 10),
            width=15,
            cursor="hand2",
            justify="center",
            state="readonly",
            values=self.acc_list,
        )
        self.username_menu.grid(row=0, column=1, sticky="w", padx=(0, 20))

        self.serverid = tk.StringVar(self)
        self.serverid.set(
            f"{self.transl('應用')}->{self.cfg_data.get(self.CK.App, self.app_list[0])}"
        )
        self.serverid_menu = ttk.Combobox(
            self.select_frame,
            textvariable=self.serverid,
            font=("Microsoft JhengHei", 10),
            cursor="hand2",
            justify="center",
            values=self.app_list,
        )
        self.serverid_menu.grid(row=0, column=2, sticky="we")
        self.server_search()

        self.path_button = tk.Button(
            self.select_frame,
            text=self.transl("修改路徑"),
            font=("Microsoft JhengHei", 10, "bold"),
            cursor="hand2",
            relief="raised",
            bg=self.secondary_color,
            fg=self.text_color,
            command=self.save_settings,
        )
        self.path_button.grid(row=1, column=0, sticky="w")

        self.save_path_label = tk.Label(
            self.select_frame,
            text=self.save_path,
            font=("Microsoft JhengHei", 14, "bold"),
            cursor="hand2",
            anchor="w",
            justify="left",
            bg=self.primary_color,
            fg=self.text_color,
        )
        self.save_path_label.grid(row=1, column=1, columnspan=2, sticky="w")
        self.save_path_label.bind("<Button-1>", self.copy_save_path)

        self.merge_button = tk.Button(
            self.select_frame,
            text=self.transl("檔案整合"),
            font=("Microsoft JhengHei", 10, "bold"),
            cursor="hand2",
            relief="raised",
            bg=self.secondary_color,
            fg=self.text_color,
            command=self.file_merge,
        )
        self.merge_button.grid(row=2, column=0, sticky="w", pady=(15, 0))

    def display_element(self):
        console_label = tk.Label(
            self.console_frame,
            text=f"{self.transl('控制台輸出')}：",
            font=("Microsoft JhengHei", 10, "bold"),
            bg=self.primary_color,
            fg=self.text_color,
        )
        console_label.grid(row=0, column=0, sticky="nsew")

        self.console = scrolledtext.ScrolledText(
            self.console_frame,
            font=("Consolas", 12),
            height=16,
            borderwidth=4,
            cursor="arrow",
            relief="sunken",
            state="disabled",
            bg=self.consolo_color,
            fg=self.text_color,
        )
        self.console.tag_configure("important", foreground="#00DB00", font=("Consolas", 12, "bold"))
        self.console.grid(row=1, column=0, sticky="nsew")

    def input_element(self):
        input_label = tk.Label(
            self.operate_frame,
            text=f"{self.transl('輸入創意工坊專案（每行一個，支援連結和檔案ID）')}：",
            font=("Microsoft JhengHei", 10, "bold"),
            bg=self.primary_color,
            fg=self.text_color,
        )
        input_label.grid(row=0, column=0, sticky="nsew")

        self.input_text = scrolledtext.ScrolledText(
            self.operate_frame,
            font=("Microsoft JhengHei", 10, "bold"),
            borderwidth=2,
            relief="sunken",
            wrap="none",
        )
        self.input_text.grid(row=1, column=0, sticky="nsew")
        threading.Thread(target=self.listen_clipboard, daemon=True).start()

        for task in self.cfg_data.get(self.CK.Task, []):  # 添加舊任務數據
            self.input_text.insert("end", f"{task}\n")

        self.run_button = tk.Button(
            self.operate_frame,
            text=self.transl("下載"),
            font=("Microsoft JhengHei", 14, "bold"),
            borderwidth=2,
            cursor="hand2",
            relief="raised",
            bg=self.secondary_color,
            fg=self.text_color,
            command=lambda: threading.Thread(target=self.download_trigger, daemon=True).start(),
        )
        self.run_button.grid(row=2, column=0, sticky="ew", pady=(12, 5))
