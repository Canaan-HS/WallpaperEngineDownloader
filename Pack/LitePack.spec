# -*- mode: python ; coding: utf-8 -*-

# 適用於 py 3.14.7 較為通用的版本 (主要還是根據該項目依賴設置)
excludes = [
    # ============================================================
    # 1. 測試、文檔和開發工具
    # ============================================================
    'unittest', 'test', 'tests', 'doctest', 'pytest', '_pytest',
    'nose', 'mock', 'tox', 'hypothesis', 'pdb', 'bdb',
    'cProfile', 'profile', 'pstats', 'tracemalloc',
    'pydoc', 'pydoc_data', 'pickletools',

    # ============================================================
    # 2. 打包與分發工具
    # ============================================================
    'setuptools', 'pip', 'venv', 'zipapp', 'pyclbr',
    'idlelib', 'pkg_resources', 'ensurepip', 'wheel',

    # ============================================================
    # 3. 網絡與 Web 服務
    # ============================================================
    'ftplib', 'gopherlib', 'imaplib', 'poplib', 'smtplib',
    'mailbox', 'wsgiref',

    # ============================================================
    # 4. GUI、多媒體與圖形
    # ============================================================
    'tkinter.tix', 'tkinter.dnd', 'turtle', 'turtledemo',
    'curses', 'winsound', 'colorsys',

    # ============================================================
    # 5. 數據庫
    # ============================================================
    'sqlite3', 'dbm', 'dbm.gnu', 'dbm.ndbm', 'dbm.dumb',

    # ============================================================
    # 6. 數據格式與解析
    # ============================================================
    'xml.dom', 'xml.sax', 'xml.etree', 'json.tool',
    'tarfile', 'plistlib',

    # ============================================================
    # 7. 加密與壓縮
    # ============================================================
    'hmac', 'secrets', 'bz2', 'lzma', 'gzip',
    'compression', 'compression.zstd',

    # ============================================================
    # 8. 並發與多進程
    # ============================================================
    'concurrent.interpreters',

    # ============================================================
    # 9. PyInstaller 與第三方庫內部組件
    # ============================================================
    'altgraph', 'pyinstaller_hooks_contrib',
    '_pyinstaller_hooks_contrib', 'pefile', 'packaging',
    'pywin32_system32',

    # ============================================================
    # 10. 不常用的標準庫
    # ============================================================
    'argparse', 'getopt', 'calendar', 'optparse',
    'getpass', 'gettext', 'decimal', 'fractions', 'statistics',
    'shelve', 'symtable', 'tabnanny',
    'string.templatelib',

    # ============================================================
    # 11. Windows 特定組件
    # ============================================================
    'win32com', 'win32ctypes', 'win32api', 'win32con',
    'pywintypes', 'win32cred', 'win32file', 'win32pipe',
    'win32process',

    # ============================================================
    # 12. 不常見的編碼
    # ============================================================
    'encodings.koi8_r', 'encodings.koi8_t', 'encodings.koi8_u',
    'encodings.kz1048', 'encodings.ptcp154', 'encodings.tis_620',
    'encodings.hp_roman8', 'encodings.palmos',

    'encodings.mac_cyrillic', 'encodings.mac_greek',
    'encodings.mac_iceland', 'encodings.mac_latin2',
    'encodings.mac_roman', 'encodings.mac_turkish',

    'encodings.iso8859_2', 'encodings.iso8859_3',
    'encodings.iso8859_4', 'encodings.iso8859_5',
    'encodings.iso8859_6', 'encodings.iso8859_7',
    'encodings.iso8859_8', 'encodings.iso8859_10',
    'encodings.iso8859_11', 'encodings.iso8859_13',
    'encodings.iso8859_14', 'encodings.iso8859_15',
    'encodings.iso8859_16',

    'encodings.cp037', 'encodings.cp273', 'encodings.cp424',
    'encodings.cp500', 'encodings.cp720', 'encodings.cp737',
    'encodings.cp775', 'encodings.cp850', 'encodings.cp855',
    'encodings.cp858', 'encodings.cp861', 'encodings.cp862',
    'encodings.cp863', 'encodings.cp864', 'encodings.cp865',
    'encodings.cp866', 'encodings.cp869', 'encodings.cp874',
    'encodings.cp875', 'encodings.cp1006', 'encodings.cp1026',
    'encodings.cp1125', 'encodings.cp1140',
    'encodings.cp1250', 'encodings.cp1251', 'encodings.cp1253',
    'encodings.cp1254', 'encodings.cp1255', 'encodings.cp1256',
    'encodings.cp1257', 'encodings.cp1258',
    'encodings.cp852', 'encodings.cp860',
]

# 排除二進制包
excluded_packages = [
    'PyInstaller', '_pyinstaller_hooks_contrib', 'pyinstaller_hooks_contrib',
    'pip', 'setuptools', 'pkg_resources', 'altgraph', 'win32ctypes', 'packaging', 'pefile'
]

# 排除不需要的文件類型
excluded_file_types = ['.pdb', '.lib', '.a', '.ilk', '.exp', '.map']

a = Analysis(
    ['../Lite_Launcher.pyw'],
    pathex=[],
    binaries=[
        ('../RePKG/RePkg.Net10.exe', 'RePKG'),
        # ('../DepotDownloaderMod', 'DepotDownloaderMod')
    ],
    datas=[
        ('../Icon/DepotDownloader.ico', 'Icon'),
        ('../APPID/ID.json', 'APPID')
    ],
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