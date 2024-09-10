# Wallpaper Engine Workshop Downloader

A simple recreation of [WallpaperEngineWorkshopDownloader](https://github.com/oureveryday/WallpaperEngineWorkshopDownloader) with a rewritten UI.

[中文版本](README_zh-TW.md)

## Features

- **No Steam account required**: Directly download Workshop projects.
- **Language adaptive**: Supports Simplified Chinese, Traditional Chinese, and English.
- **Automatic Link Capture**:
  - Copy the project URL (e.g., `https://steamcommunity.com/sharedfiles/filedetails/?id=1234567890`), and it will automatically be pasted into the input box.
  - If the URL contains `searchtext=name`, the output file will be named after that name; otherwise, it will be named using the ID.
- **Dynamic downloading**:
  - Once a download starts, the processed links will be removed from the input box.
  - Continuously added links will automatically join the download queue until the input box is cleared.
- **File Integration**  
  - Lists all files under the output path (excluding the !【Integrate】! folder), displaying file types with support for single selection or multi-selection via Ctrl/Shift.  
  - After integration, selected file types are moved to the !【Integrate】! folder, with source location appended to the file names.

## Dependencies

- [DepotDownloaderMod](https://github.com/oureveryday/DepotDownloaderMod)

## Preview

![English Version](https://github.com/user-attachments/assets/508c7cd3-f88f-4ff4-823c-8d5d005c41f8)

## How to Use

* First, install the [.NET 8.0 Runtime](https://dotnet.microsoft.com/download/dotnet/8.0/runtime)

* Windows installation command:
```
winget install Microsoft.DotNet.SDK.8
```

1. Run `WallpaperDownloader.exe`

2. Browse your favorite Workshop projects at <https://steamcommunity.com/app/431960/workshop/>

3. Copy the URL of your selected Workshop project. For example, `https://steamcommunity.com/sharedfiles/filedetails/?id=1234567890`

4. Click "Download"