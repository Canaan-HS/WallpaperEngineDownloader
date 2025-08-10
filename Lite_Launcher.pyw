from Modules.lite import sys, Path, logging, atexit, IsFrozen, LogConfig, Init_Loader, UI_Loader


class Controller(Init_Loader, UI_Loader):
    def __init__(self, default_config):
        log_path = Path(default_config["exact_dir"]) / "Info.log"

        if IsFrozen:
            LogConfig.update(
                {
                    "level": logging.WARNING,
                    "filename": str(log_path),
                    "encoding": "utf-8",
                }
            )

        logging.basicConfig(**LogConfig)
        sys.excepthook = lambda *args: (
            logging.error(exc_info=args),
            sys.__excepthook__(*args),
        )

        Init_Loader.__init__(self, default_config)
        UI_Loader.__init__(self)

        atexit.register(self.process_cleanup)  # 關閉後進程清理
        atexit.register(self.log_cleanup, log_path)  # 關閉後日誌清理


if __name__ == "__main__":
    Controller(
        {
            "output_folder": "Workshop_Output",
            "integrate_folder": "!【Integrate】!",
            "appid_dict": {"Wallpaper Engine": "431960"},
            # 適用於 pyinstaller 打包精確位置判斷
            "exact_dir": Path(sys.executable if IsFrozen else __file__).parent,
            # 適用於直接執行, 與 pyinstaller 打包後解壓位置
            "current_dir": Path(__file__).parent,
        }
    )
