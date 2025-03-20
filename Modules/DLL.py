from .__Lib__ import *
from .Language import Language

class DLL:
    def __init__(self, current_dir):
        # 打包的 exe 執行路徑 與 原碼執行要抓不同路徑
        self.current_dir = current_dir

        # 預設輸出的文件名稱
        self.integrate_folder = "!【Integrate】!"
        self.output_folder = "Wallpaper_Output"

        # 配置預設值
        self.transl = Language()
        self.account = "ruiiixx"
        self.appid_dict = {"Wallpaper Engine": "431960"}

        # 配置模板 (Key 是調用值, Value 是輸出值)
        self.cfg_key = {
            "Save": "Sava_Path",
            "Acc": "Account", "App": "Application",
            "X": "window_x", "Y": "window_y",
            "W": "window_width", "H": "window_height",
            "Task": "Tasks"
        }

        # 依賴載入路徑
        self.id_json = self.current_dir / "APPID/ID.json"
        self.config_json = self.current_dir / "Config.json"
        self.save_path = self.current_dir / self.output_folder
        self.icon_ico = self.current_dir / "Icon/DepotDownloader.ico"
        self.depot_exe = self.current_dir / "DepotdownloaderMod/DepotDownloadermod.exe"

        if not self.depot_exe.exists():
            messagebox.showerror(self.transl('依賴錯誤'), f"{self.transl('找不到')} {self.depot_exe}")
            os._exit(0)

        if self.id_json.exists():
            try:
                id_dict = json.loads(self.id_json.read_text(encoding="utf-8"))
                self.appid_dict.update(id_dict)
            except Exception as e:
                print(f"{self.transl('讀取配置文件時出錯')}: {e}")

        self.cfg_data = {}
        self.CK = SimpleNamespace(**self.cfg_key) # 方便簡短調用

        if self.config_json.exists():
            try:
                config_dict = json.loads(self.config_json.read_text(encoding="utf-8"))

                self.cfg_data = {val: config_dict[val] for val in self.cfg_key.values() if val in config_dict} # 解構數據
                record_path = Path(self.cfg_data.get(self.CK.Save, ""))

                if record_path.is_absolute():
                    self.save_path = record_path if record_path.name == self.output_folder else record_path / self.output_folder
            except Exception as e:
                print(f"{self.transl('讀取配置文件時出錯')}: {e}") # 除錯用

    def save_config(self, data):
        old_data = {}
        cache_data = ""

        if self.config_json.exists():
            old_data = json.loads(self.config_json.read_text(encoding="utf-8"))
            cache_data = old_data.copy()

        old_data.update(data)
        self.final_config = {val: old_data.get(val, "") for val in self.cfg_key.values() if val in old_data}  

        if cache_data != self.final_config:
            self.config_json.write_text(
                json.dumps(old_data, indent=4, separators=(',',':')),
                encoding="utf-8"
            )