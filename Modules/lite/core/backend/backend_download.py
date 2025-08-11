from .. import shared
from ...utils import illegal_regex, parse_regex
from ...bootstrap import Path, logging, unquote, threading, subprocess, traceback, pyperclip


class Backend_Download:
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
