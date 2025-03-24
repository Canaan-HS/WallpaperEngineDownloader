from .__Lib__ import *

def Language(lang=None):
        Word = {
            'zh_TW': {"": ""},
            'zh_CN': {
                "創意工坊下載器": "创意工坊下载器",
                "選擇配置": "选择配置",
                "修改路徑": "修改路径",
                "檔案整合": "文件整合",
                "帳號": "账号",
                "應用": "应用",
                "已複製": "已复制",
                "選擇資料夾": "选择文件夹",
                "控制台輸出": "控制台输出",
                "輸入創意工坊專案（每行一個，支援連結和檔案ID）": "输入创意工坊项目（每行一个，支持链接和文件ID）",
                "選擇整合的類型": "选择整合的类型",
                "檔案類型": "文件类型",
                "檔案數量": "文件数量",
                "操作提示": "操作提示",
                "請選擇要整合的類型": "请选择要整合的类型",
                "操作確認": "操作确认",
                "整合以下類型的檔案": "整合以下类型的文件",
                "操作完成": "操作完成",
                "檔案整合完成": "文件整合完成",
                "整合輸出": "整合输出",
                "獲取失敗": "获取失败",
                "沒有可整合的檔案": "没有可整合的文件",
                "下載": "下载",
                "例外": "例外",
                "開始下載": "开始下载",
                "下載完成": "下载完成",
                "例外中止": "例外中止",
                "無效連結": "无效链接",
                "下載失敗": "下载失败",
                "下載失敗: 請先安裝 .NET 9 執行庫": "下载失败: 请先安装 .NET 9 运行库",
                "下載失敗: 該項目可能已被刪除，或應用設置錯誤": "下载失败: 该项目可能已被删除，或应用设置错误",
                "下載失敗: 請嘗試變更帳號後在下載": "下载失败: 请尝试变更帐号后再下载",
                "找不到": "找不到",
                "依賴錯誤": "依赖错误",
                "讀取 ID.json 時出錯": "读取 ID.json 时出错",
                "讀取 Config.json 時出錯": "读取 Config.json 时出错",
            },
            'en_US': {
                "創意工坊下載器": "Workshop Downloader",
                "選擇配置": "Select",
                "修改路徑": "Modify Path",
                "檔案整合": "File Integration",
                "帳號": "Acc",
                "應用": "App",
                "已複製": "Copied",
                "選擇資料夾": "Select Folder",
                "控制台輸出": "Console Output",
                "輸入創意工坊專案（每行一個，支援連結和檔案ID）": "Enter Workshop Project (one per line, supports link and file ID)",
                "選擇整合的類型": "Select Type of Integration",
                "檔案類型": "File Type",
                "檔案數量": "File Count",
                "操作提示": "Operation Tips",
                "請選擇要整合的類型": "Please select the type of integration",
                "操作確認": "Operation Confirmation",
                "整合以下類型的檔案": "Integrate the following types of files",
                "操作完成": "Operation Completed",
                "檔案整合完成": "File Integration Completed",
                "整合輸出": "Integration Output",
                "獲取失敗": "Failed to Retrieve",
                "沒有可整合的檔案": "No Files to Integrate",
                "下載": "Download",
                "例外": "Exception",
                "開始下載": "Start Download",
                "下載完成": "Download Completed",
                "例外中止": "Exception Aborted",
                "無效連結": "Invalid Link",
                "下載失敗": "Download Failed",
                "下載失敗: 請先安裝 .NET 9 執行庫": "Download Failed: Please install .NET 9 Runtime first",
                "下載失敗: 該項目可能已被刪除，或應用設置錯誤": "Download Failed: The project may have been deleted, or the application settings are incorrect",
                "下載失敗: 請嘗試變更帳號後在下載": "Download Failed: Please try changing the account and then download",
                "找不到": "Not Found",
                "依賴錯誤": "Dependency Error",
                "讀取 ID.json 時出錯": "Failed to read ID.json",
                "讀取 Config.json 時出錯": "Failed to read Config.json",
            }
        }

        Locale = {
            '950': 'zh_TW', '936': 'zh_CN', '1252': 'en_US'
        }

        ML = {}
        default = 'en_US'

        try:
            if lang is None:
                if SysPlat == 'Windows':
                    buffer = ctypes.create_unicode_buffer(85)
                    ctypes.windll.kernel32.GetUserDefaultLocaleName(buffer, len(buffer))
                    lang = buffer.value.replace('-', '_')
                elif SysPlat in ['Linux', 'Darwin']:
                    lang = os.environ.get('LANG', '').split('.')[0]
                else:
                    locale.setlocale(locale.LC_ALL, '')
                    lang = locale.getlocale()[1].replace('cp', '')
        except Exception as e:
            logging.info(e)
            lang = default

        ML = Word.get(lang) if isinstance(lang, str) and lang in Word else \
            Word.get(Locale.get(lang)) if isinstance(lang, str) and lang in Locale else \
            Word.get(default)

        return lambda text: ML.get(text, text)