# -*- mode: python ; coding: utf-8 -*-

# 排除標準庫和第三方庫
excludes = [
    # -----------------------------------------------------------------
    # 1. 測試、文檔和開發工具 (Testing, Docs & Dev Tools)
    # 這些在發布版本中完全不需要。
    # -----------------------------------------------------------------
    'unittest', 'pydoc', 'doctest', 'test', 'tests', 'pydoc_data',
    'lib2to3', 'pickletools', 'pdb', 'tracemalloc', 'profile', 'cProfile',

    # -----------------------------------------------------------------
    # 2. 打包與分發工具 (Build & Distribution)
    # 這些是開發環境工具，不應包含在最終產品中。
    # -----------------------------------------------------------------
    'distutils', 'setuptools', 'pip', '_distutils_hack', 'pkg_resources',
    'ensurepip', 'venv', 'wheel',

    # -----------------------------------------------------------------
    # 3. 網絡與 Web 服務 (Networking & Web Services)
    # 沒有網絡請求，可以安全排除所有相關模塊。
    # -----------------------------------------------------------------
    'asyncio', 'ssl', '_ssl', 'http', 'urllib.request',
    'ftplib', 'gopherlib', 'imaplib', 'nntplib', 'poplib', 'smtpd', 'smtplib',
    'telnetlib', 'wsgiref', 'webbrowser', 'cgi', 'cgitb', 'xmlrpc',

    # -----------------------------------------------------------------
    # 4. GUI、多媒體與圖形 (GUI, Multimedia & Graphics)
    # 排除未使用的 Tkinter 擴展、聲音、圖像和顏色處理庫。
    # -----------------------------------------------------------------
    'tkinter.tix', 'tkinter.dnd', 'turtledemo', 'turtle', 'curses',
    'winsound', 'colorsys', 'chunk', 'imghdr', 'sndhdr', 'ossaudiodev',

    # -----------------------------------------------------------------
    # 5. 數據庫 (Databases)
    # 不涉及數據庫操作。
    # -----------------------------------------------------------------
    'sqlite3', 'dbm', 'dbm.gnu', 'dbm.ndbm', 'dbm.dumb',

    # -----------------------------------------------------------------
    # 6. 數據格式與解析 (Data Formats & Parsing)
    # 排除除 JSON 和基本配置外的所有數據格式處理器。
    # -----------------------------------------------------------------
    'xml', 'xml.dom', 'xml.sax', 'xml.etree', 'csv', 'configparser',
    'html', 'email', 'json.tool', 'tarfile', 'zipapp', 'plistlib', 'xdrlib',

    # -----------------------------------------------------------------
    # 7. 加密與壓縮 (Cryptography & Compression)
    # -----------------------------------------------------------------
    'hashlib', 'hmac', 'secrets', 'bz2', 'lzma', 'gzip',

    # -----------------------------------------------------------------
    # 8. 並發與多進程 (Concurrency & Multiprocessing)
    # -----------------------------------------------------------------
    'multiprocessing', 'concurrent',

    # -----------------------------------------------------------------
    # 9. PyInstaller 與第三方庫的內部組件 (Internals)
    # 這些是 PyInstaller 的輔助工具或可以安全排除的第三方庫組件。
    # -----------------------------------------------------------------
    'altgraph', 'pyinstaller_hooks_contrib', '_pyinstaller_hooks_contrib',
    'pefile', 'packaging', 'pywin32_system32',

    # -----------------------------------------------------------------
    # 10. 不常用的標準庫 (Uncommon Standard Libraries)
    # -----------------------------------------------------------------
    'argparse', 'getopt', 'optparse', 'getpass', 'gettext', 'calendar',
    'decimal', 'fractions', 'statistics', 'msilib', 'msvcrt',
    'pickle', 'shelve', 'symtable', 'tabnanny',

    # -----------------------------------------------------------------
    # 11. Windows 特定組件 (Windows-Specific Components)
    # -----------------------------------------------------------------
    'win32com', 'win32ctypes', 'win32api', 'win32con', 'pywintypes',
]

# 排除二進制包
excluded_packages = [
    'PyInstaller', '_pyinstaller_hooks_contrib', 'pyinstaller_hooks_contrib',
    'pip', 'setuptools', 'pkg_resources', 'altgraph', 'win32ctypes', 'packaging', 'pefile'
]

# 排除不需要的文件類型
excluded_file_types = ['.pdb', '.lib', '.a', '.ilk', '.exp', '.map']

a = Analysis(
    ['../LiteLauncher.pyw'],
    pathex=[],
    binaries=[],
    datas=[('../Icon/DepotDownloader.ico', '.')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    noarchive=False,
    optimize=2,
)

a.binaries = [
    binary for binary in a.binaries
    if not any(binary[0].startswith(prefix) for prefix in excluded_packages)
    and not any(binary[1].lower().endswith(ext) for ext in excluded_file_types)
]

pyz = PYZ(a.pure, a.zipped_data, compress=True)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='WallpaperDownloader',
    version='LiteVersion.txt',
    icon=['../Icon/DepotDownloader.ico'],
    debug=False,
    bootloader_ignore_signals=True,
    strip=False, # GitHub Actions 的環境啟用, 可能會無法運行
    upx=True,
    upx_exclude=['python3.dll', 'libcrypto-3.dll'],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None
)