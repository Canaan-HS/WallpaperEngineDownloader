# 桌布引擎創意工坊下載器 重製版

一款基於 [WallpaperEngineWorkshopDownloader](https://github.com/oureveryday/WallpaperEngineWorkshopDownloader) 重寫 UI 並添加多個新功能的專案

## 預覽

![中文版](https://github.com/user-attachments/assets/1d08c74b-4d98-49f8-aeb8-26f2e1c6c3ef)

## 依賴  

- [DepotDownloaderMod](https://github.com/oureveryday/DepotDownloaderMod)

## 使用方法  

* 請先安裝 [.NET 9.0 執行庫](https://dotnet.microsoft.com/download/dotnet/9.0/runtime)

* Widows 安裝指令:
```
winget install Microsoft.DotNet.SDK.9
```

1. 執行 `WallpaperDownloader.exe`

2. 在 <https://steamcommunity.com/app/431960/workshop/> 瀏覽你喜歡的創意工坊專案。

3. 複製你創意工坊專案的URL。例如，`https://steamcommunity.com/sharedfiles/filedetails/?id=1234567890`

4. 點擊下載

## 功能  

## **無需 Steam 賬戶**
- 支援直接下載 Steam 創意工坊專案，無需登入 Steam 賬戶即可使用。

## **語言自適應**
- 支援多語言介面，僅限簡體中文、繁體中文和英文三種語言，會根據使用者環境自動適配。

## **自動捕獲連結**
- **智慧貼上**
  複製創意工坊專案 URL（例如 `https://steamcommunity.com/sharedfiles/filedetails/?id=1234567890`）後，連結會自動填充至輸入框。
- **動態命名**
  若 URL 中包含 `searchtext=名稱`，輸出檔案將以此名稱命名。
  若無指定名稱，則預設以專案 ID 命名。

## **動態下載**
- **即時反饋**
  下載開始後，開始處理的連結會自動從輸入框移除。
- **隊列管理**
  用戶可持續新增連結，所有連結將依次加入下載隊列，直至輸入框清空。若在連結被處理前（即尚未移除時），用戶手動刪除輸入框中的內容，則該連結不會被載入下載。

## **檔案整合**
- **檔案選擇**
  列出輸出路徑下所有檔案（不包含 `!【Integrate】!` 資料夾），顯示檔案型別，支援單選或透過 `Ctrl`/`Shift` 鍵多選。
- **整合操作**
  選定型別的檔案合併後，將被移動至 `!【Integrate】!` 資料夾，並在檔名前附加來源資訊。

## **自定義應用**
- **自定義列表**
  使用者可透過編輯配置檔案中的 JSON 資料，自定義下拉列表的內容。
- **切換工作坊**
  使用者可透過下拉列表選擇目標應用程式，預設選項為 `Wallpaper Engine`。
- **簡易搜尋**
  輸入搜尋文字後，再次開啟下拉列表進行選擇。若輸入內容不在列表中（例如拼寫錯誤或無效字串），系統將回退至預設選項 `Wallpaper Engine`。
