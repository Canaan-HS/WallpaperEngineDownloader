from ..bootstrap import (
    tk,
    ttk,
    Path,
    logging,
    filedialog,
    scrolledtext,
    messagebox,
    threading,
    pyperclip,
)

from ..core import shared
from ..language import translator
from ..utils import account_list, get_ext_groups


class UI_Main:
    def __init__(self):  # 方便還原
        self.win_title = f"Wallpaper Engine {shared.transl('創意工坊下載器')}"

        x = shared.cfg_data.get(shared.ck.X, 200)
        y = shared.cfg_data.get(shared.ck.Y, 200)
        width = shared.cfg_data.get(shared.ck.W, 600)
        height = shared.cfg_data.get(shared.ck.H, 700)

        self.title(self.win_title)
        self.minsize(350, 250)
        self.geometry(f"{width}x{height}+{x}+{y}")

        try:
            self.iconbitmap(shared.icon_ico)
        except Exception as e:
            logging.warning(e)
            pass

        # 開啟時 窗口置頂 (非鎖定)
        self.attributes("-topmost", True)
        self.update()
        self.attributes("-topmost", False)

        self.primary_color = "#383d48"
        self.consolo_color = "#272727"
        self.secondary_color = "#4dabf7"
        self.text_color = "#ffffff"
        self.configure(bg=self.primary_color)

        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=0)
        self.rowconfigure(2, weight=0)
        self.rowconfigure(3, weight=0)
        self.rowconfigure(4, weight=1)
        self.rowconfigure(5, weight=0)
        self.columnconfigure(0, weight=1)

        # 選擇配置
        self.title_frame = tk.Frame(self, bg=self.primary_color)
        self.title_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        self.title_frame.columnconfigure(0, weight=1)

        # 下拉選單
        self.menus_frame = tk.Frame(self, bg=self.primary_color)
        self.menus_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        self.menus_frame.columnconfigure(0, weight=0)
        self.menus_frame.columnconfigure(1, weight=0)
        self.menus_frame.columnconfigure(2, weight=1)

        # 按鈕框架
        self.buttons_frame = tk.Frame(self, bg=self.primary_color)
        self.buttons_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=5)
        self.buttons_frame.columnconfigure(0, weight=1)  # 左側彈性空間
        self.buttons_frame.columnconfigure(1, weight=0)  # 修改路徑
        self.buttons_frame.columnconfigure(2, weight=0)  # 檔案整合
        self.buttons_frame.columnconfigure(3, weight=0)  # 自動提取
        self.buttons_frame.columnconfigure(4, weight=1)  # 右側彈性空間

        # 路徑文本框架
        self.path_text_frame = tk.Frame(self, bg=self.primary_color)
        self.path_text_frame.grid(row=3, column=0, sticky="ew", padx=10, pady=5)
        self.path_text_frame.columnconfigure(0, weight=1)

        # 控制台框架
        self.console_frame = tk.Frame(self, bg=self.primary_color)
        self.console_frame.grid(row=4, column=0, sticky="nsew", padx=10, pady=5)
        self.console_frame.rowconfigure(1, weight=1)
        self.console_frame.columnconfigure(0, weight=1)

        # 操作框架
        self.operate_frame = tk.Frame(self, bg=self.primary_color)
        self.operate_frame.grid(row=5, column=0, sticky="ew", padx=10, pady=5)
        self.operate_frame.rowconfigure(1, weight=1)
        self.operate_frame.columnconfigure(0, weight=1)

        self.settings_element()
        self.display_element()
        self.input_element()

        shared.msg.connect(lambda: self.username_var.get().strip(), "username")
        shared.msg.connect(lambda: self.serverid_var.get().strip(), "serverid")

    """ ====== 主要元件 ====== """

    def settings_element(self):
        self.title_label = tk.Label(
            self.title_frame,
            text=shared.transl("選擇配置"),
            font=("Microsoft JhengHei", 16, "bold"),
            bg=self.primary_color,
            fg=self.text_color,
        )
        self.title_label.grid(row=0, column=0)

        self.language_var = tk.StringVar(self)
        self.language_var.set(shared.transl(shared.set_lang))

        self.init_language_rules()
        self.language_menu = ttk.Combobox(
            self.menus_frame,
            textvariable=self.language_var,
            font=("Microsoft JhengHei", 10),
            width=12,
            cursor="hand2",
            justify="center",
            state="readonly",
            values=list(self.language_rules.keys()),
        )
        self.language_menu.grid(row=0, column=0, sticky="w", padx=(0, 10))
        self.language_menu.bind("<<ComboboxSelected>>", self.language_select)

        self.username_var = tk.StringVar(self)
        self.username_var.set(
            f"{shared.transl('帳號')}->{shared.cfg_data.get(shared.ck.Acc, account_list[0])}"
        )
        self.username_menu = ttk.Combobox(
            self.menus_frame,
            textvariable=self.username_var,
            font=("Microsoft JhengHei", 10),
            width=15,
            cursor="hand2",
            justify="center",
            state="readonly",
            values=account_list,
        )
        self.username_menu.grid(row=0, column=1, sticky="w", padx=(0, 10))

        self.serverid_var = tk.StringVar(self)
        self.serverid_var.set(
            f"{shared.transl('應用')}->{shared.cfg_data.get(shared.ck.App, self.app_list[0])}"
        )
        self.serverid_menu = ttk.Combobox(
            self.menus_frame,
            textvariable=self.serverid_var,
            font=("Microsoft JhengHei", 10),
            cursor="hand2",
            justify="center",
            values=self.app_list,
        )
        self.serverid_menu.grid(row=0, column=2, sticky="we")
        self.search_operat()

        self.path_button = tk.Button(
            self.buttons_frame,
            text=shared.transl("修改路徑"),
            font=("Microsoft JhengHei", 10, "bold"),
            cursor="hand2",
            relief="raised",
            bg=self.secondary_color,
            fg=self.text_color,
            command=self.set_save_path,
        )
        self.path_button.grid(row=0, column=1, padx=5, pady=5)

        self.merge_button = tk.Button(
            self.buttons_frame,
            text=shared.transl("檔案整合"),
            font=("Microsoft JhengHei", 10, "bold"),
            cursor="hand2",
            relief="raised",
            bg=self.secondary_color,
            fg=self.text_color,
            command=self.file_merge,
        )
        self.merge_button.grid(row=0, column=2, padx=5, pady=5)

        self.extract_pkg_var = tk.BooleanVar(value=False)
        self.extract_pkg_var.set(shared.enable_extract_pkg)
        self.extract_pkg_button = tk.Checkbutton(
            self.buttons_frame,
            text=shared.transl("提取 PKG 文件"),
            variable=self.extract_pkg_var,
            font=("Microsoft JhengHei", 11, "bold"),
            bg=self.primary_color,
            fg=self.text_color,
            selectcolor=self.primary_color,
            activebackground=self.primary_color,
            activeforeground=self.text_color,
            cursor="hand2",
            padx=5,
            pady=5,
            command=self.set_pkg_extract,
        )
        self.extract_pkg_button.grid(row=0, column=3, padx=5, pady=5)

        path_display_frame = tk.Frame(
            self.path_text_frame,
            bg=self.primary_color,
            borderwidth=2,
            cursor="hand2",
            relief="raised",
        )
        path_display_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        self.save_path_label = tk.Label(
            path_display_frame,
            text=shared.save_path,
            font=("Microsoft JhengHei", 15, "bold"),
            cursor="hand2",
            bg=self.primary_color,
            fg=self.text_color,
        )
        self.save_path_label.pack(padx=10, pady=5)

        path_display_frame.bind("<Button-1>", self.copy_save_path)
        self.save_path_label.bind("<Button-1>", self.copy_save_path)

    def display_element(self):
        self.console_label = tk.Label(
            self.console_frame,
            text=f"{shared.transl('控制台輸出')}：",
            font=("Microsoft JhengHei", 10, "bold"),
            bg=self.primary_color,
            fg=self.text_color,
            anchor="center",
        )
        self.console_label.grid(row=0, column=0, sticky="nsew")

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
        self.input_label = tk.Label(
            self.operate_frame,
            text=f"{shared.transl('輸入創意工坊專案（每行一個，支援連結和檔案ID）')}：",
            font=("Microsoft JhengHei", 10, "bold"),
            bg=self.primary_color,
            fg=self.text_color,
            anchor="center",
        )
        self.input_label.grid(row=0, column=0, sticky="nsew")

        self.input_text = scrolledtext.ScrolledText(
            self.operate_frame,
            font=("Microsoft JhengHei", 10, "bold"),
            height=8,
            borderwidth=2,
            relief="sunken",
            wrap="none",
        )
        self.input_text.grid(row=1, column=0, sticky="nsew")
        self.after(
            100, self.listen_clipboard
        )  # 避免初始化的微小延遲, 進行延遲排程 (可直接調用, 但會有微小延遲)

        for task in shared.cfg_data.get(shared.ck.Task, []):  # 添加舊任務數據
            self.capture_record.add(task)  # 避免複製移動位置時擷取
            self.input_operat("insert", f"{task}\n")

        self.run_button = tk.Button(
            self.operate_frame,
            text=shared.transl("下載"),
            font=("Microsoft JhengHei", 14, "bold"),
            borderwidth=2,
            cursor="hand2",
            relief="raised",
            bg=self.secondary_color,
            fg=self.text_color,
            command=lambda: threading.Thread(target=self.download_trigger, daemon=True).start(),
        )
        self.run_button.grid(row=2, column=0, sticky="ew", pady=(12, 5))

    """ ====== 互動功能 ====== """

    def set_pkg_extract(self):
        shared.enable_extract_pkg = self.extract_pkg_var.get()

    def set_save_path(self):
        path = filedialog.askdirectory(
            title=shared.transl("選擇資料夾"), initialdir=shared.save_path
        )

        if path:
            shared.save_path = Path(path) / shared.output_folder
            self.save_path_label.config(text=shared.save_path)
            shared.save_config({"Sava_Path": str(shared.save_path)})

    def copy_save_path(self, event):
        pyperclip.copy(shared.save_path)

        popup = tk.Toplevel(self)
        popup.overrideredirect(True)
        popup.attributes("-topmost", True)

        label = tk.Label(
            popup,
            text=shared.transl("已複製"),
            font=("Microsoft JhengHei", 10),
            bg="#333333",
            fg="#FFFFFF",
            padx=5,
            pady=5,
        )
        label.pack()

        popup.update_idletasks()  # 更新窗口以計算 label 的大小
        popup.geometry(
            f"{label.winfo_reqwidth()}x{label.winfo_reqheight()}+{event.x_root - 25}+{event.y_root - 35}"
        )

        popup.grab_set()
        popup.after(800, popup.destroy)

    def init_language_rules(self):
        self.language_rules = {
            shared.transl("en_US"): "en_US",
            shared.transl("zh_TW"): "zh_TW",
            shared.transl("zh_CN"): "zh_CN",
        }

    def language_select(self, _):
        selected = self.language_rules[self.language_var.get()]

        if selected != shared.set_lang:
            shared.transl, shared.set_lang = translator(selected)  # 更新翻譯

            # 主 UI 更新
            self.win_title = f"Wallpaper Engine {shared.transl('創意工坊下載器')}"
            self.title(self.win_title)

            self.title_label.config(text=shared.transl("選擇配置"))

            self.init_language_rules()
            self.language_var.set(shared.transl(shared.set_lang))
            self.language_menu.config(values=list(self.language_rules.keys()))

            self.username_var.set(
                f"{shared.transl('帳號')}->{shared.cfg_data.get(shared.ck.Acc, account_list[0])}"
            )

            self.serverid_var.set(
                f"{shared.transl('應用')}->{shared.cfg_data.get(shared.ck.App, self.app_list[0])}"
            )

            self.path_button.config(text=shared.transl("修改路徑"))
            self.merge_button.config(text=shared.transl("檔案整合"))
            self.extract_pkg_button.config(text=shared.transl("提取 PKG 文件"))
            self.run_button.config(text=shared.transl("下載"))

            self.console_label.config(text=f"{shared.transl('控制台輸出')}：")
            self.input_label.config(
                text=f"{shared.transl('輸入創意工坊專案（每行一個，支援連結和檔案ID）')}："
            )

            # 後端數據更新
            self.init_error_rule()

    def file_merge(self):
        data_table = get_ext_groups(shared.save_path, shared.integrate_folder)

        if data_table:
            merge_window = tk.Toplevel(self)
            merge_window.title(shared.transl("檔案整合"))
            merge_window.configure(bg=self.primary_color)

            try:
                merge_window.iconbitmap(shared.icon_ico)
            except Exception as e:
                logging.warning(e)
                pass

            width = 500
            height = 550

            merge_window.geometry(
                f"{width}x{height}+{int((self.winfo_screenwidth() - width) / 2)}+{int((self.winfo_screenheight() - height) / 2)}"
            )
            merge_window.minsize(400, 450)

            tip_frame = tk.Frame(merge_window, bg=self.primary_color)
            tip_frame.pack(fill="x", padx=10, pady=10)
            tip = tk.Label(
                tip_frame,
                text=shared.transl("選擇整合的類型"),
                font=("Microsoft JhengHei", 18, "bold"),
                bg=self.primary_color,
                fg=self.text_color,
            )
            tip.pack()

            display_frame = tk.Frame(merge_window, bg=self.primary_color)
            display_frame.pack(fill="both", expand=True, padx=10, pady=10)

            output_frame = tk.Frame(merge_window, bg=self.primary_color)
            output_frame.pack(fill="x")

            scroll_y = tk.Scrollbar(display_frame, orient="vertical")
            scroll_y.pack(side="right", fill="y")

            style = ttk.Style()
            style.configure(
                "Custom.Treeview",
                font=("Microsoft JhengHei", 14, "bold"),
                foreground=self.text_color,
                background=self.consolo_color,
                rowheight=30,
            )
            style.configure(
                "Custom.Treeview.Heading",
                font=("Microsoft JhengHei", 16, "bold"),
                foreground="#0066CC",
            )

            treeview = ttk.Treeview(
                display_frame,
                columns=("Type", "Count"),
                show="headings",
                yscrollcommand=scroll_y.set,
                cursor="hand2",
                style="Custom.Treeview",
            )
            treeview.heading("Type", text=shared.transl("檔案類型"))
            treeview.heading("Count", text=shared.transl("檔案數量"))
            treeview.column("Type", anchor="center")
            treeview.column("Count", anchor="center")

            for key, value in data_table.items():
                treeview.insert("", "end", values=(key, len(value)))

            scroll_y.config(command=treeview.yview)
            treeview.pack(fill="both", expand=True)

            output_button = tk.Button(
                output_frame,
                text=shared.transl("整合輸出"),
                font=("Microsoft JhengHei", 12, "bold"),
                borderwidth=2,
                cursor="hand2",
                relief="raised",
                bg=self.secondary_color,
                fg=self.text_color,
                command=self.move_trigger,
            )
            output_button.pack(pady=(5, 15))

        else:
            messagebox.showwarning(
                title=shared.transl("獲取失敗"),
                message=shared.transl("沒有可整合的檔案"),
                parent=self,
            )
