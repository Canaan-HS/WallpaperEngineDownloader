from ..bootstrap import vdf, Path, logging, winreg, SimpleNamespace


# 適用於 windows 的, Wallpaper Engine 'projects/myprojects' 路徑搜尋
def search_path() -> str:

    try:
        with winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE, "SOFTWARE\\WOW6432Node\\Valve\\Steam"
        ) as key:
            # 獲取 steam 安裝路徑
            steam_path, _ = winreg.QueryValueEx(key, "installPath")

            if not steam_path:
                raise Exception("Not found steam path")

            library_path = Path(steam_path) / "steamapps" / "libraryfolders.vdf"
            # 讀取 libraryfolders.vdf, 並用 vdf 解析
            library = vdf.loads(library_path.read_text(encoding="utf-8"))

            app_path = ""
            for value in library["libraryfolders"].values():
                data = SimpleNamespace(value)
                if "431960" in data.apps.keys():
                    app_path = (
                        Path(data.path)
                        / "steamapps"
                        / "common"
                        / "wallpaper_engine"
                        / "projects"
                        / "myprojects"
                    )

            if app_path and app_path.exists():
                return app_path

            raise Exception("Not found projects path")
    except Exception as e:
        logging.info(e)
        return ""

    return ""
