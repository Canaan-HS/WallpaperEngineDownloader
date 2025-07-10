from .Libs import *
from .Language import Language


class ENV:
    def __init__(self, default_config):
        getter = itemgetter(
            "language", "output_folder", "integrate_folder", "appid_dict", "current_dir"
        )
        (
            lang,
            self.output_folder,
            self.integrate_folder,
            self.appid_dict,
            current_dir,
        ) = getter(default_config)

        # 配置預設值
        self.transl = Language(lang)
        self.account = "ruiiixx"

        # 配置模板 (Key 是調用值, Value 是輸出值)
        self.cfg_key = {
            "Save": "Sava_Path",
            "Acc": "Account",
            "App": "Application",
            "X": "window_x",
            "Y": "window_y",
            "W": "window_width",
            "H": "window_height",
            "Task": "Tasks",
        }

        # 依賴載入路徑
        self.save_path = current_dir / self.output_folder
        self.icon_ico = current_dir / "Icon/DepotDownloader.ico"

        self.id_json = current_dir / "APPID/ID.json"
        self.config_json = current_dir / "Config.json"

        self.repkg_exe = current_dir / "RePkg/RePkg.exe"
        self.depot_exe = current_dir / "DepotdownloaderMod/DepotDownloadermod.exe"

        if not self.depot_exe.exists():
            logging.error(f"{self.transl('找不到')}: {self.depot_exe}")
            messagebox.showerror(
                self.transl("依賴錯誤"), f"{self.transl('找不到')}: {self.depot_exe}"
            )
            os._exit(0)

        # 判斷是否運行 RePkg
        self.repkg = True if self.repkg_exe.exists() else False

        if self.id_json.exists():
            try:
                self.appid_dict.update(json.loads(self.id_json.read_text(encoding="utf-8")))
            except Exception as e:
                logging.error(f"{self.transl('讀取 ID.json 時出錯')}: {e}")

        self.cfg_data = {}
        self.CK = SimpleNamespace(**self.cfg_key)  # 方便簡短調用

        if self.config_json.exists():
            try:
                self.cfg_data = {
                    val: config[val]
                    for val in self.cfg_key.values()
                    if val in (config := json.loads(self.config_json.read_text(encoding="utf-8")))
                }

                record_path = Path(self.cfg_data.get(self.CK.Save, ""))
                self.save_path = (
                    record_path
                    if record_path.is_absolute() and record_path.name == self.output_folder
                    else record_path / self.output_folder
                )
            except Exception as e:
                logging.error(f"{self.transl('讀取 Config.json 時出錯')}: {e}")

    def save_config(self, data):
        old_data = {}
        cache_data = ""

        if self.config_json.exists():
            try:
                cache_data = (
                    old_data := json.loads(self.config_json.read_text(encoding="utf-8"))
                ).copy()
            except Exception as e:
                logging.info(e)

        old_data.update(data)
        self.final_config = {
            val: old_data.get(val, "") for val in self.cfg_key.values() if val in old_data
        }

        if cache_data != self.final_config:
            self.config_json.write_text(
                json.dumps(old_data, indent=4, separators=(",", ":")), encoding="utf-8"
            )
