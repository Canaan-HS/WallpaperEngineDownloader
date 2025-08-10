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
from ..utils import account_list, get_ext_groups
from ..core import shared


class UI:
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

    """ ====== 主要元件 ====== """

    def settings_element(self):
        # ! GUI 的顯示值是直接取用 cfg 的數據, 不會驗證該參數是否存在, 當手動修改 cfg 時 就算不存在也會顯示
        # ! 只會在後端 get_config 時進行驗證

        username_label = tk.Label(
            self.select_frame,
            text=f"{shared.transl('選擇配置')}：",
            font=("Microsoft JhengHei", 14, "bold"),
            bg=self.primary_color,
            fg=self.text_color,
        )
        username_label.grid(row=0, column=0, sticky="w", padx=(0, 10), pady=(10, 10))

        self.username = tk.StringVar(self)
        self.username.set(
            f"{shared.transl('帳號')}->{shared.cfg_data.get(shared.ck.Acc, account_list[0])}"
        )  # 下面取用數據時, 會進行判斷是否存在, 這邊直接填充
        self.username_menu = ttk.Combobox(
            self.select_frame,
            textvariable=self.username,
            font=("Microsoft JhengHei", 10),
            width=15,
            cursor="hand2",
            justify="center",
            state="readonly",
            values=account_list,
        )
        self.username_menu.grid(row=0, column=1, sticky="w", padx=(0, 20))

        self.serverid = tk.StringVar(self)
        self.serverid.set(
            f"{shared.transl('應用')}->{shared.cfg_data.get(shared.ck.App, self.app_list[0])}"
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
            text=shared.transl("修改路徑"),
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
            text=shared.save_path,
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
            text=shared.transl("檔案整合"),
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
            text=f"{shared.transl('控制台輸出')}：",
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
            text=f"{shared.transl('輸入創意工坊專案（每行一個，支援連結和檔案ID）')}：",
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
        self.after(
            100, self.listen_clipboard
        )  # 避免初始化的微小延遲, 進行延遲排程 (可直接調用, 但會有微小延遲)

        for task in shared.cfg_data.get(shared.ck.Task, []):  # 添加舊任務數據
            self.capture_record.add(task)  # 避免複製移動位置時擷取
            self.input_text.insert("end", f"{task}\n")
        self.input_text.xview_moveto(1.0)  # 將滾動條移至最右

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

    """ ====== 其餘功能 ====== """

    def save_settings(self):
        path = filedialog.askdirectory(title=shared.transl("選擇資料夾"))

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

            def move_trigger():
                if len(treeview.selection()) == 0:
                    messagebox.showwarning(
                        title=shared.transl("操作提示"),
                        message=shared.transl("請選擇要整合的類型"),
                        parent=merge_window,
                    )
                    return

                selected = []
                selected_items = treeview.selection()

                for item in selected_items:
                    values = treeview.item(item, "values")  # 取得對應的數據
                    selected.append(values[0])

                confirm = messagebox.askquestion(
                    shared.transl("操作確認"),
                    f"{shared.transl('整合以下類型的檔案')}?\n\n{selected}",
                    parent=merge_window,
                )

                if confirm == "yes":

                    def merge_success_show(merge_path):
                        messagebox.showinfo(
                            title=shared.transl("操作完成"),
                            message=f"{shared.transl('檔案整合完成')}\n{merge_path}",
                            parent=merge_window,
                        )

                        for item in selected_items:  # 移除選中的項目
                            treeview.delete(item)

                    shared.msg.connect(merge_success_show, True)
                    self.move_files(data_table, selected)

            output_button = tk.Button(
                output_frame,
                text=shared.transl("整合輸出"),
                font=("Microsoft JhengHei", 12, "bold"),
                borderwidth=2,
                cursor="hand2",
                relief="raised",
                bg=self.secondary_color,
                fg=self.text_color,
                command=move_trigger,
            )
            output_button.pack(pady=(5, 15))

        else:
            messagebox.showwarning(
                title=shared.transl("獲取失敗"),
                message=shared.transl("沒有可整合的檔案"),
                parent=self,
            )
