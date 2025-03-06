# 桌布引擎創意工坊下載器

一款簡單復刻 [WallpaperEngineWorkshopDownloader](https://github.com/oureveryday/WallpaperEngineWorkshopDownloader) 重寫 UI 的專案

## 功能  

- **無需 Steam 帳戶**：直接下載創意工坊專案
- **語言自適應**：支援簡體中文、繁體中文和英文。
- **自動捕獲連結**：
  - 複製專案 URL（如 `https://steamcommunity.com/sharedfiles/filedetails/?id=1234567890`）會自動貼上到輸入框。
  - 若 URL 含 `searchtext=名稱`，則輸出文件以該名稱命名，否則使用 ID 命名。
- **動態下載**：
  - 下載開始後，已處理的連結會從輸入框移除。
  - 持續新增的連結會自動加入下載佇列，直到輸入框清空。
- **檔案整合**
  - 列出輸出路徑下所有文件（不含 Integrate 資料夾），顯示檔案類型，支持單選或透過 Ctrl/Shift 多選
  - 合併後，選定類型的檔案將移至 Integrate 資料夾，並在檔案名稱附加來源位置

## 依賴  

- [DepotDownloaderMod](https://github.com/oureveryday/DepotDownloaderMod)

## 預覽

![中文版](https://github.com/user-attachments/assets/3c6f23f0-c9ae-42e3-9152-2748818db0a6)

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
