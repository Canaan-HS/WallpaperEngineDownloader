from modules.lite import tk, sys, Path, logging, atexit, Loader, Backend, UI, IsFrozen, LogConfig


class Controller(Loader, tk.Tk, Backend, UI):
    def __init__(self, default_config):
        log_path = Path(default_config["current_dir"]) / "Info.log"

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

        Loader.__init__(self, default_config)
        tk.Tk.__init__(self)
        Backend.__init__(self)
        UI.__init__(self)

        self.protocol("WM_DELETE_WINDOW", self.closure)  # 關閉 GUI 與 自動保存
        atexit.register(self.process_cleanup)  # 關閉後進程清理
        atexit.register(self.log_cleanup, log_path)  # 關閉後日誌清理
        self.mainloop()


if __name__ == "__main__":
    # ! key 值不能隨意修改 (需要同時修改 ENV)
    Controller(
        {
            "language": None,  # 自動偵測
            "output_folder": "Wallpaper_Output",
            "integrate_folder": "!【Integrate】!",
            "appid_dict": {"Wallpaper Engine": "431960"},
            "current_dir": Path(sys.executable if IsFrozen else __file__).parent,
        }
    )
