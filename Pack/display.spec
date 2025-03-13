# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['WallpaperDownloader.pyw'],
    pathex=[],
    binaries=[],
    datas=[('./Icon/DepotDownloader.ico', '.')], # 程式所需的依賴檔案 (例如Icon)
    hiddenimports=[], # 排除不需要的模塊
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='WallpaperDownloader', # 打包後的 exe 文件名
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True, # 啟用 upx 壓縮 (需要再 Scripts , 放入 upx.exe)
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version='version_info.txt', # 添加版本文件
    icon=['./Icon/DepotDownloader.ico'], # 添加Icon
)
