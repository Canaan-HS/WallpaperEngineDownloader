# Wallpaper Engine Workshop Downloader — Rewritten Version

A rewritten version of WallpaperEngineWorkshopDownloader with a redesigned UI and multiple new features.

## Preview

![English Version](https://github.com/user-attachments/assets/9a0c489d-38fa-4f3e-9462-d557f2d029e2)

https://github.com/user-attachments/assets/dc70a30b-47c5-48e8-a4e5-8fcc9f665645

## Dependencies

- [DepotDownloaderMod](https://github.com/oureveryday/DepotDownloaderMod)
- [.NET 10.0 Runtime](https://dotnet.microsoft.com/download/dotnet/10.0/runtime)

## Usage

1. Run `WallpaperDownloader.exe`.

2. Browse the Workshop at https://steamcommunity.com/app/431960/workshop/ and find the Workshop item you want to download.

3. Copy the URL of the Workshop item. For example, `https://steamcommunity.com/sharedfiles/filedetails/?id=1234567890`

4. Click **Download**.

## Features

## **Steam Account**

- Supports using the default Steam account directly, with no additional login required for downloads.

- **QR Code Login**

  Supports logging in via QR code. The login session is stored locally and can be reused for future downloads.

  The session may expire after a certain period. If this happens, switch back to `QRCodeLogin` and scan the QR code again.

## **Automatic Language Detection**

- Supports multilingual interfaces in Simplified Chinese, Traditional Chinese, and English. The interface automatically adapts to the user's system language.

## **Automatic Link Capture**

- **Smart Paste**

  After copying a Workshop item URL (for example, `https://steamcommunity.com/sharedfiles/filedetails/?id=1234567890`), the URL is automatically inserted into the input field.

- **Dynamic Naming**

  If the URL contains `searchtext=Name`, the downloaded file will be named accordingly.

  If no name is specified, the Workshop item ID is used as the default filename.

## **Dynamic Downloads**

- **Real-Time Feedback**

  Once a download starts, the link currently being processed is automatically removed from the input field.

- **Queue Management**

  Users can continue adding links while downloads are in progress. Each link is added to the download queue in order until the input field is empty.

  If a link is manually removed from the input field before it is processed, it will not be added to the download queue.

## **Automatic Saving**

- **Save Settings**

  When the application closes, the window size and position are automatically saved and restored the next time the application starts.

- **Resume History**

  URLs currently in the task list, as well as URLs that were still downloading when the application was closed, are saved automatically.

  When the application starts again, these URLs are automatically restored to the task list.

## **Automatic PKG Extraction**

- **Background Processing**

  Automatically detects and extracts `.pkg` files from Wallpaper Engine Workshop items.

  Extraction runs independently in the background, **without interrupting the UI or subsequent downloads**.

- **Silent Processing**

  No notifications are displayed during extraction. If the application is closed immediately after the final item finishes downloading, any ongoing extraction may be interrupted.

## **File Integration**

- **File Selection**

  Lists all files under the output directory, excluding the `!【Integrate】!` folder, and displays their file types.

  Supports both single selection and multi-selection using `Ctrl`/`Shift`.

- **Integration**

  After selecting files of the desired type and merging them, the resulting files are moved to the `!【Integrate】!` folder with source information added to their filenames.

## **Custom Application**

- **Workshop Selection**

  Users can select the target application from the dropdown list. The default option is `Wallpaper Engine`.

- **Quick Search**

  Enter a search term and reopen the dropdown list to select an application.

  If the entered text does not match any item in the list, such as due to a typo or an invalid string, the application falls back to the default option, `Wallpaper Engine`.
