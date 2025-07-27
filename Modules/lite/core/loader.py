from ..bootstrap import os, json, Path, logging, itemgetter, messagebox, SimpleNamespace

from . import shared
from ..utils import Language


class Loader:
    def __init__(self, default_config):
        getter = itemgetter(
            "language", "output_folder", "integrate_folder", "appid_dict", "current_dir"
        )
        (
            lang,
            shared.output_folder,
            shared.integrate_folder,
            shared.appid_dict,
            current_dir,
        ) = getter(default_config)

        # 配置預設值
        shared.account = "ruiiixx"
        shared.transl = Language(lang)

        # 配置模板 (Key 是調用值, Value 是輸出值)
        shared.cfg_key = {
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
        shared.save_path = current_dir / shared.output_folder
        shared.icon_ico = current_dir / "Icon/DepotDownloader.ico"

        id_json = current_dir / "APPID/ID.json"
        shared.config_json = current_dir / "Config.json"

        shared.repkg_exe = current_dir / "RePkg/RePkg.exe"
        shared.depot_exe = current_dir / "DepotdownloaderMod/DepotDownloadermod.exe"

        if not shared.depot_exe.exists():
            err_message = f"{shared.transl('找不到')}: {shared.depot_exe}"

            logging.error(err_message)
            messagebox.showerror(shared.transl("依賴錯誤"), err_message)
            os._exit(0)

        # 判斷是否運行 RePkg
        shared.repkg = True if shared.repkg_exe.exists() else False

        if id_json.exists():
            try:
                shared.appid_dict.update(json.loads(id_json.read_text(encoding="utf-8")))
            except Exception as e:
                logging.error(f"{shared.transl('讀取 ID.json 時出錯')}: {e}")

        shared.cfg_data = {}
        shared.ck = SimpleNamespace(**shared.cfg_key)  # 方便簡短調用

        if shared.config_json.exists():
            try:
                shared.cfg_data = {
                    val: config[val]
                    for val in shared.cfg_key.values()
                    if val in (config := json.loads(shared.config_json.read_text(encoding="utf-8")))
                }

                record_path = Path(shared.cfg_data.get(shared.ck.Save, ""))
                shared.save_path = (
                    record_path
                    if record_path.is_absolute() and record_path.name == shared.output_folder
                    else record_path / shared.output_folder
                )
            except Exception as e:
                logging.error(f"{shared.transl('讀取 Config.json 時出錯')}: {e}")
