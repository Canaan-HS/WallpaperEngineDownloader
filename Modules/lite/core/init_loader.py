from ..bootstrap import os, json, Path, logging, itemgetter, messagebox, SimpleNamespace

from . import shared
from ..utils import search_path
from ..language import translator


class Init_Loader:
    def __init__(self, default_config):
        getter = itemgetter(
            "output_folder", "integrate_folder", "appid_dict", "exact_dir", "current_dir"
        )
        (
            shared.output_folder,
            shared.integrate_folder,
            shared.appid_dict,
            exact_dir,
            current_dir,
        ) = getter(default_config)

        # 配置預設值
        shared.account = "ruiiixx"
        shared.transl, shared.set_lang = translator()

        # 配置模板 (Key 是調用值, Value 是輸出值)
        shared.cfg_key = {
            "Save": "Sava_Path",
            "Lang": "Language",
            "Acc": "Account",
            "App": "Application",
            "ExtPkg": "Extract_Pkg",
            "X": "window_x",
            "Y": "window_y",
            "W": "window_width",
            "H": "window_height",
            "Task": "Tasks",
        }

        # 預設載入路徑
        shared.save_path = search_path() or exact_dir / shared.output_folder
        shared.icon_ico = current_dir / "Icon/DepotDownloader.ico"

        id_json = current_dir / "APPID/ID.json"
        shared.config_json = exact_dir / "Config.json"

        shared.repkg_exe = current_dir / "RePkg/RePkg.exe"
        shared.depot_exe = current_dir / "DepotdownloaderMod/DepotDownloadermod.exe"

        if not shared.depot_exe.exists():
            err_message = f"{shared.transl('找不到')}: {shared.depot_exe}"
            logging.error(err_message)
            messagebox.showerror(shared.transl("依賴錯誤"), err_message)
            os._exit(0)

        try:
            shared.appid_dict.update(json.loads(id_json.read_text(encoding="utf-8")))
        except FileNotFoundError:
            logging.warning("ID.json does not exist")
        except Exception as e:
            logging.error(f"{shared.transl('讀取 ID.json 時出錯')}: {e}")

        shared.cfg_data = {}
        shared.ck = SimpleNamespace(**shared.cfg_key)  # 方便簡短調用

        try:
            shared.cfg_data = {
                val: config[val]
                for val in shared.cfg_key.values()
                if val in (config := json.loads(shared.config_json.read_text(encoding="utf-8")))
            }

            record_path = Path(shared.cfg_data.get(shared.ck.Save, ""))  # 轉換用於判斷
            # 簡單的防呆, 避免有人直接修改 Config.json 導致的錯誤, 只要是絕對路徑, 下載時會自動補齊缺失
            shared.save_path = record_path if record_path.is_absolute() else shared.save_path
        except FileNotFoundError:
            pass
        except Exception as e:
            logging.error(f"{shared.transl('讀取 Config.json 時出錯')}: {e}")

        # 判斷是否運行 RePkg (預設為 False)
        shared.enable_extract_pkg = (
            True
            if shared.repkg_exe.exists() and shared.cfg_data.get(shared.ck.ExtPkg, False)
            else False
        )

        # 不是預設語言, 進行更新
        use_lang = shared.cfg_data.get(shared.ck.Lang, shared.set_lang)
        if use_lang != shared.set_lang:
            shared.transl, shared.set_lang = translator(use_lang)
