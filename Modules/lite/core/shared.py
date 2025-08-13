from ..bootstrap import json, logging
from ..utils import Signal

transl = None
set_lang = None

ck = None
cfg_key = None
cfg_data = None

output_folder = None
integrate_folder = None

icon_ico = None
save_path = None

config_json = None

repkg_exe = None
depot_exe = None

account = None
appid_dict = None
enable_extract_pkg = None

msg = Signal()


def save_config(data):
    old_data = {}
    cache_data = ""

    if config_json.exists():
        try:
            cache_data = (old_data := json.loads(config_json.read_text(encoding="utf-8"))).copy()
        except Exception as e:
            logging.info(e)

    old_data.update(data)
    final_config = {val: old_data.get(val, "") for val in cfg_key.values() if val in old_data}

    if cache_data != final_config:
        config_json.write_text(
            json.dumps(old_data, indent=4, separators=(",", ":")), encoding="utf-8"
        )
