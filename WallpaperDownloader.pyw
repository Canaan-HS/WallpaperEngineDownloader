from Modules import *

class Controller(ENV, tk.Tk, Backend, GUI):
    def __init__(self, default_config):
        ENV.__init__(self, default_config)
        tk.Tk.__init__(self)
        Backend.__init__(self)
        GUI.__init__(self)

        self.protocol("WM_DELETE_WINDOW", self.Closure)
        self.mainloop()

if __name__ == "__main__":
    #! key 值不能隨意修改 (需要同時修改 ENV)
    Controller({
        "language": None, # 自動偵測
        "output_folder": "Wallpaper_Output",
        "integrate_folder": "!【Integrate】!",
        "appid_dict": {"Wallpaper Engine": "431960"},
        "current_dir": Path(sys.executable).parent if getattr(sys, 'frozen', False) else Path(__file__).parent # pyinstaller 打包 與 原碼執行要抓不同路徑
    })