from .__Lib__ import *


class Backend:
    def __init__(self):
        self.account_dict = {
            key: {key: base64.b64decode(value).decode("utf-8")}
            for key, value in {
                "ruiiixx": "UzY3R0JUQjgzRDNZ",
                "premexilmenledgconis": "M3BYYkhaSmxEYg==",
                "vAbuDy": "Qm9vbHE4dmlw",
                "adgjl1182": "UUVUVU85OTk5OQ==",
                "gobjj16182": "enVvYmlhbzgyMjI=",
                "787109690": "SHVjVXhZTVFpZzE1",
            }.items()
        }

        self.clean_text = lambda text: text.split("->")[-1]

        # 緩存任務數據 用於未完成恢復
        self.task_cache = {}

        # 除重用
        self.capture_record = set()
        self.complete_record = set()

        self.app_list = list(self.appid_dict.keys())
        self.acc_list = list(self.account_dict.keys())

        self.illegal_regular = re.compile(r'[<>:"/\\|?*\x00-\x1F]')
        self.parse_regular = re.compile(r"(\d{8,10})(?:&searchtext=(.*))?")
        self.link_regular = re.compile(
            r"^https://steamcommunity\.com/sharedfiles/filedetails/\?id=\d+.*$"
        )

        self.token = True  # 可強制停止所有任務
        self.error_rule = {
            ".NET": self.transl("下載失敗: 請先安裝 .NET 9 執行庫"),
            "Unable to locate manifest ID for published file": self.transl(
                "下載失敗: 該項目可能已被刪除，或應用設置錯誤"
            ),
            # 列表為可觸發強制停止任務
            **dict.fromkeys(
                ["STEAM GUARD", "Authentication", "AccountDisabled"],
                self.transl("下載失敗: 請嘗試變更帳號後再下載"),
            ),
        }

    """ ====== 設定保存位置 ====== """

    def save_settings(self):
        path = filedialog.askdirectory(title=self.transl("選擇資料夾"))

        if path:
            self.save_path = Path(path) / self.output_folder
            self.save_path_label.config(text=self.save_path)
            self.save_config({"Sava_Path": str(self.save_path)})

    """ ====== 下載 數據處理/觸發 ====== """

    def get_config(self, original=False):
        username, password = next(
            iter(
                self.account_dict.get(
                    self.clean_text(self.username.get()),
                    self.account_dict.get(self.account),
                ).items()
            )
        )

        if original:
            for app in [self.clean_text(self.serverid.get()), self.app_list[0]]:
                if app in self.appid_dict:
                    return username, app
        else:
            appid = self.appid_dict.get(
                self.clean_text(self.serverid.get()), next(iter(self.appid_dict.values()))
            )
            return appid, username, password

    def input_stream(self):
        while True:
            lines = self.input_text.get("1.0", "end").splitlines()
            if not lines or not lines[0].strip():
                break  # 避免空數據
            self.input_text.delete("1.0", "2.0")
            yield unquote(lines[0]).strip()

    def download_trigger(self):
        self.status_switch("disabled")

        for link in self.input_stream():
            if link:
                match = self.parse_regular.search(link)
                if match:
                    appid, username, password = self.get_config()  # 允許臨時變更, 所以每次重獲取
                    self.capture_record.add(link)

                    match_gp1 = match.group(1)
                    task_id = f"{appid}-{match_gp1}"

                    if task_id not in self.complete_record:
                        self.task_cache[task_id] = {"url": link}
                        self.download(
                            task_id,
                            appid,
                            match_gp1,
                            match.group(2),
                            username,
                            password,
                        )
                else:
                    self.console_update(f"{self.transl('無效連結')}：{link}\n")

        self.status_switch("normal")

    """ ====== 下載處理核心 ====== """

    def console_analysis(self, text):
        for Key, message in self.error_rule.items():
            if Key in text:
                return message

    def console_update(self, message, *args):
        self.console.config(state="normal")
        self.console.insert("end", message, *args)
        self.console.yview("end")
        self.console.config(state="disabled")

    def get_unique_path(self, path):
        index = 1
        [parent, stem, suffix] = path.parent, path.stem, path.suffix
        while path.exists():
            path = parent / f"{stem} ({index}){suffix}"
            index += 1
        return path

    def status_switch(self, state):
        if state == "disabled":
            self.merge_button.config(state="disabled", cursor="no")
            self.run_button.config(state="disabled", cursor="no")
        else:
            self.token = True  # 重設令牌
            pyperclip.copy("")  # 重設剪貼簿 避免 record 清除後再次擷取
            self.title(self.win_title)  # 重設標題
            # self.capture_record.clear()

            if self.task_cache:
                self.process_cleanup()

                self.input_text.delete("1.0", "end")
                for task in self.task_cache.values():
                    self.input_text.insert("end", f"{task['url']}\n")
                self.task_cache.clear()  # 重設任務緩存

            self.merge_button.config(state="normal", cursor="hand2")
            self.run_button.config(state="normal", cursor="hand2")

    def download(self, taskId, appId, pubId, searchText, Username, Password):
        if not self.token:
            return

        try:
            full_download = False
            end_message = self.transl("下載完成")
            process_name = self.illegal_regular.sub(
                "-", searchText if searchText else pubId
            ).strip()

            self.console_update(f"\n> {self.transl('開始下載')} [{process_name}]\n", "important")

            if not self.save_path.exists():
                self.save_path.mkdir(parents=True, exist_ok=True)

            task_path = self.get_unique_path(self.save_path / process_name)
            self.task_cache[taskId]["path"] = task_path  # 再添加下載路徑

            # 避免 Command Injection
            command = [
                self.depot_exe,
                "-app",
                appId,
                "-pubfile",
                pubId,
                "-username",
                Username,
                "-password",
                Password,
                "-dir",
                task_path,
                "-max-downloads",
                "16",
                "-validate",
            ]

            process = subprocess.Popen(
                command,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                creationflags=subprocess.CREATE_NO_WINDOW,
            )

            threading.Thread(target=self.listen_network, args=(process,), daemon=True).start()
            for line in process.stdout:
                if line.strip() == "":
                    continue

                self.console_update(line)

                # 分析可能的錯誤訊息, 消息是列表狀態, 代表需要強制中止
                err_message = self.console_analysis(line)
                if isinstance(err_message, list):
                    self.token = False
                    process.terminate()
                    end_message = err_message[0]
                    return

                elif err_message:
                    end_message = err_message

                # 分析是否有下載完成, 字串
                if "Total downloaded" in line:
                    full_download = True

            process.stdout.close()
            process.wait()

            # 雖然可能不需要這麼多檢測, 但避免例外
            if (
                full_download
                and end_message == self.transl("下載完成")
                and Path(task_path).exists()
            ):
                self.task_cache.pop(taskId, None)  # 刪除任務緩存
                self.complete_record.add(taskId)  # 添加下載完成紀錄

                # 允許 repkg 且 appId 為 Wallpaper Engine 的 ID, 觸發提取
                if self.repkg and appId == "431960":
                    threading.Thread(
                        target=self.extract_pkg, args=(task_path,), daemon=True
                    ).start()
            else:
                # 進程可能還需要繼續, 不刪除錯誤的文件
                # 用於顯示不在 console_analysis 中的錯誤
                end_message = (
                    end_message
                    if end_message != self.transl("下載完成")
                    else self.transl("下載失敗")
                )

            self.console_update(f"> [{process_name}] {end_message}\n", "important")
        except:
            self.console_update(f"> {self.transl('例外中止')}\n", "important")

            exception = traceback.format_exc()
            logging.error(exception)
            messagebox.showerror(self.transl("例外"), exception, parent=self)

    """ ====== 檔案整合 ====== """

    def get_path_data(self, path: Path):
        file_data = defaultdict(list)
        for file in path.rglob("*"):
            # 取用是檔案, 且父資料夾 不是 整合資料夾
            if file.is_file() and self.integrate_folder not in file.parts:
                # ! 針對不是 file 但卻通過檢查 例外, 進行二次檢查 副檔名不為空字串
                suffix = file.suffix.strip()
                if suffix:  # key 為不含 . 的副檔名, value 為檔案列表
                    file_data[suffix[1:]].append(file)
        return dict(  # 數量多到少排序, 相同數量按字母排序, 組合 key 為副檔名, value 為檔案列表 回傳字典
            sorted(file_data.items(), key=lambda item: (-len(item[1]), item[0]))
        )

    def file_merge(self):
        data_table = self.get_path_data(self.save_path)

        if data_table:
            merge_window = tk.Toplevel(self)
            merge_window.title(self.transl("檔案整合"))
            merge_window.configure(bg=self.primary_color)

            try:
                merge_window.iconbitmap(self.icon_ico)
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
                text=self.transl("選擇整合的類型"),
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
            treeview.heading("Type", text=self.transl("檔案類型"))
            treeview.heading("Count", text=self.transl("檔案數量"))
            treeview.column("Type", anchor="center")
            treeview.column("Count", anchor="center")

            for key, value in data_table.items():
                treeview.insert("", "end", values=(key, len(value)))

            scroll_y.config(command=treeview.yview)
            treeview.pack(fill="both", expand=True)

            def move_save_file():
                if len(treeview.selection()) == 0:
                    messagebox.showwarning(
                        title=self.transl("操作提示"),
                        message=self.transl("請選擇要整合的類型"),
                        parent=merge_window,
                    )
                    return

                selected = []
                selected_items = treeview.selection()

                for item in selected_items:
                    values = treeview.item(item, "values")  # 取得對應的數據
                    selected.append(values[0])

                confirm = messagebox.askquestion(
                    self.transl("操作確認"),
                    f"{self.transl('整合以下類型的檔案')}?\n\n{selected}",
                    parent=merge_window,
                )
                if confirm == "yes":
                    for item in selected_items:  # 移除選中的項目
                        treeview.delete(item)

                    merge_path = self.save_path / self.integrate_folder
                    merge_path.mkdir(parents=True, exist_ok=True)
                    move_file = [data_table[select] for select in selected]

                    for files in move_file:
                        for file in files:
                            relative_path = file.relative_to(
                                self.save_path
                            )  # 獲取 file 在 self.save_path 下的相對路徑
                            top_folder = relative_path.parts[0]  # 取得最上層資料夾名稱

                            try:
                                file.rename(merge_path / f"[{top_folder}] {file.name}")
                            except Exception as e:
                                logging.warning(e)

                    messagebox.showinfo(
                        title=self.transl("操作完成"),
                        message=f"{self.transl('檔案整合完成')}\n{merge_path}",
                        parent=merge_window,
                    )

            output_button = tk.Button(
                output_frame,
                text=self.transl("整合輸出"),
                font=("Microsoft JhengHei", 12, "bold"),
                borderwidth=2,
                cursor="hand2",
                relief="raised",
                bg=self.secondary_color,
                fg=self.text_color,
                command=move_save_file,
            )
            output_button.pack(pady=(5, 15))
        else:
            messagebox.showwarning(
                title=self.transl("獲取失敗"),
                message=self.transl("沒有可整合的檔案"),
                parent=self,
            )

    """ ====== 關閉清理 ====== """

    def closure(self):
        username, app = self.get_config(True)
        undone = list(
            {cache["url"] for cache in self.task_cache.values()} | set(self.input_stream())
        )

        self.save_config(
            {
                "Account": username,
                "Application": app,
                "window_x": self.winfo_x(),
                "window_y": self.winfo_y(),
                "window_width": self.winfo_width(),
                "window_height": self.winfo_height(),
                "Tasks": undone,
            }
        )

        self.destroy()

    def log_cleanup(self, log_path):
        try:
            for handler in logging.root.handlers[:]:
                handler.close()

            if log_path.exists() and log_path.stat().st_size == 0:
                log_path.unlink()
        except Exception as e:
            logging.error(e)

    def process_cleanup(self):
        pids = []
        processName = "DepotDownloaderMod.exe"
        for proc in psutil.process_iter(["pid", "name"]):
            try:
                if proc.info["name"].lower() == processName.lower():
                    pids.append(proc.pid)
                    proc.kill()
            except Exception as e:
                logging.info(e)
                continue

        self.del_error_file(pids)

    def del_error_file(self, pids):
        for task in self.task_cache.values():
            path = task["path"]

            if Path(path).exists():
                for _ in range(10):  # 最多等待10秒
                    if not any(psutil.pid_exists(pid) for pid in pids):
                        try:
                            shutil.rmtree(path)
                            break
                        except Exception as e:
                            logging.info(e)
                            continue
                    time.sleep(1)

    """ ====== 附加功能 ====== """

    def extract_pkg(self, path):
        pkg_path = self.get_path_data(path).get("pkg", False)

        if pkg_path:
            for pkg in pkg_path:
                command = [self.repkg_exe, "extract", pkg, "-o", path, "-r", "-t", "-s"]

                process = subprocess.Popen(
                    command,
                    text=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    creationflags=subprocess.CREATE_NO_WINDOW,
                )

                output, _ = process.communicate()
                if process.returncode == 0:
                    pkg.unlink()

    def listen_clipboard(self):
        pyperclip.copy("")  # 避免開啟直接貼上

        while True:
            # unquote 是沒必要的, 方便觀看而已, 但會有額外性能開銷
            clipboard = unquote(pyperclip.paste()).strip()

            if self.link_regular.match(clipboard) and clipboard not in self.capture_record:
                self.capture_record.add(clipboard)
                self.input_text.insert("end", f"{clipboard}\n")
                self.input_text.yview("end")
                self.input_text.xview_moveto(1.0)

            time.sleep(0.3)

    def listen_network(self, process):
        net_io = psutil.net_io_counters()
        bytes_initial = net_io.bytes_sent + net_io.bytes_recv  # 計算初始的總流量

        while process.poll() is None:
            net_io = psutil.net_io_counters()
            bytes_current = net_io.bytes_sent + net_io.bytes_recv  # 當前總流量

            # 計算流量速度
            speed_text = (
                f"{total_speed:.2f} KB/s"
                if (total_speed := (bytes_current - bytes_initial) / 1e3) < 1e3
                else f"{(total_speed / 1e3):.2f} MB/s"
            )
            self.title(f"{self.win_title} （{speed_text}）")

            bytes_initial = bytes_current
            time.sleep(1)

    def copy_save_path(self, event):
        pyperclip.copy(self.save_path)
        popup = tk.Toplevel(self)
        popup.overrideredirect(True)
        popup.attributes("-topmost", True)

        label = tk.Label(
            popup,
            text=self.transl("已複製"),
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

    def server_search(self):

        # 編譯前綴樹函數
        def build_trie(data_list):
            trie = defaultdict(dict)
            for appid in data_list:
                current = trie
                for char in appid.lower():
                    current = current.setdefault(char, {})
                current["$"] = appid
            return trie

        # 搜尋前綴樹函數
        def search_trie(trie, prefix):
            current = trie
            for char in prefix:
                if char not in current:
                    return iter([])  # 前綴無法匹配，返回空的迭代器
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
        # 文本緩存, 用於當取消焦點狀態 且 serverid 內容為空時, 重新填充
        self.text_cache = ""

        def on_input(event):
            widget = event.widget
            prefix = widget.get().lower()  # 忽略大小寫
            matches = search_trie(appid_trie, prefix) if prefix else self.app_list  # 搜尋對象
            widget.configure(values=list(matches))  # 添加搜尋結果

        def on_click(event):
            x = event.x
            widget = event.widget
            text = self.serverid.get()

            # 判斷 點擊輸入框 且 文本含有 "->", 清空文本
            if x < widget.winfo_width() - 20 and "->" in text:
                text = self.clean_text(text)
                self.serverid.set(text)
                widget.unbind("<Button-1>")

            self.text_cache = text

        def on_select(event):
            self.text_cache = self.serverid.get()
            event.widget.configure(values=self.app_list)

        def of_select(event):
            if self.serverid.get().strip() == "":
                self.serverid.set(self.text_cache)

        self.serverid_menu.bind("<KeyRelease>", on_input)
        self.serverid_menu.bind("<Button-1>", on_click)
        self.serverid_menu.bind("<FocusOut>", of_select)
        self.serverid_menu.bind("<<ComboboxSelected>>", on_select)
