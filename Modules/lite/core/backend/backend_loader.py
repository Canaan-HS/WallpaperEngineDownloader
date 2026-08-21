from .. import shared

from .backend_tools import Backend_Tools
from .backend_cleaner import Backend_Cleaner
from .backend_download import Backend_Download


class Backend_Loader(Backend_Cleaner, Backend_Tools, Backend_Download):
    def __init__(self):
        self.clean_text = lambda text: text.split("->")[-1]

        # 緩存搜尋樹
        self.searcher = None

        # 緩存任務數據 用於未完成恢復
        self.task_cache = {}

        # 除重用
        self.capture_record = set()
        self.complete_record = set()

        self.app_list = list(shared.appid_dict.keys())

        self.token = True  # 允許下載
        self.init_error_rule()  # 初始化錯誤規則

        # ? 目前只是簡單的將, 個類型功能硬拆成不同模塊, 但其實基本都是相互依賴的, 只是都放在同一個模塊太難閱讀
        # ! Download 需要 Tools 和 Cleaner 的函數, 順序不能亂
        Backend_Cleaner.__init__(self)
        Backend_Tools.__init__(self)
        Backend_Download.__init__(self)

    def init_error_rule(self):
        self.error_rule = {
            ".NET": shared.transl("下載失敗: 請先安裝 .NET 9 執行庫"),
            "Unable to locate manifest ID for published file": shared.transl(
                "下載失敗: 該項目可能已被刪除，或應用設置錯誤"
            ),
            # 列表為可觸發強制停止任務
            **dict.fromkeys(
                [
                    "STEAM GUARD",
                    "Authentication",
                    "AccountDisabled",
                    "ArgumentException",
                    "AlreadyLoggedInElsewhere",
                ],
                [shared.transl("下載失敗: 請嘗試變更帳號後再下載")],
            ),
        }
