from . import shared

from ..bootstrap import (
    time,
    Path,
    shutil,
    psutil,
    logging,
    unquote,
    threading,
    subprocess,
    traceback,
    pyperclip,
)

from ..utils import (
    illegal_regex,
    parse_regex,
    link_regex,
    account_dict,
    get_ext_groups,
    BuildSuffixTree,
)


class Backend:
    def __init__(self):
        self.clean_text = lambda text: text.split("->")[-1]

        # 緩存搜尋樹
        self.searcher = None

        # 緩存任務數據 用於未完成恢復
        self.task_cache = {}

        # 除重用
        self.capture_record = set()
        self.complete_record = set()

        self.app_list = list(shared.appid_dict.keys())

        self.token = True  # 可強制停止所有任務
        self.error_rule = {
            ".NET": shared.transl("下載失敗: 請先安裝 .NET 9 執行庫"),
            "Unable to locate manifest ID for published file": shared.transl(
                "下載失敗: 該項目可能已被刪除，或應用設置錯誤"
            ),
            # 列表為可觸發強制停止任務
            **dict.fromkeys(
                ["STEAM GUARD", "Authentication", "AccountDisabled", "AlreadyLoggedInElsewhere"],
                shared.transl("下載失敗: 請嘗試變更帳號後再下載"),
            ),
        }

    """ ====== 下載 數據處理/觸發 ====== """

    def get_config(self, original=False):
        username, password = next(
            iter(
                account_dict.get(
                    self.clean_text(shared.msg.request("username")),
                    account_dict.get(shared.account),
                ).items()
            )
        )

        if original:
            for app in [self.clean_text(shared.msg.request("serverid")), self.app_list[0]]:
                if app in shared.appid_dict:
                    return username, app
        else:
            appid = shared.appid_dict.get(
                self.clean_text(shared.msg.request("serverid")),
                next(iter(shared.appid_dict.values())),
            )
            return appid, username, password

    def input_stream(self):
        while True:
            lines = shared.msg.request("input_operat", "get", "1.0", "end")
            if not lines or not lines[0].strip():
                break  # 避免空數據
            shared.msg.emit("input_operat", "delete", "1.0", "2.0")
            yield lines[0].strip()

    def download_trigger(self):
        self.status_switch("disabled")

        for link in self.input_stream():
            if link:
                match = parse_regex.search(link)
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
                            unquote(match.group(2)),
                            username,
                            password,
                        )
                else:
                    shared.msg.emit("console_insert", f"{shared.transl('無效連結')}：{link}\n")

        self.status_switch("normal")

    """ ====== 下載處理核心 ====== """

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

    def status_switch(self, state):
        if state == "disabled":
            shared.msg.emit("button_state_change", "disabled", "no")
        else:
            self.token = True  # 重設令牌
            pyperclip.copy("")  # 重設剪貼簿 避免 record 清除後再次擷取
            shared.msg.emit("title_change")  # 重設標題
            # self.capture_record.clear()

            if self.task_cache:
                self.process_cleanup()

                shared.msg.emit("input_operat", "delete", "1.0", "end")
                for task in self.task_cache.values():
                    shared.msg.emit("input_operat", "insert", f"{task['url']}\n")
                self.task_cache.clear()  # 重設任務緩存

            shared.msg.emit("button_state_change", "normal", "hand2")

    def download(self, taskId, appId, pubId, searchText, Username, Password):
        if not self.token:
            return

        if not shared.depot_exe.exists():
            self.token = False
            err_message = f"{shared.transl('找不到')}: {shared.depot_exe}"
            logging.error(err_message)
            shared.msg.emit("showerror", shared.transl("依賴錯誤"), err_message)
            return

        try:
            full_download = False
            end_message = shared.transl("下載完成")
            process_name = illegal_regex.sub("-", searchText if searchText else pubId).strip()

            shared.msg.emit(
                "console_insert", f"\n> {shared.transl('開始下載')} [{process_name}]\n", "important"
            )

            shared.save_path.mkdir(parents=True, exist_ok=True)
            task_path = self.get_unique_path(shared.save_path / process_name)
            self.task_cache[taskId]["path"] = task_path  # 添加下載路徑

            # 避免 Command Injection
            command = [
                shared.depot_exe,
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

                shared.msg.emit("console_insert", line)

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
                and end_message == shared.transl("下載完成")
                and Path(task_path).exists()
            ):
                self.task_cache.pop(taskId, None)  # 刪除任務緩存
                self.complete_record.add(taskId)  # 添加下載完成紀錄

                # 允許 repkg 且 appId 為 Wallpaper Engine 的 ID, 觸發提取
                if shared.repkg and appId == "431960":
                    threading.Thread(
                        target=self.extract_pkg, args=(task_path,), daemon=True
                    ).start()
            else:
                # 進程可能還需要繼續, 不刪除錯誤的文件
                # 用於顯示不在 console_analysis 中的錯誤
                end_message = (
                    end_message
                    if end_message != shared.transl("下載完成")
                    else shared.transl("下載失敗")
                )

            shared.msg.emit("console_insert", f"> [{process_name}] {end_message}\n", "important")
        except:
            shared.msg.emit("console_insert", f"> {shared.transl('例外中止')}\n", "important")

            exception = traceback.format_exc()
            logging.error(exception)
            shared.msg.emit("showerror", shared.transl("例外"), exception)

    """ ====== 檔案整合 (移動) ====== """

    def move_files(self, data_table, selected):
        merge_path = shared.save_path / shared.integrate_folder
        merge_path.mkdir(parents=True, exist_ok=True)
        move_file = [data_table[select] for select in selected]

        for files in move_file:
            for file in files:
                relative_path = file.relative_to(
                    shared.save_path
                )  # 獲取 file 在 shared.save_path 下的相對路徑

                top_folder = relative_path.parts[0]  # 取得最上層資料夾名稱

                try:
                    file.rename(merge_path / f"[{top_folder}] {file.name}")
                except Exception as e:
                    logging.warning(e)

        shared.msg.emit("merge_success_show", merge_path)

    """ ====== 關閉清理 ====== """

    def closure(self):
        if self.searcher is not None:
            self.searcher.clear_tree()  # 清除後墜樹記憶體 (占用很大)

        username, app = self.get_config(True)
        undone = list(
            {cache["url"] for cache in self.task_cache.values()} | set(self.input_stream())
        )

        shared.msg.emit("ui_close", username, app, undone)

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
            path = task.get("path")

            if path is not None and Path(path).exists():
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
        pkg_path = get_ext_groups(path).get("pkg", False)

        if pkg_path:

            # 如果中途被刪除, 關閉該功能
            if not shared.repkg_exe.exists():
                shared.repkg = False
                return

            for pkg in pkg_path:
                command = [shared.repkg_exe, "extract", pkg, "-o", path, "-r", "-t", "-s"]

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

        def loop():
            clipboard = pyperclip.paste().strip()

            if link_regex.match(clipboard) and clipboard not in self.capture_record:
                self.capture_record.add(clipboard)
                shared.msg.emit(
                    "input_operat", "insert", f"{unquote(clipboard)}\n"
                )  # unquote 是沒必要的, 方便觀看而已

            self.after(300, loop)

        loop()

    def listen_network(self, process):
        net_io = psutil.net_io_counters()
        bytes_initial = net_io.bytes_sent + net_io.bytes_recv  # 計算初始的總流量

        while process.poll() is None:
            net_io = psutil.net_io_counters()
            bytes_current = net_io.bytes_sent + net_io.bytes_recv  # 當前總流量

            # 計算流量速度
            shared.msg.emit(
                "title_change",
                (
                    f"{total_speed:.2f} KB/s"
                    if (total_speed := (bytes_current - bytes_initial) / 1e3) < 1e3
                    else f"{(total_speed / 1e3):.2f} MB/s"
                ),
            )

            bytes_initial = bytes_current
            time.sleep(1)

    def build_searcher(self):
        self.searcher = BuildSuffixTree(self.app_list)

    def search_list(self, text):
        return list(self.searcher.search(text)) if text else self.app_list
