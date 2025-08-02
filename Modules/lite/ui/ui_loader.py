from ..bootstrap import tk
from ..core import Backend_Loader

from .ui_main import UI_Main
from .ui_operat import UI_Operat


class UI_Loader(tk.Tk, Backend_Loader, UI_Main, UI_Operat):
    def __init__(self):
        tk.Tk.__init__(self)
        Backend_Loader.__init__(self)
        UI_Main.__init__(self)
        UI_Operat.__init__(self)

        self.protocol("WM_DELETE_WINDOW", self.closure)  # 關閉 GUI 與 自動保存
        self.mainloop()
