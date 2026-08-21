from .. import shared
from ...utils import ILLEGAL_REGEX, PARSE_REGEX, QR_KEY, get_file_size
from ...bootstrap import logging, unquote, threading, subprocess, traceback, pyperclip


class Backend_Download:
    def status_switch(self, state):
        if state == "disabled":
            shared.msg.emit("button_state_change", "disabled", "no")
        else:
            self.token = True  # 重設令牌
            pyperclip.copy("")  # 重設剪貼簿 避免 record 清除後再次擷取
            shared.msg.emit("title_change")  # 重設標題
            shared.current_task_name = ""  # 重設任務名
            # self.capture_record.clear()

            if self.task_cache:
                self.process_cleanup()

                shared.msg.emit("input_operat", "delete", "1.0", "end")
                for task in self.task_cache.values():
                    shared.msg.emit("input_operat", "insert", f"{task['url']}\n")
                self.task_cache.clear()  # 重設任務緩存

            shared.msg.emit("button_state_change", "normal", "hand2")

    def input_stream(self):
        while True:
            lines = shared.msg.request("input_operat", "get", "1.0", "end")
            line = lines[0].strip()

            shared.msg.emit("input_operat", "delete", "1.0", "2.0")

            # 避免空數據
            if len(lines) == 1 and not line:
                break
            elif not line:
                continue

            yield line

    def download_trigger(self):
        self.status_switch("disabled")

        try:
            for link in self.input_stream():
                if link:
                    match = PARSE_REGEX.search(link)
                    if match:
                        self.capture_record.add(link)
                        appid, username, password = (
                            self.get_config()
                        )  # 允許臨時變更, 所以每次重獲取

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
                        shared.msg.emit("console_insert", f"{shared.transl('無效連結')}：{link}\n")
        except Exception as e:
            logging.error(e)
            shared.msg.emit("showerror", shared.transl("例外"), e)

        self.status_switch("normal")

    def download(self, taskId, appId, pubId, searchText, username, password):
        if not self.token:
            return

        # 防護用, 避免有人途中刪除 depot_exe
        if not shared.depot_exe.exists():
            self.token = False
            err_message = f"{shared.transl('找不到')}: {shared.depot_exe}"
            logging.error(err_message)
            shared.msg.emit("showerror", shared.transl("依賴錯誤"), err_message)
            return

        try:

            def task(command: list, end_message: str = "") -> tuple[str, int]:
                process = subprocess.Popen(
                    command,
                    text=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    creationflags=subprocess.CREATE_NO_WINDOW,
                )

                full_download_size = 0
                threading.Thread(target=self.listen_network, args=(process,), daemon=True).start()

                for line in process.stdout:
                    if line.strip() == "":
                        continue

                    # 臨時補丁
                    if username == QR_KEY:
                        if "█" in line:
                            shared.msg.emit("console_insert", line, "QRCode")
                        elif "-remember-password" in line:
                            self.login_processing(line)
                    else:
                        shared.msg.emit("console_insert", line)

                    # 分析可能的錯誤訊息, 消息是列表狀態, 代表需要強制中止
                    err_message = self.console_analysis(line)
                    if isinstance(err_message, list):
                        self.token = False
                        process.terminate()
                        end_message = err_message[0]

                    elif err_message:
                        end_message = err_message

                    # 解析下載解壓後總大小
                    if "Total downloaded" in line:
                        full_download_size = int(line.split("(")[1].split(" bytes")[0])

                process.stdout.close()
                process.wait()

                return end_message, full_download_size

            # 宣告旗標
            success_message = shared.transl("下載完成")
            failure_message = shared.transl("下載失敗")

            # 處理檔名
            process_name = ILLEGAL_REGEX.sub(
                "-", unquote(searchText) if searchText else pubId
            ).strip()

            shared.current_task_name = process_name
            shared.msg.emit(
                "console_insert", f"\n> {shared.transl('開始下載')} [{process_name}]\n", "important"
            )

            # 防護用, 避免有人中途把文件刪掉
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
                "-dir",
                task_path,
                "-validate",
                "-max-downloads",
                "16",
            ]

            # 觸發 QR 登入
            if username == QR_KEY:
                command += ["-qr", "-remember-password"]
            # 使用儲存的帳號
            elif password == "-remember-password":
                command += ["-username", username, password]
            # 使用預設帳號
            else:
                command += ["-username", username, "-password", password]

            end_message, full_download_size = task(command, success_message)

            # 不需要這麼多檢測, 但避免例外
            if (
                # 結果字串與成功字串相同, 代表中途無檢測到錯誤
                end_message == success_message
                # 下載總大小大於 0, 代表下載成功
                and full_download_size > 0
                # 檔案存在
                and task_path.exists()
                # 本地檔案大小 與 下載大小相差不超過 5%
                and abs(get_file_size(task_path) - full_download_size) / full_download_size <= 0.05
            ):

                self.task_cache.pop(taskId, None)  # 刪除任務緩存
                self.complete_record.add(taskId)  # 添加下載完成紀錄

                # 允許 repkg 且 appId 為 Wallpaper Engine 的 ID, 觸發提取
                if shared.enable_extract_pkg and appId == "431960":
                    threading.Thread(
                        target=self.extract_pkg, args=(task_path,), daemon=True
                    ).start()

                # 刪除 depot 生成的 manifest
                threading.Thread(target=self.del_depot_data, args=(task_path,), daemon=True).start()
            else:
                # 進程可能還需要繼續, 不刪除錯誤的文件
                # 用於顯示不在 console_analysis 中的錯誤
                end_message = end_message if end_message != success_message else failure_message

            shared.msg.emit("console_insert", f"> [{process_name}] {end_message}\n", "important")
        except:
            shared.msg.emit("console_insert", f"> {shared.transl('例外中止')}\n", "important")

            exception = traceback.format_exc()
            logging.error(exception)
            shared.msg.emit("showerror", shared.transl("例外"), exception)
