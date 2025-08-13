from .. import shared
from ...utils import link_regex, get_ext_groups, BuildSuffixTree
from ...bootstrap import time, psutil, logging, unquote, subprocess, pyperclip


class Backend_Tools:
    def build_searcher(self):
        self.searcher = BuildSuffixTree(self.app_list)

    def search_list(self, text):
        return list(self.searcher.search(text)) if text else self.app_list

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

    def move_files(self, data_table, selected):
        merge_path = shared.save_path / shared.integrate_folder
        merge_path.mkdir(parents=True, exist_ok=True)
        move_file = [data_table[select] for select in selected]

        for files in move_file:
            for file in files:
                relative_path = file.relative_to(
                    shared.save_path
                )  # 獲取 file 在 shared.save_path 下的相對路徑
                parts = relative_path.parts

                try:
                    if len(parts) > 1:  # 有父資料夾
                        top_folder = parts[0]  # 取得最上層資料夾名稱
                        parent_folder = file.parent.name  # 取得檔案父資料夾名稱

                        if top_folder == parent_folder:
                            new_name = f"[{top_folder}] {file.name}"
                        else:
                            new_name = f"[{top_folder}] {parent_folder} - {file.name}"
                    else:
                        new_name = file.name

                    file.rename(merge_path / new_name)
                except Exception as e:
                    logging.warning(e)

        shared.msg.emit("merge_success_show", merge_path)

    def extract_pkg(self, path, notify=False):
        pkg_path = get_ext_groups(path).get("pkg", False)

        if pkg_path:

            # 如果中途被刪除, 關閉該功能
            if not shared.repkg_exe.exists():
                shared.enable_extract_pkg = False
                if notify:
                    shared.msg.emit(
                        "extract_info_show",
                        "error",
                        shared.transl("提取失敗"),
                        f"{shared.transl('找不到')} {shared.repkg_exe}",
                    )
                return

            for pkg in pkg_path:
                # 沒有處理 被占用中的檔案, 無法提取問題 (不影響功能)
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
                    if notify:
                        shared.msg.emit(
                            "extract_info_show",
                            "info",
                            shared.transl("提取完成"),
                            f"{shared.transl('成功提取')} {len(pkg_path)} {shared.transl('個 PKG 檔案')}",
                        )
                    pkg.unlink()

        elif notify:
            shared.msg.emit(
                "extract_info_show",
                "error",
                shared.transl("提取失敗"),
                shared.transl("找不到 PKG 檔案"),
            )
