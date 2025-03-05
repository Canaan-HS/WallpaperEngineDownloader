# 桌布引擎創意工坊下載器

一款簡單復刻 [WallpaperEngineWorkshopDownloader](https://github.com/oureveryday/WallpaperEngineWorkshopDownloader) 重寫 UI 的專案

## 功能  

- **無需 Steam 帳戶**：直接下載創意工坊專案
- **語言自適應**：支援簡體中文、繁體中文和英文。
- **自動解析連結**：
  - 貼上專案 URL（如 `https://steamcommunity.com/sharedfiles/filedetails/?id=1234567890`）會自動提取 ID。
  - 若 URL 含 `searchtext=名稱`，則以該名稱命名檔案，否則使用專案 ID。
- **動態下載**：
  - 下載開始後，已處理的連結會從輸入框移除。
  - 持續新增的連結會自動加入下載佇列，直到輸入框清空。

## 依賴  

- [DepotDownloaderMod](https://github.com/oureveryday/DepotDownloaderMod)

## 預覽

![中文版](https://github.com/user-attachments/assets/cf9acb4a-f7bd-422a-a6ec-916c266b44c6)


## 使用方法  

* 請先安裝 [.NET 8.0 執行庫](https://dotnet.microsoft.com/download/dotnet/8.0/runtime)

* Widows 安裝指令:
```
winget install Microsoft.DotNet.SDK.8
```

1. 執行 `WallpaperDownloader.exe`

2. 在 <https://steamcommunity.com/app/431960/workshop/> 瀏覽你喜歡的創意工坊專案。

3. 複製你創意工坊專案的URL。例如，`https://steamcommunity.com/sharedfiles/filedetails/?id=1234567890`

4. 點擊下載