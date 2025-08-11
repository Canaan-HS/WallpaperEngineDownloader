from .. import shared
from ...bootstrap import time, Path, shutil, psutil, logging


class Backend_Cleaner:
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
