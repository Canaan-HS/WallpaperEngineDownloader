# Wallpaper Engine Workshop Downloader Rework

A project based on [WallpaperEngineWorkshopDownloader](https://github.com/oureveryday/WallpaperEngineWorkshopDownloader) with a rewritten UI and added multiple new features.

[中文版本](README_zh-TW.md)

## Preview

![English Version](https://github.com/user-attachments/assets/7d4786d6-4826-41da-b6ee-ea8faa634077)

## Dependencies

- [DepotDownloaderMod](https://github.com/oureveryday/DepotDownloaderMod)

## How to Use

* First, install the [.NET 9.0 Runtime](https://dotnet.microsoft.com/download/dotnet/9.0/runtime)

* Windows installation command:
```
winget install Microsoft.DotNet.SDK.9
```

1. Run `WallpaperDownloader.exe`

2. Browse your favorite Workshop projects at <https://steamcommunity.com/app/431960/workshop/>

3. Copy the URL of your selected Workshop project. For example, `https://steamcommunity.com/sharedfiles/filedetails/?id=1234567890`

4. Click "Download"

## Features

## **No Steam Account Required**
- Supports direct downloading of Steam Workshop projects without the need to log into a Steam account.

## **Language Adaptation**
- Supports a multilingual interface, limited to Simplified Chinese, Traditional Chinese, and English, automatically adapting to the user's environment.

## **Automatic Link Capture**
- **Smart Paste**
  After copying a Workshop project URL (e.g., `https://steamcommunity.com/sharedfiles/filedetails/?id=1234567890`), the link will automatically populate the input field.
- **Dynamic Naming**
  - If the URL contains `searchtext=name`, the output file will be named accordingly.
  - If no name is specified, the file will default to the project ID as its name.

## **Dynamic Downloading**
- **Real-Time Feedback**
  Once downloading begins, processed links will be automatically removed from the input field.
- **Queue Management**
  Users can continuously add links, which will be sequentially added to the download queue until the input field is empty. If a link is manually deleted from the input field before being processed (i.e., before removal), it will not be added to the download queue.

## **Auto Save**
- **Save Settings**  
  When the program is closed, the window size and position will be automatically saved, and these settings will be applied the next time the program is opened.
- **Restore Records**  
  URLs that are present in the task list, as well as those that are being downloaded but not yet completed, will be saved when the program is closed. Upon reopening, these URLs will automatically be restored to the task list.

## **File Integration**
- **File Selection**
  Lists all files in the output path (excluding the `!【Integrate】!` folder), displaying file types and supporting single selection or multi-selection via `Ctrl`/`Shift` keys.
- **Integration Operation**
  After merging, selected file types will be moved to the `!【Integrate】!` folder, with source location information appended to the file names.

## **Custom Application**
- **Custom List**
  Users can customize the dropdown list content by editing the JSON data in the configuration file.
- **Workshop Switching**
  Users can select the target application via a dropdown list, with `Wallpaper Engine` as the default option.
- **Simple Search**
  After entering search text, reopen the dropdown list to select. If the input is not in the list (e.g., due to typos or invalid strings), the system will fall back to the default option, `Wallpaper Engine`.